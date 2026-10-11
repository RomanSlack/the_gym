import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { model, underlay, fmtElev } from "./model";
import type { Level, SectionDef } from "./model";
import { Plan, type Layers } from "./draw/Plan";
import { Section } from "./draw/Section";
import { Figures, type FigState } from "./draw/Figures";

type Sheet =
  | { no: string; title: string; kind: "plan"; level: Level; site: boolean; fit: [number, number, number, number] }
  | { no: string; title: string; kind: "section"; sec: SectionDef; fit: [number, number, number, number] };

function buildSheets(): Sheet[] {
  const byId = Object.fromEntries(model.levels.map((l) => [l.id, l]));
  const plans = ["F1", "F2", "E2", "F3", "F4"].filter((id) => byId[id]);
  const sheets: Sheet[] = [
    { no: "A-100", title: "Site plan · ravine, road, 2-mile trail", kind: "plan", level: byId.F1, site: true, fit: [-420, -960, 1050, 1150] },
    ...plans.map((id, i): Sheet => ({
      no: `A-10${i + 1}`,
      title: `${byId[id].name} · ${fmtElev(byId[id].elevation)}`,
      kind: "plan", level: byId[id], site: false, fit: [-48, -42, 100, 92],
    })),
    ...model.views.sections.map((sec, i): Sheet => {
      const L = Math.hypot(sec.to[0] - sec.from[0], sec.to[1] - sec.from[1]);
      return { no: `A-30${i + 1}`, title: sec.name, kind: "section", sec, fit: [-5, -16, L + 24, 54] };
    }),
  ];
  return sheets;
}

export default function App() {
  const sheets = useMemo(buildSheets, []);
  const [idx, setIdx] = useState(() => Math.max(0, sheets.findIndex((s) => "#" + s.no === location.hash)));
  const sheet = sheets[idx];
  const [layers, setLayers] = useState<Layers>({ underlay: false, terrain: true, people: false, labels: false });
  const [vb, setVb] = useState(sheet.fit);
  const [hover, setHover] = useState("");
  const svgRef = useRef<SVGSVGElement>(null);
  const drag = useRef<{ x: number; y: number; vb: typeof vb } | null>(null);
  const [figs, setFigs] = useState<FigState>(() => {
    try { return { on: false, x: 0, y: 0, n: 5, rot: 0, ...JSON.parse(localStorage.getItem("gym-figs") ?? "{}") }; }
    catch { return { on: false, x: 0, y: 0, n: 5, rot: 0 }; }
  });
  useEffect(() => localStorage.setItem("gym-figs", JSON.stringify(figs)), [figs]);
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem("gym-theme");
    return saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  });
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("gym-theme", dark ? "dark" : "light");
  }, [dark]);
  const figDrag = useRef<{ x: number; y: number; fx: number; fy: number } | null>(null);

  useEffect(() => {
    setVb(sheet.fit);
    history.replaceState(null, "", "#" + sheet.no);
  }, [sheet]);

  // keep viewBox aspect matched to the element so 1 m is square
  const [size, setSize] = useState({ w: 1, h: 1 });
  useEffect(() => {
    const el = svgRef.current!;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const pxPerM = Math.min(size.w / vb[2], size.h / vb[3]);
  const view = [
    vb[0] + vb[2] / 2 - size.w / pxPerM / 2,
    vb[1] + vb[3] / 2 - size.h / pxPerM / 2,
    size.w / pxPerM,
    size.h / pxPerM,
  ];
  const paperScale = Math.round((1000 * 96) / (25.4 * pxPerM) / 10) * 10;

  const onWheel = useCallback(
    (e: React.WheelEvent) => {
      const r = svgRef.current!.getBoundingClientRect();
      const mx = view[0] + ((e.clientX - r.left) / r.width) * view[2];
      const my = view[1] + ((e.clientY - r.top) / r.height) * view[3];
      const k = Math.exp(e.deltaY * 0.0015);
      setVb([mx - (mx - vb[0]) * k, my - (my - vb[1]) * k, vb[2] * k, vb[3] * k]);
    },
    [vb, view],
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown" || e.key === "j") setIdx((i) => Math.min(sheets.length - 1, i + 1));
      if (e.key === "ArrowUp" || e.key === "k") setIdx((i) => Math.max(0, i - 1));
      if (e.key === "f") setVb(sheet.fit);
      if (e.key === "d" || e.key === "D") setDark((v) => !v);
      if (e.key === "r" || e.key === "R") setFigs((f) => ({ ...f, rot: (f.rot + 90) % 360 }));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sheets, sheet]);

  return (
    <div className="app">
      <aside className="sheets">
        <div className="proj">
          <div className="proj-name">THE GYM</div>
          <div className="proj-sub">Drawing set · schematic</div>
        </div>
        <button className="theme-btn" onClick={() => setDark((v) => !v)}>{dark ? "☀ Light mode" : "☾ Dark mode"} <span className="mono">(D)</span></button>
        {sheets.map((s, i) => (
          <button key={s.no} className={i === idx ? "sheet on" : "sheet"} onClick={() => setIdx(i)}>
            <span className="no">{s.no}</span>
            <span className="ti">{s.title}</span>
          </button>
        ))}
        <div className="layers">
          {(Object.keys(layers) as (keyof Layers)[]).map((k) => (
            <label key={k}>
              <input type="checkbox" checked={layers[k]} onChange={() => setLayers({ ...layers, [k]: !layers[k] })} />
              {k === "underlay" ? "Gym V2 underlay" : k}
            </label>
          ))}
        </div>
        <div className="figs-tool">
          <label>
            <input type="checkbox" checked={figs.on} onChange={() => {
              // first time on: drop the row in the middle of the current view
              setFigs((f) => (f.on ? { ...f, on: false } : { ...f, on: true, ...(f.x === 0 && f.y === 0 ? { x: vb[0] + vb[2] * 0.4, y: vb[1] + vb[3] * 0.5 } : {}) }));
            }} />
            Scale people (6 ft, lying)
          </label>
          {figs.on && (
            <div className="figs-ctl">
              <button onClick={() => setFigs((f) => ({ ...f, n: Math.max(1, f.n - 1) }))}>−</button>
              <span className="mono">{figs.n}</span>
              <button onClick={() => setFigs((f) => ({ ...f, n: Math.min(60, f.n + 1) }))}>+</button>
              <button onClick={() => setFigs((f) => ({ ...f, rot: (f.rot + 90) % 360 }))}>⟳ 90°</button>
              <button onClick={() => setFigs((f) => ({ ...f, x: vb[0] + vb[2] * 0.4, y: vb[1] + vb[3] * 0.5 }))}>here</button>
            </div>
          )}
        </div>
        <div className="legend">
          <div><i className="sw new" /> new design</div>
          <div><i className="sw cut" /> cut (existing / Gym V2)</div>
          <div><i className="sw below" /> below cut</div>
          <div><i className="sw above" /> above cut</div>
          <div><i className="sw water" /> river</div>
        </div>
      </aside>

      <main
        className="paper"
        onMouseOver={(e) => setHover((e.target as Element).closest("[data-n]")?.getAttribute("data-n") ?? "")}
      >
        <svg
          ref={svgRef}
          viewBox={view.join(" ")}
          onWheel={onWheel}
          onMouseDown={(e) => (drag.current = { x: e.clientX, y: e.clientY, vb })}
          onMouseMove={(e) => {
            if (figDrag.current) {
              const d = figDrag.current;
              setFigs((f) => ({ ...f, x: d.fx + (e.clientX - d.x) / pxPerM, y: d.fy + (e.clientY - d.y) / pxPerM }));
              return;
            }
            if (!drag.current) return;
            const d = drag.current;
            setVb([d.vb[0] - (e.clientX - d.x) / pxPerM, d.vb[1] - (e.clientY - d.y) / pxPerM, d.vb[2], d.vb[3]]);
          }}
          onMouseUp={() => { drag.current = null; figDrag.current = null; }}
          onMouseLeave={() => { drag.current = null; figDrag.current = null; }}
        >
          <defs>
            <pattern id="hatch-existing" patternUnits="userSpaceOnUse" width="0.35" height="0.35" patternTransform="rotate(45)">
              <line x1="0" y1="0" x2="0" y2="0.35" className="hatch-line" />
            </pattern>
            <pattern id="hatch-timber" patternUnits="userSpaceOnUse" width="0.12" height="0.12" patternTransform="rotate(-45)">
              <line x1="0" y1="0" x2="0" y2="0.12" className="timber-line" />
            </pattern>
            <pattern id="hatch-earth" patternUnits="userSpaceOnUse" width="1.6" height="1.6" patternTransform="rotate(45)">
              <line x1="0" y1="0" x2="0" y2="1.6" className="earth-line" />
              <line x1="0.5" y1="0" x2="0.5" y2="1.6" className="earth-line" />
            </pattern>
          </defs>
          {sheet.kind === "plan" ? (
            <Plan model={model} underlay={underlay} level={sheet.level} layers={layers} site={sheet.site} />
          ) : (
            <Section model={model} underlay={underlay} sec={sheet.sec} layers={layers} />
          )}
          <Figures s={figs} onGrab={(e) => { e.stopPropagation(); figDrag.current = { x: e.clientX, y: e.clientY, fx: figs.x, fy: figs.y }; }} />
        </svg>

        <div className="titleblock">
          <div className="tb-row tb-big">
            <span>{sheet.no}</span>
            <span>{sheet.title}</span>
          </div>
          <div className="tb-row">
            <span>Scale</span><span>≈ 1:{paperScale} on screen</span>
          </div>
          <div className="tb-row">
            <span>Datum</span><span>{model.project.datum.label}</span>
          </div>
          <div className="tb-row">
            <span>Rev</span><span className="mono">{__REV__}</span>
          </div>
          <div className="tb-row">
            <span>Drawn</span><span>R. Slack + Claude</span>
          </div>
        </div>
        <div className="status mono">{hover || "scroll to zoom · drag to pan · f to fit · ↑↓ sheets · D dark mode"}</div>
      </main>
    </div>
  );
}

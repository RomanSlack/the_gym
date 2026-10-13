import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { model as currentModel, underlay as currentUnderlay, fmtElev } from "./model";
import type { Model, Underlay } from "./model";
import { ReplayBar, loadVersion, type Version } from "./draw/Replay";
import type { Level, SectionDef } from "./model";
import { Plan, type Layers } from "./draw/Plan";
import { Section } from "./draw/Section";
import { Figures, type FigState } from "./draw/Figures";
import { Elevation } from "./draw/Elevation";
import { Schedules } from "./draw/Schedules";

type Fit = [number, number, number, number];
type Sheet = ({ kind: "plan"; level: Level; site: boolean } | { kind: "section"; sec: SectionDef } | { kind: "elevation"; sec: SectionDef } | { kind: "schedule" })
  & { no: string; title: string; fit: Fit; scale: number };

const model = currentModel; // sheets come from the current design
const ELEVATIONS: SectionDef[] = [
  { id: "W", name: "West elevation · back of the gym, stair towers + garden", from: [-75, 42], to: [-75, -50] },
  { id: "N", name: "North elevation · falls side, W3 exit, decks", from: [68, 52], to: [-58, 52] },
  { id: "E", name: "East elevation · arrival, reception + daycare", from: [75, -50], to: [75, 42] },
  { id: "S", name: "South elevation · ravine downstream", from: [-58, -56], to: [68, -56] },
];
const PAPER = { w: 841, h: 594, tbW: 175 }; // A1 landscape, mm
const today = new Date().toISOString().slice(0, 10);
function buildSheets(): Sheet[] {
  const byId = Object.fromEntries(model.levels.map((l) => [l.id, l]));
  const plans = ["F1", "F2", "E2", "F3", "F4"].filter((id) => byId[id]);
  const sheets: Sheet[] = [
    { no: "A-100", title: "Site plan · ravine, road, 2-mile trail", kind: "plan", level: byId.F1, site: true, fit: [-420, -960, 1050, 1150], scale: 2500 },
    ...plans.map((id, i): Sheet => ({
      no: `A-10${i + 1}`,
      title: `${byId[id].name} · ${fmtElev(byId[id].elevation)}`,
      kind: "plan", level: byId[id], site: false, fit: [-52, -46, 108, 100], scale: 200,
    })),
    { no: "A-106", title: "Roof plan", kind: "plan", level: byId.RF, site: false, fit: [-52, -46, 108, 100], scale: 200 },
    ...ELEVATIONS.map((sec, i): Sheet => {
      const L = Math.hypot(sec.to[0] - sec.from[0], sec.to[1] - sec.from[1]);
      return { no: `A-20${i + 1}`, title: sec.name, kind: "elevation", sec, fit: [-5, -16, L + 16, 46], scale: 200 };
    }),
    ...model.views.sections.map((sec, i): Sheet => {
      const L = Math.hypot(sec.to[0] - sec.from[0], sec.to[1] - sec.from[1]);
      return { no: `A-30${i + 1}`, title: sec.name, kind: "section", sec, fit: [-5, -16, L + 24, 54], scale: 200 };
    }),
    { no: "A-601", title: "Schedules · rooms, doors, areas", kind: "schedule", fit: [0, 0, 841, 594], scale: 0 },
  ];
  return sheets;
}

export default function App() {
  const sheets = useMemo(buildSheets, []);
  const [idx, setIdx] = useState(() => Math.max(0, sheets.findIndex((s) => "#" + s.no === location.hash)));
  const sheet = sheets[idx];
  const [layers, setLayers] = useState<Layers>({ underlay: false, terrain: true, people: false, labels: false });
  const [vb, setVb] = useState(sheet.fit);
  const [paper, setPaper] = useState(() => new URLSearchParams(location.search).has("print"));
  const exportMode = new URLSearchParams(location.search).has("export"); // full-bleed A1 page for PDF export
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
  // replay: versions from tools/replay/build_history.py, shown in place of the current design
  const [versions, setVersions] = useState<Version[] | null>(null);
  const [vIdx, setVIdx] = useState(0);
  const [shown, setShown] = useState<{ model: Model; underlay: Underlay }>({ model: currentModel, underlay: currentUnderlay });
  const openReplay = async () => {
    try {
      const idx = await (await fetch("/history/index.json")).json();
      setVersions(idx.commits); setVIdx(0);
    } catch { alert("No replay data yet: run  python3 tools/replay/build_history.py"); }
  };
  useEffect(() => {
    if (!versions) { setShown({ model: currentModel, underlay: currentUnderlay }); return; }
    let live = true;
    loadVersion(versions[vIdx], currentUnderlay).then((s) => live && setShown(s));
    return () => { live = false; };
  }, [versions, vIdx]);
  // early versions had no new design yet: show Gym V2 (what we were working from) automatically
  const shownLayers = versions && shown.model.elements.length === 0 ? { ...layers, underlay: true, labels: true } : layers;
  const versionsRef = useRef(versions); versionsRef.current = versions;
  const openReplayRef = useRef(openReplay); openReplayRef.current = openReplay;
  const figDrag = useRef<{ x: number; y: number; fx: number; fy: number } | null>(null);

  useEffect(() => {
    setVb(paper || sheet.kind === "schedule" ? [0, 0, PAPER.w, PAPER.h] : sheet.fit);
    history.replaceState(null, "", "#" + sheet.no);
  }, [sheet, paper]);

  // keep viewBox aspect matched to the element so 1 m is square
  const [size, setSize] = useState({ w: 1, h: 1 });
  useEffect(() => {
    const el = svgRef.current!;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const isPaper = paper || sheet.kind === "schedule";
  const pxPerM = Math.min(size.w / vb[2], size.h / vb[3]);
  const drawing = sheet.kind === "plan" ? <Plan model={shown.model} underlay={shown.underlay} level={sheet.level} layers={shownLayers} site={sheet.site} />
    : sheet.kind === "section" ? <Section model={shown.model} underlay={shown.underlay} sec={sheet.sec} layers={shownLayers} />
    : sheet.kind === "elevation" ? <Elevation model={shown.model} underlay={shown.underlay} sec={sheet.sec} />
    : <Schedules model={shown.model} />;
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
      if (e.key === "p" || e.key === "P") setPaper((v) => !v);
      if (e.key === "d" || e.key === "D") setDark((v) => !v);
      if (e.key === "h" || e.key === "H") (versionsRef.current ? setVersions(null) : openReplayRef.current());
      if (e.key === "r" || e.key === "R") setFigs((f) => ({ ...f, rot: (f.rot + 90) % 360 }));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sheets, sheet]);

  return (
    <div className={exportMode ? "app export" : "app"}>
      <aside className="sheets">
        <div className="proj">
          <div className="proj-name">THE GYM</div>
          <div className="proj-sub">Drawing set · schematic</div>
        </div>
        <button className="theme-btn" onClick={() => (versions ? setVersions(null) : openReplay())}>{versions ? "⏹ Exit replay" : "⏵ Replay history"} <span className="mono">(H)</span></button>
        <button className="theme-btn" onClick={() => setPaper((v) => !v)}>{paper ? "▭ Screen view" : "▤ A1 sheet view"} <span className="mono">(P)</span></button>
        <button className="theme-btn" onClick={() => setDark((v) => !v)}>{dark ? "☀ Light mode" : "☾ Dark mode"} <span className="mono">(D)</span></button>
        <a className="theme-btn" href="/layout.html" style={{ display: "block", textDecoration: "none", color: "inherit" }}>▦ Layouts · locker rooms (2D)</a>
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
          {isPaper ? <PaperSheet sheet={sheet} drawing={drawing} /> : drawing}
          {!isPaper && <Figures s={figs} onGrab={(e) => { e.stopPropagation(); figDrag.current = { x: e.clientX, y: e.clientY, fx: figs.x, fy: figs.y }; }} />}
        </svg>

        <div className="titleblock" style={{ display: isPaper ? "none" : undefined }}>
          <div className="tb-row tb-big">
            <span>{sheet.no}</span>
            <span>{sheet.title}</span>
          </div>
          <div className="tb-row">
            <span>Scale</span><span>{sheet.scale ? `1:${sheet.scale} @ A1` : "n/a"} · ≈ 1:{paperScale} on screen</span>
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
        {versions && <ReplayBar versions={versions} index={vIdx} setIndex={setVIdx} onClose={() => setVersions(null)} />}
        <div className="status mono">{hover || "scroll to zoom · drag to pan · f to fit · ↑↓ sheets · D dark mode"}</div>
      </main>
    </div>
  );
}

/** A1 sheet: border, drawing at true scale in its frame, legend and title block (all in mm). */
function PaperSheet({ sheet, drawing }: { sheet: Sheet; drawing: React.ReactNode }) {
  const m = 12, dx1 = PAPER.w - m - PAPER.tbW - 4;
  const area = { x: m + 3, y: m + 3, w: dx1 - m - 6, h: PAPER.h - 2 * m - 6 };
  const k = sheet.scale ? 1000 / sheet.scale : 1;
  const [fx, fy, fw, fh] = sheet.fit;
  const tx = area.x + area.w / 2, ty = area.y + area.h / 2;
  const rows: [string, string][] = [
    ["Project", "THE GYM · luxury Nordic gym"], ["Site", "Elverum, Norway · 60.957 N 11.374 E"],
    ["Client", "Roman Slack"], ["Drawn", "R. Slack + Claude (vibe-coded)"],
    ["Scale", sheet.scale ? `1:${sheet.scale} @ A1` : "as shown"], ["Date", today],
    ["Rev", `${__REV__} (git)`], ["Status", "SCHEMATIC DESIGN · not for construction"],
  ];
  const tbx = dx1 + 4, tby = PAPER.h - m - 128;
  return (
    <g className="paper-sheet">
      <rect x={0} y={0} width={PAPER.w} height={PAPER.h} className="ps-page" />
      <rect x={m} y={m} width={PAPER.w - 2 * m} height={PAPER.h - 2 * m} className="ps-border" />
      <line x1={dx1} y1={m} x2={dx1} y2={PAPER.h - m} className="ps-border" />
      <defs><clipPath id="ps-clip"><rect x={area.x} y={area.y} width={area.w} height={area.h} /></clipPath></defs>
      <g clipPath="url(#ps-clip)">
        {sheet.kind === "schedule" ? drawing : (
          <g transform={`translate(${tx} ${ty}) scale(${k}) translate(${-(fx + fw / 2)} ${-(fy + fh / 2)})`}>{drawing}</g>
        )}
      </g>
      <g transform={`translate(${tbx} ${m + 6})`} className="ps-legend">
        <text className="ps-h">LEGEND</text>
        {[["ps-sw-wall", "Concrete / stone (cut)"], ["ps-sw-part", "Partition (cut)"], ["ps-sw-glass", "Glazing"], ["ps-sw-timber", "Glulam / timber"],
          ["ps-sw-water", "River / pool"], ["ps-sw-earth", "Earth / rock"]].map(([c, t], i) => (
          <g key={c} transform={`translate(0 ${7 + i * 6})`}><rect width={8} height={3.6} y={-2.9} className={c} /><text x={11} className="ps-t">{t}</text></g>
        ))}
        <text y={50} className="ps-t">Dimensions in metres · levels relative to ±0.00 = F1 (496.30 masl)</text>
        <text y={55} className="ps-t">Doors only where needed; open doorways elsewhere (open-plan principle)</text>
        <text y={60} className="ps-t">Gym V2 (Roman's hand-made massing) = grey underlay where shown</text>
      </g>
      <g transform={`translate(${tbx} ${tby})`} className="ps-tb">
        <rect width={PAPER.tbW} height={128} className="ps-border" />
        <text x={4} y={11} className="ps-title">THE GYM</text>
        <text x={4} y={17} className="ps-t">Elverum · Norway</text>
        {rows.map(([a, b], i) => (
          <g key={a} transform={`translate(0 ${24 + i * 7})`}>
            <line x1={0} x2={PAPER.tbW} y1={-4.6} y2={-4.6} className="ps-rule" />
            <text x={4} className="ps-k">{a}</text><text x={28} className="ps-t">{b}</text>
          </g>
        ))}
        <line x1={0} x2={PAPER.tbW} y1={81} y2={81} className="ps-border" />
        <text x={4} y={97} className="ps-no">{sheet.no}</text>
        <text x={4} y={108} className="ps-sheet">{sheet.title.length > 52 ? sheet.title.slice(0, 52) + "…" : sheet.title}</text>
        <text x={4} y={121} className="ps-k">github.com/RomanSlack/the_gym</text>
      </g>
    </g>
  );
}

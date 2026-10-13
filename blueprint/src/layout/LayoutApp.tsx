// Layouts · F1 locker rooms (Roman, 2026-10-12): the rooms top-down in 2D, exact dimensions, every element at true size, before any
// 3D. Walls / openings / columns / rooms come from model/building.json; the elements from model/layouts/lockers.json (written by
// tools/locker_layout.py, then edited here and saved back through the dev server's /api/layout).
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import modelJson from "../../../model/building.json";

type Pt = [number, number];
interface Item {
  id: string; room: string; kind: string; label: string;
  x?: number; y?: number; w?: number; d?: number; rot?: number; h?: number; n?: number;
  r_in?: number; r_out?: number; mouth?: number;
  pts?: Pt[]; width?: number; cls?: string; status?: string; need?: number;
}
interface Kind { label: string; d: number; h: number; unit?: number; clear?: number; mat: string }
interface Layout { note: string; rooms: string[]; view: [number, number, number, number]; kinds: Record<string, Kind>; items: Item[] }
interface Wall { id: string; type: string; kind?: string; material: string; from: Pt; to: Pt; size: [number, number]; z: [number, number]; openings?: { s: [number, number]; z: [number, number]; type: string }[] }
interface Space { id: string; level: string; name: string; poly: Pt[] }

const model = modelJson as unknown as { elements: (Wall & { at?: Pt })[]; spaces: Space[] };
const CUT = 1.0; // plan cut height above F1
const SNAP = 0.025;
const snap = (v: number, on: boolean) => (on ? Math.round(v / SNAP) * SNAP : Math.round(v * 1000) / 1000);
const f2 = (v: number) => v.toFixed(2);

const TAG: Record<string, string> = {
  lockers: "L", bench: "bench", shoe_bench: "shoes off", towels: "towels", towel_return: "towel return", shower: "SH", shower_acc: "SH ♿",
  wc: "WC", wc_acc: "WC ♿", urinal: "U", vanity: "vanity", grooming: "grooming", cleaner: "clean", robe_hooks: "robes + sandals",
  towel_warmer: "warmer", fossen: "FOSSEN", wash_station: "wash", spring_basin: "spring", bridge_slab: "", screen: "", oak_block: "",
  slipper_rack: "slippers UV", partition: "", floor_zone: "", robot: "🤖", robot_dock: "dock", uvc_plate: "UV-C", far_uvc: "UVC",
};
const MAT: Record<string, [string, string]> = { // fill, stroke
  oak: ["#e4cfa8", "#8a6a3a"], oak_solid: ["#efe2c6", "#8a6a3a"], walnut: ["#9b6b45", "#4f3420"], mirror: ["#cfdde3", "#4a6b78"],
  steel: ["#4a4c50", "#1e1f22"], wet: ["#dfe9ee", "#5b8aa3"], wet_feature: ["#c6dbe5", "#2f6683"], wc: ["#f4f4f2", "#555"],
  stone: ["#c9c6be", "#5d5a52"], water: ["#9fc7d9", "#2f6683"], zone: ["rgba(120, 110, 95, 0.10)", "rgba(120, 110, 95, 0.6)"], wall: ["#555", "#333"], robot: ["#d6b98a", "#2a2a2a"], uvc: ["rgba(140, 110, 220, 0.25)", "#6b4fc4"],
};

function rectPts(it: Item, w = it.w ?? 1, d = it.d ?? 1, dy = 0): Pt[] {
  const r = ((it.rot ?? 0) * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r);
  const loc: Pt[] = [[-w / 2, -d / 2 + dy], [w / 2, -d / 2 + dy], [w / 2, d / 2 + dy], [-w / 2, d / 2 + dy]];
  return loc.map(([x, y]) => [it.x! + x * c - y * s, it.y! + x * s + y * c]);
}
const path = (pts: Pt[], close = true) => "M" + pts.map(([x, y]) => `${x} ${-y}`).join("L") + (close ? "Z" : "");

function wallPolys(w: Wall): Pt[][] {
  const [ax, ay] = w.from, [bx, by] = w.to, L = Math.hypot(bx - ax, by - ay);
  const ux = (bx - ax) / L, uy = (by - ay) / L, t = w.size[0] / 2, nx = -uy * t, ny = ux * t;
  const cuts = (w.openings ?? []).filter((o) => o.z[0] <= CUT && o.z[1] >= CUT).map((o) => o.s).sort((a, b) => a[0] - b[0]);
  const segs: [number, number][] = []; let s0 = 0;
  for (const [a, b] of cuts) { if (a > s0) segs.push([s0, a]); s0 = Math.max(s0, b); }
  if (s0 < L) segs.push([s0, L]);
  return segs.map(([a, b]) => [[ax + ux * a + nx, ay + uy * a + ny], [ax + ux * b + nx, ay + uy * b + ny], [ax + ux * b - nx, ay + uy * b - ny], [ax + ux * a - nx, ay + uy * a - ny]]);
}

function polyArea(p: Pt[]) { let a = 0; for (let i = 0; i < p.length; i++) { const [x0, y0] = p[i], [x1, y1] = p[(i + 1) % p.length]; a += x0 * y1 - x1 * y0; } return Math.abs(a / 2); }

export default function LayoutApp() {
  const [data, setData] = useState<Layout | null>(null);
  const [sel, setSel] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);
  const [msg, setMsg] = useState("");
  const [vb, setVb] = useState<[number, number, number, number]>([-36.5, -12.5, 30, 25]);
  const [showClear, setShowClear] = useState(true);
  const [snapOn, setSnapOn] = useState(true);
  const [showFlow, setShowFlow] = useState(true);
  const undo = useRef<string[]>([]);
  const svgRef = useRef<SVGSVGElement>(null);
  const drag = useRef<{ kind: "item" | "pan"; x: number; y: number; ox: number; oy: number; vb: typeof vb; pts?: Pt[] } | null>(null);

  useEffect(() => {
    fetch("/api/layout?name=lockers").then((r) => r.json()).then((d: Layout) => {
      setData(d);
      const q = new URLSearchParams(location.search).get("view");  // ?view=x0,y0,x1,y1 in project metres (y north)
      if (q) { const [x0, y0, x1, y1] = q.split(",").map(Number); setVb([x0, -y1, x1 - x0, y1 - y0]); } else setVb(d.view);
    });
  }, []);

  const rooms = useMemo(() => (data ? model.spaces.filter((s) => s.level === "F1" && (data.rooms.includes(s.id) || s.id.startsWith("lift-") && s.id.endsWith("F1"))) : []), [data]);
  const bbox = useMemo(() => { const [x, y, w, h] = vb; return { x0: x - 2, x1: x + w + 2, y0: -(y + h) - 2, y1: -y + 2 }; }, [vb]);
  const walls = useMemo(() => model.elements.filter((e) => e.type === "wall" && e.z[0] <= CUT && e.z[1] >= CUT && e.from && e.to &&
    Math.max(e.from[0], e.to[0]) > -40 && Math.min(e.from[0], e.to[0]) < -4 && Math.max(e.from[1], e.to[1]) > -14 && Math.min(e.from[1], e.to[1]) < 16 && e.kind !== "lining"), []);
  const cols = useMemo(() => model.elements.filter((e) => e.type === "column" && e.at && e.z[0] <= CUT && e.z[1] >= CUT && e.at[0] > -40 && e.at[0] < -4 && e.at[1] > -14 && e.at[1] < 16), []);
  void bbox;

  const commit = useCallback((fn: (d: Layout) => Layout) => {
    setData((d) => { if (!d) return d; undo.current.push(JSON.stringify(d)); if (undo.current.length > 200) undo.current.shift(); return fn(d); });
    setDirty(true);
  }, []);
  const save = useCallback(async () => {
    if (!data) return;
    await fetch("/api/layout?name=lockers", { method: "POST", body: JSON.stringify(data, null, 1) });
    setDirty(false); setMsg("saved " + new Date().toLocaleTimeString());
  }, [data]);
  const upd = (id: string, patch: Partial<Item>) => commit((d) => ({ ...d, items: d.items.map((i) => (i.id === id ? { ...i, ...patch } : i)) }));

  // screen <-> world
  const [size, setSize] = useState({ w: 1, h: 1 });
  const loaded = data !== null;
  useEffect(() => {
    const el = svgRef.current; if (!el) return;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight })); ro.observe(el); return () => ro.disconnect();
  }, [loaded]);
  const ppm = Math.min(size.w / vb[2], size.h / vb[3]);
  const view = [vb[0] + vb[2] / 2 - size.w / ppm / 2, vb[1] + vb[3] / 2 - size.h / ppm / 2, size.w / ppm, size.h / ppm];
  const toWorld = (cx: number, cy: number): Pt => { const r = svgRef.current!.getBoundingClientRect(); return [view[0] + ((cx - r.left) / r.width) * view[2], -(view[1] + ((cy - r.top) / r.height) * view[3])]; };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "INPUT") return;
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); save(); return; }
      if ((e.ctrlKey || e.metaKey) && e.key === "z") { const u = undo.current.pop(); if (u) { setData(JSON.parse(u)); setDirty(true); } return; }
      if (!sel || !data) return;
      const it = data.items.find((i) => i.id === sel); if (!it) return;
      const st = e.shiftKey ? 0.01 : 0.05;
      const mv = (dx: number, dy: number) => {
        if (it.pts) upd(it.id, { pts: it.pts.map(([x, y]) => [Math.round((x + dx) * 1000) / 1000, Math.round((y + dy) * 1000) / 1000] as Pt) });
        else upd(it.id, { x: Math.round((it.x! + dx) * 1000) / 1000, y: Math.round((it.y! + dy) * 1000) / 1000 });
      };
      if (e.key === "ArrowLeft") { e.preventDefault(); mv(-st, 0); }
      if (e.key === "ArrowRight") { e.preventDefault(); mv(st, 0); }
      if (e.key === "ArrowUp") { e.preventDefault(); mv(0, st); }
      if (e.key === "ArrowDown") { e.preventDefault(); mv(0, -st); }
      if (e.key === "r" || e.key === "R") upd(it.id, { rot: (((it.rot ?? 0) + (e.shiftKey ? -90 : 90)) + 540) % 360 - 180 });
      if (e.key === "[" || e.key === "]") upd(it.id, { rot: (it.rot ?? 0) + (e.key === "]" ? 15 : -15) });
      if (e.key === "Delete" || e.key === "Backspace") { commit((d) => ({ ...d, items: d.items.filter((i) => i.id !== it.id) })); setSel(null); }
      if (e.key === "d" && !e.ctrlKey) {
        const nid = it.id + "-copy" + Math.floor(Math.random() * 1000);
        commit((d) => ({ ...d, items: [...d.items, { ...it, id: nid, ...(it.pts ? { pts: it.pts.map(([x, y]) => [x + 0.5, y - 0.5] as Pt) } : { x: it.x! + 0.5, y: it.y! - 0.5 }) }] }));
        setSel(nid);
      }
      if (e.key === "Escape") setSel(null);
      if (e.key === "f") setVb(data.view);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
  useEffect(() => { const b = (e: BeforeUnloadEvent) => { if (dirty) { e.preventDefault(); } }; window.addEventListener("beforeunload", b); return () => window.removeEventListener("beforeunload", b); }, [dirty]);

  if (!data) return <div className="lay-loading">loading layout…</div>;
  const selIt = data.items.find((i) => i.id === sel) ?? null;
  const counts: Record<string, number> = {};
  for (const it of data.items) if (it.kind === "lockers" || it.kind === "locker_ring") counts[it.room] = (counts[it.room] ?? 0) + (it.n ?? 0);

  const renderItem = (it: Item) => {
    const k = data.kinds[it.kind] ?? { label: it.kind, d: 0.5, h: 1, mat: "stone" };
    const [fill, stroke] = MAT[k.mat] ?? MAT.stone;
    const on = it.id === sel;
    const grab = (e: React.MouseEvent) => {
      e.stopPropagation(); setSel(it.id);
      const [wx, wy] = toWorld(e.clientX, e.clientY);
      undo.current.push(JSON.stringify(data));
      drag.current = { kind: "item", x: wx, y: wy, ox: it.x ?? 0, oy: it.y ?? 0, vb, pts: it.pts };
    };
    const cls = on ? "it on" : "it";
    if (it.kind === "route" || it.kind === "width_check") return null;
    if (it.kind === "stream" && it.pts) {
      return (
        <g key={it.id} className={cls} onMouseDown={grab}>
          <path d={path(it.pts, false)} style={{ stroke: "#2f6683", strokeWidth: (it.width ?? 0.35) + 0.08, fill: "none", strokeLinejoin: "round", strokeLinecap: "round" }} />
          <path d={path(it.pts, false)} style={{ stroke: "#9fc7d9", strokeWidth: it.width ?? 0.35, fill: "none", strokeLinejoin: "round", strokeLinecap: "round" }} />
          <path d={path(it.pts, false)} className="flow" style={{ strokeWidth: 0.03 }} />
        </g>
      );
    }
    if (it.kind === "locker_ring") {
      const ri = it.r_in ?? 1.4, ro = it.r_out ?? 1.95, n = it.n ?? 0, mouthA = (it.mouth ?? 1.2) / ri;
      const a0 = ((it.rot ?? 0) + 90) * Math.PI / 180; // the mouth's direction: rot 0 = +y
      const span = 2 * Math.PI - mouthA, start = a0 + mouthA / 2;
      const arc = (r: number, a: number): Pt => [it.x! + r * Math.cos(a), it.y! + r * Math.sin(a)];
      const sector = [...Array.from({ length: 49 }, (_, i) => arc(ro, start + (span * i) / 48)), ...Array.from({ length: 49 }, (_, i) => arc(ri, start + span - (span * i) / 48))];
      return (
        <g key={it.id} className={cls} onMouseDown={grab}>
          <circle cx={it.x} cy={-it.y!} r={ri} className="ring-floor" />
          <path d={path(sector)} style={{ fill, stroke }} />
          {Array.from({ length: n + 1 }, (_, i) => { const a = start + ((span - 0) * i) / n; const p0 = arc(ri, a), p1 = arc(ro - 0.02, a); return <line key={i} x1={p0[0]} y1={-p0[1]} x2={p1[0]} y2={-p1[1]} className="unit" />; })}
          {showClear && <circle cx={it.x} cy={-it.y!} r={ri - 0.45} className="clear" />}
          <text x={it.x} y={-it.y! - ri + 0.35} className="tag">{n} lockers</text>
        </g>
      );
    }
    if (it.kind === "round_seat") return <g key={it.id} className={cls} onMouseDown={grab}><circle cx={it.x} cy={-it.y!} r={(it.w ?? 0.8) / 2} style={{ fill, stroke }} /></g>;
    if (it.kind === "floor_zone") {
      const b = rectPts(it);
      return (
        <g key={it.id} className={cls} onMouseDown={grab}>
          <path d={path(b)} style={{ fill: "url(#zonehatch)", stroke, strokeDasharray: "0.15 0.08" }} />
          <text x={it.x} y={-(it.y! - (it.d ?? 0) / 2) - 0.12} className="zone-t">{it.label.split(":")[0]}</text>
        </g>
      );
    }
    const body = rectPts(it);
    const fr = rectPts(it, it.w, 0.02, (it.d ?? 0) / 2 - 0.01); // the front edge
    const cl = k.clear ? rectPts(it, it.w, k.clear, (it.d ?? 0) / 2 + k.clear / 2) : null;
    const n = it.n ?? 0;
    const r = ((it.rot ?? 0) * Math.PI) / 180;
    return (
      <g key={it.id} className={cls} onMouseDown={grab}>
        {showClear && cl && <path d={path(cl)} className="clear" />}
        <path d={path(body)} style={{ fill: it.kind === "oak_block" ? "url(#oakblock)" : fill, stroke }} />
        {it.kind === "lockers" && Array.from({ length: Math.max(0, n - 1) }, (_, i) => {
          const u = -(it.w ?? 0) / 2 + ((i + 1) * (it.w ?? 0)) / n; const d = (it.d ?? 0) / 2;
          const P = (y: number): Pt => [it.x! + u * Math.cos(r) - y * Math.sin(r), it.y! + u * Math.sin(r) + y * Math.cos(r)];
          const a = P(-d), b = P(d); return <line key={i} x1={a[0]} y1={-a[1]} x2={b[0]} y2={-b[1]} className="unit" />;
        })}
        {it.kind !== "oak_block" && <path d={path(fr)} className="front" />}
        {TAG[it.kind] && <text x={it.x} y={-it.y! + 0.07} className="tag">{TAG[it.kind]}{it.kind === "lockers" ? ` ${it.n}` : ""}</text>}
      </g>
    );
  };

  return (
    <div className="lay">
      <aside className="lay-side">
        <div className="proj"><div className="proj-name">THE GYM</div><div className="proj-sub">Layouts · F1 locker rooms · 2D</div></div>
        <a className="lay-link" href="/">← drawing set</a>
        <div className="lay-btns">
          <button onClick={save} className={dirty ? "hot" : ""}>{dirty ? "● Save (Ctrl S)" : "Saved"}</button>
          <button onClick={() => { const u = undo.current.pop(); if (u) { setData(JSON.parse(u)); setDirty(true); } }}>Undo (Ctrl Z)</button>
          <label><input type="checkbox" checked={showClear} onChange={() => setShowClear((v) => !v)} /> clearances</label>
          <label><input type="checkbox" checked={snapOn} onChange={() => setSnapOn((v) => !v)} /> snap 25 mm</label>
          <label><input type="checkbox" checked={showFlow} onChange={() => setShowFlow((v) => !v)} /> people flow + widths</label>
        </div>
        <div className="lay-msg mono">{msg}</div>
        <div className="lay-sec">
          <div className="lay-h">Lockers</div>
          {Object.entries(counts).map(([r, n]) => <div key={r} className="mono">{r.replace("-lockers", "")}: {n}</div>)}
        </div>
        {selIt ? (
          <div className="lay-sec">
            <div className="lay-h">{selIt.label}</div>
            <div className="lay-sub mono">{selIt.id}</div>
            {!selIt.pts && (["x", "y", "w", "d", "rot"] as const).map((f) => (
              <label key={f} className="lay-f"><span>{f}</span>
                <input type="number" step={f === "rot" ? 15 : 0.05} value={(selIt[f] as number | undefined) ?? 0}
                  onChange={(e) => upd(selIt.id, { [f]: parseFloat(e.target.value) } as Partial<Item>)} /></label>
            ))}
            {selIt.n !== undefined && <label className="lay-f"><span>units</span><input type="number" step={1} value={selIt.n}
              onChange={(e) => { const n = Math.max(1, parseInt(e.target.value)); upd(selIt.id, selIt.kind === "lockers" ? { n, w: Math.round(n * 0.4 * 1000) / 1000 } : { n }); }} /></label>}
            <div className="lay-sub">{data.kinds[selIt.kind]?.label}</div>
          </div>
        ) : <div className="lay-sec lay-sub">Click an element. Drag to move · arrows nudge 50 mm (Shift 10) · R rotate 90° · [ ] 15° · D duplicate · Del · Ctrl Z · Ctrl S · F fit</div>}
        <div className="lay-sec lay-legend">
          {Object.entries(data.kinds).map(([k, v]) => { const [fl, st] = MAT[v.mat] ?? MAT.stone; return <div key={k}><i style={{ background: fl, borderColor: st }} /> {v.label}</div>; })}
        </div>
      </aside>
      <main className="lay-main">
        <svg ref={svgRef} viewBox={view.join(" ")}
          onWheel={(e) => { const [mx, my] = toWorld(e.clientX, e.clientY); const k = Math.exp(e.deltaY * 0.0015); setVb([mx - (mx - vb[0]) * k, -my - (-my - vb[1]) * k, vb[2] * k, vb[3] * k]); }}
          onMouseDown={(e) => { setSel(null); drag.current = { kind: "pan", x: e.clientX, y: e.clientY, ox: 0, oy: 0, vb }; }}
          onMouseMove={(e) => {
            const d = drag.current; if (!d) return;
            if (d.kind === "pan") { setVb([d.vb[0] - (e.clientX - d.x) / ppm, d.vb[1] - (e.clientY - d.y) / ppm, d.vb[2], d.vb[3]]); return; }
            const [wx, wy] = toWorld(e.clientX, e.clientY);
            const dx = snap(wx - d.x, snapOn), dy = snap(wy - d.y, snapOn);
            setData((cur) => cur && ({ ...cur, items: cur.items.map((i) => (i.id === sel ? (d.pts ? { ...i, pts: d.pts.map(([x, y]) => [Math.round((x + dx) * 1000) / 1000, Math.round((y + dy) * 1000) / 1000] as Pt) }
              : { ...i, x: snap(d.ox + dx, snapOn), y: snap(d.oy + dy, snapOn) }) : i)) }));
            setDirty(true);
          }}
          onMouseUp={() => (drag.current = null)} onMouseLeave={() => (drag.current = null)}>
          <defs>
            <pattern id="zonehatch" patternUnits="userSpaceOnUse" width="0.3" height="0.3" patternTransform="rotate(45)">
              <rect width="0.3" height="0.3" fill="rgba(160, 140, 110, 0.10)" /><line x1="0" y1="0" x2="0" y2="0.3" stroke="rgba(120, 100, 70, 0.25)" strokeWidth="0.015" />
            </pattern>
            <pattern id="oakblock" patternUnits="userSpaceOnUse" width="0.25" height="0.25" patternTransform="rotate(90)">
              <rect width="0.25" height="0.25" fill="#efe2c6" /><line x1="0" y1="0" x2="0" y2="0.25" stroke="#c9ab78" strokeWidth="0.02" />
            </pattern>
          </defs>
          {rooms.map((s) => {
            const xs = s.poly.map((p) => p[0]), ys = s.poly.map((p) => p[1]);
            const cx = (Math.min(...xs) + Math.max(...xs)) / 2, top = Math.max(...ys);
            return (
              <g key={s.id}>
                <path d={path(s.poly)} className={s.id.startsWith("lift") ? "room lift" : "room"} />
                {!s.id.startsWith("lift") && <text x={cx} y={-top + 0.45} className="room-t">{s.name.split(" · ")[0]} · {polyArea(s.poly).toFixed(0)} m²</text>}
              </g>
            );
          })}
          {walls.map((w) => wallPolys(w).map((p, i) => <path key={w.id + i} d={path(p)} className={w.kind === "glazed" ? "wall glass" : w.kind === "partition" ? "wall part" : "wall"} />))}
          {cols.map((c) => <rect key={c.id} x={c.at![0] - c.size[0] / 2} y={-c.at![1] - c.size[1] / 2} width={c.size[0]} height={c.size[1]} className="col" />)}
          <Dims />
          {data.items.filter((i) => i.kind === "floor_zone").map(renderItem)}
          {data.items.filter((i) => i.kind === "oak_block").map(renderItem)}
          {data.items.filter((i) => i.kind !== "oak_block" && i.kind !== "floor_zone").map(renderItem)}
          {showFlow && <Flow items={data.items} />}
          {selIt && !selIt.pts && <SelDims it={selIt} />}
        </svg>
        <div className="lay-status mono">scroll zoom · drag empty space to pan · F fit · dims in metres to wall faces</div>
      </main>
    </div>
  );
}

/** Exact clear dimensions of each room (to the wall FACES), as dimension strings. */
function Dims() {
  const D = ({ a, b, off, horiz, label }: { a: number; b: number; off: number; horiz: boolean; label?: string }) => {
    const t = label ?? f2(Math.abs(b - a));
    return horiz ? (
      <g className="dim"><line x1={a} x2={b} y1={-off} y2={-off} /><line x1={a} x2={a} y1={-off - 0.12} y2={-off + 0.12} /><line x1={b} x2={b} y1={-off - 0.12} y2={-off + 0.12} />
        <text x={(a + b) / 2} y={-off - 0.08} className="dim-t">{t}</text></g>
    ) : (
      <g className="dim"><line y1={-a} y2={-b} x1={off} x2={off} /><line y1={-a} y2={-a} x1={off - 0.12} x2={off + 0.12} /><line y1={-b} y2={-b} x1={off - 0.12} x2={off + 0.12} />
        <text x={off - 0.1} y={-(a + b) / 2} className="dim-t" transform={`rotate(-90 ${off - 0.1} ${-(a + b) / 2})`}>{t}</text></g>
    );
  };
  return (
    <g>
      <D a={-29.375} b={-11.675} off={-10.2} horiz label="17.70 (changing rooms, wall face to wall face)" />
      <D a={-29.25} b={-11.675} off={12.6} horiz label="17.58 (wet zones)" />
      <D a={-9.225} b={-4.275} off={-30.4} horiz={false} label="4.95 men's wet" />
      <D a={-4.275} b={1.425} off={-30.4} horiz={false} label="5.70 men's changing" />
      <D a={1.575} b={7.575} off={-30.4} horiz={false} label="6.00 women's changing" />
      <D a={7.725} b={11.9} off={-30.4} horiz={false} label="4.18 women's wet" />
      <D a={-35.325} b={-29.525} off={-1.9} horiz label="5.80" />
      <D a={-11.675} b={-6.45} off={-10.2} horiz label="5.23 gallery" />
    </g>
  );
}

function SelDims({ it }: { it: Item }) {
  const w = it.w ?? 0, d = it.d ?? 0;
  return <text x={it.x! } y={-it.y! - Math.max(w, d) / 2 - 0.25} className="sel-t">{f2(w)} × {f2(d)}{it.h ? ` × ${f2(it.h)} h` : ""}{it.rot ? ` · ${it.rot}°` : ""}</text>;
}

/** People flow: the routes (arrowed) + every pinch point's clear width (green ok, amber tight, red narrow). */
function Flow({ items }: { items: Item[] }) {
  const RC: Record<string, string> = { main: "#1f6f63", shoe: "#8a5a2b", wash: "#2f6683", branch: "#6b6b6b" };
  const SC: Record<string, string> = { ok: "#2e8b57", tight: "#d18a00", narrow: "#c62828" };
  return (
    <g className="flow-layer">
      {items.filter((i) => i.kind === "route" && i.pts).map((r) => {
        const pts = r.pts!, [ax, ay] = pts[pts.length - 2], [bx, by] = pts[pts.length - 1];
        const a = Math.atan2(by - ay, bx - ax), L = 0.28;
        const head = [[bx, by], [bx - L * Math.cos(a - 0.45), by - L * Math.sin(a - 0.45)], [bx - L * Math.cos(a + 0.45), by - L * Math.sin(a + 0.45)]] as Pt[];
        const c = RC[r.cls ?? "main"];
        return (
          <g key={r.id}>
            <path d={path(pts, false)} style={{ stroke: c, strokeWidth: r.cls === "branch" ? 0.05 : 0.09, fill: "none", strokeDasharray: r.cls === "shoe" ? "0.2 0.12" : undefined, opacity: 0.85 }} />
            <path d={path(head)} style={{ fill: c, opacity: 0.9 }} />
            <title>{r.label}</title>
          </g>
        );
      })}
      {items.filter((i) => i.kind === "width_check" && i.pts).map((w) => {
        const [[ax, ay], [bx, by]] = [w.pts![0], w.pts![w.pts!.length - 1]];
        const c = SC[w.status ?? "ok"], mx = (ax + bx) / 2, my = (ay + by) / 2, vert = Math.abs(bx - ax) < Math.abs(by - ay);
        return (
          <g key={w.id}>
            <line x1={ax} y1={-ay} x2={bx} y2={-by} style={{ stroke: c, strokeWidth: 0.03 }} />
            {[[ax, ay], [bx, by]].map(([x, y], k) => <circle key={k} cx={x} cy={-y} r={0.05} style={{ fill: c }} />)}
            <text x={mx + (vert ? 0.08 : 0)} y={-my + (vert ? 0 : -0.08)} className="w-t" style={{ fill: c }} textAnchor={vert ? "start" : "middle"}>{w.width?.toFixed(2)}</text>
            <title>{w.label}</title>
          </g>
        );
      })}
    </g>
  );
}

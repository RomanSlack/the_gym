// Elevation: the building seen from outside, orthographically, looking along the left normal of from→to.
// Everything within DEPTH is projected and painted far→near (glass light blue, solid walls/towers stone,
// slabs and roofs dark edges). The ground in front of the facade then hides whatever is below grade.
import { useMemo } from "react";
import type { DesignElement, Model, SectionDef, Underlay } from "../model";
import { footprint, roofOutline, terrainAt } from "../model";
import { LevelTag, ScaleBar } from "./symbols";

const DEPTH = 140;
const BOTTOM = -22;

export function Elevation({ model, underlay, sec }: { model: Model; underlay: Underlay; sec: SectionDef }) {
  const [x0, y0] = sec.from, [x1, y1] = sec.to;
  const L = Math.hypot(x1 - x0, y1 - y0);
  const ux = (x1 - x0) / L, uy = (y1 - y0) / L, nx = -uy, ny = ux;
  const along = (x: number, y: number) => (x - x0) * ux + (y - y0) * uy;
  const depth = (x: number, y: number) => (x - x0) * nx + (y - y0) * ny;

  const items = useMemo(() => {
    const out: { e: DesignElement; s0: number; s1: number; d: number; z0: number; z1: number }[] = [];
    for (const e of model.elements) {
      let pts = footprint(e);
      let z0 = e.z[0], z1 = e.z[1];
      if (e.type === "slab" && e.id.startsWith("S-RF-") && e.material === "clt") {  // roofs carry their eaves
        const [a, b, c, d] = roofOutline(e);
        pts = [[a, b], [c, b], [c, d], [a, d]];
        if (!e.eaves) z1 = z1 + 0.35;  // older versions: eave thickness drawn on top of the 200 mm plate
      }
      const ds = pts.map(([x, y]) => depth(x, y));
      if (Math.max(...ds) < 0 || Math.min(...ds) > DEPTH) continue;
      const ss = pts.map(([x, y]) => along(x, y));
      out.push({ e, s0: Math.min(...ss), s1: Math.max(...ss), d: Math.min(...ds), z0, z1 });
    }
    return out.sort((a, b) => b.d - a.d);
  }, [model, sec]);

  // ground in front of the building: the highest terrain between the viewer and the nearest facade
  const front = items.length ? Math.min(...items.map((i) => i.d)) : 0;
  const ground = useMemo(() => {
    const pts: [number, number][] = [];
    for (let s = 0; s <= L; s += 0.5) {
      let g = -Infinity;
      for (let d = Math.max(0, front - 30); d <= front - 0.5; d += 2) {
        const v = terrainAt(underlay.terrain, x0 + ux * s + nx * d, y0 + uy * s + ny * d);
        if (!Number.isNaN(v)) g = Math.max(g, v);
      }
      pts.push([s, g === -Infinity ? NaN : g]);
    }
    return pts;
  }, [underlay, sec, front]);
  const earth = "M0 " + -BOTTOM + ground.filter(([, z]) => !Number.isNaN(z)).map(([s, z]) => `L${s} ${-z}`).join("") + `L${L} ${-BOTTOM}Z`;
  const gline = "M" + ground.filter(([, z]) => !Number.isNaN(z)).map(([s, z]) => `${s} ${-z}`).join("L");

  const cls = (e: DesignElement) =>
    e.type === "wall" ? (e.kind === "glazed" || e.material === "glass" ? "el-glass" : e.kind === "partition" ? "el-hidden" : e.material === "timber_clad" ? "el-clad" : e.kind === "trim" ? "el-trim" : "el-stone")
    : e.type === "slab" ? (e.material === "glass" ? "el-glass" : e.material === "clt" ? "el-roof" : e.material === "sod" ? "el-sod" : "el-slab")
    : e.type === "column" ? (e.material === "glulam" ? (e.finish ? "el-clad" : "el-timber") : "el-hidden") : "el-hidden";

  return (
    <g>
      {items.map(({ e, s0, s1, z0, z1 }) => (
        <g key={e.id}>
          <rect x={s0} y={-z1} width={s1 - s0} height={z1 - z0} className={cls(e)} data-n={`${e.id} · ${e.type} ${e.material}`} />
          {e.mullions && e.from && e.to && (() => {  // divided glazing: mullions + transoms
            const [fx, fy] = e.from, [tx, ty] = e.to, wl = Math.hypot(tx - fx, ty - fy);
            const ms = e.mullions.map((m) => along(fx + ((tx - fx) * m) / wl, fy + ((ty - fy) * m) / wl));
            return (
              <g className="el-mullion">
                {ms.map((x, k) => <line key={k} x1={x} y1={-z0} x2={x} y2={-z1} />)}
                {(e.transoms ?? []).map((t, k) => <line key={`t${k}`} x1={s0} y1={-t} x2={s1} y2={-t} />)}
              </g>
            );
          })()}
        </g>
      ))}
      <path d={earth} className="earth el-earth" />
      <path d={gline} className="ground-line" />
      {model.levels.filter((l) => ["RF", "F1", "F2", "F3", "F4"].includes(l.id)).map((l) => (
        <g key={l.id}>
          <line x1={-2} x2={L + 2} y1={-l.elevation} y2={-l.elevation} className="ln-level" />
          <LevelTag x={L + 3.5} y={-l.elevation} id={l.id} z={l.elevation} />
        </g>
      ))}
      <ScaleBar x={0} y={-BOTTOM + 4} />
    </g>
  );
}

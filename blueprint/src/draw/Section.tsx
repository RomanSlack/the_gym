// Vertical section along a cut line. Looking to the left of from→to, so `from`
// is on the drawing's left. Cut elements heavy with poché; elements beyond (up to
// DEPTH m behind the cut) drawn light; earth hatched below the terrain profile.
import { useMemo } from "react";
import type { Model, SectionDef, Underlay, UElement } from "../model";
import { terrainAt, waterAt } from "../model";
import { Figure, LevelTag, ScaleBar } from "./symbols";
import type { Layers } from "./Plan";

const DEPTH = 30;
const BOTTOM = -32;

export function Section({ model, underlay, sec, layers }: { model: Model; underlay: Underlay; sec: SectionDef; layers: Layers }) {
  const [x0, y0] = sec.from, [x1, y1] = sec.to;
  const L = Math.hypot(x1 - x0, y1 - y0);
  const ux = (x1 - x0) / L, uy = (y1 - y0) / L;
  const nx = -uy, ny = ux; // looking direction (left normal)
  const along = (x: number, y: number) => (x - x0) * ux + (y - y0) * uy;
  const depth = (x: number, y: number) => (x - x0) * nx + (y - y0) * ny;

  const { cut, beyond, people } = useMemo(() => {
    const cut: { e: UElement; s0: number; s1: number }[] = [];
    const beyond: { e: UElement; s0: number; s1: number; d: number }[] = [];
    const people: { e: UElement; s: number }[] = [];
    for (const e of underlay.elements) {
      if (["label", "flat_plane"].includes(e.kind)) continue;
      if (e.kind === "person") {
        const [px, py] = e.at!;
        if (Math.abs(depth(px, py)) < 4) people.push({ e, s: along(px, py) });
        continue;
      }
      if (e.center) {
        const d = depth(...e.center), s = along(...e.center), r = e.radius!;
        if (Math.abs(d) < r) {
          const h = Math.sqrt(r * r - d * d);
          cut.push({ e, s0: s - h, s1: s + h });
        } else if (d > 0 && d < DEPTH) beyond.push({ e, s0: s - r, s1: s + r, d });
        continue;
      }
      // footprint vs. infinite cut line: crossings of polygon edges
      const ds = e.plan.map(([x, y]) => depth(x, y));
      const hits: number[] = [];
      e.plan.forEach(([xa, ya], i) => {
        const [xb, yb] = e.plan[(i + 1) % e.plan.length];
        const da = ds[i], db = ds[(i + 1) % ds.length];
        if ((da <= 0 && db > 0) || (da > 0 && db <= 0)) {
          const f = da / (da - db);
          hits.push(along(xa + f * (xb - xa), ya + f * (yb - ya)));
        }
      });
      if (hits.length >= 2) {
        const s0 = Math.max(0, Math.min(...hits)), s1 = Math.min(L, Math.max(...hits));
        if (s1 > s0) cut.push({ e, s0, s1 });
      } else if (Math.min(...ds) > 0 && Math.min(...ds) < DEPTH) {
        const ss = e.plan.map(([x, y]) => along(x, y));
        const s0 = Math.min(...ss), s1 = Math.max(...ss);
        if (s1 > 0 && s0 < L) beyond.push({ e, s0, s1, d: Math.min(...ds) });
      }
    }
    return { cut, beyond, people };
  }, [underlay, sec]);

  const { earth, profile, water, lines } = useMemo(() => {
    const step = 0.5;
    const pts: [number, number][] = [];
    const wl: number[] = [];
    for (let s = 0; s <= L; s += step) {
      pts.push([s, terrainAt(underlay.terrain, x0 + ux * s, y0 + uy * s)]);
      wl.push(waterAt(underlay.terrain, x0 + ux * s, y0 + uy * s));
    }
    // split into runs with data
    const runs: [number, number][][] = [];
    let cur: [number, number][] = [];
    for (const p of pts) {
      if (Number.isNaN(p[1])) { if (cur.length) runs.push(cur); cur = []; } else cur.push(p);
    }
    if (cur.length) runs.push(cur);
    const earth = runs
      .map((r) => `M${r[0][0]} ${-BOTTOM}` + r.map(([s, z]) => `L${s} ${-z}`).join("") + `L${r[r.length - 1][0]} ${-BOTTOM}Z`)
      .join("");
    const profile = runs.map((r) => "M" + r.map(([s, z]) => `${s} ${-z}`).join("L")).join("");
    // water: wherever the site has a water surface above the ground along the cut
    const water: string[] = [];
    const lines: { s0: number; s1: number; z: number }[] = [];
    let w: [number, number, number][] = [];
    const flush = () => {
      if (w.length > 1) {
        const z = w[0][2];
        water.push(`M${w[0][0]} ${-z}` + w.map(([s, g]) => `L${s} ${-g}`).join("") + `L${w[w.length - 1][0]} ${-z}Z`);
        lines.push({ s0: w[0][0], s1: w[w.length - 1][0], z });
      }
      w = [];
    };
    pts.forEach(([s, g], k) => {
      const wet = !Number.isNaN(wl[k]) && g < wl[k];
      if (w.length && (!wet || Math.abs(wl[k] - w[0][2]) > 0.25)) flush(); // new reach: falls, sill, cascade
      if (wet) w.push([s, g, wl[k]]);
    });
    flush();
    return { earth, profile, water: water.join(""), lines };
  }, [underlay, sec]);

  const rect = (s0: number, s1: number, e: UElement) => `M${s0} ${-e.z[1]}H${s1}V${-e.z[0]}H${s0}Z`;
  const tip = (e: UElement) => `${e.name} · ${e.kind} · z ${e.z[0].toFixed(2)} to ${e.z[1].toFixed(2)}`;
  const levels = model.levels;

  return (
    <g>
      {layers.underlay &&
        beyond
          .sort((a, b) => b.d - a.d)
          .map(({ e, s0, s1 }) => <path key={e.name} d={rect(s0, s1, e)} className="u-beyond" data-n={tip(e) + " (beyond)"} />)}

      {layers.terrain && (
        <g>
          <path d={earth} className="earth" />
          <path d={water} className="water" />
          <path d={profile} className="ground-line" />
          {lines.map((l, k) => (
            <g key={k}>
              <line x1={l.s0} x2={l.s1} y1={-l.z} y2={-l.z} className="ln-water" />
              <g transform={`translate(${(l.s0 + l.s1) / 2} ${-l.z})`}>
                <path d="M-0.6 -1.1 L0.6 -1.1 L0 -0.1 Z" className="water-mark" />
                <text x={0.9} y={-0.3} className="txt-s mono">water {l.z.toFixed(2)}</text>
              </g>
            </g>
          ))}
        </g>
      )}

      {layers.underlay &&
        cut.map(({ e, s0, s1 }) => (
          <path key={e.name} d={rect(s0, s1, e)} className={e.kind === "void" ? "u-void" : "u-cut"} data-n={tip(e)} />
        ))}

      {/* new design columns crossed by the cut */}
      {model.elements
        .filter((e) => e.type === "column")
        .map((e) => {
          const [w, d] = e.size;
          const corners: [number, number][] = [[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]];
          const dd = corners.map(([cx, cy]) => depth(e.at[0] + cx, e.at[1] + cy));
          if (Math.min(...dd) > 0 || Math.max(...dd) < 0) return null;
          const ss = corners.map(([cx, cy]) => along(e.at[0] + cx, e.at[1] + cy));
          return <rect key={e.id} x={Math.min(...ss)} y={-e.z[1]} width={Math.max(...ss) - Math.min(...ss)} height={e.z[1] - e.z[0]}
            className={e.material === "glulam" ? "n-col-timber" : "n-col"} data-n={`${e.id} · ${e.material}`} />;
        })}

      {levels.map((l) => (
        <g key={l.id}>
          <line x1={-2} x2={L + 2} y1={-l.elevation} y2={-l.elevation} className="ln-level" />
          <LevelTag x={L + (l.wing === "east" ? 10 : 3.5)} y={-l.elevation} id={l.id} z={l.elevation} />
        </g>
      ))}

      {layers.people && people.map(({ e, s }) => <Figure key={e.name} x={s} z={e.at![2]} />)}

      <text x={0} y={-12} className="txt-l">{sec.id}</text>
      <text x={L} y={-12} className="txt-l" textAnchor="end">{sec.id}′</text>
      <ScaleBar x={0} y={-BOTTOM + 4} />
    </g>
  );
}

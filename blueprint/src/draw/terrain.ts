// Terrain → SVG paths. Contour lines use a plain marching-squares pass that skips
// cells with missing data (so the edge of the survey doesn't draw fake contours).
// Water uses d3-contour to get a filled region where terrain sits below the water level.
import { contours } from "d3-contour";
import type { Terrain } from "../model";

/** Path data (plan coords, y flipped) for the contour line at height `level`,
 *  plus a few spread-out points along it for elevation labels. */
export function contourPath(t: Terrain, level: number): { d: string; anchors: [number, number][] } {
  const { nx, ny, h, origin, step } = t;
  const X = (gx: number) => (origin[0] + gx * step).toFixed(2);
  const Y = (gy: number) => (-(origin[1] + gy * step)).toFixed(2);
  const out: string[] = [];
  const mids: [number, number][] = [];
  const lerp = (a: number, b: number) => (level - a) / (b - a);
  for (let j = 0; j < ny - 1; j++) {
    for (let i = 0; i < nx - 1; i++) {
      const a = h[j * nx + i], b = h[j * nx + i + 1];
      const c = h[(j + 1) * nx + i + 1], d = h[(j + 1) * nx + i];
      if (Number.isNaN(a + b + c + d)) continue;
      const code = (a > level ? 1 : 0) | (b > level ? 2 : 0) | (c > level ? 4 : 0) | (d > level ? 8 : 0);
      if (code === 0 || code === 15) continue;
      // edge midpoints: bottom (a-b), right (b-c), top (d-c), left (a-d)
      const e = {
        B: [i + lerp(a, b), j],
        R: [i + 1, j + lerp(b, c)],
        T: [i + lerp(d, c), j + 1],
        L: [i, j + lerp(a, d)],
      } as const;
      const segs: Record<number, (keyof typeof e)[][]> = {
        1: [["L", "B"]], 2: [["B", "R"]], 3: [["L", "R"]], 4: [["R", "T"]],
        5: [["L", "T"], ["B", "R"]], 6: [["B", "T"]], 7: [["L", "T"]], 8: [["T", "L"]],
        9: [["T", "B"]], 10: [["B", "L"], ["R", "T"]], 11: [["T", "R"]], 12: [["R", "L"]],
        13: [["R", "B"]], 14: [["B", "L"]],
      };
      for (const [p, q] of segs[code]) {
        out.push(`M${X(e[p][0])} ${Y(e[p][1])}L${X(e[q][0])} ${Y(e[q][1])}`);
        mids.push([+X((e[p][0] + e[q][0]) / 2), +Y((e[p][1] + e[q][1]) / 2)]);
      }
    }
  }
  const anchors: [number, number][] = [];
  for (let k = 1; k <= 4 && mids.length > 40; k++) anchors.push(mids[Math.floor((k * mids.length) / 5)]);
  return { d: out.join(""), anchors };
}

/** Filled path (plan coords) of the river and pools: every cell with a water surface. */
export function waterPath(t: Terrain): string {
  const vals = Array.from(t.water, (v) => (Number.isNaN(v) ? 0 : 1));
  const [mp] = contours().size([t.nx, t.ny]).thresholds([0.5])(vals);
  // d3-contour puts grid samples at half-integer coordinates
  const P = ([gx, gy]: number[]) =>
    `${(t.origin[0] + (gx - 0.5) * t.step).toFixed(2)} ${(-(t.origin[1] + (gy - 0.5) * t.step)).toFixed(2)}`;
  return mp.coordinates
    .map((poly) => poly.map((ring) => "M" + ring.map(P).join("L") + "Z").join(""))
    .join("");
}

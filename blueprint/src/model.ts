// Types for model/building.json and the Gym V2 underlay, plus loading into
// project coordinates (z relative to the ±0.00 datum).
import modelJson from "../../model/building.json";
import underlayJson from "../../reference/gym_v2_original/gymv2_extract.json";

export type Pt = [number, number];

export interface Level {
  id: string;
  name: string;
  elevation: number;
  wing: string;
  note?: string;
}
export interface SectionDef {
  id: string;
  name: string;
  from: Pt;
  to: Pt;
}
export interface Grid {
  id: string;
  from: Pt;
  to: Pt;
}
export interface Model {
  schema: string;
  project: { name: string; datum: { label: string; blender_z_gymv2: number; masl: number } };
  site: { water_level: number };
  levels: Level[];
  views: { plan_cut_height: number; sections: SectionDef[] };
  grids: Grid[];
  elements: unknown[];
}

export interface UElement {
  name: string;
  kind: string;
  plan: Pt[];
  z: [number, number];
  hidden: boolean;
  text?: string;
  at?: number[];
  height?: number;
  center?: Pt;
  radius?: number;
}

export interface Terrain {
  origin: Pt;
  step: number;
  nx: number;
  ny: number;
  h: Float64Array; // metres relative to datum, NaN = no data
}

export interface Underlay {
  elements: UElement[];
  terrain: Terrain;
}

/** Shift the raw Blender-z underlay onto the project datum. */
export function loadUnderlay(raw: typeof underlayJson, datumZ: number): Underlay {
  const elements = (raw.elements as unknown as UElement[])
    .filter((e) => !(e.kind === "slab" && e.hidden)) // hidden duplicate slab
    .map((e) => ({
      ...e,
      z: [e.z[0] - datumZ, e.z[1] - datumZ] as [number, number],
      at: e.at ? [e.at[0], e.at[1], e.at[2] - datumZ] : undefined,
    }));
  const t = raw.terrain;
  const h = new Float64Array(t.heights.length);
  t.heights.forEach((v, i) => (h[i] = v === null ? NaN : v / 100 - datumZ));
  return { elements, terrain: { origin: t.origin as Pt, step: t.step, nx: t.nx, ny: t.ny, h } };
}

export const model = modelJson as unknown as Model;
export const underlay = loadUnderlay(underlayJson, model.project.datum.blender_z_gymv2);

/** Bilinear terrain height at a world point (NaN outside data). */
export function terrainAt(t: Terrain, x: number, y: number): number {
  const gx = (x - t.origin[0]) / t.step;
  const gy = (y - t.origin[1]) / t.step;
  const i = Math.floor(gx), j = Math.floor(gy);
  if (i < 0 || j < 0 || i >= t.nx - 1 || j >= t.ny - 1) return NaN;
  const fx = gx - i, fy = gy - j;
  const v = (a: number, b: number) => t.h[b * t.nx + a];
  return (
    v(i, j) * (1 - fx) * (1 - fy) + v(i + 1, j) * fx * (1 - fy) +
    v(i, j + 1) * (1 - fx) * fy + v(i + 1, j + 1) * fx * fy
  );
}

const inPoly = (x: number, y: number, poly: Pt[]) => {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};

/** Ground under floors that sit below grade is building excavation, not river.
 *  (Gym V2's terrain is carved into pits for both wings.) */
const basementSlabs = underlay.elements.filter((e) => e.kind === "slab" && e.z[1] < -1);
export const isExcavation = (x: number, y: number) => basementSlabs.some((e) => inPoly(x, y, e.plan));

export const fmtElev = (z: number) =>
  Math.abs(z) < 0.005 ? "±0.00" : (z > 0 ? "+" : "−") + Math.abs(z).toFixed(2);

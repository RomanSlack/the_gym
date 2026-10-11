// Types for model/building.json and the Gym V2 underlay, plus loading into
// project coordinates (z relative to the ±0.00 datum).
import modelJson from "../../model/building.json";
import underlayJson from "../../reference/gym_v2_original/gymv2_extract.json";
import siteJson from "../../model/site_terrain.json";

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
export interface SiteFeatures {
  arrival_court: { center: Pt; size: Pt; z: number };
  road: { width: number; shoulder: number; points: [number, number, number][] };
  garage_ramp: { points: Pt[]; width: number; tunnel_from_x: number };
  daycare_garden: { rect: [number, number, number, number]; terraces: { sides: string[]; count: number; run: number } };
  sauna: { center: Pt; size: Pt; deck: { rect: [number, number, number, number] } };
  sauna_path: { points: Pt[]; width: number };
}
export interface Model {
  schema: string;
  project: { name: string; datum: { label: string; blender_z_gymv2: number; masl: number } };
  site: { water_level: number; features: SiteFeatures };
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
  water: Float64Array; // water surface, NaN = dry
}

export interface Underlay {
  elements: UElement[];
  terrain: Terrain;
}

/** Site terrain + water exported by terrain/export_blueprint.py (already relative to ±0.00). */
function loadSite(raw: typeof siteJson): Terrain {
  const h = Float64Array.from(raw.heights, (v) => v / 100);
  const water = Float64Array.from(raw.water, (v) => (v === null ? NaN : v / 100));
  return { origin: raw.origin as Pt, step: raw.step, nx: raw.nx, ny: raw.ny, h, water };
}

/** Shift the raw Blender-z Gym V2 underlay onto the project datum; terrain = the new site. */
export function loadUnderlay(raw: typeof underlayJson, datumZ: number): Underlay {
  const elements = (raw.elements as unknown as UElement[])
    .filter((e) => !(e.kind === "slab" && e.hidden)) // hidden duplicate slab
    .map((e) => ({
      ...e,
      z: [e.z[0] - datumZ, e.z[1] - datumZ] as [number, number],
      at: e.at ? [e.at[0], e.at[1], e.at[2] - datumZ] : undefined,
    }));
  return { elements, terrain: loadSite(siteJson) };
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

/** Water surface at a world point (nearest cell; NaN where dry). */
export function waterAt(t: Terrain, x: number, y: number): number {
  const i = Math.round((x - t.origin[0]) / t.step), j = Math.round((y - t.origin[1]) / t.step);
  if (i < 0 || j < 0 || i >= t.nx || j >= t.ny) return NaN;
  return t.water[j * t.nx + i];
}

export const fmtElev = (z: number) =>
  Math.abs(z) < 0.005 ? "±0.00" : (z > 0 ? "+" : "−") + Math.abs(z).toFixed(2);

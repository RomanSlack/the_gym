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
  road: { width: number; shoulder: number; points: [number, number, number][] };
  trail: { width: number; points: [number, number, number, number][]; bridges: { from: Pt; to: Pt; deck_z: number; span_m: number }[]; length_m: number };
  garage_ramp: { points: Pt[]; width: number; tunnel_from_x: number };
  daycare_garden: { curve: Pt[]; west_wall_x: number; building_edge_y: number; terraces: { count: number; run: number } };
  sauna: { center: Pt; size: Pt; deck: { rect: [number, number, number, number] } };
  sauna_path: { points: Pt[]; width: number };
  surfaces?: { id: string; kind: string; poly?: Pt[]; circle?: [number, number, number]; ring?: [number, number, number, number] }[];
  paths?: { id: string; width: number; points: Pt[] }[];
  bike_shelter?: { rect: [number, number, number, number] };
  stepping_stones?: { id: string; points: Pt[]; spacing: number; size: Pt }[];
}
export interface DesignElement {
  id: string;
  type: "column" | "beam" | "slab" | "wall";
  material: string;
  kind?: string; // walls: retaining | river_wall | glazed
  at?: Pt; // columns
  from?: Pt; // beams, walls
  to?: Pt;
  rect?: [number, number, number, number]; // slabs
  holes?: { circle?: [number, number, number]; rect?: Pt[] }[];
  openings?: { s: [number, number]; z: [number, number]; type: string; note?: string }[]; // walls: windows along the wall
  size: Pt; // column: [w, d]; beam: [width, depth]; wall: [thickness, height]
  z: [number, number];
}
export interface Space {
  id: string;
  level: string;
  kind: string;
  name: string;
  poly: Pt[];
  note?: string;
}
export interface Stair {
  id: string;
  kind: "spiral" | "straight";
  center?: Pt;
  diameter?: number;
  rect?: [number, number, number, number];
  from: string;
  to: string;
  run?: string;
}
export interface Fixture {
  id: string;
  kind: string;
  level: string;
  center?: Pt; // round fixtures
  diameter?: number;
  rect?: [number, number, number, number]; // counters
}

/** Plan footprint (4 corners) of a design element. */
export function footprint(e: DesignElement): Pt[] {
  if (e.type === "slab") {
    const [x0, y0, x1, y1] = e.rect!;
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
  }
  if (e.type === "column") {
    const [x, y] = e.at!, [w, d] = e.size;
    return [[x - w / 2, y - d / 2], [x + w / 2, y - d / 2], [x + w / 2, y + d / 2], [x - w / 2, y + d / 2]];
  }
  const [x0, y0] = e.from!, [x1, y1] = e.to!;
  const L = Math.hypot(x1 - x0, y1 - y0), hw = e.size[0] / 2; // beams and walls: width / thickness
  const nx = (-(y1 - y0) / L) * hw, ny = ((x1 - x0) / L) * hw;
  return [[x0 + nx, y0 + ny], [x1 + nx, y1 + ny], [x1 - nx, y1 - ny], [x0 - nx, y0 - ny]];
}
export interface Model {
  schema: string;
  project: { name: string; datum: { label: string; blender_z_gymv2: number; masl: number } };
  site: { water_level: number; features: SiteFeatures };
  levels: Level[];
  views: { plan_cut_height: number; sections: SectionDef[] };
  grids: Grid[];
  elements: DesignElement[];
  spaces: Space[];
  stairs: Stair[];
  fixtures: Fixture[];
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

/** Coarse 10 m grid over the whole 2 x 2 km core, for the site plan's contours. */
export const wideTerrain: Terrain = (() => {
  const w = siteJson.wide;
  const h = Float64Array.from(w.heights, (v) => v / 100);
  return { origin: w.origin as Pt, step: w.step, nx: w.nx, ny: w.ny, h, water: new Float64Array(h.length).fill(NaN) };
})();

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

export const polyArea = (p: Pt[]) =>
  Math.abs(p.reduce((a, [x, y], i) => a + x * p[(i + 1) % p.length][1] - p[(i + 1) % p.length][0] * y, 0)) / 2;

const insidePoly = (x: number, y: number, p: Pt[]) => {
  let inside = false;
  for (let i = 0, j = p.length - 1; i < p.length; j = i++) {
    const [xi, yi] = p[i], [xj, yj] = p[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};
const segDist = (x: number, y: number, [ax, ay]: Pt, [bx, by]: Pt) => {
  const dx = bx - ax, dy = by - ay, t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy || 1)));
  return Math.hypot(x - ax - t * dx, y - ay - t * dy);
};

/** Label anchor: the point deepest inside the room (max distance to its walls), plus whether the
 *  room is long and narrow enough that the label should run along it. */
export function labelPoint(p: Pt[]): { at: Pt; rotate: boolean; room: number; long: number } {
  const xs = p.map((q) => q[0]), ys = p.map((q) => q[1]);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  let best: Pt = [(x0 + x1) / 2, (y0 + y1) / 2], bd = -1;
  const step = Math.max(0.25, Math.min(x1 - x0, y1 - y0) / 12);
  for (let x = x0 + step / 2; x < x1; x += step)
    for (let y = y0 + step / 2; y < y1; y += step) {
      if (!insidePoly(x, y, p)) continue;
      const d = Math.min(...p.map((a, i) => segDist(x, y, a, p[(i + 1) % p.length])));
      if (d > bd + 1e-6) { bd = d; best = [x, y]; }
    }
  const rotate = bd > 0 && bd < 2.2 && (y1 - y0) > 3 * (x1 - x0);
  return { at: best, rotate, room: 2 * Math.max(bd, 0), long: rotate ? y1 - y0 : x1 - x0 };
}

/** Which levels' spaces appear on a plan sheet (F1 sheet also shows the east wing E1 and the lounge). */
export const planGroup: Record<string, string[]> = { F1: ["F1", "E1"], F2: ["F2"], E2: ["E2"], F3: ["F3"], F4: ["F4"] };

export const fmtElev = (z: number) =>
  Math.abs(z) < 0.005 ? "±0.00" : (z > 0 ? "+" : "−") + Math.abs(z).toFixed(2);

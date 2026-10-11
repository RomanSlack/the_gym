// Floor / site plan for one level. Horizontal cut at level + plan_cut_height:
// cut elements heavy with poché, things below the cut light, things above dashed.
import { useMemo } from "react";
import { footprint, wideTerrain } from "../model";
import type { Level, Model, SiteFeatures, Underlay, UElement } from "../model";
import { contourPath, waterPath } from "./terrain";
import { NorthArrow, ScaleBar, SectionMark } from "./symbols";

export interface Layers {
  underlay: boolean;
  terrain: boolean;
  people: boolean;
  labels: boolean;
}

const poly = (e: UElement) => "M" + e.plan.map(([x, y]) => `${x} ${-y}`).join("L") + "Z";

type Cat = "cut" | "below" | "above" | "void" | "floor" | null;

function categorize(e: UElement, elev: number, cut: number, top: number): Cat {
  const [z0, z1] = e.z;
  switch (e.kind) {
    case "slab":
      return Math.abs(z1 - elev) < 0.4 ? "floor" : null;
    case "void":
      return z0 < elev && z1 > elev - 0.3 ? "void" : null;
    case "beam":
      if (z0 <= cut && z1 >= cut) return "cut";
      return z0 > cut && z0 < top ? "above" : null;
    case "column":
    case "wall":
    case "panel":
    case "block":
    case "round_block":
      if (z0 <= cut && z1 >= cut) return "cut";
      return z1 < cut && z1 > elev - 0.2 && z0 >= elev - 1 ? "below" : null;
    default:
      return null;
  }
}

/** New site works (black ink): road, court, garage ramp/tunnel, sunken garden, sauna, path. */
function SiteWorks({ f }: { f: SiteFeatures }) {
  const line = (pts: number[][]) => "M" + pts.map((p) => `${p[0]} ${-p[1]}`).join("L");
  const rect = ([x0, y0, x1, y1]: number[]) => `M${x0} ${-y0}H${x1}V${-y1}H${x0}Z`;
  const rp = f.garage_ramp.points;
  const [gx0, gy0, gx1, gy1] = f.daycare_garden.rect;
  const tr = f.daycare_garden.terraces;
  const [sx, sy] = f.sauna.center, [sw, sh] = f.sauna.size;
  return (
    <g className="works">
      <path d={line(f.trail.points)} className="w-trail" style={{ strokeWidth: f.trail.width }} />
      {f.trail.bridges.map((b, k) => (
        <path key={k} d={line([b.from, b.to])} className="w-bridge" style={{ strokeWidth: f.trail.width + 1.2 }} />
      ))}
      <path d={line(f.road.points)} className="w-road-edge" style={{ strokeWidth: f.road.width + 2 * f.road.shoulder }} />
      <path d={line(f.road.points)} className="w-road" style={{ strokeWidth: f.road.width }} />
      <path d={rect([f.arrival_court.center[0] - f.arrival_court.size[0] / 2, f.arrival_court.center[1] - f.arrival_court.size[1] / 2,
        f.arrival_court.center[0] + f.arrival_court.size[0] / 2, f.arrival_court.center[1] + f.arrival_court.size[1] / 2])} className="w-court" />
      <path d={line(rp)} className="w-ramp" style={{ strokeWidth: f.garage_ramp.width }} />
      <path d={line(rp.filter((p) => p[0] <= f.garage_ramp.tunnel_from_x + 20))} className="w-tunnel" style={{ strokeWidth: f.garage_ramp.width }} />
      <path d={rect(f.daycare_garden.rect)} className="w-garden" />
      {Array.from({ length: tr.count }, (_, k) => (k + 1) * tr.run).map((d) => (
        <path key={d} d={`M${gx0} ${-(gy1 + d)}H${gx1 + d}V${-gy0}`} className="w-terrace" />
      ))}
      <path d={line(f.sauna_path.points)} className="w-path" style={{ strokeWidth: f.sauna_path.width }} />
      <path d={rect([sx - sw / 2, sy - sh / 2, sx + sw / 2, sy + sh / 2])} className="w-building" />
      <path d={rect(f.sauna.deck.rect)} className="w-deck" />
      <text x={sx} y={-sy} className="txt-s" textAnchor="middle">SAUNA</text>
      <text x={(gx0 + gx1) / 2} y={-(gy0 + gy1) / 2} className="txt-s" textAnchor="middle">SUNKEN GARDEN</text>
      <text x={f.arrival_court.center[0]} y={-f.arrival_court.center[1]} className="txt-s" textAnchor="middle">ARRIVAL</text>
    </g>
  );
}

export function Plan({
  model, underlay, level, layers, site,
}: { model: Model; underlay: Underlay; level: Level; layers: Layers; site: boolean }) {
  const elev = level.elevation;
  const cut = elev + model.views.plan_cut_height;
  const wing = level.wing.split("+");
  const top = Math.min(
    elev + 8,
    ...model.levels
      .filter((l) => l.elevation > elev + 0.5 && l.wing.split("+").some((w) => wing.includes(w)))
      .map((l) => l.elevation),
  );

  const t = underlay.terrain;
  const tc = site ? wideTerrain : t;  // site plan: whole core at 10 m; floor plans: detail at 2 m
  const contours = useMemo(() => {
    const out: { z: number; d: string; anchors: [number, number][] }[] = [];
    for (let z = -60; z <= 40; z += site ? 2 : 1) out.push({ z, ...contourPath(tc, z) });
    return out;
  }, [tc, site]);
  const water = useMemo(() => waterPath(t), [t]);

  const groups = useMemo(() => {
    const g: Record<string, UElement[]> = { cut: [], below: [], above: [], void: [], floor: [] };
    for (const e of underlay.elements) {
      const c = categorize(e, elev, cut, top);
      if (c) g[c].push(e);
    }
    return g;
  }, [underlay, elev, cut, top]);

  const near = (z: number | undefined, lo: number, hi: number) => z !== undefined && z >= elev + lo && z <= elev + hi;
  const people = underlay.elements.filter((e) => e.kind === "person" && near(e.at?.[2], -0.7, 0.7));
  const labels = underlay.elements.filter((e) => e.kind === "label" && near(e.at?.[2], -0.6, 2.6));
  const el = (e: UElement, cls: string) => <path key={e.name} d={poly(e)} className={cls} data-n={`${e.name} · ${e.kind} · z ${e.z[0].toFixed(2)} to ${e.z[1].toFixed(2)}`} />;

  return (
    <g>
      {layers.terrain && (
        <g className={site ? "terrain site" : "terrain"}>
          <path d={water} className="water" />
          {contours.map((c) => (
            <path key={c.z} d={c.d} className={c.z % 5 === 0 ? "contour index" : "contour"} />
          ))}
          {site &&
            contours
              .filter((c) => c.z % 5 === 0)
              .flatMap((c) =>
                c.anchors.map(([x, y], k) => (
                  <text key={`${c.z}-${k}`} x={x} y={y} className="txt-s contour-label" textAnchor="middle">
                    {c.z}
                  </text>
                )),
              )}
        </g>
      )}

      {layers.underlay && (
        <g className="underlay">
          {groups.floor.map((e) => el(e, "u-floor"))}
          {groups.below.map((e) => el(e, "u-below"))}
          {groups.void.map((e) => (
            <g key={e.name} data-n={`${e.name} · floor opening · Ø ${(2 * e.radius!).toFixed(1)} m`}>
              <circle cx={e.center![0]} cy={-e.center![1]} r={e.radius} className="u-void" />
              <path
                d={`M${e.center![0] - e.radius! * 0.7} ${-e.center![1] - e.radius! * 0.7}l${e.radius! * 1.4} ${e.radius! * 1.4}m0 ${-e.radius! * 1.4}l${-e.radius! * 1.4} ${e.radius! * 1.4}`}
                className="u-void"
              />
            </g>
          ))}
          {groups.above.map((e) => el(e, "u-above"))}
          {groups.cut.map((e) => el(e, "u-cut"))}
        </g>
      )}

      {layers.people &&
        people.map((p) => (
          <g key={p.name} className="person-plan" data-n={`${p.name} · scale figure ${p.height?.toFixed(2)} m`}>
            <circle cx={p.at![0]} cy={-p.at![1]} r={0.3} />
          </g>
        ))}

      {layers.labels &&
        labels.map((l) => (
          <text key={l.name} x={l.at![0]} y={-l.at![1]} className="txt-m note" textAnchor="middle">
            “{l.text}”
          </text>
        ))}

      {(site || level.id === "F1") && <SiteWorks f={model.site.features} />}

      {/* new design: beams overhead (dashed, as drawn above the cut) */}
      {!site &&
        model.elements
          .filter((e) => e.type === "beam" && e.z[0] > cut && e.z[0] < top + 0.2)
          .map((e) => (
            <path key={e.id} d={"M" + footprint(e).map(([x, y]) => `${x} ${-y}`).join("L") + "Z"} className="n-beam-above"
              data-n={`${e.id} · ${e.material} beam ${e.size[0]} x ${e.size[1]} · underside ${e.z[0]}`} />
          ))}

      {/* new design: columns cut by this plan (solid black), or below it (outline) */}
      {!site &&
        model.elements
          .filter((e) => e.type === "column" && e.z[0] <= cut && e.z[1] >= elev - 0.2)
          .map((e) => {
            const isCut = e.z[1] >= cut;
            const [w, d] = e.size;
            return (
              <rect key={e.id} x={e.at![0] - w / 2} y={-e.at![1] - d / 2} width={w} height={d}
                className={isCut ? (e.material === "glulam" ? "n-col-timber" : "n-col") : "n-col-below"}
                data-n={`${e.id} · ${e.material} column ${w} x ${d} · z ${e.z[0]} to ${e.z[1]}`} />
            );
          })}

      {model.grids.map((g) => (
        <g key={g.id} className="grid">
          <line x1={g.from[0]} y1={-g.from[1]} x2={g.to[0]} y2={-g.to[1]} className="ln-grid" />
          {[g.from, g.to].map((p, k) => (
            <g key={k} transform={`translate(${p[0]} ${-p[1]})`}>
              <circle r={1.2} className="ln-thin fill-paper" />
              <text y={0.45} className="txt-m" textAnchor="middle">{g.id}</text>
            </g>
          ))}
        </g>
      ))}

      {!site && model.views.sections.map((s) => <SectionMark key={s.id} from={s.from} to={s.to} id={s.id} />)}

      <NorthArrow x={site ? 580 : 45} y={site ? -880 : -38} />
      <ScaleBar x={site ? -400 : -46} y={site ? 150 : 40} />
    </g>
  );
}

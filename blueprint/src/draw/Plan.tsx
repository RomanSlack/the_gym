// Floor / site plan for one level. Horizontal cut at level + plan_cut_height:
// cut elements heavy with poché, things below the cut light, things above dashed.
import { Component, useMemo, type ReactNode } from "react";
import { footprint } from "../model";
import type { Level, Model, SiteFeatures, Underlay, UElement } from "../model";
import { contourPath, waterPath } from "./terrain";
import { NorthArrow, ScaleBar, SectionMark } from "./symbols";
import { DesignPlan } from "./Design";

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
  const gd = f.daycare_garden;
  // organic garden floor, clipped by the building (south) and the stone wall (west)
  const clip = (p: [number, number]) => [Math.max(p[0], gd.west_wall_x), Math.max(p[1], gd.building_edge_y)];
  const gFloor = "M" + gd.curve.map((p) => clip(p)).map(([x, y]) => `${x} ${-y}`).join("L") + "Z";
  const gc = gd.curve.reduce((a, p) => [a[0] + p[0] / gd.curve.length, a[1] + p[1] / gd.curve.length], [0, 0]);
  const [sx, sy] = f.sauna.center, [sw, sh] = f.sauna.size;
  return (
    <g className="works">
      <path d={line(f.trail.points)} className="w-trail" style={{ strokeWidth: f.trail.width }} />
      {f.trail.bridges.map((b, k) => (
        <path key={k} d={line([b.from, b.to])} className="w-bridge" style={{ strokeWidth: f.trail.width + 1.2 }} />
      ))}
      <path d={line(f.road.points)} className="w-road-edge" style={{ strokeWidth: f.road.width + 2 * f.road.shoulder }} />
      <path d={line(f.road.points)} className="w-road" style={{ strokeWidth: f.road.width }} />
      {(f.surfaces ?? []).map((sf) =>
        sf.poly ? <path key={sf.id} d={"M" + sf.poly.map(([x, y]) => `${x} ${-y}`).join("L") + "Z"} className={`w-${sf.kind}`} />
        : sf.circle ? <circle key={sf.id} cx={sf.circle[0]} cy={-sf.circle[1]} r={sf.circle[2]} className={`w-${sf.kind}`} />
        : <path key={sf.id} d={`M${sf.ring![0] + sf.ring![3]} ${-sf.ring![1]}A${sf.ring![3]} ${sf.ring![3]} 0 1 0 ${sf.ring![0] - sf.ring![3]} ${-sf.ring![1]}A${sf.ring![3]} ${sf.ring![3]} 0 1 0 ${sf.ring![0] + sf.ring![3]} ${-sf.ring![1]}ZM${sf.ring![0] + sf.ring![2]} ${-sf.ring![1]}A${sf.ring![2]} ${sf.ring![2]} 0 1 1 ${sf.ring![0] - sf.ring![2]} ${-sf.ring![1]}A${sf.ring![2]} ${sf.ring![2]} 0 1 1 ${sf.ring![0] + sf.ring![2]} ${-sf.ring![1]}Z`} className="w-court" fillRule="evenodd" />,
      )}
      {(f.paths ?? []).map((pa) => <path key={pa.id} d={line(pa.points)} className="w-path" style={{ strokeWidth: pa.width }} />)}
      {(f.stepping_stones ?? []).map((ln) => <path key={ln.id} d={line(ln.points)} className="w-stones" style={{ strokeWidth: ln.size[1] }} />)}
      <path d={line(rp)} className="w-ramp" style={{ strokeWidth: f.garage_ramp.width }} />
      <path d={line(rp.filter((p) => p[0] <= f.garage_ramp.tunnel_from_x + 20))} className="w-tunnel" style={{ strokeWidth: f.garage_ramp.width }} />
      <defs>
        <clipPath id="garden-clip">
          <rect x={gd.west_wall_x} y={-(gd.building_edge_y + 40)} width={60} height={40} />
        </clipPath>
      </defs>
      <g clipPath="url(#garden-clip)">
        {/* terrace rings: the floor outline offset outward (stroke trick) */}
        {Array.from({ length: gd.terraces.count }, (_, k) => gd.terraces.count - k).map((k) => (
          <path key={k} d={"M" + gd.curve.map(([x, y]) => `${x} ${-y}`).join("L") + "Z"} className="w-terrace-band"
            style={{ strokeWidth: 2 * k * gd.terraces.run }} />
        ))}
        <path d={gFloor} className="w-garden" />
      </g>
      <line x1={gd.west_wall_x} y1={-gd.building_edge_y} x2={gd.west_wall_x} y2={-(gd.building_edge_y + 15)} className="w-stone-wall" />
      <path d={line(f.sauna_path.points)} className="w-path" style={{ strokeWidth: f.sauna_path.width }} />
      <path d={rect([sx - sw / 2, sy - sh / 2, sx + sw / 2, sy + sh / 2])} className="w-building" />
      <path d={rect(f.sauna.deck.rect)} className="w-deck" />
      <text x={sx} y={-sy} className="txt-s" textAnchor="middle">SAUNA</text>
      <text x={gc[0]} y={-gc[1]} className="txt-s" textAnchor="middle">SUNKEN GARDEN</text>
      {f.bike_shelter && (
        <g>
          <path d={rect(f.bike_shelter.rect)} className="w-shelter" />
          <text x={(f.bike_shelter.rect[0] + f.bike_shelter.rect[2]) / 2} y={-(f.bike_shelter.rect[1] + f.bike_shelter.rect[3]) / 2 + 0.3} className="txt-s" textAnchor="middle">BIKE SHELTER · ~30</text>
        </g>
      )}
      <text x={44} y={-9} className="txt-s" textAnchor="middle">ENTRY MEADOW</text>
      <text x={-46} y={14} className="txt-s" textAnchor="middle">GARDEN TERRACE</text>
      {f.outdoor_rig && <path d={rect(f.outdoor_rig.rect)} className="w-rig" />}
      <text x={-36.5} y={23.3} className="txt-s" textAnchor="middle">TRAINING DECK · RIG</text>
      <text x={62} y={-19.5} className="txt-s" textAnchor="middle">DROP-OFF</text>
      <text x={160.5} y={-16} className="txt-s" textAnchor="middle">TRAILHEAD PARKING · 8</text>
    </g>
  );
}

/** Older versions of the model may lack fields a renderer expects: draw nothing rather than crash. */
class Safe extends Component<{ children: ReactNode }, { bad: boolean }> {
  state = { bad: false };
  static getDerivedStateFromError() { return { bad: true }; }
  componentDidUpdate(prev: { children: ReactNode }) { if (prev.children !== this.props.children && this.state.bad) this.setState({ bad: false }); }
  render() { return this.state.bad ? null : this.props.children; }
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
  const tc = site && underlay.wide ? underlay.wide : t;  // site plan: whole core at 10 m; floor plans: detail at 2 m
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

      {(site || level.id === "F1") && model.site.features?.road && (
        <Safe><SiteWorks f={model.site.features} /></Safe>
      )}

      {!site && <Safe><DesignPlan model={model} levelId={level.id} cut={cut} elev={elev} /></Safe>}

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

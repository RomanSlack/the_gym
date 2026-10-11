// Plan annotations: dimension strings on the structural grids, and the roof plan.
import type { Model } from "../model";
import { roofOutline } from "../model";

/** One dimension chain between successive positions, drawn along x (horizontal) or y (vertical). */
function Chain({ pos, at, horizontal }: { pos: number[]; at: number; horizontal: boolean }) {
  const p = [...pos].sort((a, b) => a - b);
  const tick = 0.6;
  const seg = (a: number, b: number, k: number, total = false) => {
    const mid = (a + b) / 2, txt = (b - a).toFixed(2);
    const off = total ? 2.4 : 0;
    return horizontal ? (
      <g key={`${k}-${total}`} className="dim">
        <line x1={a} x2={b} y1={-(at + off)} y2={-(at + off)} />
        {[a, b].map((v, j) => <line key={j} x1={v - tick / 2} x2={v + tick / 2} y1={-(at + off) + tick / 2} y2={-(at + off) - tick / 2} className="dim-tick" />)}
        <text x={mid} y={-(at + off) - 0.35} textAnchor="middle" className="txt-s dim-txt">{txt}</text>
      </g>
    ) : (
      <g key={`${k}-${total}`} className="dim">
        <line x1={at - off} x2={at - off} y1={-a} y2={-b} />
        {[a, b].map((v, j) => <line key={j} x1={at - off - tick / 2} x2={at - off + tick / 2} y1={-v + tick / 2} y2={-v - tick / 2} className="dim-tick" />)}
        <text x={at - off - 0.35} y={-mid} textAnchor="middle" className="txt-s dim-txt" transform={`rotate(-90 ${at - off - 0.35} ${-mid})`}>{txt}</text>
      </g>
    );
  };
  return (
    <g>
      {p.slice(1).map((b, k) => seg(p[k], b, k))}
      {p.length > 2 && seg(p[0], p[p.length - 1], 99, true)}
    </g>
  );
}

/** Grid dimension strings for both wings, placed outside the bubbles. */
export function GridDims({ model }: { model: Model }) {
  const v = model.grids.filter((g) => g.from[0] === g.to[0]);
  const h = model.grids.filter((g) => g.from[1] === g.to[1]);
  const west = { xs: v.filter((g) => g.from[0] < 0).map((g) => g.from[0]), ys: h.filter((g) => g.from[0] < 0).map((g) => g.from[1]) };
  const east = { xs: v.filter((g) => g.from[0] > 0).map((g) => g.from[0]), ys: h.filter((g) => g.from[0] > 0).map((g) => g.from[1]) };
  return (
    <g className="dims">
      <Chain pos={west.xs} at={Math.max(...west.ys) + 12} horizontal />
      <Chain pos={west.ys} at={Math.min(...west.xs) - 12} horizontal={false} />
      <Chain pos={east.xs} at={Math.max(...east.ys) + 12} horizontal />
      <Chain pos={east.ys} at={Math.max(...east.xs) + 9} horizontal={false} />
    </g>
  );
}

/** Roof plan: roofs with their eaves, sod roofs, skylights, towers. */
export function RoofPlan({ model }: { model: Model }) {
  const slabs = model.elements.filter((e) => e.type === "slab" && e.z[1] >= 2.5);
  const R = (r: number[]) => `M${r[0]} ${-r[1]}H${r[2]}V${-r[3]}H${r[0]}Z`;
  return (
    <g className="roof">
      {slabs.filter((e) => e.material === "clt").map((e) => (
        <g key={e.id} data-n={`${e.id} · CLT roof on glulam${e.eaves ? ` · eaves ${e.eaves.join(" / ")} m (W/S/E/N)` : ""}`}>
          <path d={R(roofOutline(e))} className="roof-eave" />
          <path d={R(e.rect!)} className="roof-line" />
        </g>
      ))}
      {slabs.filter((e) => e.material === "sod").map((e) => <path key={e.id} d={R(e.rect!)} className="roof-sod" data-n={`${e.id} · sod roof`} />)}
      {model.elements.filter((e) => e.type === "wall" && e.kind === "shaft").map((e) => {
        const [x0, y0] = e.from!, [x1, y1] = e.to!;
        return <line key={e.id} x1={x0} y1={-y0} x2={x1} y2={-y1} className="roof-tower" />;
      })}
      {slabs.filter((e) => e.material === "glass").map((e) => (
        <path key={e.id} d={R(e.rect!)} className="roof-sky" data-n={`${e.id} · glass skylight`} />
      ))}
      <text x={-17.95} y={11} textAnchor="middle" className="txt-m">CLT roof · glulam beams · 2.5 m eaves</text>
      <text x={21.25} y={-12} textAnchor="middle" className="txt-m">CLT roof · eaves</text>
    </g>
  );
}

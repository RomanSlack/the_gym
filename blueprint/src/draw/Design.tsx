// New design on a plan (black ink): rooms with names + areas, walls cut by the plan,
// stairs (spiral / straight) and fixtures. Everything comes from model/building.json.
import type { Model, Pt } from "../model";
import { labelPoint, planGroup, polyArea } from "../model";

const P = (pts: Pt[]) => "M" + pts.map(([x, y]) => `${x} ${-y}`).join("L") + "Z";

function Spiral({ c, d, landing }: { c: Pt; d: number; landing: boolean }) {
  const r = d / 2, r0 = 0.45, n = 18;
  return (
    <g className="n-stair">
      <circle cx={c[0]} cy={-c[1]} r={r} className="n-stair-edge" />
      <circle cx={c[0]} cy={-c[1]} r={r0} className="n-stair-edge" />
      {Array.from({ length: landing ? n * 0.75 : n }, (_, k) => {
        const a = (2 * Math.PI * k) / n;
        return <line key={k} x1={c[0] + r0 * Math.cos(a)} y1={-(c[1] + r0 * Math.sin(a))} x2={c[0] + r * Math.cos(a)} y2={-(c[1] + r * Math.sin(a))} />;
      })}
      <text x={c[0]} y={-c[1] + 0.35} className="txt-s" textAnchor="middle">UP</text>
    </g>
  );
}

function Straight({ rect }: { rect: [number, number, number, number] }) {
  const [x0, y0, x1, y1] = rect;
  const treads = Math.floor((y1 - y0) / 0.28);
  return (
    <g className="n-stair">
      <path d={P([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])} className="n-stair-edge" />
      {Array.from({ length: treads }, (_, k) => <line key={k} x1={x0} x2={x1} y1={-(y0 + k * 0.28)} y2={-(y0 + k * 0.28)} />)}
      <path d={`M${(x0 + x1) / 2} ${-y0 - 0.5}V${-y1 + 0.8}`} className="n-stair-arrow" />
    </g>
  );
}

export function DesignPlan({ model, levelId, cut, elev }: { model: Model; levelId: string; cut: number; elev: number }) {
  const show = planGroup[levelId] ?? [levelId];
  const spaces = model.spaces.filter((s) => show.includes(s.level));
  const walls = model.elements.filter((e) => e.type === "wall" && e.z[0] <= cut && e.z[1] >= cut);
  const lvIdx = Object.fromEntries(model.levels.map((l) => [l.id, l.elevation]));
  const stairs = model.stairs.filter((st) => {
    const lo = lvIdx[st.from], hi = lvIdx[st.to];
    return elev >= lo - 0.3 && elev < hi + 0.3;
  });
  return (
    <g className="design">
      {spaces.map((s) => (
        <path key={s.id} d={P(s.poly)} className={`sp sp-${s.kind}`} data-n={`${s.name} · ${polyArea(s.poly).toFixed(0)} m²${s.note ? " · " + s.note : ""}`} />
      ))}
      {stairs.map((st) =>
        st.kind === "spiral" ? (
          <Spiral key={st.id} c={st.center!} d={st.diameter!} landing={Math.abs(elev - lvIdx[st.from]) < 0.3} />
        ) : (
          <Straight key={st.id} rect={st.rect!} />
        ),
      )}
      {model.fixtures.filter((f) => show.includes(f.level)).map((f) => (
        <g key={f.id} className="n-fixture" data-n={`${f.id} · ${f.kind}`}>
          {f.rect ? (
            <rect x={f.rect[0]} y={-f.rect[3]} width={f.rect[2] - f.rect[0]} height={f.rect[3] - f.rect[1]} />
          ) : (
            <>
              <circle cx={f.center![0]} cy={-f.center![1]} r={f.diameter! / 2} />
              <circle cx={f.center![0]} cy={-f.center![1]} r={f.diameter! / 2 - 1.1} />
            </>
          )}
        </g>
      ))}
      {walls.flatMap((w) => {
        const [wx0, wy0] = w.from!, [wx1, wy1] = w.to!;
        const WL = Math.hypot(wx1 - wx0, wy1 - wy0);
        // split the wall along its length where an opening is cut by this plan
        const cuts = (w.openings ?? []).filter((o) => o.z[0] <= cut && o.z[1] >= cut).map((o) => o.s).sort((a, b) => a[0] - b[0]);
        const pieces: { a: number; b: number; glass: boolean }[] = [];
        let cur = 0;
        for (const [a, b] of cuts) { if (a > cur) pieces.push({ a: cur, b: a, glass: w.kind === "glazed" }); pieces.push({ a, b, glass: true }); cur = b; }
        if (cur < WL) pieces.push({ a: cur, b: WL, glass: w.kind === "glazed" });
        return pieces.map(({ a, b, glass }, k) => {
        const x0 = wx0 + ((wx1 - wx0) * a) / WL, y0 = wy0 + ((wy1 - wy0) * a) / WL;
        const x1 = wx0 + ((wx1 - wx0) * b) / WL, y1 = wy0 + ((wy1 - wy0) * b) / WL;
        const L = Math.hypot(x1 - x0, y1 - y0), t = w.size[0] / 2;
        const nx = (-(y1 - y0) / L) * t, ny = ((x1 - x0) / L) * t;
        const pts: Pt[] = [[x0 + nx, y0 + ny], [x1 + nx, y1 + ny], [x1 - nx, y1 - ny], [x0 - nx, y0 - ny]];
        return glass ? (
          <g key={`${w.id}-${k}`} className="n-glass" data-n={`${w.id} · glazing`}>
            <path d={P(pts)} />
            <line x1={x0} y1={-y0} x2={x1} y2={-y1} />
          </g>
        ) : (
          <path key={`${w.id}-${k}`} d={P(pts)} className="n-wall" data-n={`${w.id} · ${w.kind} ${w.material} ${w.size[0]} m`} />
        );
        });
      })}
      {spaces.map((s) => {
        const { at: [x, y], rotate, long } = labelPoint(s.poly);
        const a = polyArea(s.poly);
        if (s.kind === "core" || a < 20) return <text key={s.id} x={x} y={-y} className="sp-label-s" textAnchor="middle">{s.name.split(" · ")[0]}</text>;
        const [title, ...rest] = s.name.split(" · ");
        const fit = Math.min(1, (long - 0.6) / (title.length * 0.62)); // shrink to fit the room
        const tf = `${rotate ? `rotate(-90 ${x} ${-y}) ` : ""}translate(${x} ${-y}) scale(${Math.max(0.45, fit)}) translate(${-x} ${y})`;
        return (
          <g key={s.id} className="sp-label" transform={tf}>
            <text x={x} y={-y - 0.4} textAnchor="middle" className="txt-m">{title}</text>
            {rest.length > 0 && <text x={x} y={-y + 0.8} textAnchor="middle" className="txt-s sub">{rest.join(" · ")}</text>}
            <text x={x} y={-y + (rest.length ? 1.9 : 1.0)} textAnchor="middle" className="txt-s mono area">{a.toFixed(0)} m²</text>
          </g>
        );
      })}
    </g>
  );
}

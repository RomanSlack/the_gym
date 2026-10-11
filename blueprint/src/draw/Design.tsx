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
        <g key={f.id} className={`n-fixture n-fixture-${f.kind}`} data-n={`${f.id} · ${f.note ?? f.kind}`}>
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
        const ux = (wx1 - wx0) / WL, uy = (wy1 - wy0) / WL;
        // split the wall along its length where an opening is cut by this plan
        const cuts = (w.openings ?? []).filter((o) => o.z[0] <= cut && o.z[1] >= cut).sort((a, b) => a.s[0] - b.s[0]);
        const base = w.kind === "glazed" ? "glass" : "solid";
        const pieces: { a: number; b: number; t: string; swing?: number }[] = [];
        let cur = 0;
        for (const o of cuts) {
          if (o.s[0] > cur) pieces.push({ a: cur, b: o.s[0], t: base });
          pieces.push({ a: o.s[0], b: o.s[1], t: ["door", "opening", "baffle"].includes(o.type) ? o.type : "glass", swing: (o as { swing?: number }).swing ?? 1 });
          cur = o.s[1];
        }
        if (cur < WL) pieces.push({ a: cur, b: WL, t: base });
        return pieces.map(({ a, b, t, swing }, k) => {
          const x0 = wx0 + ux * a, y0 = wy0 + uy * a, x1 = wx0 + ux * b, y1 = wy0 + uy * b;
          const th = w.size[0] / 2, nx = -uy * th, ny = ux * th;
          const pts: Pt[] = [[x0 + nx, y0 + ny], [x1 + nx, y1 + ny], [x1 - nx, y1 - ny], [x0 - nx, y0 - ny]];
          const key = `${w.id}-${k}`;
          if (t === "door") {
            // gap + leaf (90° open, hinged at the start) + swing arc, into the side given by `swing`
            const r = b - a, sx = -uy * (swing ?? 1), sy = ux * (swing ?? 1);
            const hx = x0, hy = y0, lx = hx + sx * r, ly = hy + sy * r;
            const sweep = (swing ?? 1) > 0 ? 1 : 0;
            return (
              <g key={key} className="n-door" data-n={`door · ${(w.openings ?? []).find((o) => o.s[0] === a)?.note ?? ""}`}>
                <line x1={hx} y1={-hy} x2={lx} y2={-ly} />
                <path d={`M${lx} ${-ly}A${r} ${r} 0 0 ${sweep} ${x1} ${-y1}`} className="n-door-arc" />
              </g>
            );
          }
          if (t === "opening" || t === "baffle") {
            // open doorway: jamb ticks only; baffle adds a privacy screen 1.2 m inside the room
            const sx = -uy * (swing ?? 1), sy = ux * (swing ?? 1), j = th + 0.12;
            return (
              <g key={key} className="n-opening" data-n={`open doorway · ${(w.openings ?? []).find((o) => o.s[0] === a)?.note ?? ""}`}>
                <line x1={x0 - uy * j} y1={-(y0 + ux * j)} x2={x0 + uy * j} y2={-(y0 - ux * j)} />
                <line x1={x1 - uy * j} y1={-(y1 + ux * j)} x2={x1 + uy * j} y2={-(y1 - ux * j)} />
                {t === "baffle" && (
                  <line x1={x0 - ux * 0.4 + sx * 1.2} y1={-(y0 - uy * 0.4 + sy * 1.2)} x2={x1 + ux * 0.4 + sx * 1.2} y2={-(y1 + uy * 0.4 + sy * 1.2)} className="n-baffle" />
                )}
              </g>
            );
          }
          if (t === "glass") return (
            <g key={key} className="n-glass" data-n={`${w.id} · glazing`}>
              <path d={P(pts)} />
              <line x1={x0} y1={-y0} x2={x1} y2={-y1} />
            </g>
          );
          return <path key={key} d={P(pts)} className={w.kind === "partition" ? "n-partition" : "n-wall"} data-n={`${w.id} · ${w.kind} ${w.material} ${w.size[0]} m`} />;
        });
      })}
      {/* wall finishes on this level (e.g. the F3 mirror wall): a bright line on the interior face */}
      {model.elements.filter((w) => w.type === "wall" && w.finishes).flatMap((w) =>
        w.finishes!.filter((f) => show.includes(f.level)).map((f, k) => {
          const [wx0, wy0] = w.from!, [wx1, wy1] = w.to!;
          const WL = Math.hypot(wx1 - wx0, wy1 - wy0), ux = (wx1 - wx0) / WL, uy = (wy1 - wy0) / WL;
          // interior face = the side facing the wing's centre
          const off = w.size[0] / 2 + 0.08, cx = -17.95, cy = -11.0;
          let nx = -uy * off, ny = ux * off;
          if ((cx - wx0) * nx + (cy - wy0) * ny < 0) { nx = -nx; ny = -ny; }
          return <line key={`${w.id}-f${k}`} x1={wx0 + ux * f.s[0] + nx} y1={-(wy0 + uy * f.s[0] + ny)} x2={wx0 + ux * f.s[1] + nx} y2={-(wy0 + uy * f.s[1] + ny)}
            className={`n-finish n-finish-${f.kind}`} data-n={`${f.kind} · ${f.note ?? ""}`} />;
        }))}

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

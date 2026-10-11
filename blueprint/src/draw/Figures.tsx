// Scale figures: a row of 6 ft (1.83 m) people lying flat, head to toe, in drawing units (m).
// Drawn in sheet coordinates so it works on plans and sections alike.
export const FIG_LEN = 1.83;

export interface FigState {
  on: boolean;
  x: number; // sheet coords of the first figure's head end
  y: number;
  n: number;
  rot: number; // degrees
}

function Person({ dx }: { dx: number }) {
  // top-down silhouette, head at dx, feet at dx + 1.83
  return (
    <g transform={`translate(${dx} 0)`}>
      <circle cx={0.12} cy={0} r={0.11} />
      <rect x={0.25} y={-0.23} width={0.62} height={0.46} rx={0.12} />
      <rect x={0.3} y={-0.31} width={0.5} height={0.07} rx={0.035} />
      <rect x={0.3} y={0.24} width={0.5} height={0.07} rx={0.035} />
      <rect x={0.85} y={-0.17} width={0.98} height={0.15} rx={0.06} />
      <rect x={0.85} y={0.02} width={0.98} height={0.15} rx={0.06} />
    </g>
  );
}

export function Figures({ s, onGrab }: { s: FigState; onGrab: (e: React.MouseEvent) => void }) {
  if (!s.on) return null;
  const total = s.n * FIG_LEN;
  return (
    <g className="scale-figs" transform={`translate(${s.x} ${s.y}) rotate(${s.rot})`} onMouseDown={onGrab}
      data-n={`${s.n} × 6 ft (1.83 m) = ${total.toFixed(2)} m · drag to move · R to rotate`}>
      <rect x={-0.15} y={-0.5} width={total + 0.3} height={1.0} className="scale-figs-hit" />
      {Array.from({ length: s.n }, (_, k) => <Person key={k} dx={k * FIG_LEN} />)}
      <line x1={0} x2={total} y1={0.62} y2={0.62} className="scale-figs-dim" />
      <line x1={0} x2={0} y1={0.5} y2={0.74} className="scale-figs-dim" />
      <line x1={total} x2={total} y1={0.5} y2={0.74} className="scale-figs-dim" />
      <text x={total / 2} y={1.05} textAnchor="middle" className="txt-s scale-figs-txt">
        {s.n} × 1.83 = {total.toFixed(2)} m
      </text>
    </g>
  );
}

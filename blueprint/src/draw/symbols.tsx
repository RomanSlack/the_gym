// Standard drafting symbols, drawn in world units (metres) at a given text size.
import { fmtElev } from "../model";

/** Graphic scale bar: 0-5-10-20 m. */
export function ScaleBar({ x, y }: { x: number; y: number }) {
  const ticks = [0, 5, 10, 20];
  return (
    <g className="scalebar" transform={`translate(${x} ${y})`}>
      <rect x={0} y={-0.5} width={5} height={0.5} className="fill-ink" />
      <rect x={5} y={-0.5} width={5} height={0.5} className="fill-paper" />
      <rect x={10} y={-0.5} width={10} height={0.5} className="fill-ink" />
      <rect x={0} y={-0.5} width={20} height={0.5} className="ln-thin" fill="none" />
      {ticks.map((t) => (
        <text key={t} x={t} y={1.6} className="txt-s" textAnchor="middle">{t}</text>
      ))}
      <text x={21} y={0} className="txt-s">m</text>
    </g>
  );
}

/** North arrow (+y is north). */
export function NorthArrow({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle r={2.2} className="ln-thin" fill="none" />
      <path d="M0 -2.2 L1 1.4 L0 0.7 L-1 1.4 Z" className="fill-ink" />
      <text y={-2.9} className="txt-m" textAnchor="middle">N</text>
    </g>
  );
}

/** Level datum tag for sections: half-filled target + name + elevation. */
export function LevelTag({ x, y, id, z }: { x: number; y: number; id: string; z: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle r={0.55} className="ln-thin fill-paper" />
      <path d="M0 -0.55 A0.55 0.55 0 0 1 0.55 0 L0 0 Z M0 0.55 A0.55 0.55 0 0 1 -0.55 0 L0 0 Z" className="fill-ink" />
      <text x={1} y={-0.25} className="txt-m">{id}</text>
      <text x={1} y={0.95} className="txt-s mono">{fmtElev(z)}</text>
    </g>
  );
}

/** Section cut mark on a plan: line with labelled bubbles and view-direction arrows. */
export function SectionMark({ from, to, id }: { from: [number, number]; to: [number, number]; id: string }) {
  const [x0, y0] = [from[0], -from[1]];
  const [x1, y1] = [to[0], -to[1]];
  const len = Math.hypot(x1 - x0, y1 - y0);
  const ux = (x1 - x0) / len, uy = (y1 - y0) / len;
  // view direction = left of the cut direction in world coords → (−uy, ux) in svg (y flipped)
  const vx = uy, vy = -ux;
  const bubble = (bx: number, by: number) => (
    <g transform={`translate(${bx} ${by})`}>
      <path d={`M${-vy * 1.4} ${vx * 1.4} L${vx * 2.6} ${vy * 2.6} L${vy * 1.4} ${-vx * 1.4} Z`} className="fill-ink" />
      <circle r={1.4} className="ln-med fill-paper" />
      <text y={0.5} className="txt-m" textAnchor="middle">{id}</text>
    </g>
  );
  return (
    <g className="section-mark">
      <line x1={x0} y1={y0} x2={x1} y2={y1} className="ln-cutline" />
      {bubble(x0, y0)}
      {bubble(x1, y1)}
    </g>
  );
}

/** 1.83 m (6 ft) scale figure for sections, feet at (x, z). */
export function Figure({ x, z }: { x: number; z: number }) {
  const y = -z;
  return (
    <g transform={`translate(${x} ${y})`} className="figure">
      <circle cx={0} cy={-1.68} r={0.12} />
      <path d="M-0.2 -1.5 L0.2 -1.5 L0.24 -0.85 L0.12 -0.85 L0.12 0 L0.02 0 L0 -0.8 L-0.02 0 L-0.12 0 L-0.12 -0.85 L-0.24 -0.85 Z" />
    </g>
  );
}

// Schedules sheet (drawn in mm on the paper): room schedule, door schedule, area summary.
import type { Model } from "../model";
import { polyArea } from "../model";

const LEVEL_ORDER = ["F1", "E1", "F2", "E2", "F3", "F4"];

function Table({ x, y, title, cols, rows, w }: { x: number; y: number; title: string; cols: string[]; rows: string[][]; w: number[] }) {
  const rh = 4.2;
  const xs = w.reduce<number[]>((a, v, i) => [...a, (a[i] ?? 0) + v], [0]);
  return (
    <g transform={`translate(${x} ${y})`} className="sched">
      <text y={-3} className="sched-title">{title}</text>
      <rect x={0} y={0} width={xs[xs.length - 1]} height={rh * (rows.length + 1)} className="sched-frame" />
      {cols.map((c, i) => <text key={c} x={xs[i] + 1.2} y={rh - 1.2} className="sched-head">{c}</text>)}
      <line x1={0} x2={xs[xs.length - 1]} y1={rh} y2={rh} className="sched-rule" />
      {rows.map((r, j) => (
        <g key={j}>
          {j % 2 === 1 && <rect x={0} y={rh * (j + 1)} width={xs[xs.length - 1]} height={rh} className="sched-zebra" />}
          {r.map((v, i) => <text key={i} x={xs[i] + 1.2} y={rh * (j + 2) - 1.2} className="sched-cell">{v}</text>)}
        </g>
      ))}
    </g>
  );
}

export function Schedules({ model }: { model: Model }) {
  const rooms = [...model.spaces].sort((a, b) =>
    LEVEL_ORDER.indexOf(a.level) - LEVEL_ORDER.indexOf(b.level) || ((a as { number?: string }).number ?? "").localeCompare((b as { number?: string }).number ?? ""));
  const rRows = rooms.map((s) => [(s as { number?: string }).number ?? "", s.name.split(" · ")[0], s.kind, polyArea(s.poly).toFixed(0)]);
  const half = Math.ceil(rRows.length / 2);
  const doors: string[][] = [];
  for (const e of model.elements) {
    for (const o of e.openings ?? []) {
      if (!["door", "opening", "baffle"].includes(o.type)) continue;
      const lvl = model.levels.find((l) => Math.abs(l.elevation - o.z[0]) < 0.05)?.id ?? "";
      doors.push([`D${String(doors.length + 1).padStart(2, "0")}`, lvl, o.type === "door" ? "door 1.0 m" : o.type === "baffle" ? "open, baffle" : "open doorway",
        (o.s[1] - o.s[0]).toFixed(2), (o.note ?? "").slice(0, 46)]);
    }
  }
  const areas = LEVEL_ORDER.map((L) => {
    const S = model.spaces.filter((s) => s.level === L);
    return [L, model.levels.find((l) => l.id === L)?.name.split(" · ")[0] ?? L, String(S.length), S.reduce((a, s) => a + polyArea(s.poly), 0).toFixed(0)];
  });
  const total = areas.reduce((a, r) => a + +r[3], 0);
  return (
    <g>
      <Table x={20} y={30} title="ROOM SCHEDULE (1/2)" cols={["No.", "Room", "Type", "m²"]} rows={rRows.slice(0, half)} w={[16, 62, 22, 12]} />
      <Table x={140} y={30} title="ROOM SCHEDULE (2/2)" cols={["No.", "Room", "Type", "m²"]} rows={rRows.slice(half)} w={[16, 62, 22, 12]} />
      <Table x={262} y={30} title="DOOR + OPENING SCHEDULE" cols={["Mark", "Lvl", "Type", "W m", "Between / note"]} rows={doors} w={[13, 10, 26, 12, 85]} />
      <Table x={262} y={40 + 4.2 * (doors.length + 2)} title="AREA SUMMARY (net, by level)" cols={["Level", "", "Rooms", "m²"]}
        rows={[...areas, ["", "Total", "", total.toFixed(0)]]} w={[13, 70, 16, 18]} />
      <text x={262} y={58 + 4.2 * (doors.length + areas.length + 4)} className="sched-note">Net room areas from the model polygons (inside the structural grid, rock annexes included).</text>
      <text x={262} y={63 + 4.2 * (doors.length + areas.length + 4)} className="sched-note">Doors only where needed (privacy, fire, heat, security, cars, sleep); open doorways elsewhere.</text>
    </g>
  );
}

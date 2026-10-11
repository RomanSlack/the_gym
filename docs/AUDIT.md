# Audit (2026-10-11)

## Status

- ✅ **Egress fixed:** third enclosed exit stair W3 on the north face (fully outside, no floor area lost). Worst walking distance to an exit stair on F2–F4 is now about 31 m measured along the grid (about 23 m straight-line), down from 48 m. Exits are at the south (W2), middle (W1) and north (W3). Note: on F4 the W3 door opens through the thermal suite; a clear route through it has to be kept.
- ✅ **Rooms cut around cores**, and slivers closed: 0 m² gaps and 0 m² overlaps on every floor.
- ✅ **West facade rhythm:** W1 and W2 are identical 3.2 × 9 m towers. The masses repeat every 15.55 m (W2, W1, then the sauna annex between the two lifts).

## Building / code issues (original findings)

1. **Egress, the big one.** Both exit stairs (W1, W2) are on the west wall in the south half, about 17 m apart. On F2–F4 the worst walking distance to an exit stair is about **48 m**, from the north-east corner. Typical code limits are around 30 m, and exits should be remote from each other. The spiral and the F3→F4 north stair are open stairs, so they don't count as exits. **Fix: a third enclosed exit stair in the north / north-east.** It could go on the north wall next to the women's express lift, set into the rock like the others.
2. **Deep below-grade assembly use** (F4 is 15 m down, with up to 75 people plus the pool): this needs sprinklers, smoke extraction and firefighter access via a lift/stair. It's noted for the services design.
3. **Rooms drawn through the cores.** Cores and lift shafts sit 0.6 m inside the wall, and the rooms beside them still run to the wall (about 10 m² per floor overlap). The rooms should be cut around them. Small unassigned slivers (12–18 m² per floor) need to be closed too.
4. Not modeled yet, so not checked: interior partitions, interior doors, door widths and swings, accessible WC sizes, daycare fencing and gates, guard rails at the decks and the ravine edge.

## Drawing set: what a professional set has that ours doesn't yet

| Missing | Notes |
|---|---|
| Interior walls + doors with swings | rooms are colored areas, not walled |
| Dimensions | overall, grid, opening and room dimension strings |
| Room numbers + room schedule | e.g. 1.04 Women's changing, area, finishes |
| Elevations | all four facades of each wing |
| Roof plan, reflected ceiling plans | roof isn't designed yet |
| Door / window schedules | after doors exist |
| Fixed print scales + sheet borders + PDF export | currently "≈ scale on screen" |
| Title block | project info, date, revision table (rev now = commit hash) |
| Wall type legend | concrete / glazing / timber / mirror |

## Suggested order

1. Fix the code issues (third exit stair, rooms cut around cores).
2. Interior walls + doors (locker rooms, WCs, daycare, annexes); this unlocks dimensions, schedules and accessibility checks.
3. Drawing-set upgrade: dimensions, room numbers, elevations, roof plan, print scales, PDF set.
4. Then 3D detailing (materials, real structure members, facades).

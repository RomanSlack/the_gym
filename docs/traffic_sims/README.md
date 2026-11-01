# Traffic simulations of the gym floors

Kept for Roman's essay (2026-10-31: "make sure we have some visual examples for the essay later of the traffic sims"). Every run
that mattered is here as `<floor>_traffic_<before|after>_vNNN.png` (the map) + `.txt` (the numbers); nothing is overwritten.

## Why

Roman walked the floors at eye level in Blender (2026-10-31) and found what a plan view hides: "you literally have to phase through
machines", "wipe locations are literally blocking machines", "I don't think you're really taking into account the actual orientation
of things", "over half of all the placement ... is actually blocking a lot of things". The old checker only looked for overlapping
footprints. A machine can overlap nothing and still be unreachable, or reachable only by walking through someone else's set.

## How (tools/gym_walk_sim.py)

- The floor on a 0.1 m grid. Solid: the walls (their doors open), every piece's body, the spiral, the stair openings, the den river.
  A lifting platform is floor you step onto, not a solid.
- Every piece has a **training space**: its use clearance from the plan (in front of the user, the loading sides, behind; the
  numbers are NSCA's and the makers'). Walking through someone else's training space is allowed but costs 8x (they're lifting there).
  The pick zone in front of a dumbbell rack or plate tree is free to walk (that's what it's for), and so is the 2 m run-off behind a
  treadmill (kept clear of things, not of people).
- A member is 0.6 m wide: a corridor narrower than that is closed (0.46 m sideways squeeze is reported separately).
- **Access**: from the floor's ways in (the spiral's step-off, every door's landing), the cheapest walk to each piece's own training
  space. A piece reached only by crossing 0.6 m+ of someone else's training space is a problem (red on the maps).
- **Crowd**: 400 members each do a session (5 to 7 stations, a wipes station after most sets, out again). Their paths are summed into
  the traffic map (log scale: dark = busy). Reported: whose training space the crowd walks through most, in metres per 100 members, and
  the busy pinch points (top-10 % traffic where the corridor is under 1.1 m, magenta circles).

## Before / after (the same simulator on both: `before_v002` is the layout as Roman walked it, git c01b0a2; `after_v003` is the relayout)

| floor | pieces | reached only through someone's set | busy pinch points | the worst-crossed piece (m / 100 members) | the 15 worst together |
|---|---|---|---|---|---|
| F1 | 68 -> 66 | 0 -> 0 | 4 -> 0 | 140 -> 31 (an elliptical) | 295 -> 82 |
| F2 | 112 -> 86 | 17 -> 0 | 8 -> 2 | 108 -> 23 (the incline calf, then a bench) | 651 -> 62 |
| F3 | 125 -> 107 | 11 -> 2 | 6 -> 2 | 142 -> 28 (a chest press, then the maze) | 524 -> 141 |

F3's two left are inside the PWR Play maze: its cable stations face each other across shared aisles, as the maze is designed. Its two
pinch points are parked sleds on the sled lane.

`before_v001` / `after_v001` came from the first version of the simulator (stricter: platforms solid, every pick zone counted), kept
for the record. `after_v002` was a step on the way.

## What the maps showed, and what changed

- F2's olympic platforms in two staggered lines: the inner line only reachable across the outer. Now one line facing the mirror,
  the aisle behind, bumpers between.
- F2's leg room was entered through the Precor leg extension; its back row faced the north wall. Now the leg extensions back onto
  the wall facing the room, one island, a 1.2 m walk down its west side to olympic.
- F2's bench room aisle was 0.6 m with the plate trees standing in it. Now 1.2 m clear.
- F3's river row: machines back to back with a second column, their fronts 0.75 m from the water: the only way in was over the
  edge. Now one row facing the water with a 0.9 m walk in front.
- Wipes stations: the placer had only kept them off the user's front. Now they stand on walls (F2: 22 of 22), never in anyone's
  training space, an aisle or a door.

## Second walk (2026-10-31): the leg room, `after_v004` / `after_v005`

Roman: F2's leg room "looks super barren and weird and just like stuff was thrown over there". The old room passed the sim (every
piece reachable) but the pieces stood on four different lines with 2-3 m empty bands between them. Now the legs wall's north face
is a mirror and the room is four rows on one axis: the smiths (a plate tree between them) facing the mirror, the leg press + belt
squat facing it behind them, the iso leg extension + the calves back to back with those, the leg extensions on the north wall.
Same simulator, same numbers: F2 still 0 pieces reached through anyone's set (`gym_f2_traffic_after_v005`; v004 is the step before
the leg extensions were centred on the room's axis). F1 and F3 unchanged apart from the muscle-up station (one double bar instead
of two lone ones): F1 0 problems, F3 the same 2 inside the PWR Play maze.

## Third walk (2026-11-01): racks turned to the mirrors, a way into olympic, `gym_f1_v005` / `gym_f2_v006` / `gym_f3_v005`

Roman walked all three floors again. On F2 the rack room turned to face its divider wall (now a mirror): four racks 0.75 m apart
with chalk stands between (five stood 0.07 m apart), so the racks wall could stop 1.2 m shorter and the walk round the spiral is
no longer "uncomfortably thin". The pulling corner has four half racks, two on each mirror, back to back across a 0.9 m walk that
leads to a new 1.6 m opening into olympic (before, the only way in was "all the way around"). The leg hub has a second row facing
the first, the leg presses face to face. The sim still finds every piece on F1 and F2 without crossing anyone's set; F3's two left
are the same maze aisles. The busiest crossings on F2 are the incline benches nearest the bench room's way in and the PWR Play's
dual cable (as before), and the rack platforms' fronts, which people pass to reach the chalk stands between them.

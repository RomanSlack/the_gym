# Structure: proposal v2 (no interior columns)

Source of truth: `model/building.json` → `structure` (generated into `grids` + `elements` by `tools/structure.py`).

Roman's brief: as column-free as possible, none on the top floor. Flood regulations ignored for this build.

## Concept: concrete below, timber above, stone outside, everything spans wall to wall

- **Zero interior columns on every floor.** Floors and roofs span between the two long walls of each wing.
- **Below grade / river side** (F2–F4, E2): reinforced concrete.
  - The long walls are solid concrete: a retaining wall against the rock on the west, and the river wall with its windows on the east.
  - The F4 floor slab is anchored into bedrock against uplift (6.6 m of water depth).
- **Above grade** (F1, E1): glulam columns along the facades, CLT (cross-laminated timber) roof panels.
- **Stone cladding** on the concrete base. Foundations bear on bedrock.

## Spans

| Where | Span | System | Beam depth | Clear height under beams |
|---|---|---|---|---|
| Gym floors F1, F2, F3 | 23.1 m | post-tensioned concrete beams 0.55 × 1.1 m @ 7.7 m + 250 mm slab | 1.1 m | F2 3.7 m, F3 3.7 m, F4 4.4 m |
| Gym roof (F1 hall) | 23.1 m | glulam GL30c ~0.3 × 1.3 m @ 7.7 m + CLT | 1.3 m | 4.3 m |
| East floor E1 (over garage/daycare) | 18.5 m | post-tensioned 0.5 × 0.9 m @ 8.56 m + 250 mm slab | 0.9 m | ~5 m |
| East roof | 18.5 m | glulam ~0.25 × 1.0 m @ 8.56 m + CLT | 1.0 m | ~4.1 m |
| Lounge link | 18.5 m | two trusses wing to wing; decks cantilever ~3 m | n/a | n/a |

Between beams (every 7.7 / 8.56 m) the full floor height is available. Services (ducts, sprinklers) run between the beams, or through the glulam roof beams.

## Grid

- Gym: A (−29.45) and C (−6.45) × 1–7 every 7.7 m.
- East: D (12.0) and F (30.5) × 8–13 every 8.56 m (parking module).
- 52 perimeter columns / wall pilasters, 40 spanning beams.

## Stage 3 (built, `tools/structure_stage.py`)

Design rule for this stage: as sleek as the frame allows, in the style-B language (thin dark edges, warm timber underneath).

- **Roofs: CLT 300 with 2.5 m eaves.** 7-layer CLT spans the 7.7 / 8.56 m between the glulam beams under the sod. Each roof slab carries `eaves` = overhang per side [W, S, E, N]; negative means the plate stops where the neighbouring roof's eave takes over (the lounge roof between the wings).
  - The glulam roof beams run on past the long facades as **tapered tails** (1.3 / 1.0 m deep at the facade, 0.3 m at the tip) that carry the long-side eaves. On the short ends the CLT cantilevers 2.5 m off the end beam (back-span 7.7 m).
  - Wings and lounge share one roof level, so from above it reads as one thin plane stepping across the river. The W1/W2 towers and the lift shafts punch through it.
  - The sauna-lobby annex gets a 0.6 m drip edge (it sits under the main eave).
- **Lounge bridge: girders, not trusses.** The sliding glass walls open fully, so nothing diagonal can go in the walls.
  - Floor: four dark steel box girders 0.45 × 1.0 m, 18.5 m wing to wing, under the 0.3 m deck. The west ends sit in pockets in the river wall; the east ends sit on a concrete ledge between columns D13–D11. Tapered steel outriggers carry the decks (3 m south, 4.5 m north). From the gorge it reads as a thin dark plate over the water.
  - Roof: five glulam beams 0.25 × 1.0 m span across the lounge (16.3 m) on slim 150 mm steel posts in the glass lines, with the same tapered tails over the decks. The sliding panels stack between the posts. The lounge reads as a small wing turned 90°.
- **Cores:** every wall between a core / lift and a room is 250 mm concrete (fire-rated shafts that brace the floors); core E got its concrete shaft (E2 → roof).
  - Core stairs: precast concrete doglegs (0.175 rise, 0.28 going). W1/W2 flights are 1.0 m (2.2 m clear inside the core), W3 1.2 m, E 1.2 m.
  - Core doors moved onto the floor landings (a door can't open onto a flight); lift doors added in W1 and E.
- **Spiral F1 → F3:** an open helix with no centre post: inner + outer dark steel helical stringers, 56 solid oak treads. Same build for the daycare's round stair.
- **F3 → F4 north stair:** built as a dogleg in its 6 × 5 m opening (two 2.7 m flights, 0.25 going), because a single straight flight of 5.6 m rise can't fit in 5 m.
- Every phase-3 element has `phase: 3` and a `seq` that runs bottom-up by elevation, for the construction timelapse.

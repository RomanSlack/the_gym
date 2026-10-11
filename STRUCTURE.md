# Structure: proposal v1 (to confirm)

Source of truth: `model/building.json` → `structure` (generated into `grids` + `elements` by `tools/structure.py`).

## Concept: concrete below, timber above, stone outside

Like the reference image:
- **Reinforced concrete** wherever there is earth or water: F2–F4 in the gym wing and E2 in the east wing. Watertight concrete (a "white tank") on the river side, because F3 and F4 sit below the water.
  - The F4 floor is a thick slab **anchored into bedrock**. 6.6 m of water depth pushes it upward.
- **Glulam frame + CLT panels** (cross-laminated timber) for the F1 and E1 halls and their roofs. Deep roof overhangs, timber soffits.
- **Stone cladding** on the concrete base.
- **Foundations on bedrock.** The gorge is cut through rock, so the building can bear directly on it.

## Grid

| Wing | Across | Along | Why |
|---|---|---|---|
| Gym (west) | A, B, C at 11.55 m (23.1 m total) | 1–7 every 7.7 m | F1 hall **column-free across 23.1 m** (glulam roof beams on A and C, as in Gym V2). F2–F4 add line **B** for heavy gym loads + earth/water pressure (11.55 m concrete spans). 7.7 m suits CLT panels. |
| Lounge link | spans 18.5 m, grid C → D | n/a | Two deep glulam or steel trusses over the river; outdoor decks cantilever ~3 m. |
| East | D, E, F at 9.25 m | 8–13 every 8.56 m | 8.56 m = parking module (3 × 2.85 m stalls) for the garage below. |

Columns (generated): concrete 500×500 (gym, F4→F1), 450×450 (east, E2→E1); glulam 400×600 (gym F1, lines A/C only), 350×350 (east E1).

## To resolve

1. **Spiral stair vs column B4.** Gym V2's spiral void (Ø 7.9 m at −19.5, −13.6) contains column B4 (−17.95, −11.0). Move the stair or drop/transfer that column.
2. **Design flood level.** Norwegian TEK17 §7-2 flood safety classes (20 / 200 / 1000-year); a gym with a daycare is likely the 200-year class. Estimate the flood from the real upstream catchment, then check:
   - the garage floor (E2 −6.01, only 2.8 m above normal water)
   - the F3 river windows and the indoor-stream intake
3. **Cores**: stair and elevator shafts double as the stiff concrete cores that brace the timber floors above. Their positions get fixed with the floor layouts.

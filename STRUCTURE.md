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

## Still to place (with the floor layouts)

- **Cores:** stair and elevator shafts double as the stiff concrete cores that brace the floors.
- **The spiral stair** (F1 → F3; normal stairs F3 → F4 toward the north edge). No column clash anymore.

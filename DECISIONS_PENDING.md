# Decisions made while Roman was away (please review)

Everything here is editable data in `model/building.json`; change the numbers and re-run the tools. Each item says where it lives.

Session goal (2026-10-10): **schematic floor plans v1 for every level** inside the column-free frame: cores, stairs, rooms, slabs, walls; drawn in the blueprint and built as a new 3D massing.

## Layout decisions

1. **Spiral stair moved to the wing's centerline, mid-bay:** center (−17.95, −14.85), Ø 7.0 m (Gym V2: (−19.5, −13.6), Ø 7.9). It now fits between beam lines 4 and 5 instead of being cut by a beam, and sits symmetric between the two halves of the gym. It runs F1 → F3. *`model.stairs` → `spiral_west`*
2. **Two enclosed stair cores in the gym wing** (real fire exits, since the open spiral can't be one):
   - **W1** (stair + elevator) on the west wall, mid-length, F4 → F1, exits to the garden terrace.
   - **W2** (stair) in the south-west corner.
   *`model.spaces` kind `core`*
3. **F3 → F4 "normal stairs off to the north edge"** (your words): an open stair at the north edge of F3. *`model.stairs` → `north_f3_f4`*
4. **F1 (gym wing):**
   - Locker rooms (men's west, women's east) take the north two bays, with a shared **sauna lobby** at the north edge between them and the door to the sauna path.
   - A **gallery** across the middle bay receives the lounge bridge.
   - South: stretching/mobility (west), the spiral, calisthenics (by the river), cardio (south-east, river views).
5. **F2:**
   - Free weights along the solid west wall (mirrors go there).
   - Olympic platforms in the north-west.
   - Cardio along the river side, machines south-east.
6. **F3 (river rim):**
   - A 46 m **turf sprint/sled lane** the full length of the wing (from your feature list).
   - Strongman between the cores on the west.
   - Functional/CrossFit in the middle.
   - The **river edge strip** (waist-high river window + indoor stream) along the whole east wall.
7. **F4:**
   - A **25 m lap pool along the river wall** (underwater windows).
   - Thermal suite (hot/cold plunge, infrared, steam, cryo) at the north.
   - Recovery lounge, treatment rooms, plant room on the west (no windows needed there).
8. **East wing E1:**
   - Entry from the arrival court into a lobby.
   - Reception.
   - Cafe (the round island bar) toward the lounge bridge.
   - WCs.
   - Core E (stair + elevator to the garage).
   - **Daycare** in the north two bays, with its own door to the court and Gym V2's round stair (Ø 5.1 m) linking its two floors.
9. **East wing E2:**
   - Garage in the south two bays (cars along the glass, indoor bike storage, tunnel entry east).
   - Game room in the middle.
   - Daycare lower floor in the north, walking out to the sunken garden.
10. **Lounge link:** lounge between the wings at F1, outdoor decks cantilevered 3 m north (over the falls view) and south.

## Structure decisions

11. Below-grade perimeter walls are reinforced concrete: 0.5 m retaining on the rock sides, 0.4 m on the river wall with windows. F1/E1 facades are glazed timber.
12. F4 and E2 ground slabs are 0.6 m rafts (F4 rock-anchored); suspended floors are 0.25 m slabs on the post-tensioned beams.
13. **Cafe ring** moved from Gym V2 (20, 0.2) to (16.6, −0.94), Ø 7.0, to sit inside the cafe space. *`model.fixtures`*
14. **Roof eaves: 2.5 m overhang on all sides** (like the reference image). For now this exists only in the 3D scene (`terrain/blender_scene.py`); it will move into the model when we design the roof.

## What got built this session

- **Drawings** (http://localhost:5280): every floor plan has rooms with names and areas, concrete walls, glazing, stairs and the cafe ring. Sections show slabs breaking around the spiral, core and stair openings, the spiral helix, and the F3→F4 stair. The Gym V2 underlay is off by default (one checkbox to turn it on).
- **3D** (`terrain/out/scene/site.blend`): the new building is generated from the model and Gym V2 is hidden. It has the column-free F1 hall with glulam roof beams, the post-tensioned floor beams, the spiral stair with timber treads, the pool (with a basin opening in the F4 slab), the garage glass and the daycare garden glass. Renders are in `terrain/runs/*_scene/sheet5.png`.

## Not done yet (next steps)

- Windows in the river wall (the F2 views, the F3 waist-high river window, the F4 underwater windows) are not modeled. The wall is solid stone-clad concrete for now.
- Interior partitions inside rooms (lockers, WCs, showers) and doors.
- Roof design (slope/flat, sod or timber, skylights).
- The rustic bridge (still Gym V2's slab), and reframing the north footbridge views.


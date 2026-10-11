# Decisions made while Roman was away (please review)

Everything here is editable data in `model/building.json`; change the numbers and re-run the tools. Each item says where it lives.

Session goal (2026-10-10): **schematic floor plans v1 for every level** inside the column-free frame: cores, stairs, rooms, slabs, walls; drawn in the blueprint and built as a new 3D massing.

## Layout decisions

1. **Spiral stair moved to the wing's centerline, mid-bay:** center (−17.95, −14.85), Ø 7.0 m (Gym V2: (−19.5, −13.6), Ø 7.9). It now fits between beam lines 4 and 5 instead of being cut by a beam, and sits symmetric between the two halves of the gym. It runs F1 → F3. *`model.stairs` → `spiral_west`*
2. **Two enclosed stair cores in the gym wing**, revised: shrunk to the minimum (W1 stair + elevator 3.2 × 9 m, W2 exit stair 3.2 × 6.5 m) and **set into the back (west) wall** like the express lifts: 0.6 m inside, the rest outside as stone towers. Each has a **glass skylight** (daylight down the stairwell to F4), W2 has its own exit door on F1, and the west-side rooms reclaimed the space. Original version: (real fire exits, since the open spiral can't be one):
   - **W1** (stair + elevator) on the west wall, mid-length, F4 → F1, exits to the garden terrace.
   - **W2** (stair) in the south-west corner.
   *`model.spaces` kind `core`*
3. **F3 → F4 "normal stairs off to the north edge"** (your words): an open stair at the north edge of F3. *`model.stairs` → `north_f3_f4`*
4. **F1 (gym wing)**, revised twice with Roman to follow Gym V2's walls:
   - The locker block is x −29.45..−13.6, y −9.3..12.1, split at y 1.5. Each room has a **changing room** (~95 m²) and a **wet zone** on its outer side (showers, WCs, steam), and runs full width to the gallery.
   - The **gallery runs north-south** (7 m) where the lounge bridge lands; both locker doors open straight off it.
   - **Sauna lobby = an annex outside the west wall** (6 × 6 m) where the two rooms meet, shared by both, with the door to the sauna path (path re-routed from there).
   - **Core W1 moved one bay south** (y −18.7..−11) to clear the lockers; the floors below follow.
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
8. **East wing E1** (revised to follow Gym V2):
   - The **cafe takes the whole south half**, with the island bar centered and a back counter along the south wall.
   - A **central block** holds **core E** (stair + lift from the garage) and the **public WCs** (women's, men's, accessible), in Gym V2's WC-cell area.
   - The **reception desk is backed onto the core**, facing the east entrance from the arrival court. A hall on the west side links the cafe to the daycare.
   - **Daycare upper floor**, laid out as a Norwegian barnehage:
     - an entry wardrobe with drying cabinets (secure door from reception)
     - children's WC + changing (child-height WCs and basins, about 1 WC per 10 children, changing table with hand shower, accessible WC)
     - staff room + staff WC
     - play rooms
9. **East wing E2:**
   - Garage in the south half.
   - Game room and a lift lobby on either side of core E.
   - Daycare lower floor: rest/sleep room, a children's WC + changing stacked under the upper one, storage for prams and outdoor gear, and a play room walking out to the sunken garden.
   - **Gym WC annexes on F2, F3 and F4:** 3 single WCs (1 accessible) plus a water station each, dug into the rock outside the west wall between W2 and W1, stacked so the plumbing lines up.
10. **Lounge link:** lounge between the wings at F1, outdoor decks cantilevered 3 m north (over the falls view) and south.

## Structure decisions

11. Below-grade perimeter walls are reinforced concrete: 0.5 m retaining on the rock sides, 0.4 m on the river wall with windows. F1/E1 facades are glazed timber.
12. F4 and E2 ground slabs are 0.6 m rafts (F4 rock-anchored); suspended floors are 0.25 m slabs on the post-tensioned beams.
13. **Cafe ring** moved from Gym V2 (20, 0.2) to (16.6, −0.94), Ø 7.0, to sit inside the cafe space. *`model.fixtures`*
14. **Roof eaves: 2.5 m overhang on all sides** (like the reference image). For now this exists only in the 3D scene (`terrain/blender_scene.py`); it will move into the model when we design the roof.

## What got built this session

- **Drawings** (http://localhost:5280): every floor plan has rooms with names and areas, concrete walls, glazing, stairs and the cafe ring. Sections show slabs breaking around the spiral, core and stair openings, the spiral helix, and the F3→F4 stair. The Gym V2 underlay is off by default (one checkbox to turn it on).
- **3D** (`terrain/out/scene/site.blend`): the new building is generated from the model and Gym V2 is hidden. It has the column-free F1 hall with glulam roof beams, the post-tensioned floor beams, the spiral stair with timber treads, the pool (with a basin opening in the F4 slab), the garage glass and the daycare garden glass. Renders are in `terrain/runs/*_scene/sheet5.png`.

15. **River wall openings** (`W-west-C` → `openings`):
    - **F4:** 8 underwater windows, 2.4 × 2.0 m, along the pool.
    - **F3:** a continuous river window from the floor to 2.6 m, 42 m long. The water surface sits about 1.0 m above the floor, at waist height.
    - **F2:** a view band from 0.45 to 3.0 m above the floor.

    All are drawn in the plans and sections and cut into the 3D wall. The key render is `terrain/runs/*_scene/f3_river_window.png`: the river surface at waist height on the glass, rocks underwater, and the garage glass across the ravine.

## Not done yet (next steps)

- Interior partitions inside rooms (lockers, WCs, showers) and doors.
- Roof design (slope/flat, sod or timber, skylights).
- The rustic bridge (still Gym V2's slab), and reframing the north footbridge views.


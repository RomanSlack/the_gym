# Construction plan

We build the gym the way a real construction crew would, in stages. Each stage sits on the one before it, and **Roman reviews before we move on**. This doubles as the replay: every element carries a `phase` and is built in order, so Blender can play the actual construction as a timelapse alongside the design-history replay.

Source of truth stays `model/building.json`. Each stage adds real elements to it, with real thicknesses, layers and build order. Blender scenes are generated from it, one collection per phase.

## Progress

- ✅ **Stage 0 · Site**: `construction/out/stage_0.blend`, renders in `construction/renders/stage_0_*`.
- ✅ **Stage 1 · Foundations** (awaiting Roman's review): `construction/out/stage_1.blend`, renders in `construction/renders/stage_1_*`. 192 phase-1 elements from `tools/foundations.py`:
  - construction pit with rock-cut faces, and a temporary sheet-pile cofferdam that keeps the river off the river wall
  - 196 rock anchors (8 m, F4 raft + pool), blinding, thickened strip footings, rafts (F4, pool basin 2 m deeper, cores/lift pits, annexes, E2, parking), parking pad footings
  - below-grade retaining walls + the river wall with its formed window openings
  - waterproofing membranes, drainage gravel + perimeter drains
  - garage-ramp trench walls + cut-and-cover tunnel roof
  - site earthworks to formation level (added 2026-10-11, after the garden was missed): road + drop-off loop + trailhead lot, the **sunken daycare garden** (dug out, terraces roughed in, west retaining wall), the garage rock ledge, the sauna pad
- ✅ **Stage 2 · Exterior style: LOCKED = B, dark tarred timber + sod roofs, divided glazing** (see VISION.md, `docs/style/`).
- ✅ **Stage 3 · Structure** (awaiting Roman's review): `construction/out/stage_3.blend`, renders in `construction/renders/stage_3_*`. 214 phase-3 elements from `tools/structure_stage.py` (see STRUCTURE.md):
  - PT concrete floors F1–F3 + E1, pilasters, glulam facade columns, parking columns + buried roof
  - CLT 300 roofs with **2.5 m eaves in the model** (tapered glulam beam tails), one roof level across both wings and the lounge
  - lounge bridge on four dark steel girders + tapered deck outriggers; glulam roof beams on slim posts, glass walls can still open fully
  - concrete cores (incl. core E), precast dogleg stairs in every core, open steel + oak helix spiral, F3→F4 dogleg
- ✅ **Stage 4 · Envelope** (awaiting Roman's review): `construction/out/stage_4.blend`, renders in `construction/renders/stage_4_*` (`style_gorge`, `style_aerial`, `style_arrival` are framed like the stage-2 references `docs/style/bdarksod_*`). Elements from `tools/envelope.py`:
  - divided glazing with dark frames: a mullion at every column, panes ≤ 1.3 m (lounge sliding panels ≤ 2.3 m), transom on tall glass
  - **solid black board-on-board timber where privacy is needed** (changing rooms, wet zones, WCs, staff, nursing) with a high obscured clerestory band; glass everywhere else
  - black timber header band between the glass head and the roof; facade glulam posts black-stained (the dark posts of the references); beams, tails and oak soffits stay warm
  - 150 mm dry-laid granite plinth on every concrete face above the finished ground (river wall, towers, lift shafts, gorge faces), wrapping the slab edges
  - structural acrylic in the river-wall openings; sod roofs (0.45 m build-up) with thin dark roof edges, incl. the annex roofs; glass balustrades + dark edge plate on the lounge decks
  - backfill + final grading and the cofferdam pulled (the river is back in its bed); every enclosed volume (wings, cores, lift shafts, W3, rock annexes, sauna lobby, parking) is cut out of the finished ground exactly, so no ground runs through a stairwell or room and none of it gaps away from a wall
  - below-grade layers (membranes, drainage gravel, drains) stop under the finished ground; scour toe under the river wall; granite plinth under the sauna-lobby annex and on the garden wall
  - Next: stage 5, interior.
- 🔶 **Stage 5 · Interior shell, reception first:** all interior partitions up (stud + gypsum, framed glass); suspended slabs lowered 100 mm for the floor build-up; reception + cafe hall finished in the LOCKED light palette (see VISION.md). `tools/interior.py`, renders `construction/renders/stage_5_rec_*`. Next: roll the palette out zone by zone.
- Build: `terrain/.venv/bin/python tools/build_model.py` then `blender -b --factory-startup --python construction/scene.py -- <stage> render`.

## Stages

| # | Stage | What gets modelled | Review gate |
|---|---|---|---|
| 0 | **Site** | The exact landscape before any work: Elverum terrain + our ravine, river, falls, the 8 km context. No trees, no building. | Roman OK on the land |
| 1 | **Foundations** | Construction pit (excavation with rock-cut faces); temporary cofferdam in the river; rock anchors under F4; blinding; strip + pad footings; raft slabs; below-grade retaining walls + river wall; waterproofing; drainage; garage-ramp trench + tunnel; parking + annex foundations. | **STOP: Roman reviews** |
| 2 | **Exterior style** | gpt-image-2 explorations, using clean renders of the stage-1 massing from 4–6 fixed cameras as geometry references: timber, stone, roof edge, glazing rhythm, towers, bridge. Roman picks one; it's locked into VISION.md. | Roman picks a style |
| 3 | **Structure** | Concrete frame of F2–F4 (post-tensioned beams, slabs), glulam columns + beams on F1/E1, CLT roofs, lounge-bridge trusses, stairs, cores. | Review |
| 4 | **Envelope** | Backfill + final grading, cofferdam out; wall build-ups, cladding (per the chosen style), glazing systems, river windows, roof build-ups (sod, eaves), skylights. | Review |
| 5 | **Interior shell** (Roman, 2026-10-11) | All interior walls up and finished, floors, wall linings, ceilings: the building as handed over *before* interior design. **No furniture, equipment, fixtures or doors yet.** Done room by room: **reception first, until its materials + style are locked**, then rolled out. Alongside: trees (reduced render density for now) and grass / moss on the sod roofs, gardens and ground, so the interiors are designed against real views. | Review per zone |
| 5b | **Interior design** | Equipment layout from `docs/FIT_STUDY.md`, furniture, light fixtures, doors, locker fit-out, the den, pool + thermal, daycare, cafe ring. **All furniture and gym equipment is hand-designed by us** (Roman, 2026-10-11): every asset is generated in this project; only textures, HDRIs and the like are downloaded (scanned CC0, cached outside git, manifest of IDs committed: the repo is public). | Review |
| 6 | **Landscape + finish** | Planting + forest, paths, trail, water and falls, exterior lighting; surfacing (road asphalt, gravel lot, meadow, stepping stones); finishing the sunken garden (dry-stone face, terrace planting, play surface); **outbuildings + bridges**, each foundation → frame → envelope: sauna, bike shelter, rustic footbridge, upstream timber footbridge, trailhead kiosk, outdoor rig; final renders, then the replay video. | Final |

## Rules for every stage

- Real dimensions and real layer build-ups. Structure follows rules of thumb (no engineering calcs); assumptions are noted on the element.
- Open plan, column-free, no door unless needed (see VISION.md).
- Every element has `phase` (stage number) and `seq` (order within the stage) for the construction timelapse.
- Heavy things stay instanced (trees, anchors); one Blender collection per phase.
- The PDF drawing set is only re-exported when Roman asks.
- **Foliage hidden in the viewport in every saved .blend** (forest, grass, sod-roof grass modifiers) so files open without crashing or lagging; renders still include it.
- **Never overwrite an image.** Every render is kept as the next version (`construction/renders/stage_N_<camera>_vNNN.jpg`, written by `construction/scene.py`); generated art and figures get new filenames. Progress stays reviewable.
- **Coverage check:** `tools/stage_check.py` runs at the end of every build. Everything designed (site works in the terrain, site features, elements, stairs) must have an owner stage, and once that stage is built its work must exist. A new feature with no owner, or a built stage that skipped something, shows up as `!` lines. Fix those before showing Roman a stage. (Origin: the sunken daycare garden was designed but no stage dug it.) From stage 4 on it also checks that nothing meant to be buried shows above the finished ground and that no wall or footing hangs above the ground beside it (added after Roman spotted membranes, footings and gaps at the garden corners and tower bases).

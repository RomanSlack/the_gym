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
- ✅ **Stage 2 · Exterior style: LOCKED = B, dark tarred timber + sod roofs, divided glazing** (see VISION.md, `docs/style/`).
- ✅ **Stage 3 · Structure** (awaiting Roman's review): `construction/out/stage_3.blend`, renders in `construction/renders/stage_3_*`. 214 phase-3 elements from `tools/structure_stage.py` (see STRUCTURE.md):
  - PT concrete floors F1–F3 + E1, pilasters, glulam facade columns, parking columns + buried roof
  - CLT 300 roofs with **2.5 m eaves in the model** (tapered glulam beam tails), one roof level across both wings and the lounge
  - lounge bridge on four dark steel girders + tapered deck outriggers; glulam roof beams on slim posts, glass walls can still open fully
  - concrete cores (incl. core E), precast dogleg stairs in every core, open steel + oak helix spiral, F3→F4 dogleg
  - Next: stage 4, envelope.
- Build: `terrain/.venv/bin/python tools/build_model.py` then `blender -b --factory-startup --python construction/scene.py -- <stage> render`.

## Stages

| # | Stage | What gets modelled | Review gate |
|---|---|---|---|
| 0 | **Site** | The exact landscape before any work: Elverum terrain + our ravine, river, falls, the 8 km context. No trees, no building. | Roman OK on the land |
| 1 | **Foundations** | Construction pit (excavation with rock-cut faces); temporary cofferdam in the river; rock anchors under F4; blinding; strip + pad footings; raft slabs; below-grade retaining walls + river wall; waterproofing; drainage; garage-ramp trench + tunnel; parking + annex foundations. | **STOP: Roman reviews** |
| 2 | **Exterior style** | gpt-image-2 explorations, using clean renders of the stage-1 massing from 4–6 fixed cameras as geometry references: timber, stone, roof edge, glazing rhythm, towers, bridge. Roman picks one; it's locked into VISION.md. | Roman picks a style |
| 3 | **Structure** | Concrete frame of F2–F4 (post-tensioned beams, slabs), glulam columns + beams on F1/E1, CLT roofs, lounge-bridge trusses, stairs, cores. | Review |
| 4 | **Envelope** | Wall build-ups, cladding (per the chosen style), glazing systems, river windows, roof build-ups (sod, eaves), skylights. | Review |
| 5 | **Interior** | Finishes, the equipment layout from `docs/FIT_STUDY.md`, lighting, locker fit-out, the den, pool + thermal, daycare, cafe. | Review |
| 6 | **Landscape + finish** | Planting + forest, paths, water and falls, exterior lighting, final renders, then the replay video. | Final |

## Rules for every stage

- Real dimensions and real layer build-ups. Structure follows rules of thumb (no engineering calcs); assumptions are noted on the element.
- Open plan, column-free, no door unless needed (see VISION.md).
- Every element has `phase` (stage number) and `seq` (order within the stage) for the construction timelapse.
- Heavy things stay instanced (trees, anchors); one Blender collection per phase.
- The PDF drawing set is only re-exported when Roman asks.

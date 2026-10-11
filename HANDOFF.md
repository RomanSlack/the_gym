# Handoff (read first in a new session)

State on 2026-10-11: stages 0-4 built; stage 5 (interior shell) under way: reception palette LOCKED (light oak, slat walls, dark only at windows); next = roll it out room by room (see CONSTRUCTION_PLAN.md).

- Source of truth: `model/building.json`. Rebuild everything derived: `terrain/.venv/bin/python tools/build_model.py` (layout → structure → partitions → room numbers → foundations → stage-3 structure → stage-4 envelope → stage coverage check).
- Terrain: `terrain/` scripts (ravine.py → erode.py → export_blueprint.py). Construction scenes: `blender -b --factory-startup --python construction/scene.py -- <stage> render` (stages 0, 1, 3, 4 built; phase 3 / 4 elements come from `tools/structure_stage.py` / `tools/envelope.py`).
- Drawings: `cd blueprint && npx vite --port 5280` (H replay, P A1 sheets, D dark). PDF only when Roman asks: `node tools/export/export_pdf.js`.
- Decisions: VISION.md (incl. LOCKED exterior style B), STRUCTURE.md, DECISIONS_PENDING.md, docs/AUDIT.md, docs/FIT_STUDY.md.
- Roman's standing rules: open plan + no door unless needed; column-free; Gym V2 is his intent reference; no PDF re-export unless asked; every commit carries the Prompt trailer (hook in tools/capture).
- Before showing a stage: `build_model.py` ends with the stage coverage check (`tools/stage_check.py`); it must say OK. New design features need an owner stage in that file.
- **Replay discipline:** commit right after each change Roman asked for (incl. messages he sends mid-turn), not once per turn; the commit hook adds `Prompt:` + `Also-Prompt:` trailers for every message since the last commit automatically. Renders you make to check your work are kept as `_vNNN`; no extra renders just for the replay.
- Replays: drawings = H in `blueprint/`; 3D renders = `.capture/renders/replay.html` (rebuilt every turn by `tools/replay/render_history.py`, any camera, every version + its prompt).
- Never overwrite images: renders auto-version to `_vNNN.jpg`; anything else gets a new filename.
- Gotcha: Blender 4.1+ makes new faces smooth unless set flat (handled in construction/bl_common.py).

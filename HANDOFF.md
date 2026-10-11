# Handoff (read first in a new session)

State on 2026-10-11: stages 0-3 built, stage 3 (structure) **awaiting Roman's review**; next = stage 4 · Envelope (see CONSTRUCTION_PLAN.md).

- Source of truth: `model/building.json`. Rebuild everything derived: `terrain/.venv/bin/python tools/build_model.py` (layout → structure → partitions → room numbers → foundations → stage-3 structure → stage coverage check).
- Terrain: `terrain/` scripts (ravine.py → erode.py → export_blueprint.py). Construction scenes: `blender -b --factory-startup --python construction/scene.py -- <stage> render` (stages 0, 1, 3 built; stage 3 elements come from `tools/structure_stage.py`, run last by build_model).
- Drawings: `cd blueprint && npx vite --port 5280` (H replay, P A1 sheets, D dark). PDF only when Roman asks: `node tools/export/export_pdf.js`.
- Decisions: VISION.md (incl. LOCKED exterior style B), STRUCTURE.md, DECISIONS_PENDING.md, docs/AUDIT.md, docs/FIT_STUDY.md.
- Roman's standing rules: open plan + no door unless needed; column-free; Gym V2 is his intent reference; no PDF re-export unless asked; every commit carries the Prompt trailer (hook in tools/capture).
- Before showing a stage: `build_model.py` ends with the stage coverage check (`tools/stage_check.py`); it must say OK. New design features need an owner stage in that file.
- Gotcha: Blender 4.1+ makes new faces smooth unless set flat (handled in construction/bl_common.py).

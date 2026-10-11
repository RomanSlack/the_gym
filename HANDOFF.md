# Handoff (read first in a new session)

State on 2026-10-11: stages 0-2 done, **next = stage 3 · Structure** (see CONSTRUCTION_PLAN.md).

- Source of truth: `model/building.json`. Rebuild everything derived: `terrain/.venv/bin/python tools/build_model.py` (layout → structure → partitions → room numbers → foundations).
- Terrain: `terrain/` scripts (ravine.py → erode.py → export_blueprint.py). Construction scenes: `blender -b --factory-startup --python construction/scene.py -- <stage> render` (stages 0, 1 built; add stage 3 to `construction/scene.py` + a `tools/structure_stage.py` that tags phase-3 elements).
- Drawings: `cd blueprint && npx vite --port 5280` (H replay, P A1 sheets, D dark). PDF only when Roman asks: `node tools/export/export_pdf.js`.
- Decisions: VISION.md (incl. LOCKED exterior style B), STRUCTURE.md, DECISIONS_PENDING.md, docs/AUDIT.md, docs/FIT_STUDY.md.
- Roman's standing rules: open plan + no door unless needed; column-free; Gym V2 is his intent reference; no PDF re-export unless asked; every commit carries the Prompt trailer (hook in tools/capture).
- Gotcha: Blender 4.1+ makes new faces smooth unless set flat (handled in construction/bl_common.py).

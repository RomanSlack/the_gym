#!/bin/bash
# Walk the gym in scenewalk (~/tools/scenewalk): the layouts as they are now, live. Leave it open: rerun
# `python3 tools/viewer_manifest.py` after a layout change and it reloads by itself (R forces it). After a change to the
# building, the furnishings or a piece's model, re-export first:
#   blender -b construction/out/stage_5.blend --python construction/viewer_export.py      (-- shell | -- eq for half)
cd "$(dirname "$0")/.." || exit 1
python3 tools/viewer_manifest.py || exit 1
exec ~/tools/scenewalk/target/release/scenewalk construction/out/viewer/gym.json "$@"

#!/bin/bash
# Walk the gym in scenewalk (~/tools/scenewalk): the layouts as they are now, live. Leave it open: rerun
# `python3 tools/viewer_manifest.py` after a layout change and it reloads by itself (R forces it). After a change to the
# building, the furnishings or a piece's model, re-export first:
#   blender -b construction/out/stage_5.blend --python construction/viewer_export.py      (-- shell | -- eq for half)
# P captures the exact view into feedback/ for the markup app (http://localhost:5290, started here if it isn't running);
# tools/feedback.py reads the queue. --view feedback/<id>.json starts at a capture's spot.
cd "$(dirname "$0")/.." || exit 1
python3 tools/viewer_manifest.py || exit 1
MARKUP=~/tools/scenewalk/markup/markup.py
if ! curl -s -o /dev/null --max-time 1 http://localhost:5290/api/alive; then
    setsid nohup python3 "$MARKUP" serve --dir feedback --port 5290 --resolve "python3 $PWD/tools/feedback.py" > /tmp/markup_5290.log 2>&1 < /dev/null &
fi
exec ~/tools/scenewalk/target/release/scenewalk construction/out/viewer/gym.json --capture-dir feedback \
    --on-capture "python3 $MARKUP open --dir feedback --port 5290" "$@"

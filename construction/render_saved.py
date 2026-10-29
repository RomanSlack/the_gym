"""Render shots from the saved stage scene instead of rebuilding it (Roman 2026-10-28: "how do we optimize it like crazy": the
build is ~7 of every 8 minutes). One camera per process, memory-capped (a batched process once grew to 16 GB and systemd-oomd
killed Roman's session):

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
        blender -b construction/out/stage_5.blend -t 12 --python construction/render_saved.py -- 5 eq2_z_spine

The saved file must be current: rebuild it (python construction/scene.py -- 5, no render) after the model or layouts change.
"""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402
import shoot  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
STAGE, cams = int(args[0]), args[1:]
scene = bpy.context.scene
if all(n_.startswith("eq") for n_ in cams):  # layout check shots (Roman: "720p is fine not a ton of samples")
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1280, 720, 100
    scene.cycles.samples = 24
bc.gpu_or_stop()
EXPO = scene.view_settings.exposure
for n in cams:
    shoot.shoot(scene, n, n, EXPO, STAGE, bpy.data.objects.get("lod_eye"))

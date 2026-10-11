"""Extra review cameras on the saved site scene.

blender -b terrain/out/scene/site.blend --python terrain/blender_views.py -- <out_dir> view1 view2 ...
"""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = Path(args[0])
want = set(args[1:])
scene = bpy.context.scene
VIEWS = {
    # name: (location, target, lens or ("ORTHO", scale))
    "top_down": ((0, 5, 250), (0, 5.01, 0), ("ORTHO", 170)),
    "top_down_bridge": ((0, 30, 150), (0, 30.01, 0), ("ORTHO", 70)),
    "falls_from_pool": ((3, 18, -7.6), (-3, 37, -4.5), 16),
    "bridge_oblique_ne": ((45, 90, 38), (-3, 30, -4), 24),
    "east_wing_from_east": ((85, -25, 34), (15, 12, -5), 24),
    "sauna_from_stream": ((-5, 113, 1.4), (-21, 95, 1.2), 20),
    "garage_across_ravine": ((-3.5, -6, -5.5), (13, 3, -3.6), 16),
    "garage_inside_out": ((27, 1.5, -4.4), (0, 4, -5.2), 15),
    "garden_drone_close": ((44, 88, 44), (23, 40, -5), 26),
    "garden_from_daycare": ((22, 35.5, -4.4), (25, 60, -1.5), 15),
    "garden_to_daycare": ((27, 52, -1.0), (22, 33.5, -4.0), 16),
    "garage_tunnel_portal": ((96, 3, 3.5), (55, -3, -3.5), 20),
}
for name, (loc, tgt, lens) in VIEWS.items():
    if want and name not in want:
        continue
    cd = bpy.data.cameras.new(name)
    cd.clip_end = 12000
    if isinstance(lens, tuple):
        cd.type = "ORTHO"; cd.ortho_scale = lens[1]
    else:
        cd.lens = lens
    cam = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)

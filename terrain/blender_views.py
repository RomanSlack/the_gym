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
    "river_wall_from_east": ((9.5, -26, -7.6), (-6.45, -6, -10.5), 20),
    "f3_river_window": ((-13.0, -12.0, -8.3), (6.0, -9.0, -8.6), 18),
    "lifts_from_west": ((-58, -40, 28), (-30, -10, 1), 24),
    "f4_pool_deck": ((-21.0, 2.0, -13.6), (-10.0, -24.0, -15.2), 16),
    "garage_across_ravine": ((-3.5, -6, -5.5), (13, 3, -3.6), 16),
    "garage_inside_out": ((27, 1.5, -4.4), (0, 4, -5.2), 15),
    "garden_top": ((26, 43, 120), (26, 43.01, 0), ("ORTHO", 48)),
    "arrival_overview": ((95, -35, 38), (45, 12, -1), 26),
    "arrival_eye": ((60, 1.5, 1.8), (31, 12, 1.5), 22),
    "bike_shelter": ((43, 8, 2.2), (42, -4, 1.4), 20),
    "bike_room": ((29.5, -2.5, -4.6), (14, -8.5, -5.4), 18),
    "trailhead_sign": ((103.0, 26.0, 3.10), (109.5, 26.8, 2.95), 26),
    "west_garden": ((-50, -36, 4.5), (-36, -18, 0.6), 22),
    "west_garden_top": ((-42, -16, 70), (-42, -15.99, 0), ("ORTHO", 52)),
    "f3_den": ((-19.5, 4.0, -8.1), (-29.4, -22.0, -8.6), 20),
    "garden_drone_close": ((52, 78, 34), (26, 41, -5), 26),
    "garden_from_daycare": ((22, 35.5, -4.4), (25, 60, -1.5), 15),
    "garden_to_daycare": ((29, 57, 3.6), (26, 33.5, -4.5), 18),
    "trail_drone_north": ((-60.4, 610.0, 51.3), (-150.4, 690.0, 6.3), 24),
    "north_footbridge": ((-128.4, 672.0, 7.3), (-150.4, 690.0, 6.8), 18),
    "trail_in_forest": ((321.0, 752.3, 21.6), (347.6, 729.1, 21.0), 20),
    "trail_overview": ((700, -250, 420), (150, 450, 0), 26),
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

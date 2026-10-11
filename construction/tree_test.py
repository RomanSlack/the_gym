"""Tree test: one Scots pine + one Norway spruce at three distances in Cycles, a small grove for the far view, and a wind clip.

blender -b --factory-startup --python construction/tree_test.py -- [stills] [clip]
Writes construction/out/trees/*.png (+ wind.mp4).
"""
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402
import trees  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ROOT / "construction" / "out" / "trees"; OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = bc.collection("trees")

t0 = time.time()
pine, Hp, np_ = trees.make_tree("pine", 3, coll, at=(0, 0, 0), H=16)
spruce, Hs, ns_ = trees.make_tree("spruce", 5, coll, at=(14, 6, 0), H=18)
grove = []
for k, (kind, x, y) in enumerate([("spruce", -18, 40), ("spruce", -9, 46), ("pine", -2, 38), ("spruce", 6, 50), ("spruce", 15, 44), ("pine", 22, 36),
                                   ("spruce", 30, 52), ("spruce", -26, 55), ("pine", 10, 60), ("spruce", 38, 41), ("spruce", -32, 44), ("spruce", 24, 64)]):
    grove.append(trees.make_tree(kind, 100 + k, coll, at=(x, y, 0))[0])
print("generated in", round(time.time() - t0, 1), "s; shoots pine", np_, "spruce", ns_)

# ground: scanned forest floor at real scale, gently undulating
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
g = bpy.context.object; g.name = "ground"
sub = g.modifiers.new("sub", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = sub.render_levels = 6
disp = g.modifiers.new("undulate", "DISPLACE"); tx = bpy.data.textures.new("und", "CLOUDS"); tx.noise_scale = 25; disp.texture = tx; disp.strength = 1.2
gm = trees.tex_material("forest_floor", "forest_floor", scale=400 / 2.14)
g.data.materials.append(gm)

# sky + sun (late-afternoon Nordic light)
w = bpy.data.worlds.new("sky"); scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new("ShaderNodeTexSky")
for t in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "PREETHAM"):
    try:
        sky.sky_type = t; break
    except TypeError:
        continue
sky.sun_elevation = math.radians(24); sky.sun_rotation = math.radians(205)
try:
    sky.sun_disc = False  # the sun lamp is the sun; the sky only gives the blue fill
except AttributeError:
    pass
w.node_tree.links.new(sky.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.28
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); scene.collection.objects.link(sun)
sun.data.energy = 4.5; sun.data.angle = math.radians(0.6)
sun.rotation_euler = (math.radians(90 - 24), 0, math.radians(205 - 180))

scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
prefs = bpy.context.preferences.addons["cycles"].preferences
for dev in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = dev; prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        break
    except Exception:
        continue
scene.cycles.samples = 160; scene.cycles.use_denoising = True
scene.cycles.tile_size = 256  # short GPU kernels: the display GPU stays responsive
scene.render.resolution_x, scene.render.resolution_y = 1400, 1000
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"; scene.view_settings.exposure = -1.0

CAMS = {
    "pine_close": ((3.2, -3.6, 13.4), (0.6, 0.6, 15.8), 35),     # into the lower crown: needle pads, orange bark
    "pine_mid": ((10, -30, 2.0), (2, 0, 10.5), 28),
    "spruce_close": ((17.5, 1.2, 4.0), (14.2, 6.2, 5.6), 30),
    "spruce_mid": ((26, -22, 2.0), (14, 6, 11.5), 28),
    "grove_far": ((5, -95, 3.0), (6, 40, 10), 50),
    "trunk_close": ((1.6, -1.8, 1.7), (0, 0, 2.2), 30),
}
for n, (loc, tgt, lens) in CAMS.items():
    bc.camera(scene, f"cam_{n}", loc, tgt, lens)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "tree_test.blend"))
if "stills" in args:
    for n in CAMS:
        scene.camera = bpy.data.objects[f"cam_{n}"]
        scene.render.filepath = str(OUT / f"{n}.png")
        t1 = time.time(); bpy.ops.render.render(write_still=True); print("rendered", n, round(time.time() - t1, 1), "s")
if "clip" in args:
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = eng; break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 960, 686
    scene.camera = bpy.data.objects["cam_pine_mid"]
    scene.frame_start, scene.frame_end = 1, 96; scene.render.fps = 24
    scene.render.filepath = str(OUT / "wind_")
    bpy.ops.render.render(animation=True)
print("done")

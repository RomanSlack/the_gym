"""LOD test: the same pine / spruce at LOD 0 (every needle), LOD 1 (reduced) and LOD 2 (baked impostor), side by side,
seen from the distance each LOD takes over. If the swap is invisible there, the scatter can use them.

blender -b --factory-startup --python construction/lod_test.py -- [stills]
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
OUT = ROOT / "construction" / "out" / "trees" / "lod"; OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = bc.collection("trees")

t0 = time.time()
ROW = {}
for j, kind in enumerate(("pine", "spruce")):
    H = 21 if kind == "pine" else 25
    seed = 3 if kind == "pine" else 5
    for lod in (0, 1):
        ROW[(kind, lod)] = trees.make_tree(kind, seed, coll, at=(j * 60 + lod * 18, 0, 0), H=H, lod=lod)
print("generated in", round(time.time() - t0, 1), "s")
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

# LOD 2: bake impostors from the LOD 0 trees, place them as the third tree of each group
for j, kind in enumerate(("pine", "spruce")):
    root, H, _ = ROW[(kind, 0)]
    files, w, h = trees.bake_impostor(root, H, str(OUT / f"impostor_{kind}"))
    imp = trees.impostor_object(f"{kind}_lod2", files, w, h, coll); imp.location = (j * 60 + 36, 0, 0)
CAMS = {  # each pair at its switch distance: LOD0 vs LOD1 at 45 m, LOD0 vs LOD2 at 160 m
    "pine_L0_L1_45m": ((9, -45, 3), (9, 0, 10), 45),
    "pine_L0_L2_160m": ((18, -160, 4), (18, 0, 10), 110),
    "spruce_L0_L1_45m": ((69, -45, 3), (69, 0, 12), 45),
    "spruce_L0_L2_160m": ((78, -160, 4), (78, 0, 12), 110),
}
for n, (loc, tgt, lens) in CAMS.items():
    bc.camera(scene, f"cam_{n}", loc, tgt, lens)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "lod_test.blend"))
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

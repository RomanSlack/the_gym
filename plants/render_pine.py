"""Cloud-pruned pine renders: one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_pine.py -- SHOT OUT.png [--seed 1] [--samples 256] [--res x|draft]

SHOT: full (the tree in a blackened steel planter in a gym corner, portrait), pad (a cloud pad + the branch into it, close),
bark (the trunk where the plated bark turns to orange flakes).
"""
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402
import gen_birch  # noqa: E402
import gen_pine  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES, RES = opt("--seed", 1), opt("--samples", 256), opt("--res", "draft")
TREE = opt("--tree", "pine")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.render.resolution_x, sc.render.resolution_y = (2160, 2700) if RES == "x" else (1280, 1600)
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"

M = bc.interior_materials()
steel = bc.material("blackened_steel", (0.03, 0.029, 0.028), 0.62, metal=0.7)
soil = bc.material("bark_mulch", (0.05, 0.035, 0.025), 0.95)


def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); return o


box("wall", (0, 1.4, 1.8), (9, 0.1, 3.8), M["lime_plaster"])
box("floor", (0, -2, -0.05), (9, 9, 0.1), M["oak_floor"])
box("side", (-2.4, -2, 1.8), (0.1, 9, 3.8), M["oak_slat"])
box("ceil", (0, -2, 3.6), (9, 9, 0.1), bc.material("ceil", (0.7, 0.69, 0.66), 0.85))
PH = 0.4
if TREE == "birch":                                                   # a round planter, the stems from one root plate
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.48, depth=PH, location=(0, 0, PH / 2))
    bpy.context.object.data.materials.append(steel); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.465, depth=0.02, location=(0, 0, PH - 0.03))
    bpy.context.object.data.materials.append(soil)
    objs = gen_birch.build(SEED, (0, 0, PH - 0.05), height=2.9)
else:
    box("planter", (0, 0, PH / 2), (0.85, 0.85, PH), steel)
    box("soil", (0, 0, PH - 0.03), (0.826, 0.826, 0.02), soil)
    objs = gen_pine.build(SEED, (0, 0, PH - 0.05), height=2.6)
wood = [o for o in objs if o.name.endswith("_wood")][0]

wd = bpy.data.lights.new("window", "AREA"); wd.size = 2.0; wd.energy = 600; wd.color = (0.95, 0.97, 1.0)
w = bpy.data.objects.new("window", wd); sc.collection.objects.link(w); w.location = (-2.0, -3.0, 3.0)
w.rotation_euler = (mathutils.Vector((0, 0, 1.3)) - w.location).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.lights.new("wash", "AREA"); cd.size = 3.0; cd.energy = 160; cd.color = (1.0, 0.92, 0.8)
c_ = bpy.data.objects.new("wash", cd); sc.collection.objects.link(c_); c_.location = (0.8, -1.2, 3.5)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

if SHOT == "full":
    cam, tgt, lens = ((0.9, -4.4, 1.55), (0, 0, 1.4), 35) if TREE == "pine" else ((0.9, -5.0, 1.6), (0, 0, 1.65), 30)
elif SHOT == "bark":
    # aim at the front-most bark at ~1 m (the stems lean every which way)
    vs = [wood.matrix_world @ v.co for v in wood.data.vertices if abs(v.co.z + wood.location.z - 1.0) < 0.03]
    f_ = min(vs, key=lambda v: v.y)
    cam, tgt, lens = (f_.x + 0.3, f_.y - 0.75, 1.1), (f_.x, f_.y, 1.0), 55
else:                                                                   # a pad: the lowest one
    pads = [o for o in objs if o.name.startswith("pine_core")] or [type("o", (), {"location": mathutils.Vector((0.4, 0, 2.0))})]
    p = min(pads, key=lambda o: o.location.z).location
    cam, tgt, lens = (p.x * 0.6, p.y - 1.3, p.z + 0.35), (p.x, p.y, p.z), 60
c = bc.camera(sc, "cam", cam, tgt, lens); sc.camera = c
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

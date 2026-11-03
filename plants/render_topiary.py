"""Topiary renders: one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_topiary.py -- SHOT OUT.png [--seed 1] [--samples 256] [--res x|draft]

SHOT: set (a ball, a cone and a cloud in blackened-steel planters + a clipped block, in a gym corner: white-oiled oak
floor, lime plaster, an oak slat wall), close (the ball's clipped skin at 40 cm), solo:<shape> (one piece, square-on).
"""
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402
import gen_grass  # noqa: E402
import gen_topiary  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES, RES = opt("--seed", 1), opt("--samples", 256), opt("--res", "draft")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
portrait = SHOT == "close" or SHOT.startswith("solo")
sc.render.resolution_x, sc.render.resolution_y = ((2160, 2700) if portrait else (2700, 2160)) if RES == "x" else ((1280, 1600) if portrait else (1600, 1280))
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"

M = bc.interior_materials()
steel = bc.material("blackened_steel", (0.03, 0.029, 0.028), 0.62, metal=0.7)   # waxed, satin (0.45 read as plastic)
soil = bc.material("bark_mulch", (0.05, 0.035, 0.025), 0.95)


def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); return o


def planter(x, y, w, h, round_=False):
    """a blackened steel planter, soil 3 cm under the rim; returns the soil height"""
    if round_:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=w / 2, depth=h, location=(x, y, h / 2))
        bpy.context.object.data.materials.append(steel); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=w / 2 - 0.012, depth=0.02, location=(x, y, h - 0.03))
        bpy.context.object.data.materials.append(soil)
    else:
        box("planter", (x, y, h / 2), (w, w, h), steel)
        box("soil", (x, y, h - 0.03), (w - 0.024, w - 0.024, 0.02), soil)
    return h - 0.02


# the room
box("wall", (0, 0.6, 1.6), (9, 0.1, 3.4), M["lime_plaster"])
box("floor", (0, -2, -0.05), (9, 9, 0.1), M["oak_floor"])
box("side", (-2.6, -2, 1.6), (0.1, 9, 3.4), M["oak_slat"])
box("ceil", (0, -2, 3.2), (9, 9, 0.1), bc.material("ceil", (0.7, 0.69, 0.66), 0.85))

if SHOT == "grasses":
    # a long low trough of grasses: fountain grass, feather grass, miscanthus behind, fountain grass again
    box("trough", (0, 0.1, 0.2), (2.8, 0.55, 0.4), steel)
    box("trough_soil", (0, 0.1, 0.402), (2.776, 0.526, 0.006), M["pebbles"])    # (filled to the brim: the grass sat in a solid box)
    for i, (x, y, kind, sz) in enumerate(((-1.1, 0.05, "pennisetum", 1.25), (-0.55, 0.18, "stipa", 1.3), (-0.15, -0.02, "stipa", 1.1),
                                          (0.35, 0.22, "miscanthus", 1.0), (0.75, 0.0, "pennisetum", 1.2), (1.18, 0.2, "stipa", 1.1))):
        gen_grass.build(SEED + i, (x, 0.1 + y - 0.1, 0.4), kind=kind, size=sz)
    cam, tgt, lens = (0.6, -3.6, 1.1), (0, 0, 0.75), 35
elif SHOT.startswith("solo"):
    shape = SHOT.split(":")[1]
    size = {"ball": (0.62, 0.62, 0.58), "cone": (0.5, 0.5, 1.3), "cloud": (1.1, 0.8, 0.6), "block": (1.2, 0.45, 0.5)}[shape]
    z = planter(0, 0, max(size[0], size[1]) * 0.85, 0.5, round_=shape in ("ball", "cloud"))
    gen_topiary.build(SEED, (0, 0, z), shape=shape, size=size, name=shape)
    cam, tgt, lens = (0.4, -2.6, z + size[2] * 0.75), (0, 0, z + size[2] * 0.45), 60
else:
    z = planter(-0.9, 0.0, 0.55, 0.55, round_=True)
    gen_topiary.build(SEED, (-0.9, 0.0, z), shape="ball", size=(0.62, 0.62, 0.58), name="ball")
    z = planter(0.15, 0.1, 0.45, 0.45)
    gen_topiary.build(SEED + 1, (0.15, 0.1, z), shape="cone", size=(0.56, 0.56, 1.2), name="cone")
    z = planter(1.25, -0.05, 0.75, 0.42, round_=True)
    gen_topiary.build(SEED + 3, (1.25, -0.05, z), shape="cloud", size=(1.0, 0.75, 0.55), name="cloud")
    # a low clipped block in a long trough along the side wall
    box("trough", (-2.1, -0.9, 0.2), (0.4, 1.6, 0.4), steel)
    box("trough_soil", (-2.1, -0.9, 0.37), (0.376, 1.576, 0.02), soil)
    blk = gen_topiary.build(SEED + 2, (0, 0, 0), shape="block", size=(1.5, 0.36, 0.42), name="block", density=2200)
    for o in blk:
        o.rotation_euler = (0, 0, math.pi / 2); o.location = (-2.1, -0.9, 0.38)
    if SHOT == "set":
        cam, tgt, lens = (0.6, -3.9, 1.15), (-0.45, 0, 0.62), 30
    else:                                                               # close: the ball's skin
        cam, tgt, lens = (-0.75, -0.62, 0.95), (-0.9, 0.0, 0.78), 70

# light: a soft window from the left-front, a warm ceiling wash, a little bounce
wd = bpy.data.lights.new("window", "AREA"); wd.size = 1.6; wd.energy = 380; wd.color = (0.95, 0.97, 1.0)
w = bpy.data.objects.new("window", wd); sc.collection.objects.link(w); w.location = (-2.0, -3.2, 2.4)
w.rotation_euler = (mathutils.Vector((0, 0, 0.8)) - w.location).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.lights.new("wash", "AREA"); cd.shape = "RECTANGLE"; cd.size = 4.0; cd.size_y = 0.3; cd.energy = 120; cd.color = (1.0, 0.92, 0.8)
c_ = bpy.data.objects.new("wash", cd); sc.collection.objects.link(c_); c_.location = (0, -0.6, 3.12)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

c = bc.camera(sc, "cam", cam, tgt, lens); sc.camera = c
if SHOT == "close":
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 5.6
    f = bpy.data.objects.new("f", None); sc.collection.objects.link(f); f.location = (-0.88, -0.28, 0.85); c.data.dof.focus_object = f
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

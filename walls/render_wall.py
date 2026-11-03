"""Moss wall renders: one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python walls/render_wall.py -- SHOT OUT.png [--seed 1] [--samples 256] [--res x|draft]

SHOT: room (the panel in a gym corner: oak floor, pale walls, a bench), mid (the panel square-on), close (a 25 cm patch,
raking light). The room: a recessed linear light grazing down the wall, a soft window fill.
"""
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402
import gen_mosswall  # noqa: E402
import gen_greenwall  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES, RES = opt("--seed", 1), opt("--samples", 256), opt("--res", "draft")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.render.resolution_x, sc.render.resolution_y = (2160, 2700) if RES == "x" else (1600, 2000)
if SHOT in ("room", "mid"):
    sc.render.resolution_x, sc.render.resolution_y = (2700, 2160) if RES == "x" else (2000, 1600)
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"

KIND = opt("--kind", "green")
if KIND == "green":
    W, H, Z0 = 3.2, 3.12, 0.0
    MIX = tuple(float(v) for v in opt("--mix", "0.3,0.3,0.02,0.12,0.14,0.12").split(","))
    objs = gen_greenwall.build(SEED, (0, 0, Z0), width=W, height=H, mix=MIX, vine=opt("--vine", 1.3), spacing=opt("--spacing", 0.22))
else:
    W, H, Z0 = 2.4, 1.6, 0.55
    objs = gen_mosswall.build(SEED, (0, 0, Z0), width=W, height=H)
# the room in the gym's own materials (interior palette: white-oiled oak floor, warm lime plaster, oak slats)
M = bc.interior_materials()
steel = bc.material("blackened_steel", (0.035, 0.034, 0.033), 0.45, metal=0.85)
def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)       # (object-space textures at real scale)
    o.data.materials.append(mat if isinstance(mat, bpy.types.Material) else bc.material(name, mat, 0.85)); return o
box("wall", (0, 0.06, 1.6), (8, 0.1, 3.4), M["lime_plaster"])
box("floor", (0, -2, -0.05), (8, 8, 0.1), M["oak_floor"])
box("side", (-3.2, -2, 1.6), (0.1, 8, 3.4), M["oak_slat"] if KIND == "green" else M["lime_plaster"])
box("ceil", (0, -2, 3.3 if KIND != "green" else 3.15), (8, 8, 0.1), (0.7, 0.69, 0.66))
if KIND == "green":
    # a blackened-steel reveal round the planting and a drip trough at its foot (metal palette: blackened waxed steel)
    for (x, z, sx, sz) in ((-W / 2 - 0.02, H / 2, 0.04, H), (W / 2 + 0.02, H / 2, 0.04, H)):
        box("trim", (x, -0.02, z), (sx, 0.08, sz), steel)
    box("trough", (0, -0.1, 0.07), (W + 0.08, 0.2, 0.14), steel)
    box("pebbles", (0, -0.1, 0.13), (W, 0.18, 0.02), M["pebbles"])
# the wall wash: a linear slot in the ceiling set 0.5 m out, washing down the planting (not grazing the top leaves)
ld = bpy.data.lights.new("graze", "AREA"); ld.shape = "RECTANGLE"; ld.size = W; ld.size_y = 0.04; ld.energy = 110
ld.color = (1.0, 0.93, 0.82)
g = bpy.data.objects.new("graze", ld); sc.collection.objects.link(g); g.location = (0, -0.3, min(Z0 + H + 0.12, 3.08))
g.rotation_euler = (math.radians(-8), 0, 0)
if KIND == "green":
    ld.energy = 140; ld.size_y = 0.25; ld.spread = math.radians(80)
    g.location = (0, -1.0, 3.09); g.rotation_euler = (math.radians(30), 0, 0)   # (tilted toward the wall: +x rotation turns -z toward +y)
wd = bpy.data.lights.new("window", "AREA"); wd.size = 3.0; wd.energy = 90; wd.color = (0.92, 0.96, 1.0)
w = bpy.data.objects.new("window", wd); sc.collection.objects.link(w); w.location = (3.0, -3.5, 1.8)
w.rotation_euler = (mathutils.Vector((0, 0, 1.2)) - w.location).to_track_quat("-Z", "Y").to_euler()
if KIND == "green":
    wd.energy = 160; wd.size = 4.0; w.location = (1.5, -5.2, 2.9)       # a big soft fill from behind the camera
    w.rotation_euler = (mathutils.Vector((0, 0, 1.4)) - w.location).to_track_quat("-Z", "Y").to_euler()
    sc.view_settings.exposure = 0.0                                                   # (90 blew the white-oiled oak floor out)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.15
if SHOT == "room":
    # a bench in front: oak slab on blackened steel
    box("bench", (0.2, -0.6, 0.43), (1.6, 0.4, 0.05), M["oak_slat"])
    for x in (-0.45, 0.85):
        box("leg", (x, -0.6, 0.2), (0.05, 0.36, 0.4), steel if KIND == "green" else (0.03, 0.03, 0.03))
    cam_loc, tgt, lens = ((2.2, -5.2, 1.5), (0.0, 0, 1.45), 28) if KIND == "green" else ((1.7, -4.1, 1.45), (0.0, 0, 1.25), 32)
elif SHOT == "mid":
    cam_loc, tgt, lens = (0.15, -4.6 if KIND == "green" else -3.2, Z0 + H / 2), (0, 0, Z0 + H / 2), 35 if KIND == "green" else 40
else:
    tz = Z0 + H * 0.55
    cam_loc, tgt, lens = ((0.35, -1.25, tz + 0.15), (0.1, 0, tz), 70) if KIND == "green" else ((0.12, -0.42, tz + 0.12), (0.05, 0, tz), 60)
c = bc.camera(sc, "cam", cam_loc, tgt, lens); sc.camera = c
if SHOT == "close":
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 8.0
    f = bpy.data.objects.new("f", None); sc.collection.objects.link(f); f.location = (tgt[0], -0.2 if KIND == "green" else -0.05, tgt[2]); c.data.dof.focus_object = f
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

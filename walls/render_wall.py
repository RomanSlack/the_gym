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

W, H, Z0 = 2.4, 1.6, 0.55
objs = gen_mosswall.build(SEED, (0, 0, Z0), width=W, height=H)
# the room: the wall behind (pale lime plaster), the oak floor, a side wall
def box(name, loc, scale, rgb, rough=0.85):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = scale
    o.data.materials.append(bc.material(name, rgb, rough)); return o
box("wall", (0, 0.06, 1.6), (8, 0.1, 3.4), (0.62, 0.6, 0.56))
box("floor", (0, -2, -0.05), (8, 8, 0.1), (0.36, 0.26, 0.17), 0.5)
box("side", (-3.2, -2, 1.6), (0.1, 8, 3.4), (0.6, 0.58, 0.54))
box("ceil", (0, -2, 3.3), (8, 8, 0.1), (0.7, 0.69, 0.66))
# the grazing light: a narrow area strip just in front of the wall's top, pointing down it
ld = bpy.data.lights.new("graze", "AREA"); ld.shape = "RECTANGLE"; ld.size = W; ld.size_y = 0.04; ld.energy = 110
ld.color = (1.0, 0.93, 0.82)
g = bpy.data.objects.new("graze", ld); sc.collection.objects.link(g); g.location = (0, -0.18, Z0 + H + 0.12)
g.rotation_euler = (math.radians(-8), 0, 0)
wd = bpy.data.lights.new("window", "AREA"); wd.size = 3.0; wd.energy = 90; wd.color = (0.92, 0.96, 1.0)
w = bpy.data.objects.new("window", wd); sc.collection.objects.link(w); w.location = (3.0, -3.5, 1.8)
w.rotation_euler = (mathutils.Vector((0, 0, 1.2)) - w.location).to_track_quat("-Z", "Y").to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.15
if SHOT == "room":
    # a bench in front: oak slab on blackened steel
    box("bench", (0.2, -0.55, 0.43), (1.6, 0.4, 0.05), (0.4, 0.27, 0.15), 0.45)
    for x in (-0.45, 0.85):
        box("leg", (x, -0.55, 0.2), (0.05, 0.36, 0.4), (0.03, 0.03, 0.03), 0.4)
    cam_loc, tgt, lens = (1.7, -4.1, 1.45), (0.0, 0, 1.25), 32
elif SHOT == "mid":
    cam_loc, tgt, lens = (0.15, -3.2, Z0 + H / 2), (0, 0, Z0 + H / 2), 40
else:
    tz = Z0 + H * 0.55
    cam_loc, tgt, lens = (0.12, -0.42, tz + 0.12), (0.05, 0, tz), 60
c = bc.camera(sc, "cam", cam_loc, tgt, lens); sc.camera = c
if SHOT == "close":
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 8.0
    f = bpy.data.objects.new("f", None); sc.collection.objects.link(f); f.location = (tgt[0], -0.05, tgt[2]); c.data.dof.focus_object = f
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

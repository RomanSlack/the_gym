"""Test renders for the plant generators that follow the image-first method (gen_<plant>.py with build() and FRAME):
one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_plant.py -- PLANT SHOT OUT.png [--seed 1] [--samples 256]

SHOT: hero, trio (three seeds), close (FRAME["close"]), backlit.
"""
import importlib
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
PLANT, SHOT, OUT = a[0], a[1], a[2]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES = int(opt("--seed", 1)), int(opt("--samples", 256))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"
from stage import look, pot, room  # noqa: E402

gen = importlib.import_module(f"gen_{PLANT}")
F = gen.FRAME
PS = F.get("pot_scale", 1.0)


def plant(seed, x):
    zs = pot((x, 0, 0), seed, scale=PS) if PS else 0.0
    return gen.build(seed, (x, 0, zs), 0.174 * PS, zs)


if SHOT == "trio":
    sp = F.get("spacing", 1.4)
    for i, x in enumerate((-sp, 0.0, sp)):
        plant(SEED + i, x)
    room(mathutils.Vector((-2.2, -2.4, 2.8)), 260)
    look(*F["trio"])
else:
    objs = plant(SEED, 0.0)
    if F.get("auto") and SHOT in ("hero", "close", "backlit", "base"):
        # frame the tree itself (they lean and spread differently): its bounding box, the camera along FRAME's direction
        pts = [o.matrix_world @ mathutils.Vector(c) for o in objs if o.get("tree") for c in o.bound_box]
        lo = mathutils.Vector([min(p_[i] for p_ in pts) for i in range(3)]); hi = mathutils.Vector([max(p_[i] for p_ in pts) for i in range(3)])
        c = (lo + hi) / 2
        cam, tgt, lens = F[SHOT if SHOT in F else "hero"]
        d = (mathutils.Vector(cam) - mathutils.Vector(tgt)).normalized() if SHOT != "base" else mathutils.Vector((0.3, -1, 0.75)).normalized()
        size = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)
        fit = {"hero": 1.4, "backlit": 1.4, "close": 0.55, "base": 0.55}[SHOT]
        if SHOT == "base":                                             # the trunk's foot and the pot's moss
            c = mathutils.Vector((c.x, c.y, lo.z + (hi.z - lo.z) * 0.08)); size = hi.z - lo.z
        dist = max(size * fit / (2 * math.tan(math.atan(18 / lens))), 0.45 if SHOT == "base" else 0.0)
        if SHOT == "close":
            c = c + mathutils.Vector((0, 0, -(hi.z - lo.z) * 0.2))
        F[SHOT] = (tuple(c + d * dist), tuple(c), lens)
    if SHOT == "pot":                                                  # the moss in the pot, from in front and above
        pot_o = [o for o in objs if o.name.startswith("bonsai_pot")][0]
        pts = [pot_o.matrix_world @ mathutils.Vector(c_) for c_ in pot_o.bound_box]
        lo = mathutils.Vector([min(p_[i] for p_ in pts) for i in range(3)]); hi = mathutils.Vector([max(p_[i] for p_ in pts) for i in range(3)])
        tgt = mathutils.Vector(((lo.x + hi.x) / 2, lo.y + (hi.y - lo.y) * 0.28, hi.z))
        F["pot"] = (tuple(tgt + mathutils.Vector((0.12, -0.32, 0.26))), tuple(tgt), 45)
    if SHOT == "backlit":
        room(mathutils.Vector((0.3, 1.25, 1.6)), 700, rim=False)
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
        look(*F.get("backlit", F["hero"]))
    else:
        room(mathutils.Vector((-2.0, -2.2, 2.6)), 200)
        look(*F.get(SHOT, F["hero"]))
if SHOT != "backlit":
    bc.hdri_world(sc, strength=0.35)                                  # the real sky over the open room: something to reflect
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

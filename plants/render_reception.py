"""Reception greenery in the real building (Roman 2026-11-03: "alr render please, i want to see visually"). Opens the saved
stage 5 scene, adds the plants from docs/greenery/reception_spots_v001.png and renders ONE shot per process:

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
        blender -b construction/out/stage_5.blend -t 12 --python plants/render_reception.py -- SHOT

SHOT: entry (from the daycare side across the entry), cafe_side (from the cafe edge to the doors), nook, bonsai, arrive (outside)
  1  two cloud-pruned Scots pines in square blackened-steel planters, outside either side of the porch
  2  a fiddle-leaf fig in a tall round planter in the south-east corner, by the east glass
  3  a Boston fern on a tall round planter in the waiting nook, below the window line
  4  a shimpaku bonsai on the south end of the desk's high stone ledge (the low end is the accessible counter: kept clear)
Kept as construction/renders/stage_5_rec_green_<shot>_vNNN.jpg (never overwritten).
"""
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (HERE, ROOT / "walls", ROOT / "construction"):
    sys.path.insert(0, str(p))
import bl_common as bc  # noqa: E402
import shoot  # noqa: E402

SHOT = sys.argv[sys.argv.index("--") + 1:][0]
scene = bpy.context.scene
bc.gpu_or_stop()
EXPO = scene.view_settings.exposure
dg = bpy.context.evaluated_depsgraph_get()
coll = bpy.data.collections.new("7 · greenery"); scene.collection.children.link(coll)


def ground(x, y, z0=2.6):
    """the first surface below (x, y, z0): floor, mat, ledge or terrain (grass + forest are off in the saved viewport)"""
    hit, loc, *_ = scene.ray_cast(dg, Vector((x, y, z0)), Vector((0, 0, -1)))
    assert hit, (x, y)
    return loc.z


def adopt(before):
    for o in set(bpy.data.objects) - before:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)


steel = bc.material("blackened_steel_planter", (0.03, 0.029, 0.028), 0.62, metal=0.7)
soil = bc.material("bark_mulch", (0.05, 0.035, 0.025), 0.95)


def planter(x, y, z, w, h, round_=True):
    """a blackened steel planter standing at z; returns the soil height"""
    if round_:
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=w / 2, depth=h, location=(x, y, z + h / 2))
        bpy.context.object.data.materials.append(steel); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=w / 2 - 0.012, depth=0.02, location=(x, y, z + h - 0.03))
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + h / 2)); bpy.context.object.scale = (w, w, h)
        bpy.context.object.data.materials.append(steel)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + h - 0.03)); bpy.context.object.scale = (w - 0.024, w - 0.024, 0.02)
    bpy.context.object.data.materials.append(soil)
    return z + h - 0.02


# each shot builds only the plants it sees (all of them at once ran the 12 GB card out of memory: the bonsai alone is 8.5 M faces)
SEES = {"arrive": {"pines": 2600}, "cafe_side": {"pines": 900, "fig": 1, "fern": 1, "bonsai": 0.25}, "entry": {"fig": 1, "fern": 1, "bonsai": 0.25},
        "nook": {"pines": 900, "fern": 1}, "bonsai": {"bonsai": 1.0}}[SHOT]
before = set(bpy.data.objects)
import gen_pine, gen_ficus, gen_fern, fern_mat  # noqa: E402,E401
zg = zf = zn = zl = None
# 1  the pines outside the porch (porch y 9.3-13.3, outer glass x 32.9)
if "pines" in SEES:
    for seed, y in ((3, 8.7), (5, 13.9)):
        zg = ground(32.4, y, 3.5)
        zs = planter(32.4, y, zg, 0.85, 0.5, round_=False)
        gen_pine.build(seed, (32.4, y, zs - 0.03), height=2.4, density=SEES["pines"])
# 2  the fig in the SE corner by the east glass
if "fig" in SEES:
    zf = ground(29.95, 7.55)
    gen_ficus.build(2, (29.95, 7.55, planter(29.95, 7.55, zf, 0.6, 0.6) - 0.01), height=2.7)
# 3  the fern in the nook
if "fern" in SEES:
    zn = ground(30.0, 14.55)
    gen_fern.build(4, (30.0, 14.55, planter(30.0, 14.55, zn, 0.36, 0.62)), pot_r=0.16, mat=fern_mat.leaf_material())
# 4  the bonsai on the desk's high ledge, south end (its display table removed: the pot stands on the stone)
if "bonsai" in SEES:
    os.environ.setdefault("BONSAI_STYLE", "dome")
    import gen_bonsai  # noqa: E402
    zl = ground(25.86, 9.4, 1.5)
    b_before = set(bpy.data.objects)
    gen_bonsai.build(7, (25.86, 9.4, zl - gen_bonsai.TABLE))
    for o in set(bpy.data.objects) - b_before:
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith("table_oak"):
            bpy.data.objects.remove(o)
    if SEES["bonsai"] < 1:   # seen from 4-6 m: a random share of the foliage faces is plenty
        for o in set(bpy.data.objects) - b_before:
            if o.type == "MESH" and len(o.data.polygons) > 500000:
                bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
                bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_mode(type="FACE"); bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_random(ratio=1 - SEES["bonsai"], seed=1); bpy.ops.mesh.delete(type="FACE")
                bpy.ops.object.mode_set(mode="OBJECT")
adopt(before)
print("greenery: ground", {"pines": zg, "fig": zf, "nook": zn, "ledge": zl})

# the shots
E1 = 0.12
CAMS = {
    "entry": ((27.6, 15.7, 1.62), (28.6, 7.0, 1.4), 18),
    "cafe_side": ((26.6, 5.6, 1.62), (29.4, 14.5, 1.3), 18),
    "nook": ((27.4, 12.6, 1.5), (29.8, 14.6, 1.0), 20),
    "bonsai": ((27.4, 8.3, 1.55), (25.86, 9.4, 1.3), 38),
}
if SHOT == "arrive":
    cx = 41.0; cz = ground(cx, 11.3, 20.0) + 1.65
    CAMS["arrive"] = ((cx, 11.3, cz), (31.5, 11.3, cz + 0.4), 26)
loc, tgt, lens = CAMS[SHOT]
name = f"rec_green_{SHOT}" if SHOT != "arrive" else "green_arrive"
bc.camera(scene, f"cam_{name}", loc, tgt, lens)
shoot.shoot(scene, name, name, EXPO, 5, bpy.data.objects.get("lod_eye"))

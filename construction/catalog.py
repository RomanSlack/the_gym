"""Component catalogue (Roman, 2026-10-12: "from each angle ... render it so I can see each element").
Every designed piece in model['furnishings'] (one per kind + parameter set, first use) is built alone in a neutral studio and
rendered from four angles (3/4 front, front, side, 3/4 back); the four are put on one labelled sheet per piece, plus an
overview sheet of all of them. Nothing is overwritten: sheets go to construction/renders/catalog/<name>_vNNN.jpg.

nice -n 19 blender -b --factory-startup -t 12 --python construction/catalog.py -- [zone:daycare,garden,wc,...] [only:kind1,kind2]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402
import furniture  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ZONES = next((a.split(":", 1)[1].split(",") for a in args if a.startswith("zone:")), None)
ONLY = next((a.split(":", 1)[1].split(",") for a in args if a.startswith("only:")), None)
SKIP = {"light_only", "porch_floor"}
OUT = ROOT / "construction" / "renders" / "catalog"; OUT.mkdir(parents=True, exist_ok=True)
TMP = ROOT / "construction" / "out" / "catalog_frames"; TMP.mkdir(parents=True, exist_ok=True)
model = json.loads((ROOT / "model" / "building.json").read_text())

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "GPU"; scene.cycles.tile_size = 256
scene.cycles.samples = 48; scene.cycles.use_denoising = True
pr = bpy.context.preferences.addons["cycles"].preferences
for dev in ("OPTIX", "CUDA"):
    try:
        pr.compute_device_type = dev; pr.get_devices()
        for d in pr.devices:
            d.use = True
        break
    except Exception:
        continue
scene.render.resolution_x, scene.render.resolution_y = 900, 700
scene.view_settings.view_transform = "AgX"; scene.view_settings.exposure = 0.0
w = bpy.data.worlds.new("studio"); scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.88, 0.85, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
for name, rot, energy in (("key", (50, 0, -40), 3.0), ("fill", (65, 0, 140), 1.0)):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, "SUN")); L.data.energy = energy; L.data.angle = math.radians(8)
    L.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(L)
floor_mat = bc.material("studio_floor", (0.78, 0.76, 0.73), 0.7)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001)); bpy.context.object.data.materials.append(floor_mat)

MAT = {**bc.interior_materials(), "glass": bc.arch_glass("arch_glass"), "frame": bc.blackened_steel()}
furniture.materials(MAT)

# one piece per kind + parameter set (the first time it is used)
seen, pieces = set(), []
for f in model.get("furnishings", []):
    k = f["kind"]
    if k in SKIP or (ZONES and f.get("zone") not in ZONES) or (ONLY and k not in ONLY):
        continue
    if k in seen:
        continue
    seen.add(k); pieces.append(f)
print("catalogue:", len(pieces), "pieces")


def build(f):
    kw = {}
    for k in furniture.PARAMS.get(f["kind"], ()):
        if k in f:
            name = {"length": "L", "height": "h", "width": "w"}.get(k, k) if (k == "length" or (k == "height" and f["kind"] == "bar_stool")
                                                                             or (k == "width" and f["kind"] == "gate")) else k
            kw[name] = tuple(f[k]) if isinstance(f[k], list) and k not in ("labels",) else f[k]
    coll = bpy.data.collections.new("piece_" + f["kind"]); scene.collection.children.link(coll)
    P = furniture.Part(coll.name)
    furniture.BUILDERS[f["kind"]](P, **kw)
    obs = P.build(coll, bevel={"rug": 0.0, "rug_round": 0.0, "soft_play": 0.03, "floor_cushion": 0.0}.get(f["kind"], 0.004))
    return coll, obs


def frame(obs):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, (hi - lo).length / 2, lo.z


VIEWS = [("3/4 front", 35, 18), ("front", 0, 8), ("side", 90, 8), ("3/4 back", 215, 22)]  # azimuth from the front (+y), elevation
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 50
shots_all = []


for f in pieces:
    for c in scene.collection.children:
        c.hide_render = True
    coll, obs = build(f)
    coll.hide_render = False
    ctr, rad, zmin = frame(obs)
    rad = max(rad, 0.25)
    shots = []
    for label, az, el in VIEWS:
        a, e = math.radians(az), math.radians(el)
        dist = rad / math.tan(math.radians(17)) * 1.05  # 50 mm lens on a 36 mm sensor: ~20 deg half-angle vertically at 900x700
        d = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
        cam.location = ctr + d * dist
        cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
        p = TMP / f"{f['kind']}_{az}.png"
        scene.render.filepath = str(p); bpy.ops.render.render(write_still=True)
        shots.append((label, p))
    shots_all.append({"kind": f["kind"], "note": f.get("note") or "", "shots": [[lbl, str(p)] for lbl, p in shots]})
    for o in obs:
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(coll)

# sheets are composed outside Blender (its Python has no PIL): tools/catalog_sheets.py
import subprocess  # noqa: E402
(TMP / "shots.json").write_text(json.dumps(shots_all, indent=1))
subprocess.run([str(ROOT / "terrain" / ".venv" / "bin" / "python"), str(ROOT / "tools" / "catalog_sheets.py"), str(TMP / "shots.json")], check=False)
print("catalogue done")

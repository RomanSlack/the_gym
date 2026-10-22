"""A line-up of modelled pieces in one scene (each built from its model.py, as in the studio), rendered from a few views, to judge them together.

    nice -n 19 blender -b --factory-startup -t 12 --python equipment/tools/lineup.py -- <name> <layout.json>

layout.json: {"rows": [{"x": metres, "gap": metres, "pieces": [piece, ...]}, ...]}: each row stands along y at its x,
the pieces side by side, `gap` between their footprints, every piece in its own model axes (along x, head at +x).
-> equipment/lineups/<name>_<view>_vNNN.jpg (never overwritten). GPU or nothing (exit 3).
"""
import json
import math
import os
import re
import sys
from pathlib import Path

import importlib.util

import bpy
from mathutils import Vector

EQ = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index("--") + 1:]
NAME, LAYOUT = args[0], json.loads(Path(args[1]).read_text())
OUT = EQ / "lineups"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(EQ / "blender"))
import kit  # noqa: E402


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.tile_size = 256
pr = bpy.context.preferences.addons["cycles"].preferences
for dev in ("OPTIX", "CUDA"):
    try:
        pr.compute_device_type = dev; pr.get_devices()
    except Exception:
        continue
    if [d for d in pr.devices if d.type == dev]:
        for d in pr.devices:
            d.use = d.type == dev
        break
else:
    print("\n!! NO GPU: Cycles cannot reach the NVIDIA GPU, stopping instead of rendering on the CPU.\n", flush=True)
    os._exit(3)
sc.cycles.samples = 160; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 2000, 1100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92

# ---- the pieces, row by row
lo, hi = Vector((1e9, 1e9, 0)), Vector((-1e9, -1e9, 0))
for row in LAYOUT["rows"]:
    placed = []
    for piece in row["pieces"]:
        # built from its model.py with the kit, exactly as the studio does (the .glb loses the procedural looks: grain,
        # bumps, sheen), so the line-up shows each piece as its own renders do
        spec = importlib.util.spec_from_file_location(f"pm_{piece}", EQ / "pieces" / piece / "model.py")
        pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
        coll = bpy.data.collections.new(piece); sc.collection.children.link(coll)
        k = kit.Kit(piece, coll, getattr(pm, "LOOK", None))
        pm.build(k)
        obs = k.finish()
        bpy.context.view_layer.update()
        roots = obs
        mn = Vector((min(c[i] for o in obs if o.type == "MESH" for c in (o.matrix_world @ Vector(b) for b in o.bound_box)) for i in range(3)))
        mx = Vector((max(c[i] for o in obs if o.type == "MESH" for c in (o.matrix_world @ Vector(b) for b in o.bound_box)) for i in range(3)))
        placed.append((roots, mn, mx))
    width = sum(mx.y - mn.y for _, mn, mx in placed) + row["gap"] * (len(placed) - 1)
    y = -width / 2
    for roots, mn, mx in placed:
        d = Vector((row["x"] - (mn.x + mx.x) / 2, y - mn.y, 0))
        for r in roots:
            r.location += d
        lo = Vector((min(lo.x, mn.x + d.x), min(lo.y, mn.y + d.y), 0)); hi = Vector((max(hi.x, mx.x + d.x), max(hi.y, mx.y + d.y), max(hi.z, mx.z)))
        y += (mx.y - mn.y) + row["gap"]
c = (lo + hi) / 2; c.z = 0.5

# ---- a gym-like floor and soft light
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.56, 0.58, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
bpy.ops.mesh.primitive_plane_add(size=60, location=(c.x, c.y, 0))
fm = bpy.data.materials.new("floor"); fm.use_nodes = True
b = fm.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.05, 0.05, 0.055, 1); b.inputs["Roughness"].default_value = 0.7
bpy.context.object.data.materials.append(fm)


def area(loc, energy, size):
    L = bpy.data.objects.new("L", bpy.data.lights.new("L", "AREA")); L.data.energy = energy; L.data.size = size
    L.location = loc; L.rotation_euler = (c - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(L)


span = (hi - lo).length
area(c + Vector((-0.45 * span, -0.55 * span, 0.6 * span)), 1700, span * 0.5)      # key
area(c + Vector((0.55 * span, -0.25 * span, 0.4 * span)), 500, span * 0.5)        # fill
area(c + Vector((0.2 * span, 0.6 * span, 0.7 * span)), 1000, span * 0.5)          # rim
area(c + Vector((0, 0, 0.9 * span)), 700, span * 0.8)                              # top

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {"three_quarter": (-125, 28, 0.95, 35), "eye_level": (-90, 8, 0.95, 40), "side": (-20, 18, 0.95, 35),
         "top": (-90, 89.5, 1.0, 35)}


def nextv(view):
    vs = [int(m.group(1)) for f in OUT.glob(f"{NAME}_{view}_v*.jpg") if (m := re.search(r"_v(\d{3})\.jpg$", f.name))]
    return OUT / f"{NAME}_{view}_v{max(vs, default=0) + 1:03d}.jpg"


rad = 0.5 * (hi - lo).length
for view, (az, el, zoom, lens) in VIEWS.items():
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    dv = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    fov = 2 * math.atan(18 / lens) * (1100 / 2000)
    cam.location = c + dv * (rad / math.sin(fov / 2) * 0.62 / zoom)
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(nextv(view))
    bpy.ops.render.render(write_still=True)
    print("view:", sc.render.filepath, flush=True)

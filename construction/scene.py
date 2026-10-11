"""Construction scene, built stage by stage from the model (see CONSTRUCTION_PLAN.md).

blender -b --factory-startup --python construction/scene.py -- <stage> [render]
  stage 0: site, the land before any works (no trees, no building)
  stage 1: + foundations (construction pit, cofferdam, anchors, footings, rafts, retaining walls, waterproofing, drainage)
Writes construction/out/stage_<n>.blend (+ renders), one collection per phase.
"""
import json
import sys
from pathlib import Path

import math
import numpy as np
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
STAGE = int(args[0]) if args else 0
RENDER = "render" in args
OUT = ROOT / "construction" / "out"; OUT.mkdir(parents=True, exist_ok=True)
RV, SITE = ROOT / "terrain" / "out" / "ravine", ROOT / "terrain" / "out" / "site"
model = json.loads((ROOT / "model" / "building.json").read_text())
DATUM = model["project"]["datum"]["masl"]
rng = np.random.default_rng(3)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bc.world_and_render(scene)

# ---------------------------------------------------------------- terrain for this stage
DX0, DX1, DY0, DY1 = -320, 620, -320, 900
c = (slice(1000 + DY0, 1000 + DY1), slice(1000 + DX0, 1000 + DX1))
natural = np.load(RV / "natural_eroded_1m.npy")
rock = np.load(RV / "rock_natural_1m.npy")  # rock on the natural ravine walls (incl. where the building will go)
cut = np.zeros_like(natural)
H = natural.copy()
if STAGE >= 1:
    pit = np.load(ROOT / "construction" / "out" / "pit_1m.npy")  # written by construction/foundations.py
    cut = (pit < natural - 0.05).astype(np.float32)
    H = np.minimum(natural, pit)

site0 = bc.collection("0 · site")
terr = bc.grid_mesh("terrain_detail", H[c], DX0 + 0.5, DY0 + 0.5, 1.0, {"rock": rock[c], "cut": cut[c]}, coll=site0)
terr.data.materials.append(bc.terrain_material())
ctx = np.load(SITE / "context_4m.npy") - DATUM
g4 = lambda w: (w + 4000) // 4
ctx[750:1250, 750:1250] = natural.reshape(500, 4, 500, 4).mean((1, 3))
ctx[g4(DY0) + 2:g4(DY1) - 2, g4(DX0) + 2:g4(DX1) - 2] -= 60
far = bc.grid_mesh("terrain_context", ctx[::2, ::2], -4000 + 2, -4000 + 2, 8.0, {"rock": np.zeros(ctx[::2, ::2].shape), "cut": np.zeros(ctx[::2, ::2].shape)}, coll=site0)
far.data.materials.append(bpy.data.materials["terrain"])

W = np.load(RV / "water_1m.npy")
if STAGE >= 1 and (OUT / "dewatered_1m.npy").exists():
    W = np.where(np.load(OUT / "dewatered_1m.npy") > 0, np.nan, W)  # inside the cofferdam the river is pumped dry
bc.water_mesh("river", W[c], DX0 + 0.5, DY0 + 0.5, 1.0, coll=site0)

# natural cliffs (only where the ravine was already rock, not on excavation faces)
busy = cut[c] > 0
for _ in range(5):  # keep natural rock blocks clear of the excavation and the new walls
    busy = busy | np.roll(busy, 1, 0) | np.roll(busy, -1, 0) | np.roll(busy, 1, 1) | np.roll(busy, -1, 1)
bc.cliff_rocks(natural[c], rock[c], DX0, DY0, exclude=busy, rng=rng, coll=site0)

# falls: water curtains where the designed water level drops > 2 m between close stations
st = sorted(model["site"]["ravine"]["stations"], key=lambda s: -s["y"])
foam = bc.material("falls", (0.85, 0.9, 0.9), rough=0.5)
for a, b in zip(st, st[1:]):
    if a["water"] - b["water"] > 2 and a["y"] - b["y"] < 6:
        ym, hw, xc = (a["y"] + b["y"]) / 2, a["half_bed"] + 0.5, (a["x"] + b["x"]) / 2
        vs, fs = [], []
        for k in range(25):
            x = xc - hw + 2 * hw * k / 24; j = 0.4 * np.sin(k * 1.7)
            vs += [(x, ym + 0.6 + j * 0.3, a["water"]), (x, ym - 0.8 + j, b["water"] + 0.3)]
            if k:
                fs.append((2 * k - 2, 2 * k, 2 * k + 1, 2 * k - 1))
        bc.mesh_from(f"falls_{a['id']}", vs, fs, coll=site0).data.materials.append(foam)

# ---------------------------------------------------------------- built elements for this stage
MAT = {
    "concrete": bc.material("concrete", (0.48, 0.47, 0.44), 0.85),
    "lean": bc.material("lean_concrete", (0.36, 0.35, 0.33), 0.9),
    "steel": bc.material("steel_anchor", (0.25, 0.22, 0.2), 0.5, metal=0.8),
    "sheetpile": bc.material("sheet_pile", (0.22, 0.2, 0.18), 0.6, metal=0.6),
    "membrane": bc.material("membrane", (0.04, 0.04, 0.045), 0.6),
    "gravel": bc.material("drain_gravel", (0.33, 0.31, 0.28), 1.0),
    "pipe": bc.material("drain_pipe", (0.6, 0.45, 0.1), 0.5),
}
for ph in range(1, STAGE + 1):
    coll = bc.collection({1: "1 · foundations"}.get(ph, f"{ph}"))
    for e in sorted((e for e in model["elements"] if e.get("phase") == ph), key=lambda e: e.get("seq", 0)):
        mat = MAT.get(e["material"], MAT["concrete"])
        z0, z1 = e["z"]
        if e["type"] in ("slab", "footing", "blinding") and "rect" in e:
            x0, y0, x1, y1 = e["rect"]; ob = bc.box(e["id"], x0, y0, z0, x1, y1, z1, mat, coll)
            for k, h in enumerate(e.get("holes", [])):
                if "rect" in h:  # e.g. the pool basin through the F4 raft
                    xs_, ys_ = [p[0] for p in h["rect"]], [p[1] for p in h["rect"]]
                    cu = bc.box(f"{e['id']}_hole{k}", min(xs_), min(ys_), z0 - 0.5, max(xs_), max(ys_), z1 + 0.5, mat, coll)
                    cu.hide_render = True; cu.hide_viewport = True
                    md = ob.modifiers.new(f"hole{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cu
        elif e["type"] in ("wall", "sheetpile", "membrane", "drain_layer", "strip_footing"):
            ob = bc.oriented_box(e["id"], e["from"], e["to"], e["size"][0], z0, z1, mat, coll)
            (wx0, wy0), (wx1, wy1) = e["from"], e["to"]
            WL = math.hypot(wx1 - wx0, wy1 - wy0); ux, uy = (wx1 - wx0) / WL, (wy1 - wy0) / WL
            for k, op in enumerate(e.get("openings", [])):  # formed openings (windows, doors) cut with booleans
                cut_ob = bc.oriented_box(f"{e['id']}_op{k}", (wx0 + ux * op["s"][0], wy0 + uy * op["s"][0]), (wx0 + ux * op["s"][1], wy0 + uy * op["s"][1]),
                                         e["size"][0] + 1.0, op["z"][0], op["z"][1], mat, coll)
                cut_ob.hide_render = True; cut_ob.hide_viewport = True
                md = ob.modifiers.new(f"op{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cut_ob
        elif e["type"] == "pad_footing":
            (x, y), (w, d) = e["at"], e["size"]; bc.box(e["id"], x - w / 2, y - d / 2, z0, x + w / 2, y + d / 2, z1, mat, coll)
        elif e["type"] == "anchor_field":  # one instanced bar per grid point
            bpy.ops.mesh.primitive_cylinder_add(radius=e["dia"] / 2, depth=z1 - z0, vertices=8, location=(0, 0, -1000))
            proto = bpy.context.object; proto.name = e["id"] + "_bar"; proto.data.materials.append(mat)
            for o in list(proto.users_collection):
                o.objects.unlink(proto)
            coll.objects.link(proto)
            pts = np.array(e["points"], float)
            holder = bc.mesh_from(e["id"], np.column_stack([pts, np.full(len(pts), (z0 + z1) / 2)]), np.zeros((0, 4), int), coll=coll)
            proto.parent = holder; proto.location = (0, 0, 0); holder.instance_type = "VERTS"
        elif e["type"] == "drain_pipe":
            p0, p1 = np.array(e["from"] + [z0]), np.array(e["to"] + [z0]); L = float(np.linalg.norm(p1 - p0))
            bpy.ops.mesh.primitive_cylinder_add(radius=e["dia"] / 2, depth=L, vertices=12, location=tuple((p0 + p1) / 2))
            o = bpy.context.object; o.name = e["id"]
            o.rotation_euler = (0, math.pi / 2, math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            o.data.materials.append(mat)
            for cc in list(o.users_collection):
                cc.objects.unlink(o)
            coll.objects.link(o)

# ---------------------------------------------------------------- cameras + save
CAMS = {
    "site_aerial": ((150, -170, 110), (0, 0, -8), 30),
    "ravine_upstream": ((4, -95, -3.5), (-2, 25, -2), 20),
    "site_top": ((5, 0, 300), (5, 0.01, 0), ("ORTHO", 150)),
    "pit_overview": ((-70, -85, 45), (-5, 0, -10), 26),
    "pit_east": ((80, 40, 30), (5, 5, -8), 26),
    "cofferdam": ((14, -50, 4), (-6, -10, -12), 22),
    "pit_floor": ((-26, 8, -3), (-12, -20, -16), 18),
}
for n, (loc, tgt, lens) in CAMS.items():
    bc.camera(scene, f"cam_{n}", loc, tgt, lens)
for o in bpy.data.objects:  # primitives + boolean results: flat shading for every hard-surface element
    if o.type == "MESH" and not o.name.startswith(("terrain", "river", "falls")):
        o.data.polygons.foreach_set("use_smooth", np.zeros(len(o.data.polygons), bool))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"stage_{STAGE}.blend"))
if RENDER:
    for n in (["site_aerial", "ravine_upstream", "site_top"] if STAGE == 0 else ["pit_overview", "pit_east", "cofferdam", "pit_floor", "site_top"]):
        scene.camera = bpy.data.objects[f"cam_{n}"]
        scene.render.filepath = str(OUT / f"stage_{STAGE}_{n}.png")
        bpy.ops.render.render(write_still=True)
print("stage", STAGE, "done")

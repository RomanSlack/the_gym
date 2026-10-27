"""The whole library in one room: every piece built from its model.py, on a stepped stage in a gallery hall.

    nice -n 19 blender -b --factory-startup -t 12 --python equipment/tools/showroom.py -- survey
        builds every piece, writes equipment/lineups/showroom_sizes.json (footprint, height, category); no render
    nice -n 19 blender -b --factory-startup -t 12 --python equipment/tools/showroom.py -- render [samples] [view ...]
        lays the pieces out from the sizes (small kit on the front plinths, then the floor, then steps rising to the
        rigs at the back), builds the stage and the hall, renders -> equipment/lineups/showroom_<view>_vNNN.jpg
        (never overwritten). GPU or nothing (exit 3).
Each piece is turned so its own "front" view faces the camera (-y). The PWR Play maze and mega are left out: they
repeat the PWR Play set.
"""
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

EQ = Path(__file__).resolve().parents[1]
OUT = EQ / "lineups"; OUT.mkdir(exist_ok=True)
SIZES = OUT / "showroom_sizes.json"
sys.path.insert(0, str(EQ / "blender"))
import kit  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
MODE = args[0]
SKIP = ("life-fitness-pwr-play-maze", "life-fitness-pwr-play-mega")


def categories():
    L = json.loads((EQ / "list.json").read_text())
    order = [c["name"] for c in L["categories"]]
    cat = {i["id"]: c["name"] for c in L["categories"] for i in c["items"]}
    out = {}
    for d in sorted((EQ / "pieces").iterdir()):
        if d.name in SKIP or not (d / "model.py").exists():
            continue
        items = json.loads((d / "piece.json").read_text()).get("items") or ["?"]
        out[d.name] = cat.get(items[0], "?")
    return out, order


def build(piece, sc):
    """Build a piece as the studio does, turned to face -y; returns its objects and world bounds."""
    spec = importlib.util.spec_from_file_location(f"pm_{piece}", EQ / "pieces" / piece / "model.py")
    pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
    coll = bpy.data.collections.new(piece); sc.collection.children.link(coll)
    k = kit.Kit(piece, coll, getattr(pm, "LOOK", None))
    k.check = lambda: None                              # each piece passed its own check
    pm.build(k)
    obs = k.finish()
    az = getattr(pm, "VIEWS", {}).get("front", (0,))[0]
    R = Matrix.Rotation(math.radians(-az), 4, "Z")
    for o in obs:
        o.matrix_world = R @ o.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(b) for o in obs if o.type == "MESH" for b in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return coll, obs, mn, mx


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
CAT, ORDER = categories()

if MODE == "survey":
    sizes = {}
    for i, piece in enumerate(CAT):
        coll, obs, mn, mx = build(piece, sc)
        sizes[piece] = dict(cat=CAT[piece], w=round(mx.x - mn.x, 3), d=round(mx.y - mn.y, 3), h=round(mx.z, 3),
                            z0=round(mn.z, 3), polys=sum(len(o.data.polygons) for o in obs if o.type == "MESH"))
        print(f"[{i + 1}/{len(CAT)}] {piece}: {sizes[piece]}", flush=True)
        for o in list(coll.all_objects):                # keep the session light
            bpy.data.objects.remove(o)
        bpy.data.collections.remove(coll)
        for m in list(bpy.data.meshes):
            if not m.users:
                bpy.data.meshes.remove(m)
    SIZES.write_text(json.dumps(sizes, indent=1))
    print("wrote", SIZES)
    os._exit(0)

# ---- render: the layout from the survey's sizes
S = json.loads(SIZES.read_text())
SAMPLES = int(args[1]) if len(args) > 1 and args[1].isdigit() else 256
VIEWS_ON = [a for a in args[1:] if not a.isdigit() and a not in ("draft", "plan")]
DRAFT = "draft" in args
W_ROW = 27.0                                            # a row's longest run of pieces
BASES = {                                               # a platform under its rack
    "rep-pr-5000-rack-builder": "titan-series-power-rack-lifting-platform",
    "rogue-monster-half-rack": "hammer-strength-impact-suppression-platform",
    "rogue-monster-lite-half-rack": "hammer-strength-rubber-platform",
}
WALL = {"rogue-climbing-ropes", "rogue-echo-gym-timer-2-0", "rogue-pine-maple-peg-board", "rogue-wood-gymnastics-rings",
        "metolius-wood-grips-campus-rungs", "beastmaker-2000-series-hangboard", "gymleco-wooden-wall-bars-with-chins-rack",
        "life-fitness-adjustable-wall-mounted-mat-rack", "rogue-belt-and-band-hanger", "rogue-wrist-roller",
        "mutant-metals-ultimate-dip-attachment", "rogue-monster-safety-spotter-arms-2-0", "rogue-monster-landmine-2-0",
        "rogue-monster-band-pegs-2-0"}
TIERS = ("plinth", "floor", "machines", "cardio", "back")   # front to back


def tier(p, v):
    if p in BASES.values():
        return None
    if v["h"] > 2.2 or p in BASES or p in WALL:
        return "back"
    if v["cat"] == "Cardio" or p == "fit3d-proscanner":
        return "cardio"
    if v["cat"].startswith("Machines") or v["cat"] == "Cable stations":
        return "machines"
    if v["h"] < 0.5 and max(v["w"], v["d"]) < 2.6 and v["d"] < 1.6:
        return "plinth"
    return "floor"


def turned(p):
    """Long runs laid along y (a fan of fixed barbells) turned across, so a row stays shallow."""
    v = S[p]
    return v["d"] > 2.7 and v["d"] > v["w"]


def foot(p):
    v = S[BASES[p]] if p in BASES else S[p]
    w, d = max(v["w"], S[p]["w"]), max(v["d"], S[p]["d"])
    return (d, w) if turned(p) else (w, d)


rank = {c: i for i, c in enumerate(ORDER)}
GAP = {"plinth": 0.22, "floor": 0.4, "machines": 0.45, "cardio": 0.45, "back": 0.5}
DEEP = {"plinth": 1.5, "floor": 2.4, "machines": 2.7, "cardio": 2.4, "back": 2.2}   # a row's depth for its columns
RISE = {"plinth": 0.20, "floor": 0.28, "machines": 0.32, "cardio": 0.35, "back": 0.40}


def columns(ps, t):
    """Pack a category's pieces into columns: pieces of about the same width stacked front to back while they fit the
    row's depth (the bars lie side by side, the small kit two or three deep)."""
    cols = []
    for p in sorted(ps, key=lambda p: -foot(p)[0]):
        w, d = foot(p)
        for c in cols:
            if c["d"] + GAP[t] + d <= DEEP[t] and w <= c["w"] * 1.05 and w >= c["w"] * 0.45:
                c["ps"].append(p); c["d"] += GAP[t] + d
                break
        else:
            cols.append(dict(ps=[p], w=w, d=d))
    return sorted(cols, key=lambda c: -max(S[p]["h"] for p in c["ps"]))


rows = []                                               # [(tier, [columns])], front to back
for t in TIERS:
    ps = [p for p in S if p in CAT and tier(p, S[p]) == t]
    cols = []
    for cat in sorted({S[p]["cat"] for p in ps}, key=lambda c: rank.get(c, 99)):
        cols += columns([p for p in ps if S[p]["cat"] == cat], t)
    total = sum(c["w"] + GAP[t] for c in cols)
    n = max(1, math.ceil(total / W_ROW)); per = total / n
    row, run, k = [], 0.0, 1
    for c in cols:
        if run + c["w"] / 2 > per and row and k < n:
            k += 1
            rows.append((t, row)); row, run = [], 0.0
        row.append(c); run += c["w"] + GAP[t]
    rows.append((t, row))

plan, y, z = [], 0.0, 0.0
for t, row in rows:
    z += RISE[t]
    d = max(c["d"] for c in row) + (0.45 if t == "plinth" else 0.7)
    width = sum(c["w"] for c in row) + GAP[t] * (len(row) - 1)
    plan.append(dict(tier=t, y0=y, y1=y + d, z=z, width=width, cols=row, gap=GAP[t]))
    y += d
print("rows:", [(r["tier"], sum(len(c["ps"]) for c in r["cols"]), round(r["width"], 1), round(r["y1"] - r["y0"], 1),
                 round(r["z"], 2)) for r in plan], flush=True)
if "plan" in args:
    os._exit(0)
STAGE_W = max(r["width"] for r in plan) + 3.0
DEPTH = plan[-1]["y1"]

# ---- the GPU or nothing
sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.tile_size = 512
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
sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 3200, 1800
sc.render.resolution_percentage = 40 if DRAFT else 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92

# ---- the pieces
def place(p, cx, cy, cz):
    stack = [(BASES[p], 0.0), (p, S[BASES[p]]["h"])] if p in BASES else [(p, 0.0)]
    for q, dz in stack:
        coll, obs, mn, mx = build(q, sc)
        M = Matrix.Rotation(math.radians(90), 4, "Z") if turned(q) else Matrix.Identity(4)
        c = M @ Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, 0))
        M = Matrix.Translation(Vector((cx, cy, cz + dz)) - c) @ M
        for o in obs:
            if o.parent is None:
                o.matrix_world = M @ o.matrix_world
    print("placed", p, flush=True)


for r in plan:
    x = -r["width"] / 2
    for c in r["cols"]:
        yy = (r["y0"] + r["y1"]) / 2 - c["d"] / 2      # the column centred on the tread
        for p in c["ps"]:
            fd = foot(p)[1]
            place(p, x + c["w"] / 2, yy + fd / 2, r["z"])
            yy += fd + r["gap"]
        x += c["w"] + r["gap"]


# ---- the stage and the hall
def mat(name, color, rough, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    for key, val in kw.items():
        b.inputs[key].default_value = val
    return m, b


def concrete():
    """Pale microcement: a light warm grey with a faint cloudy mottle, satin."""
    m, b = mat("concrete", (0.52, 0.52, 0.50), 0.55)
    nt = m.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.44, 0.44, 0.43, 1); ramp.color_ramp.elements[1].color = (0.56, 0.56, 0.54, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def box(name, c, s, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object; o.name = name; o.scale = s
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.006; bv.segments = 2
    return o


TREAD = concrete()
RISER, _ = mat("riser", (0.22, 0.22, 0.215), 0.6)
NOSE, _ = mat("nosing", (0.02, 0.02, 0.022), 0.35, **{"Metallic": 1.0})
FLOOR, _ = mat("floor", (0.16, 0.16, 0.16), 0.3)
WALLM, _ = mat("wall", (0.30, 0.29, 0.27), 0.85)
LED, led = mat("led", (1, 1, 1), 0.5)
led.inputs["Emission Color"].default_value = (1.0, 0.85, 0.65, 1); led.inputs["Emission Strength"].default_value = 6.0
T = 0.04                                                 # the tread's thickness
for i, r in enumerate(plan):
    box(f"riser_{i}", (0, (r["y0"] + DEPTH + 1.0) / 2, (r["z"] - T) / 2), (STAGE_W, DEPTH + 1.0 - r["y0"], r["z"] - T), RISER)
    box(f"tread_{i}", (0, (r["y0"] - 0.03 + DEPTH + 1.0) / 2, r["z"] - T / 2), (STAGE_W, DEPTH + 1.03 - r["y0"], T), TREAD)
    box(f"nose_{i}", (0, r["y0"] - 0.03, r["z"] - T / 2), (STAGE_W + 0.004, 0.012, T + 0.004), NOSE)         # steel edge
    box(f"led_{i}", (0, r["y0"] - 0.012, r["z"] - T - 0.012), (STAGE_W - 0.02, 0.015, 0.012), LED)   # under the nosing
box("floor", (0, DEPTH / 2, -0.05), (STAGE_W + 40, DEPTH + 60, 0.1), FLOOR)
box("back_wall", (0, DEPTH + 1.2, 6), (STAGE_W + 40, 0.4, 12), WALLM)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.15
C = Vector((0, DEPTH * 0.55, 1.5))


def area(name, loc, energy, size, target=C):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA")); L.data.energy = energy
    L.data.shape = "RECTANGLE"; L.data.size, L.data.size_y = size
    L.location = loc; L.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(L)


area("sky", (0, DEPTH * 0.5, 14), 9000, (STAGE_W, DEPTH), Vector((0, DEPTH * 0.5, 0)))   # the skylight over the stage
area("key", (-STAGE_W * 0.45, -14, 12), 9000, (10, 10))
area("fill", (STAGE_W * 0.5, -10, 6), 2500, (12, 8))
area("rim", (0, DEPTH + 0.5, 11), 5000, (STAGE_W, 2), Vector((0, DEPTH * 0.4, 0)))

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.clip_end = 400
# name: (eye, target, lens mm)
def mid(i, j):
    """The middle of rows i..j (y, z)."""
    return (plan[i]["y0"] + plan[j]["y1"]) / 2, (plan[i]["z"] + plan[j]["z"]) / 2


VIEWS = {
    "hero": ((-STAGE_W * 0.50, -DEPTH * 0.50, 13.0), (0, DEPTH * 0.40, 1.0), 30),
    "front": ((0, -DEPTH * 0.68, 9.5), (0, DEPTH * 0.42, 1.4), 30),
    "high": ((STAGE_W * 0.42, -DEPTH * 0.55, 25.0), (0, DEPTH * 0.45, 0.5), 26),
}
TIER_ROWS = {}
for i, r in enumerate(plan):
    TIER_ROWS.setdefault(r["tier"], []).append(i)
for t, ix in TIER_ROWS.items():                         # a close-up of each tier, from the front and a little left
    yc, zc = mid(ix[0], ix[-1])
    span = max(plan[i]["width"] for i in ix)
    VIEWS[f"close_{t}"] = ((-span * 0.14, plan[ix[0]]["y0"] - span * 0.45, zc + span * 0.24), (0, yc, zc + 0.4), 30)


def nextv(view):
    vs = [int(m.group(1)) for f in OUT.glob(f"showroom_{view}_v*.jpg") if (m := re.search(r"_v(\d{3})\.jpg$", f.name))]
    return OUT / f"showroom_{view}_v{max(vs, default=0) + 1:03d}.jpg"


for view, (eye, target, lens) in VIEWS.items():
    if VIEWS_ON and view not in VIEWS_ON:
        continue
    cam.location = eye; cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(nextv(view))
    bpy.ops.render.render(write_still=True)
    print("view:", sc.render.filepath, flush=True)

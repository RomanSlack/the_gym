"""Construction scene, built stage by stage from the model (see CONSTRUCTION_PLAN.md).

blender -b --factory-startup --python construction/scene.py -- <stage> [render]
  stage 0: site, the land before any works (no trees, no building)
  stage 1: + foundations (construction pit, cofferdam, anchors, footings, rafts, retaining walls, waterproofing, drainage)
  stage 3: + structure (PT concrete floors, glulam + CLT roofs with eaves, lounge girders, cores, stairs)
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
    pit = np.load(ROOT / "construction" / "out" / "pit_1m.npy")  # written by tools/foundations.py
    ew = np.load(ROOT / "construction" / "out" / "earthworks_1m.npy")  # cut / fill: road, garden, ledge, sauna pad (tools/foundations.py)
    H = np.minimum(natural + ew, pit)
    cut = (H < natural - 0.05).astype(np.float32)
if STAGE >= 4:  # backfilled against the walls + final grading: the finished site terrain, river back in its bed
    H = np.load(RV / "eroded_1m.npy"); rock = np.load(RV / "rock_1m.npy"); cut = np.zeros_like(H)
    # backfilled terrain + the enclosed volumes cut out of it (written by tools/envelope.py)
    H = np.load(OUT / "finished_1m.npy")
    VOIDS = json.loads((OUT / "voids.json").read_text())

site0 = bc.collection("0 · site")
if STAGE >= 4:  # a local patch round the building gets the volumes cut out exactly; the rest stays one plain grid
    Hc, Rc, Cc = H[c], rock[c], cut[c]
    r0, r1, c0, c1 = -50 - DY0, 50 - DY0, -50 - DX0, 70 - DX0  # patch rows / cols in the cropped grid
    keep = np.ones((Hc.shape[0] - 1, Hc.shape[1] - 1), bool); keep[r0:r1, c0:c1] = False
    terr = bc.grid_mesh("terrain_detail", Hc, DX0 + 0.5, DY0 + 0.5, 1.0, {"rock": Rc, "cut": Cc}, coll=site0, keep=keep)
    terr.data.materials.append(bc.terrain_material())
    patch = bc.grid_mesh("terrain_building", Hc[r0:r1 + 1, c0:c1 + 1], DX0 + 0.5 + c0, DY0 + 0.5 + r0, 1.0,
                         {"rock": Rc[r0:r1 + 1, c0:c1 + 1], "cut": Cc[r0:r1 + 1, c0:c1 + 1]}, coll=site0)
    patch.data.materials.append(bpy.data.materials["terrain"])
    vs, fs = [], []
    for (x0_, y0_, x1_, y1_), zb, zt in VOIDS:
        b = len(vs)
        vs += [(x0_, y0_, zb), (x1_, y0_, zb), (x1_, y1_, zb), (x0_, y1_, zb), (x0_, y0_, zt), (x1_, y0_, zt), (x1_, y1_, zt), (x0_, y1_, zt)]
        fs += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]
    voids = bc.mesh_from("building_voids", vs, fs, smooth=False, coll=site0); voids.hide_render = True; voids.hide_viewport = True
    md = patch.modifiers.new("voids", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = voids; md.solver = "EXACT"
    for attr in ("use_hole_tolerant", "use_self"):  # open terrain patch, overlapping cutter boxes
        try:
            setattr(md, attr, True)
        except AttributeError:
            pass
else:
    terr = bc.grid_mesh("terrain_detail", H[c], DX0 + 0.5, DY0 + 0.5, 1.0, {"rock": rock[c], "cut": cut[c]}, coll=site0)
    terr.data.materials.append(bc.terrain_material())
ctx = np.load(SITE / "context_4m.npy") - DATUM
g4 = lambda w: (w + 4000) // 4
ctx[750:1250, 750:1250] = natural.reshape(500, 4, 500, 4).mean((1, 3))
ctx[g4(DY0) + 2:g4(DY1) - 2, g4(DX0) + 2:g4(DX1) - 2] -= 60
far = bc.grid_mesh("terrain_context", ctx[::2, ::2], -4000 + 2, -4000 + 2, 8.0, {"rock": np.zeros(ctx[::2, ::2].shape), "cut": np.zeros(ctx[::2, ::2].shape)}, coll=site0)
far.data.materials.append(bpy.data.materials["terrain"])

W = np.load(RV / "water_1m.npy")
if 1 <= STAGE < 4 and (OUT / "dewatered_1m.npy").exists():
    W = np.where(np.load(OUT / "dewatered_1m.npy") > 0, np.nan, W)  # inside the cofferdam the river is pumped dry
bc.water_mesh("river", W[c], DX0 + 0.5, DY0 + 0.5, 1.0, coll=site0)

# natural cliffs (only where the ravine was already rock, not on excavation faces)
busy = cut[c] > 0
if STAGE >= 4:  # keep natural rock blocks off the building, site works and graded ground
    fm_ = np.load(RV / "features_1m.npy")[c] > 0
    busy = fm_ | (np.abs(H - natural)[c] > 0.5)
for _ in range(5):  # keep natural rock blocks clear of the excavation and the new walls
    busy = busy | np.roll(busy, 1, 0) | np.roll(busy, -1, 0) | np.roll(busy, 1, 1) | np.roll(busy, -1, 1)
bc.cliff_rocks((H if STAGE >= 4 else natural)[c], rock[c], DX0, DY0, exclude=busy, rng=rng, coll=site0)

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
    "glulam": bc.material("glulam", (0.55, 0.36, 0.2), 0.6),
    "clt": bc.material("clt", (0.62, 0.45, 0.28), 0.65),
    "timber": bc.material("clt", (0.62, 0.45, 0.28), 0.65),
    "steel_dark": bc.material("steel_dark", (0.03, 0.03, 0.032), 0.45, metal=0.7),
    "precast": bc.material("precast", (0.56, 0.55, 0.52), 0.8),
    "oak": bc.material("oak", (0.42, 0.28, 0.15), 0.5),
    "timber_clad": bc.material("tarred_timber", (0.022, 0.02, 0.018), 0.75),
    "stone": bc.material("granite_plinth", (0.075, 0.073, 0.07), 0.9),
    "glass": bc.material("glass", (0.05, 0.07, 0.08), 0.05, alpha=0.28),
    "glass_obscured": bc.material("glass_obscured", (0.55, 0.58, 0.6), 0.35, alpha=0.75),
    "acrylic": bc.material("acrylic", (0.05, 0.08, 0.09), 0.03, alpha=0.2),
    "sod": bc.material("sod", (0.07, 0.11, 0.035), 0.95),
    "frame": bc.material("window_frame", (0.025, 0.025, 0.027), 0.4, metal=0.6),
}
PHASES = {1: "1 · foundations", 3: "3 · structure", 4: "4 · envelope"}
for ph in range(1, STAGE + 1):
    if ph not in PHASES:
        continue  # stage 2 (style) adds no elements
    coll = bc.collection(PHASES[ph])
    for e in sorted((e for e in model["elements"] if e.get("phase") == ph), key=lambda e: e.get("seq", 0)):
        if e.get("temporary") and STAGE >= 4:
            continue  # the cofferdam is pulled once the river wall is closed
        mat = MAT.get(e["material"], MAT["concrete"])
        if STAGE >= 4 and e.get("finish") == "black_stain":
            mat = MAT["timber_clad"]
        z0, z1 = e["z"]
        if e["type"] in ("slab", "footing", "blinding") and "rect" in e:
            x0, y0, x1, y1 = e["rect"]
            W_, S_, E_, N_ = e.get("eaves", (0, 0, 0, 0))  # roofs: plate runs past the facade
            ob = bc.box(e["id"], x0 - W_, y0 - S_, z0, x1 + E_, y1 + N_, z1, mat, coll)
            for k, h in enumerate(e.get("holes", [])):
                if "rect" in h:  # e.g. the pool basin through the F4 raft
                    xs_, ys_ = [p[0] for p in h["rect"]], [p[1] for p in h["rect"]]
                    cu = bc.box(f"{e['id']}_hole{k}", min(xs_), min(ys_), z0 - 0.5, max(xs_), max(ys_), z1 + 0.5, mat, coll)
                    cu.hide_render = True; cu.hide_viewport = True
                    md = ob.modifiers.new(f"hole{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cu
        elif e["type"] in ("wall", "sheetpile", "membrane", "drain_layer", "strip_footing") and "mullions" not in e and e.get("kind") != "clad":
            ob = bc.oriented_box(e["id"], e["from"], e["to"], e["size"][0], z0, z1, mat, coll)
            (wx0, wy0), (wx1, wy1) = e["from"], e["to"]
            WL = math.hypot(wx1 - wx0, wy1 - wy0); ux, uy = (wx1 - wx0) / WL, (wy1 - wy0) / WL
            for k, op in enumerate(e.get("openings", [])):  # formed openings (windows, doors) cut with booleans
                cut_ob = bc.oriented_box(f"{e['id']}_op{k}", (wx0 + ux * op["s"][0], wy0 + uy * op["s"][0]), (wx0 + ux * op["s"][1], wy0 + uy * op["s"][1]),
                                         e["size"][0] + 1.0, op["z"][0], op["z"][1], mat, coll)
                cut_ob.hide_render = True; cut_ob.hide_viewport = True
                md = ob.modifiers.new(f"op{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cut_ob
        elif e["type"] == "wall" and "mullions" in e:  # divided glazing: glass + dark frames, mullions, transoms
            (wx0, wy0), (wx1, wy1) = e["from"], e["to"]; WL = math.hypot(wx1 - wx0, wy1 - wy0); ux, uy = (wx1 - wx0) / WL, (wy1 - wy0) / WL
            P = lambda s_: (wx0 + ux * s_, wy0 + uy * s_)
            bc.oriented_box(e["id"], e["from"], e["to"], 0.03, z0, z1, mat, coll)
            fw, fd = 0.07, max(0.12, e["size"][0])
            for k, s_ in enumerate([0.0] + e["mullions"] + [WL]):
                a_, b_ = max(0.0, s_ - fw / 2), min(WL, s_ + fw / 2)
                bc.oriented_box(f"{e['id']}_m{k}", P(a_), P(b_), fd, z0, z1, MAT["frame"], coll)
            for k, zt in enumerate([z0, z1 - fw] + e.get("transoms", [])):
                bc.oriented_box(f"{e['id']}_t{k}", e["from"], e["to"], fd, zt, zt + fw, MAT["frame"], coll)
        elif e["type"] == "wall" and e.get("kind") == "clad":  # black board-on-board: the wall + a top board every 0.3 m (real geometry, arrayed)
            ob = bc.oriented_box(e["id"], e["from"], e["to"], e["size"][0], z0, z1, mat, coll)
            (wx0, wy0), (wx1, wy1) = e["from"], e["to"]; WL = math.hypot(wx1 - wx0, wy1 - wy0); ux, uy = (wx1 - wx0) / WL, (wy1 - wy0) / WL
            mx_, my_ = (wx0 + wx1) / 2, (wy0 + wy1) / 2
            cx_, cy_ = min(((-17.95, -11.0), (21.25, 11.9)), key=lambda c_: math.hypot(c_[0] - mx_, c_[1] - my_))
            out_side = 1 if ((-uy) * (mx_ - cx_) + ux * (my_ - cy_)) > 0 else -1  # boards on the outside face only
            for side in (out_side,):
                nx_, ny_ = -uy * side * (e["size"][0] / 2 + 0.011), ux * side * (e["size"][0] / 2 + 0.011)
                bd = bc.oriented_box(f"{e['id']}_boards{side}", (wx0 + nx_, wy0 + ny_), (wx0 + nx_ + ux * 0.1, wy0 + ny_ + uy * 0.1), 0.022, z0, z1, mat, coll)
                arr = bd.modifiers.new("boards", "ARRAY"); arr.use_relative_offset = False; arr.use_constant_offset = True
                arr.constant_offset_displace = (ux * 0.3, uy * 0.3, 0); arr.count = max(1, int(WL / 0.3))
            if e.get("openings"):
                for k, op in enumerate(e["openings"]):
                    cut_ob = bc.oriented_box(f"{e['id']}_op{k}", (wx0 + ux * op["s"][0], wy0 + uy * op["s"][0]), (wx0 + ux * op["s"][1], wy0 + uy * op["s"][1]),
                                             e["size"][0] + 1.0, op["z"][0], op["z"][1], mat, coll)
                    cut_ob.hide_render = True; cut_ob.hide_viewport = True
                    md = ob.modifiers.new(f"op{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cut_ob
        elif e["type"] == "column":
            (x, y), (w, d) = e["at"], e["size"]; bc.box(e["id"], x - w / 2, y - d / 2, z0, x + w / 2, y + d / 2, z1, mat, coll)
        elif e["type"] == "beam":
            (bx0, by0), (bx1, by1) = e["from"], e["to"]; L = math.hypot(bx1 - bx0, by1 - by0); d = z1 - z0
            c0, c1 = e.get("cantilever", (0, 0)); tip = e.get("tip_depth", d)
            if "cantilever" in e:  # tapered tails past both supports, top stays flat
                prof = [(-c0, z1), (L + c1, z1), (L + c1, z1 - (tip if c1 else d)), (L, z0), (0, z0), (-c0, z1 - (tip if c0 else d))]
            else:  # tapers root -> tip (outriggers)
                prof = [(0, z1), (L, z1), (L, z1 - tip), (0, z0)]
            bc.extrude_profile(e["id"], e["from"], e["to"], e["size"][0], prof, mat, coll)
        elif e["type"] == "stair_flight":
            (fx0, fy0), (fx1, fy1) = e["from"], e["to"]; L = math.hypot(fx1 - fx0, fy1 - fy0)
            n = e["risers"]; r = (z1 - z0) / n; g = L / (n - 1); wv = e["size"][1] * 1.3
            prof = [(0, z0)]
            for k in range(n):
                prof += [(k * g, z0 + (k + 1) * r), ((k + 1) * g if k < n - 1 else L, z0 + (k + 1) * r)]
            prof = prof[:-1] + [(L, z1 - wv), (0, z0 + r - wv)]
            bc.extrude_profile(e["id"], e["from"], e["to"], e["size"][0], prof, mat, coll)
        elif e["type"] == "spiral_stair":  # open helix: inner + outer steel stringers, oak treads, no centre post
            (cx, cy), (ri, ro) = e["center"], e["r"]; n = e["risers"]; r = (z1 - z0) / n; da = e["step_deg"]; a0 = e["a0"]
            for k, rr in (("in", ri), ("out", ro)):
                bc.helix_plate(f"{e['id']}_stringer_{k}", (cx, cy), rr, 0.025, 0.36, a0, a0 + da * n, z0 + r - 0.06, z1 - 0.06, mat, coll)
            for k in range(n):
                aa, ab = math.radians(a0 + da * k - 1), math.radians(a0 + da * (k + 1) + 1)
                pts = [(cx + rad * math.cos(t), cy + rad * math.sin(t)) for rad, t in ((ri, aa), (ro, aa), (ro, (aa + ab) / 2), (ro, ab), (ri, ab))]
                bc.poly_slab(f"{e['id']}_t{k}", pts, z0 + r * (k + 1) - 0.06, z0 + r * (k + 1), MAT["oak"], coll)
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
    "frame_overview": ((-85, -95, 42), (-2, -2, -4), 26),
    "frame_east": ((75, 45, 22), (2, -4, -3), 24),
    "frame_gorge": ((3, -62, -6), (1, -5, -2), 22),
    "roof_eaves": ((-48, -52, 9), (-28, -32, 4), 24),
    "lounge_deck": ((3, -24, 1.7), (3, 2, 3.2), 18),
    "hall_f1": ((-9, -32, 1.7), (-24, 8, 3.8), 16),
    "spiral": ((-12.5, -22, -8.0), (-17.95, -14.85, -4.5), 16),
    "daycare_garden": ((46, 82, 24), (22, 38, -5), 26),
    "style_gorge": ((3, -88, -1.0), (-1, 0, -1.5), 24),      # compare docs/style/bdarksod_gorge.jpg
    "style_aerial": ((95, -120, 70), (2, 2, -6), 30),        # compare bdarksod_aerial.jpg
    "style_arrival": ((60, -24, 2.0), (22, 4, 2.8), 22),     # compare bdarksod_arrival.jpg
    "west_garden": ((-62, -40, 4), (-26, -10, 2), 22),
    "garden_close": ((26, 45, -4.4), (23, 33.3, -2.4), 22),
    "stair_f3_f4": ((-13.0, 1.5, -13.7), (-18.5, 10.5, -12.3), 18),
    "towers_west": ((-46, -14, 3), (-30, -14, 0.5), 30),
    "river_window_f3": ((-9.0, -32.5, -8.2), (-9.0, 8, -8.6), 16),
}
for n, (loc, tgt, lens) in CAMS.items():
    bc.camera(scene, f"cam_{n}", loc, tgt, lens)
for o in bpy.data.objects:  # primitives + boolean results: flat shading for every hard-surface element
    if o.type == "MESH" and not o.name.startswith(("terrain", "river", "falls")):
        o.data.polygons.foreach_set("use_smooth", np.zeros(len(o.data.polygons), bool))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"stage_{STAGE}.blend"))
if RENDER:
    shots = {0: ["site_aerial", "ravine_upstream", "site_top"], 1: ["pit_overview", "pit_east", "cofferdam", "pit_floor", "daycare_garden", "site_top"],
             3: ["frame_overview", "frame_east", "frame_gorge", "roof_eaves", "lounge_deck", "hall_f1", "spiral", "daycare_garden", "site_top"],
             4: ["style_gorge", "style_aerial", "style_arrival", "west_garden", "frame_east", "roof_eaves", "lounge_deck", "daycare_garden", "garden_close", "hall_f1", "river_window_f3", "stair_f3_f4", "towers_west"]}
    for n in shots[max(k for k in shots if k <= STAGE)]:
        scene.camera = bpy.data.objects[f"cam_{n}"]
        scene.render.filepath = str(OUT / f"stage_{STAGE}_{n}.png")
        bpy.ops.render.render(write_still=True)
print("stage", STAGE, "done")

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
if STAGE >= 4:  # forest + glass: Cycles on the GPU, short tiles so the desktop stays responsive
    scene.render.engine = "CYCLES"; scene.cycles.device = "GPU"; scene.cycles.tile_size = 256
    scene.cycles.samples = 128 if STAGE >= 5 else 64; scene.cycles.use_denoising = True
    _pr = bpy.context.preferences.addons["cycles"].preferences
    for _dev in ("OPTIX", "CUDA"):
        try:
            _pr.compute_device_type = _dev; _pr.get_devices()
            for _d in _pr.devices:
                _d.use = True
            break
        except Exception:
            continue
ONLY = next((a_.split(":", 1)[1].split(",") for a_ in args if a_.startswith("only:")), None)  # e.g. only:style_gorge,style_aerial

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
    import ground  # noqa: E402  (construction/ground.py)
    Hc, Rc, Cc = H[c], rock[c], cut[c]
    GM = ground.ground_masks(Hc.shape, c, ROOT / "model" / "forest_sr16.npz", np.load(RV / "features_1m.npy").astype(int), rock, np.load(RV / "water_1m.npy"))
    GM["cut"] = Cc
    r0, r1, c0, c1 = -50 - DY0, 50 - DY0, -50 - DX0, 70 - DX0  # patch rows / cols in the cropped grid
    keep = np.ones((Hc.shape[0] - 1, Hc.shape[1] - 1), bool); keep[r0:r1, c0:c1] = False
    terr = bc.grid_mesh("terrain_detail", Hc, DX0 + 0.5, DY0 + 0.5, 1.0, GM, coll=site0, keep=keep)
    bc.terrain_material()  # still used by the far context ring
    TM = ground.terrain_material_v2()
    terr.data.materials.append(TM)
    patch = bc.grid_mesh("terrain_building", Hc[r0:r1 + 1, c0:c1 + 1], DX0 + 0.5 + c0, DY0 + 0.5 + r0, 1.0,
                         {k: v[r0:r1 + 1, c0:c1 + 1] for k, v in GM.items()}, coll=site0)
    patch.data.materials.append(TM)
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
if STAGE >= 4:  # no natural rock inside or right against the building (enclosed volumes + 3 m)
    for (x0_, y0_, x1_, y1_), _zb, _zt in VOIDS:
        busy[max(0, int(y0_ - 3 - DY0)):max(0, int(y1_ + 3 - DY0)), max(0, int(x0_ - 3 - DX0)):max(0, int(x1_ + 3 - DX0))] = True
Hn_ = (H if STAGE >= 4 else natural)[c]
bc.cliff_face(Hn_, rock[c], DX0, DY0, exclude=busy, coll=site0)       # jointed granite skin on the ravine walls
bc.fallen_blocks(Hn_, rock[c], DX0, DY0, exclude=busy, rng=rng, coll=site0)  # a few big angular blocks at the toes

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
    "steel_dark": bc.blackened_steel(),
    "precast": bc.material("precast", (0.56, 0.55, 0.52), 0.8),
    "oak": bc.material("oak", (0.42, 0.28, 0.15), 0.5),
    "timber_clad": bc.stained_timber("tarred_timber"),
    "stone": bc.material("granite_plinth", (0.075, 0.073, 0.07), 0.9),
    "glass": bc.material("glass", (0.05, 0.07, 0.08), 0.05, alpha=0.28),
    "glass_obscured": bc.material("glass_obscured", (0.55, 0.58, 0.6), 0.35, alpha=0.75),
    "acrylic": bc.material("acrylic", (0.05, 0.08, 0.09), 0.03, alpha=0.2),
    "sod": bc.material("sod", (0.07, 0.11, 0.035), 0.95),
    "frame": bc.blackened_steel(),  # option D (Roman): blackened, waxed steel frames
}
PHASES = {1: "1 · foundations", 3: "3 · structure", 4: "4 · envelope", 5: "5 · interior shell"}
if STAGE >= 4:  # Cycles: real architectural glass (daylight comes through)
    MAT["glass"] = bc.arch_glass("arch_glass"); MAT["glass_obscured"] = bc.arch_glass("arch_glass_obscured", rough=0.25, frosted=True)
    MAT["acrylic"] = bc.arch_glass("arch_acrylic", tint=(0.9, 0.95, 0.94))
if STAGE >= 5:  # interiors are seen up close: scanned finishes, textured timber structure
    MAT.update(bc.interior_materials()); MAT["glass_partition"] = MAT["glass"]
    MAT["glulam"] = bc.pbr_material("glulam_spruce", "coated_pine_02", 1.05, box=True, piece_var=0.05, sat=0.45, val=1.45)  # pale spruce
    MAT["clt"] = MAT["clt_natural"]
    ROOF_BEAMS_E = sorted({e["from"][1] for e in model["elements"] if e["type"] == "beam" and e["id"].endswith("-RF-east")})
    prng = np.random.default_rng(55)
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
        if "pattern" in e and e["type"] == "slab" and e["pattern"]["kind"] in ("boards", "slabs", "poured"):
            bc.pattern_floor(e, mat, coll, prng)
        elif "pattern" in e and e["type"] == "slab" and e["pattern"]["kind"] == "wave":
            bc.pattern_wave_ceiling(e, mat, coll, ROOF_BEAMS_E)
        elif "pattern" in e and e["type"] == "slab" and e["pattern"]["kind"] == "slats":
            bc.pattern_ceiling(e, mat, coll, ROOF_BEAMS_E)
        elif e["type"] == "wall" and e.get("kind") == "lining":
            bc.pattern_lining(e, mat, coll, prng, backing_mat=MAT["felt_black"])
        elif e["type"] in ("slab", "footing", "blinding") and "rect" in e:
            x0, y0, x1, y1 = e["rect"]
            W_, S_, E_, N_ = e.get("eaves", (0, 0, 0, 0))  # roofs: plate runs past the facade
            ob = bc.box(e["id"], x0 - W_, y0 - S_, z0, x1 + E_, y1 + N_, z1, mat, coll)
            for k, h in enumerate(e.get("holes", [])):
                if "rect" in h:  # e.g. the pool basin through the F4 raft
                    xs_, ys_ = [p[0] for p in h["rect"]], [p[1] for p in h["rect"]]
                    cu = bc.box(f"{e['id']}_hole{k}", min(xs_), min(ys_), z0 - 0.5, max(xs_), max(ys_), z1 + 0.5, mat, coll)
                    cu.hide_render = True; cu.hide_viewport = True
                    md = ob.modifiers.new(f"hole{k}", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cu
        elif e["type"] in ("wall", "sheetpile", "membrane", "drain_layer", "strip_footing") and "mullions" not in e and e.get("kind") not in ("clad", "lining"):
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
            ops_ = [o for o in e.get("openings", []) if o["type"] in ("door", "opening")]
            cuts_ = sorted({0.0, WL, *[v for o in ops_ for v in o["s"]]})
            fw, fd = 0.07, max(0.12, e["size"][0])
            for k, (sa, sb) in enumerate(zip(cuts_, cuts_[1:])):  # glass, minus door openings (glass continues above them)
                o_ = next((o for o in ops_ if o["s"][0] <= (sa + sb) / 2 <= o["s"][1]), None)
                za = z0 if o_ is None else o_["z"][1]
                if z1 - za > 0.05:
                    bc.oriented_box(f"{e['id']}_g{k}", P(sa), P(sb), 0.03, za, z1, mat, coll)
                for zt in [z0, z1 - fw] + e.get("transoms", []):
                    if o_ is None or zt >= o_["z"][1] - 0.01:
                        bc.oriented_box(f"{e['id']}_t{k}_{zt:.2f}", P(sa), P(sb), fd, zt, zt + fw, MAT["frame"], coll)
                if o_ is not None:  # door head
                    bc.oriented_box(f"{e['id']}_head{k}", P(sa), P(sb), fd, o_["z"][1], o_["z"][1] + fw, MAT["frame"], coll)
            for k, s_ in enumerate([0.0] + e["mullions"] + [WL]):
                a_, b_ = max(0.0, s_ - fw / 2), min(WL, s_ + fw / 2)
                if any(o["s"][0] + 0.01 < s_ < o["s"][1] - 0.01 for o in ops_):
                    continue
                bc.oriented_box(f"{e['id']}_m{k}", P(a_), P(b_), fd, z0, z1, MAT["frame"], coll)
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

# ---------------------------------------------------------------- furniture, fixtures, doors (stage 5: reception + cafe first)
if STAGE >= 5 and model.get("furnishings"):
    import furniture  # noqa: E402  (construction/furniture.py)
    print("furnishings:", furniture.build_all(model, MAT, bc.collection("5b · furniture + fixtures")))

# ---------------------------------------------------------------- grass (stage 4+): sod roofs, lawns, the meadow (reduced density for now)
if STAGE >= 4:
    gcoll = bc.collection("6 · grass")
    protos_meadow = [ground.grass_proto("tuft_meadow", "meadow", gcoll), ground.grass_proto("tuft_dry", "dry", gcoll)]
    protos_lawn = [ground.grass_proto("tuft_lawn", "lawn", gcoll), ground.grass_proto("tuft_meadow2", "meadow", gcoll)]
    ng_roof = ground.grass_nodes("GN_grass_roof", protos_meadow, density=45, seed=1)
    for o in [o for o in bpy.data.objects if o.name.startswith("EN-sod-") or o.name == "RF-W3-sod"]:
        md_ = o.modifiers.new("grass", "NODES"); md_.node_group = ng_roof
    # lawns + meadow + garden beds: a distribution surface from the terrain cells flagged lawn
    lm = GM["lawn"].copy()
    for f_ in model.get("furnishings", []):  # no grass through the porch floor
        if f_["kind"] == "porch_floor":
            (px_, py_), (sx_, sy_) = f_["at"], f_["size"]
            lm[max(0, int(py_ - sy_ / 2 - 1 - DY0)):int(py_ + sy_ / 2 + 1 - DY0), max(0, int(px_ - sx_ / 2 - 1 - DX0)):int(px_ + sx_ / 2 + 1 - DX0)] = 0
    ii, jj = np.nonzero(lm[:-1, :-1] * lm[1:, :-1] * lm[:-1, 1:] * lm[1:, 1:] > 0)
    if len(ii):
        vv, ff = [], []
        for k_, (i_, j_) in enumerate(zip(ii, jj)):
            x_, y_ = DX0 + 0.5 + j_, DY0 + 0.5 + i_
            vv += [(x_, y_, Hc[i_, j_]), (x_ + 1, y_, Hc[i_, j_ + 1]), (x_ + 1, y_ + 1, Hc[i_ + 1, j_ + 1]), (x_, y_ + 1, Hc[i_ + 1, j_])]
            ff.append((4 * k_, 4 * k_ + 1, 4 * k_ + 2, 4 * k_ + 3))
        lawn_ob = bc.mesh_from("lawn_ground", vv, ff, smooth=False, coll=gcoll)
        lawn_ob.data.materials.append(TM)
        md_ = lawn_ob.modifiers.new("grass", "NODES"); md_.node_group = ground.grass_nodes("GN_grass_lawn", protos_lawn, density=40, seed=2)
        print("grass: lawn", len(ff), "m2; sod roofs", sum(1 for o in bpy.data.objects if o.name.startswith("EN-sod-")))

# ---------------------------------------------------------------- forest (stage 4+: the site is landscaped round the finished building)
LOD_EYE = None
if STAGE >= 4 and (OUT / "tree_lib.blend").exists() and (OUT / "forest_points.npz").exists():
    with bpy.data.libraries.load(str(OUT / "tree_lib.blend"), link=False) as (src, dst):
        dst.collections = ["tree_lib"]
    lib = dst.collections[0]
    fp = np.load(OUT / "forest_points.npz")
    forest_coll = bc.collection("6 · forest")
    pv = np.stack([fp["x"], fp["y"], fp["z"]], 1)
    me = bpy.data.meshes.new("forest_points"); me.vertices.add(len(pv)); me.vertices.foreach_set("co", pv.astype(np.float32).ravel())
    for nm, arr, typ in (("idx", fp["index"], "INT"), ("scl", fp["scale"], "FLOAT"), ("rot", fp["rot"], "FLOAT")):
        at = me.attributes.new(nm, typ, "POINT"); at.data.foreach_set("value", arr)
    forest = bpy.data.objects.new("forest", me); forest_coll.objects.link(forest)
    LOD_EYE = bpy.data.objects.new("lod_eye", None); scene.collection.objects.link(LOD_EYE)
    D1, D2 = 30.0, 90.0  # every needle within 30 m, reduced to 90 m, impostors beyond (see construction/lod_test.py)
    ng = bpy.data.node_groups.new("GN_forest", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N_, L_ = ng.nodes, ng.links
    gi, go = N_.new("NodeGroupInput"), N_.new("NodeGroupOutput")
    ci = N_.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = lib
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True; ci.transform_space = "ORIGINAL"
    eye = N_.new("GeometryNodeObjectInfo"); eye.inputs[0].default_value = LOD_EYE
    pos = N_.new("GeometryNodeInputPosition")
    dist = N_.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"; L_.new(pos.outputs[0], dist.inputs[0]); L_.new(eye.outputs["Location"], dist.inputs[1])
    def mnode(op, a, b_):
        n = N_.new("ShaderNodeMath"); n.operation = op
        for k, v in enumerate((a, b_)):
            (L_.new(v, n.inputs[k]) if not isinstance(v, (int, float)) else n.inputs[k].__setattr__("default_value", v))
        return n.outputs[0]
    lod = mnode("ADD", mnode("GREATER_THAN", dist.outputs["Value"], D1), mnode("GREATER_THAN", dist.outputs["Value"], D2))
    def attr(name, typ="FLOAT"):
        a_ = N_.new("GeometryNodeInputNamedAttribute"); a_.data_type = typ; a_.inputs["Name"].default_value = name
        return a_.outputs["Attribute"]
    index = mnode("ADD", mnode("MULTIPLY", attr("idx", "INT"), 3), lod)
    # no tree within 5 m of the rendering camera (a camera never starts inside a crown)
    near = mnode("LESS_THAN", dist.outputs["Value"], 5.0)
    dl = N_.new("GeometryNodeDeleteGeometry"); dl.domain = "POINT"; L_.new(gi.outputs[0], dl.inputs["Geometry"]); L_.new(near, dl.inputs["Selection"])
    ip = N_.new("GeometryNodeInstanceOnPoints"); ip.inputs["Pick Instance"].default_value = True
    L_.new(dl.outputs[0], ip.inputs["Points"]); L_.new(ci.outputs[0], ip.inputs["Instance"]); L_.new(index, ip.inputs["Instance Index"])
    rz = N_.new("ShaderNodeCombineXYZ"); L_.new(attr("rot"), rz.inputs["Z"])
    e2r = N_.new("FunctionNodeEulerToRotation"); L_.new(rz.outputs[0], e2r.inputs[0]); L_.new(e2r.outputs[0], ip.inputs["Rotation"])
    L_.new(attr("scl"), ip.inputs["Scale"])
    L_.new(ip.outputs[0], go.inputs[0])
    md = forest.modifiers.new("forest", "NODES"); md.node_group = ng
    print("forest:", len(pv), "trees, library", lib.get("src_hash"))

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
    # reception (E1 floor = 0.12, eye 1.62)
    "rec_entry": ((29.7, 13.6, 1.62), (24.0, 9.0, 2.2), 18),
    "rec_from_cafe": ((27.5, -5.0, 1.62), (25.5, 14.0, 2.4), 18),
    "rec_ceiling": ((29.0, 15.2, 1.62), (21.0, 2.0, 4.9), 16),
    "rec_desk_wall": ((28.6, 9.0, 1.62), (24.1, 12.5, 1.6), 24),
    "rec_detail": ((25.6, 13.4, 0.95), (24.1, 14.6, 0.35), 30),
    "rec_desk": ((29.3, 7.6, 1.62), (25.4, 11.6, 1.1), 20),
    "rec_vestibule": ((26.6, 11.3, 1.62), (30.5, 11.3, 1.6), 20),
    "cafe_bar": ((28.6, 4.6, 1.62), (21.25, -1.35, 1.4), 18),
    "cafe_bridge": ((12.6, 4.8, 1.62), (19.5, -4.0, 1.4), 18),
    "cafe_window": ((25.2, -6.2, 1.4), (17.5, -8.9, 1.0), 20),
    "rec_art": ((28.4, 11.3, 1.62), (24.2, 11.3, 2.6), 18),
    "rec_art_close": ((24.9, 12.6, 2.4), (24.22, 13.2, 2.35), 50),
    "rec_corner_n": ((27.6, 13.0, 1.62), (24.0, 16.2, 2.2), 24),
    "rec_corner_s": ((27.6, 9.4, 1.62), (24.0, 6.8, 2.2), 24),
    "rec_mat": ((26.6, 12.9, 1.62), (30.2, 11.1, 0.15), 22),
    "rec_scraper": ((29.4, 13.6, 1.62), (32.2, 11.3, 0.1), 22),
    # public WCs (E1)
    "wc_w_aisle": ((14.9, 8.3, 1.62), (13.9, 15.8, 1.5), 16),
    "wc_w_vanity": ((14.3, 8.4, 1.62), (16.3, 11.6, 1.3), 18),
    "wc_w_light": ((15.9, 8.4, 1.5), (12.3, 13.5, 4.2), 15),
    "wc_m_aisle": ((17.2, 8.4, 1.62), (20.4, 13.4, 1.3), 16),
    "wc_acc": ((14.1, 13.9, 1.62), (13.0, 16.1, 0.9), 14),
}
for n, (loc, tgt, lens) in CAMS.items():
    bc.camera(scene, f"cam_{n}", loc, tgt, lens)
if STAGE >= 4:  # frames, mullions, posts, girders, stained columns: small bevels so every edge catches a highlight (real profiles are never razor sharp)
    for o in bpy.data.objects:
        if o.type == "MESH" and o.data.materials and o.data.materials[0].name in ("blackened_steel_d", "tarred_timber") \
                and not any(md_.type == "BOOLEAN" for md_ in o.modifiers):
            bv = o.modifiers.new("edge", "BEVEL"); bv.width = 0.004; bv.segments = 2; bv.limit_method = "ANGLE"; bv.harden_normals = False
for o in bpy.data.objects:  # primitives + boolean results: flat shading for every hard-surface element
    organic = o.name.startswith(("terrain", "river", "falls", "tuft_", "shoot_", "lawn_ground")) or \
        any(c_.name.startswith("v") and "_L" in c_.name for c_ in o.users_collection)  # library trees keep their smooth wood
    if o.type == "MESH" and not organic:
        o.data.polygons.foreach_set("use_smooth", np.zeros(len(o.data.polygons), bool))
# Roman's rule: all foliage is hidden in the viewport in the saved file (opening it must not crash / crawl).
# Viewport only: renders (here and in the file) still include it; tick the monitor icon on "6 · forest" / "6 · grass" to show it.
for cn in ("6 · forest", "6 · grass"):
    c_ = bpy.data.collections.get(cn)
    if c_:
        c_.hide_viewport = True  # collection-level: not even evaluated in the viewport
for o in bpy.data.objects:  # grass on the sod roofs lives as modifiers on the roof slabs: off in the viewport
    for md_ in o.modifiers:
        if md_.type == "NODES" and md_.node_group and md_.node_group.name.startswith(("GN_grass", "GN_forest")):
            md_.show_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"stage_{STAGE}.blend"))
EXPO = scene.view_settings.exposure
if RENDER:
    shots = {0: ["site_aerial", "ravine_upstream", "site_top"], 1: ["pit_overview", "pit_east", "cofferdam", "pit_floor", "daycare_garden", "site_top"],
             3: ["frame_overview", "frame_east", "frame_gorge", "roof_eaves", "lounge_deck", "hall_f1", "spiral", "daycare_garden", "site_top"],
             5: ["rec_art", "rec_art_close", "rec_entry", "rec_desk", "rec_vestibule", "rec_from_cafe", "cafe_bar", "cafe_bridge", "cafe_window", "wc_w_aisle", "wc_w_vanity", "wc_m_aisle", "wc_acc"],
             4: ["style_gorge", "style_aerial", "style_arrival", "west_garden", "frame_east", "roof_eaves", "lounge_deck", "daycare_garden", "garden_close", "hall_f1", "river_window_f3", "stair_f3_f4", "towers_west"]}
    for n in (ONLY or shots[max(k for k in shots if k <= STAGE)]):
        scene.camera = bpy.data.objects[f"cam_{n}"]
        if LOD_EYE is not None:  # LOD switches by distance from this camera
            LOD_EYE.location = scene.camera.location; bpy.context.view_layer.update()
        scene.view_settings.exposure = EXPO + (2.8 if n.startswith(("rec_", "cafe_", "wc_", "dc_")) else 0.0)  # interiors exposed for the room, like a photographer would
        scene.render.filepath = str(OUT / f"stage_{STAGE}_{n}.png")
        bpy.ops.render.render(write_still=True)
        # Roman's rule: never overwrite a render. Every render is also kept as the next version in construction/renders/.
        RND = ROOT / "construction" / "renders"; RND.mkdir(exist_ok=True)
        v = 1 + max([int(p_.stem.rsplit("_v", 1)[1]) for p_ in RND.glob(f"stage_{STAGE}_{n}_v*.jpg") if p_.stem.rsplit("_v", 1)[1].isdigit()] or [0])
        img_ = bpy.data.images.load(scene.render.filepath)
        sc_ = bpy.context.scene; ff = sc_.render.image_settings.file_format; q_ = sc_.render.image_settings.quality
        vs_ = sc_.view_settings; keep_ = (vs_.view_transform, vs_.look, vs_.exposure)
        vs_.view_transform = "Standard"; vs_.look = "None"; vs_.exposure = 0.0  # the PNG is already graded: store it as is
        sc_.render.image_settings.file_format = "JPEG"; sc_.render.image_settings.quality = 90
        img_.save_render(str(RND / f"stage_{STAGE}_{n}_v{v:03d}.jpg"), scene=sc_)
        sc_.render.image_settings.file_format = ff; sc_.render.image_settings.quality = q_
        vs_.view_transform, vs_.look, vs_.exposure = keep_
        bpy.data.images.remove(img_)
        print("kept", f"stage_{STAGE}_{n}_v{v:03d}.jpg")
print("stage", STAGE, "done")

"""The gym equipment in the building (stage 5b), from the 2D layouts (model/layouts/gym_f*.json, tools/gym_layout.py).

Each piece is built once from its own model.py with the equipment kit (equipment/blender/kit.py: the procedural looks, not
the .glb exports) into a hidden prototype collection, then placed as collection instances: the plan's (x, y) is the centre of
its footprint, rot the way the user faces (0 = north, 90 = west); the model's own axis the user faces is the kind's "face".
A remodelled piece swaps in on the next build. Wall pieces build without their display wall (k.display = False), the PWR
Play modules from the plan's Cores and stations (pwr_play.build_layout), the pull-up stations from the Monkey Rig's parts,
the rig-mount parallel bars into the Monkey Rig's end bay.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
EQ = ROOT / "equipment"
sys.path.insert(0, str(EQ / "blender"))
import kit  # noqa: E402

AXV = {"+x": (1, 0), "-x": (-1, 0), "+y": (0, 1), "-y": (0, -1)}
_mods = {}


def _model(piece):
    if piece not in _mods:
        spec = importlib.util.spec_from_file_location(f"pm_{piece.replace('-', '_')}", EQ / "pieces" / piece / "model.py")
        pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
        _mods[piece] = pm
    return _mods[piece]


def _proto(piece, parent, display=True, tweak=None):
    """Build a piece once into its own collection (excluded from the view layer); returns (collection, its xy box centre)."""
    name = f"eq_{piece}" + ("" if display else "_wall") + (f"_{tweak[0]}" if tweak else "")
    if name in bpy.data.collections:
        c = bpy.data.collections[name]
        return c, tuple(c["centre"])
    pm = _model(piece)
    if tweak:
        tweak[1](pm)
    c = bpy.data.collections.new(name); parent.children.link(c)
    k = kit.Kit(piece, c, getattr(pm, "LOOK", None))
    k.check = lambda: None
    if not display:
        k.display = False
    pm.build(k)
    obs = k.finish()
    for o in obs:
        if o.name not in c.objects:
            for cc in list(o.users_collection):
                cc.objects.unlink(o)
            c.objects.link(o)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(b) for o in obs if o.type == "MESH" for b in o.bound_box]
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    c["centre"] = (cx, cy)
    return c, (cx, cy)


def _instance(c, coll, M, name):
    e = bpy.data.objects.new(name, None)
    e.instance_type = "COLLECTION"; e.instance_collection = c
    e.matrix_world = M
    coll.objects.link(e)
    return e


def _turn(face, rot):
    """The z rotation (rad) taking the model's user-facing axis to the plan's rot."""
    fx, fy = AXV[face]
    return math.radians(rot) + math.pi / 2 - math.atan2(fy, fx)


def pullup_station(k, W):
    """A freestanding double muscle-up bar from the Monkey Rig's parts (Roman 2026-10-31: "the pull-up bars we have restrict
    muscle-ups"; then "those muscle up capable pull up bars look too thin and weird": two lone posts with a 1.25 in bar read
    as two poles). Now one station, W long: three red 3x3 uprights on 12 in bolted plates, the two outer ones braced by a
    raking 3x3 leg out along the bar's line (out of the swing, which runs front and back), knee gussets under the bars; two
    1.5 in bare-steel bars, 1.67 m clear each, sitting in black cups on top of the uprights at the rig's 2.47 m (the 6 ft 3 in
    dead-hang rule). Nothing above the bars, nothing in front of or behind them."""
    mr = _model("rogue-monster-lite-monkey-rig-2-0")
    k.look(**{r: v for r, v in mr.LOOK.items() if r not in k.looks})
    k.look(steel=dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0, bump=(1400, 0.08)))
    IN, TB, Z = mr.IN, mr.TB, mr.Z_PU
    R = 1.5 * IN / 2
    RAKE, KNEE = 0.55, 1.55                      # the brace's foot out from the upright; where it meets the upright
    CUP = 0.06
    xo = W / 2 - RAKE                            # the outer uprights' centres
    xs = (-xo, 0.0, xo)
    top = Z - R - 0.012
    PL = 12 * IN
    for x in xs:
        k.box("frame", (x, 0, 0.0127 / 2), (PL, PL, 0.0127), soft=0.0015)                                  # the base plate, 1/2 in
        for sx in (-1, 1):
            for sy in (-1, 1):
                k.bolt((x + sx * 0.11, sy * 0.11, 0.0127), "+z", size=0.016)                                 # the floor anchors
        k.bar("frame", (x, 0, 0.0127), (x, 0, top - CUP), TB, TB, r=0.004)
        k.box("black", (x, 0, top - CUP / 2), (TB + 0.008, TB + 0.008, CUP), soft=0.003)                  # the cup's body
        k.box("black", (x, 0, top + 0.006), (TB + 0.008, TB + 0.008, 0.012), soft=0.002)                 # the saddle the bar sits on
        for sy in (-1, 1):                                                                                 # the cup's lips either side of the bar
            k.box("black", (x, sy * (R + 0.005), Z - R + 0.016), (TB + 0.008, 0.008, 0.044), soft=0.001)
        k.box("black", (x, -TB / 2 - 0.0015, 1.78), (TB - 0.01, 0.003, 0.40), soft=0.001)
        k.text("label", "ROGUE", (x, -TB / 2 - 0.0033, 1.78), 0.048, depth=0.0006, spin=math.pi / 2)
        for sx in ((-1, 1) if x == 0 else ((1,) if x < 0 else (-1,))):                                     # gussets: 10 mm plates
            x0 = x + sx * TB / 2                                                                           # under the bars, welded on
            k.block("frame", lambda a, b, c, x0=x0, sx=sx: (x0 + (sx * 0.22 if a > 0 else 0.0), b * 0.005,
                                                            Z - R if (a > 0 or c > 0) else top - CUP - 0.30))
    for sx in (-1, 1):                                                                                     # the raking legs, out along the bar
        xu, xf = sx * xo, sx * (xo + RAKE)
        k.box("frame", (xf, 0, 0.0127 / 2), (0.22, PL, 0.0127), soft=0.0015)
        for sy in (-1, 1):
            k.bolt((xf + sx * 0.06, sy * 0.11, 0.0127), "+z", size=0.016)
        k.bar("frame", (xf, 0, 0.0127 + TB / 2), (xu + sx * TB / 2, 0, KNEE), TB, TB, r=0.004)
        k.tube("steel", (xu + sx * (TB / 2 + 0.004), 0, Z), (sx * 0.004, 0, Z), R, seg=28)                 # the bar: the outer cup to the middle
        k.cyl("black", (xu + sx * (TB / 2 + 0.008), 0, Z), R + 0.002, 0.008, axis="x", seg=28)              # its end cap


def build_floor(name, z, coll, protos):
    data = json.loads((ROOT / "model" / "layouts" / f"{name}.json").read_text())
    K = data["kinds"]
    byid = {it["id"]: it for it in data["items"]}
    n = 0
    for it in data["items"]:
        kd = it["kind"]
        if it.get("fixed") and kd != "pwr_meta":
            continue
        piece = K.get(kd, {}).get("piece")
        if piece and piece in ("rogue-rig-mount-parallel-bars",) and it.get("on") in byid:
            rig = byid[it["on"]]
            mr = _model(rig["kind"])
            if rig["kind"] == "rogue-monster-rig-2-0":                  # the 49 in squat cell, the bars cut to its 49 in depth
                xu, bay = mr.BAYS[0] / 2, ((mr.XS[0] + mr.XS[1]) / 2, 0.0)
            else:                                                       # the Monkey Rig: the east end's 43 in bay
                xu, bay = (mr.XS[5] - mr.XS[4]) / 2, ((mr.XS[4] + mr.XS[5]) / 2, 0.0)
            pb = lambda pm: (setattr(pm, "YU", mr.DEP / 2), setattr(pm, "XU", xu))
            c, (cx, cy) = _proto(piece, protos, display=False, tweak=(rig["kind"], pb))
            rc, (rcx, rcy) = _proto(rig["kind"], protos)
            a = _turn(K[rig["kind"]]["face"], rig["rot"])
            Mr = Matrix.Translation((rig["x"], rig["y"], z)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((-rcx, -rcy, 0))
            _instance(c, coll, Mr @ Matrix.Translation((bay[0] - cx, bay[1] - cy, 0)) @ Matrix.Translation((cx, cy, 0)), it["id"])
            n += 1
            continue
        if piece:
            wall = K[kd].get("wall", False)
            c, (cx, cy) = _proto(piece, protos, display=not wall)
            a = _turn(K[kd]["face"], it.get("rot", 0))
            M = Matrix.Translation((it["x"], it["y"], z + it.get("lift", 0.0))) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((-cx, -cy, 0))
            _instance(c, coll, M, it["id"]); n += 1   # (lift: a wall piece hung higher than its model's mount, the pegboard)
        elif kd == "rig_spur":
            span = it["w"]
            cname = f"eq_mubar2_{span:.2f}"
            if cname in bpy.data.collections:
                c = bpy.data.collections[cname]
            else:
                c = bpy.data.collections.new(cname); protos.children.link(c)
                k = kit.Kit("pullup", c, _model("rogue-monster-lite-monkey-rig-2-0").LOOK); k.check = lambda: None
                pullup_station(k, span)
                for o in k.finish():
                    if o.name not in c.objects:
                        for cc in list(o.users_collection):
                            cc.objects.unlink(o)
                        c.objects.link(o)
            a = math.radians(it.get("rot", 0))          # the bar along the plan's w (local x)
            _instance(c, coll, Matrix.Translation((it["x"], it["y"], z)) @ Matrix.Rotation(a, 4, "Z"), it["id"]); n += 1
        elif kd == "pwr_meta":
            import pwr_play as pp
            D = it["spacing"]; ox, oy = it["origin"]
            L = dict(cores={c_: (i * D, j * D) for c_, (i, j) in it["cores"].items()},
                     faces={tuple(k_.split(",")): st for k_, st in it["faces"].items() if st},
                     bars=[(a_, b_, ("flat", "neutral", "angled")[q % 3]) for q, (a_, b_) in enumerate(it["bars"])])
            cname, sig = f"eq_{it['group']}", json.dumps({k_: it.get(k_) for k_ in ("spacing", "cores", "faces", "bars")}, sort_keys=True)
            c = next((c_ for c_ in bpy.data.collections if c_.name.split(".")[0] == cname and c_.get("sig") == sig), None)
            if c is None:   # built once per layout: a saved scene's module is reused (construction/patch_saved.py)
                c = bpy.data.collections.new(cname); protos.children.link(c); c["sig"] = sig
                k = kit.Kit(cname, c, pp.LOOK); k.check = lambda: None
                pp.build_layout(k, L)
                for o in k.finish():
                    if o.name not in c.objects:
                        for cc in list(o.users_collection):
                            cc.objects.unlink(o)
                        c.objects.link(o)
            _instance(c, coll, Matrix.Translation((ox, oy, z)), it["group"]); n += 1
    return n


def build(model, coll, floors=("gym_f1",)):
    """All the listed floors' equipment into coll; the prototypes in a hidden collection beside it."""
    lv = {l["id"]: l["elevation"] for l in model["levels"]}
    protos = bpy.data.collections.new("eq_prototypes"); bpy.context.scene.collection.children.link(protos)
    out = 0
    for nm in floors:
        lvl = json.loads((ROOT / "model" / "layouts" / f"{nm}.json").read_text())["level"]
        out += build_floor(nm, lv[lvl], coll, protos)
    lc = bpy.context.view_layer.layer_collection.children.get("eq_prototypes")
    if lc:
        lc.exclude = True                                # the prototypes only render through their instances
    return out

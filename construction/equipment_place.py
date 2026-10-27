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


def pullup_station(k, span):
    """A freestanding pull-up station from the Monkey Rig's parts: two 108 in red uprights on base plates, a black cap and
    crossmember over them, the 2 in pull-up bar at the rig's 2.47 m on ROGUE gussets (the 6 ft 3 in dead-hang rule)."""
    mr = _model("rogue-monster-lite-monkey-rig-2-0")
    k.look(**{r: v for r, v in mr.LOOK.items() if r not in k.looks})
    IN, TB, Z, R = mr.IN, mr.TB, mr.Z_PU, mr.R_PU
    H = 108 * IN
    xs = (-span / 2 - TB / 2, span / 2 + TB / 2)
    for x in xs:
        k.box("frame", (x, 0, 0.0095 / 2), (7 * IN, 7 * IN, 0.0095), soft=0.0015)
        k.bar("frame", (x, 0, 0.0095), (x, 0, H - TB - 0.002), TB, TB, r=0.004)
        k.box("black", (x, 0, H - TB / 2), (TB, TB, TB), soft=0.003)
        k.box("black", (x, -TB / 2 - 0.0015, 1.78), (TB - 0.01, 0.003, 0.40), soft=0.001)
        k.text("label", "ROGUE", (x, -TB / 2 - 0.0033, 1.78), 0.048, depth=0.0006, spin=math.pi / 2)
    k.bar("black", (xs[0] + TB / 2, 0, H - TB / 2), (xs[1] - TB / 2, 0, H - TB / 2), TB, TB, up=(0, 1, 0), r=0.004)
    G, PL = 0.18, mr.PL
    for xf, sg in ((xs[0] + TB / 2, 1), (xs[1] - TB / 2, -1)):
        k.box("black", (xf + sg * PL / 2, 0, Z - R - G / 2), (PL, TB, G + 0.02), soft=0.001)
    k.tube("black", (xs[0] + TB / 2 + PL, 0, Z), (xs[1] - TB / 2 - PL, 0, Z), R, seg=28)


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
            M = Matrix.Translation((it["x"], it["y"], z)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((-cx, -cy, 0))
            _instance(c, coll, M, it["id"]); n += 1
        elif kd == "rig_spur":
            span = it["w"] - 2 * 3 * 0.0254 - 0.1
            cname = f"eq_pullup_{span:.2f}"
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
            cname = f"eq_{it['group']}"
            c = bpy.data.collections.new(cname); protos.children.link(c)
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

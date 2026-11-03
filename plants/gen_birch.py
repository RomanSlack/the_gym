"""A multi-stem silver birch (Betula pendula), the Nordic signature tree for the gym (Roman 2026-11-02: "pine trees or
those types of things"):
- 2-4 stems from one root plate, leaning apart and curving up, 2.4-3 m
- branches ascending from the upper 60 % then arching over, their tips drooping; off them the weeping twigs that make a
  silver birch: thin wiry strands hanging straight down
- leaves from a generated photo atlas (plants/maps/birch: fresh, mid, dark, young, yellowing), every 2-3 cm along the
  twigs on short petioles, hanging, faces out; light through them
- bark from two generated 4K photo textures, box-projected at real scale: chalk-white papery bark with lenticel dashes,
  the dark fissured bark at the foot, and the black "eyebrow" patches under every branch joint (the birch's tell),
  plus a few dark blotches up the stems
- wood fused into one body (voxel remesh), the twigs as thin tubes

    import gen_birch; objs = gen_birch.build(seed, (x, y, z), height=2.8)
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "walls"))
from gen_bonsai import _obj, _img, closed_tube, tube  # noqa: E402
from gen_greenwall import pothos_material  # noqa: E402

MAPS = HERE / "maps" / "birch"
_M = {}


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bark_material():
    if "bark" in _M:
        return _M["bark"]
    m = bpy.data.materials.new("birch_bark"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")

    def img(name, scale, color=True):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        t = N.new("ShaderNodeTexImage"); t.image = _img(MAPS / name, color); t.projection = "BOX"; t.projection_blend = 0.25
        L.new(mp.outputs[0], t.inputs["Vector"]); return t
    wc, wh = img("barkwhite4k_col.jpg", 5), img("barkwhite4k_h.png", 5, False)
    dc, dh = img("barkbase4k_col.jpg", 5), img("barkbase4k_h.png", 5, False)
    wt = N.new("ShaderNodeHueSaturation"); wt.inputs["Value"].default_value = 0.88; L.new(wc.outputs[0], wt.inputs["Color"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "dark"
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(at.outputs["Fac"], mx.inputs[0]); L.new(wt.outputs[0], mx.inputs[6]); L.new(dc.outputs[0], mx.inputs[7])
    hm = N.new("ShaderNodeMix"); hm.data_type = "FLOAT"
    L.new(at.outputs["Fac"], hm.inputs[0]); L.new(wh.outputs[0], hm.inputs[2]); L.new(dh.outputs[0], hm.inputs[3])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; bp.inputs["Distance"].default_value = 0.002
    L.new(hm.outputs[0], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(mx.outputs[2], pb.inputs["Base Color"]); L.new(bp.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = 0.7; pb.inputs["Specular IOR Level"].default_value = 0.3   # papery, a faint sheen
    L.new(pb.outputs[0], out.inputs["Surface"])
    _M["bark"] = m
    return m


def twig_material():
    m = bpy.data.materials.get("birch_twig") or bpy.data.materials.new("birch_twig"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.09, 0.05, 0.035, 1)   # red-brown fine twigs
    b.inputs["Roughness"].default_value = 0.55
    return m


def _arc(p0, d0, L, n, rng, droop, wob=0.15):
    """a branch: out along d0, bending down more and more toward its tip (the weeping habit)"""
    pts = [np.array(p0, float)]; d = _unit(np.array(d0, float))
    for i in range(n):
        t = (i + 1) / n
        d = _unit(d + np.array([0, 0, -droop * t * 2.2 / n]) + rng.normal(0, wob / math.sqrt(n), 3))
        pts.append(pts[-1] + d * L / n)
    return np.array(pts)


def build(seed, loc=(0, 0, 0), height=2.8, name="birch", leaf_scale=1.0):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    spines, joints, twigs = [], [], []
    n_st = int(rng.integers(2, 5))
    a0 = rng.uniform(0, 2 * math.pi)
    for s in range(n_st):
        a = a0 + 2 * math.pi * s / n_st + rng.normal(0, 0.3)
        out = np.array([math.cos(a), math.sin(a), 0.0])
        H = height * rng.uniform(0.82, 1.0) * (1 if s == 0 else rng.uniform(0.85, 1.0))
        R0 = rng.uniform(0.04, 0.058) * height / 2.8
        lean = rng.uniform(0.12, 0.28)
        pts = [out * 0.04]
        for i in range(50):
            t = (i + 1) / 50
            d = _unit(np.array([0, 0, 1.0]) + out * lean * (1.2 - t) + np.cross([0, 0, 1.0], out) * 0.05 * math.sin(5 * t + s))
            pts.append(pts[-1] + d * H / 50)
        st = np.array(pts)
        tt = np.linspace(0, 1, len(st))
        rad = R0 * (1 - 0.85 * tt ** 0.9) * (1 + 0.3 * np.exp(-tt / 0.04))
        spines.append((st, rad))
        for _ in range(int(rng.integers(8, 14))):                          # the leader: clothed in twigs to its tip
            k = int(rng.uniform(0.8, 1.0) * (len(st) - 1))
            d0 = _unit(np.array([*rng.normal(0, 0.6, 2), rng.uniform(0.0, 0.5)]))
            twigs.append(_arc(st[k], d0, rng.uniform(0.15, 0.4) * height / 2.8, 10, rng, droop=2.0, wob=0.1))
        # branches: ascending, arching over, tips drooping; longer in the middle of the crown
        n_br = int(rng.integers(20, 28))
        hs = np.sort(rng.uniform(0.38, 0.95, n_br))
        ab = rng.uniform(0, 2 * math.pi)
        for i, h in enumerate(hs):
            k = int(h * (len(st) - 1))
            ab += math.radians(rng.uniform(120, 150))
            bo = _unit(np.array([math.cos(ab), math.sin(ab), 0.0]) + out * 0.6)     # (they favour the open side)
            if bo @ out < -0.3:
                continue                                                   # not into the neighbouring stems
            up = rng.uniform(0.7, 1.3)
            L = height * (0.12 + 0.28 * math.sin(math.pi * min(1, (h - 0.3) / 0.7))) * rng.uniform(0.8, 1.2)
            bp = _arc(st[k], bo + np.array([0, 0, up]), L, 16, rng, droop=rng.uniform(0.6, 1.1))
            br = np.linspace(rad[k] * 0.45, 0.004, len(bp))
            spines.append((bp, br)); joints.append((st[k], rad[k], bo))
            # weeping twigs: off the outer 70 % of the branch, hanging down
            for _ in range(int(rng.integers(8, 15) * L / 0.6) + 3):
                j = int(rng.uniform(0.3, 1.0) * (len(bp) - 1))
                d0 = _unit(np.array([*rng.normal(0, 0.4, 2), -0.2]) + _unit(bp[min(j + 1, len(bp) - 1)] - bp[max(j - 1, 0)]) * 0.6)
                tw = _arc(bp[j], d0, rng.uniform(0.18, 0.5) * height / 2.8, 10, rng, droop=2.2, wob=0.1)
                twigs.append(tw)
    # ---- the wood: fused
    allV, allF, off = [], [], 0
    for sp, rr in spines:
        V_, F_ = closed_tube(sp, np.maximum(rr, 0.004), sides=18)
        allV.append(V_); allF += [[i + off for i in f] for f in F_]; off += len(V_)
    raw = _obj(f"{name}_wood_raw", np.concatenate(allV), allF, None)
    rm = raw.modifiers.new("fuse", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0028; rm.adaptivity = 0.0
    sm = raw.modifiers.new("sm", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(raw.evaluated_get(dg))
    bpy.data.objects.remove(raw)
    nV = len(me.vertices)
    P = np.empty(nV * 3, np.float32); me.vertices.foreach_get("co", P); P = P.reshape(-1, 3).astype(np.float64)
    # dark bark: the foot, the eyebrows under the joints, a few blotches
    foot = np.clip((0.35 * height / 2.8 - P[:, 2]) / 0.25, 0, 1) ** 0.7
    K = rng.normal(0, 1, (12, 3)) * 9; ph = rng.uniform(0, 6.3, 12)
    nz = sum(np.sin(P @ K[i] + ph[i]) for i in range(12)) / math.sqrt(12)
    blot = np.clip((nz - 1.25) * 2.5, 0, 1)
    brow = np.zeros(nV)
    for jp, jr, bo in joints:
        q = P - jp
        # a wide chevron below + either side of the joint: within ~2.5 r round the stem, 1-4 r under it
        horiz = np.linalg.norm(q[:, :2] - bo[:2] * (q[:, :2] @ bo[:2])[:, None], axis=1)
        under = -q[:, 2]
        brow = np.maximum(brow, np.clip(1 - np.abs(under - (1.2 + 0.6 * horiz / jr) * jr) / (0.5 * jr), 0, 1)
                          * (np.linalg.norm(q, axis=1) < jr * 4.5) * ((q[:, :2] @ bo[:2]) > -0.2 * jr))
    dark = np.clip(np.maximum.reduce([foot, blot, brow]), 0, 1)
    at = me.attributes.new("dark", "FLOAT", "POINT"); at.data.foreach_set("value", dark.astype(np.float32))
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
    wood = bpy.data.objects.new(f"{name}_wood", me); bpy.context.scene.collection.objects.link(wood)
    wood.data.materials.append(bark_material()); wood.location = loc
    objs = [wood]
    # ---- twigs + leaves
    atlas = json.loads((MAPS / "atlas.json").read_text())
    names = sorted(atlas); pw = np.array([0.24, 0.3, 0.22, 0.12, 0.12])
    banks = {k: ([], [], [], []) for k in names}
    tv, tf, off = [], [], 0
    for tw in twigs:
        V_, F_, _ = tube(tw, np.linspace(0.0022, 0.0007, len(tw)), sides=5, cap=False)
        tv.append(V_); tf += [[i + off for i in f] for f in F_]; off += len(V_)
        seg = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(tw, axis=0), axis=1))])
        s = rng.uniform(0.0, 0.02); side = 1
        while s < seg[-1]:
            j = min(int(np.searchsorted(seg, s)), len(tw) - 2)
            tang = _unit(tw[j + 1] - tw[j])
            sv = _unit(np.cross(tang, rng.normal(0, 1, 3))) * side
            pet = _unit(sv + np.array([0, 0, -0.3]) + rng.normal(0, 0.2, 3))
            j0 = tw[j] + pet * rng.uniform(0.008, 0.016)
            nm = names[int(rng.choice(len(names), p=pw))]; info = atlas[nm]
            Ls = rng.uniform(0.022, 0.038) * (0.75 if nm == "leaf4" else 1.0) * leaf_scale   # (3-5.5 cm read oversized at 3 m; a 7 m tree: x1.5)
            fan = _unit(np.array([0, 0, -0.75]) + pet * 0.7 + rng.normal(0, 0.25, 3))        # hanging off the petiole
            facing = _unit(np.array([*_unit(j0[:2] - 0 * j0[:2] + 1e-6)[:2], 0.4]) + rng.normal(0, 0.4, 3))
            nrm = _unit(facing - fan * (facing @ fan))
            wv = np.cross(fan, nrm); w = Ls * info["aspect"]
            V, F, U, A = banks[nm]; o_ = len(V)
            for jv in range(3):
                for ju in range(3):
                    u_, v_ = ju / 2, jv / 2
                    x = (u_ - info["midrib_u"]) * w; y = (v_ - info["joint_v"]) * Ls
                    z = -0.08 * (x / w * 2) ** 2 * w - 0.05 * v_ * v_ * Ls
                    V.append(j0 + fan * y + wv * x + nrm * z); U.append((u_, v_))
            F += [[o_ + jv * 3 + ju, o_ + jv * 3 + ju + 1, o_ + (jv + 1) * 3 + ju + 1, o_ + (jv + 1) * 3 + ju] for jv in range(2) for ju in range(2)]
            A += [rng.uniform(-0.8, 0.8)] * 9
            s += rng.uniform(0.011, 0.02) * leaf_scale ** 1.4; side = -side          # (bigger leaves, spaced to match: same cover, fewer faces)
    objs.append(_obj(f"{name}_twigs", np.concatenate(tv) + loc, tf, twig_material()))
    n_l = 0
    for nm, (V, F, U, A) in banks.items():
        if F:
            n_l += len(F) // 4
            objs.append(_obj(f"{name}_{nm}", np.array(V) + loc, F, pothos_material(nm, MAPS, rough=0.5, val=0.85, bump=0.0003), U, {"var": A}))
    for o in objs:
        o["tree"] = True
    print(f"birch {name} {seed}: {n_st} stems, {len(joints)} branches, {len(twigs)} twigs, {n_l} leaves")
    return objs

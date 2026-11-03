"""Fiddle-leaf fig (Ficus lyrata) as an interior standard: the big floor plant for the gym's calmer corners (Roman 2026-11-02:
"more plants"). A clean bare trunk to ~1 m, then a head of 3-5 branches rising and leaning out, the huge violin leaves
(generated photo atlas, plants/maps/ficus) spiralling up the outer 70 % of each branch on short thick petioles, biggest
lower down, a young pale one + a bud sheath at every tip. Leaves held out and a little nodding, cupped along the midrib
with a gentle wave; no leaf passes through another (each tries up to 25 placements, kept clear of everything placed).
The trunk: smooth grey-brown fig bark (a fine procedural speckle: it's smooth and it's small in frame).

    import gen_ficus; objs = gen_ficus.build(seed, (x, y, z), height=1.9)
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "walls"))
from gen_bonsai import _obj, tube  # noqa: E402
from gen_greenwall import pothos_material  # noqa: E402

MAPS = HERE / "maps" / "ficus"


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bark():
    m = bpy.data.materials.get("fig_bark")
    if m:
        return m
    m = bpy.data.materials.new("fig_bark"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 6
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.042, 0.032, 1); cr.color_ramp.elements[1].color = (0.13, 0.11, 0.085, 1)   # (lighter read as aluminium)
    L.new(nz.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.75
    return m


def _curve(p0, d0, L, n, rng, up=0.0, wob=0.04):
    pts = [np.array(p0, float)]; d = _unit(np.array(d0, float))
    for i in range(n):
        d = _unit(d + np.array([0, 0, up / n]) + rng.normal(0, wob, 3))
        pts.append(pts[-1] + d * L / n)
    return np.array(pts)


def build(seed, loc=(0, 0, 0), height=1.9, name="ficus"):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    Ht = height * rng.uniform(0.48, 0.56)                                # the clear trunk
    trunk = _curve([0, 0, 0], [rng.normal(0, 0.05), rng.normal(0, 0.05), 1], Ht, 20, rng, wob=0.015)
    wood = [(trunk, np.linspace(0.028, 0.02, len(trunk)))]
    atlas = json.loads((MAPS / "atlas.json").read_text())
    big = ["leaf1", "leaf2", "leaf4", "leaf5"]
    banks = {k: ([], [], [], []) for k in atlas}
    placed = []                                                          # (centre, radius)
    n_br = int(rng.integers(5, 8)); a0 = rng.uniform(0, 2 * math.pi)
    n_leaf = 0
    for b in range(n_br):
        a = a0 + 2 * math.pi * b / n_br + rng.normal(0, 0.25)
        k = int(rng.uniform(0.75, 1.0) * (len(trunk) - 1))
        Lb = (height - Ht) * rng.uniform(0.75, 1.0)
        br = _curve(trunk[k], [math.cos(a) * 0.8, math.sin(a) * 0.8, 1], Lb * rng.uniform(0.7, 1.0), 16, rng, up=0.5, wob=0.03)
        wood.append((br, np.linspace(0.017, 0.007, len(br))))
        # leaves: spiralling up the outer 70 %, biggest low, a young one at the tip
        nl = int(rng.integers(14, 21))
        phi = rng.uniform(0, 6.3)
        for i in range(nl):
            t = 0.15 + 0.85 * i / (nl - 1)
            j = min(int(t * (len(br) - 1)), len(br) - 2)
            p = br[j]; tang = _unit(br[j + 1] - br[j])
            young = i == nl - 1
            nm = "leaf3" if young or (t > 0.85 and rng.random() < 0.5) else big[int(rng.integers(4))]
            info = atlas[nm]
            Ls = (0.14 if young else rng.uniform(0.24, 0.36) * (1.1 - 0.35 * t))
            best = None
            for att in range(40):
                ph = phi + math.radians(137.5) * i + rng.normal(0, 0.35 + 0.05 * att)
                out = _unit(np.cross(tang, [0, 0, 1.0]) * math.cos(ph) + np.cross(tang, np.cross(tang, [0, 0, 1.0])) * math.sin(ph) * -1)
                out = _unit(out + np.array([0, 0, 0.1]))
                pet = rng.uniform(0.03, 0.05)
                j0 = p + _unit(out + tang * 0.4) * pet
                # the blade: out and up from the petiole, nodding (tip a little below level), facing up-and-out
                el = math.radians(rng.uniform(35, 70) if not young else 75)
                fan = _unit(out * math.cos(el) + np.array([0, 0, 1.0]) * math.sin(el) + rng.normal(0, 0.08, 3))
                c = j0 + fan * Ls * 0.5
                r = Ls * 0.4
                if all(np.linalg.norm(c - q) > 0.72 * (r + rq) for q, rq in placed) and np.linalg.norm((c - trunk[-1])[:2]) > 0.06:
                    best = (j0, fan, c, r); break
            if best is None:
                continue
            j0, fan, c, r = best
            placed.append((c, r))
            hor = _unit(np.array([c[0], c[1], 0.0]) + out * 0.5)                   # facing out of the head (edge-on read as sticks)
            nrm = _unit(hor - fan * (hor @ fan)); nrm = _unit(nrm + np.array([0, 0, 0.25]) - fan * 0.25)
            wv = _unit(np.cross(fan, nrm)); w = Ls * info["aspect"]
            V, F, U, A = banks[nm]; o_ = len(V); G = 6
            wph = rng.uniform(0, 6.3)
            for jv in range(G):
                for ju in range(G):
                    u_, v_ = ju / (G - 1), jv / (G - 1)
                    x = (u_ - info["midrib_u"]) * w; y = (v_ - info["joint_v"]) * Ls
                    z = -0.12 * (x / w * 2) ** 2 * w - 0.12 * (v_ ** 2) * Ls + 0.012 * Ls * math.sin(9 * u_ + 7 * v_ + wph) * abs(x / w * 2)
                    V.append(j0 + fan * y + wv * x + nrm * z); U.append((u_, v_))
            F += [[o_ + jv * G + ju, o_ + jv * G + ju + 1, o_ + (jv + 1) * G + ju + 1, o_ + (jv + 1) * G + ju] for jv in range(G - 1) for ju in range(G - 1)]
            A += [rng.uniform(-0.6, 0.6)] * (G * G)
            wood.append((np.array([p, p + (j0 - p) * 0.5, j0]), np.array([0.005, 0.0045, 0.004])))
            n_leaf += 1
        # the bud sheath at the tip
        wood.append((np.array([br[-1], br[-1] + _unit(br[-1] - br[-2]) * 0.03, br[-1] + _unit(br[-1] - br[-2]) * 0.05]), np.array([0.006, 0.005, 0.0005])))
    tv, tf, off = [], [], 0
    for sp, rr in wood:
        V_, F_, _ = tube(sp, rr, sides=12)
        tv.append(V_); tf += [[i + off for i in f] for f in F_]; off += len(V_)
    objs = [_obj(f"{name}_wood", np.concatenate(tv) + loc, tf, bark())]
    for nm, (V, F, U, A) in banks.items():
        if F:
            objs.append(_obj(f"{name}_{nm}", np.array(V) + loc, F, pothos_material(nm, MAPS, rough=0.32, val=0.85, bump=0.0008), U, {"var": A}))
    for o in objs:
        o["tree"] = True
    print(f"ficus {name} {seed}: trunk {Ht:.2f} m, {n_br} branches, {n_leaf} leaves")
    return objs

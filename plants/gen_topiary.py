"""Clipped topiary, parametric (Roman 2026-11-02: "pine trees ... bushes sort of tailored"): boxwood shapes for the gym,
grown the way a clipped box really is:
- the shape is a signed distance field (ball, block, cone, cloud of balls), its surface softly lumpy (a hand-clipped shrub
  is never a perfect solid)
- thousands of sprigs grow out to that surface from inside: each a thin stem with opposite leaf pairs, every pair turned
  90 degrees from the one below (decussate, like real box), the leaves angled out from the stem, their blades facing out
- most sprigs end at the clipping line, some a little short (depth), a share tipped with lime new growth since the last clip
- leaves from a generated photo atlas (plants/maps/boxwood: deep green, mid, lime new growth, bronze winter tint, a
  yellowed tip), per-leaf brightness variation
- inside: a dark shadow layer 4 cm under the skin, so the gaps read deep and never see-through

    import gen_topiary; objs = gen_topiary.build(seed, (x, y, z), shape="ball", size=(0.6, 0.6, 0.55))

shape: ball | block | cone | cloud. size = the bounding box (x, y, z) in m. fresh = share of tips in new growth.
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "walls"))
from gen_greenwall import gen_fern_tube, gen_mosswall_obj, pothos_material  # noqa: E402

BOX = HERE / "maps" / "boxwood"


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _sdf(shape, size, rng):
    sx, sy, sz = (s / 2 for s in size)
    K = rng.normal(0, 1, (10, 3)) * 7.0; ph = rng.uniform(0, 6.3, 10)
    lump_a = 0.012 * min(size) / 0.6

    def lump(p):
        return lump_a * sum(np.sin(p @ K[i] + ph[i]) for i in range(10)) / math.sqrt(10)

    if shape == "ball":
        def f(p):
            q = p - np.array([0, 0, sz])
            return np.linalg.norm(q / np.array([sx, sy, sz]), axis=-1) * min(sx, sy, sz) - min(sx, sy, sz) + lump(p)
    elif shape == "block":
        rr = 0.06 * min(size) / 0.6 + 0.02
        def f(p):
            q = np.abs(p - np.array([0, 0, sz])) - np.array([sx, sy, sz]) + rr
            return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(-1), 0) - rr + lump(p)
    elif shape == "cone":
        ang = math.atan2(sx, 2 * sz)
        def f(p):
            r = np.linalg.norm(p[..., :2], axis=-1); z = p[..., 2]
            side = (r - sx * (1 - z / (2 * sz))) * math.cos(ang)
            return np.maximum(side + 0.035, -z) - 0.035 + lump(p)          # (rounded tip: a clipped point is never sharp)
    elif shape == "cloud":
        # cloud-pruned box (wolkenhaag): a wide low mound of overlapping domes, each clipped round on its own, a couple
        # riding higher in the middle; wider than tall
        n = int(rng.integers(7, 11)); C = []; R = []
        for i in range(n):
            r = rng.uniform(0.26, 0.4) * min(sx, sy) * 1.6
            for _ in range(60):
                a = rng.uniform(0, 2 * math.pi); d = math.sqrt(rng.uniform(0, 1))
                c = np.array([math.cos(a) * d * (sx - r * 0.8), math.sin(a) * d * (sy - r * 0.8), 0.0])
                c[2] = r * rng.uniform(0.75, 1.0) + (1 - d) * rng.uniform(0, 1) * max(0.0, 2 * sz - 2 * r)
                if not C or min(np.linalg.norm(c - np.array(C), axis=1) - np.array(R) - r) > -1.1 * r:
                    break
            C.append(c); R.append(r)
        C = np.array(C); R = np.array(R)
        def f(p):
            d = np.linalg.norm(p[..., None, :] - C, axis=-1) - R
            k = 0.03                                                   # smooth union: the clumps run into each other
            h = -k * np.log(np.sum(np.exp(-d / k), axis=-1))
            return h + lump(p)
    else:
        raise ValueError(shape)
    return f


def _surface(f, size, n, rng):
    """n points on f's zero surface (+ outward normals): uniform in the box, pushed onto the surface along the gradient"""
    sx, sy, sz = size
    p = rng.uniform([-sx / 2 * 1.1, -sy / 2 * 1.1, -0.02], [sx / 2 * 1.1, sy / 2 * 1.1, sz * 1.1], (n * 3, 3))
    e = 1e-3
    for _ in range(12):
        v = f(p)
        g = np.stack([(f(p + np.array(d)) - v) / e for d in ((e, 0, 0), (0, e, 0), (0, 0, e))], -1)
        p = p - _unit(g) * v[:, None]
    v = f(p)
    g = _unit(np.stack([(f(p + np.array(d)) - v) / e for d in ((e, 0, 0), (0, e, 0), (0, 0, e))], -1))
    ok = (np.abs(v) < 2e-3) & (p[:, 2] > 0.03)
    p, g = p[ok], g[ok]
    # thin to an even spacing (a grid hash: one per cell)
    cell = math.sqrt(4 * math.pi * (max(size) / 2) ** 2 / max(n, 1)) * 0.9
    key = np.floor(p / cell).astype(np.int64)
    _, idx = np.unique(key, axis=0, return_index=True)
    return p[idx], g[idx]


def build(seed, loc=(0, 0, 0), shape="ball", size=(0.6, 0.6, 0.55), density=3600, fresh=0.06, name="topiary"):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    f = _sdf(shape, size, rng)
    area = {"ball": 3.3, "block": 6.0, "cone": 2.6, "cloud": 4.2}[shape] * (sum(size) / 3) ** 2
    P, N = _surface(f, size, int(area * density), rng)
    atlas = json.loads((BOX / "atlas.json").read_text())
    old = ["leaf1", "leaf2", "leaf4", "leaf5"]; pold = np.array([0.6, 0.34, 0.03, 0.03])   # (more bronze / yellowed read as confetti)
    banks = {k: ([], [], [], []) for k in atlas}
    SV, SF, off = [], [], 0
    n_leaf = 0
    for p, n in zip(P, N):
        depth = rng.uniform(0.0, 0.006) if rng.random() < 0.85 else rng.uniform(0.01, 0.025)   # most at the clip line
        L = rng.uniform(0.035, 0.07)
        d = _unit(n + rng.normal(0, 0.35, 3))
        tip = p - n * depth
        base = tip - d * L
        nodes = int(rng.integers(3, 6))
        pts = np.array([base + d * L * t for t in np.linspace(0, 1, 5)])
        Vt, Ft = gen_fern_tube(pts, np.linspace(0.0011, 0.0006, 5), sides=4)
        SV.append(Vt); SF += [[i + off for i in fc] for fc in Ft]; off += len(Vt)
        side0 = _unit(np.cross(d, rng.normal(0, 1, 3)))
        new_tip = rng.random() < fresh
        for k in range(nodes):
            t = (k + 1) / nodes
            q = base + d * L * t * 0.97
            s = side0 if k % 2 == 0 else _unit(np.cross(d, side0))
            s = _unit(s + rng.normal(0, 0.12, 3))
            young = t > 0.7 and new_tip
            ln = rng.uniform(0.012, 0.018) if young else rng.uniform(0.014, 0.022)
            for sg in (1, -1):
                a = math.radians(rng.uniform(40, 62)) if not young else math.radians(rng.uniform(25, 40))
                ld = _unit(d * math.cos(a) + s * sg * math.sin(a))
                nm_ = n - ld * (n @ ld)
                nm_ = _unit(nm_ if np.linalg.norm(nm_) > 1e-3 else d)
                nm_ = _unit(nm_ + rng.normal(0, 0.25, 3))
                wv = _unit(np.cross(ld, nm_))
                key = "leaf3" if young else old[int(rng.choice(4, p=pold))]
                info = atlas[key]; w = ln * info["aspect"]
                V, F, U, A = banks[key]; o_ = len(V)
                for jv in range(3):
                    v_ = jv / 2
                    for ju in range(3):
                        u_ = ju / 2
                        x = (u_ - info["midrib_u"]) * w; y = (v_ - info["joint_v"]) * ln
                        z = -0.08 * (x / w * 2) ** 2 * w + 0.04 * v_ * ln            # cupped, the tip lifting a touch
                        V.append(q + ld * y + wv * x + nm_ * z); U.append((u_, v_))
                F += [[o_ + jv * 3 + ju, o_ + jv * 3 + ju + 1, o_ + (jv + 1) * 3 + ju + 1, o_ + (jv + 1) * 3 + ju] for jv in range(2) for ju in range(2)]
                A += [rng.uniform(-0.6, 0.4) - (0.9 if depth > 0.008 else 0)] * 9          # leaves deeper in are darker
                n_leaf += 1
    objs = []
    for key, (V, F, U, A) in banks.items():
        if F:
            m = pothos_material(key, BOX, rough=0.3, val=0.74, bump=0.00015)   # (bump scaled to a 2 cm leaf: 1 mm embossed them pale)
              # glossy like real box: a tight highlight, a dark body (satin 0.42-0.58 read milky)
            o = gen_mosswall_obj(f"{name}_{key}", np.array(V) + loc, F, m, U, {"var": A}); objs.append(o)
    stem = bpy.data.materials.get("box_stem") or bpy.data.materials.new("box_stem"); stem.use_nodes = True
    stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.09, 0.1, 0.035, 1)
    objs.append(gen_mosswall_obj(f"{name}_stems", np.concatenate(SV) + loc, SF, stem))
    # the shadow core: the shape shrunk 4 cm, near-black green, so the gaps read deep, never see-through
    core = bpy.data.materials.get("box_core") or bpy.data.materials.new("box_core"); core.use_nodes = True
    b = core.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.012, 0.02, 0.006, 1); b.inputs["Roughness"].default_value = 0.9
    if True:
        # small dark discs 4 cm under every other sprig: one dark layer that follows any shape (convex or not)
        V, F = [], []
        for p, n in zip(P[::2], N[::2]):
            c = p - n * 0.04
            if f(c[None])[0] > -0.03:                                     # (at a narrow tip the layer would poke out)
                continue
            a1 = _unit(np.cross(n, [0.3, 0.2, 1.0])); a2 = np.cross(n, a1); o_ = len(V)
            V += [c + (a1 * math.cos(t) + a2 * math.sin(t)) * 0.035 for t in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
            F.append(list(range(o_, o_ + 6)))
        objs.append(gen_mosswall_obj(f"{name}_core", np.array(V) + loc, F, core))
    for o in objs:
        o["tree"] = True
    print(f"topiary {name} {shape} {size}: {len(P)} sprigs, {n_leaf} leaves")
    return objs

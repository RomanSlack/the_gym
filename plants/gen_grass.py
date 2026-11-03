"""Ornamental grasses for the gym (Roman 2026-11-02: "more plants ... bushes"): soft movement next to the clipped box and
the pines. Blades and plumes are too fine for photo textures to matter, so they are built in geometry (like the juniper's
scale shoots), every blade its own arc:
- pennisetum (fountain grass): a dense arching mound of narrow blades, buff-pink bottlebrush plumes nodding out over it
- miscanthus: tall upright clump, wide blades with the white midrib, arching at the top, silver feathery plumes above
- stipa (feather grass): a fine hair-like tuft, green at the base turning blonde, swept one way like it's in the wind
Every blade: a ribbon from the crown, out and up, bending over under its own weight (more the longer it is), twisting a
little, tapering to a point; colours green -> straw toward the tips; the older outer blades lower and paler.

    import gen_grass; objs = gen_grass.build(seed, (x, y, z), kind="pennisetum", size=0.8)
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gen_bonsai import _obj  # noqa: E402

KINDS = {
    #             blades, length (m),  width (m),     lift, droop, colours (base, mid, tip),                          plumes
    "pennisetum": (520, (0.35, 0.65), (0.003, 0.005), 0.75, 1.25, ((0.06, 0.12, 0.03), (0.12, 0.22, 0.06), (0.32, 0.3, 0.14)), "brush"),
    "miscanthus": (300, (0.8, 1.35), (0.007, 0.011), 1.3, 1.5, ((0.05, 0.11, 0.03), (0.1, 0.2, 0.06), (0.28, 0.3, 0.14)), "feather"),
    "stipa":      (900, (0.3, 0.55), (0.0009, 0.0014), 1.0, 0.9, ((0.12, 0.2, 0.05), (0.32, 0.36, 0.14), (0.62, 0.52, 0.3)), "none"),
}


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def material():
    m = bpy.data.materials.get("grass_blade")
    if m:
        return m
    m = bpy.data.materials.new("grass_blade"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    ca = N.new("ShaderNodeVertexColor"); ca.layer_name = "col"
    L.new(ca.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.5; b.inputs["Specular IOR Level"].default_value = 0.35
    # light through the blades (backlit grass glows)
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(ca.outputs["Color"], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.25
    out = N["Material Output"]
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])
    return m


def _ribbon(V, F, C, pts, width, cols, rng, midrib=False, twist=0.0):
    """a tapered blade along pts; cols per point; a fold along the middle (V-shaped blade) catches the light"""
    n = len(pts)
    T = _unit(np.gradient(pts, axis=0))
    side = _unit(np.cross(T, np.array([0, 0, 1.0])) + rng.normal(0, 0.05, 3))
    o_ = len(V)
    for k in range(n):
        s = k / (n - 1)
        w = width * (1 - s ** 2.2) + 0.0002
        a = twist * s
        sd = side[k] * math.cos(a) + np.cross(T[k], side[k]) * math.sin(a)
        up = np.cross(sd, T[k])
        c = cols[k]
        V += [pts[k] - sd * w, pts[k] + up * w * 0.25, pts[k] + sd * w]
        C += [c * 0.85, c * (1.25 if midrib else 1.05), c * 0.85]
    for k in range(n - 1):
        b = o_ + 3 * k
        F += [[b, b + 1, b + 4, b + 3], [b + 1, b + 2, b + 5, b + 4]]


def build(seed, loc=(0, 0, 0), kind="pennisetum", size=1.0, name=None):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    name = name or kind
    nb, (l0, l1), (w0, w1), lift, droop, (cb, cm, ct), plume = KINDS[kind]
    cb, cm, ct = map(np.array, (cb, cm, ct))
    V, F, C = [], [], []
    wind = rng.uniform(0, 2 * math.pi); wv = np.array([math.cos(wind), math.sin(wind), 0.0])
    crown_r = 0.06 * size
    for i in range(int(nb * size)):
        a = rng.uniform(0, 2 * math.pi)
        r = crown_r * math.sqrt(rng.uniform(0, 1))
        base = np.array([math.cos(a) * r, math.sin(a) * r, 0.0])
        # outer blades lean out more and lower; inner ones stand up
        outer = r / crown_r
        L = rng.uniform(l0, l1) * size * (1.05 - 0.3 * outer)
        tilt = rng.uniform(0.05, 0.35) + 0.5 * outer
        d = _unit(np.array([math.cos(a) * tilt, math.sin(a) * tilt, lift]))
        n = 14
        pts = [base]
        for k in range(n):
            t = (k + 1) / n
            bend = droop * t * (L / l1) * 1.4
            d = _unit(d + np.array([0, 0, -bend / n * 2.4]) + (wv * 0.08 if kind == "stipa" else 0) + rng.normal(0, 0.02, 3))
            pts.append(pts[-1] + d * L / n)
        pts = np.array(pts)
        age = rng.uniform(0, 1) * (0.4 + 0.6 * outer)                    # older blades outside: paler, strawier
        tint = 1 + rng.normal(0, 0.08)
        cols = []
        for k in range(len(pts)):
            s = k / (len(pts) - 1)
            c = cb * (1 - s) + cm * s if s < 0.6 else cm * (1 - (s - 0.6) / 0.4) + ct * ((s - 0.6) / 0.4) * (0.6 + 0.4 * age)
            cols.append(c * (1 - age) + ct * age * 0.9 if s > 0.3 else c)
        cols = np.array(cols) * tint * (0.75 + 0.25 * min(1, pts[:, 2].mean() / (l0 * size)))      # inside/low: shaded
        _ribbon(V, F, C, pts, rng.uniform(w0, w1), cols, rng, midrib=kind == "miscanthus", twist=rng.normal(0, 1.2))
    # ---- plumes
    n_pl = {"brush": int(46 * size), "feather": int(22 * size), "none": 0}[plume]
    for i in range(n_pl):
        a = rng.uniform(0, 2 * math.pi)
        tilt = rng.uniform(0.2, 0.55) if plume == "brush" else rng.uniform(0.05, 0.25)
        d = _unit(np.array([math.cos(a) * tilt, math.sin(a) * tilt, 1.0]))
        Lst = (rng.uniform(0.55, 0.8) if plume == "brush" else rng.uniform(1.25, 1.6)) * size
        pts = [np.zeros(3)]
        for k in range(16):
            t = (k + 1) / 16
            d = _unit(d + np.array([math.cos(a), math.sin(a), 0]) * (0.05 if plume == "brush" else 0.02) * t + np.array([0, 0, -0.06 * t if plume == "brush" else 0]))
            pts.append(pts[-1] + d * Lst / 16)
        pts = np.array(pts)
        _ribbon(V, F, C, pts, 0.0012, np.tile(cm * 1.2, (len(pts), 1)), rng)              # the culm
        # the head: the top 25 % (brush) / 30 % (feather) of the culm carries bristles / silky branches
        k0 = int(len(pts) * (0.75 if plume == "brush" else 0.68))
        head = pts[k0:]
        hc = np.array([0.52, 0.42, 0.34]) if plume == "brush" else np.array([0.62, 0.57, 0.52])
        for _ in range(520 if plume == "brush" else 70):
            j = int(rng.integers(len(head) - 1)); f = rng.uniform(0, 1)
            p0 = head[j] + (head[j + 1] - head[j]) * f
            ax = _unit(head[j + 1] - head[j])
            out = _unit(np.cross(ax, rng.normal(0, 1, 3)))
            if plume == "brush":                                            # bristles: short, stiff, angled forward
                bl = rng.uniform(0.018, 0.03) * size
                q = np.array([p0, p0 + _unit(out + ax * 0.6) * bl * 0.5, p0 + _unit(out + ax * 0.9) * bl])
                _ribbon(V, F, C, q, 0.0008, np.tile(hc * rng.uniform(0.85, 1.15), (3, 1)), rng)
            else:                                                           # feather: silky branches arching up + out
                bl = rng.uniform(0.06, 0.13) * size
                q = np.array([p0 + (_unit(out * 0.45 + ax) * bl * t + np.array([0, 0, -0.02 * t * t])) for t in np.linspace(0, 1, 5)])
                _ribbon(V, F, C, q, 0.0022, np.tile(hc * rng.uniform(0.9, 1.1), (5, 1)), rng, twist=1.0)
    o = _obj(f"{name}_{seed}", np.array(V) + loc, F, material(), colors=np.array(C))
    o["tree"] = True
    print(f"grass {kind} {seed}: {int(nb * size)} blades, {n_pl} plumes, {len(F)} faces")
    return [o]

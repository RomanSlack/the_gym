"""Snake plant (Dracaena / Sansevieria trifasciata) generator: one seed = one plant (plants/GOAL.md). From the reference sheet
(out/refs_snake_v001.jpg):
- 2-5 rosettes (pups) in the pot, each 3-8 stiff sword leaves spiralling from its base; the newest in the middle upright,
  the older ones leaning out 10-30 deg; 0.4-1.05 m long
- a leaf: lanceolate, cupped into a channel (deepest at the clasping base), a slow twist, arching out a little; thick (~4 mm)
- the leaves are atlas images (maps/snake: real-looking leaf photos, build_leaf_atlas.py), the mesh follows each leaf's own
  outline so its edge is real geometry (the yellow 'Laurentii' margin shows on the thickness too); one variety per plant
- no leaf through another, the pot or the floor (the monstera's rule: tries placements, keeps a clear one)

    import gen_snake; objs = gen_snake.build(seed, (x, y, z_soil), pot_r, pot_h)
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ATLAS = HERE / "maps" / "snake"
FRAME = {"pot_scale": 1.15, "hero": ((0.5, -2.8, 1.35), (0, 0, 0.8), 40), "trio": ((0, -5.8, 1.55), (0, 0, 0.8), 36), "spacing": 1.3}


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


class Clash:
    """voxel occupancy (the monstera's clipping rule, shared): mark() what is placed, hits() for a candidate"""

    def __init__(self, vox=0.008):
        self.vox, self.K, self.occ = vox, 1 << 12, np.array([], np.int64)

    def _q(self, P):
        return np.floor(np.asarray(P) / self.vox).astype(np.int64) + self.K // 2

    def hits(self, P):
        if not len(self.occ):
            return 0
        q = self._q(P)
        return int(np.isin(q[:, 0] + q[:, 1] * self.K + q[:, 2] * self.K * self.K, self.occ).sum())

    def mark(self, P):
        q = self._q(P)
        ks = [(q[:, 0] + dx) + (q[:, 1] + dy) * self.K + (q[:, 2] + dz) * self.K * self.K
              for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]
        self.occ = np.union1d(self.occ, np.unique(np.concatenate(ks)))

    def pot(self, pot_r, pot_h, top=0.07):
        th = np.linspace(0, 2 * math.pi, 140)
        wall = [np.stack([(pot_r + 0.02) * np.cos(th), (pot_r + 0.02) * np.sin(th), np.full_like(th, z)], 1) for z in np.arange(-pot_h, top, 0.01)]
        g = np.linspace(-1.2, 1.2, 200); gx, gy = np.meshgrid(g, g)
        self.mark(np.concatenate(wall + [np.stack([gx.ravel(), gy.ravel(), np.full(gx.size, -pot_h)], 1)]))


_MATS, _ALPHA = {}, {}


def material(name):
    """satin wax over the leaf image (no clear coat: the monstera lesson), both sides patterned, the back a touch paler"""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    col = N.new("ShaderNodeTexImage"); col.image = bpy.data.images.load(str(ATLAS / f"{name}_col.png"), check_existing=True)
    col.interpolation = "Cubic"
    bmp = N.new("ShaderNodeTexImage"); bmp.image = bpy.data.images.load(str(ATLAS / f"{name}_bump.png"), check_existing=True)
    bmp.image.colorspace_settings.name = "Non-Color"
    oi = N.new("ShaderNodeObjectInfo"); geo = N.new("ShaderNodeNewGeometry")

    def mad(x, mul, add):
        n = N.new("ShaderNodeMath"); n.operation = "MULTIPLY_ADD"; n.inputs[1].default_value = mul; n.inputs[2].default_value = add
        L.new(x, n.inputs[0]); return n.outputs[0]
    var = N.new("ShaderNodeHueSaturation")
    L.new(col.outputs["Color"], var.inputs["Color"])
    L.new(mad(oi.outputs["Random"], 0.02, 0.49), var.inputs["Hue"])
    L.new(mad(oi.outputs["Random"], -0.1, 0.68), var.inputs["Value"])          # (v2 read washed-out next to the refs)
    var.inputs["Saturation"].default_value = 1.12
    back = N.new("ShaderNodeHueSaturation"); back.inputs["Value"].default_value = 1.12; back.inputs["Saturation"].default_value = 0.85
    L.new(var.outputs[0], back.inputs["Color"])
    base = N.new("ShaderNodeMix"); base.data_type = "RGBA"
    L.new(geo.outputs["Backfacing"], base.inputs[0]); L.new(var.outputs[0], base.inputs[6]); L.new(back.outputs[0], base.inputs[7])
    mic = N.new("ShaderNodeTexNoise"); mic.inputs["Scale"].default_value = 1100; mic.inputs["Detail"].default_value = 2
    hh = N.new("ShaderNodeMath"); hh.operation = "MULTIPLY_ADD"; hh.inputs[1].default_value = 0.04
    L.new(mic.outputs[0], hh.inputs[0]); L.new(bmp.outputs["Color"], hh.inputs[2])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.3; bump.inputs["Distance"].default_value = 0.0012
    L.new(hh.outputs[0], bump.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(base.outputs[2], pb.inputs["Base Color"])
    L.new(mad(bmp.outputs["Color"], -0.15, 0.5), pb.inputs["Roughness"])
    pb.inputs["Specular IOR Level"].default_value = 0.38
    L.new(bump.outputs[0], pb.inputs["Normal"])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(col.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(pb.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def _alpha(name):
    if name not in _ALPHA:
        im = bpy.data.images.load(str(ATLAS / f"{name}_col.png"), check_existing=True)
        w, h = im.size
        px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
        _ALPHA[name] = px.reshape(h, w, 4)[..., 3]                     # row 0 = the bottom = the leaf base
    return _ALPHA[name]


def leaf(name, info, L, base, D0, N0, rng, nv=90, nu=12):
    """the leaf sheet following the image's outline: row v from base (0) to tip (1), across from its left edge to its right"""
    A = _alpha(name)
    h, w = A.shape
    Wf = L * info["aspect"] * 0.72                                   # (v1 at the image's own aspect read squat, like an agave)
    rows = np.linspace(0.0, 1.0, nv)
    edges = []
    for v in rows:
        r = A[min(int(v * (h - 1)), h - 1)] > 0.5
        idx = np.nonzero(r)[0]
        edges.append((idx.min() / (w - 1), idx.max() / (w - 1)) if len(idx) else None)
    last = max(i for i, e in enumerate(edges) if e)
    first = min(i for i, e in enumerate(edges) if e)
    tip_u = sum(edges[last]) / 2
    twist = rng.normal(0, 0.5)
    cup = rng.uniform(0.16, 0.3)
    arch = rng.uniform(0.05, 0.3)
    V, UV, F = [], [], []
    p, d, n = base.copy(), D0.copy(), N0.copy()
    ds = L / (nv - 1)
    keep = list(range(first, last + 1))
    for jj, j in enumerate(keep):
        v = rows[j]
        if jj:
            # arch away from the concave side (outward), slowly; twist about the spine
            d = _unit(d - n * arch * ds * (0.5 + v))
            n = _unit(n - d * (n @ d))
        tw = twist * v
        s_ = _unit(np.cross(d, n))
        s2 = s_ * math.cos(tw) + n * math.sin(tw)
        n2 = _unit(np.cross(s2, d))
        ul, ur = edges[j]
        if j == last:
            ul = ur = tip_u
        for i in range(nu + 1):
            u = ul + (ur - ul) * i / nu
            x = (u - info.get("midrib_u", 0.5)) * Wf
            hw = max((ur - ul) * Wf / 2, 1e-4)
            z = cup * (abs(x) / hw) ** 2 * hw * (1.6 - 0.8 * v)          # the channel, deepest at the clasping base
            V.append(p + s2 * x + n2 * z)
            UV.append((u, v))
        p = p + d * ds
    R = nu + 1
    for j in range(len(keep) - 1):
        for i in range(nu):
            F.append([j * R + i, j * R + i + 1, (j + 1) * R + i + 1, (j + 1) * R + i])
    return np.array(V), F, UV


def build(seed, loc=(0, 0, 0), pot_r=0.2, pot_h=0.3):
    atlas = json.loads((ATLAS / "atlas.json").read_text())
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    laurentii = rng.random() < 0.45
    LAUR = {"snakel1", "snakel2", "snaket3"}                            # (snaket3 came out with the golden margins too)
    names = [k for k in atlas if (k in LAUR) == laurentii]
    clash = Clash(); clash.pot(pot_r, pot_h)
    n_ros = int(rng.integers(2, 6))
    objs, dry_used = [], False
    for r_ in range(n_ros):
        ang = rng.uniform(0, 2 * math.pi); rad = rng.uniform(pot_r * 0.3, pot_r * 0.7) * (0.3 if r_ == 0 else 1)
        c = np.array([rad * math.cos(ang), rad * math.sin(ang), 0.0])
        n_leaf = min(int(rng.integers(3, 8)), 20 - len(objs))            # (35 in one pot couldn't fit without crossing)
        if n_leaf < 2:
            break
        scale = rng.uniform(0.6, 1.0) if r_ else 1.0                    # the pups smaller than the mother rosette
        az0 = rng.uniform(0, 2 * math.pi)
        for k in range(n_leaf):
            age = 1 - k / max(n_leaf - 1, 1)                             # 1 oldest (outside) -> 0 newest (centre)
            name = names[int(rng.integers(len(names)))]
            while name == "snaket4" and dry_used:                          # the dry-tipped old leaf: once per plant
                name = names[int(rng.integers(len(names)))]
            dry_used |= name == "snaket4"
            L = scale * np.interp(age, [0, 0.3, 1], [0.7, 1.15, 0.95]) * rng.uniform(0.85, 1.12)
            best = None
            for attempt in range(45):
                az = az0 + k * math.radians(137.5) + rng.normal(0, 0.2 + 0.05 * attempt)
                out = np.array([math.cos(az), math.sin(az), 0.0])
                lean = math.radians(min(np.interp(age, [0, 1], [2, 13]) + abs(rng.normal(0, 2 + attempt * 0.25)), 20))   # (capped: a leaf at 40 deg read broken)
                D0 = _unit(np.array([0, 0, 1.0]) * math.cos(lean) + out * math.sin(lean))
                N0 = _unit(-out + rng.normal(0, 0.6, 3)); N0 = _unit(N0 - D0 * (N0 @ D0))    # the channel faces the rosette, roughly
                base = c + out * 0.012 * age + np.array([0, 0, -0.02])
                V, F, UV = leaf(name, atlas[name], L, base, D0, N0, rng)
                hits = clash.hits(V[len(V) // 3:])                       # (the clasping lower thirds sit together, like the plant's)
                if best is None or hits < best[0]:
                    best = (hits, V, F, UV)
                if hits == 0:
                    break
            hits, V, F, UV = best
            clash.mark(V[len(V) // 3:])
            me = bpy.data.meshes.new(f"snake_{seed}_{r_}_{k}")
            me.from_pydata((V + loc).tolist(), [], F)
            ul = me.uv_layers.new(name="UVMap")
            ul.data.foreach_set("uv", np.array([UV[i] for f in F for i in f], np.float32).ravel())
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
            o = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(o)
            o.data.materials.append(material(name))
            so = o.modifiers.new("thick", "SOLIDIFY"); so.thickness = 0.004; so.offset = 0.0
            o["clash"] = hits
            objs.append(o)
    print(f"snake {seed}: {'Laurentii' if laurentii else 'green'}, {n_ros} rosettes, {len(objs)} leaves; "
          f"touching: {sum(1 for o in objs if o['clash'])}")
    return objs

"""Monstera deliciosa generator: one seed = one plant (plants/GOAL.md). Every number from the reference sheet
(out/refs_monstera_v001.jpg):
- 7-14 leaves on long petioles (0.35-0.8 m) from a short thick stem, spiralling round it; newest smallest and in the middle
- a leaf: ovate-cordate, about as wide as long (0.2-0.55 m), the petiole joining at the basal sinus; mature leaves slit
  from the margin 30-70 % of the way in between pale lateral veins, an inner row of oval holes by the midrib; young
  leaves lime green and entire; deep glossy green, the panels between the veins slightly puffed (a relief map)
- petiole: smooth, pale green, a winged sheath at its base, a swollen kink (geniculum) under the blade
- brown aerial roots from the stem nodes down into the soil
Each leaf gets its own images (work/monstera/<seed>_<i>_col.png: colour + alpha cut-out, _bump.png: relief), so the
slits and holes are crisp at any distance; the mesh is a smooth bent sheet under them.

    import gen_monstera; objs = gen_monstera.build(seed, (x, y, z_soil), pot_r)
"""
import math
from pathlib import Path

import bpy
import numpy as np

WORK = Path(__file__).resolve().parent / "work" / "monstera"
TEX = 1024


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


def _blur(a, s):
    """separable gaussian (numpy only: Blender's python has no scipy/cv2)"""
    if s <= 0:
        return a
    r = int(3 * s)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode="edge"), k, "valid"), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode="edge"), k, "valid"), 1, a)


# ------------------------------------------------------------------------------------------------------------ leaf images
class Leaf:
    """the 2D leaf (metres, midrib along +y from the petiole joint at 0 to the tip at L, basal lobes down to -0.16 L)"""

    def __init__(self, L, maturity, rng):
        self.L, self.m, self.rng = L, maturity, rng
        self.W = L * rng.uniform(0.44, 0.5)                       # half-width at the widest
        self.y0, self.y1 = -0.16 * L, L
        nv = int(round(np.interp(maturity, [0, 1], [4, 7]) + rng.integers(-1, 2)))   # (9 read as a palm frond)
        self.a = math.radians(rng.uniform(52, 62))                 # lateral veins' angle off the midrib (toward the tip)
        ys = np.linspace(0.04, 0.86, nv) * L
        self.veins = {sd: ys + rng.normal(0, 0.012, nv) * L for sd in (-1, 1)}
        self.slit = {sd: [] for sd in (-1, 1)}                     # (phi between two veins, depth fraction, width)
        self.holes = {sd: [] for sd in (-1, 1)}
        if maturity > 0.3:
            for sd in (-1, 1):
                v = np.sort(self.veins[sd])
                for k in range(len(v) - 1):
                    if rng.random() < np.interp(maturity, [0.3, 0.6, 1], [0.35, 0.8, 0.95]):
                        depth = np.interp(maturity, [0.3, 1], [0.18, 0.52]) * rng.uniform(0.75, 1.15)
                        self.slit[sd].append(((v[k] + v[k + 1]) / 2, min(depth, 0.66), rng.uniform(0.008, 0.016) * L / 0.45))
                    if maturity > 0.6 and rng.random() < 0.7:
                        self.holes[sd].append(((v[k] + v[k + 1]) / 2 + rng.normal(0, 0.004) * L, rng.uniform(0.22, 0.38),
                                               rng.uniform(0.03, 0.065) * L / 0.45, rng.uniform(0.009, 0.014) * L / 0.45))

    def halfwidth(self, y):
        t = np.clip((y - self.y0) / (self.y1 - self.y0), 0, 1)
        w = self.W * np.clip(np.sin(np.pi * t ** 0.95), 0, 1) ** 0.6     # widest ~40 % up (v1 widest at the base: a lily pad)
        return w * np.clip((1 - t) / 0.16, 0, 1) ** 0.75             # tapering to an acute tip

    def phi(self, ax, y):
        """the midrib point a lateral vein through (ax, y) leaves from (veins curve a little toward the tip)"""
        return y - ax / math.tan(self.a) - 0.25 * ax ** 2 / self.L

    def images(self, path):
        S = TEX
        xs = np.linspace(-self.W * 1.04, self.W * 1.04, S)
        ys = np.linspace(self.y0 - 0.01, self.y1 + 0.01, S)
        X, Y = np.meshgrid(xs, ys)
        ax = np.abs(X); sd = np.sign(X)
        hw = self.halfwidth(Y)
        inside = ax < hw
        sinus = (Y < 0.02 * self.L) & (ax < 0.07 * self.L * np.clip((0.02 * self.L - Y) / (0.18 * self.L), 0, 1) ** 0.5 + 0.004)
        inside &= ~sinus
        ph = self.phi(ax, Y)
        sa = math.sin(self.a)
        cut = np.zeros_like(inside)
        for s_ in (-1, 1):
            on = sd == s_
            for m, depth, w in self.slit[s_]:
                inner = (1 - depth) * hw
                dperp = (ph - m) * sa
                dax = np.maximum(inner - ax, 0) / sa
                wid = w * (0.55 + 0.45 * np.clip((ax - inner) / (hw - inner + 1e-6), 0, 1))     # wider toward the margin
                cut |= on & (np.hypot(dperp, dax) < wid)
            for m, hx, ln, wd in self.holes[s_]:
                c_ax = hx * self.W
                along = (ax - c_ax) / sa
                dperp = (ph - m) * sa
                cut |= on & ((along / (ln / 2)) ** 2 + (dperp / (wd / 2)) ** 2 < 1)
        alpha = (inside & ~cut).astype(np.float32)
        # veins: the midrib (wide at the base), the laterals, fine veinlets between them
        mid_w = np.interp(Y, [0, self.L], [0.011, 0.0025]) * self.L / 0.45
        midrib = np.clip(1 - ax / mid_w, 0, 1) ** 0.7
        lat = np.zeros_like(X)
        for s_ in (-1, 1):
            for v in self.veins[s_]:
                lat = np.maximum(lat, (sd == s_) * np.clip(1 - np.abs((ph - v) * sa) / (0.0022 * self.L / 0.45), 0, 1) * (Y > -0.05 * self.L))
        fine = 0.5 + 0.5 * np.cos((ph * sa) / (0.0035 * self.L / 0.45) * 2 * np.pi)
        fine = np.clip((fine - 0.86) / 0.14, 0, 1) * 0.12
        veins = np.maximum(np.maximum(midrib, lat * (ax > mid_w * 0.6)), fine)
        # colour: young lime -> mature deep green, broad mottling, paler veins, a slightly paler margin band
        rng = self.rng
        young = np.array([0.22, 0.5, 0.06]); old = np.array([0.028, 0.095, 0.016])
        base = young * (1 - self.m) + old * self.m
        mott = _blur(rng.normal(0, 1, (S // 8, S // 8)), 2.0)
        mott = np.kron(mott, np.ones((8, 8)))[:S, :S]
        mott = (mott - mott.mean()) / (mott.std() + 1e-6)
        col = base[None, None] * (1 + 0.04 * mott[..., None])
        vein_c = np.array([0.2, 0.36, 0.08]) if self.m > 0.4 else np.array([0.42, 0.66, 0.16])
        col = col * (1 - veins[..., None] * 0.55) + vein_c[None, None] * veins[..., None] * 0.55
        edge = np.clip(1 - (hw - ax) / 0.006, 0, 1) * inside
        col = col * (1 - 0.25 * edge[..., None]) + np.array([0.3, 0.42, 0.12]) * 0.25 * edge[..., None]
        # relief: the panels between the laterals puff up, veins sit in grooves, the midrib a groove on top
        dist_v = np.full_like(X, 1e9)
        for s_ in (-1, 1):
            for v in self.veins[s_]:
                dist_v = np.minimum(dist_v, np.where(sd == s_, np.abs((ph - v) * sa), 1e9))
        gap = (self.veins[1].max() - self.veins[1].min()) / max(len(self.veins[1]) - 1, 1) * sa
        panel = np.sin(np.clip(dist_v / (gap / 2), 0, 1) * np.pi / 2)
        bump = 0.6 * panel * np.clip(ax / (0.15 * self.W), 0, 1) - 0.5 * midrib - 0.2 * lat
        bump = _blur(bump, 1.5)
        rgba = np.dstack([np.clip(col, 0, 1) ** (1 / 2.2), alpha])            # stored sRGB
        path.parent.mkdir(parents=True, exist_ok=True)
        _save(path.with_name(path.name + "_col.png"), rgba)
        _save(path.with_name(path.name + "_bump.png"), np.dstack([(bump - bump.min()) / (np.ptp(bump) + 1e-6)] * 3 + [np.ones_like(bump)]))
        self.alpha = alpha
        return xs, ys


def _save(p, rgba):
    S = rgba.shape[0]
    im = bpy.data.images.new(p.stem, S, S, alpha=True)
    im.pixels.foreach_set(rgba.astype(np.float32).ravel())          # (row 0 = the leaf base = v 0: no flip; v1 flipped it)
    im.filepath_raw = str(p); im.file_format = "PNG"; im.save()
    bpy.data.images.remove(im)


# ------------------------------------------------------------------------------------------------------------ geometry
def tube(pts, radii, sides=12):
    V, F = [], []
    n = len(pts)
    for k in range(n):
        d = _unit(pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)])
        a1 = _unit(np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.98 else np.cross(d, [1.0, 0, 0]))
        a2 = np.cross(d, a1)
        for j in range(sides):
            t = 2 * math.pi * j / sides
            V.append(pts[k] + (a1 * math.cos(t) + a2 * math.sin(t)) * radii[k])
    for k in range(n - 1):
        for j in range(sides):
            a_, b_ = k * sides + j, k * sides + (j + 1) % sides
            F.append([a_, a_ + sides, b_ + sides, b_])
    F.append(list(range(sides))[::-1]); F.append([(n - 1) * sides + j for j in range(sides)])   # capped ends
    return np.array(V), F


def mesh_obj(name, V, F, mat, uv=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.asarray(V).tolist(), [], F)
    if uv is not None:
        ul = me.uv_layers.new(name="UVMap")
        ul.data.foreach_set("uv", np.array([uv[i] for f in F for i in f], np.float32).ravel())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def leaf_mesh(lf, xs, ys, P, D, N, rng):
    """the leaf sheet: (x across, y along the midrib) -> the joint P, midrib heading D, blade up N; the midrib arches down,
    the halves lift in a shallow V near the midrib and roll down at the margins, a slow twist"""
    nu, nv = 90, 110                                                 # dense enough for the corrugation
    gx = np.linspace(xs[0], xs[-1], nu); gy = np.linspace(ys[0], ys[-1], nv)
    S = np.cross(D, N)
    droop = rng.uniform(1.0, 2.2) / lf.L
    vfold = math.radians(rng.uniform(4, 14)); roll = rng.uniform(0.05, 0.16)
    twist = rng.normal(0, 0.25)
    # the bent midrib, integrated in small steps
    pos = np.zeros((nv, 3)); dirs = np.zeros((nv, 3)); ups = np.zeros((nv, 3))
    p = P + D * gy[0]                                               # (the basal lobes reach back past the joint)
    for j, y in enumerate(gy):
        ang = droop * max(y, 0) ** 1.4 * lf.L ** 0.4
        d = _unit(D * math.cos(ang) - N * math.sin(ang))
        n = _unit(N * math.cos(ang) + D * math.sin(ang))
        tw = twist * max(y, 0) / lf.L
        sv = _unit(S * math.cos(tw) + n * math.sin(tw))
        n = _unit(np.cross(sv, d))
        if j:
            p = p + d * (gy[j] - gy[j - 1])
        pos[j], dirs[j], ups[j] = p, sv, n
    # the corrugation: each panel between two lateral veins bulges up, the veins sit in the folds (the references); the
    # margins wave
    sa = math.sin(lf.a)
    pleat = rng.uniform(0.006, 0.012) * lf.L / 0.45
    wave = rng.uniform(0.004, 0.01) * lf.L / 0.45
    V, UV = [], []
    for j in range(nv):
        for i, x in enumerate(gx):
            ax = abs(x)
            z = ax * math.tan(vfold) * math.exp(-ax / (0.3 * lf.W)) - roll * (ax / lf.W) ** 2 * lf.W
            vs = np.sort(lf.veins[1 if x >= 0 else -1])
            ph = lf.phi(ax, gy[j])
            k = np.searchsorted(vs, ph)
            if 0 < k < len(vs):
                f_ = (ph - vs[k - 1]) / (vs[k] - vs[k - 1])
                z += pleat * (1 - math.cos(2 * math.pi * f_)) / 2 * min(ax / (0.12 * lf.W), 1)   # smooth valleys (a crease zippered)
            z += wave * math.sin(gy[j] / lf.L * 9 + (1.3 if x >= 0 else 0)) * (ax / lf.W) ** 2
            V.append(pos[j] + dirs[j] * x + ups[j] * z)
            UV.append(((x - xs[0]) / (xs[-1] - xs[0]), (gy[j] - ys[0]) / (ys[-1] - ys[0])))
    # keep only quads that touch the leaf (the alpha cut does the exact outline)
    A = lf.alpha
    S_ = A.shape[0]
    def a_at(u, v):
        return A[min(int(v * (S_ - 1)), S_ - 1), min(int(u * (S_ - 1)), S_ - 1)]
    F = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            q = [j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i]
            us = [UV[k] for k in q]
            cu, cv = sum(u for u, _ in us) / 4, sum(v for _, v in us) / 4
            hw = lf.halfwidth(ys[0] + cv * (ys[-1] - ys[0]))
            xx = xs[0] + cu * (xs[-1] - xs[0])
            if abs(xx) < hw + (xs[-1] - xs[0]) / nu * 1.5:
                F.append(q)
    return V, F, UV


def build(seed, loc=(0, 0, 0), pot_r=0.22, leaf_mat=None, stem_mat=None, root_mat=None):
    """returns the objects (stem + petioles + roots in one, each leaf its own with its own images)"""
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    n_leaf = int(rng.integers(7, 15))
    stem_h = rng.uniform(0.06, 0.14)
    lean = _unit(np.array([rng.normal(0, 0.25), rng.normal(0, 0.25), 1.0]))
    stem_pts = np.array([lean * stem_h * t for t in np.linspace(0, 1, 12)])
    TV, TF = [], []

    def add(v, f):
        off = sum(len(x) for x in TV)
        TV.append(v); TF.extend([[i + off for i in q] for q in f])

    v, f = tube(stem_pts, np.linspace(0.02, 0.012, 12), 14); add(v, f)          # (hidden in the sheaths)
    leaves = []
    golden = math.radians(137.5)
    az0 = rng.uniform(0, 2 * math.pi)
    for i in range(n_leaf):
        age = i / max(n_leaf - 1, 1)                                 # 0 oldest (low, outside) -> 1 newest
        maturity = np.clip(1 - age * 0.9 + rng.normal(0, 0.12), 0, 1)
        node = stem_pts[min(int(age * 11), 11)] + rng.normal(0, 0.004, 3)
        az = az0 + i * golden + rng.normal(0, 0.25)
        out = np.array([math.cos(az), math.sin(az), 0.0])
        tilt = math.radians(np.interp(age, [0, 1], [30, 6]) + rng.normal(0, 6))
        plen = np.interp(maturity, [0, 1], [0.42, 0.88]) * rng.uniform(0.85, 1.15)   # a 1-1.3 m plant (v3 squat)
        # the petiole: a gentle arc out and up
        d0 = _unit(out * math.sin(tilt) + np.array([0, 0, 1.0]) * math.cos(tilt))
        bend = rng.uniform(0.3, 0.7)                                  # arching out (v1: straight spokes)
        pts = []
        p = node.copy(); d = d0.copy()
        for k in range(40):
            p = p + d * plen / 40
            d = _unit(d + out * bend / 40 * 1.2 - np.array([0, 0, 1.0]) * bend / 40 * 0.4)
            pts.append(p.copy())
        pts = np.array([node] + pts)
        r = np.interp(np.linspace(0, 1, len(pts)), [0, 0.18, 0.3, 0.9, 1], [0.02, 0.016, 0.0095, 0.0082, 0.0105]) * (0.65 + 0.35 * maturity)   # (v4: thin sticks)
        v, f = tube(pts, r, 12); add(v, f)                            # sheath at the base, the swollen geniculum at the top
        L = np.interp(maturity, [0, 1], [0.2, 0.56]) * rng.uniform(0.88, 1.12)
        lf = Leaf(L, maturity, rng)
        # the blade hangs from the geniculum: midrib out and down, the blade facing out and up (v1 held them flat: lily pads)
        pitch = math.radians(np.interp(maturity, [0, 1], [-5, -42]) + rng.normal(0, 10))
        D = _unit(out * math.cos(pitch) + np.array([0, 0, 1.0]) * math.sin(pitch))
        D = _unit(D + rng.normal(0, 0.12, 3))
        N = _unit(np.array([0, 0, 1.0]) - D * D[2])
        N = _unit(N + out * rng.uniform(0.1, 0.5))
        N = _unit(N - D * (N @ D))
        path = WORK / f"{seed}_{i}"
        xs, ys = lf.images(path)
        LV, LF, LUV = leaf_mesh(lf, xs, ys, pts[-1] + D * 0.006, D, N, rng)
        mat = leaf_mat(path) if leaf_mat else None
        o = mesh_obj(f"monstera_{seed}_leaf{i}", np.array(LV) + loc, LF, mat, LUV)
        leaves.append(o)
    RV, RF = [], []
    for _ in range(int(rng.integers(2, 5))):                           # aerial roots: from the stem nodes down into the soil
        k = int(rng.integers(3, 12)); p = stem_pts[k].copy()
        az = rng.uniform(0, 2 * math.pi); d = _unit(np.array([math.cos(az), math.sin(az), -0.2]))
        pts = [p.copy()]
        for _s in range(30):
            d = _unit(d + np.array([0, 0, -0.12]) + rng.normal(0, 0.06, 3))
            p = p + d * 0.012
            if p[2] < -0.01:
                break
            pts.append(p.copy())
        pts = np.array(pts)
        if len(pts) > 2:
            v, f = tube(pts, np.linspace(0.0045, 0.003, len(pts)), 8)
            off = sum(len(x) for x in RV); RV.append(v); RF.extend([[i + off for i in q] for q in f])
    stem = mesh_obj(f"monstera_{seed}_stems", np.concatenate(TV) + loc, TF, stem_mat)
    objs = [stem] + leaves
    if RV:
        objs.append(mesh_obj(f"monstera_{seed}_roots", np.concatenate(RV) + loc, RF, root_mat))
    print(f"monstera {seed}: {n_leaf} leaves, stems {len(stem.data.polygons)} faces, leaves {sum(len(o.data.polygons) for o in leaves)} faces")
    return objs

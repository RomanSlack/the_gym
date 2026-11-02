"""Boston fern (Nephrolepis exaltata) generator: one seed = one plant, never the same twice (plants/GOAL.md).

Every number comes from the reference sheet (out/refs_boston_fern_v001.jpg):
- 35-55 fronds from a crown ~6 cm across: young ones upright in the centre (2-4 still coiled croziers), mature ones arching
  out and drooping 40-90 cm, the oldest outermost drooping hardest, yellowing, some pinnae lost
- pinnae alternate, ~9 mm apart, oblong and blunt, slightly falcate (curved toward the frond tip), an auricle (lobe) at the
  upper base, crenate wavy margins, twisted / undulating; 2.5-4 cm at the frond's widest, shorter at its base and tip
- brown-green rachis, round, tapering; wiry runners (stolons) hanging over the pot rim
Attributes for the material: fr (per frond random), age (0 young -> 1 old), pr (per pinna random), t (along the frond),
brown (old tips / damage). UVs per pinna: u along it, v across it (0.5 = the midrib).

    import gen_fern; obj = gen_fern.build(seed, (x, y, z_soil), pot_radius)
"""
import math

import bpy
import numpy as np


def _rot(axis, ang):
    """rotation matrix about `axis` by `ang` (Rodrigues)"""
    k = axis / (np.linalg.norm(axis) + 1e-12)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


class Mesh:
    def __init__(self):
        self.V, self.F, self.UV, self.A = [], [], [], {k: [] for k in ("fr", "age", "pr", "t", "brown")}
        self.n = 0

    def add(self, verts, faces, uvs, attrs):
        """verts (k,3); faces (m,3|4) local indices; uvs per face-corner list aligned with faces; attrs: per-vertex dict"""
        self.V.append(verts)
        self.F.extend([[i + self.n for i in f] for f in faces])
        self.UV.extend(uvs)
        for k in self.A:
            a = attrs.get(k, 0.0)
            self.A[k].append(np.full(len(verts), a, np.float32) if np.isscalar(a) else np.asarray(a, np.float32))
        self.n += len(verts)

    def object(self, name, mat):
        V = np.concatenate(self.V)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], self.F)
        uvl = me.uv_layers.new(name="UVMap")
        uv = np.array([c for f in self.UV for c in f], np.float32)
        uvl.data.foreach_set("uv", uv.ravel())
        for k, vals in self.A.items():
            at = me.attributes.new(k, "FLOAT", "POINT")
            at.data.foreach_set("value", np.concatenate(vals))
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        me.update()
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        o.data.materials.append(mat)
        return o


# ------------------------------------------------------------------------------------------------------------ one pinna
NU, NV = 14, 6           # quads along / across a pinna (hero detail)


def pinna_outline(rng):
    """half-widths (upper = toward the frond tip, lower) along the pinna for u in 0..1, in units of its length"""
    u = np.linspace(0, 1, NU + 1)
    aur = rng.uniform(0.05, 0.09)                                  # the auricle on the upper base
    core = 0.158 * np.clip(np.sin(np.pi * np.clip(u * 0.62 + 0.04, 0, 1)) ** 0.35, 0, 1)
    tip = np.clip((1 - u) / 0.22, 0, 1) ** 0.6                       # blunt, rounded tip
    teeth = 1 + rng.uniform(0.04, 0.08) * np.sin(u * np.pi * rng.uniform(13, 19) + rng.uniform(0, 6))   # crenate margin
    upper = (core + aur * np.exp(-((u - 0.06) / 0.07) ** 2)) * tip * teeth
    lower = core * tip * teeth * np.clip(u / 0.08, 0.35, 1)         # the lower base cut away (truncate)
    return u, upper, lower


def pinna(M, origin, along, side, normal, length, rng, attrs):
    """a pinna rooted at origin, its midrib heading `along`, `side` toward the frond tip, `normal` the blade's up"""
    u, up_w, lo_w = pinna_outline(rng)
    fold = rng.uniform(0.12, 0.3)                                    # V fold along the midrib
    curl = rng.uniform(-0.08, 0.18)                                  # tips droop (or lift a little)
    twist = rng.uniform(0.25, 0.6) * rng.choice([-1, 1])             # the undulation the references show
    waves = rng.uniform(1.0, 2.2)
    falc = rng.uniform(0.04, 0.1)                                    # curved toward the frond tip
    verts, uvs_v = [], []
    for i, ui in enumerate(u):
        x = ui * length
        mid_side = falc * ui ** 2 * length
        mid_up = -curl * ui ** 2 * length
        ang = twist * math.sin(math.pi * ui * waves) * ui
        ca, sa = math.cos(ang), math.sin(ang)
        for j in range(NV + 1):
            v = j / NV                                               # 0 lower margin -> 1 upper margin
            w = (v - 0.5) * 2
            hw = (up_w[i] if w > 0 else lo_w[i]) * length * abs(w)
            y = math.copysign(hw, w) if w != 0 else 0.0
            z = abs(y) * fold * (1 - ui * 0.5)
            y, z = y * ca - z * sa, y * sa + z * ca                     # twist about the midrib
            p = origin + along * x + side * (y + mid_side) + normal * (z + mid_up)
            verts.append(p)
            uvs_v.append((ui, v))
    verts = np.array(verts)
    faces, uvs = [], []
    R = NV + 1
    flip = np.cross(along, side) @ normal < 0                       # wind every pinna so its face normal is the blade's up
    for i in range(NU):
        for j in range(NV):
            a, b, c, d = i * R + j, (i + 1) * R + j, (i + 1) * R + j + 1, i * R + j + 1
            if flip:
                a, b, c, d = a, d, c, b
            faces.append([a, b, c, d])
            uvs.append([uvs_v[a], uvs_v[b], uvs_v[c], uvs_v[d]])
    at = dict(attrs)
    if "brown_tip" in attrs:                                         # old pinnae brown from the tip in
        at["brown"] = np.repeat(np.clip((u - (1 - attrs["brown_tip"])) / 0.15, 0, 1), R)
        del at["brown_tip"]
    M.add(verts, faces, uvs, at)


# ------------------------------------------------------------------------------------------------------------ a frond
def frond(M, R, base, azim, elev, L, rng, age, crozier=False):
    """spine by marching with gravity bending it down harder toward the tip (stiff base, arching blade), a slow roll of
    the blade, small wander; pinnae alternate along it from ~12 % of its length"""
    n = 160
    ds = L / n
    d = np.array([math.cos(elev) * math.cos(azim), math.cos(elev) * math.sin(azim), math.sin(elev)])
    up = np.array([0, 0, 1.0])
    stiff = rng.uniform(0.75, 1.15) * (1.0 - 0.35 * age)
    pts, dirs = [base.copy()], [d.copy()]
    p = base.copy()
    wander = rng.normal(0, 1, 3) * 0.002
    for k in range(n):
        s = (k + 1) / n
        if crozier and s > 0.55:                                     # the coiled fiddlehead
            axis = _unit(np.cross(d, up)) if abs(d[2]) < 0.99 else np.array([1.0, 0, 0])
            d = _rot(axis, -0.09 - 0.25 * (s - 0.55)) @ d
        else:
            horiz = _unit(np.cross(np.cross(d, up), d)) if abs(d[2]) < 0.999 else np.zeros(3)
            g = (0.08 + (4.2 + 2.2 * age) * s ** 2) / stiff * ds                      # a stiff stipe, the arch from ~1/3 out (v2 bent flat from the base)
            d = _unit(d - horiz * g * 1.0 + (rng.normal(0, 1, 3) * 0.004 + wander))
        p = p + d * ds
        if R and p[2] < 0.045 and R - 0.02 < np.hypot(p[0], p[1]) < R + 0.012:   # draped over the pot's rim, never through it
            rr = np.hypot(p[0], p[1]) + 1e-9
            if p[2] > 0.0:
                p[2] = max(p[2], 0.045)
            p[:2] *= (R + 0.012) / rr
            d = _unit(np.array([p[0], p[1], 0.0]) / rr * 0.6 + np.array([0, 0, -0.4]) + d * 0.5)
        pts.append(p.copy()); dirs.append(d.copy())
    pts, dirs = np.array(pts), np.array(dirs)
    # the blade's up: world up projected off the spine, rolled slowly about it
    roll_end = rng.uniform(-0.6, 0.6) + (0.5 if age > 0.6 else 0)
    ups = []
    for k, dk in enumerate(dirs):
        ref = np.array([0, 0, 1.0]) if abs(dk[2]) < 0.97 else _unit(np.array([math.cos(azim), math.sin(azim), 0]))
        nk = _unit(ref - dk * (ref @ dk))
        nk = _rot(dk, roll_end * (k / n) ** 1.5) @ nk
        ups.append(nk)
    ups = np.array(ups)
    fr = rng.random()
    # rachis: a tapering tube
    r0 = 0.0021 * (L / 0.7) ** 0.5
    sides = 8
    rv, rf, ruv = [], [], []
    for k in range(n + 1):
        s = k / n
        r = r0 * (1 - 0.8 * s)
        b = _unit(np.cross(dirs[k], ups[k]))
        for j in range(sides):
            a = 2 * math.pi * j / sides
            rv.append(pts[k] + (ups[k] * math.cos(a) + b * math.sin(a)) * r)
    for k in range(n):
        for j in range(sides):
            a_, b_ = k * sides + j, k * sides + (j + 1) % sides
            rf.append([a_, a_ + sides, b_ + sides, b_])
            ruv.append([(0.5, 0.5)] * 4)
    M.add(np.array(rv), rf, ruv, {"fr": fr, "age": age, "pr": 0.0, "t": np.repeat(np.linspace(0, 1, n + 1), sides), "brown": -1.0})
    # pinnae
    s0 = rng.uniform(0.10, 0.14) * L
    gap = rng.uniform(0.0082, 0.0098) * (L / 0.7) ** 0.25
    pmax = rng.uniform(0.026, 0.038) * (L / 0.7) ** 0.6
    s = s0
    side_sign = 1
    lost = 0.18 * max(age - 0.6, 0) / 0.4                            # old fronds lose pinnae
    while s < L * 0.985:
        tt = (s - s0) / (L - s0)
        env = np.interp(tt, [0, 0.12, 0.3, 0.68, 0.9, 1.0], [0.38, 0.75, 1.0, 1.0, 0.55, 0.12])
        if crozier:
            env *= np.interp(s / L, [0, 0.5, 0.8, 1], [1, 0.8, 0.35, 0.15])
        k = min(int(s / L * n), n)
        dk, nk = dirs[k], ups[k]
        bk = _unit(np.cross(dk, nk)) * side_sign
        if rng.random() > lost:
            ang = math.radians(rng.uniform(68, 82))                     # toward the frond tip
            along = _unit(bk * math.sin(ang) + dk * math.cos(ang))
            lift = math.radians(rng.uniform(-6, 14))                     # the blade's slight keel
            along = _unit(along + nk * math.tan(lift))
            sidev = _unit(np.cross(nk, along)) * side_sign
            if sidev @ dk < 0:
                sidev = -sidev
            nrm = _unit(np.cross(along, sidev))
            if nrm @ nk < 0:
                nrm = -nrm
            plen = pmax * env * rng.uniform(0.9, 1.1)
            bt = 0.0
            if age > 0.65:
                bt = rng.uniform(0, 0.5) * (age - 0.65) / 0.35 + (0.25 if tt > 0.85 and rng.random() < 0.6 else 0)
            elif rng.random() < 0.015:
                bt = rng.uniform(0.05, 0.2)                              # the odd dry tip on a healthy frond
            origin = pts[k] + bk * r0 * (1 - 0.8 * s / L)
            pinna(M, origin, along, sidev, nrm, plen, rng, {"fr": fr, "age": age, "pr": rng.random(), "t": tt, "brown_tip": bt})
        s += gap / 2 * rng.uniform(0.9, 1.1)                         # (gap = the spacing on one side; they alternate)
        side_sign = -side_sign


def stolon(M, base, azim, rim_r, rng):
    """a wiry runner: out over the rim, then hanging down, slight kinks"""
    n, r = 60, rng.uniform(0.0005, 0.0008)
    L = rng.uniform(0.18, 0.55)
    d = _unit(np.array([math.cos(azim), math.sin(azim), rng.uniform(0.1, 0.5)]))
    p = base.copy(); pts = [p.copy()]
    for k in range(n):
        horiz = np.array([d[0], d[1], 0])
        out_r = np.hypot(p[0], p[1])
        d = _unit(d + (np.array([0, 0, -0.09]) if out_r > rim_r else np.zeros(3)) + rng.normal(0, 1, 3) * 0.05)
        p = p + d * L / n
        pts.append(p.copy())
    pts = np.array(pts)
    sides = 5
    vv, ff, uu = [], [], []
    for k, pk in enumerate(pts):
        dk = _unit(pts[min(k + 1, n)] - pts[max(k - 1, 0)])
        a1 = _unit(np.cross(dk, [0, 0, 1.0]) if abs(dk[2]) < 0.99 else np.array([1.0, 0, 0]))
        a2 = np.cross(dk, a1)
        for j in range(sides):
            a = 2 * math.pi * j / sides
            vv.append(pk + (a1 * math.cos(a) + a2 * math.sin(a)) * r * (1 - 0.6 * k / n))
    for k in range(n):
        for j in range(sides):
            a_, b_ = k * sides + j, k * sides + (j + 1) % sides
            ff.append([a_, a_ + sides, b_ + sides, b_]); uu.append([(0.5, 0.5)] * 4)
    M.add(np.array(vv), ff, uu, {"fr": rng.random(), "age": 0.9, "pr": 0.0, "t": 0.0, "brown": -2.0})


# ------------------------------------------------------------------------------------------------------------ the plant
def build(seed, loc=(0, 0, 0), pot_r=0.16, mat=None, name=None):
    rng = np.random.default_rng(seed)
    M = Mesh()
    n_fr = int(rng.integers(75, 110))                                  # a full potted plant (v1's 45 read sparse)
    crown = rng.uniform(0.025, 0.04)
    rings = []
    for i in range(n_fr):
        age = rng.beta(1.6, 1.4)                                     # 0 young (centre) -> 1 old (outside)
        rr = crown * (0.15 + 0.85 * age) * rng.uniform(0.7, 1.1)
        az = rng.uniform(0, 2 * math.pi)
        base = np.array([rr * math.cos(az), rr * math.sin(az), rng.uniform(-0.005, 0.01)])
        elev = math.radians(np.interp(age, [0, 0.4, 1], [86, 64, 36]) + rng.normal(0, 6))
        L = np.interp(age, [0, 0.3, 1], [0.32, 0.66, 0.92]) * rng.uniform(0.8, 1.15)
        rings.append((age, base, az + rng.normal(0, 0.15), elev, L))
    for age, base, az, elev, L in rings:
        frond(M, pot_r, base, az, elev, L, rng, age)
    for _ in range(int(rng.integers(2, 5))):                          # croziers in the centre
        az = rng.uniform(0, 2 * math.pi)
        base = np.array([crown * 0.2 * math.cos(az), crown * 0.2 * math.sin(az), 0.0])
        frond(M, None, base, az, math.radians(rng.uniform(78, 88)), rng.uniform(0.1, 0.22), rng, 0.0, crozier=True)
    for _ in range(int(rng.integers(4, 12))):                         # runners over the rim
        az = rng.uniform(0, 2 * math.pi)
        stolon(M, np.array([crown * math.cos(az), crown * math.sin(az), 0.0]), az, pot_r, rng)
    o = M.object(name or f"boston_fern_{seed}", mat)
    o.location = loc
    o.rotation_euler[2] = rng.uniform(0, 2 * math.pi)
    print(f"fern {seed}: {n_fr} fronds, {len(o.data.vertices)} verts, {len(o.data.polygons)} faces")
    return o

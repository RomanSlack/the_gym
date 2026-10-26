"""Hammer Strength's 4-sided urethane dumbbell, shared by the dumbbell set and the racks that hold it: the head round with
four flats (it can't roll), a textured patch on each flat, HAMMER STRENGTH and the pounds raised in grey outside, the
kilos and the chrome hub inside; the chrome handle knurled between the heads. (The fixed barbells' heads are the same
design, built in their own model.)

    dumbbell(k, lb, c, axis="y")    the dumbbell centred at c, its handle along axis ("x" or "y"), lying on a flat
"""
import math

LOOK = {
    "hs_chrome": dict(color=(0.82, 0.82, 0.83), rough=0.08, metal=1.0),
    "hs_knurl": dict(color=(0.7, 0.7, 0.71), rough=0.35, metal=1.0, bump=(4000, 0.25)),
    "hs_ure": dict(color=(0.014, 0.014, 0.015), rough=0.45, coat=0.2, spec=0.4),
    "hs_ink": dict(color=(0.55, 0.55, 0.56), rough=0.5, coat=0.0),
    "hs_tex": dict(color=(0.02, 0.02, 0.021), rough=0.85, coat=0.0, bump=(3000, 0.3)),
}
GRIP = 0.127                          # between the heads (5 in)
R_HANDLE = 0.0165


def size(lb):
    """The head's across and thick for a dumbbell of lb pounds (each head half of it; estimates against ref_01's 50)."""
    f = (lb / 50) ** (1 / 3)
    return 0.16 * f, 0.085 * f


def height(lb):
    """The handle's axis over the floor when it lies on a flat."""
    return 0.9 * size(lb)[0] / 2


def _head(k, p, s, t, lb, sgn, axis):
    """One head, its inner face at p's along-axis coordinate, outward by sgn."""
    R, F = s / 2, 0.9 * s / 2
    ring = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        q = (max(-F, min(F, R * math.cos(a))), max(-F, min(F, R * math.sin(a))))
        if not ring or abs(q[0] - ring[-1][0]) > 1e-6 or abs(q[1] - ring[-1][1]) > 1e-6:
            ring.append(q)
    cx, cy, cz = p
    if axis == "x":
        x0, x1 = (cx, cx + sgn * t) if sgn > 0 else (cx + sgn * t, cx)
        k.slab("hs_ure", [(cy + a, cz + b) for a, b in ring], x0, x1, min(0.005, t * 0.1))
        xo, xi = (x1, x0) if sgn > 0 else (x0, x1)
        P = lambda xx, u, v: (xx, cy + u, cz + v)
        rz = sgn * math.pi / 2
        hub_axis = "x"
    else:
        # build along y: the slab extrudes along x, so take the outline in (x, z) by building at y and swapping
        y0, y1 = (cy, cy + sgn * t) if sgn > 0 else (cy + sgn * t, cy)
        _slab_y(k, "hs_ure", [(cx + a, cz + b) for a, b in ring], y0, y1, min(0.005, t * 0.1))
        xo, xi = (y1, y0) if sgn > 0 else (y0, y1)
        P = lambda yy, u, v: (cx - u, yy, cz + v)
        rz = 0.0 if sgn < 0 else math.pi
        hub_axis = "y"
    k.disc("hs_chrome", P(xi - sgn * 0.0006, 0, 0), 0.026 * s / 0.16, R_HANDLE, 0.0012, axis=hub_axis, seg=32, soft=0.0)
    k.text("hs_ink", "HAMMER", P(xo + sgn * 0.0003, 0, s * 0.27), s * 0.155, rz=rz, depth=0.0006)
    k.text("hs_ink", "STRENGTH", P(xo + sgn * 0.0003, 0, s * 0.12), s * 0.145, rz=rz, depth=0.0006)
    k.text("hs_ink", str(lb), P(xo + sgn * 0.0003, 0, -s * 0.15), s * 0.34, rz=rz, depth=0.0008)
    k.text("hs_ink", f"{lb * 0.4536:.1f} KG", P(xi - sgn * 0.0003, 0, s * 0.26), s * 0.09, rz=rz + math.pi, depth=0.0005)
    m = ((x0 + x1) / 2) if axis == "x" else ((y0 + y1) / 2)
    for du, dv in ((0, 1), (0, -1), (1, 0), (-1, 0)):  # the flats' textured patches
        w = 0.42 * s
        c = P(m, du * (F + 0.0004), dv * (F + 0.0004))
        along = t - 0.012
        if axis == "x":
            size_ = (along, w if dv else 0.0008, 0.0008 if dv else w)
        else:
            size_ = (w if dv else 0.0008, along, 0.0008 if dv else w)
        k.box("hs_tex", c, size_, soft=0.0)


def _slab_y(k, mat, outline_xz, y0, y1, r):
    """kit.slab extrudes along x; build the head along x at the origin and turn it a quarter about z onto y."""
    bm = k.bm(mat, 0.0)
    before = set(bm.verts)
    xs = [p[0] for p in outline_xz]
    cxm = (min(xs) + max(xs)) / 2
    k.slab(mat, [(p[0] - cxm, p[1]) for p in outline_xz], y0, y1, r)
    new = [v for v in bm.verts if v not in before]
    # the slab sits at x in [y0, y1], its outline in (y, z) = (x - cxm, z): turn (x, y) -> (cxm + y, x)
    for v in new:
        x, y = v.co.x, v.co.y
        v.co.x, v.co.y = cxm + y, x


def dumbbell(k, lb, c, axis="y"):
    s, t = size(lb)
    cx, cy, cz = c
    g = GRIP / 2
    if axis == "x":
        k.tube("hs_chrome", (cx - g - 0.01, cy, cz), (cx + g + 0.01, cy, cz), R_HANDLE - 0.0005, seg=24)
        k.tube("hs_knurl", (cx - g + 0.012, cy, cz), (cx + g - 0.012, cy, cz), R_HANDLE, seg=24)
        for sg in (1, -1):
            _head(k, (cx + sg * g, cy, cz), s, t, lb, sg, "x")
    else:
        k.tube("hs_chrome", (cx, cy - g - 0.01, cz), (cx, cy + g + 0.01, cz), R_HANDLE - 0.0005, seg=24)
        k.tube("hs_knurl", (cx, cy - g + 0.012, cz), (cx, cy + g - 0.012, cz), R_HANDLE, seg=24)
        for sg in (1, -1):
            _head(k, (cx, cy + sg * g, cz), s, t, lb, sg, "y")

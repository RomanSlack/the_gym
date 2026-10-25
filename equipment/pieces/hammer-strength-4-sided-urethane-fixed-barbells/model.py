"""Hammer Strength 4-Sided Urethane Fixed Barbells, the straight and EZ-curl sets (refs/: ref_01 a straight 40 lb and an
EZ 20 lb; ref_02 an EZ; ref_03 a straight; ref_04 the inner face (27.2 KG) and the chrome hub; ref_05 the outer face:
HAMMER STRENGTH over a large 60 in grey, the head round with four flats cut at its top, bottom and sides). The shop
page refused requests (HTTP 429): the sizes are ours (estimates): the straights 1.25 m overall, the EZ 1.15 m, a 28 mm
chrome knurled shaft; the heads from 150 mm across and 55 mm thick at 20 lb to 265 / 97 mm at 110 lb (growing with
the cube root of the weight). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Grab-and-go barbells for curls, presses, rows: no loading, the heads fixed; racked on a barbell rack (not this
   piece), set down on the floor on a flat of the heads (the square heads don't roll).
2. Each mass named (ref_04 / ref_05): the shaft, chrome steel, knurled where it is held (the EZ's bent through its
   grips); at each end a head: a steel core in a black urethane shell, round with four flats (the 4 sides: it can't
   roll), the faces flat, the chrome hub on the inner face; the markings raised in grey: HAMMER STRENGTH and the
   pounds outside, the kilos inside.
3. Adjustments. None (a weight per bar): 20-110 lb in 10 lb steps, straight and EZ.
4. Load path. The hands on the knurl, the shaft, the heads' cores.
5. Fit range. The straight's 0.9 m between the heads takes any user's (1.55 / 1.78 / 1.95 m) shoulder-width grip; the
   EZ's grips angled for curls and skull crushers. On the floor the shaft stands 75-135 mm up: picked up with a hinge.
6. Size. Two rows of ten on the floor.
Axes: metres, floor z = 0; the bars along x, the straights in a row at -y, the EZs at +y, the lightest first.
"""
import math

WEIGHTS = tuple(range(20, 120, 10))
L_ST, L_EZ = 1.25, 1.15
R_SH = 0.014

LOOK = {
    "chrome": dict(color=(0.82, 0.82, 0.83), rough=0.08, metal=1.0),
    "knurl": dict(color=(0.7, 0.7, 0.71), rough=0.35, metal=1.0, bump=(4000, 0.25)),
    "ure": dict(color=(0.014, 0.014, 0.015), rough=0.45, coat=0.2, spec=0.4),                # black urethane
    "ink": dict(color=(0.55, 0.55, 0.56), rough=0.5, coat=0.0),
    "tex": dict(color=(0.02, 0.02, 0.021), rough=0.85, coat=0.0, bump=(3000, 0.3)),            # the flats' texture
}
VIEWS = {"three_quarter": (-35, 28, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "back_three_quarter": (150, 28, 1.0)}
DETAILS = {
    "detail_head": ((-0.95, -0.45, 0.45), (-0.62, -0.10, 0.10), 35),    # ref_05: a head's outer face
}


def size(lb):
    f = (lb / 20) ** (1 / 3)
    return 0.15 * f, 0.055 * f


def head(k, x, s, t, y, zc, lb, sgn):
    """A head at x (its inner face), outward along sgn: the rounded square shell, the rims, the hub, the markings."""
    R, F = s / 2, 0.9 * s / 2                          # round, four flats cut at 0.9 R (ref_05)
    out = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        p = (max(-F, min(F, R * math.cos(a))), max(-F, min(F, R * math.sin(a))))
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    out = [(y + a, zc + b) for a, b in out]
    x0, x1 = (x, x + t) if sgn > 0 else (x - t, x)
    k.slab("ure", out, x0, x1, 0.006)
    xo, xi = (x1, x0) if sgn > 0 else (x0, x1)       # the outer and the inner face
    k.disc("chrome", (xi - sgn * 0.0006, y, zc), 0.03, R_SH, 0.0012, axis="x", seg=32, soft=0.0)          # the hub
    rz = sgn * math.pi / 2
    k.text("ink", "HAMMER", (xo + sgn * 0.0003, y, zc + s * 0.27), s * 0.155, rz=rz, depth=0.0006)
    k.text("ink", "STRENGTH", (xo + sgn * 0.0003, y, zc + s * 0.12), s * 0.145, rz=rz, depth=0.0006)
    k.text("ink", str(lb), (xo + sgn * 0.0003, y, zc - s * 0.15), s * 0.34, rz=rz, depth=0.0008)
    for dy, dz in ((0, 1), (0, -1), (1, 0), (-1, 0)):  # the textured patch on each flat (ref_05)
        w = 0.42 * s
        k.box("tex", ((x0 + x1) / 2, y + dy * (F + 0.0004), zc + dz * (F + 0.0004)),
              (t - 0.012, w if dz else 0.0008, 0.0008 if dz else w), soft=0.0)
    k.text("ink", f"{lb * 0.4536:.1f} KG", (xi - sgn * 0.0003, y + sgn * 0.0, zc + s * 0.26), s * 0.09, rz=-rz,
           depth=0.0005)


def bar(k, lb, y, ez):
    s, t = size(lb)
    zc = 0.9 * s / 2                                    # lying on a flat of the heads
    L = L_EZ if ez else L_ST
    xi = L / 2 - t                                      # the heads' inner faces
    if ez:                                              # the EZ bends lie flat (it rests on its heads)
        pts = [(-xi - 0.01, 0), (-0.34, 0), (-0.27, 0.045), (-0.17, -0.035), (-0.07, 0.0), (0.07, 0.0), (0.17, -0.035),
               (0.27, 0.045), (0.34, 0), (xi + 0.01, 0)]
        k.sweep("knurl", [(x, y + dy, zc) for x, dy in pts], k.circle(R_SH, 16), bend=0.03, soft=0.0)
    else:
        k.tube("chrome", (-xi - 0.01, y, zc), (xi + 0.01, y, zc), R_SH, seg=24)
        for sx in (1, -1):                              # the knurled grips
            k.tube("knurl", (sx * 0.10, y, zc), (sx * 0.40, y, zc), R_SH + 0.0003, seg=24)
    for sx in (1, -1):
        head(k, sx * xi, s, t, y, zc, lb, sx)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    y = -0.10
    for lb in WEIGHTS:                                  # the straights, toward -y
        s, _ = size(lb)
        y -= s / 2
        bar(k, lb, y, False)
        y -= s / 2 + 0.04
    y = 0.10
    for lb in WEIGHTS:                                  # the EZs, toward +y
        s, _ = size(lb)
        y += s / 2
        bar(k, lb, y, True)
        y += s / 2 + 0.06

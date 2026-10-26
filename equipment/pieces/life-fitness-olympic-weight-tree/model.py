"""Life Fitness Olympic Weight Tree (refs/: ref_01 black, ref_02 silver: an H base on the floor, a central post rising
from it with the Life Fitness script up its face, horns out front and back low and out to the sides up top,
loaded: 45s and 25s low, the small plates up top). The shop page refuses requests (HTTP 429): every size is an estimate off
the refs against the 450 mm plates (about 1.15 m high, 0.75 m deep). Built to the two gates and README point 9. Shown
black, loaded with the HS urethane round plates (their builder: pieces/hammer-strength-urethane-round-olympic-plates).

DESIGN SPEC (gate 1)
1. Use. Plate storage by the platform: plates slid on and off the horns at three heights.
2. Each mass named (ref_01): the base, a foot front and back joined by a spine; the post, a rectangular tube
   up the middle; a low crossbar with four horns front and back (the 45s and 25s), two horns out the
   sides at the top (the small plates), rubber-capped; the script up the post.
3. Adjustments. None.
4. Load path. The plates on the horns, the post, the base's feet.
5. Fit range. The 45s at their bore 0.25 m up (a hinge for every user, 1.55-1.95 m), the small plates at chest
   height. No figure.
6. Size. 0.80 x 0.75 x 1.15 m (loaded, the plates out to 0.70 m wide).
Axes: metres, floor z = 0; the low horns along +-y, the top ones along +-x, the base's feet along x.
"""
import importlib.util
import os

H = 1.15
POST = (0.08, 0.06)
R_HORN = 0.024
Z_LOW, Z_TOP = 0.27, 1.02
# low horns along +-y off a crossbar: (x, the plates out each way); top horns along +-x off the post's top
LOW = ((-0.20, (45, 45)), (0.22, (25, 25)))
TOP = ((1, (10, 5)), (-1, (5, 2.5)))
L_LOW, L_TOP = 0.30, 0.20


def _plates():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hammer-strength-urethane-round-olympic-plates",
                     "model.py")
    spec = importlib.util.spec_from_file_location("hsure", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PL = _plates()
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "horn": dict(color=(0.75, 0.75, 0.76), rough=0.18, metal=1.0),
    "cap": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0),
    "script": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
}
LOOK.update({r: v for r, v in PL.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-50, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (130, 16, 1.0)}
DETAILS = {
    "detail_top": ((-0.6, -0.9, 1.25), (0.0, 0.0, 0.95), 35),           # the top horns, the small plates
}


def hang(k, lb, axis, sign, p, specs):
    """A plate on a horn along axis (sign out), its inner face at p along the horn; the bore on the horn's top."""
    r, t, w = specs[lb]
    before = {key: set(g.verts) for key, g in k.groups.items()}
    PL.plate(k, lb, r, t, w, 0.0)
    for key, g in k.groups.items():
        for v in g.verts:
            if v in before.get(key, ()):
                continue
            a = sign * (v.co.x + t / 2)                 # along the horn, from the inner face
            q = v.co.y
            z = v.co.z - r + p[2] + PL.R_INS - R_HORN
            v.co = (p[0] + a, p[1] + q, z) if axis == "x" else (p[0] - q, p[1] + a, z)
    return t


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sy in (1, -1):                                  # the base: a foot front and back, joined
        k.bar("frame", (-0.42, sy * 0.30, 0.03), (0.42, sy * 0.30, 0.03), 0.06, 0.06, r=0.005)
    k.bar("frame", (0, -0.30, 0.03), (0, 0.30, 0.03), 0.06, 0.06, r=0.005)
    k.bar("frame", (0, 0.10, 0.06), (0, -0.02, H), POST[0], POST[1], r=0.004)                         # the post, leaning
    k.text("script", "LifeFitness", (POST[0] / 2 + 0.0004, 0.05, 0.62), 0.06, rz=1.5708, spin=1.3, depth=0.0005)
    specs = {lb: (r, t, w) for lb, r, t, w in PL.PLATES}
    yp = 0.10 - 0.12 * Z_LOW / H
    k.tube("frame", (-0.22, yp, Z_LOW), (0.24, yp, Z_LOW), 0.03, seg=20)                             # the low crossbar
    for x, load in LOW:
        for sy in (1, -1):
            k.tube("horn", (x, yp, Z_LOW), (x, yp + sy * L_LOW, Z_LOW), R_HORN, seg=24)
            k.cyl("cap", (x, yp + sy * (L_LOW + 0.004), Z_LOW), R_HORN + 0.003, 0.012, axis="y", seg=24, soft=0.002)
            d = 0.05
            for lb in load:
                d += hang(k, lb, "y", sy, (x, yp + sy * d, Z_LOW), specs) + 0.004
    yt = 0.10 - 0.12 * Z_TOP / H
    for sx, load in TOP:
        x0 = sx * POST[0] / 2
        k.tube("horn", (x0, yt, Z_TOP), (x0 + sx * L_TOP, yt, Z_TOP), R_HORN, seg=24)
        k.cyl("cap", (x0 + sx * (L_TOP + 0.004), yt, Z_TOP), R_HORN + 0.003, 0.012, axis="x", seg=24, soft=0.002)
        d = 0.03
        for lb in load:
            d += hang(k, lb, "x", sx, (x0 + sx * d, yt, Z_TOP), specs) + 0.004

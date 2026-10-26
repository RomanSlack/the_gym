"""Hammer Strength Three-Tier Dumbbell Rack, loaded with the Hammer Strength 5-75 lb urethane set (refs/: ref_01 loaded with
heavy dumbbells; ref_02 / ref_04-ref_06 empty: the black trays tilted toward the user on two grey supports; ref_03 from
the end: a support's foot, rear post and front strut, the trays stepped up and back, the black end caps with yellow
caution labels, the HAMMER STRENGTH plate; ref_07 / ref_08 loaded with exactly our set: 5-25 / 30-50 / 55-75 lb, five
pairs a tier; ref_09 a tray's textured liner, its curved saddles, a number disc). The shop refused further requests
(HTTP 429): the sizes are ours from the photos (estimates): 2.05 m long, 0.84 m deep, the trays 0.36 m wide tilted
22 deg, their middles at 0.30 / 0.56 / 0.82 m. Built to the two gates and README point 9; the dumbbells from the shared
builder (equipment/blender/hs_urethane.py, the dumbbell piece's own).

DESIGN SPEC (gate 1)
1. Use. Each pair lies across a tray, its outer head toward the user (the number readable), tipped back by the tray's
   slope so it stays put; lifted out by the handle and set back in its saddles.
2. Each mass named (ref_03 / ref_09): two supports, each a foot tube on floor pads, a rear post, a front strut, an arm
   from the post under each tray; three trays, black steel channels (a bottom, a front and a back lip) tilted toward the
   user, stepped up and back, a textured liner in each, a curved saddle under each head, black end caps with the
   caution labels; the HAMMER STRENGTH plate on a support. Supports grey, trays black.
3. Adjustments. None.
4. Load path. The dumbbells' heads in the saddles, the trays, the arms, the posts and struts, the feet.
5. Fit range. The trays' middles at 0.30 / 0.56 / 0.82 m: the heaviest pairs lowest (lifted from mid-shin with a hinge),
   the lightest at the waist of the 1.55 m user; nothing above 0.9 m.
6. Size. 2.05 x 0.84 x 0.95 m (estimates).
Axes: metres, floor z = 0; the trays along x, the user at -y.
"""
import math

import hs_urethane as hs

L = 2.05
X_SUP = 0.62                          # the supports (x)
ALPHA = math.radians(22)              # the trays' tilt toward the user
W = 0.36                              # a tray's width across its slope
TRAYS = ((-0.30, 0.30, tuple(range(55, 80, 5))), (-0.07, 0.56, tuple(range(30, 55, 5))),
         (0.16, 0.82, tuple(range(5, 30, 5))))       # (middle y, middle z, the pairs)
Y_POST = 0.30
TB = 0.05

LOOK = dict(hs.LOOK)
LOOK.update({
    "grey": dict(color=(0.45, 0.46, 0.47), rough=0.35, metal=0.6, coat=0.2),                 # the supports
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.4, metal=0.3, coat=0.2),
    "liner": dict(color=(0.02, 0.02, 0.021), rough=0.9, coat=0.0, bump=(2500, 0.35)),
    "saddle": dict(color=(0.015, 0.015, 0.016), rough=0.4, coat=0.2),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "yellow": dict(color=(0.8, 0.6, 0.03), rough=0.4),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.45),
})
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_end": ((1.55, -0.35, 0.75), (0.95, 0.0, 0.50), 40),         # ref_03: a support, an end cap
    "detail_tray": ((-0.30, -0.95, 0.75), (-0.40, -0.25, 0.35), 35),    # ref_09: a tray, the saddles, the heads
}


def tray_frame(ym, zm):
    """A tray's middle, its across-slope direction (up and back) and its normal (up and toward the user)."""
    u = (0.0, math.cos(ALPHA), math.sin(ALPHA))
    n = (0.0, -math.sin(ALPHA), math.cos(ALPHA))
    return (ym, zm), u, n


def P(ym, zm, a, b, x=0.0):
    """A point a across the slope and b out of the tray from its middle."""
    (_, _), u, n = tray_frame(ym, zm)
    return (x, ym + u[1] * a + n[1] * b, zm + u[2] * a + n[2] * b)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for ym, zm, pairs in TRAYS:
        tray(k, ym, zm, pairs)
    for sx in (1, -1):
        support(k, sx * X_SUP)


def tray(k, ym, zm, pairs):
    half = L / 2
    blk = lambda a0, a1, b0, b1, x0=-half, x1=half: k.block("black", lambda cx, cy, cz: (
        x1 if cx > 0 else x0, *P(ym, zm, a1 if cy > 0 else a0, b1 if cz > 0 else b0)[1:]), soft=0.002)
    blk(-W / 2, W / 2, -0.004, 0.0)                     # the bottom
    blk(-W / 2 - 0.004, -W / 2, -0.004, 0.045)          # the front lip
    blk(W / 2, W / 2 + 0.004, -0.004, 0.045)            # the back lip
    k.block("liner", lambda cx, cy, cz: ((half - 0.01) * cx, *P(ym, zm, (W / 2 - 0.01) * cy, 0.002 if cz > 0 else 0.0)[1:]),
            soft=0.0)
    for sx in (1, -1):                                  # the end caps, their caution labels
        x = sx * (half + 0.003)
        k.block("black", lambda cx, cy, cz, x=x: (x + cx * 0.003, *P(ym, zm, (W / 2 + 0.01) * cy,
                                                                     0.06 if cz > 0 else -0.03)[1:]), soft=0.002)
        k.block("yellow", lambda cx, cy, cz, x=x, sx=sx: (x + sx * (0.0035 + (0.0004 if cx > 0 else 0.0)),
                                                          *P(ym, zm, 0.06 * cy, 0.02 + 0.012 * cz)[1:]), soft=0.0)
    # the dumbbells, five pairs side by side, each across the tray on two saddles
    pitch = (L - 0.12) / 10                             # ten fixed slots a tray (ref_07)
    slot = 0
    for lb in pairs:
        s, t = hs.size(lb)
        for _ in range(2):
            x = -half + 0.06 + pitch * (slot + 0.5)
            slot += 1
            for a in (-1, 1):                           # a curved saddle under each head
                ah = a * (hs.GRIP / 2 + t / 2)
                k.block("saddle", lambda cx, cy, cz, x=x, ah=ah, s=s, t=t: (
                    x + cx * s * 0.3, *P(ym, zm, ah + cy * t * 0.4, 0.002 + (0.012 if cz > 0 else 0.0))[1:]), soft=0.004)
            c = P(ym, zm, 0.0, 0.014 + 0.9 * s / 2, x)
            hs.dumbbell(k, lb, c, axis="y", tilt=ALPHA)


def support(k, x):
    """A support at x: the foot on its pads, the rear post, the front strut, an arm under each tray."""
    k.bar("grey", (x, -0.42, 0.04), (x, 0.40, 0.04), TB, TB * 1.2, r=0.004)                         # the foot
    for y in (-0.38, 0.36):
        k.box("rubber", (x, y, 0.004), (0.07, 0.07, 0.008), soft=0.002)
        k.box("grey", (x, y, 0.009), (0.065, 0.065, 0.004), soft=0.001)
    ztop = TRAYS[-1][1] - 0.05
    k.bar("grey", (x, Y_POST, 0.07), (x, Y_POST, ztop + 0.06), TB, TB, r=0.004)                     # the rear post
    mid = TRAYS[1]
    k.bar("grey", (x, -0.38, 0.07), (x, mid[0] - 0.02, mid[1] - 0.09), TB, TB, r=0.004)             # the front strut
    for ym, zm, _ in TRAYS:                             # the arms: from the post forward under each tray
        under = P(ym, zm, 0.0, -0.025)
        k.bar("grey", (x, Y_POST, under[2]), (x, under[1], under[2]), TB * 0.9, TB * 0.9, r=0.003)
        k.block("grey", lambda cx, cy, cz, ym=ym, zm=zm: (x + cx * TB * 0.45, *P(ym, zm, 0.12 * cy,
                                                                                 -0.004 if cz > 0 else -0.05)[1:]),
                soft=0.002)                             # its saddle plate under the tray
    low = P(TRAYS[0][0], TRAYS[0][1], 0.0, -0.025)      # the plate on the bottom arm's outer face (ref_03)
    yp, xo = (Y_POST + low[1]) / 2, x + (1 if x > 0 else -1) * (TB * 0.45 + 0.0015)
    k.box("black", (xo, yp, low[2]), (0.003, 0.20, TB * 0.8), soft=0.001)
    k.text("label", "HAMMER STRENGTH", (xo + (1 if x > 0 else -1) * 0.0019, yp, low[2]), 0.016,
           rz=(1 if x > 0 else -1) * math.pi / 2, depth=0.0004)

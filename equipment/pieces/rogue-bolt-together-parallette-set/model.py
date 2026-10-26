"""Rogue Bolt Together Parallette Set (refs/: ref_01 the pair: each a bent pipe handle standing on two square-tube
feet, ROGUE in white up a leg; ref_02 / ref_03 a foot close: the leg welded into a bent channel over the foot, two
chrome bolts through it, end caps; ref_04 / ref_05 in use, a handstand and an L-sit). The linked page: 24 x 15 x 14
in each, a 1.5 in 14-gauge bent pipe handle, 2 x 2 in 11-gauge feet, 7-gauge channels, 0.5 in bolts, rubber feet,
textured black. Fetched 2026-10-25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Handstands, L-sits, push-ups, planches: a hand on each handle.
2. Each mass named (ref_01 / ref_02): the handle, 1.5 in pipe bent into a flat-topped U, 24 in long, 14 in high; at
   each leg's foot a channel straddling a 2 x 2 in foot tube 15 in long, two bolts through it; end caps; ROGUE.
3. Adjustments. The pair's spacing (the user sets them shoulder-width apart).
4. Load path. The hands on the pipe, the legs, the channels and bolts, the feet, rubber pads on the floor.
5. Fit range. 1.5 in pipe: every user (1.55 / 1.78 / 1.95 m) grips it; 14 in clears the floor under the L-sit's
   heels for every user (ref_05). No figure.
6. Size. A pair, 0.38 x 0.61 x 0.36 m each, set 0.5 m apart.
Axes: metres, floor z = 0; each handle along y, the pair side by side along x.
"""
import math

IN = 0.0254
L, W, H = 24 * IN, 15 * IN, 14 * IN
R_P, FT = 0.75 * IN, 2 * IN

LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.015), rough=0.6, coat=0.05, bump=(1500, 0.15)),
    "bolt": dict(color=(0.7, 0.7, 0.72), rough=0.15, metal=1.0),
    "cap": dict(color=(0.02, 0.02, 0.022), rough=0.6, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 20, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_foot": ((0.05, -0.70, 0.25), (0.25, -0.25, 0.04), 30),     # a channel, its bolts, a foot's caps
}


def parallette(k, x0):
    yl = L / 2 - FT / 2                                 # the legs over the feet's middles
    k.sweep("frame", [(x0, -yl, FT + 0.03), (x0, -yl, H), (x0, yl, H), (x0, yl, FT + 0.03)], k.circle(R_P, 24), bend=0.06,
            soft=0.0)                                   # the handle
    for sy in (1, -1):
        y = sy * yl
        k.bar("frame", (x0 - W / 2, y, FT / 2), (x0 + W / 2, y, FT / 2), FT, FT, r=0.003)          # a foot
        for sx in (1, -1):
            k.box("cap", (x0 + sx * (W / 2 + 0.002), y, FT / 2), (0.006, FT + 0.002, FT + 0.002), soft=0.002)
            k.box("cap", (x0 + sx * (W / 2 - 0.03), y, 0.002), (0.04, FT, 0.004), soft=0.001)         # rubber pad
        k.box("frame", (x0, y, FT / 2 + 0.006), (0.10, FT + 0.010, FT + 0.012), soft=0.003)            # the channel
        k.tube("frame", (x0, y, FT), (x0, y, FT + 0.035), R_P, seg=24)                                  # leg's weld
        for sx in (1, -1):
            k.cyl("bolt", (x0 + sx * 0.03, y - FT / 2 - 0.006, FT / 2), 0.008, 0.004, axis="y", seg=16, soft=0.001)
            k.cyl("bolt", (x0 + sx * 0.03, y + FT / 2 + 0.006, FT / 2), 0.007, 0.004, axis="y", seg=6, soft=0.0005)
    k.text("white", "ROGUE", (x0 + R_P + 0.0003, -yl, H * 0.6), 0.02, rz=math.pi / 2, spin=math.pi / 2, depth=0.0005)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sx in (1, -1):
        parallette(k, sx * 0.25)

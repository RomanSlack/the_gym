"""Metolius Wood Grips Campus Rungs (refs/: ref_01 five pale wood rungs, each a bar with a rounded front edge, three
screw holes, the "wood grips" mark burnt in). The linked page (rockrun.com) was not fetched: the usual rung, about
18 x 1.75 x 1.25 in, is an estimate. Built to the two gates and README point 9. Screwed to a plywood campus board
(ours: 0.90 x 1.50 m on a display wall section, not the piece), the rungs 22 cm apart.

DESIGN SPEC (gate 1)
1. Use. Campusing: hanging and moving hand to hand up the rungs, feet off, for finger power.
2. Each mass named (ref_01): the rung, pale wood, its top front edge rounded (the hold), three screw holes; the mark.
3. Adjustments. None (the spacing is set when they are screwed on).
4. Load path. The fingers on the rung's edge, its screws, the board, the wall.
5. Fit range. The rungs from 1.70 to 2.58 m: every user (1.55 / 1.78 / 1.95 m) starts from a stool or a jump on the
   lowest. No figure.
6. Size. Five rungs, 0.46 m each.
Axes: metres, floor z = 0; the wall's face at y = 0, the board on it facing -y.
"""
IN = 0.0254
L, D, H = 18 * IN, 1.25 * IN, 1.75 * IN
BT = 0.018
ZS = (1.70, 1.92, 2.14, 2.36, 2.58)

LOOK = {
    "wood": dict(color=(0.50, 0.33, 0.16), rough=0.6, coat=0.0,
                 grain=dict(dark=(0.42, 0.26, 0.11), scale=6.0, distortion=2.0, along="Y")),
    "ply": dict(color=(0.45, 0.36, 0.24), rough=0.7, coat=0.0),
    "burn": dict(color=(0.10, 0.05, 0.02), rough=0.8, coat=0.0),
    "screw": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 10, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-70, 20, 1.0)}
DETAILS = {
    "detail_rung": ((-0.45, -0.70, 2.30), (0.0, -0.03, 2.14), 35),     # a rung, its screws, the mark
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.box("wall", (0, 0.05, 1.5), (1.2, 0.10, 3.0), soft=0.0)                                      # display wall
    k.box("ply", (0, -BT / 2, 1.95), (0.90, BT, 1.50), soft=0.002)                                  # the board
    for z in ZS:
        sec = [(-BT, z - H / 2), (-BT - D + 0.006, z - H / 2), (-BT - D, z - H / 2 + 0.006), (-BT - D, z + H / 2 - 0.012),
               (-BT - D + 0.004, z + H / 2 - 0.003), (-BT - D + 0.012, z + H / 2), (-BT, z + H / 2)]
        k.slab("wood", sec, -L / 2, L / 2, 0.002, seg=2)                                              # the rung
        for x in (-L / 2 + 0.04, 0.0, L / 2 - 0.04):
            k.cyl("screw", (x, -BT - D - 0.0003, z - 0.004), 0.005, 0.001, axis="y", seg=12, soft=0.0)
        k.text("burn", "wood grips", (L / 2 - 0.10, -BT - D - 0.0004, z - 0.004), 0.012, depth=0.0004)

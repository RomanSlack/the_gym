"""RevBalance 101 Mini balance board (refs/: ref_01 the board top and bottom and its roller: a black board with rounded
ends, concentric rings and the R mark on top, MINI in blue on the bottom, a black roller; ref_02 in use, the board on
the roller). The linked page was not fetched: the board (about 28 x 11 in) and roller (about 12 x 4 in) are estimates
off the refs. Laid out as ref_01. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Balance training: the board on the roller, stood on and balanced side to side.
2. Each mass named (ref_01): the board, black, its ends rounded, a stop rail under each end, the rings and R on top;
   the roller, black, a cylinder.
3. Adjustments. None.
4. Load path. The feet on the board, the board on the roller, the floor.
5. Fit range. 28 in: every user (1.55 / 1.78 / 1.95 m) stands feet shoulder-width on it. No figure.
6. Size. The board 0.71 x 0.28 m, the roller 0.30 x 0.10 m.
Axes: metres, floor z = 0.
"""
import math
import mats

IN = 0.0254
BL, BW, BT = 28 * IN, 11 * IN, 0.018

LOOK = {
    "board": dict(color=(0.014, 0.014, 0.015), rough=0.6, coat=0.1, bump=(2000, 0.05)),
    "ring": dict(color=(0.04, 0.04, 0.045), rough=0.6, coat=0.0),
    "blue": dict(color=(0.02, 0.30, 0.55), rough=0.5, coat=0.0),
    "white": dict(color=(0.6, 0.6, 0.6), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_top": ((0.0, -0.45, 0.35), (0.0, 0.0, 0.0), 35),            # the rings, the R
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    r = BW / 2
    pts = [(BL / 2 - r + r * math.cos(a), r * math.sin(a)) for a in [math.pi * (i / 16 - 0.5) for i in range(17)]]
    pts += [(-BL / 2 + r + r * math.cos(a), r * math.sin(a)) for a in [math.pi * (i / 16 + 0.5) for i in range(17)]]
    mats._plate(k, "board", [(x, y - 0.0) for x, y in pts], 0.0, BT)                               # the board
    for i, rr in enumerate((0.03, 0.06, 0.09, 0.12)):  # the rings round the middle
        k.disc("ring", (0, 0, BT + 0.0003), rr + 0.002, rr, 0.0008, axis="z", seg=64, soft=0.0)
    k.text("white", "R", (0, 0, BT + 0.0004), 0.03, rx=0.0, depth=0.0006)
    k.cyl("board", (0.0, -0.30, 2 * IN), 2 * IN, 12 * IN, axis="x", seg=40, soft=0.004)             # the roller
    k.text("blue", "MINI", (0.0, -0.30, 4 * IN + 0.0002), 0.03, rx=0.0, depth=0.0006)

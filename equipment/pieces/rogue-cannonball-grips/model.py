"""Rogue Cannonball Grips, a pair (refs/: ref_01 / ref_04 hung from a pull-up bar: a strap over the bar, a carabiner,
the ball hanging; ref_02 / ref_03 laid out: two straps (coyote or black, ROGUE on each), two oval carabiners, two steel
balls each with a tab welded on top with a hole). The linked page was not fetched (the refs carry the parts): the
ball's size, about 2.9 in, the strap's 1.5 in, are estimates. Built to the two gates and README point 9. Laid out as
ref_03, black.

DESIGN SPEC (gate 1)
1. Use. Grip work: hung from a bar by the strap and carabiner, hangs and pull-ups on the balls.
2. Each mass named (ref_03): the ball, solid steel, black, a tab welded on top with a hole for the carabiner; the
   carabiner; the strap, a loop of webbing with ROGUE.
3. Adjustments. None.
4. Load path. The hands round the balls, the tabs, the carabiners, the straps, the bar.
5. Fit range. 2.9 in: every user (1.55 / 1.78 / 1.95 m) palms it; hung so the arms are long and the feet clear. No
   figure.
6. Size. Laid out in three rows, as ref_03.
Axes: metres, floor z = 0.
"""
import math

IN = 0.0254
R = 2.9 * IN / 2

LOOK = {
    "ball": dict(color=(0.015, 0.015, 0.016), rough=0.6, metal=0.3, coat=0.0, bump=(1500, 0.1)),
    "web": dict(color=(0.010, 0.010, 0.011), rough=0.9, coat=0.0, bump=(3000, 0.12)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "biner": dict(color=(0.75, 0.75, 0.77), rough=0.2, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
}
VIEWS = {"three_quarter": (-20, 45, 1.0), "front": (0, 35, 1.0), "side": (90, 35, 1.0), "back_three_quarter": (160, 45, 1.0)}
DETAILS = {
    "detail_ball": ((0.0, -0.45, 0.30), (0.0, -0.12, 0.0), 30),         # a ball, its tab
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sx in (1, -1):
        x = sx * 0.12
        k.sphere("ball", (x, -0.12, R), R, seg=48, soft=0.002)                                     # the ball
        k.box("ball", (x, -0.12 + R * 0.95, R), (0.03, 0.04, 0.006), soft=0.002)                      # its tab, lying
        k.cyl("hole", (x, -0.12 + R + 0.008, R), 0.006, 0.0064, seg=16, soft=0.0)                    # the tab's hole
        biner = [(x + 0.045 * math.cos(t), 0.04 + 0.024 * math.sin(t), 0.005) for t in
                 [2 * math.pi * i / 32 for i in range(33)]]
        k.sweep("biner", biner, k.circle(0.005, 10), soft=0.0)                                         # the carabiner
        k.box("web", (x, 0.15, 0.002), (0.16, 1.5 * IN, 0.004), soft=0.0008)                            # the strap
        k.text("white", "ROGUE", (x, 0.15, 0.0041), 0.028, rx=0.0, depth=0.0004)

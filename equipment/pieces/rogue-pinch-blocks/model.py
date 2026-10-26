"""Rogue Pinch Blocks (refs/: ref_01 hung from a pull-up bar by straps and carabiners; ref_02 a pair laid out: two
black steel blocks, each a rectangular tube with a tab welded on top with a hole, two carabiners, two straps with
ROGUE; ref_03 the three sizes hung: 3 x 3, 1.5 x 4 and 2 x 3 in). The linked page was not fetched (the refs carry the
parts and sizes): the 2 x 3 in shown as ref_02's pair, its length (4 in) and the strap an estimate. Built to the two
gates and README point 9. Laid out as ref_02.

DESIGN SPEC (gate 1)
1. Use. Pinch grip: hung from a bar and held (or loaded through the tab as a loading pin's pinch).
2. Each mass named (ref_02): the block, a 2 x 3 in steel tube 4 in long, black, a tab welded on top with a hole; the
   carabiner; the strap, a loop of webbing with ROGUE.
3. Adjustments. The size (three).
4. Load path. The fingers and thumb pinching the block's sides, the tab, the carabiner, the strap, the bar.
5. Fit range. A 2 in pinch: every user (1.55 / 1.78 / 1.95 m) spans it, the 3 x 3 for big hands. No figure.
6. Size. Laid out in three rows.
Axes: metres, floor z = 0.
"""
import math

IN = 0.0254

LOOK = {
    "steel": dict(color=(0.015, 0.015, 0.016), rough=0.6, metal=0.3, coat=0.0, bump=(1500, 0.1)),
    "web": dict(color=(0.010, 0.010, 0.011), rough=0.9, coat=0.0, bump=(3000, 0.12)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "biner": dict(color=(0.75, 0.75, 0.77), rough=0.2, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
}
VIEWS = {"three_quarter": (-20, 45, 1.0), "front": (0, 35, 1.0), "side": (90, 35, 1.0), "back_three_quarter": (160, 45, 1.0)}
DETAILS = {
    "detail_block": ((0.0, -0.40, 0.28), (0.0, 0.08, 0.0), 30),         # a block, its tab
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    w, h, L = 3 * IN, 2 * IN, 4 * IN
    for sx in (1, -1):
        x = sx * 0.12
        y = 0.12
        k.box("steel", (x, y, h / 2), (L, w, h), soft=0.003)                                       # the block, lying
        k.box("steel", (x, y + w / 2 + 0.015, 0.004), (0.035, 0.035, 0.006), soft=0.002)            # its tab
        k.cyl("hole", (x, y + w / 2 + 0.02, 0.004), 0.006, 0.0064, seg=16, soft=0.0)
        biner = [(x + 0.045 * math.cos(t), -0.02 + 0.024 * math.sin(t), 0.005) for t in
                 [2 * math.pi * i / 32 for i in range(33)]]
        k.sweep("biner", biner, k.circle(0.005, 10), soft=0.0)                                       # the carabiner
        k.box("web", (x, -0.13, 0.002), (0.16, 1.5 * IN, 0.004), soft=0.0008)                          # the strap
        k.text("white", "ROGUE", (x, -0.13, 0.0041), 0.028, rx=0.0, depth=0.0004)

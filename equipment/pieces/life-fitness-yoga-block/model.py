"""Life Fitness Yoga Block (refs/: ref_01 one block: grey EVA foam, its long edges chamfered, the LifeFitness script
pressed into a long side). The shop page refuses requests (HTTP 429): the size, 9 x 6 x 3 in (229 x 152 x 76 mm, the
standard block), is an estimate. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Yoga support: under a hand, a hip or the head, turned to give 3, 6 or 9 in.
2. Each mass named (ref_01): one block of grey EVA foam, the long edges chamfered, the ends eased, the script
   pressed into a side.
3. Adjustments. The face it stands on: 76 / 152 / 229 mm.
4. Load path. The hand or body on the foam, the floor.
5. Fit range. Three heights: every user (1.55 / 1.78 / 1.95 m) brings the floor up to the hand. No figure.
6. Size. A pair: one flat, one on its long edge.
Axes: metres, floor z = 0.
"""
import math

IN = 0.0254
A, B, C = 9 * IN, 6 * IN, 3 * IN
CH = 0.008                            # the chamfer

LOOK = {
    "eva": dict(color=(0.11, 0.11, 0.115), rough=0.85, coat=0.0, spec=0.25, bump=(2500, 0.1)),
    "press": dict(color=(0.085, 0.085, 0.09), rough=0.85, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 25, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_block": ((0.0, -0.55, 0.20), (0.0, 0.0, 0.05), 30),         # the flat one's side, the script
}


def block(k, c, sx, sy, sz):
    """A block, its long edges cut at 45 degrees by CH: its section in y-z, extruded along x, the ends eased."""
    hy, hz = sy / 2, sz / 2
    sec = [(hy - CH, -hz), (hy, -hz + CH), (hy, hz - CH), (hy - CH, hz), (-hy + CH, hz), (-hy, hz - CH), (-hy, -hz + CH),
           (-hy + CH, -hz)]
    k.slab("eva", [(c[1] + y, c[2] + z) for y, z in sec], c[0] - sx / 2, c[0] + sx / 2, 0.003, seg=2)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    block(k, (-0.10, 0.0, C / 2), A, B, C)                                                            # flat
    k.text("press", "LifeFitness", (-0.10 + A / 2 - 0.06, -B / 2 - 0.0001, C / 2), 0.016, depth=0.0004)
    block(k, (0.18, 0.0, B / 2), A, C, B)                                                             # on its edge

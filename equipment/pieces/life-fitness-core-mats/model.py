"""Life Fitness Core Mats (refs/: ref_01-03 flat, black and blue, two grommets at one end, the LifeFitness CORE script
by the lower one; ref_04 one of each rolled; ref_05 / ref_06 the corner and grommet close: a soft foam mat, its
corners rounded, a grey core showing at the edge; ref_07 / ref_08 in use). The shop page refuses requests (HTTP 429):
the size, 1.40 x 0.60 m and 15 mm, is an estimate off ref_07 / ref_08 against the user. Built to the two gates and
README point 9 (the shared mat: equipment/blender/mats.py).

DESIGN SPEC (gate 1)
1. Use. Floor work: core, stretching, mobility; hung by the grommets on the mat rack between uses.
2. Each mass named (ref_05): a closed-cell foam mat, 15 mm, a grey layer under the colour, its corners rounded; two steel grommets at the hanging
   end; the script in white.
3. Adjustments. None (two colours, black and blue).
4. Load path. The body on the foam, the floor.
5. Fit range. 1.40 m: the 1.95 m user lying on it has the head and hips on it (the feet off), as ref_08's stretch;
   every user (1.55 / 1.78 / 1.95 m) kneels or planks on it. No figure.
6. Size. Two flat, two rolled (as ref_04).
Axes: metres, floor z = 0; the flat ones along x.
"""
import mats

L, W, T = 1.40, 0.60, 0.015

LOOK = {
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(3000, 0.15)),
    "blue": dict(color=(0.02, 0.10, 0.45), rough=0.8, coat=0.0, spec=0.25, bump=(3000, 0.15)),
    "core": dict(color=(0.12, 0.12, 0.13), rough=0.8, coat=0.0),
    "grommet": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 30, 1.0), "front": (0, 20, 1.0), "side": (90, 20, 1.0), "back_three_quarter": (150, 30, 1.0)}
DETAILS = {
    "detail_corner": ((0.35, -0.95, 0.40), (0.55, -0.45, 0.0), 35),     # the grommets, the script
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for y, col in ((-0.40, "black"), (0.30, "blue")):
        mats.flat(k, col, "grommet", (0.0, y, 0.0), L, W, T, under="core")
        k.text("white", "LifeFitness CORE", (L / 2 - 0.27, y - W / 2 + 0.055, T + 0.0001), 0.036, rx=0.0, depth=0.0004)
    for x, col in ((0.95, "black"), (1.20, "blue")):
        mats.rolled(k, col, "core", (x, 0.0, 0.0), W, 0.075)

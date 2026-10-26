"""Life Fitness Premium Yoga Mat (refs/: ref_01 flat; ref_02 its grommet end from above, two grommets, the LifeFitness
YOGA script by one; ref_03 the grommet and edge close: black, a fine texture, rounded corners; ref_04-07 in use). The
shop page refuses requests (HTTP 429): the size, 1.83 x 0.61 m (72 x 24 in, the yoga standard) and 8 mm, is an
estimate against the user in ref_04-06. Built to the two gates and README point 9 (the shared mat:
equipment/blender/mats.py).

DESIGN SPEC (gate 1)
1. Use. Yoga, stretching, floor work; hung by its grommets on the mat rack.
2. Each mass named (ref_03): a black textured mat, 8 mm, rounded corners, two grommets at one end, the script.
3. Adjustments. None.
4. Load path. The body on the mat, the floor.
5. Fit range. 1.83 m: the 1.95 m user lying on it has head to heel on it but the feet (ref_04's down dog fits every
   user, 1.55-1.95 m). No figure.
6. Size. Two flat, side by side.
Axes: metres, floor z = 0; the mats along x.
"""
import mats

L, W, T = 1.83, 0.61, 0.008

LOOK = {
    "mat": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(4000, 0.2)),
    "grommet": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 30, 1.0), "front": (0, 20, 1.0), "side": (90, 20, 1.0), "back_three_quarter": (150, 30, 1.0)}
DETAILS = {
    "detail_end": ((1.2, -0.75, 0.55), (0.75, -0.35, 0.0), 35),         # the grommet end, the script
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for y in (-0.35, 0.35):
        mats.flat(k, "mat", "grommet", (0.0, y, 0.0), L, W, T)
        k.text("white", "LifeFitness YOGA", (L / 2 - 0.07, y + W / 2 - 0.15, T + 0.0001), 0.026, rx=0.0, rz=1.5708,
               depth=0.0004)

"""Life Fitness Speed Cones, a set of 6 (refs/: ref_01 / ref_02 the six, lime green, numbered 1-6 in black on the
flare, the LifeFitness script up the stem; ref_03 stacked; ref_04 the top close: a flat hexagonal tip; ref_05 in use).
The shop page refuses requests (HTTP 429): the size, about 9 in tall and 6 in across the base, is an estimate against
the user in ref_05. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Agility drills: set out as markers, run round, touched; they stack to put away.
2. Each mass named (ref_02): one moulded cone, a wide flared base curving up into a tall narrow stem, a flat tip; the
   number on the flare, the script up the stem.
3. Adjustments. None.
4. Load path. None: it stands and is knocked over.
5. Fit range. 9 in: touched with a hand from a run by every user (1.55-1.95 m). No figure.
6. Size. Six in an arc, 0.15 x 0.23 m each.
Axes: metres, floor z = 0.
"""
import math

IN = 0.0254
HT, RB, RT = 9 * IN, 3.3 * IN, 0.8 * IN

LOOK = {
    "lime": dict(color=(0.28, 0.60, 0.02), rough=0.55, coat=0.0, spec=0.4),
    "ink": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_cone": ((0.0, -0.55, 0.20), (0.0, -0.10, 0.08), 30),        # a cone's number and stem
}


def radius(t):
    """The cone's radius at height t (0-1): a flare that curves fast into the stem (ref_02)."""
    return RT + (RB - RT) * (1 - t) ** 3.6


def cone(k, x, y, n):
    prof = [(radius(i / 40), HT * i / 40) for i in range(41)]
    k.lathe("lime", (x, y, 0.0), prof, seg=48)                                  # the cone (a hexagon tip: ref_04, left round)
    t = 0.10                                            # the number on the flare's front, laid back with it
    r = radius(t)
    slope = math.atan2(HT * 0.10, radius(0.05) - radius(0.15))
    k.text("ink", str(n), (x, y - r + 0.0015, HT * t), 0.045, rx=slope, depth=0.003)
    k.text("ink", "LifeFitness", (x + radius(0.6) + 0.0003, y, HT * 0.62), 0.011, rz=math.pi / 2, spin=math.pi / 2,
           depth=0.0004)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i in range(6):
        a = math.radians(-50 + 20 * i)
        cone(k, 0.6 * math.sin(a), -0.6 * math.cos(a) + 0.5, i + 1)

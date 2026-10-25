"""Hammer Strength Premium Rubber Black Bumpers, 25 / 35 / 45 / 55 lb (refs/: ref_01-ref_04 the 45 / 25 / 35 / 55 face on
at an angle: black rubber, a large steel hub, HAMMER over it and STRENGTH under it and the weight either side, all
raised in the same black; ref_05 the set small). The shop page refused requests (HTTP 429) after the first fetch, so
the sizes are ours: all 450 mm across (bumpers), the hub 130 mm across read off ref_04, 42 / 55 / 68 / 82 mm thick by
weight against the photos' edges (estimates). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Loaded on 50 mm sleeves, dropped from overhead onto a platform: the rubber takes the impact.
2. Each mass named (ref_01): a solid black rubber disc 450 mm across, its rim rounded; the steel hub set flush in each
   face, a raised rubber ring round it and a lip near the rim, the 50.5 mm bore through it; the markings raised
   tone-on-tone: HAMMER, STRENGTH, the weight twice (upright).
3. Adjustments. None.
4. Load path. The sleeve on the hub; a drop: the rim, the rubber, the platform.
5. Fit range. All at the 450 mm standard: a loaded bar's centre 225 mm up for any user's pull (1.55 / 1.78 / 1.95 m).
6. Size. 450 mm; the four on edge side by side.
Axes: metres, floor z = 0; the plates on edge, faces along x (the front toward -x).
"""
import math

R = 0.225
R_HUB = 0.065                         # the steel hub (ref_04)
R_BORE = 0.02525
PLATES = ((55, 0.082), (45, 0.068), (35, 0.055), (25, 0.042))
GAP = 0.08

LOOK = {
    "rubber": dict(color=(0.013, 0.013, 0.014), rough=0.6, coat=0.05, spec=0.35),
    "raised": dict(color=(0.010, 0.010, 0.011), rough=0.4, coat=0.15, spec=0.45),            # the raised marks
    "hub": dict(color=(0.75, 0.76, 0.77), rough=0.15, metal=1.0, aniso=0.6),
    "hole": dict(color=(0.02, 0.02, 0.02), rough=0.6),
}
VIEWS = {"three_quarter": (-125, 12, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (55, 14, 1.0)}
DETAILS = {
    "detail_face": ((-0.72, -0.20, 0.30), (0.04, 0.0, 0.225), 34),     # ref_04: the 55 at an angle
}


def plate(k, lb, t, x):
    z = R
    k.disc("rubber", (x, 0, z), R, R_HUB, t, axis="x", seg=96, soft=0.008)
    k.disc("hub", (x, 0, z), R_HUB + 0.0005, R_BORE, t - 0.002, axis="x", seg=64, soft=0.001)
    k.disc("hole", (x, 0, z), R_BORE, R_BORE - 0.001, t - 0.002, axis="x", seg=32, soft=0.0)
    for s in (1, -1):                                   # the raised ring round the hub and the lip near the rim
        xf = x + s * (t / 2 + 0.0007)
        k.disc("rubber", (xf, 0, z), 0.098, R_HUB, 0.0014, axis="x", seg=72, soft=0.0004)
        k.disc("rubber", (xf, 0, z), 0.218, 0.207, 0.0014, axis="x", seg=96, soft=0.0004)
    for s in (1, -1):
        xt = x + s * (t / 2 + 0.0004)
        rz = s * math.pi / 2
        side = s                                        # the right as seen from this face
        k.text("raised", "HAMMER", (xt, 0, z + 0.148), 0.066, rz=rz, depth=0.0018)
        k.text("raised", "STRENGTH", (xt, 0, z - 0.148), 0.058, rz=rz, depth=0.0018)
        for sy in (1, -1):
            k.text("raised", str(lb), (xt, sy * side * 0.152, z - 0.006), 0.048, rz=rz, depth=0.0018)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = 0.0
    for lb, t in PLATES:
        plate(k, lb, t, x + t / 2)
        x += t + GAP

"""Eleiko IPF Powerlifting Competition Plates, the 10 / 15 / 20 / 25 kg (refs/: ref_01 the 25 kg's front and back faces
and the four on edge; ref_02 a stack of change plates and a red plate on a floor; ref_03 a lifter holding a 10 kg; and
from the page's gallery the blue 20 kg's back (ELEIKO POWERLIFTING round the rim, the calibration plugs, the rim's
grip notches) and its front close up). Eleiko's page: 450 mm across, 27 mm thick, 25 kg, IPF certified, calibrated
steel. Fetched 2026-10-25 (the page, five of its images, one request each, 6 s apart). Built to the two gates and README
point 9.

DESIGN SPEC (gate 1)
1. Use. Calibrated plates for competition powerlifting: loaded heaviest inside on a 50 mm sleeve, never dropped (they
   are steel); their thinness puts more weight on a sleeve.
2. Each mass named (ref_01): a painted steel disc, the 25 and 20 kg 450 mm across, the 15 kg 400, the 10 kg 325 (read
   off ref_01's edge view against the 450), 27 mm thick for the 25 (Eleiko), the others read off the same view (24 /
   22 / 21 mm); on the front a raised ring round the bore, ELEIKO over and under it, the weight and SWEDEN either side
   (one turned over), the IPF mark; on the back the two calibration plugs either side of the bore and ELEIKO
   POWERLIFTING along the lower rim; two grip notches in the rim.
3. Adjustments. None (the calibration plugs are the factory's).
4. Load path. The sleeve on the bore; the plate's face against the next plate or the collar.
5. Fit range. Picked up by the rim and its notches (ref_03: held at the chest by a 1.7 m lifter); nothing else to fit.
6. Size. 450 mm, 27 mm the 25 kg.
Axes: metres, floor z = 0; the plates on edge, their faces along x (the front toward -x), side by side along x, the
red first.
"""
import math

R_BORE = 0.02525
# (look, kg, radius, thickness), lightest first as in ref_01's edge view
PLATES = (("green", 10, 0.1625, 0.021), ("yellow", 15, 0.200, 0.022), ("blue", 20, 0.225, 0.024),
          ("red", 25, 0.225, 0.027))
GAP = 0.09

LOOK = {
    "green": dict(color=(0.022, 0.040, 0.015), rough=0.35, coat=0.3),                         # painted steel
    "yellow": dict(color=(0.29, 0.20, 0.010), rough=0.35, coat=0.3),
    "blue": dict(color=(0.010, 0.05, 0.20), rough=0.35, coat=0.3),
    "red": dict(color=(0.28, 0.012, 0.025), rough=0.35, coat=0.3),
    "steel": dict(color=(0.75, 0.75, 0.76), rough=0.2, metal=1.0),
    "hole": dict(color=(0.02, 0.02, 0.02), rough=0.6),
    "ink": dict(color=(0.9, 0.9, 0.9), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-125, 12, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (55, 14, 1.0)}
DETAILS = {
    "detail_face": ((-0.76, 0.0, 0.225), (0.0135, 0.0, 0.225), 34),     # ref_01: the red 25's front
    "detail_back": ((1.15, 0.0, 0.17), (0.39, 0.0, 0.16), 30),          # the green 10's back: the plugs, the lettering
}


def plate(k, look, kg, r, t, x):
    z = r
    k.disc(look, (x, 0.0, z), r, R_BORE, t, axis="x", seg=96, soft=0.002)
    k.disc("hole", (x, 0.0, z), R_BORE, R_BORE - 0.001, t, axis="x", seg=32, soft=0.0)
    xf, xb = x - t / 2, x + t / 2                       # the front (-x) and the back
    s = r / 0.225                                       # the markings scale with the plate
    k.disc(look, (xf - 0.0007, 0.0, z), 0.068 * s, R_BORE + 0.004, 0.0014, axis="x", seg=64, soft=0.0003)  # hub ring
    k.disc(look, (xf - 0.0007, 0.0, z), r - 0.002, r - 0.014 * s, 0.0014, axis="x", seg=96, soft=0.0004)   # rim lip
    rz = -math.pi / 2                                   # facing -x
    xt = xf - 0.0003
    k.text("ink", "ELEIKO", (xt, 0.0, z + 0.122 * s), 0.072 * s, rz=rz, depth=0.0008)
    k.text("ink", "ELEIKO", (xt, 0.0, z - 0.122 * s), 0.072 * s, rz=rz, spin=math.pi, depth=0.0008)
    k.text("ink", str(kg), (xt, -0.14 * s, z + 0.01 * s), 0.058 * s, rz=rz, depth=0.0008)          # on the right
    k.text("ink", "SWEDEN", (xt, -0.14 * s, z - 0.033 * s), 0.015 * s, rz=rz, depth=0.0006)
    k.text("ink", str(kg), (xt, 0.14 * s, z - 0.01 * s), 0.058 * s, rz=rz, spin=math.pi, depth=0.0008)
    k.text("ink", "SWEDEN", (xt, 0.14 * s, z + 0.033 * s), 0.015 * s, rz=rz, spin=math.pi, depth=0.0006)
    k.text("ink", "IPF", (xt, -0.125 * s, z + 0.07 * s), 0.02 * s, rz=rz, depth=0.0006)
    for sy in (1, -1):                                  # the back: the calibration plugs, the lettering, the notches
        k.cyl("steel", (xb + 0.0004, sy * 0.07 * s, z), 0.011, 0.0012, axis="x", seg=24, soft=0.0003)
    k.text("ink", "ELEIKO POWERLIFTING", (xb + 0.0003, 0.0, z - 0.19 * s), 0.016 * s, rz=math.pi / 2, depth=0.0005)
    for a in (math.radians(35), math.radians(145)):     # the rim's grip notches (ref: the blue's rim)
        k.box("hole", (x, r * math.cos(a) * 0.985, z + r * math.sin(a) * 0.985), (t + 0.001, 0.02, 0.006),
              rx=a - math.pi / 2, soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = 0.0
    for look, kg, r, t in PLATES[::-1]:               # the red first, its front clear
        plate(k, look, kg, r, t, x + t / 2)
        x += t + GAP

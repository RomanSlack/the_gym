"""Eleiko IWF Weightlifting Competition Plates, the 10 / 15 / 20 / 25 kg set (refs/: ref_01 the 25 kg face on: ELEIKO
over and under the hub, 25 SWEDEN each side, the IWF mark, COMPETITION; ref_02 the four on edge, green / yellow / blue /
red, their rounded rims; ref_03 / ref_04 in competition). Eleiko's page: 450 mm across, a 50.5 mm centre hole, 35 /
39 / 50 / 58 mm thick, solid rubber with zinced steel hubs. Fetched 2026-10-24 / 25 (the page and three of its images,
one request each, 6 s apart). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Loaded on a 50 mm sleeve, heaviest inside; dropped from overhead onto a platform, the rubber takes the impact.
2. Each mass named (ref_01 / ref_02): the plate a solid coloured rubber disc 450 mm across, its rim rounded; the hub a
   zinced steel disc set flush in each face, the 50.5 mm bore through it; the markings in white: ELEIKO over and under
   the hub, the weight with SWEDEN on each side (one upright, one turned over), the IWF mark, COMPETITION.
3. Adjustments. None.
4. Load path. The sleeve on the hub's bore, the hub bonded in the rubber; a drop: the rim, the rubber, the platform.
5. Fit range. A 25 kg plate is lifted by its rim from the floor (no handle); all 450 mm, so a loaded bar's centre is
   225 mm up at any user's (1.55 / 1.78 / 1.95 m) pull. No figure.
6. Size. Each 450 mm; the four on edge side by side (ref_02).
Axes: metres, floor z = 0; the plates on edge, their faces along x, side by side along x.
"""
import math

R = 0.225
R_HUB = 0.100
R_BORE = 0.02525
PLATES = (("green", 10, 0.035), ("yellow", 15, 0.039), ("blue", 20, 0.050), ("red", 25, 0.058))
GAP = 0.09

LOOK = {
    "green": dict(color=(0.006, 0.042, 0.015), rough=0.55, coat=0.1),                           # Eleiko's deep colours
    "yellow": dict(color=(0.30, 0.20, 0.012), rough=0.55, coat=0.1),
    "blue": dict(color=(0.004, 0.015, 0.075), rough=0.55, coat=0.1),
    "red": dict(color=(0.09, 0.006, 0.008), rough=0.55, coat=0.1),
    "hub": dict(color=(0.78, 0.79, 0.8), rough=0.12, metal=1.0, aniso=0.6),                    # zinced, spun
    "hole": dict(color=(0.02, 0.02, 0.02), rough=0.6),
    "ink": dict(color=(0.88, 0.88, 0.88), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (145, 14, 1.0)}
DETAILS = {
    "detail_face": ((1.18, 0.0, 0.23), (0.42, 0.0, 0.23), 34),          # ref_01: the red 25 face on
    "detail_rims": ((0.20, -0.85, 0.30), (0.25, 0.0, 0.23), 35),        # ref_02: the rims side by side
}


def plate(k, look, kg, t, x):
    z = R
    k.disc(look, (x, 0.0, z), R, R_HUB, t, axis="x", seg=96, soft=0.008)                    # the rubber, rounded rim
    k.disc("hub", (x, 0.0, z), R_HUB + 0.0005, R_BORE, t - 0.002, axis="x", seg=64, soft=0.001)
    k.disc("hole", (x, 0.0, z), R_BORE, R_BORE - 0.001, t - 0.002, axis="x", seg=32, soft=0.0)
    for s in (1, -1):                                   # the markings on each face
        xf = x + s * (t / 2 + 0.0003)
        rz = s * math.pi / 2
        k.text("ink", "ELEIKO", (xf, 0.0, z + 0.163), 0.048, rz=rz, depth=0.0006)
        k.text("ink", "ELEIKO", (xf, 0.0, z - 0.163), 0.048, rz=rz, spin=math.pi, depth=0.0006)
        side = s                                        # the upright weight on the right as seen from this face
        k.text("ink", str(kg), (xf, side * 0.163, z + 0.008), 0.04, rz=rz, depth=0.0006)
        k.text("ink", "SWEDEN", (xf, side * 0.163, z - 0.024), 0.012, rz=rz, depth=0.0006)
        k.text("ink", str(kg), (xf, -side * 0.163, z - 0.008), 0.04, rz=rz, spin=math.pi, depth=0.0006)
        k.text("ink", "SWEDEN", (xf, -side * 0.163, z + 0.024), 0.012, rz=rz, spin=math.pi, depth=0.0006)
        k.text("ink", "IWF", (xf, side * 0.125, z + 0.06), 0.011, rz=rz, depth=0.0006)
        k.disc("ink", (xf, side * 0.125, z + 0.085), 0.011, 0.008, 0.0006, axis="x", seg=24, soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = 0.0
    for look, kg, t in PLATES:
        plate(k, look, kg, t, x + t / 2)
        x += t + GAP

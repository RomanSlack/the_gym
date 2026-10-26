"""Hammer Strength 4-Sided Urethane Dumbbells, a 5-75 lb set in 5 lb pairs (refs/: ref_01 a 50 lb: the head round with
four flats, a textured patch on each flat, HAMMER STRENGTH and 50 raised in grey, 22.7 KG on the inner face, the chrome
hub; ref_02 the 5 / 30 / 50; ref_03-ref_14 in use and on the three-tier rack). The shop refused further requests
(HTTP 429): the sizes are ours against ref_01's 50 lb (estimates): its head 160 mm across and 85 mm thick, the heads
growing with the cube root of the weight, a 5 in knurled chrome handle 33 mm thick. Built to the two gates and README
point 9 on the shared builder (equipment/blender/hs_urethane.py, which the rack loads too).

DESIGN SPEC (gate 1)
1. Use. Lifted by the handle for presses, rows, curls, carries; set down on a flat of the heads (they don't roll) or
   racked on the three-tier rack (its own piece).
2. Each mass named (ref_01): the handle, chrome steel, knurled between the heads; the two heads, steel cores in black
   urethane, round with four flats, a textured patch on each flat, the markings raised in grey (HAMMER STRENGTH and
   the pounds outside, the kilos inside), the chrome hub on each inner face.
3. Adjustments. None (a weight per pair).
4. Load path. The hand on the knurl, the handle, the heads' cores.
5. Fit range. The handle's 127 mm between the heads takes any user's (1.55 / 1.78 / 1.95 m) palm (85-105 mm across);
   its 33 mm fills the grip.
6. Size. 15 pairs, 5-75 lb; on the floor in three rows of five pairs, the handles across.
Axes: metres, floor z = 0; the rows along x, the handles along y.
"""
import hs_urethane as hs

WEIGHTS = tuple(range(5, 80, 5))
LOOK = dict(hs.LOOK)
VIEWS = {"three_quarter": (-35, 30, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "back_three_quarter": (150, 30, 1.0)}
DETAILS = {
    "detail_head": ((-0.55, -0.60, 0.30), (-0.25, -0.30, 0.06), 35),    # ref_01: a head's outer face
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for row in range(3):                                # three rows of five pairs, the lightest in front
        x = -0.75
        y = -0.45 + row * 0.45
        for lb in WEIGHTS[row * 5:(row + 1) * 5]:
            s, t = hs.size(lb)
            for _ in range(2):
                x += s / 2
                hs.dumbbell(k, lb, (x, y, hs.height(lb)), axis="y")
                x += s / 2 + 0.015
            x += 0.04

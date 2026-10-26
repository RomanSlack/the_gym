"""Hammer Strength stability ball (refs/: ref_01 the 75 cm: black, matte, panel seams down it from a cap at the top with
HS on it, HAMMER STRENGTH and 75 cm in white on its side). The linked page (shop.lifefitness.com) has rate-limited us:
the sizes 55 / 65 / 75 cm are the usual three and ref_01 shows the 75; estimates. Built to the two gates and README
point 9 (wrapped lettering: equipment/blender/balls.py).

DESIGN SPEC (gate 1)
1. Use. Core and balance work: sitting, bridging, rollouts, a bench for dumbbell presses.
2. Each mass named (ref_01): an inflated PVC ball, its eight panel seams from the cap round the top, settled a little
   flat where it rests; HS on the cap, HAMMER STRENGTH and its size on the side.
3. Adjustments. The size (and the inflation).
4. Load path. The body on the ball, the air, the floor.
5. Fit range. Sitting with the thighs level the seat wants about 0.25 H: 55 cm for the 1.55 m user, 65 for the 1.78,
   75 for the 1.95 (0.35-0.38 H across the ball; it settles under the user). No figure.
6. Size. Three balls in a row, 0.55 / 0.65 / 0.75 m.
Axes: metres, floor z = 0; the row along x, the lettering toward -y.
"""
import math
import balls

SIZES = (55, 65, 75)
SETTLE = 0.96                         # height over width, resting

LOOK = {
    "pvc": dict(color=(0.012, 0.012, 0.013), rough=0.55, coat=0.0, spec=0.35, bump=(1200, 0.02)),
    "seam": dict(color=(0.008, 0.008, 0.009), rough=0.5, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 15, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_ball": ((1.75, -1.75, 0.55), (1.065, 0.0, 0.36), 30),          # the 75 cm, as ref_01
}


def ball(k, x, cm):
    r = cm / 200
    c = (x, 0.0, r)
    k.sphere("pvc", c, r, seg=72, soft=0.002)
    for i in range(4):                                  # eight panel seams (four great circles through the cap)
        balls.seam(k, "seam", c, r, math.pi / 4 * i + math.pi / 8, w=0.004, h=0.0008)
    k.cyl("pvc", (x, 0.0, 2 * r + 0.0004), 0.05, 0.0012, seg=40, soft=0.0)                         # the cap
    k.text("white", "HS", (x, 0.0, 2 * r + 0.0012), 0.035, rx=0.0, depth=0.0004)
    balls.band(k, "seam", c, r, 0.0, 0.004, h=0.0008)                                               # the middle seam
    f = r / 0.375                                       # the print scaled to the ball (ref_01 on the 75)
    for text, size, lat in (("HAMMER", 0.07, 0.22), ("STRENGTH", 0.07, 0.07), (f"{cm}", 0.17, -0.17)):
        balls.label(k, "white", text, c, r + 0.001, size * f, lat=lat, lon=math.radians(25), depth=0.0006)
    balls.label(k, "white", "CM", c, r + 0.001, 0.025 * f, lat=-0.26, lon=math.radians(25) + 0.30, depth=0.0006)
    return c, r


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = -0.75
    placed = []
    for cm in SIZES:
        r = cm / 200
        x += r
        placed.append(ball(k, x, cm))
        x += r + 0.12
    for g in k.groups.values():                         # settled: squashed toward the floor
        for v in g.verts:
            v.co.z *= SETTLE

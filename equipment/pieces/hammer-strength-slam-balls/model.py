"""Hammer Strength slam balls (refs/: ref_01 the 15 lb face on: black rubber, its surface in dimpled panels framed by
smooth raised channels, a smooth disc at each face's middle, HAMMER / 15 lb / STRENGTH in grey on
the front disc; ref_02 the 5 / 10 / 15 on the floor, one size; ref_03 slammed). The linked page (shop.lifefitness.com)
has rate-limited us: the weights 5-30 lb in 5 lb steps and the 9 in (229 mm) size are estimates off ref_02. Built to
the two gates and README point 9 (wrapped lettering: equipment/blender/balls.py).

DESIGN SPEC (gate 1)
1. Use. Slams: overhead, then thrown into the floor; it doesn't bounce.
2. Each mass named (ref_01): a ball of thick black rubber (sand-filled), 9 in, its dimpled panels, two smooth channels
   over it at right angles, a smooth disc at each of the six face middles, the lettering on the front disc.
3. Adjustments. None: a weight per ball.
4. Load path. Both hands round it overhead, then the floor.
5. Fit range. 9 in across: every user (1.55 / 1.78 / 1.95 m) holds it overhead in two hands. No figure.
6. Size. Six balls in a row, 229 mm each.
Axes: metres, floor z = 0; the row along x, the lettering toward -y.
"""
import math
import balls

IN = 0.0254
R = 9 * IN / 2
WEIGHTS = (5, 10, 15, 20, 25, 30)

LOOK = {
    "dimple": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.3, bump=(450, 0.9)),
    "smooth": dict(color=(0.014, 0.014, 0.015), rough=0.45, coat=0.0, spec=0.4),
    "grey": dict(color=(0.32, 0.33, 0.35), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 15, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_ball": ((-0.14, -0.75, 0.15), (-0.14, 0.0, 0.11), 30),           # the 15 lb face on, as ref_01
}


def ball(k, x, lb):
    c = (x, 0.0, R)
    k.sphere("dimple", c, R, seg=64, soft=0.002)
    for lon in (math.radians(45), math.radians(135)):   # the smooth channels, a cube's pattern
        balls.seam(k, "smooth", c, R, lon, w=0.018, h=0.0008)
    for lat, lon in ((0, 0), (0, math.pi / 2), (0, math.pi), (0, -math.pi / 2), (math.pi / 2, 0)):  # the face discs
        n = balls.normal(lat, lon)
        p = tuple(c[i] + n[i] * R for i in range(3))
        ax = "z" if lat else ("y" if lon in (0, math.pi) else "x")
        balls.wrap(k, "smooth", 0.0, c, R, n, lambda p=p, ax=ax: k.cyl("smooth", p, R * 0.40, 0.0016, axis=ax, seg=48, soft=0.0))
    for text, size, lat in (("HAMMER", 0.021, 0.20), (f"{lb}lb", 0.036, 0.0), ("STRENGTH", 0.019, -0.21)):
        balls.label(k, "grey", text, c, R + 0.0015, size, lat=lat, lon=0.0, depth=0.0006)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, lb in enumerate(WEIGHTS):
        ball(k, (i - 2.5) * (2 * R + 0.06), lb)

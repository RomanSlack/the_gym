"""Escape Endura wall balls (refs/: ref_01 / ref_03 the range, black, stitched panels, the weight big in white inside
a shield outline, a small red Escape tag under it; ref_02 the shield close). The linked page (shop.lifefitness.com)
has rate-limited us: the brief asks 4-14 kg; the refs are the lb range. The size, 14 in for every weight (the wall
ball standard), and the panel pattern read off the refs; estimates. Built to the two gates and README point 9
(wrapped print: equipment/blender/balls.py).

DESIGN SPEC (gate 1)
1. Use. Wall balls: squat with the ball at the chest, drive it up to a target 3 m (10 ft) up, catch it into the next
   squat; also throws and carries.
2. Each mass named (ref_01 / ref_02): a soft ball, 14 in, a textured synthetic leather cover in stitched panels, the
   seams sunk; on one panel the shield outline with the weight and its unit; the red tag under it.
3. Adjustments. None: a weight per ball, 4 / 6 / 8 / 10 / 12 / 14 kg.
4. Load path. Both hands under it at the chest, the throw, the catch.
5. Fit range. 14 in: every user (1.55 / 1.78 / 1.95 m) holds it at the chest, elbows under. No figure.
6. Size. Six balls in two rows, 0.356 m each.
Axes: metres, floor z = 0; the shields toward -y.
"""
import math
from mathutils import Vector
import balls

IN = 0.0254
R = 14 * IN / 2
WEIGHTS = (4, 6, 8, 10, 12, 14)

LOOK = {
    "cover": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "seam": dict(color=(0.004, 0.004, 0.005), rough=0.9, coat=0.0),
    "white": dict(color=(0.78, 0.78, 0.78), rough=0.6, coat=0.0),
    "red": dict(color=(0.5, 0.03, 0.03), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_shield": ((-0.40, -0.85, 0.30), (-0.40, -0.20, 0.18), 30),  # a shield, as ref_02
}


def shield(k, c, n, size):
    """The shield outline on the tangent plane at c + n R (flat, then wrapped)."""
    w, h = size, size * 1.15
    side = [(0.50, 0.50), (0.49, 0.20), (0.44, -0.05), (0.34, -0.25), (0.19, -0.41), (0.0, -0.50)]   # ref_02's shield
    pts2 = [(w * x, h * y) for x, y in side] + [(-w * x, h * y) for x, y in side[-2::-1]]
    e = Vector((n.y * -1, n.x, 0.0)).normalized() if abs(n.z) < 0.99 else Vector((1, 0, 0))   # across
    if e.dot(Vector((1, 0, 0))) < 0 and abs(n.y) > 0.5:
        e = -e
    u = n.cross(e).normalized() * -1                    # up the panel
    if u.z < 0:
        u = -u
    p0 = Vector(c) + n * (R + 0.0005)
    ring = pts2 + pts2[:1]
    dense = []                                          # dense enough to wrap without chords sinking
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        for i in range(12):
            t = i / 12
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    dense.append(ring[-1])
    path = [tuple(p0 + e * x + u * y) for x, y in dense]
    balls.wrap(k, "white", 0, c, R, n, lambda: k.sweep("white", path, k.rect(0.004, 0.001, 0.0003), up=tuple(n), soft=0.0))


def ball(k, x, y, kg):
    c = (x, y, R)
    k.sphere("cover", c, R, seg=64, soft=0.002)
    for lon in (0.0, math.pi / 3, 2 * math.pi / 3):     # the panels' stitched seams
        balls.seam(k, "seam", c, R, lon + math.pi / 6, w=0.003, h=0.0006)
    for lat in (math.radians(35), math.radians(-35)):
        balls.band(k, "seam", c, R, lat, 0.003, h=0.0006)
    n = balls.normal(0.05, 0.0)
    shield(k, c, n, 0.17)
    balls.label(k, "white", str(kg), c, R + 0.0006, 0.10, lat=0.16, lon=0.0, depth=0.0006)
    balls.label(k, "white", "kg", c, R + 0.0006, 0.028, lat=-0.12, lon=0.0, depth=0.0005)
    balls.wrap(k, "red", 0, c, R, balls.normal(-0.55, 0.0),
               lambda: k.box("red", tuple(Vector(c) + balls.normal(-0.55, 0.0) * (R + 0.0006)), (0.035, 0.0012, 0.008),
                             rx=-0.55, soft=0.0))


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, kg in enumerate(WEIGHTS):
        row, col = divmod(i, 3)
        ball(k, (col - 1) * (2 * R + 0.06) + row * 0.20, row * (2 * R + 0.10), kg)

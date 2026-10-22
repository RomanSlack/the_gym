"""Titan Fitness Deadlift Pulling Blocks, the pair, set to a mid height.

Built by eye from Titan's photos (refs/: ref_01 the pair, ref_02 in use, ref_03-ref_06 the cradle, pin and post up
close).
Axes: metres, floor z = 0, the bar would run along x through both cradles; each block's foot runs along y.
Each: a 2 x 3 in foot with gloss end caps, a 3 x 3 in post welded on its middle (a hole row), a 2.5 in inner post
sliding in it set by a pop pin with a D ring, a collar plate on top carrying a short round cradle the bar's sleeve
sits in, a T screw through the cradle's side; TITAN FITNESS on the foot.
"""
IN = 0.0254
LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.015), rough=0.5, metal=0.1, coat=0.0, bump=(1400, 0.06)),   # black textured coat
    "cap": dict(color=(0.010, 0.010, 0.011), rough=0.3, coat=0.2),
    "hole": dict(color=(0.003, 0.003, 0.003), rough=0.9, coat=0.0),
    "white": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-50, 20, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (140, 20, 1.0)}
DETAILS = {"detail_cradle": ((-0.75, -0.35, 0.55), (-0.40, 0.0, 0.40), 45)}

PAIR_X = 0.40                    # each block's centre off the middle (x)
FOOT_L, FOOT = 0.40, (3 * IN, 2 * IN)   # foot length (y), section across (x) x tall
POST, INNER = 3 * IN, 2.5 * IN
POST_TOP, INNER_TOP = 0.33, 0.42


def block(k, x):
    Z = (0, 0, 1)
    fz = 0.003 + FOOT[1] / 2
    k.bar("frame", (x, -FOOT_L / 2 + 0.02, fz), (x, FOOT_L / 2 - 0.02, fz), FOOT[0], FOOT[1], up=Z)
    for d in (1, -1):
        k.box("cap", (x, d * (FOOT_L / 2 - 0.025), fz - 0.0015), (FOOT[0] + 0.006, 0.05, FOOT[1] + 0.003), soft=0.004)
    ft = 0.003 + FOOT[1]
    k.bar("frame", (x, 0, ft), (x, 0, POST_TOP), POST, POST, up=(0, 1, 0), cut0=((0, 0, ft), Z), weld=True)
    k.bar("frame", (x, 0, POST_TOP - 0.10), (x, 0, INNER_TOP), INNER, INNER, up=(0, 1, 0))
    k.box("frame", (x, 0, POST_TOP + 0.002), (POST + 0.004, POST + 0.004, 0.004), soft=0.001)        # the post's lip
    for i in range(4):                                               # the hole rows, the face along the bar
        k.cyl("hole", (x - POST / 2 - 0.0005, 0, 0.12 + i * 0.045), 0.006, 0.001, axis="x", seg=14)
    for i in range(2):
        k.cyl("hole", (x - INNER / 2 - 0.0005, 0, POST_TOP + 0.035 + i * 0.03), 0.005, 0.001, axis="x", seg=14)
    # the pop pin on the post's side: a boss, the pin, its D ring
    py = POST / 2
    k.box("frame", (x, py + 0.008, POST_TOP - 0.07), (0.03, 0.016, 0.03), soft=0.003)
    k.tube("steel", (x, py + 0.016, POST_TOP - 0.07), (x, py + 0.03, POST_TOP - 0.07), 0.006)
    ring = [(x + 0.0, py + 0.03, POST_TOP - 0.07 + 0.012)] + [(x, py + 0.03 + 0.022 * __import__("math").sin(a / 8 * 3.1416),
            POST_TOP - 0.07 + 0.012 - 0.024 * a / 8) for a in range(1, 8)] + [(x, py + 0.03, POST_TOP - 0.07 - 0.012)]
    k.sweep("frame", ring, k.circle(0.0035, 8))
    # the collar plate and the cradle (a short pipe along x), its T screw
    k.box("frame", (x, 0, INNER_TOP + 0.005), (0.075, 0.075, 0.01), soft=0.002)
    cz = INNER_TOP + 0.01 + 0.034
    k.disc("frame", (x, 0, cz), 0.034, 0.027, 0.07, axis="x")
    k.tube("steel", (x, 0.034, cz + 0.006), (x, 0.05, cz + 0.006), 0.004)
    k.box("frame", (x, 0.054, cz + 0.006), (0.03, 0.008, 0.01), soft=0.003)
    # the logo on the foot's face along the bar
    k.text("white", "TITAN", (x - FOOT[0] / 2 - 0.0005, -0.08, fz + 0.007), 0.024, rz=-1.5708, depth=0.0006)
    k.text("red", "FITNESS", (x - FOOT[0] / 2 - 0.0005, -0.08, fz - 0.012), 0.012, rz=-1.5708, depth=0.0006)


def build(k):
    for s in (1, -1):
        block(k, s * PAIR_X)

"""Life Fitness Dual-Height Hex Bar, lying on the floor high handles up.

Built by eye from Life Fitness's photos (refs/: ref_01 from the front, ref_02 from above at an angle, ref_03 the Y, its
plate and a loop handle up close), held to Life Fitness's spec: 7 ft long, 16.625 in loadable sleeves, 1.9 in grips,
no knurl.
Axes: metres, floor z = 0, the bar along x (the sleeves at +-x), the lifter stands in the hexagon facing -y.
Structure: the hexagon of round tube in two halves meeting at a Y each end, a plate across the inside of each Y, a
stub tube from the Y to the collar, the sleeve; at each side a straight low grip across the hexagon and a raised loop
grip over it (flip the bar for the other height). All matte black.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.016, 0.016, 0.017), rough=0.55, metal=0.2, coat=0.0, bump=(1200, 0.07)),   # black textured coat
}
VIEWS = {"three_quarter": (-35, 28, 1.2), "front": (0, 8, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 30, 1.2)}
DETAILS = {"detail_y": ((0.85, -0.45, 0.32), (0.52, 0.0, 0.07), 45)}      # the Y, its plate, the loop beside it (ref_03)

L = 7 * 12 * IN                 # overall
SLEEVE = 16.625 * IN            # loadable
R_COL = 0.042                   # the collar's radius: the bar lies on its collars
Z0 = R_COL                      # the hexagon's plane
FR = 0.0175                     # frame tube radius
GR = 1.9 * IN / 2               # the grips
APEX, SHX, HY = 0.545, 0.29, 0.275   # the Y's apex (x), the shoulders (x), the long sides (y)
GX = 0.235                      # the grips (x)
LOOP_H = 0.13                   # the raised grip over the low one


def build(k):
    # the hexagon: two halves, rounded at the shoulders, meeting sharp at each Y
    for s in (1, -1):
        k.sweep("frame", [(-APEX, 0, Z0), (-SHX, s * HY, Z0), (SHX, s * HY, Z0), (APEX, 0, Z0)], k.circle(FR, 28), bend=0.07)
    x_col = L / 2 - SLEEVE - 0.012
    for s in (1, -1):
        # the plate across the inside of the Y, the stub out to the collar, the collar, the sleeve and its end
        k.box("frame", (s * (APEX - 0.022), 0, Z0), (0.008, 0.075, 0.055), soft=0.002)
        k.tube("frame", (s * (APEX - 0.018), 0, Z0), (s * x_col, 0, Z0), 0.0225, seg=32)
        k.cyl("frame", (s * (x_col + 0.006), 0, Z0), R_COL, 0.012, axis="x", seg=48, soft=0.002)
        k.tube("frame", (s * (x_col + 0.012), 0, Z0), (s * L / 2, 0, Z0), 0.025, seg=40)
        k.disc("frame", (s * (L / 2 + 0.0005), 0, Z0), 0.025, 0.019, 0.001, axis="x", seg=40)
        # the low grip straight across, the raised loop over it, its legs landing on the long sides
        k.tube("frame", (s * GX, -HY, Z0), (s * GX, HY, Z0), GR, seg=32)
        k.sweep("frame", [(s * GX, -HY, Z0), (s * GX, -HY, Z0 + LOOP_H), (s * GX, HY, Z0 + LOOP_H), (s * GX, HY, Z0)],
                k.circle(GR, 32), bend=0.075)

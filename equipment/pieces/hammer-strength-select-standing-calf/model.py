"""Hammer Strength Select Standing Calf, Charcoal frame / Black upholstery, the lever down at rest.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit photographed
all round at Fitness Equipment Empire (ref_02 / ref_07 / ref_08 front three-quarters, ref_04 / ref_06 the tower's front
and the pivot close up, ref_03 the plates' printed weights, ref_09-11 the back, the side, the base and toe plate),
held to Life Fitness's 58 x 45 x 72 in (148 x 114 x 183 cm, L x W x H). The stack is 20 plates of 20 lb numbered 10
to 390 (ref_03).
Axes: metres, floor z = 0, the user stands on the toe plate at -y facing +y (the column), shoulders under the pads;
the tower stands at +x beside the column, its front facing -y like the pads (ref_11: from the user's side the tower
hides behind the column).
Structure: the stack tower (shared builder, "open" style) beside the column; the column tied to the tower's near post
top and bottom; the base: a rail forward from the column's foot to the toe plate, a brace from the column down to it;
the lever on its pivot bracket half way up the column, reaching forward to a sleeve; the adjustment tube up through the
sleeve (its row of holes, the pop pin) to the yoke and the two shoulder pads; the cable from the lever down to a
pulley at the column's foot and over to the tower.
"""
import math

import stack_tower

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7, coat=0.0),
    "plate": dict(color=(0.04, 0.04, 0.042), rough=0.45, metal=0.3, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (25, 14, 1.0), "front": (0, 5, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (140, 16, 1.0)}
DETAILS = {"detail_pivot": ((-0.75, -0.85, 1.30), (0.0, -0.05, 1.05), 45)}   # the pivot, the sleeve, the pop pin, the yoke

TOWER = dict(style="open", W=0.56, D=0.30, H=72 * IN, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="STANDING CALF RAISE", brand="HAMMER STRENGTH", round=1, step=20, start=-10)
TC = (0.40, 0.12)
FOOT_H = 0.015
T = 0.076
COL = (0.0, 0.12)                   # the column (x, y)
COL_H = 1.62
PIV = (COL[1] - T / 2 - 0.05, 1.00)  # the lever's pivot (y, z), on a bracket on the column's front
SLEEVE = (-0.22, 1.00)               # the lever's sleeve (y, z)
YOKE_Z = 1.44
Y_TOE = -0.48


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (0.09, 0.09, FOOT_H), soft=0.003)


def build(k):
    Z = (0, 0, 1)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    xp = TC[0] - TOWER["W"] / 2 + 0.038                    # the tower's near posts (x)
    cx, cy = COL
    # ---- the column on its foot plate, capped; tied to the tower's near post top and bottom
    k.box("frame", (cx, cy, FOOT_H / 2 + 0.005), (0.16, 0.16, FOOT_H + 0.01), soft=0.002)
    foot(k, cx, cy)
    k.bar("frame", (cx, cy, FOOT_H + 0.01), (cx, cy, COL_H), T, T, cut0=((0, 0, FOOT_H + 0.01), Z), weld=True)
    k.box("plastic", (cx, cy, COL_H + 0.005), (T + 0.004, T + 0.004, 0.01), soft=0.002)
    for z in (0.30, COL_H - 0.10):
        for y_ in (TC[1] - TOWER["D"] / 2 + 0.025, TC[1] + TOWER["D"] / 2 - 0.025):
            k.bar("frame", (cx + T / 2, y_, z), (xp - 0.038, y_, z), 0.05, 0.05,
                  cut0=((cx + T / 2, 0, 0), (1, 0, 0)), cut1=((xp - 0.038, 0, 0), (1, 0, 0)), weld=True)
    u = k                    # (the user's side: the pads and the toe plate face -y like the tower's front, ref_01 / ref_11)
    # ---- the base: a rail forward from the column's foot to the toe plate, cross feet; the brace from the column down
    u.bar("frame", (cx, cy - 0.08, FOOT_H + 0.035), (cx, Y_TOE - 0.24, FOOT_H + 0.035), T, 0.05, r=0.006)
    u.box("plastic", (cx, Y_TOE - 0.244, FOOT_H + 0.035), (T + 0.004, 0.008, 0.054), soft=0.002)
    u.bar("frame", (-0.30, Y_TOE - 0.18, FOOT_H + 0.035), (0.30, Y_TOE - 0.18, FOOT_H + 0.035), T, 0.05, r=0.006)
    for s in (1, -1):
        foot(k, s * 0.26, Y_TOE - 0.18)
        u.box("plastic", (s * 0.304, Y_TOE - 0.18, FOOT_H + 0.035), (0.008, T + 0.004, 0.054), soft=0.002)
    b0 = (cx, cy - T / 2, 0.78)
    b1 = (cx, Y_TOE + 0.05, FOOT_H + 0.06)
    u.bar("frame", b0, b1, 0.06, 0.06, up=(1, 0, 0), cut0=((0, cy - T / 2, 0), (0, 1, 0)), cut1=((0, 0, FOOT_H + 0.06), Z), weld=True)
    # the toe plate: a grit platform across the rail, the raised toe block at its back edge
    u.box("frame", (cx, Y_TOE - 0.05, 0.11), (0.08, 0.30, 0.13), soft=0.004)
    u.box("lever", (cx, Y_TOE - 0.05, 0.185), (0.60, 0.34, 0.02), soft=0.004)
    u.box("grip", (cx, Y_TOE - 0.07, 0.197), (0.58, 0.28, 0.004), soft=0.001)
    u.box("lever", (cx, Y_TOE + 0.08, 0.225), (0.58, 0.07, 0.06), rx=-0.35, soft=0.008)
    # ---- the lever: its pivot bracket on the column, the arm forward to the sleeve, the adjustment tube to the yoke
    u.box("frame", (cx, cy - T / 2 - 0.025, PIV[1]), (0.12, 0.05, 0.16), soft=0.003)
    u.tube("steel", (cx - 0.07, PIV[0], PIV[1]), (cx + 0.07, PIV[0], PIV[1]), 0.018, seg=18)
    for s in (1, -1):
        u.bolt((s * 0.07, PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.022)
        u.box("lever", (s * 0.045, (PIV[0] + SLEEVE[0]) / 2, PIV[1]), (0.012, abs(SLEEVE[0] - PIV[0]) + 0.06, 0.10), soft=0.002)
    u.box("warn", (0.052, (PIV[0] + SLEEVE[0]) / 2, PIV[1] + 0.02), (0.002, 0.05, 0.04), soft=0.0)
    sy, sz = SLEEVE
    u.box("lever", (cx, sy, sz + 0.05), (0.078, 0.078, 0.22), soft=0.003)                       # the sleeve
    u.bar("steel", (cx, sy, sz - 0.12), (cx, sy, YOKE_Z - 0.03), 0.06, 0.06, r=0.004)           # the adjustment tube
    for i in range(7):
        u.cyl("hole", (cx, sy - 0.0305, sz + 0.20 + i * 0.03), 0.006, 0.001, axis="y", seg=12, soft=0.0)
    u.tube("steel", (cx, sy - 0.039, sz + 0.12), (cx, sy - 0.09, sz + 0.12), 0.007, seg=12)
    u.cyl("redplastic", (cx, sy - 0.10, sz + 0.12), 0.017, 0.024, axis="y", seg=20, soft=0.004)
    # the yoke: a cross bar on the tube's top, the arms forward, the two shoulder pads; grips at its ends
    u.box("lever", (cx, sy, YOKE_Z), (0.40, 0.08, 0.06), soft=0.004)
    for s in (1, -1):
        x = s * 0.15
        u.bar("lever", (x, sy - 0.04, YOKE_Z), (x, sy - 0.30, YOKE_Z), 0.05, 0.05, cut0=((0, sy - 0.04, 0), (0, 1, 0)), weld=True)
        u.pad("pad", (x, sy - 0.20, YOKE_Z - 0.06), (0.14, 0.28, 0.07), r=0.03)
        g0, g1 = (s * 0.20, sy, YOKE_Z), (s * 0.30, sy - 0.04, YOKE_Z - 0.10)
        u.sweep("lever", [g0, (s * 0.27, sy, YOKE_Z), g1], u.circle(0.014, 16), bend=0.03, soft=0.0015)
        u.tube("rubber", (s * 0.275, sy - 0.01, YOKE_Z - 0.03), g1, 0.02, seg=20)
    # ---- the cable: from the lever's arm down to a pulley at the column's foot, across to the tower's foot, up its
    # near post to its top pulley
    u.box("frame", (cx, cy - T / 2 - 0.03, 0.14), (0.06, 0.06, 0.10), soft=0.002)
    u.pulley((cx, cy - T / 2 - 0.06, 0.16), 0.04, axis="x")
    u.cable([(cx, (PIV[0] + sy) / 2, PIV[1] - 0.05), (cx, cy - T / 2 - 0.06 - 0.04, 0.17), (cx, cy - T / 2 - 0.02, 0.12)])
    ox, oy, oz = tw["cable"]
    xq = xp - 0.07
    yq = TC[1] - TOWER["D"] / 2 + 0.025
    # from the foot pulley at the column's front across to the tower's foot pulley
    k.cable([(cx, cy - T / 2 - 0.02, 0.12), (cx + 0.04, cy - T / 2 - 0.03, 0.13), (xq - 0.04, yq, 0.16)])
    k.box("frame", (xq + 0.016, yq, 0.16), (0.032, 0.05, 0.08), soft=0.002)
    k.pulley((xq, yq, 0.16), 0.04, axis="y")
    k.box("frame", (xq + 0.016, yq, oz + 0.03), (0.032, 0.05, 0.08), soft=0.002)
    k.pulley((xq, yq, oz + 0.03), 0.04, axis="y")
    k.cable([(cx, (PIV[0] + sy) / 2, PIV[1] - 0.05), (cx, cy - T / 2 - 0.06 - 0.04 + 0.0, 0.17), (cx, cy - T / 2 - 0.02, 0.12),
             (xq - 0.04, yq, 0.16)])
    k.cable([(xq + 0.034, yq, 0.15), (xq + 0.04, yq, 0.17), (xq + 0.04, yq, oz + 0.02), (xq + 0.034, yq, oz + 0.04)])
    k.cable([(xq, yq, oz + 0.06), (xq + 0.02, yq, oz + 0.07), (ox, oy - 0.02, oz + 0.04), (ox, oy, oz - 0.01)])

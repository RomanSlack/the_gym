"""Life Fitness Insignia Series Glute (standing kickback), Charcoal frame / Black upholstery, the carriage at its start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit (titanium
frame) photographed all round at Fitness Equipment Empire (ref_02 / ref_03 / ref_05 three-quarters, ref_04 square on to
the tower's face, ref_06 from the column's end, ref_07 / ref_08 the back), held to Life Fitness's 73 x 38.4 x 58.1 in
(185 x 98 x 148 cm, L x W x H).
Axes: metres, floor z = 0, the user stands facing -y with the chest on the pad, x+ = the user's left; the tower on the
user's left (+x), its face turned across (-x), the guide rods running along y in front of it (ref_01 / ref_04: facing
the tower, the rods' rear post on the left and the column on the right).
Structure: the closed stack tower (shared builder, "shroud" style, Insignia placard); the base beam along y from the
rear end post to the column's foot, a cross beam from it to the tower's foot; the rear end post holding the two chrome
guide rods' back ends, the front block their front ends; the carriage on the rods (a bearing on each, the plate, the
arm up to the foot pad facing the user's foot); the column rising from its foot and leaning back, the chest pad on
two parallel links (it sets fore and aft) locked by a yellow pop pin, the U bar round the column's front up to the two
grips; the bar from the column across to the tower; the cable from the carriage to a pulley on the front block, along
the floor to the tower's foot and in.
"""
import importlib.util
import math
from pathlib import Path

import stack_tower

_spec = importlib.util.spec_from_file_location(
    "insignia_leg_extension", Path(__file__).resolve().parent.parent / "life-fitness-insignia-series-leg-extension" / "model.py")
le = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(le)

LOOK = le.LOOK
VIEWS = {"three_quarter": (-125, 12, 1.0), "front": (0, 5, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (60, 16, 1.0)}   # as ref_01 / ref_05
DETAILS = {
    "detail_pad": ((-1.05, -1.25, 1.45), (-0.18, -0.70, 1.05), 45),        # the chest pad, its links and pin, the grips
    "detail_carriage": ((-1.0, 0.10, 0.75), (-0.18, -0.40, 0.30), 45),     # the carriage on its rods, the foot pad
}

TOWER = dict(le.TOWER, title="GLUTE")
T, FOOT_H, Z, X, Y = le.T, le.FOOT_H, le.Z, le.X, le.Y
RZ0 = le.RZ0
SIDE = 1                             # the tower's side: the user's left
TC = (SIDE * 0.46, 0.15)             # the tower: its face across the rods (ref_01 / ref_04)
X_FACE = TC[0] - SIDE * TOWER["D"] / 2
X0 = -SIDE * 0.20                            # the line of the base beam, the rods, the column
Y_REAR, Y_COL = 0.98, -0.82          # the rear end post, the column's foot
Y_BLOCK = -0.56                      # the front block (the rods' front ends)
RODS = (0.20, 0.35)                  # the guide rods' heights
ROD_R = 0.0127
CAR_Y = -0.40                        # the carriage at its start, against the front block's bumpers
COL_TOP = (-0.70, 1.02)              # the column's top (y, z): it leans back towards the user going up (ref_01)


def build(k):
    tw = stack_tower.tower(k, TOWER, TC, -90.0 * SIDE)
    # ---- the base: the beam along y, its feet, the cross beam to the tower's foot
    le.foot(k, X0, Y_REAR, 0.12)
    le.foot(k, X0, Y_COL, 0.12)
    k.bar("frame", (X0, Y_COL, RZ0 + 0.004), (X0, Y_REAR, RZ0 + 0.004), T, 0.05, r=0.006)
    yc = TC[1] - TOWER["W"] / 2 + 0.12
    k.bar("frame", (X_FACE, yc, RZ0 + 0.004), (X0 + SIDE * T / 2, yc, RZ0 + 0.004), T, 0.05,
          cut0=((X_FACE, 0, 0), X), cut1=((X0 + SIDE * T / 2, 0, 0), X), weld=True)
    top = RZ0 + 0.004 + 0.025                       # the base beam's top
    # ---- the rear end post with its cap, the front block, the rods between them
    k.bar("frame", (X0, Y_REAR, top), (X0, Y_REAR, 0.46), 0.09, 0.09, r=0.01, cut0=((0, 0, top), Z), weld=True)
    k.box("plastic", (X0, Y_REAR, 0.465), (0.094, 0.094, 0.012), soft=0.004)
    k.box("frame", (X0, Y_BLOCK, (top + 0.42) / 2), (0.10, 0.03, 0.42 - top), soft=0.003)
    for z in RODS:
        k.tube("chrome", (X0, Y_BLOCK, z), (X0, Y_REAR, z), ROD_R, seg=20)
        k.cyl("rubber", (X0, Y_BLOCK + 0.025, z), 0.03, 0.02, axis="y", seg=24, soft=0.004)        # the bumpers
        k.bolt((X0, Y_REAR + 0.045, z), "+y", size=0.02)
    # ---- the carriage: a bearing round each rod, the plate tying them, the arm up and back to the foot pad
    cy = CAR_Y
    for z in RODS:
        k.tube("lever", (X0, cy - 0.06, z), (X0, cy + 0.06, z), 0.026, seg=24)
    k.box("lever", (X0 + 0.032, cy, (RODS[0] + RODS[1]) / 2), (0.012, 0.12, RODS[1] - RODS[0] + 0.05), soft=0.002)
    k.box("lever", (X0 - 0.032, cy, (RODS[0] + RODS[1]) / 2), (0.012, 0.12, RODS[1] - RODS[0] + 0.05), soft=0.002)
    a0 = (X0, cy, RODS[1] + 0.02)
    a1 = (X0, cy + 0.10, 0.54)
    k.bar("lever", a0, a1, 0.05, 0.05, up=(1, 0, 0))
    tilt = math.radians(30)                                                  # the pad faces the foot, tipped up
    nrm = (0.0, -math.cos(tilt), math.sin(tilt))
    k.shaped_pad("pad", [(-0.13, -0.07), (0.13, -0.07), (0.13, 0.07), (-0.13, 0.07)],
                 tuple(a1[i] + nrm[i] * 0.045 for i in range(3)), nrm, (1, 0, 0), 0.07, r=0.03, cushion=0.015)
    k.box("frame", tuple(a1[i] + nrm[i] * 0.004 for i in range(3)), (0.22, 0.012, 0.12), rx=tilt, soft=0.002)
    # ---- the column: from its foot up, leaning back towards the user; its cap
    cy0, cz0 = COL_TOP
    k.sweep("frame", [(X0, Y_COL, FOOT_H), (X0, Y_COL, 0.45), (X0, cy0, cz0)], k.rect(0.09, 0.09, 0.012),
            bend=0.25, up=(1, 0, 0), cut0=((0, 0, FOOT_H), Z), soft=0.002)
    # the bar from the column back across to the tower's side panel (ref_01 / ref_06)
    ys_ = TC[1] - TOWER["W"] / 2
    k.bar("frame", (X0 + SIDE * 0.04, Y_COL + 0.06, 0.72), (TC[0] - SIDE * 0.04, ys_ + 0.004, 0.72), 0.06, 0.06,
          cut1=((0, ys_, 0), Y), weld=True)
    k.box("frame", (TC[0] - SIDE * 0.04, ys_ - 0.004, 0.72), (0.10, 0.008, 0.10), soft=0.001)            # its plate
    # ---- the chest pad: two pairs of parallel links (a plate each side of the column) from the column's head back to
    # the pad's upright bracket; the yellow pop pin through the lower pivot; the pad on the bracket
    head = (X0, cy0, cz0)
    k.bar("frame", (X0, cy0, cz0 - 0.03), (X0, cy0 + 0.02, cz0 + 0.24), 0.08, 0.08)
    L = 0.14
    pivs = [cz0 + 0.03, cz0 + 0.20]
    yb2 = cy0 + L
    for z in pivs:
        for s in (1, -1):
            xp = X0 + s * 0.05
            k.box("frame", (xp, cy0 + L / 2, z), (0.012, L + 0.06, 0.05), soft=0.004)
            for y_ in (cy0, yb2):
                k.bolt((xp + s * 0.006, y_, z), "+x" if s > 0 else "-x", size=0.02)
    k.tube("steel", (X0 - 0.056, cy0, pivs[0]), (X0 + 0.056, cy0, pivs[0]), 0.012, seg=16)
    k.cyl("frame", (X0 - SIDE * 0.062, yb2, pivs[0]), 0.016, 0.012, axis="x", seg=20, soft=0.002)        # the pin's boss
    k.cyl("yellow", (X0 - SIDE * 0.08, yb2, pivs[0]), 0.018, 0.024, axis="x", seg=20, soft=0.004)
    k.bar("frame", (X0, yb2, pivs[0] - 0.06), (X0, yb2, pivs[1] + 0.06), 0.088, 0.05)            # the pad's bracket
    lean = math.radians(12)                                                   # the pad's top back towards the user
    pn = (0.0, math.cos(lean), math.sin(lean) * -1.0)
    pu = (0.0, math.sin(lean), math.cos(lean))
    pc = (X0, yb2 + 0.025 + 0.06, (pivs[0] + pivs[1]) / 2 + 0.05)
    k.shaped_pad("pad", [(-0.13, -0.24), (0.13, -0.24), (0.13, 0.24), (-0.13, 0.24)], pc, pn, (1, 0, 0), 0.10,
                 r=0.05, cushion=0.035)
    k.box("frame", (X0, yb2 + 0.031, (pivs[0] + pivs[1]) / 2 + 0.05), (0.18, 0.012, 0.40), rx=lean, soft=0.002)
    # ---- the grips: the U bar round the column's front, its ends up and out to the two grips (ref_01 / ref_06)
    zu = cz0 + 0.12
    yu = cy0 - 0.04
    for s in (1, -1):
        g0 = (X0 + s * 0.03, cy0 - 0.02, zu)
        g1 = (X0 + s * 0.17, yu - 0.02, zu)
        g2 = (X0 + s * 0.19, yu + 0.02, zu + 0.17)
        k.sweep("frame", [g0, g1, g2], k.circle(0.016, 18), bend=0.05, soft=0.0015)
        g3 = (X0 + s * 0.20, yu + 0.035, zu + 0.32)
        k.tube("rubber", g2, g3, 0.021, seg=22)
        k.cyl("plastic", g3, 0.023, 0.012, axis="z", seg=20, soft=0.003)
    # ---- the cable: off the carriage's front, round a pulley on the front block and back along the floor, round a
    # pulley on the cross beam and across into the tower's face (inside, up to the stack's top pulley, hidden)
    zc = 0.12
    p1 = (X0 + SIDE * 0.07, Y_BLOCK - 0.05, zc)
    k.box("frame", (X0 + SIDE * 0.07, Y_BLOCK - 0.004, zc), (0.06, 0.03, 0.08), soft=0.002)
    k.pulley(p1, 0.04, axis="z")
    k.cable([(X0 + SIDE * 0.03, cy - 0.065, RODS[0] - 0.026), (X0 + SIDE * 0.03, Y_BLOCK + 0.02, zc), (X0 + SIDE * 0.03, p1[1], zc)])
    p2 = (X0 + SIDE * 0.15, yc, zc)
    k.box("frame", (p2[0], yc, (RZ0 + 0.029 + zc - 0.015) / 2), (0.05, 0.05, zc - 0.015 - RZ0 - 0.029), soft=0.002)
    k.pulley(p2, 0.04, axis="z")
    k.cable([(p1[0] + SIDE * 0.035, p1[1], zc), (p2[0] - SIDE * 0.035, p2[1], zc)])
    ox, oy, oz = tw["cable"]
    out = (TC[0] + SIDE * (oy - TC[1]), TC[1] - SIDE * (ox - TC[0]), oz)   # turned -90 * SIDE about TC
    k.cable([(p2[0], p2[1] + 0.04, zc), (out[0] + SIDE * 0.02, p2[1] + 0.04, zc), (out[0] + SIDE * 0.02, out[1], oz - 0.06), out])

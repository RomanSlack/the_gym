"""Hammer Strength Select Biceps Curl (HS-BC), Charcoal frame / Black upholstery, the lever down at its start.

Built by eye from refs/: ref_01 the maker's image, and a used unit photographed all round at Fitness Equipment Empire
(ref_02 / ref_03 from in front of the user, ref_04-06 from the tower's front, ref_09 the side, ref_07 / ref_08 the back,
ref_10 the plates' printed weights), held to Life Fitness's 45 x 41 x 55 in (114 x 104 x 140 cm, L x W x H), the stack
200 lb: 14 plates of 15 lb (the top one 5 lb), numbered 20 to 200 (ref_10).
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left. Sides (ref_02, ref_09): the tower stands
behind the user's right, its front facing +x across the seat; the lever's pivot and cam on the tower's side (-x), the
lever reaching under the arm pad across to the open side (+x), its grey top cap there.
Structure: the stack tower (shared builder, "open" style, turned to face +x); the base from the tower's face; the
saddle seat on its height tube (row of holes, red pop pin); the pad's column and the curved brace from the base's front;
the preacher pad sloping down away from the user; the axle at the pad's front edge, the cam outside it on the tower's
side; the U lever under the pad (an arm each side), the handle bar with its two grey grips in front; the cable down
from the cam to the tower's foot and up its face.
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
    "cam": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.1),
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),
    "greyplastic": dict(color=(0.30, 0.30, 0.31), rough=0.6, coat=0.0),                                 # the grips, the cap
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (60, 14, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (-125, 16, 1.0)}
DETAILS = {"detail_lever": ((0.55, -1.05, 1.15), (0.0, -0.40, 0.80), 45)}   # the pad, the cam, the U lever, the grips

TOWER = dict(style="open", W=0.56, D=0.30, H=55 * IN, n=14, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="BICEPS CURL", brand="HAMMER STRENGTH", round=-1, step=15, start=5)
TC = (-0.40, 0.18)
TX_FRONT = TC[0] + 0.15
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
BX = 0.30
Y_FRONT = -0.62
SEAT = (0.0, 0.12, 0.55)             # the saddle's top centre
PAD_C, PAD_T = (0.0, -0.20, 0.86), math.radians(38)
PIV = (-0.43, 0.76)                  # the axle (y, z), under the pad's front edge
AXL = 0.32                           # the lever's arms (x)
HANDLE = (-0.66, 0.56)               # the handle bar (y, z) at the start


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (0.09, 0.09, FOOT_H), soft=0.003)


def bar_x(k, mat, y, z, x0, x1, w=0.076, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 90.0)
    # ---- the base: a rail along the tower's face and the left rail, cross bars
    xr = TX_FRONT + RAIL[0] / 2
    y_b = 0.40
    for x in (BX, xr):
        k.bar("frame", (x, Y_FRONT - 0.04, RAIL_Z), (x, y_b + 0.04, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y_FRONT - 0.04, -1), (y_b + 0.04, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.04)
    for y_ in (Y_FRONT, -0.12, SEAT[1], y_b):
        bar_x(k, "frame", y_, RAIL_Z, xr + RAIL[0] / 2, BX - RAIL[0] / 2, 0.076, RAIL[1])
    # ---- the saddle seat: its sleeve post, the height tube with its holes and pop pin, the saddle
    sx, sy, sz = SEAT
    k.bar("frame", (0, sy, RAIL_TOP), (0, sy, 0.34), 0.076, 0.076, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.bar("steel", (0, sy, 0.28), (0, sy, sz - 0.07), 0.06, 0.06, r=0.004)
    for i in range(6):
        k.cyl("hole", (0, sy - 0.0305, 0.36 + i * 0.022), 0.005, 0.001, axis="y", seg=12, soft=0.0)
    k.tube("steel", (0.038, sy, 0.31), (0.08, sy, 0.31), 0.007, seg=12)
    k.cyl("redplastic", (0.09, sy, 0.31), 0.016, 0.022, axis="x", seg=20, soft=0.004)
    k.box("frame", (0, sy, sz - 0.065), (0.20, 0.20, 0.02), soft=0.003)
    k.pad("pad", (0, sy, sz - 0.03), (0.36, 0.30, 0.07), r=0.035)
    # ---- the pad's column from the cross bar, the curved brace from the base's front up into it, the pad
    cy = -0.12
    ztop = PAD_C[2] - 0.12
    k.bar("frame", (0, cy, RAIL_TOP), (0, cy, ztop), 0.076, 0.076, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.sweep("frame", [(0, Y_FRONT, RAIL_TOP), (0, Y_FRONT + 0.08, 0.40), (0, cy - 0.038, ztop - 0.20)], k.rect(0.06, 0.06, 0.008),
            bend=0.15, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z), cut1=((0, cy - 0.038, 0), Y), weld=True, soft=0.002)
    nrm = (0.0, -math.sin(PAD_T), math.cos(PAD_T))          # its face: up and away from the user
    k.box("frame", (0, cy, ztop + 0.01), (0.20, 0.12, 0.02), soft=0.002)
    k.box("frame", tuple(PAD_C[i] - nrm[i] * 0.05 for i in range(3)), (0.50, 0.32, 0.012), rx=PAD_T, soft=0.002)
    k.box("frame", (0, (cy + PAD_C[1]) / 2, ztop + 0.04), (0.10, abs(cy - PAD_C[1]) + 0.10, 0.06), soft=0.003)
    k.shaped_pad("pad", [(-0.27, -0.17), (0.27, -0.17), (0.27, 0.17), (-0.27, 0.17)], PAD_C, nrm, (1, 0, 0), 0.08,
                 r=0.04, cushion=0.03)
    # ---- the axle: bearing blocks under the pad's front edge, the axle across, the cam outside on the tower's side
    py, pz = PIV
    for s in (1, -1):
        k.box("frame", (s * 0.24, py + 0.04, pz + 0.04), (0.05, 0.10, 0.10), soft=0.004)
        k.box("frame", (s * 0.24, py + 0.09, pz + 0.07), (0.04, 0.06, 0.06), soft=0.003)
    k.bar("frame", (-0.24, py + 0.10, pz + 0.07), (0.24, py + 0.10, pz + 0.07), 0.04, 0.04)                 # under the pad
    k.tube("steel", (-(AXL + 0.10), py, pz), (AXL + 0.03, py, pz), 0.018, seg=18)
    k.cyl("cam", (-(AXL + 0.06), py, pz), 0.13, 0.03, axis="x", seg=48, soft=0.003)
    k.disc("steel", (-(AXL + 0.06), py, pz), 0.132, 0.11, 0.026, axis="x", seg=48)
    k.bolt((-(AXL + 0.09), py, pz), "-x", size=0.022)
    k.box("warn", (-0.24 - 0.026, py + 0.04, pz + 0.04), (0.002, 0.04, 0.04), soft=0.0)
    # ---- the U lever: an arm each side from its hub on the axle down and forward to the handle bar, joined under the
    # pad; the grey cap on the open side's arm; the handle bar with its two grips
    hy, hz = HANDLE
    for s in (1, -1):
        x = s * AXL
        k.tube("lever", (x - 0.03, py, pz), (x + 0.03, py, pz), 0.04, seg=28)
        k.sweep("lever", [(x, py, pz), (x, hy + 0.06, hz + 0.10), (x, hy, hz)], k.rect(0.04, 0.06, 0.006), bend=0.06,
                up=(1, 0, 0), soft=0.002)
    ux = AXL
    k.bar("lever", (ux, py + 0.02, pz + 0.04), (ux, py - 0.02, pz + 0.30), 0.04, 0.06, up=(0, 1, 0))
    k.box("greyplastic", (ux, py - 0.025, pz + 0.34), (0.10, 0.12, 0.10), soft=0.01)
    k.tube("lever", (-AXL, hy, hz), (AXL, hy, hz), 0.02, seg=20)
    for s in (1, -1):
        k.tube("greyplastic", (s * 0.08, hy, hz), (s * 0.22, hy, hz), 0.022, seg=22)
    # ---- the cable: from the cam down to a pulley at the tower's foot, up its face to its top pulley
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)
    yp = TC[1] - TOWER["W"] / 2 + 0.038
    xq = TX_FRONT + 0.05
    cxp = -(AXL + 0.06)
    k.box("frame", (TX_FRONT + 0.025, yp, RAIL_TOP + 0.08), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, RAIL_TOP + 0.08), 0.045, axis="y")
    k.box("frame", (TX_FRONT + 0.025, yp, oz + 0.03), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, oz + 0.03), 0.045, axis="y")
    k.cable([(cxp, py + 0.05, pz - 0.12), (cxp, py + 0.20, 0.30), (xq - 0.01, yp, RAIL_TOP + 0.036)])
    k.cable([(xq - 0.045, yp, RAIL_TOP + 0.08), (xq - 0.045, yp, oz + 0.03)])
    k.cable([(xq, yp, oz + 0.075), (out[0] + 0.05, out[1] - 0.05, oz + 0.05), out])

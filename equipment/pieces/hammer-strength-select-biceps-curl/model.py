"""Hammer Strength Select Biceps Curl (HS-BC), Charcoal frame / Black upholstery, the lever down at its start.

Built by eye from refs/: ref_01 the maker's image, and a used unit photographed all round at Fitness Equipment Empire
(ref_02 / ref_03 from in front of the user, ref_04-06 from the tower's front, ref_09 the side, ref_07 / ref_08 the back,
ref_10 the plates' printed weights), held to Life Fitness's 45 x 41 x 55 in (114 x 104 x 140 cm, L x W x H), the stack
200 lb: 14 plates of 15 lb (the top one 5 lb), numbered 20 to 200 (ref_10).
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left. Sides (ref_02, ref_09): the tower stands
behind the user's right, its front facing +x across the seat; the lever's pivot and cam on the tower's side (-x), the
lever reaching under the arm pad across to the open side (+x), its grey top cap there.
Structure: the stack tower (shared builder, "open" style, turned to face +x); the base from the tower's face; the
saddle seat on its height tube (row of holes, red pop pin); the pad on its single column;
the preacher pad sloping down away from the user; the axle at the pad's front edge, the cam outside it on the tower's
side; the lever in three parts (v004, Roman): a short U connector between the hubs just under the pad's front, a
rectangular arm off it perpendicular out to the hands, the two grey grips each side of its end; the counterweight arm
up from the open side's hub with the grey block turned with it; proportions from a seated average man; the cable down
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
DETAILS = {"detail_lever": ((0.75, -1.05, 0.75), (0.0, -0.50, 0.55), 40)}   # the arm, the handle hub, the bent handle rods, the grips

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
# proportions from a seated average man (Roman: use the body's proportions): seated on the 0.55 m saddle his armpit is
# ~0.45 m higher, at y -0.05; the upper arm (0.33 m) lies down the pad's 38 degree slope to the elbow at (y -0.31,
# z 0.80); the axle sits at the elbow just under the pad; forearm + hand put the grips 0.33 m from the axle
PAD_C, PAD_T = (0.0, -0.155, 0.868), math.radians(38)
PIV = (-0.33, 0.76)                  # the axle (y, z), at the elbow under the pad's front edge
AXL = 0.32                           # the lever's hubs (x), at the pad's ends
GRIP_R, GRIP_A = 0.33, math.radians(45)   # the grips: their distance from the axle, the angle below level at the start


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
    # ---- the lever, three parts (ref_03 / ref_04; Roman): 1. the U: a short connector between the two hubs, dipping
    # just under the pad's front edge; 2. the arm: a rectangular bar off the U's bottom, perpendicular to it, out
    # forward and down to where the hands are; 3. the grips sticking out each side of its end. The open side's hub
    # carries the counterweight arm, the grey block on it turned with it.
    for s in (1, -1):
        k.tube("lever", (s * AXL - 0.03, py, pz), (s * AXL + 0.03, py, pz), 0.04, seg=28)
    ub = (0.0, py - 0.02, pz - 0.08)                          # the U's bottom
    path = [(-AXL, py, pz), (-0.22, py - 0.02, pz - 0.075), (0.22, py - 0.02, pz - 0.075), (AXL, py, pz)]
    k.sweep("lever", path, k.rect(0.045, 0.06, 0.008), bend=0.06, up=(0, 1, 0), soft=0.002)
    gh = (0.0, py - GRIP_R * math.cos(GRIP_A), pz - GRIP_R * math.sin(GRIP_A))   # the grips' hub, at the hands
    k.bar("lever", (0.0, ub[1] + 0.02, ub[2]), gh, 0.06, 0.035, up=(1, 0, 0))
    # the handle hub at the arm's end (ref_03 / ref_04): a bracket plate each side on a pin; off each, the handle's own
    # bent rod: forward along the arm's line, then turned outwards into the grey grip
    k.box("lever", gh, (0.12, 0.07, 0.07), rx=GRIP_A, soft=0.004)
    k.tube("steel", (-0.075, gh[1], gh[2]), (0.075, gh[1], gh[2]), 0.012, seg=14)
    fwd = (0.0, -math.cos(GRIP_A), -math.sin(GRIP_A))           # on along the arm, away from the axle
    for s in (1, -1):
        k.box("lever", (s * 0.066, gh[1], gh[2]), (0.012, 0.09, 0.05), rx=GRIP_A, soft=0.002)     # the bracket plate
        r0 = (s * 0.066, gh[1] + fwd[1] * 0.03, gh[2] + fwd[2] * 0.03)
        r1 = (s * 0.09, gh[1] + fwd[1] * 0.14, gh[2] + fwd[2] * 0.14 + 0.02)
        g1 = (s * 0.25, r1[1] - 0.05, r1[2] + 0.01)
        k.sweep("lever", [r0, r1, g1], k.circle(0.016, 18), bend=0.03, soft=0.0015)
        gm = tuple(r1[i] + (g1[i] - r1[i]) * 0.25 for i in range(3))
        k.tube("greyplastic", gm, g1, 0.022, seg=20)
        k.cyl("greyplastic", g1, 0.024, 0.01, axis="x", seg=20, soft=0.003)
    ca = math.radians(28)                                     # the counterweight arm leans forward with the lever
    c1 = (AXL, py - 0.26 * math.sin(ca), pz + 0.26 * math.cos(ca))
    k.bar("lever", (AXL, py, pz), c1, 0.045, 0.06, up=(0, 1, 0))
    k.box("greyplastic", (AXL, c1[1] - 0.04 * math.sin(ca), c1[2] + 0.04 * math.cos(ca)), (0.10, 0.14, 0.10), rx=ca, soft=0.01)
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

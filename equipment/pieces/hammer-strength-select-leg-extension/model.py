"""Hammer Strength Select Leg Extension (SLE), Charcoal Frame / Black Upholstery, the lever at its start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit photographed
all round at Fitness Equipment Empire (ref_02 front three-quarter, ref_03 the side from the lever's side, ref_04 /
ref_05 from the back pad's side, ref_06 the placard, ref_07 the plates' printed weights, ref_08 / ref_09 the back with
its frosted panel), held to Life Fitness's 47 x 41 x 64 in (119 x 104 x 163 cm, L x W x H). The stack is 20 plates of
15 lb (the top one 10 lb), numbered 10 to 295 (ref_07).
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left (the lever's side).
Structure: the stack tower behind the seat (shared builder: equipment/blender/stack_tower.py, "open" style); a base
of side rails and cross bars from the tower forward; the seat on a post; the back pad hinged at the seat's rear on a
quadrant plate of holes with its pop pin (to set it nearer or further); the lever's post at the seat's front left,
the axle through its head with the cam outside (the cable round it back to the tower); the lever: the arm down and
forward to the shin roller, the short upper arm with the start-position knob, the thigh pad on its stem; a grip each
side of the seat.
"""
import math

import stack_tower

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
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
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),                                       # red pop-pin knobs
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (60, 14, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (-125, 16, 1.0)}   # from the lever side, as the photos
DETAILS = {
    "detail_lever": ((0.95, -0.85, 0.85), (0.30, -0.25, 0.48), 45),     # the cam, the post, the lever, the thigh pad
    "detail_back": ((-0.85, 0.45, 0.95), (-0.10, 0.18, 0.62), 45),      # the back pad's quadrant and pop pin
}

TOWER = dict(style="open", W=0.56, D=0.30, H=64 * IN, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="LEG EXTENSION", brand="HAMMER STRENGTH", round=-1, step=15, start=-5)
TC = (-0.40, 0.10)                   # the tower's footprint centre: beside the user on the right, its front facing +x
                                     # across the seat (ref_01, ref_03: the seat runs along the tower's face)
TX_FRONT = TC[0] + 0.15              # the tower's front face (x)
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
BX = 0.34                            # the base's left rail (x); the right rail runs along the tower's face
Y_FRONT = -0.40
SEAT = (0.0, -0.03, 0.47)            # the seat pad's top centre: a long seat, the thighs on it to the knee
PIV = (0.40, -0.31, 0.50)            # the lever's axle (x of the post, y, z): at the knee, just in front of the seat
LX = 0.33                            # the lever's plane (inside the post)
ROLLER = (-0.42, 0.17)               # the shin roller's axis (y, z) at the start: low, just ahead of the knee


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (0.09, 0.09, FOOT_H), soft=0.003)


def bar_x(k, mat, y, z, x0, x1, w=0.076, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 90.0)
    # ---- the base: a rail along the tower's face, the left rail, cross bars (front, under the seat, at the back)
    xr = TX_FRONT + RAIL[0] / 2
    y_b = 0.34
    for x in (BX, xr):
        k.bar("frame", (x, Y_FRONT - 0.04, RAIL_Z), (x, y_b + 0.04, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y_FRONT - 0.04, -1), (y_b + 0.04, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.04)
    for y_ in (Y_FRONT, -0.02, y_b):
        bar_x(k, "frame", y_, RAIL_Z, xr + RAIL[0] / 2, BX - RAIL[0] / 2, 0.076, RAIL[1])
    # ---- the seat: its post, the frame under it, the pad; a grip each side
    sx, sy, sz = SEAT
    k.bar("frame", (0, -0.02, RAIL_TOP), (0, -0.02, sz - 0.12), 0.076, 0.076, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, sy, sz - 0.105), (0.30, 0.50, 0.03), soft=0.003)
    k.pad("pad", (0, sy, sz - 0.045), (0.42, 0.54, 0.09), r=0.04)
    for s in (1, -1):
        g0 = (s * 0.15, sy + 0.08, sz - 0.105)
        g1 = (s * 0.23, sy + 0.02, sz - 0.08)
        g2 = (s * 0.24, sy - 0.12, sz - 0.12)
        k.sweep("frame", [g0, g1, g2], k.circle(0.015, 18), bend=0.04, soft=0.0015)
        k.tube("rubber", (s * 0.235, sy - 0.03, sz - 0.093), g2, 0.021, seg=22)
    # ---- the back pad: hinged at the seat's rear, its post, the quadrant of holes and the pop pin (ref_05)
    hinge = (0, sy + 0.25, sz - 0.08)
    k.box("frame", (0, sy + 0.235, sz - 0.105), (0.10, 0.06, 0.03), soft=0.002)
    k.cyl("frame", hinge, 0.025, 0.14, axis="x", seg=24, soft=0.003)
    lean = math.radians(20)
    up = (0.0, math.sin(lean), math.cos(lean))
    top = tuple(hinge[i] + up[i] * 0.62 for i in range(3))
    k.bar("frame", hinge, top, 0.06, 0.04, up=(0, 1, 0))
    pc = tuple(hinge[i] + up[i] * 0.36 for i in range(3))
    n_ = (0.0, -math.cos(lean), math.sin(lean))
    k.shaped_pad("pad", [(-0.19, -0.27), (0.19, -0.27), (0.19, 0.27), (-0.19, 0.27)],
                 tuple(pc[i] + n_[i] * 0.065 for i in range(3)), n_, (1, 0, 0), 0.09, r=0.05, cushion=0.03)
    k.box("frame", tuple(pc[i] + n_[i] * 0.016 for i in range(3)), (0.30, 0.012, 0.50), rx=-lean, soft=0.002)
    qx = 0.045
    quad = [(0.0, 0.0)] + [(0.20 * math.cos(math.radians(a)), 0.20 * math.sin(math.radians(a))) for a in range(60, 101, 5)]
    k.sweep("frame", [(qx - 0.004, hinge[1], hinge[2]), (qx + 0.004, hinge[1], hinge[2])], [(-dy, dz) for dy, dz in quad],
            up=Z, soft=0.001)
    for a in range(64, 99, 6):
        k.cyl("hole", (qx + 0.0045, hinge[1] + 0.17 * math.cos(math.radians(a)), hinge[2] + 0.17 * math.sin(math.radians(a))),
              0.006, 0.001, axis="x", seg=12, soft=0.0)
    pin = (qx + 0.004, hinge[1] + 0.17 * math.cos(math.radians(82)), hinge[2] + 0.17 * math.sin(math.radians(82)))
    k.tube("steel", pin, (pin[0] + 0.05, pin[1], pin[2]), 0.006, seg=12)
    k.cyl("redplastic", (pin[0] + 0.06, pin[1], pin[2]), 0.016, 0.022, axis="x", seg=20, soft=0.004)
    # ---- the lever's post at the seat's front left, the head round the axle, the cam outside
    px, py, pz = PIV
    k.bar("frame", (px, Y_FRONT + RAIL[0] / 2, RAIL_Z), (BX, Y_FRONT + RAIL[0] / 2 + 0.0001, RAIL_Z), 0.08, RAIL[1])
    k.bar("frame", (px, py, RAIL_TOP), (px, py, pz - 0.06), 0.076, 0.076, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.bar("frame", (px, py, RAIL_Z), (px, Y_FRONT + 0.038, RAIL_Z), 0.076, RAIL[1], cut1=((0, Y_FRONT + 0.038, 0), Y), weld=True)
    k.box("frame", (px, py, pz), (0.09, 0.13, 0.13), soft=0.006)
    k.tube("steel", (LX - 0.03, py, pz), (px + 0.11, py, pz), 0.02, seg=20)
    k.cyl("cam", (px + 0.075, py, pz), 0.15, 0.03, axis="x", seg=48, soft=0.003)          # the cam disc
    k.disc("steel", (px + 0.075, py, pz), 0.152, 0.13, 0.026, axis="x", seg=48)            # its grooved rim
    k.bolt((px + 0.11, py, pz), "+x", size=0.024)
    k.box("warn", (px, py - 0.039, pz - 0.15), (0.045, 0.002, 0.05), soft=0.0)
    # the cable: round the cam's bottom, back under the seat to a pulley at the tower's foot, up its side, over a
    # pulley on top to the stack's top pulley
    # (the tower's out point is in its own frame: turned 90 degrees about TC its front's -y becomes +x)
    cxp = px + 0.075
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)
    yp = TC[1] - TOWER["W"] / 2 + 0.038                 # the tower's front post nearer the user (y)
    xq = TX_FRONT + 0.05                                # the cable's run up the tower's face
    k.box("frame", (TX_FRONT + 0.025, yp, RAIL_TOP + 0.08), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, RAIL_TOP + 0.08), 0.045, axis="y")
    k.box("frame", (TX_FRONT + 0.025, yp, oz + 0.03), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, oz + 0.03), 0.045, axis="y")
    k.cable([(cxp, py + 0.05, pz - 0.14), (cxp, py + 0.20, pz - 0.15), (xq + 0.045, yp, RAIL_TOP + 0.08)])
    k.cable([(xq - 0.045, yp, RAIL_TOP + 0.08), (xq - 0.045, yp, oz + 0.03)])
    k.cable([(xq, yp, oz + 0.075), (out[0] + 0.05, out[1] - 0.05, oz + 0.05), out])
    # ---- the lever: its hub on the axle inside the post, the arm down and forward to the shin roller, the short upper
    # arm with the start-position knob, the thigh pad's stem and pad
    k.tube("lever", (LX - 0.03, py, pz), (px - 0.045, py, pz), 0.045, seg=32)
    ry, rz_ = ROLLER
    k.sweep("lever", [(LX, py, pz), (LX, ry + 0.05, rz_ + 0.05), (LX, ry, rz_)], k.rect(0.05, 0.08, 0.008), bend=0.08,
            up=(1, 0, 0), soft=0.002)
    k.tube("steel", (LX + 0.02, ry, rz_), (-0.22, ry, rz_), 0.02, seg=20)
    k.tube("pad", (LX - 0.03, ry, rz_), (-0.22, ry, rz_), 0.065, seg=36, soft=0.012)
    k.cyl("plastic", (-0.225, ry, rz_), 0.066, 0.01, axis="x", seg=36, soft=0.003)
    ua = (LX, py + 0.02, pz + 0.24)
    k.bar("lever", (LX, py, pz), ua, 0.05, 0.08, up=(0, 1, 0))
    k.box("plastic", (LX, ua[1], ua[2] + 0.04), (0.08, 0.12, 0.08), soft=0.01)                       # its grey cap
    k.tube("steel", (LX + 0.025, py + 0.03, pz + 0.10), (LX + 0.07, py + 0.03, pz + 0.10), 0.007, seg=12)
    k.cyl("redplastic", (LX + 0.08, py + 0.03, pz + 0.10), 0.018, 0.024, axis="x", seg=20, soft=0.004)
    st0 = (LX - 0.025, py + 0.03, pz + 0.17)
    st1 = (0.12, py + 0.10, pz + 0.17)
    k.bar("lever", st0, st1, 0.04, 0.04, cut0=(st0, (1, 0, 0)), weld=True)
    k.pad("pad", (0.10, py + 0.14, pz + 0.12), (0.14, 0.18, 0.07), r=0.03)

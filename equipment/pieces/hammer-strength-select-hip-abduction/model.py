"""Hammer Strength Select Hip Abduction, Charcoal frame / Black upholstery, the arms closed at the start.

Built by eye from refs/: ref_01 the maker's studio three-quarter (it is the adduction's sister: same frame, the pads on
the other side of the knees), and a matched abductor + adductor pair photographed all round at Fitness Equipment Empire
(ref_02 / ref_03 / ref_07 three-quarters, ref_04 the back, ref_05 the two side by side, ref_10 from above the seat,
ref_08 the plates' printed weights, ref_09 / ref_06 the placards), held to Life Fitness's 61 x 26 x 55 in
(155 x 66 x 140 cm, L x W x H). The stack is 20 plates of 15 lb numbered 10 to 295 (ref_08).
The Hip Adduction (pieces/hammer-strength-select-hip-adduction) builds this file with ADDUCTION = True.
Axes: metres, floor z = 0, the user sits facing -y towards the tower, knees together; x+ = the user's left.
Structure: the stack tower at the front (shared builder, "open" style, its front facing the user); the base: a centre
beam from the tower's foot back under the seat, a cross foot at the back; the seat on its frame with the rear legs
splayed (ref_01), the reclined back pad on its post; the two arms on vertical axles under the seat's front, over the cam
disc between them; each arm's post with the upright knee pad (outside the knee here; inside for the adduction) and
its foot peg below; the cable from the cam along the beam to the tower's foot and up its face; the handles beside the
seat.
"""
import math

import stack_tower

IN = 0.0254
ADDUCTION = False
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
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (60, 12, 1.0), "front": (180, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (-35, 16, 1.0)}
DETAILS = {"detail_arms": ((0.75, 0.55, 1.05), (0.0, -0.05, 0.45), 45)}   # the arms, the cam, the knee pads, the pegs

TOWER = dict(style="open", W=0.56, D=0.28, H=55 * IN, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="HIP ABDUCTION", brand="HAMMER STRENGTH", round=1, step=15, start=-5)
TC = (0.0, -0.50)                         # the tower: at the front, its front facing sideways to the user's left (+x),
                                          # as ref_01 / ref_02 show it (the stack face on, the seat in profile)
FOOT_H = 0.015
T = 0.076
RAIL = (0.076, 0.06)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
Y_BACK = 0.92
# from a seated average man: the seat 0.50 m up, the hips at its back (y ~0.57), thighs 0.45 m forward to the knees at
# y ~0.12; the arms pivot on axles under the seat's front, the knee pads at the knees' sides
SEAT = (0.0, 0.42, 0.50)                  # the seat's top centre
PIV_Y, PIV_Z = 0.30, 0.30                 # the arms' vertical axles (y, z of the hub's middle)
PIV_X = 0.07
KNEE_Y = 0.06                             # the knee pads (y), at the knee
OPEN = 0.0                                # the arms' opening at the start (radians)


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (0.09, 0.09, FOOT_H), soft=0.003)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    T_ = dict(TOWER, title="HIP ADDUCTION" if ADDUCTION else "HIP ABDUCTION")
    tw = stack_tower.tower(k, T_, TC, 90.0)
    y_t = TC[1] + TOWER["W"] / 2                    # the tower's side towards the user
    x_f = TC[0] + TOWER["D"] / 2                    # its front face (+x)
    # ---- the base: the centre beam from the tower's front back to the cross foot; the cross foot at the tower's back
    k.bar("frame", (0, y_t - 0.01, RAIL_Z), (0, Y_BACK, RAIL_Z), 0.10, RAIL[1], cut0=((0, y_t, 0), Y), weld=True)
    for yb in (Y_BACK, ):
        k.bar("frame", (-0.30, yb, RAIL_Z), (0.30, yb, RAIL_Z), T, RAIL[1], r=0.006)
        for s in (1, -1):
            foot(k, s * 0.26, yb)
            k.box("plastic", (s * 0.304, yb, RAIL_Z), (0.008, T + 0.004, RAIL[1] + 0.004), soft=0.002)
    # ---- the seat's frame: two front posts on the beam's outriggers, the splayed rear legs, the seat pan, the pad
    sx, sy, sz = SEAT
    k.bar("frame", (-0.20, sy - 0.10, RAIL_Z), (0.20, sy - 0.10, RAIL_Z), T, RAIL[1],
          cut0=((-0.20, 0, 0), (1, 0, 0)), cut1=((0.20, 0, 0), (1, 0, 0)))
    for s in (1, -1):
        x = s * 0.16
        k.bar("frame", (x, sy - 0.10, RAIL_TOP), (x, sy - 0.10, sz - 0.08), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.sweep("frame", [(s * 0.26, Y_BACK, RAIL_TOP), (s * 0.20, sy + 0.30, sz - 0.30), (x, sy + 0.10, sz - 0.08)],
                k.rect(0.06, 0.06, 0.008), bend=0.10, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True, soft=0.002)
    k.box("frame", (0, sy, sz - 0.065), (0.40, 0.34, 0.03), soft=0.003)
    k.pad("pad", (0, sy, sz - 0.01), (0.44, 0.36, 0.10), r=0.045)
    # the handles each side of the seat
    for s in (1, -1):
        g0, g1 = (s * 0.20, sy + 0.05, sz - 0.065), (s * 0.27, sy - 0.12, sz - 0.04)
        k.sweep("frame", [g0, (s * 0.26, sy + 0.02, sz - 0.07), g1], k.circle(0.015, 16), bend=0.03, soft=0.0015)
        k.tube("rubber", (s * 0.265, sy - 0.04, sz - 0.055), g1, 0.021, seg=20)
    # the back pad: its post from the beam's end, reclined ~20 degrees, the pad on it
    lean = math.radians(20)
    b0 = (0.0, sy + 0.24, sz - 0.05)
    upv = (0.0, math.sin(lean), math.cos(lean))
    b1 = tuple(b0[i] + upv[i] * 0.66 for i in range(3))
    k.bar("frame", (0, b0[1], RAIL_TOP), b0, 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.bar("frame", b0, b1, 0.06, 0.04, up=Y)
    n_ = (0.0, -math.cos(lean), math.sin(lean))
    pc = tuple(b0[i] + upv[i] * 0.40 + n_[i] * 0.075 for i in range(3))
    k.shaped_pad("pad", [(-0.21, -0.28), (0.21, -0.28), (0.21, 0.28), (-0.21, 0.28)], pc, n_, (1, 0, 0), 0.09,
                 r=0.05, cushion=0.03)
    k.box("frame", tuple(b0[i] + upv[i] * 0.40 + n_[i] * 0.024 for i in range(3)), (0.30, 0.012, 0.50), rx=-lean, soft=0.002)
    # ---- the arms: the axle housing on the beam, the cam disc between the two hubs, each arm forward to its post
    k.bar("frame", (0, PIV_Y, RAIL_TOP), (0, PIV_Y, PIV_Z - 0.06), 0.09, 0.09, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, PIV_Y, PIV_Z - 0.045), (0.24, 0.12, 0.03), soft=0.003)
    k.cyl("cam", (0, PIV_Y, PIV_Z + 0.075), 0.16, 0.03, seg=48, soft=0.003)
    k.disc("steel", (0, PIV_Y, PIV_Z + 0.075), 0.162, 0.14, 0.026, axis="z", seg=48)
    k.box("warn", (0.0, PIV_Y - 0.162, PIV_Z + 0.075), (0.04, 0.002, 0.025), soft=0.0)
    for s in (1, -1):
        px = s * PIV_X
        k.tube("steel", (px, PIV_Y, PIV_Z - 0.03), (px, PIV_Y, PIV_Z + 0.06), 0.016, seg=16)
        k.cyl("lever", (px, PIV_Y, PIV_Z + 0.015), 0.04, 0.05, seg=28, soft=0.004)
        # the arm: from the hub forward to the knee, opened OPEN; the pad's post on it, the pad at the knee's side
        a = s * OPEN
        kx = s * (0.20 if ADDUCTION else 0.15)
        ky = KNEE_Y
        end = (px + (kx - px) * math.cos(a) - (ky - PIV_Y) * math.sin(a), PIV_Y + (kx - px) * math.sin(a) + (ky - PIV_Y) * math.cos(a), PIV_Z + 0.015)
        k.sweep("lever", [(px, PIV_Y, PIV_Z + 0.015), (end[0], end[1] + 0.10, end[2]), end], k.rect(0.05, 0.05, 0.006),
                bend=0.05, soft=0.002)
        k.bar("lever", end, (end[0], end[1], 0.90), 0.04, 0.05, cut0=(end, Z), weld=True)
        side = -s if ADDUCTION else s                 # the pad's back: outside the knee (abduction) or inside (adduction)
        k.box("lever", (end[0] - side * 0.022, end[1], 0.74), (0.006, 0.12, 0.26), soft=0.002)
        if ADDUCTION:                                 # a big round pad (ref_01)
            k.cyl("pad", (end[0] - side * 0.05, end[1], 0.74), 0.15, 0.05, axis="x", seg=40, soft=0.012)
        else:                                         # a tall pad (ref_02)
            k.pad("pad", (end[0] - side * 0.05, end[1], 0.74), (0.05, 0.18, 0.36), r=0.022)
        # the foot plate: a bar down and forward off the arm to a low grit plate (ref_02 / ref_05)
        fy = end[1] - 0.30
        k.bar("lever", (end[0], end[1] + 0.02, end[2] - 0.02), (end[0], fy, 0.14), 0.04, 0.03, up=(1, 0, 0))
        k.box("lever", (end[0] - s * 0.06, fy - 0.02, 0.13), (0.16, 0.12, 0.012), soft=0.002)
        k.box("grip", (end[0] - s * 0.06, fy - 0.02, 0.138), (0.15, 0.11, 0.004), soft=0.001)
    # ---- the cable: from the cam's back forward under the arms along the beam to the tower's foot, up its face
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)    # turned 90 degrees about the tower's centre
    yp = y_t - 0.038                                # the tower's front post nearer the user (y)
    xq = x_f + 0.05                                 # the cable's run up the tower's face
    k.box("frame", (x_f + 0.025, yp, RAIL_TOP + 0.08), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, RAIL_TOP + 0.08), 0.045, axis="y")
    k.box("frame", (x_f + 0.025, yp, oz + 0.03), (0.05, 0.04, 0.10), soft=0.002)
    k.pulley((xq, yp, oz + 0.03), 0.045, axis="y")
    k.cable([(0.0, PIV_Y - 0.15, PIV_Z + 0.075), (0.02, PIV_Y - 0.35, RAIL_TOP + 0.08), (xq - 0.01, yp, RAIL_TOP + 0.036)])
    k.cable([(xq - 0.045, yp, RAIL_TOP + 0.08), (xq - 0.045, yp, oz + 0.03)])
    k.cable([(xq, yp, oz + 0.075), (out[0] + 0.05, out[1] - 0.05, oz + 0.05), out])

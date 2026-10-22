"""Hammer Strength MTS Iso-Lateral Kneeling Leg Curl, Charcoal frame / Black upholstery, both levers at their start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit photographed
all round at Fitness Equipment Empire (ref_02 the front, ref_03 / ref_04 / ref_08 three-quarters, ref_05 / ref_09 / ref_10
the sides and back, ref_06 the base, ref_11 the placard), held to Life Fitness's 45 x 62 x 54 in (115 x 158 x 138 cm,
L x W x H). Iso-lateral: a stack tower for each leg.
Axes: metres, floor z = 0, the user kneels facing -y, x+ = the user's left. The towers stand at the two sides (their
fronts facing in, a top pulley each), tied by the base's side rails.
Structure: the two slim open towers (shared builder, "open" style, turned to face each other: the stacks in view from
the middle, the frosted backs with HAMMER STRENGTH outside, ref_05); the base: front
and back cross members between the towers and a centre rail; two posts carrying the forearm pad and its grips on top;
the two upright thigh pads on a cross bar; the knee pad low; each leg's lever: a hub on a bracket beside the knee, the
arm back to the ankle roller, a short arm up to the cable's eye; the cable from it up to its tower's top pulley.
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
    "shroud": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.15),
    "shroud2": dict(color=(0.75, 0.76, 0.77), rough=0.35, metal=0.3, coat=0.1),                       # the silver panels
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 5, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {"detail_lever": ((0.85, 0.95, 0.75), (0.20, 0.15, 0.40), 45)}   # a lever, its roller, the knee pad

TOWER = dict(style="open", round=1, W=0.26, D=0.30, H=54 * IN, n=15, plate=(0.17, 0.12, 0.0254), rods=0.13,
             title="KNEELING LEG CURL", brand="HAMMER STRENGTH", step=10, start=0)
TX = 0.66                                # the towers' centres (x)
FOOT_H = 0.015
T = 0.076
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
Y0, Y1 = -0.45, 0.45                     # the base's cross members
PIV = (0.0, 0.34)                        # the levers' pivots (y, z): at the knee
LX = 0.30                                # the levers' arms (x)
ROLLER = (0.40, 0.40)                    # the ankle rollers' axis (y, z) at the start


def rot(p, c, deg):
    a = math.radians(deg)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a), p[2])


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    xin = TX - TOWER["D"] / 2                     # the towers' inner faces (turned, their depth runs along x)
    outs = {}
    for s in (1, -1):
        rz = -90.0 if s > 0 else 90.0             # the +x tower faces -x, the -x tower faces +x
        tw = stack_tower.tower(k, TOWER, (s * TX, 0.0), rz, f"tower{'L' if s > 0 else 'R'}")
        outs[s] = rot(tw["cable"], (s * TX, 0.0), rz)
        # the tower's top pulley housing over its inner edge
        k.box("frame", (s * (xin + 0.03), 0.0, TOWER["H"] + 0.04), (0.10, 0.08, 0.08), soft=0.004)
        k.pulley((s * (xin + 0.03), 0.0, TOWER["H"] + 0.09), 0.05, axis="y")
    # ---- the base: the front and back cross members from tower to tower, a centre rail
    for y_ in (Y0, Y1):
        k.bar("frame", (-xin, y_, RAIL_Z), (xin, y_, RAIL_Z), 0.076, RAIL[1],
              cut0=((-xin, 0, 0), (1, 0, 0)), cut1=((xin, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (0, Y0 + 0.038, RAIL_Z), (0, Y1 - 0.038, RAIL_Z), 0.076, RAIL[1],
          cut0=((0, Y0 + 0.038, 0), Y), cut1=((0, Y1 - 0.038, 0), Y), weld=True)
    for s in (1, -1):
        k.bar("frame", (s * 0.30, Y0 + 0.038, RAIL_Z), (s * 0.30, Y1 - 0.038, RAIL_Z), 0.076, RAIL[1],
              cut0=((0, Y0 + 0.038, 0), Y), cut1=((0, Y1 - 0.038, 0), Y), weld=True)
    # ---- the posts in front carrying the forearm pad and its grips; the thigh pads' cross bar; the knee pad
    yp = -0.30
    for s in (1, -1):
        x = s * 0.18
        k.bar("frame", (x, Y0 + 0.038, RAIL_Z), (x, yp, RAIL_Z), 0.06, RAIL[1], cut0=((0, Y0 + 0.038, 0), Y), weld=True)
        k.bar("frame", (x, yp, RAIL_TOP), (x, yp, 1.02), T, T, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        g0, g1 = (s * 0.22, yp, 0.98), (s * 0.30, yp + 0.10, 1.10)
        k.sweep("frame", [(x + s * 0.038, yp, 0.98), (s * 0.28, yp, 0.99), g1], k.circle(0.015, 16), bend=0.03, soft=0.0015)
        k.tube("rubber", (s * 0.29, yp + 0.05, 1.045), g1, 0.021, seg=20)
    k.bar("frame", (-0.25, yp, 1.04), (0.25, yp, 1.04), 0.06, 0.06)
    k.pad("pad", (0, yp + 0.02, 1.11), (0.56, 0.26, 0.09), r=0.04)                   # the forearm pad
    zt = 0.62
    k.bar("frame", (-0.18 + T / 2, yp, zt), (0.18 - T / 2, yp, zt), 0.06, 0.06,
          cut0=((-0.18 + T / 2, 0, 0), (1, 0, 0)), cut1=((0.18 - T / 2, 0, 0), (1, 0, 0)), weld=True)
    for s in (1, -1):
        k.bar("frame", (s * 0.09, yp + 0.03, zt), (s * 0.09, yp + 0.10, zt), 0.04, 0.04, cut0=((0, yp + 0.03, 0), Y), weld=True)
        k.box("frame", (s * 0.09, yp + 0.105, zt), (0.14, 0.012, 0.24), soft=0.002)
        k.pad("pad", (s * 0.09, yp + 0.15, zt), (0.15, 0.26, 0.08), r=0.035, rx=math.pi / 2)            # the thigh pads
    k.bar("frame", (0, -0.02, RAIL_TOP), (0, -0.02, 0.22), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, -0.02, 0.23), (0.40, 0.24, 0.02), soft=0.002)
    k.pad("pad", (0, -0.02, 0.28), (0.46, 0.28, 0.08), r=0.035)                      # the knee pad
    # ---- each leg's lever: its hub on a bracket on the side rail, the arm back to the ankle roller, the short arm up
    # to the cable's eye; the cable up to its tower's top pulley
    py, pz = PIV
    ry, rz_ = ROLLER
    for s in (1, -1):
        x = s * LX
        k.bar("frame", (s * 0.30, py, RAIL_TOP), (s * 0.30, py, pz - 0.05), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("frame", (s * 0.30, py, pz), (0.09, 0.10, 0.10), soft=0.004)
        k.tube("steel", (s * 0.25, py, pz), (s * 0.39, py, pz), 0.016, seg=16)
        xl = s * 0.37
        k.tube("lever", (s * 0.345, py, pz), (s * 0.395, py, pz), 0.045, seg=28)
        k.sweep("lever", [(xl, py, pz), (xl, py + 0.10, pz + 0.28), (xl, ry + 0.05, rz_ + 0.24), (xl, ry, rz_)],
                k.rect(0.06, 0.09, 0.01), bend=0.10, up=(1, 0, 0), soft=0.002)          # the heavy curved arm (ref_01)
        k.tube("steel", (xl, ry, rz_), (s * 0.04, ry, rz_), 0.024, seg=16)
        k.tube("pad", (s * 0.34, ry, rz_), (s * 0.05, ry, rz_), 0.055, seg=32, soft=0.01)
        top = (xl, py - 0.05, pz + 0.22)
        k.bar("lever", (xl, py, pz), top, 0.04, 0.05, up=(0, 1, 0))
        k.box("lever", (xl, top[1], top[2]), (0.05, 0.04, 0.04), soft=0.003)                           # the cable's eye
        p = (s * (xin + 0.03), 0.0, TOWER["H"] + 0.09)
        k.cable([(xl, top[1], top[2] + 0.02), (p[0] - s * 0.05, p[1], p[2])])
        o = outs[s]
        k.cable([(p[0], p[1], p[2] + 0.05), (o[0], o[1], o[2] + 0.04), (o[0], o[1], o[2] - 0.01)])

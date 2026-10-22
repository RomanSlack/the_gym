"""Hammer Strength Plate-Loaded Seated Calf Raise (PL-CALF), Charcoal frame / Black upholstery, the lever on its stop.

Built by eye from the dealer gallery (refs/: ref_09 a true side view, ref_07 a true front view, ref_01 the studio
three-quarter in the picked colourway, ref_10 the three-quarter in silver, ref_11-14 close-ups of the thigh pads, the toe
plate, the horn and the base's badges), held to Life Fitness's 49 x 33 x 44 in (124 x 84 x 112 cm, L x W x H).
Axes: metres, floor z = 0, the user sits at +y facing -y, the balls of the feet on the toe plate, the thigh pads on the
knees; x+ = the user's left.
Structure: the base (side rails, cross bars, badges); the seat on two cross bars between the side gates at its ends; the
toe plate on the centre; the lever: on an axle in brackets under the seat's front, curving forward and down to the post,
the post rising to the top, the chrome horn across it, the thigh pad yoke on a sleeve with its pop pin, the two pads;
the lever's stop on the base; the start lever with its knob.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 16, 1.0), "front": (0, 6, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_pads": ((-0.55, -0.55, 1.20), (0.0, 0.0, 0.80), 45),        # the yoke, thigh pads, horn
    "detail_base": ((0.75, -0.75, 0.55), (0.0, 0.0, 0.15), 45),         # the toe plate, pivot, stop, start lever
}

FOOT_H = 0.02
RAIL = (0.076, 0.076)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
BX = 0.36
Y0, Y1 = -0.62, 0.60
SEAT = (0.40, 0.52)               # the seat's centre (y, z top)
PIV = (0.16, 0.24)                # the lever's axle (y, z)
POST_Y = -0.07                    # the lever's post (between the knees, just in front of them)
POST_TOP = 1.00


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def bar_x(k, mat, y, z, x0, x1, w=0.076, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    # ---- the base
    for s in (1, -1):
        x = s * BX
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.045)
        k.box("placard", (x + s * (RAIL[0] / 2 + 0.002), -0.30, RAIL_Z), (0.004, 0.15, 0.05), soft=0.0)
        for i, line in enumerate(("HAMMER", "STRENGTH")):
            k.text("label", line, (x + s * (RAIL[0] / 2 + 0.0043), -0.30, RAIL_Z + 0.01 - i * 0.02), 0.017,
                   rz=s * math.pi / 2, depth=0.0003)
    xi = BX - RAIL[0] / 2
    for y_ in (Y0 + 0.08, 0.0, Y1 - 0.08):
        bar_x(k, "frame", y_, RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    # ---- the seat: a gate each side at its ends (two posts and a top bar), two cross bars, the seat's slide, the pad
    zs = SEAT[1] - 0.10
    for s in (1, -1):
        x = s * BX
        for py in (SEAT[0] - 0.14, SEAT[0] + 0.14):
            k.bar("frame", (x, py, RAIL_TOP), (x, py, zs + 0.03), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.bar("frame", (x, SEAT[0] - 0.17, zs + 0.06), (x, SEAT[0] + 0.17, zs + 0.06), 0.06, 0.06, r=0.006)
    for py in (SEAT[0] - 0.08, SEAT[0] + 0.08):
        k.tube("steel", (-BX + 0.03, py, zs + 0.06), (BX - 0.03, py, zs + 0.06), 0.016, seg=18)
    k.box("frame", (0, SEAT[0], zs + 0.06), (0.16, 0.24, 0.05), soft=0.004)       # the slide on the bars
    k.box("frame", (0, SEAT[0], SEAT[1] - 0.06), (0.36, 0.26, 0.02), soft=0.003)
    k.box("frame", (0, SEAT[0], (zs + 0.085 + SEAT[1] - 0.07) / 2), (0.08, 0.08, SEAT[1] - 0.07 - zs - 0.085), soft=0.003)
    k.pad("pad", (0, SEAT[0], SEAT[1] - 0.005), (0.44, 0.32, 0.10), r=0.045)
    # ---- the toe plate on the centre cross bar
    k.box("frame", (0, 0.03, RAIL_TOP + 0.04), (0.10, 0.10, 0.08), soft=0.003)
    k.box("lever", (0, 0.06, RAIL_TOP + 0.09), (0.34, 0.12, 0.02), soft=0.003)
    k.box("grip", (0, 0.06, RAIL_TOP + 0.102), (0.32, 0.10, 0.004), soft=0.001)
    # ---- the lever: two brackets on a cross bar under the seat's front carrying the axle, the hub on it, the arm
    # curving forward and down to the post's foot, the post up to the top
    for s in (1, -1):
        k.box("frame", (s * 0.12, PIV[0], (RAIL_TOP + PIV[1] + 0.05) / 2), (0.012, 0.10, PIV[1] + 0.05 - RAIL_TOP), soft=0.001)
    bar_x(k, "frame", PIV[0], RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    k.tube("steel", (-0.15, PIV[0], PIV[1]), (0.15, PIV[0], PIV[1]), 0.02, seg=20)
    for s in (1, -1):
        k.bolt((s * 0.15, PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.022)
    k.tube("lever", (-0.114, PIV[0], PIV[1]), (0.114, PIV[0], PIV[1]), 0.04, seg=28)                  # the hub
    k.sweep("lever", [(0, PIV[0], PIV[1]), (0, 0.08, 0.30), (0, POST_Y, 0.36)], k.rect(0.07, 0.10, 0.01), bend=0.12,
            up=(1, 0, 0), soft=0.002)
    k.bar("lever", (0, POST_Y, 0.36), (0, POST_Y, POST_TOP), 0.076, 0.076, up=Y)
    k.box("plastic", (0, POST_Y, POST_TOP + 0.005), (0.08, 0.08, 0.01), soft=0.002)
    k.box("rubber", (0, POST_Y, (RAIL_TOP + 0.36) / 2 + 0.0), (0.07, 0.07, 0.36 - RAIL_TOP), soft=0.006)       # its stop
    bar_x(k, "frame", POST_Y, RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    # the chrome horn across the post
    zh = 0.56
    k.cyl("lever", (0, POST_Y, zh), 0.05, 0.12, axis="x", seg=32, soft=0.004)
    k.tube("chrome", (-0.44, POST_Y, zh), (0.44, POST_Y, zh), 0.025, seg=32)
    for s in (1, -1):
        k.cyl("lever", (s * 0.448, POST_Y, zh), 0.029, 0.016, axis="x", seg=32, soft=0.004)
    # the thigh pad yoke on a sleeve with its pop pin, two pads hanging on the knees
    zy = 0.78
    k.box("lever", (0, POST_Y, zy), (0.10, 0.10, 0.16), soft=0.004)
    k.tube("steel", (0, POST_Y - 0.05, zy + 0.03), (0, POST_Y - 0.11, zy + 0.03), 0.007, seg=14)
    k.cyl("plastic", (0, POST_Y - 0.12, zy + 0.03), 0.016, 0.025, axis="y", seg=20, soft=0.004)
    ypad = 0.12
    for s in (1, -1):
        k.sweep("lever", [(0, POST_Y + 0.05, zy), (s * 0.10, POST_Y + 0.07, zy), (s * 0.15, ypad - 0.06, zy - 0.02),
                          (s * 0.15, ypad + 0.10, zy - 0.02)], k.rect(0.05, 0.04, 0.006), bend=0.06, up=(0, 0, 1), soft=0.002)
        k.box("lever", (s * 0.15, ypad, zy - 0.045), (0.13, 0.20, 0.012), soft=0.002)
        k.pad("pad", (s * 0.15, ypad, zy - 0.09), (0.14, 0.24, 0.08), r=0.035)
    # the start lever: a bent rod up from the base's centre to a knob by the seat's right
    k.sweep("steel", [(-0.02, 0.0 + 0.038, RAIL_Z), (-0.05, 0.10, 0.20), (-0.20, 0.16, 0.56)], k.circle(0.011, 14),
            bend=0.05, soft=0.001)
    k.cyl("plastic", (-0.205, 0.162, 0.585), 0.018, 0.06, seg=20, soft=0.006)

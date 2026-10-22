"""Hammer Strength Plate-Loaded Hack Squat (PL-HSQ), Charcoal frame / Black upholstery, the sled at rest on its stops.

Built by eye from the dealer gallery (refs/: ref_02 a true side view, ref_08 a true front view, ref_10 the back, ref_01
the studio three-quarter, ref_09 the rear three-quarter, ref_07 / ref_12-14 close-ups of the foot plate, the pads, the
bearings and the rods), held to Life Fitness's 85 x 61 x 59 in (216 x 155 x 153 cm, L x W x H; W across the sled's horns).
Axes: metres, floor z = 0, the user faces -y (the foot plate at -y), x+ = the user's left. Sides mirrored (s = +1 / -1).
Structure: a base rail each side, a front cross bar; on each side an incline beam (3 x 5 in, ~42 degrees) from the cross
bar up to a rear post, a middle post under it, a chrome guide rod on end blocks above it; the sled rides the rods on
linear bearings: a plate carrying the back pad, the head pad, the two shoulder pads, the handles and the loading horns;
the foot plate, tilted towards the user, on two curved legs; two storage horns on each rear post.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black sled
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),             # black vinyl
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),                            # horns
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),                            # the guide rods
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),        # the foot plate's grit
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.15), "front": (0, 5, 1.15), "side": (-90, 3, 1.15), "back_three_quarter": (150, 18, 1.15)}
DETAILS = {
    "detail_sled": ((-1.05, -0.35, 1.70), (0.0, 0.62, 1.15), 45),        # the pads, handles and horns from the user's side
    "detail_bearing": ((0.85, 0.05, 0.75), (0.26, 0.55, 0.78), 45),      # a bearing on its rod, the stop, the beam
    "detail_foot": ((0.95, -1.55, 0.85), (0.0, -0.85, 0.45), 45),        # the foot plate on its legs
    "detail_handles": ((0.75, -0.30, 0.75), (0.05, 0.40, 0.85), 45),    # the start-position handle, the pop pin
}

A = math.radians(41.6)                     # the incline
U = (0.0, math.cos(A), math.sin(A))        # up the rails
N = (0.0, -math.sin(A), math.cos(A))       # off the rails, towards the user
B0 = (-0.36, 0.19)                         # the beams' centreline at s = 0 (y, z)
BL = 1.92                                  # the beams' length along U
BX = 0.26                                  # each side's plane (x): base rail, beam, rod, posts
BEAM = (0.075, 0.127)                      # 3 x 5 in (across, along N)
RAIL = (0.076, 0.10)                       # base rails
FOOT_H = 0.02
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
RY0, RY1 = -0.62, 1.03                     # base rails: front cross bar, rear end (y)
POST_Y = (0.40, 0.98)                      # the middle and rear posts (y)
ROD_H, ROD_R = 0.12, 0.019                 # the guide rods: off the beam's centreline, radius
ROD_S = (0.15, 1.85)
SLED_S = (0.85, 1.80)                      # the sled plate's span along U (at rest)
SLED_H = 0.18
HORN_X = 0.775                             # the loading horns' tips (61 in across)
FOOT_C, FOOT_TILT = (-0.875, 0.55), math.radians(35.6)   # the foot plate's top centre (y, z), its tilt
FOOT_W, FOOT_D = 0.72, 0.48


def at(x, s, h):
    """A point on the incline: s along U from B0, h along N off the beams' centreline."""
    return (x, B0[0] + U[1] * s + N[1] * h, B0[1] + U[2] * s + N[2] * h)


def s_at_y(y, h):
    return (y - B0[0] - N[1] * h) / U[1]


def foot(k, x, y):
    """A rubber foot under a member's end: a block on a flat pad, an anchor hole each side."""
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def build(k):
    Z = (0, 0, 1)
    for s in (1, -1):
        x = s * BX
        # the base rail on its feet, capped
        k.bar("frame", (x, RY0 - 0.04, RAIL_Z), (x, RY1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((RY0 - 0.04, -1), (RY1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.04)
        # the incline beam: its foot cut onto the front cross bar's top, capped at the top
        p0, p1 = at(x, -0.12, 0.0), at(x, BL, 0.0)
        k.bar("lever", p0, p1, BEAM[0], BEAM[1], up=N, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", at(x, BL + 0.005, 0.0), (BEAM[0] + 0.004, 0.01, BEAM[1] + 0.004), rx=A, soft=0.002)
        # the posts up to the beam's underside (the rear one with the warning label and two storage horns)
        for py in POST_Y:
            sp = s_at_y(py, -BEAM[1] / 2)
            top = at(x, sp, -BEAM[1] / 2)
            k.bar("frame", (x, py, RAIL_TOP), (x, py, top[2] + 0.05), 0.076, 0.076, up=(0, 1, 0),
                  cut0=((0, 0, RAIL_TOP), Z), cut1=(top, tuple(-c for c in N)), weld=True)
        py = POST_Y[1]
        k.box("warn", (x, py - 0.0385, 1.05), (0.045, 0.002, 0.07), soft=0.0)
        for zh in (0.23, 0.75):
            xo = x + s * 0.038
            k.cyl("frame", (xo + s * 0.006, py, zh), 0.045, 0.012, axis="x", seg=32, soft=0.003)
            k.tube("steel", (xo + s * 0.012, py, zh), (xo + s * 0.30, py, zh), 0.025, seg=32)
            k.cyl("frame", (xo + s * 0.308, py, zh), 0.029, 0.016, axis="x", seg=32, soft=0.004)
        # the guide rod on its end blocks, a stop under the sled
        for sr in ROD_S:
            k.box("lever", at(x, sr, (BEAM[1] / 2 + ROD_H + 0.02) / 2), (0.07, 0.06, ROD_H + 0.02 - BEAM[1] / 2),
                  rx=A, soft=0.004)
        k.tube("chrome", at(x, ROD_S[0] + 0.03, ROD_H), at(x, ROD_S[1] - 0.03, ROD_H), ROD_R, seg=28)
        k.box("lever", at(x, SLED_S[0] + 0.03 - 0.035, ROD_H), (0.075, 0.07, 0.075), rx=A, soft=0.006)
        k.cyl("plastic", at(x - s * 0.05, SLED_S[0] - 0.005, ROD_H), 0.016, 0.03, axis="x", seg=20, soft=0.003)
        # the sled's linear bearings round the rod
        for sb in (SLED_S[0] + 0.10, SLED_S[1] - 0.18):
            k.box("lever", at(x, sb, ROD_H + 0.005), (0.085, 0.14, 0.10), rx=A, soft=0.006)
            for d in (-0.04, 0.04):
                k.bolt(at(x + s * 0.0425, sb + d, ROD_H + 0.02), "+x" if s > 0 else "-x", size=0.01)
        # the sled's loading horn at the shoulders, its handle rising beside the shoulder pad
        sh = SLED_S[1] - 0.30
        xe = s * 0.30
        k.box("lever", at(xe + s * 0.02, sh, SLED_H + 0.01), (0.04, 0.12, 0.09), rx=A, soft=0.005)
        hc = at(0, sh, SLED_H + 0.01)
        k.cyl("lever", (xe + s * 0.05, hc[1], hc[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
        k.tube("steel", (xe + s * 0.058, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
        k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
        g0 = at(s * 0.27, SLED_S[1] - 0.12, SLED_H + 0.01)
        g1 = at(s * 0.29, SLED_S[1] - 0.06, SLED_H + 0.20)
        g2 = at(s * 0.42, SLED_S[1] + 0.02, SLED_H + 0.36)
        g3 = at(s * 0.60, SLED_S[1] + 0.04, SLED_H + 0.40)
        k.sweep("lever", [g0, g1, g2, g3], k.circle(0.016, 20), bend=0.05, soft=0.0015)
        k.tube("rubber", tuple(g2[i] + (g3[i] - g2[i]) * 0.25 for i in range(3)), g3, 0.021, seg=24)
    # the front cross bar (the beams land on it) and the rear cross bar, between the base rails
    xi = BX - RAIL[0] / 2
    for y_ in (RY0, B0[0] - 0.08, RY1 - 0.05):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), 0.076, RAIL[1],
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (BX + RAIL[0] / 2 + 0.0004, 0.70, RAIL_Z + 0.014 - i * 0.026), 0.022, rz=math.pi / 2, depth=0.0004)
    # the sled: its plate, the back pad (tapering to the top), the head pad, the two shoulder pads on their brackets
    s0, s1 = SLED_S
    k.box("lever", at(0, (s0 + s1) / 2, SLED_H), (0.60, s1 - s0, 0.02), rx=A, soft=0.004)
    side = (1, 0, 0)
    pl = 0.64
    k.shaped_pad("pad", [(-0.20, -pl / 2), (0.20, -pl / 2), (0.16, pl / 2), (-0.16, pl / 2)], at(0, s0 + 0.03 + pl / 2, SLED_H + 0.05),
                 N, side, 0.08, r=0.05, cushion=0.03)
    k.shaped_pad("pad", [(-0.09, -0.07), (0.09, -0.07), (0.09, 0.07), (-0.09, 0.07)], at(0, s0 + pl + 0.13, SLED_H + 0.05),
                 N, side, 0.08, r=0.03, cushion=0.02)
    for s in (1, -1):
        k.box("lever", at(s * 0.16, s1 - 0.16, SLED_H + 0.07), (0.05, 0.10, 0.12), rx=A, soft=0.004)
        k.pad("pad", at(s * 0.16, s1 - 0.13, SLED_H + 0.21), (0.13, 0.26, 0.17), r=0.04, rx=A)
    # the release lever (ref_01): a rod rising from a pivot bracket on the sled's left edge beside the shoulder pad, a grip
    # on its end; the start-position handle (ref_06): a bracket under the sled's lower end, a bent grip across it; the
    # pop-pin T-knob on the left bearing (ref_01, ref_13)
    pv = at(0.33, s1 - 0.26, SLED_H)
    k.box("lever", (0.31 + 0.02, pv[1], pv[2]), (0.04, 0.07, 0.06), rx=A, soft=0.004)
    k.tube("steel", (0.30, pv[1], pv[2]), (0.36, pv[1], pv[2]), 0.008, seg=14)
    l1 = at(0.35, s1 + 0.12, SLED_H + 0.50)
    k.tube("lever", (0.35, pv[1], pv[2]), l1, 0.011, seg=18)
    l2 = at(0.35, s1 + 0.15, SLED_H + 0.62)
    k.tube("rubber", tuple(l1[i] + (l2[i] - l1[i]) * -0.15 for i in range(3)), l2, 0.016, seg=20)
    k.box("lever", at(0, s0 + 0.03, SLED_H - 0.055), (0.12, 0.02, 0.09), rx=A, soft=0.003)
    q0, q1 = at(-0.06, s0 + 0.02, SLED_H - 0.095), at(0.06, s0 + 0.02, SLED_H - 0.095)
    k.sweep("lever", [(q0[0], q0[1], q0[2]), at(-0.06, s0 - 0.05, SLED_H - 0.10), at(0.06, s0 - 0.05, SLED_H - 0.10),
                      (q1[0], q1[1], q1[2])], k.circle(0.011, 16), bend=0.02, soft=0.001)
    kb = at(BX + 0.0425, SLED_S[1] - 0.18, ROD_H + 0.02)
    k.tube("steel", (kb[0], kb[1], kb[2]), (kb[0] + 0.05, kb[1], kb[2]), 0.007, seg=14)
    k.box("plastic", (kb[0] + 0.055, kb[1], kb[2]), (0.012, 0.06, 0.018), rx=A, soft=0.004)
    # the foot plate: the grit top on its plate and frame, a wing each side; two curved legs under it to the floor
    fy, fz = FOOT_C
    nrm = (0.0, math.sin(FOOT_TILT), math.cos(FOOT_TILT))
    along = (0.0, math.cos(FOOT_TILT), -math.sin(FOOT_TILT))
    rx = -FOOT_TILT

    def fp(h, a=0.0):
        return (0.0, fy + nrm[1] * h + along[1] * a, fz + nrm[2] * h + along[2] * a)
    k.box("grip", fp(-0.003), (FOOT_W - 0.04, FOOT_D - 0.04, 0.006), rx=rx, soft=0.001)
    k.box("lever", fp(-0.016), (FOOT_W, FOOT_D, 0.02), rx=rx, soft=0.003)
    k.box("lever", fp(-0.05), (FOOT_W - 0.10, FOOT_D - 0.08, 0.05), rx=rx, soft=0.004)
    for s in (1, -1):
        c = fp(0.02)
        k.box("lever", (s * (FOOT_W / 2 + 0.004), c[1], c[2]), (0.008, FOOT_D, 0.10), rx=rx, soft=0.002)
        bot = fp(-0.075)
        x = s * 0.13
        k.sweep("frame", [(x, -0.86, FOOT_H), (x, -0.86, 0.30), (x, bot[1] - 0.02, bot[2] - 0.02)], k.rect(0.076, 0.076, 0.008),
                bend=0.18, up=(1, 0, 0), cut0=((0, 0, FOOT_H), Z), cut1=(bot, tuple(-v for v in nrm)), weld=True)
        foot(k, x, -0.86)
        # the short rail from the front cross bar to the leg
        k.bar("frame", (x, RY0 - 0.038, RAIL_Z), (x, -0.86 + 0.038, RAIL_Z), 0.076, RAIL[1],
              cut0=((0, RY0 - 0.038, 0), (0, 1, 0)), cut1=((0, -0.86 + 0.038, 0), (0, 1, 0)), weld=True)

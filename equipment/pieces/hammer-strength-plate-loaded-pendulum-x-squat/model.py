"""Hammer Strength Plate-Loaded Pendulum-X Squat (PL-XSQ), Charcoal, the pendulum at rest.

Built by eye from the dealer gallery (refs/: ref_09 a true side view, ref_01 / ref_02 the studio three-quarters front and
back, ref_10 the side three-quarter loaded, ref_05 in use from the side, ref_12-14 close-ups of the pads, the platform's
handle and grit), held to Life Fitness's 97 x 45 x 81 in (246 x 114 x 206 cm, L x W x H), 6 storage horns.
Axes: metres, floor z = 0, the user stands on the platform at -y facing -y, back to the pads; x+ = the user's left.
Structure: a base (side rails, cross bars); a peaked side frame each side (front leg rising into the roof, the apex, the
rear slope, the rear leg down to the base), cross tubes at the front and the apex; rear braces from the rear legs down to
the base carrying the storage horns; the stop posts. The black pendulum swings on an axle under the apex: a pair of arms,
each with a front branch along the roof (the counterweight end: a cross bar with three grey bumper blocks, the front
horns), a rear branch out past the frame's rear corner (the main loading horns) and a lower branch curving down under the
pads (the carriage: back pad, shoulder pads, grips). The inclined foot platform on its frame, its adjuster handle.
"""
import math

LOOK = {
    "frame": dict(color=(0.11, 0.115, 0.12), rough=0.42, metal=0.45, coat=0.1, bump=(1400, 0.06)),    # Charcoal (grey)
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black pendulum
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bumper": dict(color=(0.30, 0.30, 0.31), rough=0.8, coat=0.0, spec=0.25, bump=(1800, 0.12)),      # grey rubber blocks
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 14, 1.1), "front": (0, 5, 1.1), "side": (-90, 3, 1.1), "back_three_quarter": (140, 16, 1.1)}
DETAILS = {
    "detail_pads": ((-0.65, -0.80, 1.65), (0.0, 0.45, 1.25), 45),       # the carriage from the user's side
    "detail_front": ((-1.05, -1.95, 1.55), (0.0, -1.05, 1.15), 45),     # the bumper blocks, front horns
    "detail_rear": ((1.35, 1.85, 1.20), (0.40, 0.90, 0.70), 45),        # the rear braces, storage horns
}

FOOT_H = 0.02
RAIL = (0.076, 0.10)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
FX = 0.45                          # the side frames (x)
AX = 0.36                          # the pendulum's arms (x)
T = 0.076                          # frame tube (3 x 3 in)
FRAME = [(-1.21, RAIL_TOP), (-1.21, 0.85), (0.06, 1.97), (0.75, 1.66), (0.23, 0.77), (0.23, RAIL_TOP)]
PIV = (0.06, 1.76)                 # the pendulum's axle (y, z)
FRONT_END = (-1.02, 0.97)          # the arms' front ends
REAR_END = (1.05, 1.50)            # the arms' rear horn ends
LOWER = [(0.58, 1.34), (0.58, 1.00), (0.34, 0.86)]   # the lower branch, after the pivot
Y0, Y1 = -1.25, 1.22               # the base's ends


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def bar_x(k, mat, y, z, x0, x1, w=T, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def horn(k, mat, x, y, z, s, length, base_x):
    k.cyl(mat, (base_x + s * 0.006, y, z), 0.045, 0.012, axis="x", seg=32, soft=0.003)
    k.tube("steel", (base_x + s * 0.012, y, z), (base_x + s * length, y, z), 0.025, seg=32)
    k.cyl(mat, (base_x + s * (length + 0.008), y, z), 0.029, 0.016, axis="x", seg=32, soft=0.004)


def on(p0, p1, f):
    return tuple(p0[i] + (p1[i] - p0[i]) * f for i in range(len(p0)))


def build(k):
    Z = (0, 0, 1)
    # ---- the base
    for s in (1, -1):
        x = s * FX
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.045)
        for by in (-1.0, -0.5, 0.0, 0.6, 1.0):
            k.cyl("bolt", (x + s * (RAIL[0] / 2 + 0.002), by, RAIL_Z), 0.008, 0.004, axis="x", seg=16, soft=0.001)
    xi = FX - RAIL[0] / 2
    for y_ in (Y0 + 0.04, -0.78, -0.30, 0.23, Y1 - 0.04):
        bar_x(k, "frame", y_, RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    # ---- the side frames: one bent tube each, the front leg up into the roof, over the apex, down the rear
    for s in (1, -1):
        x = s * FX
        k.sweep("frame", [(x, y, z) for y, z in FRAME], k.rect(T, T, 0.008), bend=0.16, up=(1, 0, 0),
                cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, RAIL_TOP), Z), weld=True, soft=0.002)
        # the rear brace down to the base's end, three storage horns on it
        b0, b1 = (x, 0.23 + T / 2, 0.62), (x, Y1 - 0.10, RAIL_TOP)
        k.bar("frame", b0, b1, 0.06, 0.06, up=(1, 0, 0), cut0=((0, 0.23 + T / 2, 0), (0, 1, 0)),
              cut1=((0, 0, RAIL_TOP), Z), weld=True)
        for f in (0.15, 0.50, 0.85):
            p = on(b0, b1, f)
            horn(k, "frame", x, p[1], p[2] + 0.0, s, 0.22, x + s * 0.03)
        # the stop post under the pendulum's lower branch, its rubber bumper
        k.bar("frame", (x, -0.26, RAIL_TOP), (x, -0.26, 0.86), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("rubber", (x, -0.26, 0.885), (0.07, 0.07, 0.05), soft=0.006)
        k.box("warn", (x + s * (T / 2 + 0.001), 0.40, 1.00), (0.002, 0.05, 0.07), soft=0.0)
        # the axle's block hung under the apex
        k.box("frame", (x, PIV[0], (PIV[1] + 1.93) / 2), (T, 0.10, 1.93 - PIV[1] + 0.06), soft=0.004)
    # the cross tubes: at the front legs, under the apex (the axle runs through the blocks)
    bar_x(k, "frame", -1.21, 0.85, -(FX - T / 2), FX - T / 2)
    k.tube("steel", (-FX - 0.06, PIV[0], PIV[1]), (FX + 0.06, PIV[0], PIV[1]), 0.025, seg=28)
    for s in (1, -1):
        k.bolt((s * (FX + 0.06), PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.03)
    # the placard on the roof's rear slope
    pc = on(FRAME[2], FRAME[3], 0.35)
    k.box("placard", (FX + T / 2 + 0.002, pc[0], pc[1] - 0.02), (0.004, 0.17, 0.07), rx=math.atan2(FRAME[3][1] - FRAME[2][1], FRAME[3][0] - FRAME[2][0]), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("seam", line, (FX + T / 2 + 0.0043, pc[0], pc[1] - 0.008 - i * 0.024), 0.02, rz=math.pi / 2,
               spin=-math.atan2(FRAME[3][1] - FRAME[2][1], FRAME[3][0] - FRAME[2][0]), depth=0.0003)
    # ---- the pendulum: each arm a hub on the axle and three branches
    for s in (1, -1):
        x = s * AX
        k.tube("lever", (x - 0.05, PIV[0], PIV[1]), (x + 0.05, PIV[0], PIV[1]), 0.05, seg=32)
        hub = (x, PIV[0], PIV[1])
        k.sweep("lever", [hub, (x, FRONT_END[0], FRONT_END[1])], k.rect(0.06, 0.12, 0.01), up=(1, 0, 0), soft=0.002)
        k.sweep("lever", [hub, (x, REAR_END[0], REAR_END[1])], k.rect(0.06, 0.12, 0.01), up=(1, 0, 0), soft=0.002)
        k.sweep("lever", [hub] + [(x, y, z) for y, z in LOWER], k.rect(0.05, 0.08, 0.008), bend=0.15, up=(1, 0, 0), soft=0.002)
        horn(k, "lever", x, FRONT_END[0] + 0.03, FRONT_END[1], s, 0.26, x + s * 0.025)
        horn(k, "lever", x, REAR_END[0] - 0.03, REAR_END[1], s, 0.32, x + s * 0.025)
    # the front cross bar between the arms' front ends, the three grey bumper blocks on it
    bar_x(k, "lever", FRONT_END[0] + 0.05, FRONT_END[1], -(AX - 0.025), AX - 0.025, 0.07, 0.07)
    for bx in (-0.22, 0.0, 0.22):
        k.box("bumper", (bx, FRONT_END[0] + 0.05, FRONT_END[1] + 0.035 + 0.06), (0.21, 0.24, 0.12), soft=0.012)
    # ---- the carriage on the lower branch: the cross bar behind the back pad, its mounting plate, the back pad leaning
    # back, the shoulder cross bar with the pads hanging forward over the shoulders, the grips
    yb, zb = 0.59, 1.12
    bar_x(k, "lever", yb, zb, -(AX - 0.025), AX - 0.025, 0.06, 0.06)
    lean = math.radians(22)
    n = (0.0, -math.cos(lean), math.sin(lean))
    k.box("lever", (0, yb - 0.04, 1.05), (0.30, 0.02, 0.48), rx=-lean, soft=0.003)
    c = (0, yb - 0.05 - 0.05 * math.cos(lean), 1.05 + 0.05 * math.sin(lean))
    k.shaped_pad("pad", [(-0.18, -0.26), (0.18, -0.26), (0.16, 0.26), (-0.16, 0.26)], c, n, (1, 0, 0), 0.09, r=0.05, cushion=0.03)
    ys, zs = 0.30, 1.57
    bar_x(k, "lever", ys, zs, -(AX - 0.025), AX - 0.025, 0.05, 0.05)
    for s in (1, -1):
        x = s * 0.13
        k.bar("lever", (x, ys - 0.025, zs), (x, ys - 0.27, zs), 0.04, 0.04, cut0=((0, ys - 0.025, 0), (0, 1, 0)), weld=True)
        k.pad("pad", (x, ys - 0.15, zs - 0.07), (0.12, 0.24, 0.10), r=0.035)
        g0, g1 = (x + s * 0.02, ys - 0.27, zs), (s * 0.22, ys - 0.30, zs + 0.20)
        k.sweep("lever", [g0, (s * 0.20, ys - 0.29, zs + 0.02), g1], k.circle(0.014, 18), bend=0.04, soft=0.0015)
        k.tube("rubber", (s * 0.205, ys - 0.295, zs + 0.08), g1, 0.02, seg=22)
    # ---- the foot platform on its frame: two legs a side on the cross bars, the grit plate, the adjuster handle
    t = math.radians(28)
    pf, pb = (-0.80, 0.58), (-0.27, 0.30)
    mid = ((pf[0] + pb[0]) / 2, (pf[1] + pb[1]) / 2)
    L = math.hypot(pb[0] - pf[0], pf[1] - pb[1])
    nrm = (0.0, math.sin(t), math.cos(t))
    k.box("grip", (0, mid[0], mid[1] - 0.002), (0.68, L - 0.02, 0.004), rx=-t, soft=0.001)
    k.box("lever", (0, mid[0] - nrm[1] * 0.02, mid[1] - nrm[2] * 0.02), (0.70, L, 0.036), rx=-t, soft=0.004)
    for s in (1, -1):
        for y_, f in ((-0.78, 0.04), (-0.30, 0.95)):
            q = on(pf, pb, f)
            top = (q[0] - nrm[1] * 0.04, q[1] - nrm[2] * 0.04)
            k.bar("frame", (s * 0.28, y_, RAIL_TOP), (s * 0.28, top[0], top[1] + 0.02), 0.05, 0.05, up=(1, 0, 0),
                  cut0=((0, 0, RAIL_TOP), Z), cut1=((0, top[0], top[1]), nrm), weld=True)
    h0 = (0.0, -0.78 - T / 2, RAIL_Z)
    k.sweep("steel", [h0, (0.0, -1.00, RAIL_Z + 0.02), (0.0, -1.06, RAIL_Z + 0.12)], k.circle(0.012, 16), bend=0.04,
            cut0=(h0, (0, 1, 0)), soft=0.001)
    k.tube("rubber", (0.0, -1.03, RAIL_Z + 0.07), (0.0, -1.065, RAIL_Z + 0.13), 0.02, seg=20)

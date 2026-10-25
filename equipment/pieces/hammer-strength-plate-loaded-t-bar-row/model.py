"""Hammer Strength Plate-Loaded T-Bar Row (PL-TBR): a standing bent-over row, the lever pivoting at the floor at the
rear and running forward between the foot plates to the handles, the weight horn under them. Claude's pick (Roman,
2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_08 the empty true side, ref_12 the empty true front, ref_01 the
maker's render in Charcoal, ref_10 / ref_11 the three-quarters and the handles, ref_02-ref_07 in use), held to Life
Fitness's 210 x 82 x 53 cm (L x W x H), the foot plates 23.4 cm off the floor, the neutral grips 21.8 cm apart on
centre, the front weight horn and the two back rods (on a triangle on the lever). Side-view numbers off ref_08 at
~438 px/m. The lever lies level at rest on its stop.
Axes: metres, floor z = 0, the user stands on the foot plates facing -y (the handles' end), x+ = the user's left.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # black lever
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),                            # horns, axle
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "grip": dict(color=(0.03, 0.03, 0.03), rough=0.95),                                                 # the plates' tread
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4),
    "placard": dict(color=(0.04, 0.07, 0.22), rough=0.35),
}
VIEWS = {"three_quarter": (-35, 14, 1.15), "front": (0, 6, 1.15), "side": (90, 4, 1.15), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_handles": ((0.75, -1.45, 0.95), (0.0, -0.68, 0.48), 45),      # the handles, the post, the horn
    "detail_pivot": ((0.70, 1.55, 0.75), (0.0, 0.90, 0.30), 45),          # the rear bracket, the hub
    "detail_plates": ((0.85, -0.10, 0.75), (0.16, -0.37, 0.20), 45),      # a foot plate on its post and brace
}

SQ = 0.076
FOOT_H = 0.012
RAIL_Z = FOOT_H + SQ / 2
RAIL_TOP = FOOT_H + SQ
X_RAIL = 0.20
Y_REAR, Y_FRONT = 0.96, -0.66    # the rails' ends (the rear cross bar, the front cross bar)
FOOT_F = (0.40, -1.00)           # the splayed front legs' feet (x, y): Life Fitness's 82 cm width over them
# ---- the lever (level at rest)
PIV = (0.90, 0.33)               # the pivot (y, z): ref_08's rear bracket
X_BR = 0.09                      # the rear bracket's plates (x)
Z_LEV = 0.31                     # the lever's centre line at rest
LEV = (0.05, 0.10)               # its section: across (x) x tall
Y_POST = -0.70                   # the handles' post on the lever's front end
Z_BAR = 0.555                    # the wide bar (Life Fitness's 52.6 cm height to its top)
GRIP_X = 0.109                   # the neutral grips (21.8 cm apart on centre)
TRI = (0.43, -0.11, (0.16, 0.51))  # the triangle on the lever: its two feet (y) and its apex (y, z), the back rod there
ROD_X = 0.36                     # the back rods' tips
Z_HORN = 0.39                    # the front weight horn
HORN_L = 0.30
# ---- the foot plates
PLATE_TOP = 0.234
PLATE = (0.20, 0.38, 0.012)      # width (x), length (y), thickness
PLATE_X, PLATE_Y = 0.165, -0.37


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    rear_bracket(k)
    lever(k)
    foot_plates(k)


def foot(k, x, y, rz=0.0):
    k.box("rubber", (x, y, FOOT_H / 2), (SQ + 0.06, 0.09, FOOT_H), rz=rz, soft=0.003)
    c, s_ = math.cos(rz), math.sin(rz)
    for d in (-1, 1):
        o = d * (SQ / 2 + 0.018)
        k.cyl("hole", (x + o * c, y + o * s_, FOOT_H + 0.0002), 0.006, 0.0005, seg=14)


def base(k):
    """Two rails from the rear cross bar to the front cross bar, the front legs splayed out to their feet, the lever's
    stop on the front cross bar."""
    Y = (0, 1, 0)
    xi = X_RAIL - SQ / 2
    for s in (1, -1):
        x = s * X_RAIL
        k.bar("frame", (x, Y_REAR - SQ / 2, RAIL_Z), (x, Y_FRONT + SQ / 2, RAIL_Z), SQ, SQ,
              cut0=((0, Y_REAR - SQ / 2, 0), Y), cut1=((0, Y_FRONT + SQ / 2, 0), Y), weld=True)
        for by in (0.55, -0.10):
            k.bolt((s * (X_RAIL + SQ / 2), by, RAIL_Z), "+x" if s > 0 else "-x", size=0.012)
        # the front leg: off the front cross bar's end, forward and out to its foot
        fx, fy = s * FOOT_F[0], FOOT_F[1]
        k.sweep("frame", [(x, Y_FRONT, RAIL_Z), (fx, fy + 0.04, RAIL_Z)], k.rect(SQ, SQ, 0.008), up=(0, 0, 1),
                cut0=((0, Y_FRONT - SQ / 2, 0), (0, -1, 0)), weld=True)
        rz = math.atan2(fx - x, -(fy + 0.04 - Y_FRONT))    # the leg's heading
        v = ((fx - x), (fy + 0.04 - Y_FRONT))
        vl = math.hypot(*v)
        k.box("plastic", (fx + v[0] / vl * 0.004, fy + 0.04 + v[1] / vl * 0.004, RAIL_Z), (SQ + 0.004, 0.008, SQ + 0.004),
              rz=rz, soft=0.002)                                                        # its end cap
        foot(k, fx, fy + 0.07, rz=rz)
        for y_ in (Y_REAR,):
            foot(k, x, y_)
    for y_ in (Y_REAR, Y_FRONT):
        k.bar("frame", (-(X_RAIL + SQ / 2), y_, RAIL_Z), (X_RAIL + SQ / 2, y_, RAIL_Z), SQ, SQ)
        for s in (1, -1):
            k.box("plastic", (s * (X_RAIL + SQ / 2 + 0.004), y_, RAIL_Z), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)
    # the stop: a block on the front cross bar the lever rests on, its rubber top
    zs = Z_LEV - LEV[1] / 2
    k.box("frame", (0, Y_FRONT, (RAIL_TOP + zs - 0.012) / 2), (0.12, 0.07, zs - 0.012 - RAIL_TOP), soft=0.003)
    k.box("rubber", (0, Y_FRONT, zs - 0.006), (0.10, 0.06, 0.012), soft=0.003)
    k.box("warn", (0, Y_FRONT - SQ / 2 - 0.001, RAIL_Z), (0.035, 0.002, 0.03), soft=0.0)
    k.text("label", "HAMMER STRENGTH", (X_RAIL + SQ / 2 + 0.001, 0.30, RAIL_Z), 0.03, rz=math.pi / 2, spin=0.0,
           depth=0.0006)


def rear_bracket(k):
    """Two plates standing on the rear cross bar, the axle through them."""
    zb = RAIL_TOP
    for s in (1, -1):
        k.box("frame", (s * X_BR, Y_REAR - 0.01, (zb + PIV[1] + 0.07) / 2), (0.012, 0.13, PIV[1] + 0.07 - zb), soft=0.003)
        k.bolt((s * (X_BR + 0.006), PIV[0] + 0.0, PIV[1]), "+x" if s > 0 else "-x", size=0.03)
    k.tube("steel", (-(X_BR + 0.006), PIV[0], PIV[1]), (X_BR + 0.006, PIV[0], PIV[1]), 0.019)


def lever(k):
    """The lever: its hub on the axle, the 2 x 4 run forward level to the handles' post, the triangle and back rod on
    it, the post up to the wide bar and the neutral grips, the weight horn forward from the post."""
    hz = PIV[1]
    k.tube("lever", (-(X_BR - 0.006), PIV[0], hz), (X_BR - 0.006, PIV[0], hz), 0.045, seg=36)          # the hub
    y0 = PIV[0] - 0.045
    yp = Y_POST + 0.03                                  # the post's back face
    k.bar("lever", (0, y0, Z_LEV), (0, yp, Z_LEV), LEV[0], LEV[1], up=(0, 0, 1))
    # the post: a box on the lever's front end up under the wide bar, a gusset plate each side under the bar
    zb = Z_BAR - 0.02                                   # the wide bar's centre
    zt = zb - 0.016                                     # the post's top: under the bar
    k.bar("lever", (0, Y_POST, Z_LEV - LEV[1] / 2), (0, Y_POST, zt), 0.08, 0.06, up=(0, 1, 0))
    for s in (1, -1):
        k.bar("lever", (s * 0.03, Y_POST, zt - 0.11), (s * 0.15, Y_POST, zt + 0.01), 0.05, 0.012, up=(0, 1, 0),
              cut0=((s * 0.04, 0, 0), (s, 0, 0)), cut1=((0, 0, zt), (0, 0, 1)), weld=True)
    # the wide bar: one tube across the post's top, its ends turned up and forward, foam over the outer runs
    path = [(-0.33, Y_POST - 0.02, zb + 0.06), (-0.24, Y_POST, zb), (0.24, Y_POST, zb), (0.33, Y_POST - 0.02, zb + 0.06)]
    k.sweep("lever", path, k.circle(0.016, 20), bend=0.05)
    for s in (1, -1):
        k.sweep("rubber", [(s * 0.15, Y_POST, zb), (s * 0.24, Y_POST, zb), (s * 0.33, Y_POST - 0.02, zb + 0.06)],
                k.circle(0.020, 20), bend=0.05, soft=0.003)
        e, d = (s * 0.33, Y_POST - 0.02, zb + 0.06), (s * 0.09, -0.02, 0.06)
        dl = math.sqrt(sum(c * c for c in d))
        k.sweep("plastic", [e, tuple(e[i] + d[i] / dl * 0.01 for i in range(3))], k.circle(0.021, 20), soft=0.002)
        # the neutral grip: back from the bar toward the user, rising a little
        g0, g1 = (s * GRIP_X, Y_POST + 0.016, zb), (s * GRIP_X, Y_POST + 0.17, zb + 0.04)
        k.tube("lever", g0, g1, 0.016, seg=20)
        k.tube("rubber", ((g0[0], g0[1] + 0.03, g0[2] + 0.007)), g1, 0.020, soft=0.003)
        k.cyl("plastic", (g1[0], g1[1] + 0.004, g1[2] + 0.001), 0.021, 0.01, axis="y", seg=20, soft=0.002)
    # the weight horn: forward from the post's front face, a collar, the cap
    k.cyl("lever", (0, Y_POST - 0.03 - 0.01, Z_HORN), 0.05, 0.02, axis="y", seg=32, soft=0.004)
    k.tube("steel", (0, Y_POST - 0.048, Z_HORN), (0, Y_POST - 0.03 - HORN_L, Z_HORN), 0.025, seg=32)
    k.cyl("lever", (0, Y_POST - 0.03 - HORN_L - 0.008, Z_HORN), 0.029, 0.018, axis="y", seg=32, soft=0.005)
    k.box("warn", (0.031, Y_POST + 0.02, 0.45), (0.002, 0.03, 0.03), soft=0.0)
    # the triangle and the back rods at its apex
    ya, yb, (yc, zc) = TRI
    zl = Z_LEV + LEV[1] / 2
    for yf in (ya, yb):                                 # the struts: off the lever's top into the apex boss
        L = math.hypot(yc - yf, zc - zl)
        e = (0, yc - (yc - yf) / L * 0.04, zc - (zc - zl) / L * 0.04)
        k.bar("lever", (0, yf, zl), e, 0.06, 0.04, up=(1, 0, 0), cut0=((0, 0, zl), (0, 0, 1)), weld=True)
    k.cyl("lever", (0, yc, zc), 0.045, 0.10, axis="x", seg=32, soft=0.004)                # the apex boss
    for s in (1, -1):
        k.cyl("lever", (s * 0.06, yc, zc), 0.04, 0.02, axis="x", seg=32, soft=0.004)
        k.tube("steel", (s * 0.068, yc, zc), (s * ROD_X, yc, zc), 0.025, seg=32)
        k.cyl("plastic", (s * (ROD_X + 0.006), yc, zc), 0.029, 0.012, axis="x", seg=32, soft=0.004)
    # the placard on the lever's side (ref_14)
    for s in (1, -1):
        k.box("placard", (s * (LEV[0] / 2 + 0.001), -0.05, Z_LEV), (0.002, 0.16, 0.07), soft=0.0)


def foot_plates(k):
    """Each plate on a post off its rail, a brace out to the front leg; a tread on top."""
    for s in (1, -1):
        x = s * PLATE_X
        zp = PLATE_TOP - PLATE[2] / 2
        k.box("frame", (x, PLATE_Y, zp), PLATE, soft=0.002)
        k.box("grip", (x, PLATE_Y, PLATE_TOP + 0.002), (PLATE[0] - 0.01, PLATE[1] - 0.01, 0.004), soft=0.001)
        xp = s * X_RAIL
        k.bar("frame", (xp, PLATE_Y, RAIL_TOP), (xp, PLATE_Y, PLATE_TOP - PLATE[2]), 0.06, 0.06,
              cut0=((0, 0, RAIL_TOP), (0, 0, 1)), cut1=((0, 0, PLATE_TOP - PLATE[2]), (0, 0, 1)), weld=True)
        # the brace: from under the plate's front end forward and down onto the rail (ref_12's V, seen side on)
        q0 = (xp, PLATE_Y - PLATE[1] / 2 + 0.04, PLATE_TOP - PLATE[2])
        q1 = (xp, Y_FRONT + SQ / 2 + 0.03, RAIL_TOP)
        k.bar("frame", q0, q1, 0.04, 0.04, up=(1, 0, 0),
              cut0=((0, 0, q0[2]), (0, 0, 1)), cut1=((0, 0, RAIL_TOP), (0, 0, 1)), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """On the foot plates facing the handles, the knees bent, the hips back, the back flat at ~45 deg, the arms
    hanging to the neutral grips (the start of the row); for a short, a middle and a tall user."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        best = None
        for shank in range(5, 41, 5):
            for thigh in range(-95, 1, 5):
                for trunk in range(30, 81, 5):
                    sol = pose(H, shank, thigh, trunk)
                    if sol and (best is None or sol[0] < best[0]):
                        best = sol + (shank, thigh, trunk)
        miss, ball, arm, fore, out_, shank, thigh, trunk = best
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=shank, thigh=thigh, trunk=trunk, neck=-40,
                          arm=arm, forearm=fore, arm_out=out_)
    return out


def pose(H, shank, thigh, trunk):
    """The arms' best reach to the grips for this stance (the feet's balls on the plates' middles), plus a cost for a
    rounded, upright or squatting back (a row's start: a hip hinge, the back flat near 60 deg, the knees soft)."""
    r = math.radians
    ball_y = PLATE_Y - 0.02
    Lf = 0.152 * H
    ay, az = ball_y + 0.48 * Lf, PLATE_TOP + 0.039 * H            # the ankle (forward is -y)
    ky, kz = ay - math.sin(r(shank)) * 0.246 * H, az + math.cos(r(shank)) * 0.246 * H
    hy, hz = ky - math.sin(r(thigh)) * 0.245 * H, kz + math.cos(r(thigh)) * 0.245 * H
    sy, sz = hy - math.sin(r(trunk)) * 0.288 * H, hz + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    tx, ty, tz = GRIP_X, Y_POST + 0.10, Z_BAR - 0.02 + 0.025
    # the arms hang nearly straight at the grips: aim both segments along the shoulder-to-grip line
    dy, dz, dx = ty - sy, tz - sz, tx - sx
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    a = math.degrees(math.atan2(-dy, dz))               # body.figure's angle: from up, toward the face (-y)
    o = math.degrees(math.asin(max(-1.0, min(1.0, dx / max(d, 1e-6)))))
    cost = abs(d - 0.365 * H) * 10 + abs(trunk - 60) * 0.004 + abs(shank - 15) * 0.002 + abs(thigh + 25) * 0.003
    return (cost, (0.0, ball_y, PLATE_TOP), a, a, o)

"""Hammer Strength Plate-Loaded Abdominal Oblique Crunch (PL-AB): a seated crunch, the back on pads hung from a U-shaped
lever pivoting at the sides, the hands on the handles by the head, the ankles under rollers; the seat swivels for the
obliques. Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_14 the empty side, ref_11 the empty true front, ref_12 / ref_13 the
three-quarter fronts, ref_02-ref_10 in use, ref_01 the maker's render in Charcoal), held to Life Fitness's 144 cm width
(over the weight horns) and 154 cm height (to the handles), 4 horns. Its catalogue's 148 cm length does not fit the
photos (the side view gives about 0.95 m front to back, the swivelled seat and the loaded horns not counted): the
depth here is the photos'. Side-view numbers off ref_14 at ~461 px/m, front-view numbers off ref_11 at ~429 px/m.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black lever
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4),
    "placard": dict(color=(0.04, 0.07, 0.22), rough=0.35),
}
VIEWS = {"three_quarter": (-35, 12, 1.25), "front": (0, 5, 1.25), "side": (90, 3, 1.25), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_pivot": ((1.25, -0.70, 1.25), (0.53, 0.0, 0.95), 45),         # the side frame's apex, the hub, the horn
    "detail_seat": ((0.90, -1.20, 1.00), (0.0, -0.22, 0.58), 45),         # the swivel seat, its post, the rollers
    "detail_pads": ((0.80, -1.10, 1.70), (0.0, 0.15, 1.20), 45),          # the back pads, the handles, the top bar
}

FOOT_H = 0.022
SQ = 0.076
BOX = (0.076, 0.05)
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
# ---- the side frames (each an A on its floor rail)
X_SF = 0.50
Y_F, Y_R = -0.42, 0.50           # the floor rails' ends (front, rear)
PIV = (0.0, 0.95)                # the lever's pivot (y, z): the A's apex
REAR_LEG = [(0.44, RAIL_TOP), (0.05, PIV[1] - 0.09)]
FRONT_LEG = [(-0.16, RAIL_TOP), (-0.05, PIV[1] - 0.09)]
Z_CROSS = 0.45                   # the cross bars between the side frames (front view)
# ---- the lever (the black U, outside the side frames)
X_LEV = 0.563
TOP = (0.33, 1.25)               # its top bar (y, z)
ARM_UP = [(0.0, 0.95), (0.20, 1.15), TOP]
HORN_E = (0.37, 0.66)            # its lower arm's end, the weight horn there (behind and below the pivot)
LEV = (0.05, 0.09)
HORN_X = 0.72                    # Life Fitness's 144 cm width is over the weight horns
STORE_Z = 0.30                   # a storage horn low on each rear leg
# ---- the seat, the rollers, the pads, the handles
SEAT_C, SEAT_TOP = (-0.20,), 0.72
SEAT = (0.43, 0.36, 0.08)
Y_SWIVEL = -0.10                 # the swivel post (on the front cross bar)
ROLLER = (-0.42, 0.42)           # the ankle rollers' tube (y, z)
SPINE = ((0.33, 1.25), (0.17, 0.86))   # the pads' spine from the top bar down and forward (y, z)
PADS = ((0.40, 0.24, 0.21), (0.84, 0.24, 0.14))  # (position along the spine, width, height): the upper and the lumbar pad
PAD_T = 0.08
HANDLES = ((0.06, 0.33, 1.29), (0.17, 0.22, 1.54))   # each handle from its root to its tip (x, y, z), mirrored


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def on(pts, z):
    (y0, z0), (y1, z1) = pts
    return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for s in (1, -1):
        side_frame(k, s)
        lever_side(k, s)
    cross(k)
    top_bar(k)
    seat(k)


def foot(k, x, y):
    k.box("rubber", (x, y, 0.008 + (FOOT_H - 0.008) / 2), (BOX[0] + 0.004, 0.075, FOOT_H - 0.008), soft=0.003)
    k.box("rubber", (x, y, 0.004), (BOX[0] + 0.10, 0.065, 0.008), soft=0.003)


def side_frame(k, s):
    """The floor rail, the rear and front legs up from it to the apex block (the pivot's housing), a storage horn on
    the rear leg."""
    Z = (0, 0, 1)
    x = s * X_SF
    k.bar("frame", (x, Y_F, RAIL_Z), (x, Y_R, RAIL_Z), BOX[0], BOX[1])
    for ye, d in ((Y_F, -1), (Y_R, 1)):
        k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (BOX[0] + 0.004, 0.008, BOX[1] + 0.004), soft=0.002)
        foot(k, x, ye - d * 0.036)
    zb = PIV[1] - 0.09                                   # the apex block's underside
    for leg in (REAR_LEG, FRONT_LEG):
        k.bar("frame", (x,) + leg[0], (x,) + leg[1], SQ, SQ, up=(1, 0, 0),
              cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, zb), Z), weld=True)
    k.box("frame", (x, PIV[0], PIV[1] - 0.01), (SQ, 0.20, 0.16), soft=0.004)            # the apex block
    for dy in (-0.07, 0.07):
        k.bolt((x + s * SQ / 2, PIV[0] + dy, PIV[1] - 0.06), "+x" if s > 0 else "-x", size=0.012)
    yh = on(REAR_LEG, STORE_Z)
    xf = x + s * SQ / 2
    k.cyl("frame", (xf + s * 0.01, yh, STORE_Z), 0.045, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, yh, STORE_Z), (s * HORN_X, yh, STORE_Z), 0.025, seg=32)
    k.cyl("plastic", (s * (HORN_X + 0.006), yh, STORE_Z), 0.029, 0.012, axis="x", seg=32, soft=0.004)
    zl = 0.62
    k.text("label", "HAMMER STRENGTH", (xf + s * 0.001, on(FRONT_LEG, zl), zl), 0.024, rz=math.pi / 2 * s,
           spin=math.atan2(FRONT_LEG[1][1] - FRONT_LEG[0][1], FRONT_LEG[1][0] - FRONT_LEG[0][0]), depth=0.0006)
    k.box("warn", (xf + s * 0.001, on(REAR_LEG, 0.70), 0.70), (0.002, 0.04, 0.04), soft=0.0)


def cross(k):
    """The cross bars between the side frames' legs (front and rear) at Z_CROSS, the floor cross bar at the rear."""
    xi = X_SF - SQ / 2
    for leg in (FRONT_LEG, REAR_LEG):
        y = on(leg, Z_CROSS)
        k.bar("frame", (-xi, y, Z_CROSS), (xi, y, Z_CROSS), SQ, 0.05, cut0=((-xi, 0, 0), (1, 0, 0)),
              cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    xi = X_SF - BOX[0] / 2
    k.bar("frame", (-xi, Y_R - 0.10, RAIL_Z), (xi, Y_R - 0.10, RAIL_Z), BOX[0], BOX[1],
          cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)


def lever_side(k, s):
    """One side of the U: the hub on the axle out of the apex block, the upper arm up and back to the top bar, the
    lower arm down and back to the weight horn."""
    x = s * X_LEV
    P = (x, PIV[0], PIV[1])
    x0 = s * (X_SF + SQ / 2)
    k.tube("steel", (x0, P[1], P[2]), (s * (X_LEV + LEV[0] / 2 + 0.012), P[1], P[2]), 0.019)       # the axle
    k.bolt((s * (X_LEV + LEV[0] / 2 + 0.012), P[1], P[2]), "+x" if s > 0 else "-x", size=0.03)
    k.tube("lever", (x0, P[1], P[2]), (s * (X_LEV + LEV[0] / 2), P[1], P[2]), 0.05, seg=36)        # the hub
    up = [(x,) + p for p in ARM_UP]
    u = tuple((up[1][i] - up[0][i]) / math.dist(up[0], up[1]) for i in range(3))
    up[0] = tuple(P[i] + u[i] * 0.045 for i in range(3))
    zt = TOP[1] - SQ / 2
    k.sweep("lever", up[:-1] + [(x, TOP[0], zt)], k.rect(LEV[1], LEV[0], 0.006), bend=0.08, up=(1, 0, 0), soft=0.003,
            cut1=((0, 0, zt), (0, 0, 1)), weld=True)
    E = (x,) + HORN_E
    ud = tuple((E[i] - P[i]) / math.dist(P, E) for i in range(3))
    k.sweep("lever", [tuple(P[i] + ud[i] * 0.045 for i in range(3)), E], k.rect(LEV[1], LEV[0], 0.006), up=(1, 0, 0),
            soft=0.003)
    k.sweep("plastic", [E, tuple(E[i] + ud[i] * 0.012 for i in range(3))], k.rect(LEV[1] + 0.004, LEV[0] + 0.004, 0.003),
            up=(1, 0, 0), soft=0.002)
    hc = tuple(E[i] - ud[i] * 0.05 for i in range(3))
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, hc[1], hc[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    k.box("warn", (xf + s * 0.001, *lerp(P[1:], E[1:], 0.5)), (0.002, 0.04, 0.04), soft=0.0)


def top_bar(k):
    """The U's top bar across, the placard on it; the pads' spine from it down and forward, the upper and the lumbar
    pad on the spine; the two handles up from the bar's middle, splayed (the front view's V)."""
    xe = X_LEV + LEV[0] / 2
    k.bar("lever", (-xe, TOP[0], TOP[1]), (xe, TOP[0], TOP[1]), SQ, SQ)
    for s in (1, -1):
        k.box("plastic", (s * (xe + 0.004), TOP[0], TOP[1]), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)
    k.box("placard", (-0.30, TOP[0] - SQ / 2 - 0.001, TOP[1]), (0.24, 0.002, 0.05), soft=0.0)
    (y0, z0), (y1, z1) = SPINE
    L = math.hypot(y1 - y0, z1 - z0)
    dn = (0.0, (y1 - y0) / L, (z1 - z0) / L)            # down the spine
    face = (0.0, dn[2], -dn[1]) if dn[2] < 0 else (0.0, -dn[2], dn[1])   # the pads' face: forward (-y)
    face = face if face[1] < 0 else tuple(-c for c in face)
    s0 = (0.0, y0 + dn[1] * SQ / 2, z0 + dn[2] * SQ / 2)
    s1 = (0.0, y1, z1)
    k.bar("lever", (0.0, y0, z0), s1, 0.10, 0.04, up=face, cut0=((0, 0, z0 - SQ / 2), (0, 0, 1)), weld=True)
    for f, w, h in PADS:
        q = lerp((0.0, y0, z0), s1, f)
        c = tuple(q[i] + face[i] * (0.02 + PAD_T / 2) for i in range(3))
        k.shaped_pad("pad", [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], c, face, (1, 0, 0),
                     PAD_T, r=0.04, cushion=0.025)
    (hx0, hy0, hz0), (hx1, hy1, hz1) = HANDLES
    for s in (1, -1):
        a, b = (s * hx0, hy0, hz0), (s * hx1, hy1, hz1)
        k.tube("lever", (s * hx0, TOP[0], TOP[1]), b, 0.017, seg=20, cut0=((0, 0, TOP[1] + SQ / 2), (0, 0, 1)),
               weld=True)                                                                   # off the bar's top face
        k.tube("rubber", lerp(a, b, 0.35), b, 0.021, soft=0.003)
        ub = tuple((b[i] - a[i]) / math.dist(a, b) for i in range(3))
        k.sweep("plastic", [b, tuple(b[i] + ub[i] * 0.01 for i in range(3))], k.circle(0.022, 20), soft=0.002)


def seat(k):
    """The seat on its swivel: the post up off the front cross bar, the turntable, the seat's frame plate, the seat;
    the rollers' post down from the plate's front, the tube across, the two rollers; the swivel's pull knob."""
    yc = on(FRONT_LEG, Z_CROSS)
    zp0 = Z_CROSS + 0.025
    zf = SEAT_TOP - SEAT[2] - 0.015                     # the seat's frame plate (centre): the seat on it
    zt = zf - 0.015                                     # the turntable's top
    k.bar("frame", (0, yc, zp0), (0, yc, zt - 0.03), 0.07, 0.07, cut0=((0, 0, zp0), (0, 0, 1)), weld=True)
    k.cyl("frame", (0, yc, zt - 0.015), 0.08, 0.03, seg=48, soft=0.003)                           # the turntable
    k.box("frame", (0, SEAT_C[0], zf), (0.32, 0.40, 0.03), soft=0.003)
    c = (0.0, SEAT_C[0], SEAT_TOP - SEAT[2] / 2)
    k.pad("pad", c, SEAT, r=0.035)
    # the rollers
    yr, zr = ROLLER
    k.bar("frame", (0, yr, zf - 0.015), (0, yr, zr + 0.03), 0.06, 0.05, up=(0, 1, 0),
          cut0=((0, 0, zf - 0.015), (0, 0, 1)), weld=True)
    k.box("frame", (0, yr, zr), (0.06, 0.06, 0.06), soft=0.003)
    k.tube("steel", (-0.30, yr, zr), (0.30, yr, zr), 0.0125)
    for s in (1, -1):
        k.cyl("pad", (s * 0.155, yr, zr), 0.06, 0.25, axis="x", seg=40, soft=0.012)
        k.cyl("plastic", (s * 0.286, yr, zr), 0.022, 0.012, axis="x", seg=24, soft=0.002)
    k.tube("steel", (0.16, SEAT_C[0] + 0.05, zf), (0.25, SEAT_C[0] + 0.05, zf), 0.007)            # the swivel's pull pin
    k.cyl("plastic", (0.26, SEAT_C[0] + 0.05, zf), 0.02, 0.03, axis="x", seg=24, soft=0.006)


FIT_VIEWS = ("side", "three_quarter", "front")


def fit():
    """On the seat facing -y, the back on the pads, the hands on the handles by the head, the knees bent sharply and
    the ankles hooked under the rollers (the start of the crunch); for a short, a middle and a tall user."""
    out = {}
    r = math.radians
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        hip = (0.0, SEAT_C[0] + 0.10 + 0.02 * sc, SEAT_TOP + 0.045 * sc)
        thigh, shank, sole = -84.0, 38.0, -30.0           # the shins back behind the rollers (ref_06)
        d = lambda a: (-math.sin(r(a)), math.cos(r(a)))    # (y, z): from up toward the face (-y)
        knee = (hip[1] - d(thigh)[0] * 0.245 * H, hip[2] - d(thigh)[1] * 0.245 * H)
        ank = (knee[0] - d(shank)[0] * 0.246 * H, knee[1] - d(shank)[1] * 0.246 * H)
        so = (-math.cos(r(sole)), math.sin(r(sole)))     # along the sole, to the toes
        su = (math.sin(r(sole)), math.cos(r(sole)))      # out of the sole
        Lf = 0.152 * H
        ball = (0.0, ank[0] + so[0] * 0.48 * Lf - su[0] * 0.039 * H, ank[1] + so[1] * 0.48 * Lf - su[1] * 0.039 * H)
        lean = 18
        arm, forearm, arm_out = reach(H, hip, -lean)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=sole, shank=shank, thigh=thigh, trunk=-lean, neck=12,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles that put the left hand on the left handle's rubber, the elbow forward and out (the hands by the
    head, as the photos' users hold them)."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    (hx0, hy0, hz0), (hx1, hy1, hz1) = HANDLES
    tx, ty, tz = lerp((hx0, hy0, hz0), (hx1, hy1, hz1), 0.6)

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        m = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / m * 0.186 * H, sy + ay / m * 0.186 * H, sz + az / m * 0.186 * H
        g = 0.191 * H
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ey > sy else 0.0)

    best = min(((miss(a, f, o), a, f, o) for a in range(-30, 181, 5) for f in range(-180, 1, 5) for o in range(0, 81, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    if best[0] > 0.03:
        print(f"fit: the hand {best[0] * 100:.0f} cm from the handle", flush=True)
    return best[1], best[2], best[3]

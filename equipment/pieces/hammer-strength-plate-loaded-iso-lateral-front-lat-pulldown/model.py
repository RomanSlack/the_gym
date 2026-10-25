"""Hammer Strength Plate-Loaded Iso-Lateral Front Lat Pulldown (IL-PD): a seated pulldown, the user's back to the
tower, each arm its own lever pivoting on the tower's top yoke, its handle high over the head, its weight horn behind
and below the pivot. Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_10 the empty true side, ref_09 the empty true front, ref_11 / ref_12
the three-quarters, ref_02-ref_08 in use, ref_01 the maker's render), held to Life Fitness's 165 x 124 x 201 cm (L x W x
H, the width over the weight horns, the height to the levers' tops), 6 storage horns. Side-view numbers off ref_10 at
~405 px/m, front-view numbers off ref_09 at ~300 px/m. The shop's variant (ref_01) is Charcoal with black upholstery.
The tower: two legs a side leaning in toward the top (front view), the rear one near upright, the front one the
family's S (side view), the storage horns on them; the seat on its own small frame in front of it (an inverted U on the
centre line carrying the belly pad and the knee pads' adjustable arm).
Axes: metres, floor z = 0, the user sits facing -y (the tower behind, at +y), x+ = the user's left; both sides mirror.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # black levers
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),                            # horns, axles
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),                                                    # warning labels
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4),
    "placard": dict(color=(0.04, 0.07, 0.22), rough=0.35),                                              # the instructions
}
VIEWS = {"three_quarter": (-35, 12, 1.25), "front": (0, 5, 1.25), "side": (90, 3, 1.25), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_pivot": ((1.20, -0.40, 2.10), (0.32, 0.18, 1.62), 50),        # the yoke, the pivot plates, the hubs
    "detail_handles": ((0.80, -1.20, 2.00), (0.20, -0.27, 1.88), 50),     # the grips over the seat
    "detail_seat": ((0.85, -1.40, 1.05), (0.0, -0.40, 0.75), 50),         # the U frame, belly pad, knee pads, seat
}

# ---- the base
FOOT_H = 0.03
BOX = (0.076, 0.05)
SQ = 0.076
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
X_RAIL = 0.50
Y0, Y1 = -0.82, 0.82             # Life Fitness's 165 cm length
BY = (-0.78, -0.40, 0.07, 0.78)  # the cross bars: the seat frame's front and back, under the tower, the rear
# ---- the tower (each side s), from the side view (y, z) and the front view (x leaning in with height)
Z_YOKE = 1.50                    # the yoke's centre (a deep bar across the legs' tops)
YOKE = (0.15, 0.076)             # its depth (y) x height
Y_YOKE = 0.19
X_TOP = 0.21                     # the legs' tops (x)
REAR_LEG = [(0.08, RAIL_TOP), (0.14, Z_YOKE - YOKE[1] / 2)]
FRONT_LEG = [(0.62, RAIL_TOP), (0.46, 0.84), (0.42, 1.04), (0.24, Z_YOKE - YOKE[1] / 2)]   # the S
HORNS = (("front", 0.22), ("front", 0.68), ("rear", 0.30))    # the storage horns (the 25 / 45 / 10 lb ones)
HORN_S = 0.64
# ---- the levers
PL = (0.13, 0.51)                # the pivot plates each side (x), the hub between them
X_LEV = 0.32
PIV = (0.19, 1.66)               # the pivot (y, z)
Z_PL = 1.79                      # the plates' tops
TOP = (-0.25, 1.99)              # the lever's top end over the user (side view)
BEND, HORN_E = (0.40, 1.56), (0.57, 1.18)   # its rear arm: back over the yoke, then down to the weight horn
LEV = (0.05, 0.09)
HORN_X = 0.62                    # Life Fitness's 124 cm width is over the weight horns
GRIP_IN = 0.10
# ---- the seat and its frame (on the centre line)
SEAT_TOP, SEAT_Y = 0.63, -0.17  # set high, as the photos' users have it (it adjusts)
SEAT = (0.36, 0.30, 0.08)
U_REAR, U_FRONT, U_TOP = -0.40, -0.74, 1.07  # the inverted U's posts (y) and its top
BELLY = (0.20, 0.24, 0.07)       # the belly pad: width, height, thickness (on the U's rear post, facing the user)
BELLY_Z = 0.97
KNEE = (U_REAR - 0.068, 0.84)    # the knee pads' tube (y, z): its boss on the sleeve's front


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def leg_x(z):
    """The legs lean in: x at height z (front view, ref_09)."""
    return X_RAIL - (X_RAIL - X_TOP) * (z - RAIL_TOP) / (Z_YOKE - YOKE[1] / 2 - RAIL_TOP)


def on_leg(pts, z):
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    for s in (1, -1):
        tower(k, s)
        lever(k, s)
    yoke(k)
    seat_frame(k)
    seat(k)


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (BOX[0] + 0.03, 0.10, FOOT_H), soft=0.004)


def base(k):
    bw, bh = BOX
    for s in (1, -1):
        x = s * X_RAIL
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), bw, bh)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (bw + 0.004, 0.008, bh + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.05)
        for by in (Y0 + 0.14, -0.25, 0.30, Y1 - 0.14):
            k.bolt((s * (X_RAIL + bw / 2), by, RAIL_Z), "+x" if s > 0 else "-x", size=0.012)
    xi = X_RAIL - bw / 2
    for y_ in BY:
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), bw, bh,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    Y = (0, 1, 0)
    for a, b in zip(BY, BY[1:3]):                       # the spine under the seat, between the cross bars
        k.bar("frame", (0, a + bw / 2, RAIL_Z), (0, b - bw / 2, RAIL_Z), bw, bh,
              cut0=((0, a + bw / 2, 0), Y), cut1=((0, b - bw / 2, 0), Y), weld=True)
    for s in (1, -1):
        k.box("warn", (s * (X_RAIL + bw / 2 + 0.001), 0.40, RAIL_Z), (0.002, 0.035, 0.03), soft=0.0)


def tower(k, s):
    """One side: the near-upright rear leg and the S-shaped front leg, both off the side rail leaning in to the yoke,
    the storage horns on their outer faces."""
    Z = (0, 0, 1)
    zt = Z_YOKE - YOKE[1] / 2
    for pts, name in ((REAR_LEG, "rear"), (FRONT_LEG, "front")):
        path = [(s * leg_x(z), y, z) for y, z in pts]
        k.sweep("frame", path, k.rect(SQ, SQ, 0.008), bend=0.10, up=(1, 0, 0),
                cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, zt), Z), weld=True)
    for which, zh in HORNS:
        pts = FRONT_LEG if which == "front" else REAR_LEG
        yh, xf = on_leg(pts, zh), s * (leg_x(zh) + SQ / 2)
        k.cyl("frame", (xf + s * 0.016, yh, zh), 0.045, 0.02, axis="x", seg=32, soft=0.004)   # (the leg leans: its face too)
        k.tube("steel", (xf + s * 0.024, yh, zh), (s * HORN_S, yh, zh), 0.025, seg=32)
        k.cyl("plastic", (s * (HORN_S + 0.006), yh, zh), 0.029, 0.012, axis="x", seg=32, soft=0.004)
    zl = 1.20
    k.text("label", "HAMMER STRENGTH", (s * (leg_x(zl) + SQ / 2 + 0.001), on_leg(FRONT_LEG, zl), zl), 0.024,
           rz=math.pi / 2 * s, spin=math.atan2(FRONT_LEG[3][1] - FRONT_LEG[2][1], FRONT_LEG[3][0] - FRONT_LEG[2][0]),
           depth=0.0006)
    zw = 0.95
    k.box("warn", (s * (leg_x(zw) + SQ / 2 + 0.001), on_leg(REAR_LEG, zw), zw), (0.002, 0.04, 0.04), soft=0.0)


def yoke(k):
    """The yoke across the legs' tops, the pivot plates standing on it in pairs, the axles through them."""
    xe = PL[1] + 0.006
    k.bar("frame", (-xe, Y_YOKE, Z_YOKE), (xe, Y_YOKE, Z_YOKE), YOKE[0], YOKE[1], up=(0, 0, 1))
    zb = Z_YOKE + YOKE[1] / 2
    for s in (1, -1):
        for xp in PL:
            k.box("frame", (s * xp, PIV[0], (zb - 0.004 + Z_PL) / 2), (0.012, 0.15, Z_PL - zb + 0.004), soft=0.003)
            side = 1 if xp == PL[1] else -1
            for dy in (-0.05, 0.05):
                k.bolt((s * (xp + side * 0.006), PIV[0] + dy, zb + 0.04), ("+x" if s * side > 0 else "-x"), size=0.011)
        a0, a1 = s * (PL[0] - 0.018), s * (PL[1] + 0.018)
        k.tube("steel", (a0, PIV[0], PIV[1]), (a1, PIV[0], PIV[1]), 0.019)
        for x_, d in ((a0, -s), (a1, s)):
            k.bolt((x_ - d * 0.012, PIV[0], PIV[1]), ("+x" if d > 0 else "-x"), size=0.03)


def lever(k, s):
    """One lever: its hub on the axle, the front arm up and forward over the user to the handle, the rear arm down and
    back to the weight horn; the grip in from the top end, hanging a little."""
    x = s * X_LEV
    P = (x, PIV[0], PIV[1])
    T, B, E = (x,) + TOP, (x,) + BEND, (x,) + HORN_E
    k.tube("lever", (s * (PL[0] + 0.006), P[1], P[2]), (s * (PL[1] - 0.006), P[1], P[2]), 0.05, seg=36)   # the hub
    uf = tuple((T[i] - P[i]) / math.dist(P, T) for i in range(3))
    ub = tuple((B[i] - P[i]) / math.dist(P, B) for i in range(3))
    k.sweep("lever", [tuple(P[i] + uf[i] * 0.045 for i in range(3)), T], k.rect(LEV[1], LEV[0], 0.006), up=(1, 0, 0),
            soft=0.003)
    k.sweep("lever", [tuple(P[i] + ub[i] * 0.045 for i in range(3)), B, E], k.rect(LEV[1], LEV[0], 0.006), bend=0.06,
            up=(1, 0, 0), soft=0.003)
    for a, b in ((T, P), (E, B)):                       # the end caps
        u = tuple((a[i] - b[i]) / math.dist(a, b) for i in range(3))
        k.sweep("plastic", [a, tuple(a[i] + u[i] * 0.012 for i in range(3))], k.rect(LEV[1] + 0.004, LEV[0] + 0.004, 0.003),
                up=(1, 0, 0), soft=0.002)
    ue = tuple((E[i] - B[i]) / math.dist(B, E) for i in range(3))
    hc = tuple(E[i] - ue[i] * 0.05 for i in range(3))   # the weight horn
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, hc[1], hc[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the grip: in from the top end's inner face, curving down (ref_09 / ref_12)
    g0 = tuple(T[i] - uf[i] * 0.05 for i in range(3))
    g0 = (x - s * (LEV[0] / 2 - 0.004), g0[1], g0[2])
    g1 = (s * (GRIP_IN + 0.06), g0[1] - 0.01, g0[2] - 0.03)
    g2 = (s * GRIP_IN, g0[1] - 0.02, g0[2] - 0.11)
    k.sweep("lever", [g0, g1, g2], k.circle(0.017, 20), bend=0.05)
    k.tube("rubber", lerp(g0, g1, 0.45), g1, 0.021, soft=0.003)
    k.sweep("rubber", [g1, g2], k.circle(0.021, 20), soft=0.003)
    k.cyl("plastic", (g2[0], g2[1], g2[2] - 0.004), 0.022, 0.01, seg=20, soft=0.002)
    q = lerp(T, P, 0.45)                                # the instruction placard along the arm's outer face
    k.sweep("placard", [(x + s * (LEV[0] / 2 + 0.001), q[1] - uf[1] * 0.08, q[2] - uf[2] * 0.08),
                        (x + s * (LEV[0] / 2 + 0.001), q[1] + uf[1] * 0.08, q[2] + uf[2] * 0.08)],
            k.rect(0.06, 0.002, 0.0), up=(1, 0, 0), soft=0.0)
    k.box("warn", (x + s * (LEV[0] / 2 + 0.001), *lerp(B[1:], E[1:], 0.4)), (0.002, 0.04, 0.04), soft=0.0)


def seat_frame(k):
    """The inverted U on the centre line in front of the seat (its posts on the front cross bars, a rounded top), the
    belly pad on the rear post facing the user, the knee pads' arm in a sleeve on the rear post (pop pin), the two
    roller pads on its tube."""
    Z = (0, 0, 1)
    r = 0.10
    path = [(0, U_REAR, RAIL_TOP), (0, U_REAR, U_TOP), (0, U_FRONT, U_TOP), (0, U_FRONT, RAIL_TOP)]
    k.sweep("frame", path, k.rect(0.06, 0.06, 0.006), bend=r, up=(1, 0, 0),
            cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, RAIL_TOP), (0, 0, -1)), weld=True)
    # the belly pad
    yb = U_REAR + 0.03
    k.box("frame", (0, yb + 0.004, BELLY_Z), (0.12, 0.008, 0.18), soft=0.001)
    k.shaped_pad("pad", [(-BELLY[0] / 2, -BELLY[1] / 2), (BELLY[0] / 2, -BELLY[1] / 2), (BELLY[0] / 2, BELLY[1] / 2),
                         (-BELLY[0] / 2, BELLY[1] / 2)], (0, yb + 0.008 + BELLY[2] / 2, BELLY_Z), (0, 1, 0), (1, 0, 0),
                 BELLY[2], r=0.04, cushion=0.025)
    # the knee pads' arm: a sleeve round the rear post, the arm forward to the tube
    zk = KNEE[1]
    for sx, sy, w_, d_ in ((1, 0, 0.008, 0.076), (-1, 0, 0.008, 0.076), (0, 1, 0.06, 0.008), (0, -1, 0.06, 0.008)):
        k.box("frame", (sx * 0.034, U_REAR + sy * 0.034, zk), (w_, d_, 0.12), soft=0.001)
    k.cyl("plastic", (0.038 + 0.015, U_REAR, zk), 0.018, 0.03, axis="x", seg=24, soft=0.005)     # the pop pin
    k.tube("steel", (0.038, U_REAR, zk), (0.042, U_REAR, zk), 0.006)
    k.tube("frame", (-0.32, KNEE[0], zk), (0.32, KNEE[0], zk), 0.019)
    k.box("frame", (0, KNEE[0], zk), (0.08, 0.06, 0.06), soft=0.003)                         # the tube's boss
    for s in (1, -1):
        k.cyl("pad", (s * 0.19, KNEE[0], zk), 0.05, 0.23, axis="x", seg=40, soft=0.012)
        k.cyl("plastic", (s * 0.31, KNEE[0], zk), 0.024, 0.01, axis="x", seg=24, soft=0.002)


def seat(k):
    """The seat on its post off the spine (an outer sleeve with holes, the inner post, the pop pin at its front)."""
    bw = 0.076
    zs = 0.36
    wt = (bw - 0.058) / 2
    for sx, sy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (sx * (bw - wt) / 2, SEAT_Y + sy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP),
              soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, SEAT_Y - bw / 2 - 0.0005, 0.15 + i * 0.04), 0.007, 0.001, axis="y", seg=14)
    zt = SEAT_TOP - SEAT[2] - 0.012
    k.bar("frame", (0, SEAT_Y, zs - 0.08), (0, SEAT_Y, zt), 0.058, 0.058, up=(0, 1, 0))
    k.tube("steel", (0, SEAT_Y - 0.02, zs - 0.03), (0, SEAT_Y - bw / 2 - 0.035, zs - 0.03), 0.007)
    k.cyl("plastic", (0, SEAT_Y - bw / 2 - 0.05, zs - 0.03), 0.02, 0.03, axis="y", seg=24, soft=0.006)
    k.box("frame", (0, SEAT_Y, zt + 0.006), (0.26, 0.22, 0.012), soft=0.002)
    c = (0.0, SEAT_Y, SEAT_TOP - SEAT[2] / 2)
    k.shaped_pad("pad", [(-SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, SEAT[1] / 2),
                         (-SEAT[0] / 2, SEAT[1] / 2)], c, (0, 0, 1), (1, 0, 0), SEAT[2], r=0.06, cushion=0.03)


FIT_VIEWS = ("side", "three_quarter", "front")


def fit():
    """On the seat facing away from the tower, the thighs under the knee pads, the feet on the floor, the arms up to
    the grips at the start, for a short, a middle and a tall user (the seat adjusts; shown at one height: the short
    user rises off the seat to take the grips, as the photos' users do)."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        s = H / 1.78
        hip = (0.0, SEAT_Y + 0.05, SEAT_TOP + 0.045 * s)
        lt, ls = 0.245 * H, 0.246 * H
        kz = ls + 0.039 * H
        a = -math.degrees(math.acos(max(-1.0, min(1.0, (hip[2] - kz) / lt))))
        ky = hip[1] - lt * math.sin(math.radians(-a))
        ball = (0.0, ky - 0.073 * H, 0.0)
        arm, forearm, arm_out, miss = reach(H, hip, -4)
        if miss > 0.02:
            print(f"fit {label}: the grips {miss * 100:.0f} cm out of reach seated", flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=0, thigh=a, trunk=-4, neck=6,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles that put the left hand nearest the left grip's middle; returns them and the distance left."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    T = TOP
    tx, ty, tz = GRIP_IN + 0.04, T[0] - 0.06, T[1] - 0.10

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        n = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / n * 0.186 * H, sy + ay / n * 0.186 * H, sz + az / n * 0.186 * H
        g = 0.191 * H
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz))

    best = min(((miss(a, f, o), a, f, o) for a in range(-40, 61, 5) for f in range(-40, 61, 5) for o in range(-30, 31, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    return best[1], best[2], best[3], best[0]

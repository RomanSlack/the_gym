"""Hammer Strength Plate-Loaded Iso-Lateral Shoulder Press (IL-SP): a reclined seated press overhead, each arm its own
lever hanging from a pivot in the top frame, its grip beside the shoulder, its weight horn just above the grip. Claude's
pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_08 the empty true side, ref_10 / ref_07 the empty true fronts, ref_09
/ ref_11 the three-quarters, ref_02-ref_06 in use, ref_01 the maker's render in Charcoal), held to Life Fitness's
132 x 152 x 185 cm (L x W x H, the width over the storage horns), 8 storage horns. Side-view numbers off ref_08 at
~384 px/m, front-view numbers off ref_10 at ~428 px/m. The frame: straight front uprights (three horns each) bent back
at the top into the top frame (a flat rectangle, the pivots between its inner and outer bars), the family's S inside
them (a fourth horn at its foot); the seat tilted back on its post, the back pad steeply reclined on its own post.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left; both sides mirror images (s = +1 / -1).
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
    "detail_top": ((1.10, -1.20, 2.40), (0.35, -0.27, 1.78), 50),        # the top frame, the pivots, the hubs
    "detail_grip": ((0.95, -0.80, 1.35), (0.33, 0.10, 1.02), 50),        # the lever's foot, the horn, the grip
    "detail_seat": ((0.85, -1.20, 0.75), (0.0, -0.05, 0.45), 50),        # the tilted seat, its post, the back's post
}

# ---- the base
FOOT_H = 0.022
BOX = (0.076, 0.05)
SQ = 0.076
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
X_RAIL = 0.51
Y0, Y1 = -0.68, 0.64             # Life Fitness's 132 cm length
BY_F, BY_R = -0.60, 0.58
# ---- the uprights, the S, the top frame (side view y, z; front view x)
X_UP = 0.555                     # the front uprights
Y_UP = -0.64
UP_BEND = 1.45                   # where the upright leans back to the top frame
Z_TF = 1.81                      # the top frame's bars (centre)
Y_TF = (-0.40, -0.10)            # its front and rear cross bars
X_TF_IN = 0.16                   # its inner bars (the pivots between them and the outer ones)
X_S = 0.455                      # the S members
S_PATH = [(0.20, RAIL_TOP), (-0.12, 0.70), (-0.18, 0.98), (-0.40, 1.45), (-0.40, Z_TF - SQ / 2)]
HORNS_UP = (1.08, 0.59, 0.17)    # three horns on each upright (the 45, 25 and 10 lb ones)
HORN_S_Z = 0.23                  # and one at the S's foot (the 5)
HORN_TIP = 0.76                  # Life Fitness's 152 cm width is over the horns
# ---- the levers
X_LEV = 0.43
PIV = (-0.25, Z_TF)              # the axle runs through the inner and outer bars of the top frame
END = (0.12, 1.02)               # the lever's foot (side view), the grip there
HORN_F = 0.74                    # the weight horn this far down the lever (side view: the plate's centre)
LEV = (0.05, 0.09)
HORN_X = 0.66
GRIP_IN = 0.20
# ---- the seat and back
SEAT_Y, SEAT_TOP = -0.17, 0.58   # the seat's centre, its top there
SEAT_TILT = 20.0                 # tilted back (front edge up)
SEAT = (0.42, 0.32, 0.08)
BACK_BOT, BACK_TOP = (0.05, 0.53), (0.49, 1.05)  # the back pad's face (y, z): reclined ~40 deg (ref_08)
BACK = (0.28, 0.08)
Y_BPOST = 0.32                   # the back's post


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def on_path(pts, z):
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    for s in (1, -1):
        sides(k, s)
        lever(k, s)
    top(k)
    seat(k)
    back(k)


def foot(k, x, y):
    k.box("rubber", (x, y, 0.008 + (FOOT_H - 0.008) / 2), (BOX[0] + 0.004, 0.075, FOOT_H - 0.008), soft=0.003)
    k.box("rubber", (x, y, 0.004), (BOX[0] + 0.10, 0.065, 0.008), soft=0.003)


def base(k):
    bw, bh = BOX
    for s in (1, -1):
        x = s * X_RAIL
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), bw, bh)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (bw + 0.004, 0.008, bh + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.036)
        for by in (-0.30, 0.0, 0.35):
            k.bolt((s * (X_RAIL + bw / 2), by, RAIL_Z), "+x" if s > 0 else "-x", size=0.012)
    xi = X_RAIL - bw / 2
    for y_ in (BY_F, BY_R):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), bw, bh,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    Y = (0, 1, 0)
    k.bar("frame", (0, BY_F + bw / 2, RAIL_Z), (0, BY_R - bw / 2, RAIL_Z), bw, bh,
          cut0=((0, BY_F + bw / 2, 0), Y), cut1=((0, BY_R - bw / 2, 0), Y), weld=True)
    k.box("warn", (0.20, BY_F - bw / 2 - 0.001, RAIL_Z), (0.04, 0.002, 0.035), soft=0.0)


def horn(k, s, xf, y, z, tip):
    k.cyl("frame", (xf + s * 0.01, y, z), 0.045, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, y, z), (s * tip, y, z), 0.025, seg=32)
    k.cyl("plastic", (s * (tip + 0.006), y, z), 0.029, 0.012, axis="x", seg=32, soft=0.004)


def sides(k, s):
    """One side: the front upright off the rail's front, straight up then leaning back into the top frame's outer bar;
    the S inside it off the rail's middle up to the top frame's front bar; the storage horns."""
    Z = (0, 0, 1)
    x = s * X_UP
    zt = Z_TF - SQ / 2
    k.sweep("frame", [(x, Y_UP, RAIL_TOP), (x, Y_UP, UP_BEND), (x, Y_TF[0] + 0.02, zt)], k.rect(SQ, SQ, 0.008),
            bend=0.12, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, zt), Z), weld=True)
    xs = s * X_S
    k.sweep("frame", [(xs, y, z) for y, z in S_PATH], k.rect(SQ, SQ, 0.008), bend=0.10, up=(1, 0, 0),
            cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, zt), Z), weld=True)
    for zh in HORNS_UP:
        horn(k, s, x + s * SQ / 2, Y_UP, zh, HORN_TIP)
    horn(k, s, xs + s * SQ / 2, on_path(S_PATH, HORN_S_Z), HORN_S_Z, 0.60)
    zl = 1.25
    k.text("label", "HAMMER STRENGTH", (xs + s * (SQ / 2 + 0.001), on_path(S_PATH, zl), zl), 0.024,
           rz=math.pi / 2 * s, spin=math.atan2(S_PATH[3][1] - S_PATH[2][1], S_PATH[3][0] - S_PATH[2][0]), depth=0.0006)
    k.box("warn", (xs + s * (SQ / 2 + 0.001), on_path(S_PATH, 0.85), 0.85), (0.002, 0.04, 0.04), soft=0.0)


def top(k):
    """The top frame: the front and rear cross bars full width, the outer bars over the uprights, the inner bars; the
    axles through the inner and outer bars."""
    xo = X_UP
    for y_ in Y_TF:
        k.bar("frame", (-(xo + SQ / 2), y_, Z_TF), (xo + SQ / 2, y_, Z_TF), SQ, SQ)
    yi0, yi1 = Y_TF[0] + SQ / 2, Y_TF[1] - SQ / 2
    Y = (0, 1, 0)
    for s in (1, -1):
        for xb in (X_TF_IN, xo):
            k.bar("frame", (s * xb, yi0, Z_TF), (s * xb, yi1, Z_TF), SQ, SQ,
                  cut0=((0, yi0, 0), Y), cut1=((0, yi1, 0), Y), weld=True)
        a0, a1 = s * (X_TF_IN - SQ / 2 - 0.012), s * (xo + SQ / 2 + 0.012)
        k.tube("steel", (a0, PIV[0], PIV[1]), (a1, PIV[0], PIV[1]), 0.019)
        for x_, d in ((a0, -s), (a1, s)):
            k.bolt((x_ - d * 0.012, PIV[0], PIV[1]), ("+x" if d > 0 else "-x"), size=0.03)
    for y_ in Y_TF:
        for s in (1, -1):
            k.box("plastic", (s * (xo + SQ / 2 + 0.004), y_, Z_TF), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)


def lever(k, s):
    """One lever: its hub on the axle between the top frame's inner and outer bars, the arm down and back to its foot,
    the weight horn on its outer face near the foot, the grip in from the foot."""
    x = s * X_LEV
    P, E = (x, PIV[0], PIV[1]), (x, END[0], END[1])
    hx0, hx1 = s * (X_TF_IN + SQ / 2), s * (X_UP - SQ / 2)
    k.tube("lever", (hx0, P[1], P[2]), (hx1, P[1], P[2]), 0.05, seg=36)                 # the hub
    u = tuple((E[i] - P[i]) / math.dist(P, E) for i in range(3))
    k.sweep("lever", [tuple(P[i] + u[i] * 0.045 for i in range(3)), E], k.rect(LEV[1], LEV[0], 0.006), up=(1, 0, 0),
            soft=0.003)
    k.sweep("plastic", [E, tuple(E[i] + u[i] * 0.012 for i in range(3))], k.rect(LEV[1] + 0.004, LEV[0] + 0.004, 0.003),
            up=(1, 0, 0), soft=0.002)
    L = math.dist(P, E)
    hc = tuple(P[i] + u[i] * L * HORN_F for i in range(3))
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, hc[1], hc[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the grip: in from the foot's inner face, dipping a little (front view)
    gb = tuple(E[i] - u[i] * 0.05 for i in range(3))
    g0 = (x - s * (LEV[0] / 2 - 0.004), gb[1], gb[2])
    g1 = (s * GRIP_IN, gb[1] + 0.01, gb[2] - 0.04)
    k.tube("lever", g0, g1, 0.016, seg=20)
    k.tube("rubber", lerp(g0, g1, 0.3), g1, 0.02, soft=0.003)
    k.cyl("plastic", (g1[0] - s * 0.005, g1[1], g1[2]), 0.021, 0.01, axis="x", seg=20, soft=0.002)
    q = lerp(P, E, 0.40)                                # the instruction placard on the outer face
    k.sweep("placard", [(xf + s * 0.001, q[1] - u[1] * 0.09, q[2] - u[2] * 0.09),
                        (xf + s * 0.001, q[1] + u[1] * 0.09, q[2] + u[2] * 0.09)],
            k.rect(0.06, 0.002, 0.0), up=(1, 0, 0), soft=0.0)
    k.box("warn", (xf + s * 0.001, *lerp(P[1:], E[1:], 0.88)), (0.002, 0.04, 0.04), soft=0.0)


def seat(k):
    """The seat tilted back on its post off the spine (the sleeve with holes, the inner post, the pop pin)."""
    bw = 0.076
    zs = 0.30
    wt = (bw - 0.058) / 2
    for sx, sy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (sx * (bw - wt) / 2, SEAT_Y + sy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP),
              soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, SEAT_Y - bw / 2 - 0.0005, 0.12 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    t = math.radians(SEAT_TILT)
    n = (0.0, math.sin(t), math.cos(t))                # the seat's up: tilted back (its front edge up)
    c = (0.0, SEAT_Y, SEAT_TOP - SEAT[2] / 2 / math.cos(t))
    br = tuple(c[i] - n[i] * (SEAT[2] / 2 + 0.02) for i in range(3))
    k.bar("frame", (0, SEAT_Y, zs - 0.06), (0, SEAT_Y, br[2]), 0.058, 0.058, up=(0, 1, 0),
          cut1=(tuple(br[i] - n[i] * 0.02 for i in range(3)), n), weld=True)                # cut to the bracket's tilt
    k.box("frame", br, (0.20, 0.16, 0.04), rx=-t, soft=0.003)                            # the tilted seat bracket
    k.tube("steel", (0, SEAT_Y - 0.02, zs - 0.03), (0, SEAT_Y - bw / 2 - 0.035, zs - 0.03), 0.007)
    k.cyl("plastic", (0, SEAT_Y - bw / 2 - 0.05, zs - 0.03), 0.02, 0.03, axis="y", seg=24, soft=0.006)
    k.pad("pad", c, SEAT, r=0.035, rx=-t)


def back(k):
    """The reclined back pad on its spine plate, the post from the spine up under it."""
    (y0, z0), (y1, z1) = BACK_BOT, BACK_TOP
    L = math.hypot(y1 - y0, z1 - z0)
    up = (0.0, (y1 - y0) / L, (z1 - z0) / L)
    face = (0.0, -up[2], up[1])
    mid = ((y0 + y1) / 2, (z0 + z1) / 2)
    c = (0.0, mid[0] - face[1] * BACK[1] / 2, mid[1] - face[2] * BACK[1] / 2)
    k.shaped_pad("pad", [(-BACK[0] / 2, -L / 2), (BACK[0] / 2, -L / 2), (BACK[0] / 2, L / 2), (-BACK[0] / 2, L / 2)],
                 c, face, (1, 0, 0), BACK[1], r=0.05, cushion=0.03)
    sp = tuple(c[i] - face[i] * (BACK[1] / 2 + 0.02) for i in range(3))
    s0, s1 = tuple(sp[i] - up[i] * L * 0.45 for i in range(3)), tuple(sp[i] + up[i] * L * 0.40 for i in range(3))
    k.bar("frame", s0, s1, 0.12, 0.04, up=face)                                                    # the spine plate
    # the post: from the spine (base) straight up to the plate's back face
    f = (Y_BPOST - s0[1]) / (s1[1] - s0[1])
    q = lerp(s0, s1, f)
    zq = q[2] - 0.02 / face[2]                          # the plate's back face above the post
    k.bar("frame", (0, Y_BPOST, RAIL_TOP), (0, Y_BPOST, zq), 0.06, 0.06, up=(0, 1, 0),
          cut0=((0, 0, RAIL_TOP), (0, 0, 1)), cut1=(tuple(q[i] - face[i] * 0.02 for i in range(3)), face), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Reclined on the back pad facing -y, the hands on the grips beside the shoulders (the start of the press), the
    feet flat on the floor; for a short, a middle and a tall user (the seat adjusts; shown at one height)."""
    out = {}
    lean = math.degrees(math.atan2(BACK_TOP[0] - BACK_BOT[0], BACK_TOP[1] - BACK_BOT[1]))
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        s = H / 1.78
        hip = (0.0, BACK_BOT[0] - 0.02 - 0.10 * s * math.cos(math.radians(lean)), SEAT_TOP - 0.02 + 0.06 * s)
        lt, ls = 0.245 * H, 0.246 * H
        kz = ls + 0.039 * H
        a = -math.degrees(math.acos(max(-1.0, min(1.0, (hip[2] - kz) / lt))))
        ky = hip[1] - lt * math.sin(math.radians(-a))
        ball = (0.0, ky - 0.073 * H, 0.0)
        arm, forearm, arm_out = reach(H, hip, -lean)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=0, thigh=a, trunk=-lean, neck=20,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles that put the left hand on the left grip's middle, the elbow below the hand."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    u = ((END[0] - PIV[0]), (END[1] - PIV[1]))
    n = math.hypot(*u)
    gy, gz = END[0] - u[0] / n * 0.05 + 0.005, END[1] - u[1] / n * 0.05 - 0.02
    tx, ty, tz = (X_LEV + GRIP_IN) / 2 - 0.04, gy, gz

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        m = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / m * 0.186 * H, sy + ay / m * 0.186 * H, sz + az / m * 0.186 * H
        g = 0.191 * H
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ez > hz else 0.0)

    best = min(((miss(a, f, o), a, f, o) for a in range(60, 271, 5) for f in range(-60, 121, 5) for o in range(0, 81, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    assert best[0] < 0.03, f"the grips are out of reach ({best[0]:.3f} m short)"
    return best[1], best[2], best[3]

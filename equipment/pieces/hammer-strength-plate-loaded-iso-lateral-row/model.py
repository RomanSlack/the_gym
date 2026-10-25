"""Hammer Strength Plate-Loaded Iso-Lateral Row (IL-ROW): a seated row, the chest on a pad, each arm its own lever
pivoting low at the front, its handles high in front of the chest, its weight horn below and in front of the pivot.
Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_02 the side in use, ref_03 the front in use, ref_01 / ref_12 the maker's
renders, ref_10 / ref_11 a gym's photos at rest), held to Life Fitness's 155 x 127 x 132 cm (L x W x H, the width over
the weight horns, the height to the handles at rest). Side-view numbers off ref_02 at ~465 px/m (the user there has the
handles pulled back: the levers are drawn here at rest, turned 40 deg forward about their pivots, the horns low as in
ref_11), front-view numbers off ref_03 at ~410 px/m. The shop's variant (ref_01) is Charcoal with black upholstery.
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
}
VIEWS = {"three_quarter": (-35, 12, 1.25), "front": (0, 5, 1.25), "side": (90, 3, 1.25), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_pivot": ((1.15, -0.85, 0.85), (0.46, -0.10, 0.50), 50),        # the pivot bracket, the hub, the A-legs
    "detail_handles": ((0.85, 0.75, 1.65), (0.32, -0.02, 1.22), 50),       # the double handles at the levers' tops
    "detail_seat": ((0.85, 1.20, 1.05), (0.0, 0.40, 0.80), 50),            # the seat on its post, the chest pad
}

# ---- the frame
FOOT_H = 0.03
BOX = (0.076, 0.05)              # base section (3 x 2 in)
SQ = 0.076
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
X_RAIL = 0.50                    # the side rails (front view)
Y0, Y1 = -0.77, 0.77             # the rails' ends: Life Fitness's 155 cm length
BY_F, BY_R = -0.72, 0.70         # the front and rear cross bars
# ---- the levers (each in its plane x = s * X_LEV), from the side view, at rest
X_LEV = 0.45
PIV = (-0.10, 0.55)              # the pivot (y, z): ref_02's bracket
PL = (0.31, 0.59)                # the bracket's two plates (x), the hub between them
REST = 40.0                      # ref_02 has the handles pulled back; at rest the lever sits this far forward (deg)
# the lever as ref_02 shows it (pulled): the main member from the horn up and back, curving level to the handle; two
# links from the pivot up into it
PULLED = dict(horn=(-0.49, 0.67), k1=(-0.10, 0.97), k2=(0.13, 1.05), hand=(0.32, 1.05), l1=(-0.23, 0.87), l2=(0.03, 1.01))
LEV = (0.05, 0.09)               # the lever section: across (x) x deep
HORN_X = 0.635                   # the weight horns' tips: Life Fitness's 127 cm width is over them
GRIP_IN = 0.19                   # the inner grips (x)
# ---- the user's side
SEAT_TOP, SEAT_Y = 0.83, 0.47    # the high seat (side view), its centre
SEAT = (0.38, 0.30, 0.08)
COL0, COL1 = (-0.14, RAIL_TOP), (0.10, 1.24)   # the chest pad's column: up and back off the spine (ref_01)
PAD_C, PAD = (0.21, 1.17), (0.25, 0.32, 0.08)  # the chest pad's centre (y, z), its width, height, thickness
FOOT_BAR = 0.33                  # the foot bar's height on the column (the feet at ~0.4 in ref_02)


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def rest(p):
    """A point of the pulled lever turned forward by REST about the pivot (y, z)."""
    a = math.radians(REST)
    vy, vz = p[0] - PIV[0], p[1] - PIV[1]
    return (PIV[0] + vy * math.cos(a) - vz * math.sin(a), PIV[1] + vy * math.sin(a) + vz * math.cos(a))


LP = {n: rest(p) for n, p in PULLED.items()}


def col_at(z):
    f = (z - COL0[1]) / (COL1[1] - COL0[1])
    return COL0[0] + (COL1[0] - COL0[0]) * f


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    for s in (1, -1):
        bracket(k, s)
        lever(k, s)
    column(k)
    seat(k)


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (BOX[0] + 0.03, 0.10, FOOT_H), soft=0.004)


def base(k):
    """The two side rails on their feet, the front and rear cross bars between them, the spine down the middle."""
    bw, bh = BOX
    for s in (1, -1):
        x = s * X_RAIL
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), bw, bh)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (bw + 0.004, 0.008, bh + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.05)
        for by in (Y0 + 0.16, Y0 + 0.26, Y1 - 0.26, Y1 - 0.16):
            k.bolt((s * (X_RAIL + bw / 2), by, RAIL_Z), "+x" if s > 0 else "-x", size=0.012)
    xi = X_RAIL - bw / 2
    for y_ in (BY_F, BY_R):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), bw, bh,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    Y = (0, 1, 0)
    k.bar("frame", (0, BY_F + bw / 2, RAIL_Z), (0, BY_R - bw / 2, RAIL_Z), bw, bh,
          cut0=((0, BY_F + bw / 2, 0), Y), cut1=((0, BY_R - bw / 2, 0), Y), weld=True)
    k.box("warn", (X_RAIL + bw / 2 + 0.001, -0.35, RAIL_Z), (0.002, 0.035, 0.03), soft=0.0)
    k.box("warn", (-X_RAIL - bw / 2 - 0.001, -0.35, RAIL_Z), (0.002, 0.035, 0.03), soft=0.0)


def bracket(k, s):
    """The pivot bracket on its A: two legs up off the side rail (front and back) into a base plate, the two upright
    plates on it, the axle through them."""
    Z = (0, 0, 1)
    xa = s * (X_RAIL - 0.01)
    zb = PIV[1] - 0.24                                  # the base plate's underside
    for yb in (-0.42, 0.22):                            # the A's feet on the rail
        top = (xa, PIV[0] + (0.035 if yb > PIV[0] else -0.035), zb)
        k.bar("frame", (xa, yb, RAIL_TOP), top, 0.06, 0.06, up=(1, 0, 0),
              cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, zb), Z), weld=True)
    xm = s * (PL[0] + PL[1]) / 2
    k.box("frame", (xm, PIV[0], zb + 0.0125), (PL[1] - PL[0] + 0.012, 0.16, 0.025), soft=0.002)
    for xp in PL:
        k.box("frame", (s * xp, PIV[0], (zb + 0.025 + PIV[1] + 0.09) / 2), (0.012, 0.14, PIV[1] + 0.09 - zb - 0.025),
              soft=0.003)
        side = 1 if xp == PL[1] else -1                 # outer / inner face
        for dz in (-0.12, 0.0):
            for dy in (-0.045, 0.045):
                k.bolt((s * (xp + side * 0.006), PIV[0] + dy, PIV[1] + dz - 0.04 if dz else PIV[1] + 0.05),
                       ("+x" if s * side > 0 else "-x"), size=0.011)
    a0, a1 = s * (PL[0] - 0.006 - 0.012), s * (PL[1] + 0.006 + 0.012)
    k.tube("steel", (a0, PIV[0], PIV[1]), (a1, PIV[0], PIV[1]), 0.019)
    for x_, d in ((a0, -s), (a1, s)):
        k.bolt((x_ - d * 0.012, PIV[0], PIV[1]), ("+x" if d > 0 else "-x"), size=0.03)


def lever(k, s):
    """One lever at rest: its hub on the axle, the main member from the horn up and back to the handle, two links from
    the hub up into it, the double handle at its top (an outer grip straight on, an inner one in from a cross bar)."""
    x = s * X_LEV
    p3 = lambda n: (x, LP[n][0], LP[n][1])
    P = (x, PIV[0], PIV[1])
    k.tube("lever", (s * (PL[0] + 0.006), P[1], P[2]), (s * (PL[1] - 0.006), P[1], P[2]), 0.045, seg=36)   # the hub
    H, K1, K2, Hd = p3("horn"), p3("k1"), p3("k2"), p3("hand")
    k.sweep("lever", [H, K1, K2, Hd], k.rect(LEV[1], LEV[0], 0.006), bend=0.10, up=(1, 0, 0), soft=0.003)
    for n, a, b, dx in (("l1", H, K1, 0.011), ("l2", K1, K2, -0.011)):   # the links: twin plates, the outer half of
        q = p3(n)                                       # the lever's width forward, the inner half up, off the hub
        t = tuple((b[i] - a[i]) / math.dist(a, b) for i in range(3))     # the main member's run there
        nm = (0.0, -t[2], t[1])                         # its face toward the hub
        if (P[1] - q[1]) * nm[1] + (P[2] - q[2]) * nm[2] < 0:
            nm = tuple(-c for c in nm)
        u = tuple((q[i] - P[i]) / math.dist(P, q) for i in range(3))
        xo = x + s * dx
        f = (xo, q[1] + nm[1] * (LEV[1] / 2 - 0.004), q[2] + nm[2] * (LEV[1] / 2 - 0.004))
        k.bar("lever", (xo, P[1] + u[1] * 0.04, P[2] + u[2] * 0.04), (xo, q[1], q[2]), 0.06, 0.022, up=(1, 0, 0),
              cut1=(f, nm), weld=True)
    ue = tuple((H[i] - K1[i]) / math.dist(H, K1) for i in range(3))
    k.sweep("plastic", [H, tuple(H[i] + ue[i] * 0.012 for i in range(3))], k.rect(LEV[1] + 0.004, LEV[0] + 0.004, 0.003),
            up=(1, 0, 0), soft=0.002)                                                     # the horn end's cap
    hc = tuple(H[i] - ue[i] * 0.05 for i in range(3))   # the weight horn, out from the outer face near the end
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, hc[1], hc[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the handles: the main member's end turned back to the user as the outer grip; a cross bar in from it carrying
    # the inner grip (ref_11 / ref_12)
    uh = tuple((Hd[i] - K2[i]) / math.dist(K2, Hd) for i in range(3))
    o1 = (x, Hd[1] + 0.20, Hd[2] + 0.10)
    k.tube("lever", tuple(Hd[i] - uh[i] * 0.03 for i in range(3)), o1, 0.017, seg=20)
    k.tube("rubber", lerp(Hd, o1, 0.35), o1, 0.021, soft=0.003)
    k.cyl("plastic", (o1[0], o1[1] + 0.004, o1[2] + 0.002), 0.022, 0.01, axis="y", seg=20, soft=0.002)
    c0, c1 = (x - s * LEV[0] / 2, Hd[1] - 0.07, Hd[2] - 0.03), (s * GRIP_IN, Hd[1] - 0.07, Hd[2])
    i1 = (s * GRIP_IN, Hd[1] + 0.17, Hd[2] + 0.07)
    k.sweep("lever", [(x - s * (LEV[0] / 2 - 0.004), c0[1], c0[2]), c1, i1], k.circle(0.017, 20), bend=0.04)
    k.tube("rubber", lerp(c1, i1, 0.3), i1, 0.021, soft=0.003)
    k.cyl("plastic", (i1[0], i1[1] + 0.004, i1[2] + 0.002), 0.022, 0.01, axis="y", seg=20, soft=0.002)
    wq = lerp(K1, H, 0.45)
    k.box("warn", (x + s * (LEV[0] / 2 + 0.001), wq[1], wq[2]), (0.002, 0.04, 0.04), soft=0.0)
    lq = lerp(K1, K2, 0.5)
    k.text("label", "HAMMER STRENGTH", (x + s * (LEV[0] / 2 + 0.001), lq[1], lq[2]), 0.022,
           rz=math.pi / 2 * s, spin=math.atan2(K2[2] - K1[2], K2[1] - K1[1]), depth=0.0006)


def column(k):
    """The chest pad's column up and back off the spine, the pad on its top, the foot bar across its front with the two
    foot plates."""
    cl = math.hypot(COL1[0] - COL0[0], COL1[1] - COL0[1])
    u = (0.0, (COL1[0] - COL0[0]) / cl, (COL1[1] - COL0[1]) / cl)
    k.bar("frame", (0, COL0[0], COL0[1]), (0, COL1[0], COL1[1]), SQ, SQ, up=(0, -u[2], u[1]),
          cut0=((0, 0, RAIL_TOP), (0, 0, 1)), weld=True)
    k.sweep("plastic", [(0, COL1[0], COL1[1]), (0, COL1[0] + u[1] * 0.01, COL1[1] + u[2] * 0.01)],
            k.rect(SQ + 0.004, SQ + 0.004, 0.003), up=(0, -u[2], u[1]), soft=0.002)
    # the pad: a plate off the column's back face, the pad on it facing the user (+y)
    nb = (0.0, u[2], -u[1])                             # the column's back face's normal (toward the user)
    cb = (0.0, col_at(PAD_C[1]) + nb[1] * SQ / 2, PAD_C[1] + nb[2] * SQ / 2)
    k.bar("frame", (0, col_at(PAD_C[1]), PAD_C[1]), (0, PAD_C[0] - PAD[2] / 2, PAD_C[1]), 0.06, 0.16, up=(0, 0, 1),
          cut0=(cb, nb), weld=True)
    w, h = PAD[0], PAD[1]
    k.shaped_pad("pad", [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], (0, PAD_C[0], PAD_C[1]),
                 (0, 1, 0), (1, 0, 0), PAD[2], r=0.05, cushion=0.03)
    # the foot bar and its plates (toes up)
    yf = col_at(FOOT_BAR)
    k.tube("frame", (-0.20, yf, FOOT_BAR), (0.20, yf, FOOT_BAR), 0.019)
    for s in (1, -1):
        k.cyl("plastic", (s * 0.205, yf, FOOT_BAR), 0.021, 0.01, axis="x", seg=20, soft=0.002)
        nz = (0.0, -math.sin(math.radians(40)), math.cos(math.radians(40)))   # the plate's face: toes up
        pc = (s * 0.12, yf, FOOT_BAR + 0.019 + 0.003)
        k.box("frame", pc, (0.10, 0.16, 0.008), rx=math.radians(40), soft=0.002)
        k.box("rubber", tuple(pc[i] + nz[i] * 0.006 for i in range(3)), (0.09, 0.15, 0.004), rx=math.radians(40), soft=0.001)
    k.box("label", (0, col_at(0.70) - SQ / 2 / u[2] - 0.001, 0.70), (0.03, 0.002, 0.10), soft=0.0)


def seat(k):
    """The seat on its post off the spine: an outer sleeve with a row of holes, the inner post up to the seat's plate,
    the pop pin's knob on the sleeve's back."""
    bw = 0.076
    zs = 0.58                                           # the sleeve's top
    wt = (bw - 0.058) / 2
    for sx, sy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (sx * (bw - wt) / 2, SEAT_Y + sy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP),
              soft=0.002)
    for i in range(7):
        k.cyl("hole", (0, SEAT_Y + bw / 2 + 0.0005, 0.25 + i * 0.04), 0.007, 0.001, axis="y", seg=14)
    zt = SEAT_TOP - SEAT[2] - 0.012
    k.bar("frame", (0, SEAT_Y, zs - 0.08), (0, SEAT_Y, zt), 0.058, 0.058, up=(0, 1, 0))
    k.tube("steel", (0, SEAT_Y + 0.02, zs - 0.03), (0, SEAT_Y + bw / 2 + 0.035, zs - 0.03), 0.007)
    k.cyl("plastic", (0, SEAT_Y + bw / 2 + 0.05, zs - 0.03), 0.02, 0.03, axis="y", seg=24, soft=0.006)
    k.box("frame", (0, SEAT_Y, zt + 0.006), (0.26, 0.22, 0.012), soft=0.002)
    c = (0.0, SEAT_Y, SEAT_TOP - SEAT[2] / 2)
    k.shaped_pad("pad", [(-SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, SEAT[1] / 2),
                         (-SEAT[0] / 2, SEAT[1] / 2)], c, (0, 0, 1), (1, 0, 0), SEAT[2], r=0.06, cushion=0.03)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """On the seat facing -y, the chest on the pad, the feet on the foot plates, the hands on the inner grips at rest
    (the start of the row), for a short, a middle and a tall user (the seat adjusts on its post; shown at one height)."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        s = H / 1.78
        trunk = 8                                       # leaning a little into the pad
        hip = (0.0, PAD_C[0] + PAD[2] / 2 + 0.12 * s + math.sin(math.radians(trunk)) * 0.20 * H, SEAT_TOP + 0.045 * s)
        ball = (0.0, col_at(FOOT_BAR) - 0.06, FOOT_BAR + 0.06)
        shank, thigh = legs(H, ball, hip, sole=40)
        arm, forearm, arm_out = reach(H, hip, trunk)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=40, shank=shank, thigh=thigh, trunk=trunk, neck=0,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def legs(H, ball, hip, sole):
    """The shank and thigh angles (body.figure's) from the foot on its plate up to the hip on the seat."""
    r = math.radians
    Lf = 0.152 * H
    ay = ball[1] + 0.48 * Lf * math.cos(r(sole)) - 0.039 * H * math.sin(r(sole))   # the ankle (forward is -y)
    az = ball[2] - 0.48 * Lf * math.sin(r(sole)) + 0.039 * H * math.cos(r(sole))
    best = min(((math.dist((ay - math.sin(r(a)) * 0.246 * H - math.sin(r(b)) * 0.245 * H,
                            az + math.cos(r(a)) * 0.246 * H + math.cos(r(b)) * 0.245 * H), (hip[1], hip[2])), a, b)
                for a in range(-60, 61) for b in range(-150, -20)))
    return best[1], best[2]


def reach(H, hip, trunk):
    """The arm angles that put the left hand on the left inner grip's middle, the elbow below the hand."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    hd = LP["hand"]
    tx, ty, tz = GRIP_IN, hd[0] + 0.07, hd[1] + 0.04      # the inner grip's rubber, its middle

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        n = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / n * 0.186 * H, sy + ay / n * 0.186 * H, sz + az / n * 0.186 * H
        g = 0.191 * H
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ez > hz + 0.05 else 0.0)

    best = min(((miss(a, f, o), a, f, o) for a in range(0, 181, 5) for f in range(0, 181, 5) for o in range(-30, 61, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    assert best[0] < 0.03, f"the grips are out of reach ({best[0]:.3f} m short)"
    return best[1], best[2], best[3]

"""Hammer Strength Plate-Loaded Iso-Lateral Bench Press (IL-BP): a seated press, each arm its own lever pivoting on a yoke
above and behind the user's head, pressed forward from beside the chest. Claude's pick (Roman, 2026-10-23: a free hand,
Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_14 an empty true side view, ref_10 an empty true front view, ref_12 /
ref_13 the three-quarters, ref_02-ref_09 the press in use), held to Life Fitness's 122 x 170 x 183 cm (L x W x H, the
width over the weight horns), 6 storage horns. Side-view numbers off ref_14's near side at ~410 px/m, front-view numbers
off ref_10 at ~339 px/m. The photos are the Platinum frame; the shop's variant (and its main photo, ref_01) is Charcoal
with black upholstery, as the other Hammer Strength pieces.
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
    "detail_pivot": ((1.25, 0.95, 2.05), (0.49, 0.18, 1.68), 50),          # the yoke posts, the hub, the axle
    "detail_grip": ((0.95, -1.15, 1.25), (0.38, -0.12, 0.95), 50),        # the drop arm and its grip, the horn above
    "detail_seat": ((0.75, -1.25, 0.65), (0.0, -0.19, 0.35), 50),         # the seat's post, its pop pin
}

# ---- the user (rule 2b): seated facing -y, the back on the pad, the hands beside the chest on the grips at the start
SEAT_TOP = 0.53                  # the seat's top (front view: 0.46-0.53 m)
SEAT_Y = -0.19                   # its centre (side view: d 0.20-0.53 from the front foot)
SEAT = (0.43, 0.32, 0.08)        # width, depth, thickness
BACK_BOT, BACK_TOP = (-0.04, 0.60), (0.11, 1.30)  # the back pad's face, bottom and top (y, z): leaning back ~12 deg
BACK = (0.24, 0.08)              # its width, thickness
GRIP_Y, GRIP_Z = -0.17, 0.90     # the grips at the drop arms' feet (side view: the arm at d 0.39, its foot z 0.83-0.90)
GRIP_IN = 0.24                   # the grips' inner ends (x): just outside the user's shoulders
# ---- the levers, from the side view: the pivot just above and behind the head, the arm forward and down to the horn
X_LEV = 0.49                     # each lever's plane (front view: between the yoke posts)
PIV = (0.18, 1.70)               # the pivot (y, z)
FRONT = (-0.47, 1.40)            # the arm's front end, where the weight horn is (side view: d 0.07, z 1.40)
LEV = (0.05, 0.10)               # the lever section: across (x) x tall (2 x 4 in)
HORN_X = 0.85                    # the weight horns' tips: Life Fitness's 170 cm width is over them
HORN_S = 0.78                    # the storage horns' tips (front view: a little short of the levers')
# ---- the frame
X_SW, X_UP = 0.56, 0.30          # the outer curved members (the swoops, carrying the storage horns) and the rear uprights
POSTS = (0.38, 0.60)             # the yoke posts each side (x)
POST = (0.04, 0.09)              # a post: across (x) x deep (y)
Z_TOP = 1.56                     # the top cross bar (centre), the posts stand on it
Y_TOP = 0.18
Z_POST = 1.83                    # the posts' tops: the highest point
Z_MID, Z_LOW = 1.09, 0.66        # the cross bars between the rear uprights (front view)
BOX = (0.076, 0.05)              # base section (3 x 2 in)
SQ = 0.076                       # swoops, uprights, cross bars (3 x 3 in)
FOOT_H = 0.022
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
Y0, Y1 = -0.56, 0.50             # the side rails' ends (front, rear)
BY_F, BY_R = -0.42, 0.40         # the front and rear cross bars
# the swoop (ref_14, its near side): up and back off the rail, a tight bend, up and forward into the straight brace that
# runs from below the bend's height up to the top cross bar (its lower end stands free, the warning label on it)
SWOOP = [(-0.17, RAIL_TOP), (0.22, 0.78), (0.20, 1.02), (0.0, 1.22)]    # (y, z), its end cut on the brace
BRACE = ((-0.06, 1.00), (Y_TOP, Z_TOP - SQ / 2))
HORNS_Z = (0.26, 0.62, 1.07)     # the storage horns (the 5, 25 and 45 lb ones, side view)


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def swoop_at(z):
    """(y, z) on the swoop's straight runs at height z."""
    for (y0, z0), (y1, z1) in zip(SWOOP, SWOOP[1:]):
        if z0 <= z <= z1 or z1 <= z <= z0:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    return SWOOP[-1][0]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    for s in (1, -1):
        tower(k, s)
        lever(k, s)
    top(k)
    seat(k)
    back(k)


def foot(k, x, y):
    """A rubber foot under a rail's end: a block the rail sits on, a flanged pad with an anchor hole each side."""
    bw = BOX[0]
    k.box("rubber", (x, y, 0.008 + (FOOT_H - 0.008) / 2), (bw + 0.004, 0.075, FOOT_H - 0.008), soft=0.003)
    k.box("rubber", (x, y, 0.004), (bw + 0.10, 0.065, 0.008), soft=0.003)
    for d in (-1, 1):
        k.cyl("hole", (x + d * (bw / 2 + 0.026), y, 0.0082), 0.0075, 0.001, seg=16)


def rail_bolt(k, c, axis):
    ax = axis[-1]; sg = 1 if axis[0] == "+" else -1
    o = {"x": (sg, 0, 0), "y": (0, sg, 0)}[ax]
    k.cyl("plastic", tuple(c[i] + o[i] * 0.003 for i in range(3)), 0.017, 0.006, axis=ax, seg=28, soft=0.0015)
    k.bolt(tuple(c[i] + o[i] * 0.006 for i in range(3)), axis, size=0.012)


def base(k):
    """A side rail under each tower past both cross bars to its feet, the front and rear cross bars teed between them,
    the centre rail between the cross bars carrying the seat's post."""
    bw, bh = BOX
    Y = (0, 1, 0)
    for s in (1, -1):
        k.bar("frame", (s * X_SW, Y0, RAIL_Z), (s * X_SW, Y1, RAIL_Z), bw, bh)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (s * X_SW, ye + d * 0.004, RAIL_Z), (bw + 0.004, 0.008, bh + 0.004), soft=0.002)
            foot(k, s * X_SW, ye - d * 0.036)
        for by in (Y0 + 0.10, 0.05, Y1 - 0.12):
            rail_bolt(k, (s * (X_SW + bw / 2), by, RAIL_Z), "+x" if s > 0 else "-x")
    xi = X_SW - bw / 2
    for y_ in (BY_F, BY_R):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), bw, bh,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (0, BY_F + bw / 2, RAIL_Z), (0, BY_R - bw / 2, RAIL_Z), bw, bh,
          cut0=((0, BY_F + bw / 2, 0), Y), cut1=((0, BY_R - bw / 2, 0), Y), weld=True)
    k.box("warn", (0.20, BY_F - bw / 2 - 0.001, RAIL_Z), (0.04, 0.002, 0.035), soft=0.0)


def tower(k, s):
    """One side: the swoop up from the rail's front half curving back to the top cross bar (the storage horns on its
    outer face), the rear upright from the rear cross bar leaning in to it, the cross bars between the uprights."""
    Z = (0, 0, 1)
    x = s * X_SW
    (b0y, b0z), (b1y, b1z) = BRACE
    bl = math.hypot(b1y - b0y, b1z - b0z)
    bn = (0.0, -(b1z - b0z) / bl, (b1y - b0y) / bl)        # across the brace, facing forward and up: the swoop's end cut
    k.sweep("frame", [(x, y, z) for y, z in SWOOP], k.rect(SQ, SQ, 0.008), bend=0.10, up=(1, 0, 0),
            cut0=((0, 0, RAIL_TOP), Z), cut1=((x, b0y - bn[1] * SQ / 2, b0z - bn[2] * SQ / 2), bn), weld=True)
    k.bar("frame", (x, b0y, b0z), (x, b1y, b1z), SQ, SQ, up=(1, 0, 0), cut1=((0, 0, b1z), Z), weld=True)
    k.sweep("plastic", [(x, b0y, b0z), (x, b0y - 0.008 * (b1y - b0y) / math.hypot(b1y - b0y, b1z - b0z),
                                         b0z - 0.008 * (b1z - b0z) / math.hypot(b1y - b0y, b1z - b0z))],
            k.rect(SQ + 0.004, SQ + 0.004, 0.003), up=(1, 0, 0), soft=0.002)              # its end cap
    for zh in HORNS_Z:                                  # the storage horns: a collar on the outer face, the sleeve, a cap
        yh = swoop_at(zh)
        xf = x + s * SQ / 2
        k.cyl("frame", (xf + s * 0.01, yh, zh), 0.045, 0.02, axis="x", seg=32, soft=0.004)
        k.tube("steel", (xf + s * 0.018, yh, zh), (s * HORN_S, yh, zh), 0.025, seg=32)
        k.cyl("plastic", (s * (HORN_S + 0.006), yh, zh), 0.029, 0.012, axis="x", seg=32, soft=0.004)
    (b0y, b0z), (b1y, b1z) = BRACE
    bz = lambda f: (b0y + (b1y - b0y) * f, b0z + (b1z - b0z) * f)
    wy, wz = bz(0.06)
    k.box("warn", (x + s * (SQ / 2 + 0.001), wy, wz), (0.002, 0.04, 0.04), soft=0.0)
    ly, lz = bz(0.72)
    k.text("label", "HAMMER STRENGTH", (x + s * (SQ / 2 + 0.001), ly, lz), 0.03,
           rz=math.pi / 2 * s, spin=math.atan2(b1z - b0z, b1y - b0y), depth=0.0006)
    xu = s * X_UP
    k.bar("frame", (xu, BY_R, RAIL_TOP), (xu, Y_TOP, Z_TOP - SQ / 2), SQ, SQ, up=(1, 0, 0),
          cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, Z_TOP - SQ / 2), Z), weld=True)


def upright_y(z):
    return BY_R + (Y_TOP - BY_R) * (z - RAIL_TOP) / (Z_TOP - SQ / 2 - RAIL_TOP)


def top(k):
    """The top cross bar over both towers, the yoke posts on it, the axles through them; the cross bars between the rear
    uprights lower down."""
    Z = (0, 0, 1)
    xe = POSTS[1] + POST[0] / 2
    k.bar("frame", (-xe, Y_TOP, Z_TOP), (xe, Y_TOP, Z_TOP), SQ, SQ)
    for s in (1, -1):
        for xp in POSTS:
            k.bar("frame", (s * xp, Y_TOP, Z_TOP + SQ / 2), (s * xp, Y_TOP, Z_POST), POST[0], POST[1], up=(0, 1, 0),
                  cut0=((0, 0, Z_TOP + SQ / 2), Z), weld=True)
            k.box("plastic", (s * xp, Y_TOP, Z_POST + 0.006), (POST[0] + 0.004, POST[1] + 0.004, 0.012), soft=0.003)
            k.bolt((s * (xp + POST[0] / 2 * (1 if xp == POSTS[1] else -1)), Y_TOP, Z_POST - 0.05),
                   ("+x" if (s > 0) == (xp == POSTS[1]) else "-x"), size=0.016)
        a0, a1 = s * (POSTS[0] - POST[0] / 2 - 0.012), s * (POSTS[1] + POST[0] / 2 + 0.012)
        k.tube("steel", (a0, PIV[0], PIV[1]), (a1, PIV[0], PIV[1]), 0.019)
        for x_, d in ((a0, -s), (a1, s)):
            k.bolt((x_ - d * 0.012, PIV[0], PIV[1]), ("+x" if d > 0 else "-x"), size=0.03)
        k.box("frame", (s * (POSTS[1] + POST[0] / 2 + 0.001), Y_TOP, Z_TOP + 0.13), (0.002, 0.06, 0.12), soft=0.0)
    xi = X_UP - SQ / 2
    for z in (Z_MID, Z_LOW):
        k.bar("frame", (-xi, upright_y(z), z), (xi, upright_y(z), z), SQ, 0.05,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)


def lever(k, s):
    """One lever: its hub on the axle between the yoke posts, the 2 x 4 arm forward and down to the weight horn, the
    drop arm hanging from its middle to the grip beside the chest."""
    x = s * X_LEV
    P, F = (x, PIV[0], PIV[1]), (x, FRONT[0], FRONT[1])
    L = math.dist(P, F)
    u = tuple((F[i] - P[i]) / L for i in range(3))                  # down the arm
    n = (0.0, -u[2], u[1]) if u[2] < 0 else (0.0, u[2], -u[1])      # the arm's up (its 4 in face's normal, upward)
    n = n if n[2] > 0 else tuple(-c for c in n)
    hx0, hx1 = s * (POSTS[0] + POST[0] / 2), s * (POSTS[1] - POST[0] / 2)
    k.tube("lever", (hx0, P[1], P[2]), (hx1, P[1], P[2]), 0.05, seg=36)                 # the hub
    root = tuple(P[i] + u[i] * 0.044 for i in range(3))            # welded on the hub's face
    k.sweep("lever", [root, F], k.rect(LEV[0], LEV[1], 0.006), up=n, soft=0.003)
    k.sweep("plastic", [F, tuple(F[i] + u[i] * 0.012 for i in range(3))], k.rect(LEV[0] + 0.004, LEV[1] + 0.004, 0.004),
            up=n, soft=0.002)                                                                     # the end cap
    for d in (0.18, 0.40):
        q = tuple(P[i] + u[i] * d for i in range(3))
        k.bolt((q[0] + s * LEV[0] / 2, q[1], q[2]), "+x" if s > 0 else "-x", size=0.012, nut=LEV[0])
    # the weight horn at the arm's front end: a collar on the lever's outer face, the sleeve out, its cap
    hf = tuple(F[i] - u[i] * 0.06 for i in range(3))
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, hf[1], hf[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, hf[1], hf[2]), (s * HORN_X, hf[1], hf[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), hf[1], hf[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the drop arm: from the arm's underside at the grip's y straight down, the grip in from its inner face
    t = (GRIP_Y - P[1]) / (F[1] - P[1])
    M = lerp(P, F, t)
    under = tuple(M[i] - n[i] * LEV[1] / 2 for i in range(3))
    k.bar("lever", (x, GRIP_Y, under[2] + 0.02), (x, GRIP_Y, GRIP_Z - 0.06), 0.05, 0.08, up=(0, 1, 0),
          cut0=(under, n), weld=True)
    k.box("plastic", (x, GRIP_Y, GRIP_Z - 0.066), (0.054, 0.084, 0.012), soft=0.002)
    xin = x - s * 0.025
    k.box("lever", (xin - s * 0.02, GRIP_Y, GRIP_Z), (0.04, 0.07, 0.07), soft=0.005)          # the grip's boss
    g0, g1 = (xin - s * 0.04, GRIP_Y, GRIP_Z), (s * GRIP_IN, GRIP_Y - 0.02, GRIP_Z + 0.07)   # rising inward (front view)
    k.tube("lever", g0, g1, 0.016, seg=20)
    k.tube("rubber", lerp(g0, g1, 0.25), g1, 0.02, soft=0.003)
    k.cyl("plastic", (g1[0] - s * 0.005, g1[1], g1[2]), 0.021, 0.01, axis="x", seg=20, soft=0.002)
    k.box("warn", (x + s * (LEV[0] / 2 + 0.001), GRIP_Y, GRIP_Z + 0.20), (0.002, 0.045, 0.04), soft=0.0)
    # the brace (ref_14): from the arm's underside near its front end back and down into the drop arm's front face
    q = tuple(P[i] + u[i] * (L - 0.16) - n[i] * LEV[1] / 2 for i in range(3))
    dz = under[2] - 0.28
    k.bar("lever", q, (x, GRIP_Y - 0.03, dz), 0.04, 0.05, up=(1, 0, 0),
          cut0=(q, n), cut1=((x, GRIP_Y - 0.04, dz), (0, 1, 0)), weld=True)


def seat(k):
    """The seat on its post: an outer sleeve on the centre rail with a row of holes, the inner post up to the seat's
    bracket, the pop pin's knob on the sleeve's front."""
    bw = 0.076
    zs = 0.36                                           # the sleeve's top
    wt = (bw - 0.058) / 2                               # the sleeve: four walls round the inner post
    for sx, sy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (sx * (bw - wt) / 2, SEAT_Y + sy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP), soft=0.002)
    for i in range(6):
        k.cyl("hole", (0, SEAT_Y - bw / 2 - 0.0005, 0.13 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = SEAT_TOP - SEAT[2] - 0.012
    k.bar("frame", (0, SEAT_Y, zs - 0.06), (0, SEAT_Y, zt), 0.058, 0.058, up=(0, 1, 0))           # the inner post
    k.tube("steel", (0, SEAT_Y - 0.02, zs - 0.03), (0, SEAT_Y - bw / 2 - 0.035, zs - 0.03), 0.007)   # into the post
    k.cyl("plastic", (0, SEAT_Y - bw / 2 - 0.05, zs - 0.03), 0.02, 0.03, axis="y", seg=24, soft=0.006)  # the pop pin
    k.box("frame", (0, SEAT_Y, zt + 0.006), (0.30, 0.24, 0.012), soft=0.002)                       # the seat's plate
    c = (0.0, SEAT_Y, SEAT_TOP - SEAT[2] / 2)
    k.shaped_pad("pad", [(-SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, SEAT[1] / 2),
                         (-SEAT[0] / 2, SEAT[1] / 2)], c, (0, 0, 1), (1, 0, 0), SEAT[2], r=0.06, cushion=0.03)


def back(k):
    """The back pad leaning back, on its spine plate, bracketed back to the two cross bars between the rear uprights."""
    (y0, z0), (y1, z1) = BACK_BOT, BACK_TOP
    L = math.hypot(y1 - y0, z1 - z0)
    up = (0.0, (y1 - y0) / L, (z1 - z0) / L)
    face = (0.0, -up[2], up[1])                         # toward the user (-y, a little up)
    mid = ((y0 + y1) / 2, (z0 + z1) / 2)
    c = (0.0, mid[0] - face[1] * BACK[1] / 2, mid[1] - face[2] * BACK[1] / 2)
    k.shaped_pad("pad", [(-BACK[0] / 2, -L / 2), (BACK[0] / 2, -L / 2), (BACK[0] / 2, L / 2), (-BACK[0] / 2, L / 2)],
                 c, face, (1, 0, 0), BACK[1], r=0.05, cushion=0.03)
    sp = tuple(c[i] - face[i] * (BACK[1] / 2 + 0.02) for i in range(3))
    s0, s1 = tuple(sp[i] - up[i] * L * 0.42 for i in range(3)), tuple(sp[i] + up[i] * L * 0.42 for i in range(3))
    k.bar("frame", s0, s1, 0.12, 0.04, up=face)                                                    # the spine plate
    for z in (Z_MID, Z_LOW):                            # brackets from the spine back to the cross bars' front faces
        f = (z - s0[2]) / (s1[2] - s0[2])
        q = lerp(s0, s1, f)
        yb = upright_y(z) - SQ / 2
        k.bar("frame", (0, q[1] + 0.02, z), (0, yb, z), 0.06, 0.05, up=(0, 0, 1),
              cut1=((0, yb, 0), (0, 1, 0)), weld=True)
    # the seat's post stands under the seat; the back pad's lower end meets the seat's rear edge


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Seated facing -y, the back on the pad, the hands on the grips beside the chest (the start of the press), the feet
    flat on the floor in front; for a short, a middle and a tall user (the seat adjusts on its post; shown at one
    height)."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        hip = (0.0, SEAT_Y + 0.07, SEAT_TOP + 0.045 * H / 1.78)
        lt, ls = 0.245 * H, 0.246 * H
        kz = ls + 0.039 * H                             # the knee over the ankle, the foot flat on the floor
        a = -math.degrees(math.acos(max(-1.0, min(1.0, (hip[2] - kz) / lt))))
        ky = hip[1] - lt * math.sin(math.radians(-a))
        ball = (0.0, ky - 0.073 * H, 0.0)
        arm, forearm, arm_out = reach(H, hip, -12)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=0, thigh=a, trunk=-12, neck=4,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles (body.figure's) that put the left hand's palm on the left grip's middle, the elbow back and out
    (the press's start): a coarse search, then a fine one round the best."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H                       # the shoulders (facing -y: forward is -y)
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    tx, ty, tz = (X_LEV + GRIP_IN) / 2 - 0.04, GRIP_Y - 0.01, GRIP_Z + 0.035

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        n = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / n * 0.186 * H, sy + ay / n * 0.186 * H, sz + az / n * 0.186 * H
        g = 0.191 * H                                                   # the wrist and half the hand
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ey < sy else 0.0)   # keep the elbow back

    best = min(((miss(a, f, o), a, f, o) for a in range(90, 271, 5) for f in range(-60, 181, 5) for o in range(0, 81, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    assert best[0] < 0.02, f"the grips are out of reach ({best[0]:.3f} m short)"
    return best[1], best[2], best[3]

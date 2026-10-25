"""Hammer Strength Plate-Loaded Iso-Lateral Incline Press (IL-IP): a seated press up and forward, each arm its own lever
hanging from a pivot high above and behind the head, its grip at the lever's foot beside the shoulder. Claude's pick
(Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from the shop's gallery (refs/: ref_05 / ref_06 the side in use, ref_09 / ref_10 empty true fronts, ref_12 /
ref_13 the three-quarters, ref_01 the maker's render in Charcoal), held to Life Fitness's 117 x 140 x 191 cm (L x W x
H, the width over the weight horns), 6 storage horns. Side-view numbers off ref_05 at ~458 px/m, front-view numbers off
ref_09 at ~382 px/m. The photos are the Platinum frame; the shop's variant (ref_01) is Charcoal with black upholstery.
The same family as the Iso-Lateral Bench Press (its S-shaped horn member and brace, its levers' hubs between paired
pivot plates); here the rear uprights stand straight up, the front feet splay out, the levers hang steeply as a V.
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
    "detail_pivot": ((1.20, 1.00, 2.20), (0.43, 0.29, 1.72), 50),          # the pivot plates, the hub, the axle
    "detail_grip": ((0.95, -1.20, 1.35), (0.36, -0.39, 1.08), 50),        # the lever's foot and its grip, the horn above
    "detail_seat": ((0.75, -1.25, 0.60), (0.0, -0.18, 0.32), 50),         # the seat's post, its pop pin
}

# ---- the user: seated facing -y, the back on the reclined pad, the hands on the grips beside the shoulders
SEAT_TOP = 0.47                  # the seat's top (side view)
SEAT_Y = -0.19                   # its centre
SEAT = (0.43, 0.30, 0.08)        # width, depth, thickness
BACK_BOT, BACK_TOP = (-0.05, 0.54), (0.17, 1.26)   # the back pad's face, bottom and top (y, z): reclined ~17 deg
BACK = (0.26, 0.08)              # its width, thickness
# ---- the levers, from the side view: the pivot high behind the head, the lever down and forward to the grip
X_LEV = 0.47                     # each lever's plane (front view)
PIV = (0.29, 1.76)               # the pivot (y, z)
HORN_P = (-0.29, 1.39)           # the lever's bend, where the weight horn is (side view: the plate's centre)
FOOT = (-0.39, 1.06)             # the lever's foot, the grip there (side view)
LEV = (0.05, 0.10)               # the lever section: across (x) x tall (2 x 4 in)
GRIP_IN = 0.24                   # the grips' inner ends (x, front view)
HORN_X = 0.70                    # the weight horns' tips: Life Fitness's 140 cm width is over them
HORN_S = 0.66                    # the storage horns' tips
# ---- the frame
X_UP = 0.37                      # the rear uprights and the horn members (front view: the verticals)
Y_UP = 0.40                      # the rear uprights (side view: straight up)
POSTS = (0.30, 0.58)             # the pivot plates each side (x), the lever's hub between them
PLATE = (0.012, 0.22)            # a pivot plate: thick (x) x deep (y), from the pivot back over the cross bar
Z_TOP = 1.46                     # the top cross bar (centre), the pivot plates stand on it
Y_TOP = Y_UP                     # on the rear uprights
Y_PL = (PIV[0] - 0.07 + Y_TOP + 0.038) / 2     # the plates' centre (y): from round the pivot back to the bar's rear face
Z_PL = 1.91                      # the plates' tops: the highest point
Z_MID, Z_LOW = 1.02, 0.62        # the cross bars between the rear uprights (front view: the back pad's brackets)
BOX = (0.076, 0.05)              # base section (3 x 2 in)
SQ = 0.076                       # uprights, horn members, cross bars (3 x 3 in)
FOOT_H = 0.022
RAIL_Z = FOOT_H + BOX[1] / 2
RAIL_TOP = FOOT_H + BOX[1]
Y0, Y1 = -0.40, 0.58             # the side rails' ends (front, rear)
Y_FF, X_FF = -0.57, 0.55         # the splayed front feet (ref_09 / ref_12: forward and out from the rails' fronts)
BY_F, BY_R = -0.30, 0.47         # the front and rear cross bars
# the horn member (ref_05, its near side): up and back off the rail, a tight bend, up and forward into the straight brace
# that runs on up to the top cross bar (its lower end stands free, the warning label on it)
SWOOP = [(-0.06, RAIL_TOP), (0.25, 0.82), (0.24, 1.00), (0.0, 1.27)]   # (y, z), its end cut on the brace
BRACE = ((-0.05, 1.18), (Y_UP - SQ / 2, Z_TOP - SQ / 2 - 0.04))   # its top on the upright's front face
HORNS = ((Y_UP, 1.12), (Y_UP, 0.57), (None, 0.22))   # the storage horns: two on each upright, one on the horn member


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(len(a)))


def swoop_at(z):
    """y on the horn member's straight runs at height z (its lower run)."""
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


def foot(k, x, y, rz=0.0):
    """A rubber foot under a rail's end: a block the rail sits on, a flanged pad with an anchor hole each side."""
    bw = BOX[0]
    c, s_ = math.cos(rz), math.sin(rz)
    k.box("rubber", (x, y, 0.008 + (FOOT_H - 0.008) / 2), (bw + 0.004, 0.075, FOOT_H - 0.008), soft=0.003, rz=rz)
    k.box("rubber", (x, y, 0.004), (bw + 0.10, 0.065, 0.008), soft=0.003, rz=rz)
    for d in (-1, 1):
        o = d * (bw / 2 + 0.026)
        k.cyl("hole", (x + o * c, y + o * s_, 0.0082), 0.0075, 0.001, seg=16)


def rail_bolt(k, c, axis):
    ax = axis[-1]; sg = 1 if axis[0] == "+" else -1
    o = {"x": (sg, 0, 0), "y": (0, sg, 0)}[ax]
    k.cyl("plastic", tuple(c[i] + o[i] * 0.003 for i in range(3)), 0.017, 0.006, axis=ax, seg=28, soft=0.0015)
    k.bolt(tuple(c[i] + o[i] * 0.006 for i in range(3)), axis, size=0.012)


def base(k):
    """A side rail under each upright from the front cross bar to its rear foot, a splayed front leg forward and out
    from the rail's front to its foot, the front and rear cross bars between the rails, the centre rail carrying the
    seat's post."""
    bw, bh = BOX
    Y = (0, 1, 0)
    for s in (1, -1):
        x = s * X_UP
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), bw, bh)
        k.box("plastic", (x, Y1 + 0.004, RAIL_Z), (bw + 0.004, 0.008, bh + 0.004), soft=0.002)
        foot(k, x, Y1 - 0.036)
        ff = (s * X_FF, Y_FF, RAIL_Z)
        k.sweep("frame", [(x, Y0 + bw / 2, RAIL_Z), (x, Y0 - 0.02, RAIL_Z), ff], k.rect(bw, bh, 0.006), bend=0.08,
                up=(0, 0, 1))                                                           # the splayed front leg
        rz = math.atan2(ff[1] - (Y0 - 0.02), ff[0] - x) - math.pi / 2
        foot(k, ff[0] + 0.03 * math.sin(rz) * -1, ff[1] + 0.03 * math.cos(rz), rz=rz)
        for by in (0.05, Y1 - 0.12):
            rail_bolt(k, (s * (X_UP + bw / 2), by, RAIL_Z), "+x" if s > 0 else "-x")
    xi = X_UP - bw / 2
    for y_ in (BY_F, BY_R):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), bw, bh,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (0, BY_F + bw / 2, RAIL_Z), (0, BY_R - bw / 2, RAIL_Z), bw, bh,
          cut0=((0, BY_F + bw / 2, 0), Y), cut1=((0, BY_R - bw / 2, 0), Y), weld=True)
    k.box("warn", (0.20, BY_F - bw / 2 - 0.001, RAIL_Z), (0.04, 0.002, 0.035), soft=0.0)


def tower(k, s):
    """One side: the rear upright straight up from the rail to the top cross bar, the horn member up off the rail's
    front half (an S) cut into the brace running up to the top cross bar, the storage horns on their outer faces."""
    Z = (0, 0, 1)
    x = s * X_UP
    (b0y, b0z), (b1y, b1z) = BRACE
    bl = math.hypot(b1y - b0y, b1z - b0z)
    bn = (0.0, -(b1z - b0z) / bl, (b1y - b0y) / bl)        # across the brace, facing forward and up: the swoop's end cut
    k.bar("frame", (x, Y_UP, RAIL_TOP), (x, Y_UP, Z_TOP - SQ / 2), SQ, SQ, up=(1, 0, 0),
          cut0=((0, 0, RAIL_TOP), Z), cut1=((0, 0, Z_TOP - SQ / 2), Z), weld=True)
    k.sweep("frame", [(x, y, z) for y, z in SWOOP], k.rect(SQ, SQ, 0.008), bend=0.10, up=(1, 0, 0),
            cut0=((0, 0, RAIL_TOP), Z), cut1=((x, b0y - bn[1] * SQ / 2, b0z - bn[2] * SQ / 2), bn), weld=True)
    k.bar("frame", (x, b0y, b0z), (x, b1y, b1z), SQ, SQ, up=(1, 0, 0), cut1=((0, b1y, 0), (0, 1, 0)), weld=True)
    ub = ((b1y - b0y) / bl, (b1z - b0z) / bl)
    k.sweep("plastic", [(x, b0y, b0z), (x, b0y - 0.008 * ub[0], b0z - 0.008 * ub[1])],
            k.rect(SQ + 0.004, SQ + 0.004, 0.003), up=(1, 0, 0), soft=0.002)              # its end cap
    for yh, zh in HORNS:                                # the storage horns: a collar on the outer face, the sleeve, a cap
        yh = swoop_at(zh) if yh is None else yh
        xf = x + s * SQ / 2
        k.cyl("frame", (xf + s * 0.01, yh, zh), 0.045, 0.02, axis="x", seg=32, soft=0.004)
        k.tube("steel", (xf + s * 0.018, yh, zh), (s * HORN_S, yh, zh), 0.025, seg=32)
        k.cyl("plastic", (s * (HORN_S + 0.006), yh, zh), 0.029, 0.012, axis="x", seg=32, soft=0.004)
    bz = lambda f: (b0y + (b1y - b0y) * f, b0z + (b1z - b0z) * f)
    wy, wz = bz(0.10)
    k.box("warn", (x + s * (SQ / 2 + 0.001), wy, wz), (0.002, 0.04, 0.04), soft=0.0)
    ly, lz = bz(0.62)
    k.text("label", "HAMMER STRENGTH", (x + s * (SQ / 2 + 0.001), ly, lz), 0.026,
           rz=math.pi / 2 * s, spin=math.atan2(b1z - b0z, b1y - b0y), depth=0.0006)


def top(k):
    """The top cross bar over both sides, the pivot plates standing on it in pairs, the axles through them; the cross
    bars between the rear uprights lower down."""
    xe = POSTS[1] + PLATE[0] / 2
    k.bar("frame", (-xe, Y_TOP, Z_TOP), (xe, Y_TOP, Z_TOP), SQ, SQ)
    for s in (1, -1):
        for xp in POSTS:
            k.box("frame", (s * xp, Y_PL, (Z_TOP + SQ / 2 - 0.004 + Z_PL) / 2), (PLATE[0], PLATE[1], Z_PL - Z_TOP - SQ / 2 + 0.004),
                  soft=0.003)
            for dz in (0.06, -0.06):
                k.bolt((s * (xp + (PLATE[0] / 2 if xp == POSTS[1] else -PLATE[0] / 2)), PIV[0] + 0.04, Z_PL - 0.06 + dz - 0.06),
                       ("+x" if (s > 0) == (xp == POSTS[1]) else "-x"), size=0.014)
        a0, a1 = s * (POSTS[0] - PLATE[0] / 2 - 0.012), s * (POSTS[1] + PLATE[0] / 2 + 0.012)
        k.tube("steel", (a0, PIV[0], PIV[1]), (a1, PIV[0], PIV[1]), 0.019)
        for x_, d in ((a0, -s), (a1, s)):
            k.bolt((x_ - d * 0.012, PIV[0], PIV[1]), ("+x" if d > 0 else "-x"), size=0.03)
    xi = X_UP - SQ / 2
    for z in (Z_MID, Z_LOW):
        k.bar("frame", (-xi, Y_UP, z), (xi, Y_UP, z), SQ, 0.05,
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)


def lever(k, s):
    """One lever: its hub on the axle between the pivot plates, the 2 x 4 arm forward and down to its bend (the weight
    horn there), on down to its foot, a chord strut from the hub to the foot (the V of the front view), the grip in
    from the foot."""
    x = s * X_LEV
    P, B, F = (x, PIV[0], PIV[1]), (x, HORN_P[0], HORN_P[1]), (x, FOOT[0], FOOT[1])
    hx0, hx1 = s * (POSTS[0] + PLATE[0] / 2), s * (POSTS[1] - PLATE[0] / 2)
    k.tube("lever", (hx0, P[1], P[2]), (hx1, P[1], P[2]), 0.05, seg=36)                 # the hub
    u1 = tuple((B[i] - P[i]) / math.dist(P, B) for i in range(3))
    root = tuple(P[i] + u1[i] * 0.044 for i in range(3))            # welded on the hub's face
    k.sweep("lever", [root, B, F], k.rect(LEV[1], LEV[0], 0.006), bend=0.06, up=(1, 0, 0), soft=0.003)
    uf = tuple((F[i] - B[i]) / math.dist(B, F) for i in range(3))
    k.sweep("plastic", [F, tuple(F[i] + uf[i] * 0.012 for i in range(3))], k.rect(LEV[1] + 0.004, LEV[0] + 0.004, 0.004),
            up=(1, 0, 0), soft=0.002)                                                             # the end cap
    uc = tuple((F[i] - P[i]) / math.dist(P, F) for i in range(3))
    xs = x - s * (LEV[0] / 2 + 0.02)                    # beside the lever's inner face (the front view's V)
    c0 = (xs, P[1] + uc[1] * 0.05, P[2] + uc[2] * 0.05)
    c1 = (xs, F[1] - uc[1] * 0.16, F[2] - uc[2] * 0.16)
    k.bar("lever", c0, c1, 0.06, 0.04, up=(1, 0, 0))                                             # the chord strut
    for d in (0.18, 0.42):
        q = tuple(P[i] + u1[i] * d for i in range(3))
        k.bolt((q[0] + s * LEV[0] / 2, q[1], q[2]), "+x" if s > 0 else "-x", size=0.012, nut=LEV[0])
    # the weight horn at the bend: a collar on the lever's outer face, the sleeve out, its cap
    xf = x + s * LEV[0] / 2
    k.cyl("lever", (xf + s * 0.01, B[1], B[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.018, B[1], B[2]), (s * HORN_X, B[1], B[2]), 0.025, seg=32)
    k.cyl("lever", (s * (HORN_X + 0.008), B[1], B[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the grip: in from the foot's inner face, rising a little (front view), rubber over its inner two thirds
    g0 = (x - s * LEV[0] / 2, F[1] + 0.03, F[2] + 0.02)
    g1 = (s * GRIP_IN, F[1] + 0.02, F[2] + 0.06)
    k.box("lever", (x - s * (LEV[0] / 2 + 0.015), g0[1], g0[2]), (0.03, 0.06, 0.06), soft=0.004)   # the grip's boss
    g0 = (g0[0] - s * 0.03, g0[1], g0[2])
    k.tube("lever", g0, g1, 0.016, seg=20)
    k.tube("rubber", lerp(g0, g1, 0.3), g1, 0.02, soft=0.003)
    k.cyl("plastic", (g1[0] - s * 0.005, g1[1], g1[2]), 0.021, 0.01, axis="x", seg=20, soft=0.002)
    wq = lerp(B, F, 0.4)
    k.box("warn", (x + s * (LEV[0] / 2 + 0.001), wq[1], wq[2]), (0.002, 0.045, 0.04), soft=0.0)


def seat(k):
    """The seat on its post: an outer sleeve on the centre rail with a row of holes, the inner post up to the seat's
    bracket, the pop pin's knob on the sleeve's front."""
    bw = 0.076
    zs = 0.30                                           # the sleeve's top
    wt = (bw - 0.058) / 2                               # the sleeve: four walls round the inner post
    for sx, sy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (sx * (bw - wt) / 2, SEAT_Y + sy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP), soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, SEAT_Y - bw / 2 - 0.0005, 0.12 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = SEAT_TOP - SEAT[2] - 0.012
    k.bar("frame", (0, SEAT_Y, zs - 0.06), (0, SEAT_Y, zt), 0.058, 0.058, up=(0, 1, 0))           # the inner post
    k.tube("steel", (0, SEAT_Y - 0.02, zs - 0.03), (0, SEAT_Y - bw / 2 - 0.035, zs - 0.03), 0.007)   # into the post
    k.cyl("plastic", (0, SEAT_Y - bw / 2 - 0.05, zs - 0.03), 0.02, 0.03, axis="y", seg=24, soft=0.006)  # the pop pin
    k.box("frame", (0, SEAT_Y, zt + 0.006), (0.30, 0.22, 0.012), soft=0.002)                       # the seat's plate
    c = (0.0, SEAT_Y, SEAT_TOP - SEAT[2] / 2)
    k.shaped_pad("pad", [(-SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, -SEAT[1] / 2), (SEAT[0] / 2, SEAT[1] / 2),
                         (-SEAT[0] / 2, SEAT[1] / 2)], c, (0, 0, 1), (1, 0, 0), SEAT[2], r=0.06, cushion=0.03)


def back(k):
    """The back pad reclined, on its spine plate, bracketed back to the two cross bars between the rear uprights."""
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
        yb = Y_UP - SQ / 2
        k.bar("frame", (0, q[1], z), (0, yb, z), 0.06, 0.05, up=(0, 0, 1),
              cut0=(tuple(q[i] - face[i] * 0.02 for i in range(3)), face), cut1=((0, yb, 0), (0, 1, 0)), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Seated facing -y, the back on the reclined pad, the hands on the grips beside the shoulders (the start of the
    press), the feet flat on the floor in front; for a short, a middle and a tall user (the seat adjusts on its post;
    shown at one height)."""
    out = {}
    lean = math.degrees(math.atan2(BACK_TOP[0] - BACK_BOT[0], BACK_TOP[1] - BACK_BOT[1]))
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        hip = (0.0, SEAT_Y + 0.06, SEAT_TOP + 0.045 * H / 1.78)
        lt, ls = 0.245 * H, 0.246 * H
        kz = ls + 0.039 * H                             # the knee over the ankle, the foot flat on the floor
        a = -math.degrees(math.acos(max(-1.0, min(1.0, (hip[2] - kz) / lt))))
        ky = hip[1] - lt * math.sin(math.radians(-a))
        ball = (0.0, ky - 0.073 * H, 0.0)
        arm, forearm, arm_out = reach(H, hip, -lean)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=0, thigh=a, trunk=-lean, neck=8,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles (body.figure's) that put the left hand's palm on the left grip's middle, the elbow under and
    behind the hand: a coarse search, then a fine one round the best."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H                       # the shoulders (facing -y: forward is -y)
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    tx, ty, tz = (X_LEV + GRIP_IN) / 2 - 0.04, FOOT[0] + 0.025, FOOT[1] + 0.04   # the grip rises inward from the foot

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        n = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / n * 0.186 * H, sy + ay / n * 0.186 * H, sz + az / n * 0.186 * H
        g = 0.191 * H                                                   # the wrist and half the hand
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ez > hz else 0.0)   # keep the elbow below the hand

    best = min(((miss(a, f, o), a, f, o) for a in range(90, 271, 5) for f in range(-60, 181, 5) for o in range(0, 81, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    assert best[0] < 0.03, f"the grips are out of reach ({best[0]:.3f} m short)"
    return best[1], best[2], best[3]


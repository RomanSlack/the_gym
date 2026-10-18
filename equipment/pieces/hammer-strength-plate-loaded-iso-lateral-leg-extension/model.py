"""Hammer Strength Plate-Loaded Iso-Lateral Leg Extension (IL-LE).

Built by eye from the dealer gallery (refs/: ref_10 a true side view, ref_08 a true front view, ref_01 the studio
three-quarter, the rest close-ups), held to Life Fitness's 153 x 186 x 137 cm (L x W with the weight horns x H).
No camera fitting (the Precor's lesson): positions from the side + front views, the look from the close-ups.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left. Both levers are mirror images (s = +1 / -1).
Colourway: Charcoal frame, black upholstery (the listing's main photo).
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black levers
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),             # black vinyl
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),                            # horns, axles
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),                                                    # yellow warning labels
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4),
}
VIEWS = {"three_quarter": (27, 12, 1.3), "front": (0, 5, 1.3), "side": (-90, 3, 1.3), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {   # the joints up close, from the angles of the close-ups (ref_08's left tower, ref_12's pivot)
    "detail_pivot_front": ((-0.95, -1.9, 0.95), (-0.62, 0.0, 0.62), 60),
    "detail_pivot": ((1.25, -0.75, 1.05), (0.68, 0.0, 0.78), 50),
}
ORTHO = {"ortho_side": -90, "ortho_front": 0, "ortho_top": "top"}

# ---- each side (mirror images, s = +1 / -1), from the side view (ref_10, ~350 px/m), the front view (ref_08) and the
# close-ups (ref_12, ref_09): the pivot is a YOKE, a 3 x 3 in bridge welded across the A-frame's apex with a short post
# rising from each end; the lever swings between the posts on a hub round the axle, which runs through both posts; the
# black ROM plates (rows of start-position holes) are bolted flat onto the posts, the inner one on the lever's side
YOKE_Z = 0.62                    # top of the bridge (the posts stand on it)
POST = 0.076                     # posts and bridge: 3 x 3 in
POST_X = (0.55, 0.74)            # inner and outer post centres (x)
POST_TOP = 0.95
PIV_Y, PIV_Z = 0.0, 0.86         # the knee pivot (the user's knee sits on its axis)
LX = 0.66                        # the lever bar, between the posts
ROM_T, ROM_D, ROM_Z = 0.035, 0.11, (0.70, 1.02)   # ROM plates: thickness (x), depth (y), from / to (z)
HUB_R = 0.042                    # the lever's hub round the axle
TILT = 27.0                      # at rest the lower arm leans forward of vertical (deg)
UP_L, LO_L = 0.42, 0.70          # lever lengths above / below the pivot
LEV = (0.05, 0.10)               # lever section: across (x) x along the swing (2 x 4 in)
HORN_AT, HORN_L = 0.36, 0.27     # the weight horn: distance down the lower arm, length outwards
SHIN_AT = 0.25                   # the shin pad's rod: distance down the lower arm
SHIN = (0.28, 0.20, 0.075)       # shin pad: width (x), height, thickness
SHIN_X = 0.21                    # its centre (x)
# ---- the frame
BX = 0.645                       # the A-frames and the side rails under them (x), under the yoke's middle
BY0, BY1 = -0.47, 0.27           # main base: front and rear cross bars (y)
RX, RY = 0.33, 0.84              # the seat's rear legs (x, beside the seat) and their feet (y)
BOX = (0.076, 0.05)              # base section (3 x 2 in)
LEG = (0.076, 0.076)             # A-frame legs and the swoops (3 x 3 in)
# ---- seat + back pad (ref_10: the seat high and tilted back, the back pad long and leaning)
SEAT_F = (0.07, 0.85)            # the seat's front top edge (y, z)
SEAT_L, SEAT_W, SEAT_T, SEAT_TILT = 0.49, 0.58, 0.10, 22.0
BACK_L, BACK_W, BACK_T, BACK_LEAN = 0.88, 0.30, 0.08, 36.0   # its top (1.37 m) is the highest point


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))


def lever_dir():
    t = math.radians(TILT)
    return (0.0, -math.sin(t), -math.cos(t))      # down the lower arm


def on_lever(s, d):
    """A point d along the lever from the pivot (d > 0 down the lower arm, < 0 up the upper arm)."""
    u = lever_dir()
    return (s * LX, PIV_Y + u[1] * d, PIV_Z + u[2] * d)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for s in (1, -1):
        side(k, s)
    base(k)
    seat(k)


def side(k, s):
    """One side: the A-frame and its yoke, the lever on its hub between the posts, ROM plates, horn and shin pad.
    Every joint is one of: welded (the member's end cut to the face it meets, a bead round it), bolted (a plate flat on a
    face, bolts with washers), or on the axle (a hub or a bore, nuts at its ends). kit.check() reports anything else."""
    t = math.radians(TILT)
    xi, xo = s * POST_X[0], s * POST_X[1]
    bot = YOKE_Z - POST                                       # the bridge's underside
    Z = (0, 0, 1)
    # the A-frame: two legs from the side rail's top up under the bridge, a gusset filling the top of the V between them,
    # the swoop welded to the front leg's inner face, down and inwards to the middle
    legs = [((s * BX, fy, BOX[1]), (s * BX, PIV_Y, bot)) for fy in (BY0 + 0.06, BY1 - 0.04)]
    for p0, p1 in legs:
        k.bar("frame", p0, p1, LEG[0], LEG[1], up=(1, 0, 0), cut0=((0, 0, BOX[1]), Z), cut1=((0, 0, bot), Z), weld=True)

    def leg_y(n, z):                                          # where leg n's centreline is at height z
        (_, y0, z0), (_, y1, z1) = legs[n]
        return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    zw = bot - 0.13
    web = [(leg_y(0, zw), zw), (leg_y(1, zw), zw), (PIV_Y, bot)]
    k.sweep("frame", [(s * BX - 0.03, 0, 0), (s * BX + 0.03, 0, 0)], [(-y, z) for y, z in web], up=Z, soft=0.002)
    fx = s * (BX - LEG[0] / 2)                                # the legs' inner faces
    zs = 0.42
    k.sweep("frame", [(fx, leg_y(0, zs), zs), (s * (BX - 0.25), -0.02, 0.12), (s * 0.06, PIV_Y + 0.07, 0.10)],
            k.rect(LEG[0], LEG[1], 0.008), bend=0.17, up=(0, 1, 0), cut0=((fx, 0, 0), (s, 0, 0)), weld=True)
    # the yoke: the bridge across the apex, a post at each end welded on top, plastic caps
    k.bar("frame", (xi - s * POST / 2, PIV_Y, bot + POST / 2), (xo + s * POST / 2, PIV_Y, bot + POST / 2), POST, POST)
    for x_ in (xi, xo):
        k.bar("frame", (x_, PIV_Y, YOKE_Z), (x_, PIV_Y, POST_TOP), POST, POST, up=(0, 1, 0), cut0=((0, 0, YOKE_Z), Z), weld=True)
        k.box("plastic", (x_, PIV_Y, POST_TOP + 0.006), (POST + 0.004, POST + 0.004, 0.012), soft=0.003)
    k.box("warn", (xo + s * (POST / 2 + 0.001), PIV_Y, YOKE_Z + 0.07), (0.002, 0.05, 0.045), soft=0.0)
    # the ROM plates bolted flat on the posts (the inner on its lever side, the outer on its outside), through-bolts
    for x_, face in ((xi + s * POST / 2, s), (xo + s * POST / 2, s)):
        pc = x_ + face * ROM_T / 2
        k.box("lever", (pc, PIV_Y, sum(ROM_Z) / 2), (ROM_T, ROM_D, ROM_Z[1] - ROM_Z[0]), soft=0.003)
        for zz in (YOKE_Z + 0.09, POST_TOP - 0.04):
            k.bolt((x_ + face * ROM_T, PIV_Y + 0.03, zz), ("+x" if face > 0 else "-x"), nut=ROM_T + POST)
        for i in range(9):   # the start-position holes: a row on the front, two on the outer face (ref_12)
            zz = ROM_Z[0] + 0.035 + i * (ROM_Z[1] - ROM_Z[0] - 0.07) / 8
            if abs(zz - PIV_Z) < 0.035 or abs(zz - YOKE_Z - 0.09) < 0.02 or abs(zz - POST_TOP + 0.04) < 0.02:
                continue
            k.cyl("hole", (pc, PIV_Y - ROM_D / 2 - 0.0005, zz), 0.0085, 0.002, axis="y", seg=14)
            for dy in (-0.025, 0.025):
                k.cyl("hole", (pc + face * (ROM_T / 2 + 0.0005), PIV_Y + dy, zz), 0.0085, 0.002, axis="x", seg=14)
    # the axle through both posts and the hub, a nut at each end; the hub fills the gap between the inner plate and the
    # outer post (it bears on both)
    a0, a1 = xi - s * (POST / 2 + 0.012), xo + s * (POST / 2 + ROM_T + 0.012)
    k.tube("steel", (a0, PIV_Y, PIV_Z), (a1, PIV_Y, PIV_Z), 0.019)
    for x_, d in ((a0, -s), (a1, s)):
        k.bolt((x_ - d * 0.012, PIV_Y, PIV_Z), ("+x" if d > 0 else "-x"), size=0.03)
    h0, h1 = xi + s * (POST / 2 + ROM_T), xo - s * POST / 2
    k.tube("lever", (h0, PIV_Y, PIV_Z), (h1, PIV_Y, PIV_Z), HUB_R, seg=32)
    # the start-position T-handle: its rod through the tops of both ROM plates, the grip out past the outer one
    hz_ = ROM_Z[1] - 0.025
    k.tube("steel", (xi + s * (POST / 2 - 0.01), PIV_Y - 0.03, hz_), (xo + s * (POST / 2 + ROM_T + 0.18), PIV_Y - 0.03, hz_), 0.011)
    k.tube("rubber", (xo + s * (POST / 2 + ROM_T + 0.07), PIV_Y - 0.03, hz_), (xo + s * (POST / 2 + ROM_T + 0.19), PIV_Y - 0.03, hz_), 0.016)
    # the lever: a 2 x 4 in bar through the hub (welded to it), the square top cap, bolts down its face
    top, bot_ = on_lever(s, -UP_L), on_lever(s, LO_L)
    k.sweep("lever", [top, bot_], k.rect(LEV[0], LEV[1], 0.006), up=(0, math.cos(t), -math.sin(t)), soft=0.003)
    k.box("plastic", top, (0.10, 0.13, 0.11), rx=-t, soft=0.01)                                          # the top cap
    for d in (-0.20, 0.14, 0.50):
        q = on_lever(s, d)
        k.bolt((q[0] + s * LEV[0] / 2, q[1], q[2]), "+x" if s > 0 else "-x", size=0.012, nut=LEV[0])
    # the weight horn: a gusset block welded to the lever's outer face, a collar on it, the sleeve, its end cap
    h = on_lever(s, HORN_AT)
    xf = h[0] + s * LEV[0] / 2
    k.box("lever", (xf + s * 0.02, h[1], h[2]), (0.04, 0.10, 0.10), rx=-t, soft=0.006)
    k.cyl("lever", (xf + s * 0.05, h[1], h[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xf + s * 0.058, h[1], h[2]), (s * (LX + HORN_L), h[1], h[2]), 0.025, seg=32)
    k.cyl("lever", (s * (LX + HORN_L + 0.008), h[1], h[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the shin pad (ref_08, ref_09): a collar welded to the lever's inner face, the rod from it inwards, bent back into a
    # bracket plate it's welded to; the bracket bolted to the pad's back plate; a flat brace from higher up the lever
    r0 = on_lever(s, SHIN_AT)
    ry, rz = r0[1] - 0.03, r0[2]
    xin = s * (LX - LEV[0] / 2)                               # the lever's inner face
    k.box("lever", (xin - s * 0.02, ry, rz), (0.04, 0.075, 0.075), soft=0.006)
    yb = ry + 0.045                                           # the bracket's front face
    xr = s * (SHIN_X - 0.04)
    k.sweep("lever", [(xin - s * 0.04, ry, rz), (xr, ry, rz), (xr, yb, rz)], k.circle(0.017, 20), bend=0.03,
            cut0=((xin - s * 0.04, 0, 0), (s, 0, 0)), cut1=((0, yb, 0), (0, 1, 0)), weld=True)
    k.box("lever", (s * SHIN_X, yb + 0.006, rz), (0.16, 0.012, 0.075), soft=0.002)                       # the bracket
    k.box("lever", (s * SHIN_X, yb + 0.018, rz), (SHIN[0] - 0.04, 0.012, SHIN[1] - 0.04), soft=0.003)   # the pad's back plate
    for dx in (-0.06, 0.06):
        k.bolt((s * SHIN_X + dx, yb, rz + 0.02), "-y", size=0.01)
    q = on_lever(s, SHIN_AT - 0.15)
    k.bar("lever", (xin, q[1], q[2]), (s * (SHIN_X + 0.06), yb, rz + 0.025), 0.035, 0.012, up=(0, 1, 0),
          cut0=((xin, 0, 0), (s, 0, 0)), cut1=((0, yb, 0), (0, 1, 0)), weld=True)
    pc = (s * SHIN_X, yb + 0.024 + SHIN[2] / 2, rz)
    k.shaped_pad("pad", [(-SHIN[0] / 2, -SHIN[1] / 2), (SHIN[0] / 2, -SHIN[1] / 2), (SHIN[0] / 2, SHIN[1] / 2), (-SHIN[0] / 2, SHIN[1] / 2)],
                 pc, (0, 1, 0), (1, 0, 0), SHIN[2], r=0.03, cushion=0.025)


def base(k):
    bw, bh = BOX
    # main base: a side rail under each tower, the front and rear cross bars, a centre rail
    for s in (1, -1):
        k.bar("frame", (s * BX, BY0, bh / 2), (s * BX, BY1, bh / 2), bw, bh)
        for fy in (BY0, BY1):
            k.box("rubber", (s * BX, fy, 0.006), (0.12, 0.09, 0.012), soft=0.003)
        for by in (BY0 + 0.12, -0.12, 0.08, BY1 - 0.1):
            k.cyl("bolt", (s * (BX + bw / 2 + 0.003), by, bh / 2), 0.011, 0.007, axis="x", seg=6)
    for y_ in (BY0, BY1):
        k.bar("frame", (-BX, y_, bh / 2), (BX, y_, bh / 2), bw, bh)
    k.bar("frame", (0, BY0, bh / 2), (0, RY, bh / 2), bw, bh)
    k.box("warn", (0.25, BY0 - bw / 2 - 0.002, bh / 2), (0.04, 0.002, 0.035), soft=0.0)
    # the seat's rear section: its rails out to the rear feet, a cross bar
    for s in (1, -1):
        k.bar("frame", (s * RX, BY1, bh / 2), (s * RX, RY, bh / 2), bw, bh)
        k.box("rubber", (s * RX, RY, 0.006), (0.10, 0.10, 0.012), soft=0.003)
    k.bar("frame", (-RX, RY - 0.03, bh / 2), (RX, RY - 0.03, bh / 2), bw, bh)


def seat(k):
    t = math.radians(SEAT_TILT)
    fy, fz = SEAT_F
    along = (0.0, math.cos(t), -math.sin(t))                 # front -> back along the seat top
    nrm = (0.0, math.sin(t), math.cos(t))                    # the seat's up
    c = (0.0, fy + along[1] * SEAT_L / 2 - nrm[1] * SEAT_T / 2, fz + along[2] * SEAT_L / 2 - nrm[2] * SEAT_T / 2)
    k.shaped_pad("pad", [(-SEAT_W / 2, -SEAT_L / 2), (SEAT_W / 2, -SEAT_L / 2), (SEAT_W / 2, SEAT_L / 2), (-SEAT_W / 2, SEAT_L / 2)],
                 c, nrm, (1, 0, 0), SEAT_T, r=0.06, cushion=0.035)
    under = (0.0, c[1] - nrm[1] * (SEAT_T / 2 + 0.02), c[2] - nrm[2] * (SEAT_T / 2 + 0.02))
    k.box("frame", under, (0.36, SEAT_L * 0.9, 0.05), rx=-t, soft=0.005)               # the seat's frame (a deep box under it)
    fr = (0.0, fy + 0.04, fz - SEAT_T - 0.046)
    k.tube("frame", (-SEAT_W / 2 + 0.03, fr[1], fr[2]), (SEAT_W / 2 - 0.03, fr[1], fr[2]), 0.02)        # the tube across under its front
    # the swoops meet in a block on the centre rail; the seat's slim post stands on the rail under the seat's middle
    k.box("frame", (0.0, PIV_Y + 0.07, BOX[1] + 0.045), (0.14, 0.11, 0.09), soft=0.005)
    k.tube("frame", (0.0, under[1], BOX[1]), (0.0, under[1], under[2] - 0.02), 0.03, seg=28)
    k.box("frame", (0.0, under[1], BOX[1] + 0.006), (0.10, 0.10, 0.012), soft=0.002)                  # its foot plate
    # the back pad: a lumbar section at the seat's rear, the long main pad, both leaning BACK_LEAN
    rear_top = (0.0, fy + along[1] * SEAT_L, fz + along[2] * SEAT_L)
    b = math.radians(BACK_LEAN)
    upv = (0.0, math.sin(b), math.cos(b)); bn = (0.0, -math.cos(b), math.sin(b))   # up the pad, its face (towards the user)
    p0 = (0.0, rear_top[1] - 0.03, rear_top[2] - 0.015)      # the lumbar pad sits on the seat's rear edge
    for d0, d1 in ((0.0, 0.17), (0.175, BACK_L)):
        mid = (d0 + d1) / 2
        pc = (0.0, p0[1] + upv[1] * mid - bn[1] * BACK_T / 2, p0[2] + upv[2] * mid - bn[2] * BACK_T / 2)
        L = d1 - d0
        k.shaped_pad("pad", [(-BACK_W / 2, -L / 2), (BACK_W / 2, -L / 2), (BACK_W / 2, L / 2), (-BACK_W / 2, L / 2)],
                     pc, bn, (1, 0, 0), BACK_T, r=0.05, cushion=0.03)
    # its frame: a spine plate behind the pad, two rear legs (an A each side) carrying it and the seat's rear, the grips
    sp0 = (0.0, p0[1] - bn[1] * (BACK_T + 0.02), p0[2] - bn[2] * (BACK_T + 0.02))
    sp1 = (0.0, sp0[1] + upv[1] * BACK_L * 0.8, sp0[2] + upv[2] * BACK_L * 0.8)
    k.bar("frame", sp0, sp1, 0.08, 0.04, up=bn)
    # the rear legs (ref_03, ref_10): each one bent tube up from its foot and forwards at seat height into the hand grip,
    # a strut from the base's rear cross bar, a cross tube between them carrying the back pad's spine
    zg = rear_top[2] - 0.02
    for sx in (1, -1):
        x_ = sx * RX
        bend_at = (x_, RY - 0.10, zg)
        tip = (x_, rear_top[1] - 0.24, zg + 0.01)
        k.sweep("frame", [(x_, RY, BOX[1]), bend_at, tip], k.rect(0.05, 0.05, 0.006), bend=0.10, up=(1, 0, 0))
        k.tube("rubber", lerp(bend_at, tip, 0.55), (tip[0], tip[1] - 0.02, tip[2]), 0.022)               # the hand grip
        k.cyl("rubber", (tip[0], tip[1] - 0.02, tip[2]), 0.024, 0.012, axis="y")
        k.bar("frame", (x_, BY1 + 0.10, BOX[1]), lerp((x_, RY, BOX[1]), bend_at, 0.72), 0.05, 0.05, up=(1, 0, 0))   # the strut
    cz = zg - 0.06
    k.bar("frame", (-RX, RY - 0.12, cz), (RX, RY - 0.12, cz), 0.06, 0.05)
    k.bar("frame", sp0, (0.0, RY - 0.12, cz), 0.06, 0.05)                                                   # the spine down to it

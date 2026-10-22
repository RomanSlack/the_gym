"""Hammer Strength Plate-Loaded Linear Leg Press (HSLLP), Charcoal frame / Black upholstery, the sled racked at rest.

Built by eye from the dealer gallery (refs/: ref_12 a true side view, ref_10 a true view from the seat end, ref_01 the
studio three-quarter in the picked colourway, ref_13 the side loaded, ref_08 / ref_09 / ref_14 close-ups of the beam's
badge, the foot plate's grit and the racking handles; most photos show the silver frame, the build is the same), held to
Life Fitness's 95 x 65 x 57 in (241 x 165 x 145 cm, L x W x H; W across the sled's horns).
Axes: metres, floor z = 0, the user sits at +y facing -y, pushing the sled up the rails towards -y; x+ = the user's
left. Sides mirrored (s = +1 / -1).
Structure: a base rail each side under the incline, cross bars, a spine forward under the seat; on each side an incline
beam (45 degrees) from the front cross bar up to a rear post, a middle post and a diagonal brace under it, a chrome
guide rod on end blocks above it, two storage horns on the rear post; the sled on four linear bearings: two side plates
carrying the foot plate (tilted a little off square to the rails), two loading horns each side, the racking handles
reaching down beside the seat; the seat pad and the reclined back pad on the spine.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black sled
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-145, 16, 1.15), "front": (180, 6, 1.15), "side": (90, 3, 1.15), "back_three_quarter": (35, 18, 1.15)}
DETAILS = {
    "detail_sled": ((0.95, 0.75, 1.55), (0.0, -0.20, 1.00), 45),         # the foot plate and its horns from the seat
    "detail_seat": ((0.95, 1.65, 0.95), (0.0, 0.75, 0.45), 45),          # the seat, back pad and racking handles
    "detail_rear": ((-0.95, -1.75, 0.85), (-0.20, -0.95, 0.60), 45),     # the rear posts, horns, brace
}

A = math.radians(45.0)
U = (0.0, -math.cos(A), math.sin(A))       # up the rails (towards -y)
N = (0.0, math.sin(A), math.cos(A))        # off the rails, up towards the seat
B0 = (0.22, 0.13)                          # the beams' centreline at s = 0 (y, z)
BL = 1.85
BX = 0.22                                  # each side's plane: base rail, beam, posts; the rods either side of it
BEAM = (0.10, 0.152)                       # 4 x 6 in
RAIL = (0.10, 0.10)
POST = 0.10
ROD_DX = 0.045                             # the two rods each side, off the side's plane
SIDE_X = BX + 0.098                        # the sled's side plates, outside the bearings
FOOT_H = 0.02
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
RY0, RY1 = 0.29, -1.10                     # base rails: the front cross bar (y), the rear end
POSTS = (-0.86, -1.05)                     # middle and rear posts (y)
ROD_H, ROD_R, ROD_S = 0.14, 0.019, (0.12, 1.78)
SLED = (0.60, 1.55)                        # the sled's span along U (racked)
PLATE_C = (0.905, 0.467)                   # the foot plate's centre (s, h)
PLATE = (0.92, 0.66, 0.05)
PLATE_UP = (0.27, 0.96)                    # the plate's up, in (s, h)
HORNS = ((1.47, 0.283), (0.955, 0.347))    # the sled's loading horns (s, h)
HORN_X = 0.825


def at(x, s, h):
    return (x, B0[0] + U[1] * s + N[1] * h, B0[1] + U[2] * s + N[2] * h)


def s_at_y(y, h):
    return (y - B0[0] - N[1] * h) / U[1]


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def build(k):
    Z = (0, 0, 1)
    nU = tuple(-c for c in N)
    for s in (1, -1):
        x = s * BX
        # the base rail on its feet, capped
        k.bar("frame", (x, RY0 + 0.04, RAIL_Z), (x, RY1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((RY0 + 0.04, 1), (RY1, -1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.04)
        # the incline beam, its foot cut onto the base rail's top, capped; the HAMMER STRENGTH badge on its outer face
        k.bar("frame", at(x, -0.15, 0.0), at(x, BL, 0.0), BEAM[0], BEAM[1], up=N, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", at(x, BL + 0.005, 0.0), (BEAM[0] + 0.004, 0.01, BEAM[1] + 0.004), rx=-A, soft=0.002)
        bc = at(x + s * (BEAM[0] / 2 + 0.002), 1.30, 0.0)
        k.box("lever", bc, (0.004, 0.17, 0.07), rx=-A, soft=0.001)
        for i, line in enumerate(("HAMMER", "STRENGTH")):
            c = at(x + s * (BEAM[0] / 2 + 0.0045), 1.30, 0.014 - i * 0.028)
            k.text("label", line, c, 0.022, rz=s * math.pi / 2, spin=-s * A, depth=0.0004)
        # the posts up under the beam (the rear one with a warning label and two storage horns), the diagonal brace
        for py in POSTS:
            top = at(x, s_at_y(py, -BEAM[1] / 2), -BEAM[1] / 2)
            k.bar("frame", (x, py, RAIL_TOP), (x, py, top[2] + 0.05), POST, POST, up=(0, 1, 0),
                  cut0=((0, 0, RAIL_TOP), Z), cut1=(top, nU), weld=True)
        bt = at(x, s_at_y(-0.40, -BEAM[1] / 2), -BEAM[1] / 2)
        k.bar("frame", (x, bt[1] + 0.03, bt[2] + 0.03), (x, POSTS[0] + POST / 2, RAIL_TOP + 0.12), 0.08, 0.08, up=(1, 0, 0),
              cut0=(bt, nU), cut1=((0, POSTS[0] + POST / 2, 0), (0, 1, 0)), weld=True)
        py = POSTS[1]
        k.box("warn", (x, py - POST / 2 - 0.001, 0.95), (0.045, 0.002, 0.07), soft=0.0)
        for zh in (0.26, 0.75):
            xo = x + s * POST / 2
            k.cyl("frame", (xo + s * 0.008, py, zh), 0.055, 0.016, axis="x", seg=32, soft=0.003)
            k.tube("steel", (xo + s * 0.012, py, zh), (xo + s * 0.30, py, zh), 0.025, seg=32)
            k.cyl("frame", (xo + s * 0.308, py, zh), 0.029, 0.016, axis="x", seg=32, soft=0.004)
        # the two guide rods on their end blocks
        for sr in ROD_S:
            k.box("frame", at(x, sr, (BEAM[1] / 2 + ROD_H + 0.025) / 2), (0.18, 0.07, ROD_H + 0.025 - BEAM[1] / 2), rx=-A, soft=0.004)
        for dx in (-ROD_DX, ROD_DX):
            k.tube("chrome", at(x + dx, ROD_S[0] + 0.035, ROD_H), at(x + dx, ROD_S[1] - 0.035, ROD_H), ROD_R, seg=28)
        # the sled: two bearing housings round both rods, the side plate outside them up to the foot plate's back,
        # the loading horns
        for sb in (SLED[0] + 0.10, SLED[1] - 0.10):
            k.box("lever", at(x, sb, ROD_H + 0.01), (0.18, 0.18, 0.11), rx=-A, soft=0.008)
            for d in (-0.05, 0.05):
                for dz in (-0.025, 0.025):
                    k.bolt(at(x + s * 0.09, sb + d, ROD_H + 0.01 + dz), "+x" if s > 0 else "-x", size=0.01)
        ps, ph = PLATE_C
        bk = (ps + 0.96 * PLATE[2] / 2 + 0.002, ph - 0.27 * PLATE[2] / 2)          # the plate's back face, centre (s, h)
        top_ = (bk[0] + PLATE_UP[0] * PLATE[1] / 2, bk[1] + PLATE_UP[1] * PLATE[1] / 2)
        bot_ = (bk[0] - PLATE_UP[0] * PLATE[1] / 2, bk[1] - PLATE_UP[1] * PLATE[1] / 2)
        poly = [(SLED[0], 0.10), (SLED[1], 0.10), (SLED[1], 0.40), top_, (bot_[0], max(bot_[1], 0.12)), (SLED[0], 0.28)]
        pts = [at(0, a, b) for a, b in poly]
        xs = s * SIDE_X
        k.sweep("lever", [(xs - 0.008, 0, 0), (xs + 0.008, 0, 0)], [(-p[1], p[2]) for p in pts], up=Z, soft=0.002)
        for hs, hh in HORNS:
            hc = at(0, hs, hh)
            xo = xs + s * 0.008
            k.cyl("lever", (xo + s * 0.03, hc[1], hc[2]), 0.06, 0.06, axis="x", seg=32, soft=0.004)
            k.tube("steel", (xo + s * 0.06, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
            k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
        # the racking handle: down from the side plate's low end towards the seat, a grip out sideways
        r0 = at(xs + s * 0.008, SLED[0] + 0.06, 0.20)
        r1 = at(xs + s * 0.03, 0.22, 0.27)
        r2 = at(xs + s * 0.14, 0.20, 0.27)
        k.sweep("lever", [r0, r1, r2], k.circle(0.015, 18), bend=0.05, soft=0.0015)
        k.tube("plastic", tuple(r1[i] + (r2[i] - r1[i]) * 0.35 for i in range(3)), r2, 0.021, seg=22)
    # the sled's cross members between the bearing housings, the top cross tube between the beams' tops
    xb = BX - 0.09
    for sb in (SLED[0] + 0.10, SLED[1] - 0.10):
        a0, a1 = at(-xb, sb, ROD_H + 0.04), at(xb, sb, ROD_H + 0.04)
        k.bar("lever", a0, a1, 0.08, 0.08, cut0=(a0, (1, 0, 0)), cut1=(a1, (1, 0, 0)), weld=True)
    xbi = BX - BEAM[0] / 2
    t0, t1 = at(-xbi, BL - 0.12, 0.0), at(xbi, BL - 0.12, 0.0)
    k.bar("frame", t0, t1, 0.08, 0.08, cut0=(t0, (1, 0, 0)), cut1=(t1, (1, 0, 0)), weld=True)
    # the counter-frame each side (ref_12): a heavy diagonal from the floor up over the sled to the front top, the top
    # bar from there back to the beam's top, a stub tying the beam to the diagonal where they cross; a cross tube
    # between the two front tops; the diagonals stand on a wide foot bar
    CX = 0.42
    d0, d1 = (-0.84, RAIL_TOP), (-0.24, 1.47)
    tb = at(0, BL - 0.06, BEAM[1] / 2 + 0.05)
    for sx in (1, -1):
        x = sx * CX
        k.bar("frame", (x, d0[0] - 0.04, d0[1] - 0.10), (x, d1[0], d1[1]), 0.10, 0.12, up=(1, 0, 0),
              cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.bar("frame", (x, d1[0] + 0.05, d1[1]), (x, tb[1], tb[2]), 0.10, 0.10, up=(1, 0, 0))
        k.bar("frame", (sx * (BX + 0.06), tb[1], tb[2]), (x + sx * 0.05, tb[1], tb[2]), 0.08, 0.08)
        xc = (sx * (BX + BEAM[0] / 2), -0.495, 0.845)
        k.bar("frame", xc, (x, -0.495, 0.845), 0.08, 0.08, cut0=(xc, (1, 0, 0)), weld=True)
        k.box("warn", (x, d1[0] + 0.02, d1[1] - 0.12), (0.002, 0.05, 0.06), soft=0.0)
    k.bar("frame", (-CX + 0.05, d1[0], d1[1]), (CX - 0.05, d1[0], d1[1]), 0.09, 0.09, cut0=((-CX + 0.05, 0, 0), (1, 0, 0)),
          cut1=((CX - 0.05, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (-0.52, d0[0], RAIL_Z), (0.52, d0[0], RAIL_Z), 0.10, RAIL[1], r=0.006)
    for sx in (1, -1):
        k.box("plastic", (sx * 0.524, d0[0], RAIL_Z), (0.008, 0.104, RAIL[1] + 0.004), soft=0.002)
        foot(k, sx * 0.47, d0[0])
    # the cross bars between the base rails (front, under the posts), the wide rear foot bar, the spine to the seat
    xi = BX - RAIL[0] / 2
    for y_ in (RY0, POSTS[0]):
        k.bar("frame", (-xi, y_, RAIL_Z), (xi, y_, RAIL_Z), 0.10, RAIL[1],
              cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (-0.52, RY1 + 0.05, RAIL_Z), (0.52, RY1 + 0.05, RAIL_Z), 0.10, RAIL[1], r=0.006)
    for sx in (1, -1):
        k.box("plastic", (sx * 0.524, RY1 + 0.05, RAIL_Z), (0.008, 0.104, RAIL[1] + 0.004), soft=0.002)
        foot(k, sx * 0.47, RY1 + 0.05)
    sp1 = 1.26
    k.bar("frame", (0, RY0 + 0.05, RAIL_Z), (0, sp1, RAIL_Z), 0.10, RAIL[1], cut0=((0, RY0 + 0.05, 0), (0, 1, 0)), weld=True)
    k.bar("frame", (-0.22, sp1 - 0.05, RAIL_Z), (0.22, sp1 - 0.05, RAIL_Z), 0.10, RAIL[1], r=0.006)
    for sx in (1, -1):
        foot(k, sx * 0.17, sp1 - 0.05)
        k.box("plastic", (sx * 0.224, sp1 - 0.05, RAIL_Z), (0.008, 0.104, RAIL[1] + 0.004), soft=0.002)
    # the foot plate: its plate and the grit face towards the user
    ps, ph = PLATE_C
    rxp = math.radians(60.6)
    k.box("lever", at(0, ps, ph), PLATE, rx=rxp, soft=0.006)
    g = at(0, ps - 0.96 * (PLATE[2] / 2 + 0.002), ph + 0.27 * (PLATE[2] / 2 + 0.002))
    k.box("grip", g, (PLATE[0] - 0.03, PLATE[1] - 0.03, 0.004), rx=rxp, soft=0.001)
    k.box("warn", (0.30, g[1] + 0.49 * 0.24 + 0.87 * 0.002, g[2] + 0.87 * 0.24 - 0.49 * 0.002), (0.035, 0.035, 0.002), rx=rxp, soft=0.0)
    # the seat: a post on the spine, the seat pad tilted back; the back pad reclined on a hinge and a strut, its knob
    st = math.radians(16)
    sc = (0.0, 0.62, 0.40)
    k.bar("frame", (0, sc[1], RAIL_TOP), (0, sc[1], sc[2] - 0.08), 0.08, 0.08, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, sc[1], sc[2] - 0.07), (0.36, 0.38, 0.03), rx=-st, soft=0.004)
    k.pad("pad", sc, (0.50, 0.44, 0.11), r=0.05, rx=-st)
    # the seat's grips: a cross bar under it, a bent handle up at each end
    k.bar("frame", (-0.30, sc[1], 0.24), (0.30, sc[1], 0.24), 0.05, 0.05, r=0.006)
    for sx in (1, -1):
        g0, g1 = (sx * 0.30, sc[1], 0.265), (sx * 0.31, sc[1] - 0.05, 0.42)
        k.sweep("frame", [g0, (sx * 0.30, sc[1] + 0.02, 0.36), g1], k.circle(0.016, 18), bend=0.04, soft=0.0015)
        k.tube("rubber", (sx * 0.302, sc[1] + 0.005, 0.38), g1, 0.021, seg=22)
    bt_ = math.radians(40)
    b0 = (0.0, 0.83, 0.43)
    upb = (0.0, math.cos(bt_), math.sin(bt_)); nb = (0.0, -math.sin(bt_), math.cos(bt_))
    L = 0.80
    bc_ = tuple(b0[i] + upb[i] * L / 2 + nb[i] * 0.05 for i in range(3))
    k.shaped_pad("pad", [(-0.25, -L / 2), (0.25, -L / 2), (0.23, L / 2), (-0.23, L / 2)], bc_, nb, (1, 0, 0), 0.09,
                 r=0.06, cushion=0.03)
    k.box("frame", tuple(b0[i] + upb[i] * L / 2 - nb[i] * 0.005 for i in range(3)), (0.10, L * 0.85, 0.03), rx=bt_, soft=0.004)
    k.box("frame", (0, b0[1] - 0.02, b0[2] - 0.03), (0.12, 0.10, 0.07), soft=0.004)                    # the hinge block
    k.bar("frame", (0, b0[1] - 0.02, RAIL_TOP), (0, b0[1] - 0.02, b0[2] - 0.065), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    sb = tuple(b0[i] + upb[i] * L * 0.62 - nb[i] * 0.02 for i in range(3))
    k.bar("frame", (0, 1.16, RAIL_TOP), sb, 0.05, 0.05, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.tube("steel", (0.02, 1.167, 0.30), (0.10, 1.167, 0.30), 0.007, seg=14)
    k.cyl("plastic", (0.11, 1.167, 0.30), 0.016, 0.03, axis="x", seg=20, soft=0.004)

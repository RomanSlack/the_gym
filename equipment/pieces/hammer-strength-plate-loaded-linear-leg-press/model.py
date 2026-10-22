"""Hammer Strength Plate-Loaded Linear Leg Press (HSLLP), Charcoal frame / Black upholstery, the sled racked at rest.

Built by eye from the dealer gallery (refs/: ref_13 a true side view empty and ref_02 the same in use (the geometry is
read off these two), ref_12 the side closer, ref_10 a true view from the seat end, ref_01 the studio three-quarter in
the picked colourway, ref_04 / ref_06 / ref_07 the seat, its adjuster and the racking handles in use; most photos show the
silver frame, the build is the same), held to Life Fitness's 95 x 65 x 57 in (241 x 165 x 145 cm, L x W x H; W across
the sled's horns).
Axes: metres, floor z = 0, the user sits at +y facing -y, pushing the sled up the rails towards -y; x+ = the user's
left. Sides mirrored (s = +1 / -1).
Structure (ref_13): the rails start right at the seat, near the floor, and climb at ~40 degrees to the top at the back,
~2 m along the slope: on each side a 4 x 6 in beam on the base rail, two chrome rods on end blocks above it, a rear post
pair carrying two storage horns, a brace from the beam's middle down to them. The sled (on bearing housings round both
rods) is a frame each side: the foot plate on its front, nearly upright, the top arm back to the upper loading horn, the
lower horn, the racking handles down beside the seat. The seat lies low at the rails' foot, tilted back; the back pad is
hinged at the seat's rear and stands on a strut whose foot sits in a notched rack on the spine; the release handle
comes out the spine's end: pull it and the strut drops to the next notch (the back pad lower or higher).
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
    "detail_seat": ((0.80, 1.65, 0.62), (0.0, 0.95, 0.25), 42),          # the back pad's strut, its notched rack, the release handle
    "detail_rear": ((-0.95, -1.75, 0.85), (-0.20, -0.95, 0.60), 45),     # the rear posts, horns, brace
}

A = math.radians(40.0)                     # the rails' climb (ref_13)
U = (0.0, -math.cos(A), math.sin(A))       # up the rails (towards -y)
N = (0.0, math.sin(A), math.cos(A))        # off the rails, up towards the seat
B0 = (0.33, 0.14)                          # the beams' centreline at s = 0 (y, z): their foot, at the seat
BL = 2.00                                  # the beams' length along U (to the top at y -1.20, z 1.43)
BX = 0.22                                  # each side's plane: base rail, beam, posts; the rods either side of it
BEAM = (0.10, 0.152)                       # 4 x 6 in
RAIL = (0.10, 0.10)
POST = 0.10
ROD_DX = 0.045
SIDE_X = BX + 0.098                        # the sled's side frames, outside the bearings
FOOT_H = 0.02
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
RY0, RY1 = 0.37, -1.12                     # base rails: the front cross bar (y), the rear end
POSTS = (-0.94, -1.06)                     # the rear post pair (y)
ROD_H, ROD_R, ROD_S = 0.14, 0.019, (0.10, 1.92)
SLED = (0.55, 1.55)                        # the sled's span along U (racked)
PLATE_C = (0.874, 0.481)                   # the foot plate's centre (s, h): y -0.03, z 1.07 (ref_13)
PLATE = (0.80, 0.60, 0.05)
PLATE_UP = (0.365, 0.931)                  # the plate's up, in (s, h): leaning back ~18 degrees from upright
PLATE_RX = math.radians(71.4)
HORNS = ((1.454, 0.333), (0.965, 0.325))   # the sled's loading horns (s, h): upper and lower (ref_13)
HORN_X = 0.825
SPINE_END = 1.20


def at(x, s, h):
    return (x, B0[0] + U[1] * s + N[1] * h, B0[1] + U[2] * s + N[2] * h)


def s_at_y(y, h):
    return (y - B0[0] - N[1] * h) / U[1]


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def bar_x(k, mat, y, z, x0, x1, w, h):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def tilted(c, t, d_along, d_norm):
    """A point d_along up a plane rising towards +y at angle t from c, d_norm off it (upwards)."""
    return (c[0], c[1] + math.cos(t) * d_along - math.sin(t) * d_norm, c[2] + math.sin(t) * d_along + math.cos(t) * d_norm)


def build(k):
    Z = (0, 0, 1)
    nU = tuple(-c for c in N)
    for s in (1, -1):
        x = s * BX
        # ---- the base rail on its feet, capped
        k.bar("frame", (x, RY0 + 0.05, RAIL_Z), (x, RY1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((RY0 + 0.05, 1), (RY1, -1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.045)
        # ---- the beam from the rail's top at the seat to the top at the back, capped; its badge
        k.bar("frame", at(x, -0.12, 0.0), at(x, BL, 0.0), BEAM[0], BEAM[1], up=N, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", at(x, BL + 0.005, 0.0), (BEAM[0] + 0.004, 0.01, BEAM[1] + 0.004), rx=-A, soft=0.002)
        k.box("lever", at(x + s * (BEAM[0] / 2 + 0.002), 1.42, 0.0), (0.004, 0.17, 0.07), rx=-A, soft=0.001)
        for i, line in enumerate(("HAMMER", "STRENGTH")):
            c = at(x + s * (BEAM[0] / 2 + 0.0045), 1.42, 0.014 - i * 0.028)
            k.text("label", line, c, 0.022, rz=s * math.pi / 2, spin=-s * A, depth=0.0004)
        # ---- the rear post pair up under the beam; the brace from the beam's middle down to the front post's foot;
        # the warning label; two storage horns on the rear post
        for py in POSTS:
            top = at(x, s_at_y(py, -BEAM[1] / 2), -BEAM[1] / 2)
            k.bar("frame", (x, py, RAIL_TOP), (x, py, top[2] + 0.06), POST, POST, up=(0, 1, 0),
                  cut0=((0, 0, RAIL_TOP), Z), cut1=(top, nU), weld=True)
        bt = at(x, s_at_y(-0.37, -BEAM[1] / 2), -BEAM[1] / 2)
        k.bar("frame", (x, bt[1] + 0.03, bt[2] + 0.03), (x, POSTS[0] + POST / 2, RAIL_TOP + 0.10), 0.08, 0.08, up=(1, 0, 0),
              cut0=(bt, nU), cut1=((0, POSTS[0] + POST / 2, 0), (0, 1, 0)), weld=True)
        k.box("warn", (x + s * (POST / 2 + 0.001), POSTS[1], 0.95), (0.002, 0.045, 0.07), soft=0.0)
        for zh in (0.23, 0.70):
            xo = x + s * POST / 2
            k.cyl("frame", (xo + s * 0.008, POSTS[1], zh), 0.055, 0.016, axis="x", seg=32, soft=0.003)
            k.tube("steel", (xo + s * 0.016, POSTS[1], zh), (xo + s * 0.31, POSTS[1], zh), 0.025, seg=32)
            k.cyl("frame", (xo + s * 0.318, POSTS[1], zh), 0.029, 0.016, axis="x", seg=32, soft=0.004)
        # ---- the two guide rods on their end blocks
        for sr in ROD_S:
            k.box("frame", at(x, sr, (BEAM[1] / 2 + ROD_H + 0.025) / 2), (0.18, 0.07, ROD_H + 0.025 - BEAM[1] / 2), rx=-A, soft=0.004)
        for dx in (-ROD_DX, ROD_DX):
            k.tube("chrome", at(x + dx, ROD_S[0] + 0.035, ROD_H), at(x + dx, ROD_S[1] - 0.035, ROD_H), ROD_R, seg=28)
        # ---- the sled: two bearing housings round both rods; the side frame outside them (the foot plate's back, the
        # top arm back to the upper horn, down to the carriage); the loading horns
        for sb in (SLED[0] + 0.10, SLED[1] - 0.10):
            k.box("lever", at(x, sb, ROD_H + 0.01), (0.18, 0.18, 0.11), rx=-A, soft=0.008)
            for d in (-0.05, 0.05):
                for dz in (-0.025, 0.025):
                    k.bolt(at(x + s * 0.09, sb + d, ROD_H + 0.01 + dz), "+x" if s > 0 else "-x", size=0.01)
        ps, ph = PLATE_C
        bk = (ps + 0.934 * PLATE[2] / 2 + 0.002, ph - 0.366 * PLATE[2] / 2)        # the plate's back face, centre (s, h)
        top_ = (bk[0] + PLATE_UP[0] * PLATE[1] / 2, bk[1] + PLATE_UP[1] * PLATE[1] / 2)
        bot_ = (bk[0] - PLATE_UP[0] * PLATE[1] / 2, bk[1] - PLATE_UP[1] * PLATE[1] / 2)
        poly = [(SLED[0], 0.10), (SLED[1], 0.10), (SLED[1], 0.40), (HORNS[0][0] + 0.06, HORNS[0][1] + 0.12),
                (top_[0] + 0.08, top_[1] - 0.02), top_, (bot_[0], max(bot_[1], 0.12)), (SLED[0], 0.26)]
        pts = [at(0, a, b) for a, b in poly]
        xs = s * SIDE_X
        k.sweep("lever", [(xs - 0.008, 0, 0), (xs + 0.008, 0, 0)], [(-p[1], p[2]) for p in pts], up=Z, soft=0.002)
        for hs, hh in HORNS:
            hc = at(0, hs, hh)
            xo = xs + s * 0.008
            k.cyl("lever", (xo + s * 0.03, hc[1], hc[2]), 0.06, 0.06, axis="x", seg=32, soft=0.004)
            k.tube("steel", (xo + s * 0.06, hc[1], hc[2]), (s * HORN_X, hc[1], hc[2]), 0.025, seg=32)
            k.cyl("lever", (s * (HORN_X + 0.008), hc[1], hc[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
        # the racking handle: from the side frame's low end down beside the seat, the grip turned out
        r0 = at(xs + s * 0.008, SLED[0] + 0.06, 0.20)
        r1 = at(xs + s * 0.03, 0.10, 0.24)
        r2 = at(xs + s * 0.14, 0.08, 0.24)
        k.sweep("lever", [r0, r1, r2], k.circle(0.015, 18), bend=0.05, soft=0.0015)
        k.tube("plastic", tuple(r1[i] + (r2[i] - r1[i]) * 0.35 for i in range(3)), r2, 0.021, seg=22)
    # ---- the sled's cross members between the bearing housings
    xb = BX - 0.09
    for sb in (SLED[0] + 0.10, SLED[1] - 0.10):
        a0, a1 = at(-xb, sb, ROD_H + 0.04), at(xb, sb, ROD_H + 0.04)
        k.bar("lever", a0, a1, 0.08, 0.08, cut0=(a0, (1, 0, 0)), cut1=(a1, (1, 0, 0)), weld=True)
    # ---- the top cross tube between the beams, the cross bars (the rails' foot, the posts), the spine to the seat end
    xbi = BX - BEAM[0] / 2
    t0, t1 = at(-xbi, BL - 0.10, 0.0), at(xbi, BL - 0.10, 0.0)
    k.bar("frame", t0, t1, 0.08, 0.08, cut0=(t0, (1, 0, 0)), cut1=(t1, (1, 0, 0)), weld=True)
    xi = BX - RAIL[0] / 2
    for y_ in (RY0, POSTS[0]):
        bar_x(k, "frame", y_, RAIL_Z, -xi, xi, 0.10, RAIL[1])
    k.bar("frame", (-0.50, RY1 + 0.05, RAIL_Z), (0.50, RY1 + 0.05, RAIL_Z), 0.10, RAIL[1], r=0.006)
    for sx in (1, -1):
        k.box("plastic", (sx * 0.504, RY1 + 0.05, RAIL_Z), (0.008, 0.104, RAIL[1] + 0.004), soft=0.002)
        foot(k, sx * 0.45, RY1 + 0.05)
    k.bar("frame", (0, RY0 + 0.05, RAIL_Z), (0, SPINE_END, RAIL_Z), 0.10, RAIL[1], cut0=((0, RY0 + 0.05, 0), (0, 1, 0)), weld=True)
    k.box("plastic", (0, SPINE_END + 0.004, RAIL_Z), (0.104, 0.008, RAIL[1] + 0.004), soft=0.002)
    k.bar("frame", (-0.20, SPINE_END - 0.06, RAIL_Z), (0.20, SPINE_END - 0.06, RAIL_Z), 0.08, RAIL[1], r=0.006)
    for sx in (1, -1):
        foot(k, sx * 0.16, SPINE_END - 0.06)
        k.box("plastic", (sx * 0.204, SPINE_END - 0.06, RAIL_Z), (0.008, 0.084, RAIL[1] + 0.004), soft=0.002)
    # ---- the foot plate: its plate and the grit face towards the user, a warning label
    ps, ph = PLATE_C
    k.box("lever", at(0, ps, ph), PLATE, rx=PLATE_RX, soft=0.006)
    g = at(0, ps - 0.934 * (PLATE[2] / 2 + 0.002), ph + 0.366 * (PLATE[2] / 2 + 0.002))
    k.box("grip", g, (PLATE[0] - 0.03, PLATE[1] - 0.03, 0.004), rx=PLATE_RX, soft=0.001)
    w = at(0.30, ps - 0.934 * 0.029 + 0.365 * 0.24, ph + 0.366 * 0.029 + 0.931 * 0.24)
    k.box("warn", w, (0.035, 0.035, 0.002), rx=PLATE_RX, soft=0.0)
    # ---- the seat: low at the rails' foot, tilted back, on a post and a frame from the spine
    st = math.radians(21)
    s_front = (0.0, 0.48, 0.26)                       # the seat's top at its front edge (just behind the rails' foot)
    L_seat = 0.42
    sc = tilted(s_front, st, L_seat / 2, -0.055)       # the pad's centre (it is 0.11 thick)
    k.pad("pad", sc, (0.50, L_seat, 0.11), r=0.05, rx=st)
    under = tilted(s_front, st, L_seat / 2, -0.125)
    k.box("frame", under, (0.36, L_seat - 0.04, 0.03), rx=st, soft=0.004)
    k.bar("frame", (0, under[1], RAIL_TOP), (0, under[1], under[2] - 0.01), 0.08, 0.08, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    # ---- the back pad: hinged at the seat's rear on a block on a post from the spine, reclined, its frame under it
    hinge = tilted(s_front, st, L_seat + 0.01, -0.10)
    k.cyl("frame", hinge, 0.028, 0.16, axis="x", seg=24, soft=0.003)                  # the hinge knuckle
    k.bar("frame", (0, hinge[1], RAIL_TOP), (0, hinge[1], hinge[2] - 0.02), 0.07, 0.07, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    bt_ = math.radians(28)
    L = 0.52
    bpc = tilted(hinge, bt_, L / 2 + 0.02, 0.10)                                       # the pad's centre
    nb = (0.0, -math.sin(bt_), math.cos(bt_))
    k.shaped_pad("pad", [(-0.25, -L / 2), (0.25, -L / 2), (0.23, L / 2), (-0.23, L / 2)], bpc, nb, (1, 0, 0), 0.09,
                 r=0.06, cushion=0.03)
    k.box("frame", tilted(hinge, bt_, L / 2, 0.03), (0.12, L, 0.05), rx=bt_, soft=0.004)          # its frame
    # ---- the adjuster: the strut from under the back pad down to the notched rack on the spine, the release handle
    sa = tilted(hinge, bt_, L * 0.45, 0.005)                                           # the strut's top pivot
    k.cyl("frame", sa, 0.022, 0.14, axis="x", seg=20, soft=0.003)
    foot_y = sa[1] - 0.04                                                              # on the spine, short of its end
    rack0, rack1 = foot_y - 0.08, foot_y + 0.08
    k.box("steel", (0, (rack0 + rack1) / 2, RAIL_TOP + 0.015), (0.06, rack1 - rack0, 0.03), soft=0.002)
    for i in range(5):                                                                  # the notches' teeth
        ty = rack0 + 0.016 + i * 0.032
        k.box("steel", (0, ty, RAIL_TOP + 0.038), (0.06, 0.012, 0.018), rx=-0.5, soft=0.001)
    for sx in (1, -1):
        k.bar("frame", (sx * 0.04, sa[1], sa[2]), (sx * 0.04, foot_y, RAIL_TOP + 0.05), 0.03, 0.04, up=(1, 0, 0))
    k.tube("steel", (-0.06, foot_y, RAIL_TOP + 0.05), (0.06, foot_y, RAIL_TOP + 0.05), 0.012, seg=14)   # the pin in a notch
    h0 = (0.0, foot_y, RAIL_TOP + 0.05)
    h1 = (0.0, SPINE_END + 0.02, RAIL_TOP + 0.10)
    h2 = (0.11, SPINE_END + 0.04, RAIL_TOP + 0.10)
    k.sweep("steel", [h0, h1, h2], k.circle(0.011, 14), bend=0.04, soft=0.001)
    k.cyl("plastic", (0.125, SPINE_END + 0.04, RAIL_TOP + 0.10), 0.02, 0.04, axis="x", seg=20, soft=0.005)

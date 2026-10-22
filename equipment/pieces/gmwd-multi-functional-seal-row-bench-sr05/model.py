"""GMWD SR05 Multi-Functional Seal Row Bench.

Built by eye from GMWD's gallery (refs/: ref_01 + ref_02 the studio three-quarters, ref_04 the product size sheet,
ref_13 + ref_14 in use, ref_06 the barbell holder's pin, ref_07 the seat's rack, ref_10 the rear foot), held to its
47.8 in length, 47.2 in rail and 37 in height.
Axes: metres, floor z = 0, the user lies along x (head at -x over the rail, knees at +x on the seat); y across.
Structure: a cross rail on the floor with a red barbell holder at each end (a red foot on wedge feet, a red post on two
gussets, a black inner post on a pop pin, a J cradle on top: the bar lies across under the chest pad); an arch along
x: the front leg up off the rail's middle (kinked back at the top), a beam under the chest pad bolted between the legs'
tops, the rear leg leaning back down to a T foot. On the rear leg: the thigh pad (GMWD), and a sliding carriage on a
toothed rack carrying the knee seat, held by a pin.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, metal=0.1, coat=0.2, bump=(1400, 0.05)),   # black gloss powder coat
    "red": dict(color=(0.50, 0.012, 0.012), rough=0.3, metal=0.1, coat=0.25, bump=(1400, 0.05)),       # the holders' red
    "pad": dict(color=(0.010, 0.010, 0.011), rough=0.42, sheen=0.2, bump=(1800, 0.08)),              # black PU
    "plastic": dict(color=(0.015, 0.015, 0.016), rough=0.6),
    "rubber": dict(color=(0.014, 0.014, 0.015), rough=0.7, bump=(700, 0.1)),                         # the wedge feet
    "hole": dict(color=(0.003, 0.003, 0.003), rough=0.9),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4),
    "bolt": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-125, 12, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (40, 16, 1.0)}
DETAILS = {
    "detail_holder": ((-0.55, -1.05, 0.6), (0.0, -0.56, 0.4), 40),      # a barbell holder: foot, gussets, pin, J
    "detail_carriage": ((1.35, -0.55, 0.75), (0.74, 0.0, 0.5), 40),     # the knee seat's carriage on the rack
    "detail_top": ((0.35, -0.85, 1.1), (0.36, 0.0, 0.82), 40),          # the chest pad's beam and its bolted plates
}

T2, T3 = 2 * IN, 3 * IN
RAIL_Y = 47.2 * IN / 2          # the rail's half length, the holders' feet included
HOLD_Y = RAIL_Y - 0.045         # the holders' centres (y)
FOOT_L = 0.42                   # the holders' red feet (x)
PAD_TOP, CHEST = 37 * IN, (0.06, 0.68)   # the chest pad: top, x from / to
CHEST_W, PAD_T = 0.27, 0.07
BEAM_X = (0.12, 0.60)           # the beam under it: the front leg's top, the rear leg's top
KINK_Z = 0.45                   # the front leg rises straight to here, then leans back to the beam
REAR_FOOT = (0.92, 0.56)        # the rear T foot: x, length (y)
SEAT_TOP, SEAT = 0.55, (0.70, 1.12)
SEAT_W = 0.26
THIGH_AT, THIGH = 0.13, (0.27, 0.24, 0.07)  # the thigh pad: distance down the rear leg, width, height, thickness
J_TOP = 0.78                    # the J cradles' floor height (the bar's rest)


def wedge(k, c, along):
    """A black wedge foot capping a tube's end (ref_01, ref_10): a block, sloped faces left soft."""
    sx, sy = (0.075, 0.095) if along == "x" else (0.095, 0.075)
    k.box("rubber", (c[0], c[1], 0.035), (sx, sy, 0.07), soft=0.012)


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    rz = 0.012 + T2 / 2                                               # the floor tubes' centreline
    # ---- the barbell holders and the rail between them
    for s in (1, -1):
        holder(k, s)
    yi = HOLD_Y - T3 / 2                                              # the red feet's inner faces
    k.bar("frame", (0, -yi, rz), (0, yi, rz), T3, T2, up=Z, cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=False)
    for s in (1, -1):
        for dx in (-0.025, 0.025):
            k.bolt((dx, s * (HOLD_Y + T3 / 2), rz), "+y" if s > 0 else "-y", size=0.012, nut=T3 + 0.002)
    # ---- the arch: the front leg off the rail, the beam, the rear leg down to the T foot
    beam_c = PAD_TOP - PAD_T - T3 / 2
    beam_bot = beam_c - T3 / 2
    rail_top = rz + T2 / 2
    k.sweep("frame", [(0, 0, rail_top), (0, 0, KINK_Z), (BEAM_X[0], 0, beam_bot)], k.rect(T2, T3, 0.006), up=Y, bend=0.02,
            cut0=((0, 0, rail_top), Z), cut1=((0, 0, beam_bot), Z), weld=True)
    k.box("frame", (0, 0, rail_top + 0.003), (0.10, 0.10, 0.006), soft=0.002)       # its base plate on the rail
    k.bolt((0.035, -0.035, rail_top + 0.006), "+z", size=0.01)
    rf = (REAR_FOOT[0], 0, 0.012 + T3)
    k.bar("frame", (BEAM_X[1], 0, beam_bot), rf, T2, T3, up=Y, cut0=((0, 0, beam_bot), Z), cut1=((0, 0, rf[2]), Z), weld=True)
    k.bar("frame", (BEAM_X[0] - 0.04, 0, beam_c), (BEAM_X[1] + 0.04, 0, beam_c), T3, T2, up=Y)
    for bx in (BEAM_X[0], BEAM_X[1]):                                 # the bolted plates joining the legs to the beam
        for s in (1, -1):
            k.box("frame", (bx, s * (T2 / 2 + 0.003), beam_c - 0.03), (0.13, 0.006, 0.14), soft=0.002)
        for dx in (-0.035, 0.035):
            k.bolt((bx + dx, -(T2 / 2 + 0.006), beam_c), "-y", size=0.012, nut=T2 + 0.012)
    # the rear T foot: across y on wedge feet, the rear leg welded on its middle
    fx, fl = REAR_FOOT
    k.bar("frame", (fx, -fl / 2, 0.012 + T3 / 2), (fx, fl / 2, 0.012 + T3 / 2), T2, T3, up=Z)
    for s in (1, -1):
        wedge(k, (fx, s * (fl / 2 - 0.03)), "y")
    # ---- the chest pad on the beam
    pad(k, CHEST, CHEST_W, PAD_TOP - PAD_T)
    # ---- on the rear leg
    rear(k, (BEAM_X[1], 0, beam_bot), rf)


def holder(k, s):
    """One barbell holder (ref_01, ref_06): a red foot along x on wedge feet, a red post on two gussets, a black inner
    post set by a pop pin with a ball knob, a J cradle on top."""
    y = s * HOLD_Y
    Z = (0, 0, 1)
    fz = 0.012 + T2 / 2
    k.bar("red", (-FOOT_L / 2 + 0.02, y, fz), (FOOT_L / 2 - 0.02, y, fz), T3, T2, up=Z)
    for d in (1, -1):
        wedge(k, (d * (FOOT_L / 2 - 0.03), y), "x")
    top = 0.012 + T2
    P = 2.5 * IN
    k.bar("red", (0, y, top), (0, y, 0.50), P, P, up=(0, 1, 0), cut0=((0, 0, top), Z), weld=True)
    for d in (1, -1):                                                 # the gussets
        k.bar("red", (d * 0.15, y, top), (d * P / 2, y, 0.27), 0.04, 0.04, up=(0, 1, 0),
              cut0=((0, 0, top), Z), cut1=((d * P / 2, 0, 0), (1, 0, 0)), weld=True)
    k.box("plastic", (0, y, 0.502), (P + 0.004, P + 0.004, 0.006), soft=0.002)          # the post's collar
    ip = 2 * IN                                                       # the inner post, its hole row
    k.bar("frame", (0, y, 0.40), (0, y, J_TOP - 0.012), ip, ip, up=(0, 1, 0))
    for i in range(6):
        k.cyl("hole", (-(ip / 2 + 0.0005), y, 0.54 + i * 0.035), 0.0055, 0.001, axis="x", seg=12)
    # the pop pin through the post's face towards the bench (-y for the +y holder), its ball knob
    py = y - s * (P / 2)
    k.box("red", (0, py - s * 0.008, 0.40), (0.035, 0.016, 0.035), soft=0.003)
    k.tube("steel", (0, py - s * 0.016, 0.40), (0, py - s * 0.06, 0.40), 0.006)
    k.cyl("plastic", (0, py - s * 0.072, 0.40), 0.02, 0.026, axis="y", seg=28, soft=0.009)
    # the J cradle: a floor plate, a tall back tab (outboard) and a short lip (inboard), the bar rests between them
    k.box("frame", (0, y, J_TOP - 0.006), (0.065, 0.06, 0.012), soft=0.002)
    k.box("frame", (0, y + s * 0.024, J_TOP + 0.05), (0.065, 0.012, 0.10), soft=0.003)
    k.box("frame", (0, y - s * 0.03, J_TOP + 0.022), (0.065, 0.012, 0.044), rx=s * 0.35, soft=0.003)
    k.box("plastic", (0, y, J_TOP + 0.002), (0.06, 0.036, 0.004), soft=0.001)            # the cradle's liner


def rear(k, top, bot):
    """On the rear leg: the thigh pad bolted to its rear face, the toothed rack on its front face, the carriage with the
    knee seat sliding on it, held by a pin."""
    L = math.dist(top, bot)
    d = tuple((bot[i] - top[i]) / L for i in range(3))                # down the leg
    n = (-d[2], 0, d[0])                                               # its rear face's normal (back and up)
    if n[0] < 0:
        n = tuple(-v for v in n)

    def at(q, off=0.0):
        return tuple(top[i] + d[i] * q + n[i] * off for i in range(3))
    tilt = math.atan2(n[2], n[0])                                     # the rear face's lean back from vertical
    # the thigh pad: a bracket plate on the leg's rear face, the pad on it, GMWD on its face
    tw, th, tt = THIGH
    c0 = at(THIGH_AT, T2 / 2 + 0.006)
    k.box("frame", c0, (0.012, 0.12, 0.14), ry=-tilt, soft=0.002)
    pc = at(THIGH_AT, T2 / 2 + 0.012 + tt / 2)
    k.shaped_pad("pad", [(-tw / 2, -th / 2), (tw / 2, -th / 2), (tw / 2, th / 2), (-tw / 2, th / 2)], pc, n, (0, 1, 0), tt,
                 r=0.03, seam=False, cushion=0.02)
    lc = at(THIGH_AT, T2 / 2 + 0.012 + tt + 0.0095)
    k.text("label", "GMWD", lc, 0.05, rz=math.pi / 2, rx=math.pi / 2 - tilt, depth=0.002)
    # the rack: teeth on the leg's front face
    for i in range(10):
        q = 0.24 + i * 0.03
        k.box("frame", at(q, -(T2 / 2 + 0.006)), (0.012, 0.03, 0.014), ry=-tilt, soft=0.002)
    # the carriage: a sleeve round the leg where the seat sits, an arm back from it, the seat's plate and pad
    zc = SEAT_TOP - PAD_T - 0.05
    q = (top[2] - zc) / -d[2]
    s0, s1 = at(q - 0.09), at(q + 0.09)
    k.bar("frame", s0, s1, T2 + 0.012, T3 + 0.012, up=(0, 1, 0))
    k.box("frame", at(q, -(T2 / 2 + 0.006 + 0.012)), (0.02, 0.04, 0.05), ry=-tilt, soft=0.002)       # the pin's boss
    k.tube("steel", at(q, -(T2 / 2 + 0.026)), at(q, -(T2 / 2 + 0.07)), 0.007)
    k.cyl("plastic", at(q, -(T2 / 2 + 0.08)), 0.017, 0.022, axis="x", seg=24, soft=0.006)
    sx = at(q, (T2 + 0.012) / 2)[0]
    k.bar("frame", (sx, 0, zc), (SEAT[1] - 0.10, 0, zc), T2, T2, up=(0, 1, 0), cut0=((sx, 0, 0), (1, 0, 0)), weld=True)
    sb = SEAT_TOP - PAD_T
    k.box("frame", ((SEAT[0] + SEAT[1]) / 2 + 0.02, 0, (zc + T2 / 2 + sb) / 2), (0.30, 0.16, sb - zc - T2 / 2), soft=0.002)
    pad(k, SEAT, SEAT_W, sb)


def pad(k, span, w, bottom):
    """A black PU pad on its board, rounded, no visible stitching (ref_01)."""
    x0, x1 = span
    L = x1 - x0
    k.shaped_pad("pad", [(-L / 2, -w / 2), (L / 2, -w / 2), (L / 2, w / 2), (-L / 2, w / 2)],
                 ((x0 + x1) / 2, 0, bottom + PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.035, seam=False, cushion=0.02)

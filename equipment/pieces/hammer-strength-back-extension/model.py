"""Hammer Strength Back Extension (the 45 degree hyper), Charcoal frame / Black upholstery.

Built by eye from the listing's photos (refs/: ref_01 the studio three-quarter, ref_02-ref_08 in use from the side,
ref_09 the galvanized adjustment plates close up).
Axes: metres, floor z = 0, along x: the thigh pads and handles high at -x, the footrest and ankle pads low at +x; the
user lies face down along the 45 degree line between them.
Structure: a centre rail on the floor from a Y-shaped front foot to a rear cross foot (anchor tabs at the ends); a
beam rising at 45 degrees from the rail's rear half to the front, propped by a post; galvanized plates bolted either
side of its upper end with a notched slot, the carriage sleeve on the beam pinned in a notch, the split thigh pads and
the handlebars on the carriage; at the rear a bent post carrying the two ankle pads above the textured footrest.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.045, 0.047, 0.05), rough=0.45, metal=0.3, coat=0.05, bump=(1400, 0.06)),   # Charcoal
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.5, sheen=0.25, bump=(1500, 0.12)),
    "galv": dict(color=(0.62, 0.63, 0.64), rough=0.35, metal=1.0, coat=0.0, bump=(300, 0.15)),         # galvanized plate
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, bump=(900, 0.8)),                     # the footrest's grit
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 16, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_carriage": ((0.25, -0.75, 1.05), (-0.30, 0.0, 0.62), 40),   # the galvanized plates, the carriage, the pin
    "detail_ankles": ((0.95, -0.8, 0.7), (0.38, 0.0, 0.38), 40),        # the ankle pads over the footrest
}

R = (3 * IN, 2 * IN)            # rail / feet: across x tall
RX = (-0.50, 0.55)              # the rail's ends (x)
A = math.radians(45.0)
U = (-math.cos(A), 0.0, math.sin(A))   # up the 45 degree line, towards the front
N = (math.cos(A), 0.0, math.sin(A))    # perpendicular to it, up and back: the faces the user lies on
B0 = (0.22, 0.06)               # where the beam leaves the rail (x, z)
BEAM = (3 * IN, 2.5 * IN)       # beam section: across y x deep (along N)
BEAM_L = 0.92
SLV = 3 * 0.0254 / 2 + 0.015    # the carriage sleeve's half width
POST_X = -0.24
CAR = (0.62, 0.82)              # the carriage along the beam (s from / to)
THIGH = (0.17, 0.38, 0.09)      # each thigh pad: width (y), length (along U), thickness
FOOT_C = (0.40, 0.24)           # the footrest's centre (x, z)


def at(s, off=0.0, y=0.0):
    return (B0[0] + U[0] * s + N[0] * off, y, B0[1] + U[2] * s + N[2] * off)


def tab(k, x, y):
    k.box("frame", (x, y, 0.006), (0.08, 0.06, 0.012), soft=0.002)
    k.cyl("hole", (x, y, 0.0122), 0.007, 0.001, seg=14)


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    rz = 0.012 + R[1] / 2
    rt = 0.012 + R[1]
    # the rail, the rear cross foot, the Y front foot
    k.bar("frame", (RX[0], 0, rz), (RX[1] - R[0] / 2, 0, rz), R[1], R[0], up=Y, cut1=((RX[1] - R[0] / 2, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (RX[1], -0.40, rz), (RX[1], 0.40, rz), R[0], R[1], up=Z)
    for s in (1, -1):
        tab(k, RX[1], s * 0.43)
        k.box("plastic", (RX[1], s * 0.402, rz), (R[0] + 0.004, 0.006, R[1] + 0.004), soft=0.002)
        k.sweep("frame", [(RX[0] + 0.02, 0, rz), (RX[0] - 0.10, s * 0.12, rz), (RX[0] - 0.24, s * 0.38, rz)], k.rect(R[0], R[1], 0.006),
                up=Z, bend=0.12)
        k.box("plastic", (RX[0] - 0.243, s * 0.384, rz), (R[0] + 0.004, 0.006, R[1] + 0.004), rz=-s * 1.07, soft=0.002)
        tab(k, RX[0] - 0.28, s * 0.40)
    k.box("label", (0.0, -R[0] / 2 - 0.0006, rz), (0.10, 0.001, 0.03), soft=0.0)                  # the placard on the rail
    # the beam at 45 degrees, its foot welded on the rail, the post up to it
    b_top = at(BEAM_L)
    k.bar("frame", (B0[0], 0, rt), b_top, BEAM[1], BEAM[0], up=Y, cut0=((0, 0, rt), Z), weld=True)
    k.box("plastic", tuple(b_top[i] + U[i] * 0.004 for i in range(3)), (0.008, BEAM[0] + 0.004, BEAM[1] + 0.004), ry=A, soft=0.002)
    s_post = (B0[0] - POST_X) / math.cos(A)                              # where the post meets the beam's underside
    under = at(s_post, -BEAM[1] / 2)
    k.bar("frame", (POST_X, 0, rt), (POST_X, 0, under[2] + 0.02), R[0], R[0], up=Y,
          cut0=((0, 0, rt), Z), cut1=(at(0, -BEAM[1] / 2), tuple(-v for v in N)), weld=True)
    # the galvanized plates either side of the beam's upper end: a notched slot, bolts, a warning label
    pm = (CAR[0] + CAR[1]) / 2 + 0.02
    for s in (1, -1):
        yp = s * (SLV + 0.004)                                          # outside the carriage's sleeve
        for sb in (pm - 0.16, pm + 0.16):                               # spacer blocks off the beam's sides
            k.box("galv", at(sb, -0.035, s * (BEAM[0] / 2 + SLV) / 2), (0.04, SLV - BEAM[0] / 2 + 0.001, 0.04), ry=A, soft=0.001)
        c = at(pm, 0.01, yp)
        k.box("galv", c, (0.36, 0.008, 0.13), ry=A, soft=0.002)
        k.box("hole", at(pm, 0.02, s * (SLV + 0.0085)), (0.26, 0.001, 0.03), ry=A, soft=0.0)
        for j in range(5):
            k.box("galv", at(CAR[0] + 0.04 + j * 0.05, 0.005, s * (SLV + 0.0088)), (0.022, 0.001, 0.02), ry=A, soft=0.0)
        for sb in (pm - 0.15, pm + 0.15):
            k.bolt(at(sb, -0.035, s * (SLV + 0.008)), "+y" if s > 0 else "-y", size=0.012, nut=2 * SLV + 0.016)
    k.box("warn", at(pm + 0.12, -0.03, -(SLV + 0.0086)), (0.03, 0.001, 0.03), ry=A, soft=0.0)
    # the carriage: a sleeve round the beam, its pin through the plates' notch, the thigh pads' bracket on it
    k.bar("frame", at(CAR[0]), at(CAR[1]), BEAM[1] + 0.016, 2 * SLV, up=Y)
    pin = at(CAR[0] + 0.12, 0.02)
    k.tube("steel", (pin[0], -(SLV + 0.03), pin[2]), (pin[0], SLV + 0.03, pin[2]), 0.009)
    k.cyl("plastic", (pin[0], -(SLV + 0.045), pin[2]), 0.018, 0.03, axis="y", seg=24, soft=0.006)
    brk = at((CAR[0] + CAR[1]) / 2, BEAM[1] / 2 + 0.008 + 0.006)
    k.box("frame", brk, (0.012, 0.30, 0.20), ry=A - math.pi / 2, soft=0.002)
    tw, tl, tt = THIGH
    for s in (1, -1):
        pc = at((CAR[0] + CAR[1]) / 2 + 0.02, BEAM[1] / 2 + 0.008 + 0.012 + tt / 2, s * (tw / 2 + 0.008))
        k.shaped_pad("pad", [(-tw / 2, -tl / 2), (tw / 2, -tl / 2), (tw / 2, tl / 2), (-tw / 2, tl / 2)], pc, N, (0, 1, 0), tt,
                     r=0.04, cushion=0.025)
    # the handlebars: from the carriage's top end out to each side and forwards, grips on
    h0 = at(CAR[1] - 0.01, 0.0)
    for s in (1, -1):
        k.sweep("frame", [(h0[0], s * (SLV - 0.002), h0[2]), (h0[0], s * 0.24, h0[2] + 0.03), (h0[0] - 0.26, s * 0.27, h0[2] + 0.05)],
                k.circle(0.016, 20), bend=0.06)
        k.tube("rubber", (h0[0] - 0.12, s * 0.257, h0[2] + 0.042), (h0[0] - 0.265, s * 0.27, h0[2] + 0.05), 0.02, seg=24)
    # the footrest: a textured plate square to the 45 degree line on two struts from the rail
    fc = (FOOT_C[0], 0, FOOT_C[1])
    k.box("frame", fc, (0.012, 0.36, 0.22), ry=A, soft=0.002)
    k.box("grip", tuple(fc[i] + U[i] * 0.0065 for i in range(3)), (0.001, 0.34, 0.20), ry=A, soft=0.0)
    for s in (1, -1):
        top = (fc[0] - U[0] * 0.006 + 0.03, s * 0.12, fc[2] - U[2] * 0.006 - 0.03)
        k.bar("frame", (top[0] + 0.06, s * 0.12, rt), top, 0.04, 0.04, up=Y, cut0=((0, 0, rt), Z), weld=True)
    # the ankle post: up from the rail's rear, bending forwards over the footrest; the two ankle pads under its end
    ac = (fc[0] + U[0] * 0.17 + N[0] * 0.14, 0, fc[2] + U[2] * 0.17 + N[2] * 0.14)          # the pads' centre
    end = (ac[0] + N[0] * 0.07, 0, ac[2] + N[2] * 0.07)
    k.sweep("frame", [(0.48, 0, rt), (0.48, 0, end[2] - 0.05), end], k.rect(R[0], R[1] + 0.01, 0.008), up=Y, bend=0.1,
            cut0=((0, 0, rt), Z), weld=True)
    k.box("frame", (end[0] - N[0] * 0.006, 0, end[2] - N[2] * 0.006), (0.012, 0.32, 0.10), ry=A - math.pi / 2, soft=0.002)
    for s in (1, -1):
        k.shaped_pad("pad", [(-0.075, -0.055), (0.075, -0.055), (0.075, 0.055), (-0.075, 0.055)],
                     (ac[0], s * 0.085, ac[2]), tuple(-v for v in N), (0, 1, 0), 0.075, r=0.03, cushion=0.018)

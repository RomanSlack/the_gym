"""Atlantis Incline Calf Raise (M318), Precision Series, black frame, red upholstery, the carriage at its start.

Built by eye from Atlantis's four renders (refs/: ref_02 the front three-quarter from the left, ref_05 from the right,
ref_03 / ref_04 the two sides in profile), held to Atlantis's 63 x 38 x 68 in (L x W x H), the 400 lb stack (20 x 20 lb).
Axes: metres, floor z = 0, the incline runs along x: the tower at -x facing +x, the foot plates at +x; y across. The user
stands on a step facing the tower, leans in with the chest on the pad and the shoulders under the two shoulder pads,
and rises on the toes, pushing the carriage up its rods.
Structure: the closed stack tower ("atlantis" style); a rail each side from the floor at the front up to the tower's
face at the top (56 deg, a little steeper below the knee), a chrome guide rod on each rail's top face; the carriage on
the rods' linear bearings: its plate, the chest pad, the two shoulder pads at its top on their backing plates, the
pop pin; a tie and a brace each side from the rail back to the tower's face; low down, a beam each side from the tower
to the rail with the rear leg down from it, the cross tubes between the sides; the three foot plates (the three
start heights) square to the body off the rails, rubber treads; the cable from the carriage's foot down to a pulley on the low cross tube,
back to a pulley at the tower's face and up inside it.
"""
import math

import stack_tower

IN = 0.0254
FOOT_H = stack_tower.FOOT_H
LOOK = dict(
    frame=dict(color=(0.022, 0.022, 0.024), rough=0.45, metal=0.3, coat=0.2),
    lever=dict(color=(0.022, 0.022, 0.024), rough=0.45, metal=0.3, coat=0.2),
    pad=dict(color=(0.42, 0.018, 0.022), rough=0.5, sheen=0.3),
    seam=dict(color=(0.30, 0.012, 0.016), rough=0.6),
    plastic=dict(color=(0.02, 0.02, 0.02), rough=0.5),
    rubber=dict(color=(0.03, 0.03, 0.03), rough=0.85, bump=(220, 0.3)),
    tread=dict(color=(0.045, 0.045, 0.047), rough=0.8, bump=(90, 0.6)),
    chrome=dict(color=(0.85, 0.85, 0.86), rough=0.08, metal=1.0),
    steel=dict(color=(0.5, 0.5, 0.52), rough=0.3, metal=1.0),
    plate=dict(color=(0.05, 0.05, 0.055), rough=0.55, metal=0.4),
    cable=dict(color=(0.05, 0.05, 0.05), rough=0.4),
)
VIEWS = {"three_quarter": (50, 12, 1.0), "front": (90, 5, 1.0), "side": (0, 4, 1.0), "right_three_quarter": (130, 12, 1.0),
         "back_three_quarter": (-130, 16, 1.0)}
DETAILS = {
    "detail_carriage": ((1.35, -0.85, 1.75), (0.0, 0.0, 1.05), 40),       # the pads, the rods, the bearings, the pin
    "detail_tower": ((0.60, -1.25, 1.30), (-0.55, 0.0, 1.05), 40),        # the placard, the stack, the side's logo
}

TOWER = dict(style="atlantis", W=0.56, D=0.50, H=68 * IN, n=20, plate=(0.27, 0.15, 0.029), rods=0.17,
             title="CALF RAISE", brand="ATLANTIS", step=20, start=0, pin_at=6)
TC = (-0.55, 0.0)                    # the tower's footprint centre: its back at -0.80, its face at -0.30
X_FACE = TC[0] + TOWER["D"] / 2
YR = 0.28                            # the rails' centres, either side, in line with the tower's sides
RW, RD = 0.08, 0.12                  # a rail's width (y) and depth (across its slope)
RA = RB = math.radians(62)          # the rail's slope, straight to the floor
A = (X_FACE + 0.05, 1.58)            # the rail's top end (x, z), its back corner on the tower's face
ZK = 0.55                            # the knee
D1 = (math.cos(RA), -math.sin(RA))   # down the upper rail
N1 = (math.sin(RA), math.cos(RA))    # out of its top face, to the user
K = (A[0] + (A[1] - ZK) / math.tan(RA), ZK)
B = (K[0] + ZK / math.tan(RB), 0.0)
S_PAD = 0.42                         # the chest pad's middle, along the rail from its top end: the carriage at its
                                     # start puts the shoulder pads up by the placard (ref_02 / ref_05)
S_SH = S_PAD - 0.27 + 0.03           # the tops of the user's shoulders, under the shoulder pads
FEET = (1.24, 1.38, 1.52)            # shoulders to soles, down the slope, for the three foot plates
LK = (-0.02, 0.40)                   # the rear legs' knee
ZL = 0.62                            # the low beams and the cross tube


def P(s, h=0.0, y=0.0):
    """A point s down the upper rail from its top end, h out of the rail's centre line, at y."""
    return (A[0] + D1[0] * s + N1[0] * h, y, A[1] + D1[1] * s + N1[1] * h)


def x_rail(z):
    """The rail's centre line's x at height z."""
    return A[0] + (A[1] - z) / math.tan(RA) if z >= ZK else K[0] + (ZK - z) / math.tan(RB)


def build(k):
    tw = stack_tower.tower(k, TOWER, TC, 90.0)
    # ---- the rails: from the floor at the front up to the tower's face, a foot under each; the top end capped
    for sy in (1, -1):
        y = sy * YR
        b0 = (B[0] + math.cos(RB) * 0.05, y, -math.sin(RB) * 0.05)
        k.sweep("frame", [b0, (B[0], y, 0.0), (K[0], y, K[1]), (A[0], y, A[1])], k.rect(RD, RW, 0.008), bend=0.10,
                up=(0, 1, 0), cut0=((0, 0, FOOT_H), (0, 0, 1)), soft=0.002)
        k.cyl("rubber", (B[0] - FOOT_H / math.tan(RB), y, FOOT_H / 2), 0.055, FOOT_H, seg=28, soft=0.002)
        k.box("plastic", P(-0.004, 0.0, y), (0.012, RW + 0.004, RD + 0.004), ry=RA, soft=0.003)
        # the chrome rod on the rail's top face on its two blocks
        s0, s1 = 0.05, 1.10
        hr = RD / 2 + 0.024
        for s in (s0, s1):
            k.box("frame", P(s, RD / 2 + 0.015, y), (0.04, 0.05, 0.034), ry=RA, soft=0.003)
        k.tube("chrome", P(s0 - 0.02, hr, y), P(s1 + 0.02, hr, y), 0.0125, seg=20)
        # the tie at the top and the brace below it, back to the tower's face (ref_03 / ref_02)
        k.bar("frame", (X_FACE - 0.01, y, 1.30), (x_rail(1.30), y, 1.30), 0.06, 0.05)
        k.bar("frame", (X_FACE - 0.01, y, 0.92), (x_rail(1.18), y, 1.18), 0.06, 0.05, up=(0, 1, 0))
        # low down: the beam from the tower to the rail, the rear leg down from it to its foot (ref_03 / ref_04)
        k.bar("frame", (X_FACE - 0.01, y, ZL), (x_rail(ZL), y, ZL), 0.07, 0.06)
        xl = -0.14
        k.bar("frame", (xl, y, ZL + 0.02), (LK[0] + 0.01, y, LK[1] - 0.02), 0.06, 0.07, up=(0, 1, 0))
        k.bar("frame", (0.17, y, -0.03), (LK[0], y, LK[1] + 0.02), 0.06, 0.07, up=(0, 1, 0), cut0=((0, 0, FOOT_H), (0, 0, 1)))
        k.cyl("rubber", (0.17 - (FOOT_H + 0.03) * 0.19 / 0.43, y, FOOT_H / 2), 0.05, FOOT_H, seg=28, soft=0.002)
    # the cross tubes between the sides: under the carriage at the rails, at the rear legs' knee
    k.tube("frame", (x_rail(ZL), -YR, ZL), (x_rail(ZL), YR, ZL), 0.03, seg=24)
    k.tube("frame", (LK[0], -YR, LK[1] + 0.03), (LK[0], YR, LK[1] + 0.03), 0.03, seg=24)
    k.box("frame", (X_FACE - 0.015, 0.0, ZL), (0.03, 2 * YR, 0.04), soft=0.002)        # the tie across the tower's face
    # ---- the foot plates, laid out from the user: the body lies along the incline on the chest pad, the shoulders
    # under the shoulder pads, so the soles land 1.24 / 1.38 / 1.52 m down the slope from the shoulders (a short,
    # a middle, a tall user: the three start points). Each plate stands square to the body (its face up the slope,
    # to the head), out from the rails' top faces as far as the balls of the feet, its free edge clear so the heels
    # drop past it. Seen from the front only the plates' plain backs show, from the side their treads (ref_02 /
    # ref_03): a tray between the rails reaching back behind them and out past them, its corners rounded, a low rim
    # round its face, the rubber tread in it, a gusset under it to each rail
    # each lower plate stands 40 mm further out than the one above (ref_03), so the ball of the foot sits on an open
    # edge with the toes under the plate above, 0.11 m clear
    wp = 2 * YR - RW + 0.004
    for i, L in enumerate(FEET):
        s = S_SH + L
        h0, h1 = -0.10 + 0.04 * i, 0.20 + 0.04 * i
        k.box("frame", P(s + 0.015, (h0 + h1) / 2, 0.0), (0.03, wp, h1 - h0), ry=RA, soft=0.012)
        k.box("tread", P(s - 0.002, (h0 + h1) / 2, 0.0), (0.006, wp - 0.05, h1 - h0 - 0.05), ry=RA, soft=0.002)
        for j in range(6):                                                    # the tread's ribs
            k.box("rubber", P(s - 0.005, h0 + 0.05 + j * (h1 - h0 - 0.10) / 5, 0.0), (0.006, wp - 0.09, 0.012), ry=RA, soft=0.002)
        for hh in (h0 + 0.008, h1 - 0.008):                                   # the rim
            k.box("frame", P(s - 0.004, hh, 0.0), (0.014, wp, 0.016), ry=RA, soft=0.004)
        for sy in (1, -1):
            k.box("frame", P(s - 0.004, (h0 + h1) / 2, sy * (wp / 2 - 0.008)), (0.014, 0.016, h1 - h0), ry=RA, soft=0.004)
            k.box("frame", P(s + 0.06, 0.0, sy * (wp / 2 - 0.01)), (0.08, 0.012, 0.12), ry=RA, soft=0.002)
    # ---- the carriage: a linear bearing on each rod, the plate across them, the chest pad on it
    hb = RD / 2 + 0.024
    for sy in (1, -1):
        k.box("lever", P(S_PAD, hb, sy * YR), (0.42, 0.06, 0.05), ry=RA, soft=0.006)
    hp = hb + 0.035
    k.box("lever", P(S_PAD - 0.04, hp, 0.0), (0.60, 2 * YR + 0.04, 0.024), ry=RA, soft=0.003)
    tp = 0.10
    k.shaped_pad("pad", [(-0.25, -0.27), (0.25, -0.27), (0.25, 0.27), (-0.25, 0.27)], P(S_PAD, hp + 0.01 + tp / 2),
                 (N1[0], 0.0, N1[1]), (0, 1, 0), tp, r=0.05, cushion=0.03)
    # the shoulder pads at the chest pad's top, out of it, their faces down the slope to the shoulders; each on its
    # backing plate up from the carriage's top end (ref_02 / ref_05)
    st = S_PAD - 0.27                    # the chest pad's top end
    h0, h1 = hp - 0.01, hp + tp + 0.28
    for sy in (1, -1):
        y = sy * 0.11
        k.box("lever", P(st - 0.06, (h0 + h1) / 2, y), (0.02, 0.13, h1 - h0), ry=RA, soft=0.003)
        k.shaped_pad("pad", [(-0.07, -0.14), (0.07, -0.14), (0.07, 0.14), (-0.07, 0.14)],
                     P(st - 0.012, h1 - 0.145, y), (D1[0], 0.0, D1[1]), (0, 1, 0), 0.075, r=0.03, cushion=0.012)
    k.box("lever", P(st - 0.06, hp + 0.03, 0.0), (0.02, 0.36, 0.08), ry=RA, soft=0.003)     # the backing's cross plate
    # the pop pin out of the left bearing (ref_02): its chrome stem, the knob, the hose down along the rail
    pb = P(S_PAD - 0.17, hb, -YR - 0.03)
    k.tube("chrome", pb, (pb[0], -YR - 0.10, pb[2]), 0.006, seg=12)
    k.cyl("plastic", (pb[0], -YR - 0.11, pb[2]), 0.014, 0.03, axis="y", seg=20, soft=0.003)
    # ---- the cable: off the carriage's foot down the slope between the rails, round the pulley on the cross tube,
    # back along to the pulley at the tower's face and up inside the tower to its top pulley
    yc = 0.06
    p1 = (x_rail(ZL) - 0.04, yc, 0.70)
    h1c = (p1[0] - A[0]) * N1[0] + (p1[2] - A[1]) * N1[1] + 0.05          # the cable's height off the rail
    s1c = (p1[0] - A[0]) * D1[0] + (p1[2] - A[1]) * D1[1]
    p2 = (X_FACE - 0.045, yc, 0.70)
    for p, z0 in ((p1, ZL), (p2, ZL)):                                     # each pulley's side plate down to its tube
        k.box("frame", (p[0], yc + 0.02, (z0 + p[2]) / 2 + 0.01), (0.04, 0.02, p[2] - z0 + 0.02), soft=0.002)
        k.pulley(p, 0.05, axis="y")
    se = S_PAD + 0.24
    k.box("lever", P(se, (h1c + hp) / 2, yc), (0.03, 0.03, hp - h1c + 0.01), ry=RA, soft=0.002)   # the cable's eye
    k.cable([P(se, h1c, yc), P(s1c, h1c - 0.003, yc)])
    k.cable([(p1[0], yc, p1[2] - 0.047), (p2[0], yc, p2[2] - 0.047)])
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)
    k.cable([(p2[0] - 0.047, yc, p2[2]), (p2[0] - 0.047, yc, oz - 0.08), (out[0], out[1], oz - 0.02), out])

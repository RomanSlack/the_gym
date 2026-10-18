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
VIEWS = {"three_quarter": (27, 12, 1.12), "front": (0, 5, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (150, 18, 1.0)}
ORTHO = {"ortho_side": -90, "ortho_front": 0, "ortho_top": "top"}

# ---- the levers (one each side, in the plane x = s * LX), from the side view (ref_10, ~350 px/m) and front view (ref_08)
LX = 0.60                        # lever plane
PIV_Y, PIV_Z = 0.0, 0.86         # the knee pivot (the user's knee sits on its axis)
TILT = 27.0                      # at rest the lower arm leans forward of vertical (deg)
UP_L, LO_L = 0.50, 0.70          # lever lengths above / below the pivot
LEV = (0.05, 0.08)               # lever section: across (x) x along the swing (rectangular tube)
HORN_AT, HORN_L = 0.43, 0.30     # the weight horn: distance down the lower arm, length outwards
SHIN_AT = 0.29                   # the shin pad's rod: distance down the lower arm
SHIN = (0.28, 0.20, 0.075)       # shin pad: width (x), height, thickness
# ---- the pivot housings: two upright plates either side of the lever, a row of range-of-motion holes
PLATE_IN, PLATE_OUT = 0.47, 0.73  # their x
PLATE_Z = (0.60, 1.04)
PLATE_W = 0.15                   # along y
# ---- the frame
BX = 0.70                        # the side rails / A-frames (x)
BY0, BY1 = -0.47, 0.27           # main base: front and rear cross bars (y)
RX, RY = 0.24, 0.84              # the seat's rear legs (x) and their feet (y)
BOX = (0.076, 0.05)              # frame section (3 x 2 in)
# ---- seat + back pad (ref_10: the seat high and tilted back, the back pad long and leaning)
SEAT_F = (0.07, 0.82)            # the seat's front top edge (y, z)
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
    """One side: its A-frame tower, the pivot housing, the lever with its top cap, horn and shin pad."""
    t = math.radians(TILT)
    # the A-frame: two legs from the side rail up to the housing's foot, in the outer plate's plane
    apex = (s * BX, PIV_Y, PLATE_Z[0] + 0.01)
    for fy in (BY0 + 0.05, BY1 - 0.06):
        k.bar("frame", (s * BX, fy, 0.08), apex, BOX[1], BOX[0], up=(1, 0, 0))
    # the swoop: a bent tube from under the housing down and inwards to the middle of the base
    k.sweep("frame", [(s * (BX - 0.04), PIV_Y + 0.05, PLATE_Z[0]), (s * (BX - 0.10), PIV_Y + 0.05, 0.13), (s * 0.06, PIV_Y + 0.05, 0.11)],
            k.rect(BOX[0], BOX[1], 0.008), bend=0.16, up=(0, 1, 0))
    # the housing: outer + inner plates, a spacer block at the foot, the axle through, the ROM holes + pin knob
    for px in (PLATE_IN, PLATE_OUT):
        k.box("frame", (s * px, PIV_Y, (PLATE_Z[0] + PLATE_Z[1]) / 2), (0.014, PLATE_W, PLATE_Z[1] - PLATE_Z[0]), soft=0.004)
        for i in range(7):   # the range-of-motion holes, round the pivot
            a = math.radians(-60 + 20 * i)
            hy, hz = PIV_Y + 0.105 * math.sin(a) * 0.55, PIV_Z + 0.105 * math.cos(a) + 0.02
            k.cyl("hole", (s * (px + 0.0075 * (1 if px == PLATE_OUT else -1)), hy, hz), 0.009, 0.002, axis="x", seg=16)
        for by, bz in ((-0.05, PLATE_Z[0] + 0.04), (0.05, PLATE_Z[0] + 0.04), (-0.05, PLATE_Z[1] - 0.04), (0.05, PLATE_Z[1] - 0.04)):
            k.cyl("bolt", (s * (px + 0.009 * (1 if px == PLATE_OUT else -1)), PIV_Y + by, bz), 0.011, 0.008, axis="x", seg=6)
    k.box("frame", (s * (PLATE_IN + PLATE_OUT) / 2, PIV_Y, PLATE_Z[0] + 0.04), (PLATE_OUT - PLATE_IN, PLATE_W, 0.08), soft=0.004)
    k.box("warn", (s * (PLATE_OUT + 0.008), PIV_Y - 0.03, PLATE_Z[0] + 0.13), (0.002, 0.045, 0.04), soft=0.0)
    k.tube("steel", (s * (PLATE_IN - 0.02), PIV_Y, PIV_Z), (s * (PLATE_OUT + 0.025), PIV_Y, PIV_Z), 0.022)
    k.cyl("lever", (s * (PLATE_OUT + 0.03), PIV_Y, PIV_Z), 0.034, 0.012, axis="x", seg=24)            # axle cap
    k.sweep("lever", [(s * (PLATE_OUT + 0.01), PIV_Y - 0.02, PIV_Z + 0.12), (s * (PLATE_OUT + 0.07), PIV_Y - 0.02, PIV_Z + 0.12)],
            k.circle(0.006), soft=0.0)                                                                       # the pop-pin
    k.cyl("lever", (s * (PLATE_OUT + 0.08), PIV_Y - 0.02, PIV_Z + 0.12), 0.022, 0.03, axis="x", seg=24, soft=0.008)
    # the start-position T-handle across the housing's top, out past the outer plate (front view)
    hz = PLATE_Z[1] - 0.05
    k.tube("steel", (s * (PLATE_IN - 0.03), PIV_Y - 0.04, hz), (s * (PLATE_OUT + 0.22), PIV_Y - 0.04, hz), 0.011)
    k.tube("rubber", (s * (PLATE_OUT + 0.12), PIV_Y - 0.04, hz), (s * (PLATE_OUT + 0.23), PIV_Y - 0.04, hz), 0.016)
    # the lever: a rectangular tube through the pivot, a square cap at the top, the hub block at the pivot
    top, bot = on_lever(s, -UP_L), on_lever(s, LO_L)
    k.sweep("lever", [top, bot], k.rect(LEV[0], LEV[1], 0.006), up=(0, math.cos(t), -math.sin(t)), soft=0.003)
    k.box("lever", lerp(top, bot, 0.0), (0.10, 0.13, 0.10), rx=-t, soft=0.01)                            # the top cap
    k.box("lever", (s * LX, PIV_Y, PIV_Z), (0.075, 0.12, 0.14), rx=-t, soft=0.006)                     # the hub block
    # the weight horn outwards (a collar, the sleeve, its end cap) and its gusset on the lever
    h0 = on_lever(s, HORN_AT)
    k.box("lever", (h0[0] + s * 0.04, h0[1], h0[2]), (0.04, 0.09, 0.09), rx=-t, soft=0.006)
    k.cyl("lever", (h0[0] + s * 0.075, h0[1], h0[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (h0[0] + s * 0.08, h0[1], h0[2]), (h0[0] + s * HORN_L, h0[1], h0[2]), 0.025, seg=32)
    k.cyl("lever", (h0[0] + s * (HORN_L + 0.008), h0[1], h0[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the shin pad: a rod inwards from the lever (with its adjust collar), the pad facing the shins (+y)
    r0 = on_lever(s, SHIN_AT)
    pad_x0, pad_x1 = s * 0.07, s * (0.07 + SHIN[0])
    k.box("lever", (r0[0] - s * 0.04, r0[1], r0[2]), (0.06, 0.07, 0.07), soft=0.006)                    # the collar
    k.tube("lever", (r0[0] - s * 0.06, r0[1], r0[2]), ((pad_x0 + pad_x1) / 2, r0[1], r0[2]), 0.016)
    pc = ((pad_x0 + pad_x1) / 2, r0[1] + 0.03 + SHIN[2] / 2, r0[2])
    k.box("lever", (pc[0], r0[1] + 0.022, pc[2]), (SHIN[0] - 0.04, 0.012, SHIN[1] - 0.04), soft=0.003)   # its back plate
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
    fr = (0.0, fy + 0.04, fz - SEAT_T - 0.05)
    k.tube("frame", (-SEAT_W / 2 + 0.03, fr[1], fr[2]), (SEAT_W / 2 - 0.03, fr[1], fr[2]), 0.02)        # the tube across under its front
    # the seat post: from the centre rail up under the seat's middle
    k.bar("frame", (0.0, under[1], BOX[1]), (0.0, under[1], under[2] - 0.02), 0.08, 0.08)
    # the back pad: a lumbar section at the seat's rear, the long main pad, both leaning BACK_LEAN
    rear_top = (0.0, fy + along[1] * SEAT_L, fz + along[2] * SEAT_L)
    b = math.radians(BACK_LEAN)
    upv = (0.0, math.sin(b), math.cos(b)); bn = (0.0, -math.cos(b), math.sin(b))   # up the pad, its face (towards the user)
    p0 = (0.0, rear_top[1] + 0.02, rear_top[2] + 0.02)
    for d0, d1 in ((0.0, 0.17), (0.18, BACK_L)):
        mid = (d0 + d1) / 2
        pc = (0.0, p0[1] + upv[1] * mid - bn[1] * BACK_T / 2, p0[2] + upv[2] * mid - bn[2] * BACK_T / 2)
        L = d1 - d0
        k.shaped_pad("pad", [(-BACK_W / 2, -L / 2), (BACK_W / 2, -L / 2), (BACK_W / 2, L / 2), (-BACK_W / 2, L / 2)],
                     pc, bn, (1, 0, 0), BACK_T, r=0.05, cushion=0.03)
    # its frame: a spine plate behind the pad, two rear legs (an A each side) carrying it and the seat's rear, the grips
    sp0 = (0.0, p0[1] - bn[1] * (BACK_T + 0.02), p0[2] - bn[2] * (BACK_T + 0.02))
    sp1 = (0.0, sp0[1] + upv[1] * BACK_L * 0.8, sp0[2] + upv[2] * BACK_L * 0.8)
    k.bar("frame", sp0, sp1, 0.08, 0.04, up=bn)
    for s in (1, -1):
        top = (s * RX, rear_top[1] + 0.06, rear_top[2] - 0.08)
        k.bar("frame", (s * RX, RY - 0.02, BOX[1]), top, BOX[1], BOX[0], up=(1, 0, 0))                  # the rear leg
        k.bar("frame", (s * RX, BY1 + 0.12, BOX[1]), lerp((s * RX, RY - 0.02, BOX[1]), top, 0.75), BOX[1], BOX[0], up=(1, 0, 0))  # its strut
        k.bar("frame", top, (0.0, top[1], top[2]), BOX[0], BOX[1])                                         # across to the spine
        g0 = (s * (RX + 0.03), top[1], top[2] + 0.01)
        k.sweep("frame", [(s * RX, top[1], top[2]), g0, (s * (SEAT_W / 2 + 0.05), top[1] - 0.25, top[2] + 0.03)], k.circle(0.016), bend=0.04)
        k.tube("rubber", lerp(g0, (s * (SEAT_W / 2 + 0.05), top[1] - 0.25, top[2] + 0.03), 0.35),
               (s * (SEAT_W / 2 + 0.05), top[1] - 0.25, top[2] + 0.03), 0.02)                                # the hand grip

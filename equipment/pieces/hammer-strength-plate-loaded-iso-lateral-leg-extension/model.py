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
ORTHO = {"ortho_side": -90, "ortho_front": 0, "ortho_top": "top"}

# ---- each side (mirror images, s = +1 / -1), from the side view (ref_10, ~350 px/m), the front view (ref_08) and the
# close-ups (ref_12, ref_04): a square UPRIGHT rises from the A-frame's apex with the axle through its top; the lever's two
# black ROM plates (rows of start-position holes) turn round it, one each side; the lever bar is fixed to the outer plate
UX = 0.60                        # the upright (x)
UPRIGHT = 0.08                   # 3 x 3 in
PIV_Y, PIV_Z = 0.0, 0.86         # the knee pivot (the user's knee sits on its axis)
LX = UX + 0.075                  # the lever bar, just outside the upright (front view: out from the upright's centre)
ROM_X = (-0.065, 0.16)           # the two black ROM blocks: hard against the upright's inner face, and outside the lever
ROM = (0.05, 0.11, 0.62, 1.06)   # their section (x, y) and height (z from, to): upright boxes with two rows of holes
TILT = 27.0                      # at rest the lower arm leans forward of vertical (deg)
UP_L, LO_L = 0.42, 0.70          # lever lengths above / below the pivot
LEV = (0.05, 0.10)               # lever section: across (x) x along the swing (2 x 4 in)
HORN_AT, HORN_L = 0.36, 0.26     # the weight horn: distance down the lower arm, length outwards
SHIN_AT = 0.25                   # the shin pad's rod: distance down the lower arm
SHIN = (0.28, 0.20, 0.075)       # shin pad: width (x), height, thickness
# ---- the frame
BX = UX                          # the side rails under the A-frames (x)
BY0, BY1 = -0.47, 0.27           # main base: front and rear cross bars (y)
APEX_Z = 0.52                    # where the A-frame's legs meet the upright
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
    """One side: the A-frame and its upright, the lever with its ROM plates, top cap, horn and shin pad."""
    t = math.radians(TILT)
    ux = s * UX
    # the A-frame: two legs from the side rail up to the upright's foot, the swoop from it down and inwards to the middle
    for fy in (BY0 + 0.06, BY1 - 0.04):
        k.bar("frame", (ux, fy, BOX[1]), (ux, PIV_Y, APEX_Z + 0.03), LEG[0], LEG[1], up=(1, 0, 0))
    k.box("frame", (ux, PIV_Y, APEX_Z), (UPRIGHT + 0.01, 0.16, 0.08), soft=0.004)                       # the gusset where they meet
    k.sweep("frame", [(ux, PIV_Y + 0.07, APEX_Z), (s * (UX - 0.06), PIV_Y + 0.07, 0.13), (s * 0.05, PIV_Y + 0.07, 0.10)],
            k.rect(LEG[0], LEG[1], 0.008), bend=0.17, up=(0, 1, 0))
    # the upright: up from the apex past the pivot, a cap, the axle bolt; a warning label
    k.bar("frame", (ux, PIV_Y, APEX_Z), (ux, PIV_Y, PIV_Z + 0.09), UPRIGHT, UPRIGHT, up=(0, 1, 0))
    k.box("frame", (ux, PIV_Y, PIV_Z + 0.095), (UPRIGHT + 0.006, UPRIGHT + 0.006, 0.012), soft=0.003)
    k.box("warn", (ux + s * (UPRIGHT / 2 + 0.001), PIV_Y + 0.0, APEX_Z + 0.14), (0.002, 0.05, 0.045), soft=0.0)
    k.tube("steel", (s * (UX + ROM_X[0] - 0.04), PIV_Y, PIV_Z), (s * (UX + ROM_X[1] + 0.04), PIV_Y, PIV_Z), 0.019)
    k.cyl("bolt", (s * (UX + ROM_X[1] + 0.045), PIV_Y, PIV_Z), 0.03, 0.016, axis="x", seg=6)            # the axle nut
    # the ROM blocks: upright black boxes, the axle through both, two rows of start-position holes on their fronts
    for dx in ROM_X:
        bx = s * (UX + dx)
        k.box("lever", (bx, PIV_Y, (ROM[2] + ROM[3]) / 2), (ROM[0], ROM[1], ROM[3] - ROM[2]), soft=0.004)
        for i in range(9):   # the holes on their fronts
            zz = ROM[2] + 0.05 + i * (ROM[3] - ROM[2] - 0.10) / 8
            if abs(zz - PIV_Z) > 0.04:
                k.cyl("hole", (bx, PIV_Y - ROM[1] / 2 - 0.0005, zz), 0.0085, 0.002, axis="y", seg=14)
        for zz in (ROM[2] + 0.03, ROM[3] - 0.03):
            k.cyl("bolt", (bx + s * (ROM[0] / 2 + 0.003), PIV_Y + 0.03, zz), 0.011, 0.007, axis="x", seg=6)
        for i in range(9):   # the holes, also on the outer faces (ref_12)
            zz = ROM[2] + 0.05 + i * (ROM[3] - ROM[2] - 0.10) / 8
            if abs(zz - PIV_Z) > 0.04:
                k.cyl("hole", (bx + s * (ROM[0] / 2 + 0.0005), PIV_Y - 0.025, zz), 0.0085, 0.002, axis="x", seg=14)
                k.cyl("hole", (bx + s * (ROM[0] / 2 + 0.0005), PIV_Y + 0.025, zz), 0.0085, 0.002, axis="x", seg=14)
    # the start-position T-handle (its pin through the plates into the upright), out past the lever
    hz_ = PIV_Z + 0.16
    k.tube("steel", (s * (UX + ROM_X[0] - 0.02), PIV_Y - 0.075, hz_), (s * (UX + ROM_X[1] + 0.19), PIV_Y - 0.075, hz_), 0.011)
    k.tube("rubber", (s * (UX + ROM_X[1] + 0.08), PIV_Y - 0.075, hz_), (s * (UX + ROM_X[1] + 0.20), PIV_Y - 0.075, hz_), 0.016)
    # the lever: a 2 x 4 in bar on the outer plate, through the pivot; the square top cap; bolts into the plate
    top, bot = on_lever(s, -UP_L), on_lever(s, LO_L)
    k.sweep("lever", [top, bot], k.rect(LEV[0], LEV[1], 0.006), up=(0, math.cos(t), -math.sin(t)), soft=0.003)
    k.box("lever", top, (0.10, 0.13, 0.11), rx=-t, soft=0.01)                                            # the top cap
    for d in (-0.12, 0.12, 0.24):
        q = on_lever(s, d)
        k.cyl("bolt", (q[0] + s * (LEV[0] / 2 + 0.003), q[1], q[2]), 0.011, 0.006, axis="x", seg=6)
    # the weight horn outwards (a collar, the sleeve, its end cap) and its gusset on the lever
    h0 = on_lever(s, HORN_AT)
    k.box("lever", (h0[0] + s * 0.04, h0[1], h0[2]), (0.04, 0.10, 0.10), rx=-t, soft=0.006)
    k.cyl("lever", (h0[0] + s * 0.075, h0[1], h0[2]), 0.05, 0.02, axis="x", seg=32, soft=0.004)
    k.tube("steel", (h0[0] + s * 0.08, h0[1], h0[2]), (h0[0] + s * HORN_L, h0[1], h0[2]), 0.025, seg=32)
    k.cyl("lever", (h0[0] + s * (HORN_L + 0.008), h0[1], h0[2]), 0.029, 0.018, axis="x", seg=32, soft=0.005)
    # the shin pad: a rod inwards from the lever's inner face (its adjust collar), the pad facing the shins (+y)
    r0 = on_lever(s, SHIN_AT)
    pad_x0, pad_x1 = s * 0.07, s * (0.07 + SHIN[0])
    k.box("lever", (r0[0] - s * 0.045, r0[1], r0[2]), (0.04, 0.075, 0.075), soft=0.006)                 # the collar
    k.tube("lever", (r0[0] - s * 0.06, r0[1], r0[2]), ((pad_x0 + pad_x1) / 2, r0[1], r0[2]), 0.017)
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
    # the swoops meet in a block on the centre rail; the seat's slim post stands on the rail under the seat's middle
    k.box("frame", (0.0, PIV_Y + 0.07, 0.10), (0.14, 0.11, 0.09), soft=0.005)
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

"""Rogue Manta Ray Adjustable Bench (textured foam pads), set flat as in ref_02.

Built by eye from Rogue's gallery (refs/: ref_02 the flat three-quarter, ref_03 a true side view at an incline, ref_01
the incline three-quarter + the UHMW core close-up), held to Rogue's spec: 57 x 24.75 x 17.5 in, pads 52 in overall
with a 1 in gap, 12 in wide, 2.25 in thick, frame 3 x 4 in 7-gauge steel.
Axes: metres, floor z = 0, the bench runs along x: the seat, front leg and front foot plate at -x, the rear foot with
its wheels at +x.
Structure (ref_02, ref_03): a 3 x 4 in spine from the rear foot rising forwards into the front leg; a long window in
each side of the spine shows the machined UHMW core whose notches take the back's rod; the front leg (its own window +
notches for the seat) stands on a bolted foot plate with a carry handle; the seat on side plates with the R cut out;
the back pad on a frame hinged at the spine's front end, side plates with ROGUE cut out; two flat arms from under the
back down to the rod, its knobs out each side; a post at the rear the flat back rests on; wheels behind the rear foot.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.016, 0.016, 0.017), rough=0.45, metal=0.1, coat=0.05, bump=(1400, 0.06)),   # black satin powder coat
    "pad": dict(color=(0.030, 0.030, 0.032), rough=0.8, sheen=0.05, bump=(2600, 0.35)),              # textured foam
    "emboss": dict(color=(0.024, 0.024, 0.025), rough=0.55, bump=(2600, 0.1)),
    "plastic": dict(color=(0.012, 0.012, 0.013), rough=0.7),
    "cap": dict(color=(0.010, 0.010, 0.011), rough=0.22, coat=0.3),
    "hole": dict(color=(0.003, 0.003, 0.003), rough=0.9),                                             # cut-outs, windows
    "uhmw": dict(color=(0.22, 0.22, 0.215), rough=0.55),                                              # the machined core
    "etch": dict(color=(0.5, 0.5, 0.5), rough=0.6),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, bump=(700, 0.15)),
    "bolt": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-30, 14, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_core": ((0.3, -0.7, 0.4), (0.26, 0.0, 0.2), 40),           # the spine's window, the UHMW core, the rod
    "detail_front": ((-1.0, -0.55, 0.42), (-0.56, 0.0, 0.2), 40),      # the front leg, the R plate, the foot + handle
    "detail_rear": ((1.1, -0.6, 0.35), (0.58, 0.0, 0.15), 40),          # the rear foot, wheels, the post
}

SPINE = (3 * IN, 4 * IN)        # spine: across (y) x tall
PAD_T, PAD_W, PAD_TOP = 2.25 * IN, 12 * IN, 17.5 * IN
SEAT = (-0.72, -0.385)          # seat pad (x from / to)
BACK = (-0.36, 0.60)            # back pad
REAR_X = 0.60                   # rear foot centre (x)
REAR = (4 * IN, 3 * IN)         # rear foot: along x, tall
REAR_W = 24.75 * IN
NODE = (-0.42, 0.27)            # where the spine's centreline meets the front leg's
LEG_BOT = (-0.58, 0.012)        # the front leg's foot (on the plate)
LEG = (4 * IN, 3 * IN)          # front leg: along its slope, across
HINGE = (-0.35, None)           # the back's hinge (x); z = the back frame's centre
ARM_AT = 0.08                   # the arms hang from under the back frame here (x)
ROD_X = 0.44                    # the notch the rod sits in for flat (x)
POST_X = 0.52                   # the rear post (x)
WIN = (0.0, 0.48)               # the spine's window (x)


def spine_z(x):
    """The spine's centreline: resting on the rear foot, rising to the node at the front leg."""
    z0 = REAR[1] + 0.002 + SPINE[1] / 2
    return z0 + (REAR_X - x) * (NODE[1] - z0) / (REAR_X - NODE[0])


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    sl = math.atan((NODE[1] - spine_z(REAR_X)) / (REAR_X - NODE[0]))   # the spine's rise (rad), forwards
    up = (math.sin(sl), 0.0, math.cos(sl))                              # perpendicular to the spine, upwards
    hs = SPINE[0] / 2
    # ---- the rear foot: 4 x 3 in across, gloss caps printed ROGUE, two wheels behind it on brackets
    body = REAR_W / 2 - 0.002
    k.bar("frame", (REAR_X, -body, 0.002 + REAR[1] / 2), (REAR_X, body, 0.002 + REAR[1] / 2), REAR[0], REAR[1], up=Z)
    for d in (1, -1):
        k.box("cap", (REAR_X, d * (REAR_W / 2 - 0.012), 0.002 + REAR[1] / 2), (REAR[0] + 0.004, 0.024, REAR[1] + 0.004), soft=0.004)
        k.text("etch", "ROGUE", (REAR_X, d * (REAR_W / 2 + 0.0006), 0.04), 0.014, rz=(0 if d < 0 else math.pi), depth=0.0005)
        wy = d * (REAR_W / 2 - 0.08)
        k.box("frame", (REAR_X + REAR[0] / 2 + 0.02, wy, 0.045), (0.04, 0.05, 0.05), soft=0.003)          # wheel bracket
        k.cyl("rubber", (REAR_X + REAR[0] / 2 + 0.04, wy, 0.038), 0.033, 0.03, axis="y", seg=32, soft=0.004)
        k.cyl("cap", (REAR_X + REAR[0] / 2 + 0.04, wy - d * 0.017, 0.038), 0.014, 0.004, axis="y", seg=20)
    # ---- the spine: sitting on the rear foot (capped past it), rising into the front leg
    leg_d = (NODE[0] - LEG_BOT[0], 0, NODE[1] - LEG_BOT[1]); n_ = math.hypot(leg_d[0], leg_d[2])
    leg_d = (leg_d[0] / n_, 0, leg_d[2] / n_)
    leg_rear = (leg_d[2], 0, -leg_d[0])                                  # the leg's face towards the rear (normal)
    lp = (NODE[0] + leg_rear[0] * LEG[0] / 2, 0, NODE[1] + leg_rear[2] * LEG[0] / 2)
    xe = REAR_X + REAR[0] / 2
    k.bar("frame", (xe, 0, spine_z(xe)), (NODE[0], 0, NODE[1]), SPINE[1], SPINE[0], up=Y, cut1=(lp, leg_rear), weld=True)
    k.box("cap", (xe + 0.004, 0, spine_z(xe)), (0.008, SPINE[0] + 0.004, SPINE[1] + 0.004), ry=sl, soft=0.003)
    # its windows: a dark slot each side with the UHMW core's notches along its bottom (ref_01's close-up)
    xm, L = (WIN[0] + WIN[1]) / 2, WIN[1] - WIN[0]
    for s in (1, -1):
        yf = s * (hs + 0.0006)
        k.box("hole", (xm, yf, spine_z(xm) + 0.004), (L, 0.001, 0.05), ry=sl, soft=0.0)
        for j in range(9):
            tx = WIN[0] + 0.03 + j * (L - 0.06) / 8
            k.box("uhmw", (tx, s * (hs + 0.0011), spine_z(tx) - 0.012), (0.035, 0.001, 0.018), ry=sl, soft=0.0)
        for bx in (WIN[0] - 0.03, WIN[1] + 0.03):
            k.bolt((bx, s * hs, spine_z(bx)), "+y" if s > 0 else "-y", size=0.012, nut=SPINE[0])
    # the rod in its notch, through the spine, knobs out each side
    rz_ = spine_z(ROD_X) - 0.004
    k.tube("steel", (ROD_X, -(hs + 0.05), rz_), (ROD_X, hs + 0.05, rz_), 0.0127)
    for s in (1, -1):
        k.cyl("cap", (ROD_X, s * (hs + 0.065), rz_), 0.022, 0.035, axis="y", seg=28, soft=0.006)
    # ---- the front leg: on its foot plate, rising back to the node and on up under the seat; its own window
    plate_t = 0.010
    k.box("rubber", (LEG_BOT[0] - 0.02, 0, 0.001), (0.22, 0.30, 0.002), soft=0.0)
    k.box("frame", (LEG_BOT[0] - 0.02, 0, 0.002 + plate_t / 2), (0.22, 0.30, plate_t), soft=0.002)
    for dx in (-0.1, 0.06):
        for dy in (-0.12, 0.12):
            k.cyl("bolt", (LEG_BOT[0] - 0.02 + dx, dy, 0.012 + 0.002), 0.008, 0.004, seg=6)
    zf = 0.002 + plate_t
    top = (NODE[0] + leg_d[0] * 0.08, 0, NODE[1] + leg_d[2] * 0.08)      # the leg runs on past the node to the seat
    k.bar("frame", (LEG_BOT[0], 0, zf), top, LEG[0], LEG[1], up=Y, cut0=((0, 0, zf), Z), cut1=((0, 0, top[2]), Z), weld=True)
    la = math.atan2(leg_d[0], leg_d[2])                                  # its lean from vertical
    lm = (LEG_BOT[0] + leg_d[0] * 0.13, LEG_BOT[1] + leg_d[2] * 0.13)
    k.box("hole", (lm[0], -(LEG[1] / 2 + 0.0006), zf + leg_d[2] * 0.13), (0.035, 0.001, 0.16), ry=la, soft=0.0)
    ln = (leg_d[2], 0, -leg_d[0])                                       # across the leg's face, towards the rear

    def on_leg(q, off):
        return (LEG_BOT[0] + leg_d[0] * q + ln[0] * off, -(LEG[1] / 2 + 0.0011), zf + leg_d[2] * q + ln[2] * off)
    for j in range(4):
        k.box("uhmw", on_leg(0.07 + j * 0.04, 0.008), (0.012, 0.001, 0.022), ry=la, soft=0.0)
    for t_, q in (("0", 0.215), ("-20", 0.05)):
        c_ = on_leg(q, -0.03)
        k.text("etch", t_, (c_[0], -(LEG[1] / 2 + 0.0006), c_[2]), 0.016, depth=0.0005)
    # the carry handle: a stem forwards off the plate, a bar across with grips
    hx = LEG_BOT[0] - 0.13 - 0.025
    k.bar("frame", (LEG_BOT[0] - 0.13, 0, 0.027), (hx, 0, 0.027), 0.03, 0.03, up=Z)
    k.box("frame", (LEG_BOT[0] - 0.13 + 0.005, 0, 0.0215), (0.01, 0.04, 0.019), soft=0.001)
    k.tube("frame", (hx, -0.13, 0.03), (hx, 0.13, 0.03), 0.016)
    for s in (1, -1):
        k.tube("rubber", (hx, s * 0.05, 0.03), (hx, s * 0.135, 0.03), 0.019, seg=24)
    # ---- the seat: side plates welded to the leg's top (the R cut out of the outer one), a mount plate, the pad
    sb = PAD_TOP - PAD_T                                                  # the pads' bottoms
    sc = (SEAT[0] + SEAT[1]) / 2
    for s in (1, -1):
        k.box("frame", (top[0] - 0.03, s * (LEG[1] / 2 + 0.004), (top[2] - 0.08 + sb - 0.01) / 2), (0.20, 0.008, sb - 0.01 - top[2] + 0.08), soft=0.002)
    k.box("frame", (sc + 0.02, 0, sb - 0.005), (0.26, 0.20, 0.01), soft=0.002)
    k.box("hole", (top[0] - 0.07, -(LEG[1] / 2 + 0.0085), sb - 0.06), (0.05, 0.001, 0.06), soft=0.0)
    k.text("frame", "R", (top[0] - 0.07, -(LEG[1] / 2 + 0.009), sb - 0.06), 0.05, depth=0.001)
    k.bolt((top[0] + 0.04, -(LEG[1] / 2 + 0.008), sb - 0.04), "-y", size=0.014, nut=LEG[1] + 0.016)
    # the seat's pull pin: a rod through the leg's side plates, a knob out the near side
    pz = sb - 0.14
    k.tube("steel", (top[0] - 0.02, LEG[1] / 2 + 0.01, pz), (top[0] - 0.02, -(LEG[1] / 2 + 0.11), pz), 0.0105)
    k.cyl("cap", (top[0] - 0.02, -(LEG[1] / 2 + 0.12), pz), 0.02, 0.03, axis="y", seg=28, soft=0.005)
    k.box("frame", (top[0] - 0.02, -(LEG[1] / 2 + 0.004), pz), (0.05, 0.008, 0.05), soft=0.002)
    pad(k, SEAT, sb)
    # ---- the back: hinge plates on the spine's front end, a 2 x 3 in frame on a hub between them, the pad on it
    fh = 2 * IN
    fz = sb - fh / 2                                                      # the back frame's centreline
    hx_ = HINGE[0]
    stop = spine_z(hx_) + SPINE[1] / 2 / math.cos(sl)
    for s in (1, -1):
        k.box("frame", (hx_, s * (hs + 0.005), (stop - 0.01 + fz + 0.03) / 2), (0.09, 0.01, fz + 0.04 - stop), soft=0.002)
        k.bolt((hx_, s * (hs + 0.01), fz), "+y" if s > 0 else "-y", size=0.018)
    k.tube("frame", (hx_, -hs, fz), (hx_, hs, fz), 0.026, seg=28)
    k.bar("frame", (hx_ + 0.01, 0, fz), (BACK[1] - 0.03, 0, fz), fh, SPINE[0], up=Y)
    k.box("cap", (BACK[1] - 0.026, 0, fz), (0.008, SPINE[0] + 0.004, fh + 0.004), soft=0.003)
    # its side plates (ROGUE cut out of each), bolted through the frame
    for s in (1, -1):
        yp = s * (hs + 0.003)
        k.box("frame", (-0.205, yp, fz - 0.008), (0.25, 0.006, fh + 0.016), soft=0.002)
        k.box("hole", (-0.20, s * (hs + 0.0062), fz - 0.008), (0.16, 0.001, 0.03), soft=0.0)
        k.text("frame", "ROGUE", (-0.20, s * (hs + 0.0066), fz - 0.008), 0.03, rz=(0 if s < 0 else math.pi), depth=0.0008)
        k.bolt((-0.07, s * (hs + 0.006), fz), "+y" if s > 0 else "-y", size=0.012, nut=SPINE[0] + 0.012)
    pad(k, BACK, sb)
    k.text("emboss", "ROGUE", (BACK[1] - 0.07, 0.0, PAD_TOP - 0.0003), 0.042, rz=math.pi / 2, rx=0.0, depth=0.0016)
    # the arms: a hub under the back frame, a flat bar down each side to the rod
    az = fz - fh / 2 - 0.024
    k.tube("frame", (ARM_AT, -(hs + 0.025), az), (ARM_AT, hs + 0.025, az), 0.024, seg=24)
    k.box("frame", (ARM_AT, 0, fz - fh / 2 - 0.006), (0.05, SPINE[0], 0.012), soft=0.002)
    for s in (1, -1):
        k.bar("frame", (ARM_AT, s * (hs + 0.015), az), (ROD_X, s * (hs + 0.015), rz_), 0.045, 0.012, up=Y)
        k.cyl("bolt", (ROD_X, s * (hs + 0.023), rz_), 0.014, 0.006, axis="y", seg=6)
    # ---- the rear post: welded on the spine's top, a rubber bumper the flat back rests on
    pz0 = spine_z(POST_X) + SPINE[1] / 2 / math.cos(sl)
    ptop = fz - fh / 2 - 0.03
    k.bar("frame", (POST_X, 0, pz0 - 0.01), (POST_X, 0, ptop), 3 * IN, 3 * IN, up=Y, cut0=((POST_X, 0, pz0), up), weld=True)
    k.box("rubber", (POST_X, 0, ptop + 0.015), (0.08, 0.08, 0.03), soft=0.006)


def pad(k, span, bottom):
    """A moulded textured foam pad on its plywood board: no stitching, rounded edges (ref_01's close-up)."""
    x0, x1 = span
    L = x1 - x0
    k.shaped_pad("pad", [(-L / 2, -PAD_W / 2), (L / 2, -PAD_W / 2), (L / 2, PAD_W / 2), (-L / 2, PAD_W / 2)],
                 ((x0 + x1) / 2, 0, bottom + PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.012, seam=False)

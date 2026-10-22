"""Life Fitness Axiom Series Leg Curl (prone), Charcoal frame / Black upholstery, the lever at its start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway and ref_02 the same shot in
Platinum (its silver frame reads the tubes and joints the black hides); no used unit photographed all round could be
found (2026-10-22), so the hidden sides follow the visible ones. Held to Life Fitness's 65 x 43 x 53 in
(165 x 109 x 135 cm, L x W x H), the stack 202.5 lb.
Axes: metres, floor z = 0, the user lies face down along x, the head at -x, the knees at the lever's pivot, the feet
under the rollers at +x; the bench's centre line at y = BY, the tower behind it (+y), its face (-y) to the bench.
Structure: the Axiom stack tower (shared builder, "axiom" style); the base: the floor tube along the bench from the
head end's foot to the knee end's foot, a tube back from it to the tower's foot; the head end's post up (leaning out)
to the spine; the spine rising from it under the chest pad to the hip, then on under the thigh pad, a little down, to
the knuckle under the knee; the knee end's leg slanting from its foot up into the spine, the cable's pulley on it; the
chest pad long and sloping down to the head, the thigh pad higher, sloping down to the knee (the diverging hip and
chest angles), a chamfer at its knee end; the two U handles off the head end's post; the lever: two plates up from
the knuckle to the pivot, the hub between them, the cam on the front with its bolted plate, the arm out level to the
rollers (its lower tube sliding in it, the yellow pop pin under it), the two ankle rollers either side of its end;
the cable from the cam to the pulley on the knee end's leg, on to the tower's foot and in.
"""
import math

import stack_tower

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.05, 0.052, 0.056), rough=0.38, metal=0.45, coat=0.15, bump=(1400, 0.05)),  # Charcoal
    "lever": dict(color=(0.03, 0.031, 0.033), rough=0.4, metal=0.35, coat=0.12, bump=(1400, 0.06)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.14, 0.012, 0.01), rough=0.6, coat=0.0),                                        # the red piping
    "plate": dict(color=(0.04, 0.04, 0.042), rough=0.45, metal=0.3, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "cam": dict(color=(0.02, 0.02, 0.021), rough=0.35, metal=0.3, coat=0.1),
    "shroud": dict(color=(0.012, 0.012, 0.013), rough=0.25, coat=0.6),                                  # the cap
    "shroud2": dict(color=(0.018, 0.018, 0.02), rough=0.4, metal=0.1, coat=0.25),                       # the black panels
    "ink2": dict(color=(0.16, 0.165, 0.175), rough=0.4, coat=0.1),                                      # the grey strip
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "yellow": dict(color=(0.95, 0.55, 0.02), rough=0.4, coat=0.1),
    "warn": dict(color=(0.95, 0.55, 0.02), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (18, 7, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (-140, 16, 1.0)}
DETAILS = {
    "detail_lever": ((1.35, -1.10, 1.05), (0.50, -0.20, 0.55), 45),    # the knuckle, the cam, the arm, the rollers
    "detail_tower": ((0.45, -1.30, 1.35), (-0.10, 0.20, 1.05), 40),    # the tower's face: the placard band, the slot
}

TOWER = dict(style="axiom", W=0.52, D=0.40, H=53 * IN, n=13, plate=(0.30, 0.14, 0.0254), rods=0.22,
             title="LEG CURL", brand="LifeFitness", step=15, start=0, pin_at=4)
TC = (-0.10, 0.40)                   # the tower: behind the bench, its face 0.2 m behind the pads' back edge
FOOT_H = 0.015
BY = -0.20                           # the bench's centre line
R = 0.036                            # the round frame tubes
X_HEAD, X_KNEE = -0.66, 0.40         # the feet: under the head end's post, under the knee end's leg
POST_TOP = (-0.70, 0.33)             # the head end's post top (x, z): it leans out going up (ref_02)
HIP = (-0.04, 0.47)                  # the spine's peak, under the pads' joint
KNUCKLE = (0.38, 0.44)               # its end under the knee
PIV = (0.46, 0.53)                   # the lever's pivot (x, z), the axle along y
ROLL = (0.80, 0.55)                  # the rollers' axle at the start: the legs out straight
Z, X, Y = (0, 0, 1), (1, 0, 0), (0, 1, 0)


def foot(k, x, y, sx=0.10, sy=0.26):
    k.box("rubber", (x, y, FOOT_H / 2), (sx, sy, FOOT_H), soft=0.003)


def on_spine(x):
    """The spine's centre height at x."""
    (x0, z0), (x1, z1), (x2, z2) = POST_TOP, HIP, KNUCKLE
    if x <= x1:
        return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return z1 + (z2 - z1) * (x - x1) / (x2 - x1)


def build(k):
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    yf = TC[1] - TOWER["D"] / 2                        # the tower's face
    zt = FOOT_H + R                                    # the floor tubes' centre
    # ---- the base: the feet, the floor tube between them, the tube back to the tower's foot with its plate
    foot(k, X_HEAD, BY)
    foot(k, X_KNEE, BY)
    k.tube("frame", (X_HEAD - 0.03, BY, zt), (X_KNEE + 0.03, BY, zt), R, seg=24)
    k.bar("frame", (TC[0], BY + R, zt), (TC[0], yf, zt), 0.07, 0.05, cut1=((0, yf, 0), Y), weld=True)
    k.box("frame", (TC[0], yf - 0.004, zt), (0.12, 0.008, 0.10), soft=0.001)
    for dx in (-0.035, 0.035):
        k.bolt((TC[0] + dx, yf - 0.008, zt), "-y", size=0.012)
    # ---- the head end's post, the spine up to the hip and on to the knuckle, the knee end's leg into it
    k.sweep("frame", [(X_HEAD, BY, FOOT_H), (X_HEAD - 0.01, BY, 0.20), (POST_TOP[0], BY, POST_TOP[1])], k.circle(R, 24),
            bend=0.05, cut0=((0, 0, FOOT_H), Z), soft=0.002)
    k.sweep("frame", [(POST_TOP[0] - 0.03, BY, POST_TOP[1] - 0.005), (HIP[0], BY, HIP[1]), (KNUCKLE[0], BY, KNUCKLE[1])],
            k.circle(R, 24), bend=0.15, soft=0.002)
    k.box("frame", (KNUCKLE[0] + 0.02, BY, KNUCKLE[1]), (0.10, 0.13, 0.08), soft=0.008)                     # the knuckle
    xl = 0.22
    k.sweep("frame", [(X_KNEE, BY, FOOT_H), (X_KNEE - 0.02, BY, 0.12), (xl, BY, on_spine(xl) - 0.01)], k.circle(R, 24),
            bend=0.05, cut0=((0, 0, FOOT_H), Z), soft=0.002)
    for x, z in ((X_HEAD - 0.004, 0.11), (X_KNEE - 0.06, 0.25)):
        k.bolt((x, BY - R, z), "-y", size=0.012)
    # ---- the pads: each on a board on the spine, the chest pad long and sloping down to the head, the thigh pad
    # higher and thicker, sloping down to the knee, a chamfer off its knee end's front corner (ref_01 / ref_02)
    def pad_on(x0, x1, th, outline):
        xm = (x0 + x1) / 2
        dzdx = (on_spine(x1 - 0.02) - on_spine(x0 + 0.02)) / (x1 - x0 - 0.04)
        a = math.atan(dzdx)
        n = (-math.sin(a), 0.0, math.cos(a))
        sd = (math.cos(a), 0.0, math.sin(a))
        zm = on_spine(xm)
        k.box("frame", (xm + n[0] * (R + 0.004), BY, zm + n[2] * (R + 0.004)), (x1 - x0 - 0.12, 0.10, 0.012), ry=-a, soft=0.002)
        c = (xm + n[0] * (R + 0.010 + th / 2), BY, zm + n[2] * (R + 0.010 + th / 2))
        k.shaped_pad("pad", outline, c, n, sd, th, r=0.035, cushion=0.025)
    lc, wc = 0.76, 0.30
    pad_on(-0.80, -0.04, 0.09, [(-lc / 2, -wc / 2), (lc / 2, -wc / 2), (lc / 2, wc / 2), (-lc / 2, wc / 2)])
    lt, wt = 0.44, 0.36
    pad_on(-0.05, 0.39, 0.12, [(-lt / 2, -wt / 2), (lt / 2 - 0.06, -wt / 2), (lt / 2, -wt / 2 + 0.07), (lt / 2, wt / 2),
                               (-lt / 2, wt / 2)])
    # ---- the U handles off the head end's post: a cross tube through it, each end out from the post and up
    zh = 0.20
    xh = X_HEAD - 0.01 * zh / 0.20                                     # the post's x there
    k.tube("frame", (xh, BY - 0.13, zh), (xh, BY + 0.13, zh), 0.016, seg=18)
    for s in (1, -1):
        y_ = BY + s * 0.13
        g0, g1, g2 = (xh, y_, zh), (xh - 0.13, y_, zh), (xh - 0.17, y_, zh + 0.20)
        k.sweep("rubber", [g0, g1, g2], k.circle(0.021, 20), bend=0.05, soft=0.002)
        k.cyl("steel", (g2[0] - 0.004, y_, g2[2] + 0.004), 0.021, 0.02, axis="z", seg=20, soft=0.003)
    # ---- the lever: the two plates up from the knuckle to the pivot, the axle, the hub between them; the cam on the
    # front with its bolted plate
    px, pz = PIV
    for s in (1, -1):
        k.bar("frame", (KNUCKLE[0] + 0.02, BY + s * 0.055, KNUCKLE[1]), (px, BY + s * 0.055, pz), 0.11, 0.012, up=(0, 1, 0))
        k.cyl("frame", (px, BY + s * 0.055, pz), 0.055, 0.012, axis="y", seg=32, soft=0.002)
    k.tube("steel", (px, BY - 0.09, pz), (px, BY + 0.075, pz), 0.016, seg=16)
    k.tube("lever", (px, BY - 0.049, pz), (px, BY + 0.049, pz), 0.045, seg=28)
    k.cyl("cam", (px + 0.02, BY - 0.072, pz - 0.05), 0.12, 0.022, axis="y", seg=56, soft=0.003)        # (hangs under the pivot)
    k.cyl("steel", (px, BY - 0.086, pz), 0.075, 0.006, axis="y", seg=40, soft=0.001)
    for i in range(4):
        a = math.radians(200 + 47 * i)
        k.bolt((px + 0.052 * math.cos(a), BY - 0.089, pz + 0.052 * math.sin(a)), "-y", size=0.014)
    k.bolt((px, BY - 0.089, pz), "-y", size=0.022)
    # the arm out to the rollers: the outer tube, the lower tube sliding in it, the yellow pop pin under it
    rx, rz = ROLL
    a = math.atan2(rz - pz, rx - px)
    k.bar("lever", (px, BY, pz), (px + 0.24 * math.cos(a), BY, pz + 0.24 * math.sin(a)), 0.06, 0.06)
    k.bar("steel", (px + 0.18 * math.cos(a), BY, pz + 0.18 * math.sin(a)), (rx, BY, rz), 0.045, 0.045, r=0.004)
    pp = (px + 0.21 * math.cos(a), pz + 0.21 * math.sin(a))
    k.cyl("lever", (pp[0], BY, pp[1] - 0.036), 0.016, 0.012, axis="z", seg=20, soft=0.002)
    k.cyl("yellow", (pp[0], BY, pp[1] - 0.056), 0.017, 0.028, axis="z", seg=20, soft=0.004)
    k.cyl("plastic", (pp[0], BY, pp[1] - 0.076), 0.012, 0.012, axis="z", seg=16, soft=0.003)
    for i in range(4):
        q = 0.26 + 0.035 * i
        k.cyl("hole", (px + q * math.cos(a), BY - 0.0228, pz + q * math.sin(a)), 0.005, 0.001, axis="y", seg=12, soft=0.0)
    # the rollers either side of the arm's end, on one axle
    k.tube("steel", (rx, BY - 0.24, rz), (rx, BY + 0.24, rz), 0.018, seg=18)
    for s in (1, -1):
        k.tube("pad", (rx, BY + s * 0.03, rz), (rx, BY + s * 0.23, rz), 0.085, seg=40, soft=0.012)
        k.cyl("plastic", (rx, BY + s * 0.235, rz), 0.07, 0.01, axis="y", seg=36, soft=0.003)
    # ---- the cable: off the cam's bottom down to the pulley on the knee end's leg, back to the tower's foot and in
    zq = 0.26
    xq = X_KNEE - 0.02 - (0.18 / 0.47) * (zq - 0.12)                                      # the leg's x there
    k.cyl("frame", (xq, BY - R - 0.006, zq), 0.075, 0.012, axis="y", seg=40, soft=0.002)  # the pulley's housing
    k.pulley((xq, BY - R - 0.03, zq), 0.05, axis="y")
    k.cable([(px + 0.01, BY - 0.072, pz - 0.165), (xq + 0.047, BY - R - 0.03, zq)])
    xt = TC[0] + 0.20
    k.box("frame", (xt, yf - 0.024, 0.12), (0.06, 0.06, 0.12), soft=0.004)
    k.pulley((xt, yf - 0.035, 0.12), 0.04, axis="x")
    k.cable([(xq, BY - R - 0.03, zq - 0.05), (xt, BY - R - 0.03, 0.08), (xt, yf - 0.075, 0.12)])
    ox, oy, oz = tw["cable"]
    k.cable([(xt, yf + 0.005, 0.12), (xt, oy, 0.12), (ox + 0.02, oy, oz - 0.06), (ox, oy, oz)])

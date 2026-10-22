"""Life Fitness Signature Series Smith Machine (SSM), with its bar, as it ships (weights and bench not included).

Built by eye from Life Fitness's photo (refs/: ref_01, a three-quarter from the front left; every dealer shows the same
one), held to Life Fitness's spec: 87 in wide (the bar's sleeves) x 49 in deep x 93 in tall, 11-gauge steel, the bar's
path 7 degrees off vertical, 8 weight horns, the bar's catches 6 in apart.
Axes: metres, floor z = 0, the bar along x, the lifter faces -y (the front posts and the bar at the front).
Structure, each side (x = +-XS): an oval base rail along y on rubber pads; the front post rising from its front end,
leaning back 7 degrees; the back upright rising from its back end and bending forward into a top rail welded to the post;
the chrome guide rod behind the post on the same lean, a silver hook plate between them, the bar's carriage riding the
rod, a safety stop below; four weight horns on the back upright's outer face. Across: a round top tube between the top
rails, the Life Fitness crossmember between the back uprights on two gussets.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.016), rough=0.38, coat=0.25, bump=(900, 0.05)),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "steel": dict(color=(0.74, 0.75, 0.77), rough=0.3, metal=1.0, coat=0.0, aniso=0.3),   # the hook plates
    "bar": dict(color=(0.20, 0.20, 0.21), rough=0.3, metal=0.9, coat=0.0),
    "cap": dict(color=(0.25, 0.25, 0.26), rough=0.5, coat=0.0),                          # grey end caps
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "warn": dict(color=(0.95, 0.42, 0.02), rough=0.45, coat=0.0),
    "bolt": dict(color=(0.7, 0.7, 0.72), rough=0.25, metal=1.0, coat=0.0),
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_carriage": ((0.25, -0.85, 1.45), (0.66, -0.12, 1.12), 45),    # the carriage on its rod, the hook plate
    "detail_top": ((-0.25, -1.30, 2.35), (0.0, 0.30, 2.05), 45),          # the top tube, the Life Fitness crossmember
}

XS = 0.70                        # the side frames' plane (x)
Y0, Y1 = -49 / 2 * IN, 49 / 2 * IN
RAIL_W, RAIL_H = 0.075, 0.060
ZR = 0.006 + RAIL_H / 2          # the rails' centre, on 6 mm pads
LEAN = math.radians(7)
YP, YB = -0.52, 0.50             # the front posts' and back uprights' feet (y)
PW, PD = 0.075, 0.115            # the front post: across, deep
BW, BD = 0.075, 0.090            # the back upright and top rail
H = 93 * IN
ZT = 2.25                        # the top rails' centre
ROD = 0.17                       # the guide rod behind the post's axis
BAR_Z = 1.15
HORNS = (9 * IN, 28 * IN, 50 * IN, 70 * IN)


def lean_y(y0, z0, z):
    """y on a line leaning back 7 degrees through (y0, z0)."""
    return y0 + (z - z0) * math.tan(LEAN)


def build(k):
    zr_top = ZR + RAIL_H / 2
    rx = -LEAN                                     # boxes turned onto the lean
    for s in (1, -1):
        x = s * XS
        # the base rail on its pads, grey caps on its ends
        k.sweep("frame", [(x, Y0 + 0.004, ZR), (x, Y1 - 0.004, ZR)], k.stadium(RAIL_W, RAIL_H), soft=0.002)
        for y in (Y0, Y1):
            k.box("cap", (x, y + (0.002 if y < 0 else -0.002), ZR), (RAIL_W - 0.004, 0.008, RAIL_H - 0.004), soft=0.002)
            k.box("rubber", (x, y + (0.06 if y < 0 else -0.06), 0.003), (RAIL_W, 0.08, 0.006), soft=0.001)
        # the front post, leaning back, capped
        p0 = (x, YP, zr_top - 0.004)
        p1 = (x, lean_y(YP, p0[2], H - 0.006), H - 0.006)
        k.sweep("frame", [p0, p1], k.rect(PW, PD, 0.03), soft=0.002)
        k.box("cap", (x, p1[1], H - 0.003), (PW - 0.004, PD - 0.004, 0.006), rx=rx, soft=0.002)
        # the back upright bending forward into the top rail, cut onto the post's back face
        yface = lean_y(YP, p0[2], ZT) + PD / 2 / math.cos(LEAN)
        nrm = (0, math.cos(LEAN), -math.sin(LEAN))
        k.sweep("frame", [(x, YB, zr_top - 0.004), (x, YB, ZT), (x, yface - 0.01, ZT)], k.rect(BW, BD, 0.028),
                bend=0.16, cut1=((x, yface, ZT), nrm), weld=True, soft=0.002)
        # the guide rod on the lean, on a block on the rail, under a collar on the top rail
        r0 = (x, YP + ROD, zr_top + 0.04)
        r1 = (x, lean_y(YP + ROD, r0[2], ZT - BD / 2 - 0.04), ZT - BD / 2 - 0.04)
        k.box("frame", (x, r0[1] - 0.002, zr_top + 0.02), (0.06, 0.07, 0.04), soft=0.003)
        k.cyl("frame", (x, r1[1] + 0.0025, ZT - BD / 2 - 0.02), 0.026, 0.04, seg=24, soft=0.002)
        k.tube("chrome", r0, r1, 0.016, seg=28)
        # the hook plate on the post's back face: a strip on the lean, a catch every 6 in
        zb, zh = 0.30, 2.00
        zc = (zb + zh) / 2
        yc = lean_y(YP, p0[2], zc) + PD / 2 / math.cos(LEAN) + 0.035
        k.box("steel", (x, yc, zc), (0.008, 0.070, zh - zb), rx=rx, soft=0.0008)
        z = zb + 0.08
        while z < zh - 0.05:
            yt = lean_y(YP, p0[2], z) + PD / 2 / math.cos(LEAN) + 0.070 + 0.010
            k.box("steel", (x, yt, z), (0.008, 0.030, 0.018), rx=rx - math.radians(40), soft=0.0008)
            z += 6 * IN
        # the carriage on the rod (the bar's catch lever, its orange warning), the safety stop below it
        yr = lean_y(YP + ROD, r0[2], BAR_Z)
        k.box("frame", (x, yr, BAR_Z), (0.060, 0.065, 0.16), rx=rx, soft=0.004)
        k.box("frame", (x, yr - 0.045, BAR_Z + 0.03), (0.030, 0.03, 0.05), rx=rx - 0.3, soft=0.003)
        k.box("warn", (x - s * 0.0305, yr - 0.01, BAR_Z + 0.045), (0.001, 0.035, 0.03), rx=rx, soft=0.0)
        ys = lean_y(YP + ROD, r0[2], 0.45)
        k.box("frame", (x, ys - 0.012, 0.45), (0.055, 0.085, 0.07), rx=rx, soft=0.004)   # its nose in the hook plate
        k.tube("frame", (x - s * 0.0275, ys, 0.45), (x - s * 0.075, ys, 0.45), 0.008, seg=16)
        k.cyl("plastic", (x - s * 0.08, ys, 0.45), 0.014, 0.012, axis="x", seg=20, soft=0.002)
        # the bar's sleeve outside the carriage, with its collar
        k.cyl("bar", (s * (XS + 0.036), yr, BAR_Z), 0.034, 0.012, axis="x", seg=40, soft=0.001)
        k.tube("chrome", (s * (XS + 0.042), yr, BAR_Z), (s * 87 / 2 * IN, yr, BAR_Z), 0.025, seg=36)
        # four weight horns on the back upright's outer face
        for zh_ in HORNS:
            xo = s * (XS + BW / 2)
            k.cyl("frame", (xo + s * 0.005, YB, zh_), 0.045, 0.010, axis="x", seg=36, soft=0.002)
            k.tube("frame", (xo + s * 0.010, YB, zh_), (xo + s * 0.29, YB, zh_), 0.025, seg=28)
            k.cyl("cap", (xo + s * 0.295, YB, zh_), 0.031, 0.010, axis="x", seg=36, soft=0.002)
        # button heads up the back upright's outer face
        for zb_ in (0.62, 1.05, 1.47, 1.85):
            k.cyl("bolt", (s * (XS + BW / 2 + 0.0015), YB, zb_), 0.006, 0.003, axis="x", seg=16, soft=0.0008)
    # the bar between the carriages
    yr = lean_y(YP + ROD, ZR + RAIL_H / 2 + 0.04, BAR_Z)
    k.tube("bar", (-XS + 0.03, yr, BAR_Z), (XS - 0.03, yr, BAR_Z), 0.0125, seg=24)
    # the round top tube between the top rails
    yt = (YB + lean_y(YP, ZR, ZT)) / 2 - 0.05
    k.tube("frame", (-XS + BW / 2, yt, ZT), (XS - BW / 2, yt, ZT), 0.036, seg=32)
    # the Life Fitness crossmember between the back uprights, a gusset under each end
    zc = 2.00
    k.bar("frame", (-XS + BW / 2, YB, zc), (XS - BW / 2, YB, zc), 0.065, 0.075, r=0.012)
    for s in (1, -1):
        xi = s * (XS - BW / 2)
        tri = [(xi, zc - 0.037), (xi - s * 0.16, zc - 0.037), (xi, zc - 0.30)]
        k.sweep("frame", [(0, YB - 0.004, 0), (0, YB + 0.004, 0)], tri, soft=0.002)
    k.text("label", "LifeFitness", (0, YB - 0.0335, zc), 0.055, depth=0.0004)

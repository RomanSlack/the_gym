"""Hammer Strength Plate-Loaded V-Squat, Charcoal frame / Black upholstery, the lever down on its start stop.

Built by eye from the dealer gallery (refs/: ref_10 a true side view, ref_11 a true front view, ref_01 the studio
three-quarter in the picked colourway, ref_13 the three-quarter in silver, ref_03 / ref_09 / ref_14 close-ups of the
shoulder pads and grips, the platform's grit, the rear frame), held to Life Fitness's 97 x 42 x 81 in (247 x 107 x 205
cm, L x W x H). The user stands on the platform at -y, back to the pads, facing -y; x+ = the user's left.
Structure: twin centre rails from the platform's frame back to the rear frame (an A each side carrying the pivot axle and
two storage horns); the platform tilted towards the user on four legs; the lever, swinging on the axle: the pad post
(back pads, shoulder pads, grips), the top arm curving from the shoulders back down to the pivot, a curved lower arm each
side from the post's foot back up to its hub, a loading horn each side at the post's foot and on the lower arm, the
counterbalance bar behind the pivot with the HAMMER STRENGTH placard; the post rests on a rubber stop at the start.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),  # the black lever
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "placard": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.15), "front": (0, 5, 1.15), "side": (-90, 3, 1.15), "back_three_quarter": (150, 18, 1.15)}
DETAILS = {
    "detail_pads": ((-0.95, -1.10, 1.75), (0.0, -0.10, 1.40), 45),      # the pads, shoulder pads and grips
    "detail_pivot": ((1.15, 0.30, 1.30), (0.20, 0.68, 0.90), 45),       # the pivot, hubs and counterbalance
    "detail_platform": ((1.00, -1.75, 0.95), (0.0, -0.85, 0.50), 45),   # the platform and its legs
}

FOOT_H = 0.02
RAIL = (0.076, 0.10)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
CX = 0.12                        # the twin centre rails (x)
PX = 0.33                        # the platform frame (x)
AX = 0.36                        # the rear A-frames (x)
PIV = (0.68, 0.97)               # the pivot (y, z)
PLAT = ((-1.175, 0.656), (-0.52, 0.437))   # the platform's top: front edge, back edge (y, z)
PLAT_W = 0.86
POST0, POST1 = (-0.16, 0.36), (-0.02, 1.80)   # the pad post's foot and top (y, z)


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def post_at(z):
    f = (z - POST0[1]) / (POST1[1] - POST0[1])
    return POST0[0] + (POST1[0] - POST0[0]) * f


def bar_x(k, mat, y, z, x0, x1, w=0.076, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z = (0, 0, 1)
    Y = (0, 1, 0)
    # ---- the base: the platform frame (side rails, front + back cross bars), the twin centre rails back to the rear
    # frame's cross bar, the rear frame's side rails
    yp0, yp1 = -1.15, -0.55
    for s in (1, -1):
        k.bar("frame", (s * PX, yp0, RAIL_Z), (s * PX, yp1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((yp0, -1), (yp1, 1)):
            k.box("plastic", (s * PX, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * PX, yp0 + 0.04)
        foot(k, s * PX, yp1 - 0.04)
    for y_ in (-0.95, -0.65):
        bar_x(k, "frame", y_, RAIL_Z, -(PX - RAIL[0] / 2), PX - RAIL[0] / 2, RAIL[0], RAIL[1])
    for bx in (-0.27, -0.09, 0.09, 0.27):
        k.bolt((bx, -0.95 - 0.038, RAIL_Z), "-y", size=0.014)
    yr0 = 0.41
    for s in (1, -1):
        k.bar("frame", (s * CX, -0.95 + 0.038, RAIL_Z), (s * CX, yr0 - 0.038, RAIL_Z), RAIL[0], RAIL[1],
              cut0=((0, -0.95 + 0.038, 0), Y), cut1=((0, yr0 - 0.038, 0), Y), weld=True)
        k.bar("frame", (s * AX, yr0 - 0.038, RAIL_Z), (s * AX, 1.20, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        k.box("plastic", (s * AX, 1.204, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * AX, 1.16)
        foot(k, s * AX, yr0 + 0.0)
    bar_x(k, "frame", yr0, RAIL_Z, -(AX - RAIL[0] / 2), AX - RAIL[0] / 2, RAIL[0], RAIL[1])
    # ---- the rear frame: an A each side up to an apex block, the pivot axle through both; two storage horns each side
    for s in (1, -1):
        x = s * AX
        apex = (x, PIV[0], PIV[1] - 0.07)
        for fy in (yr0 + 0.05, 1.12):
            k.bar("frame", (x, fy, RAIL_TOP), apex, 0.07, 0.07, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z),
                  cut1=((0, 0, PIV[1] - 0.10), Z), weld=True)
        k.box("frame", (x, PIV[0], PIV[1] - 0.03), (0.08, 0.16, 0.14), soft=0.004)
        for zh in (0.30, 0.62):          # on the rear leg, at its y at that height
            ly = 1.12 + (PIV[0] - 1.12) * (zh - RAIL_TOP) / (PIV[1] - 0.10 - RAIL_TOP)
            xo = x + s * 0.035
            k.cyl("frame", (xo + s * 0.006, ly, zh), 0.045, 0.012, axis="x", seg=32, soft=0.003)
            k.tube("steel", (xo + s * 0.012, ly, zh), (xo + s * 0.20, ly, zh), 0.025, seg=32)
            k.cyl("frame", (xo + s * 0.208, ly, zh), 0.029, 0.016, axis="x", seg=32, soft=0.004)
        k.box("warn", (x + s * 0.041, PIV[0], PIV[1] - 0.04), (0.002, 0.05, 0.06), soft=0.0)
    k.tube("steel", (-AX - 0.05, PIV[0], PIV[1]), (AX + 0.05, PIV[0], PIV[1]), 0.025, seg=28)
    for s in (1, -1):
        k.bolt((s * (AX + 0.05), PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.03)
    # ---- the platform: the grit top on its plate, four legs down to its frame
    (fy, fz), (by, bz) = PLAT
    t = math.atan2(fz - bz, by - fy)
    mid = ((fy + by) / 2, (fz + bz) / 2)
    L = math.hypot(by - fy, fz - bz)
    nrm = (0.0, math.sin(t), math.cos(t))
    k.box("grip", (0, mid[0], mid[1] - 0.002), (PLAT_W - 0.02, L - 0.02, 0.004), rx=-t, soft=0.001)
    k.box("frame", (0, mid[0] - nrm[1] * 0.02, mid[1] - nrm[2] * 0.02), (PLAT_W, L, 0.036), rx=-t, soft=0.004)
    for s in (1, -1):
        for f in (0.08, 0.92):
            py = fy + (by - fy) * f
            pz = fz + (bz - fz) * f - 0.038 / math.cos(t)
            k.bar("frame", (s * PX, py - 0.04 * (1 if f < 0.5 else -1), RAIL_TOP), (s * PX, py, pz + 0.02), 0.06, 0.06,
                  up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z), cut1=((0, py, pz), nrm), weld=True)
    # ---- the lever: the pad post, its stop
    p0 = (0, POST0[0], POST0[1]); p1 = (0, POST1[0], POST1[1])
    k.bar("lever", p0, p1, 0.076, 0.076, up=Y)
    bar_x(k, "frame", POST0[0], RAIL_Z, -(CX - RAIL[0] / 2), CX - RAIL[0] / 2, RAIL[0], RAIL[1])     # the stop's cross bar
    k.box("rubber", (0, POST0[0], (RAIL_TOP + POST0[1]) / 2), (0.08, 0.08, POST0[1] - RAIL_TOP), soft=0.006)
    # the back pads on the post's face, the shoulder bracket and pads, the grips
    lean = math.atan2(POST1[0] - POST0[0], POST1[1] - POST0[1])
    n_p = (0.0, -math.cos(lean), math.sin(lean))
    for zc, w, ln in ((1.06, 0.36, 0.40), (1.58, 0.26, 0.62)):
        yc = post_at(zc) - 0.038 - 0.045
        k.shaped_pad("pad", [(-w / 2, -ln / 2), (w / 2, -ln / 2), (w / 2, ln / 2), (-w / 2, ln / 2)], (0, yc, zc), n_p, (1, 0, 0),
                     0.09, r=0.05, cushion=0.03)
    zs = 1.66
    ys = post_at(zs)
    bar_x(k, "lever", ys, zs, -0.20, 0.20, 0.05, 0.05)
    for s in (1, -1):
        x = s * 0.14
        k.bar("lever", (x, ys - 0.025, zs), (x, ys - 0.30, zs), 0.04, 0.04, cut0=((0, ys - 0.025, 0), Y), weld=True)
        k.pad("pad", (x, ys - 0.17, zs - 0.07), (0.12, 0.26, 0.10), r=0.035)
        k.sweep("lever", [(x, ys - 0.30, zs), (s * 0.22, ys - 0.32, zs + 0.02), (s * 0.30, ys - 0.30, zs + 0.03)],
                k.circle(0.014, 18), bend=0.03, soft=0.0015)
        k.tube("rubber", (s * 0.235, ys - 0.315, zs + 0.025), (s * 0.31, ys - 0.30, zs + 0.03), 0.02, seg=22)
    # the top arm: from the shoulder bracket straight back, then down to the centre hub on the axle
    k.cyl("lever", (0, PIV[0], PIV[1]), 0.045, 0.12, axis="x", seg=32, soft=0.004)
    k.sweep("lever", [(0, ys + 0.025, zs), (0, 0.32, zs), (0, PIV[0] - 0.01, PIV[1] + 0.04)], k.rect(0.06, 0.06, 0.008),
            bend=0.18, up=(1, 0, 0), cut0=((0, ys + 0.025, 0), Y), weld=True, soft=0.002)
    # the counterbalance bar behind the pivot with the placard
    k.bar("lever", (0, PIV[0] + 0.04, PIV[1]), (0, 1.16, PIV[1]), 0.06, 0.07)
    k.box("placard", (0.032, 1.02, PIV[1]), (0.002, 0.16, 0.055), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("seam", line, (0.0336, 1.02, PIV[1] + 0.011 - i * 0.022), 0.019, rz=math.pi / 2, depth=0.0003)
    # the lower cross tube on the post, a curved arm each side back up to its hub on the axle, the loading horns
    zl = 0.62
    yl = post_at(zl)
    bar_x(k, "lever", yl, zl, -0.25, 0.25, 0.06, 0.06)
    for s in (1, -1):
        x = s * 0.22
        k.sweep("lever", [(x, yl + 0.03, zl), (x, 0.20, 0.50), (x, 0.52, 0.78), (x, PIV[0], PIV[1] - 0.04)],
                k.rect(0.07, 0.11, 0.01), bend=0.16, up=(1, 0, 0), cut0=((0, yl + 0.03, 0), Y), weld=True, soft=0.002)   # heavy, as in ref_01
        k.tube("lever", (s * 0.18, PIV[0], PIV[1]), (s * 0.30, PIV[0], PIV[1]), 0.045, seg=32)
        for hy, hz, x0 in ((yl, zl, 0.25), (0.42, 0.68, 0.255)):
            k.cyl("lever", (s * (x0 + 0.01), hy, hz), 0.05, 0.02, axis="x", seg=32, soft=0.004)
            k.tube("steel", (s * (x0 + 0.02), hy, hz), (s * (x0 + 0.33), hy, hz), 0.025, seg=32)
            k.cyl("lever", (s * (x0 + 0.338), hy, hz), 0.029, 0.018, axis="x", seg=32, soft=0.005)

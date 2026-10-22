"""The ABS Company The Nordic Curl.

Built by eye from the dealer's photos (refs/: ref_01 the studio three-quarter, ref_02 in use), held to the listing's
60 x 25 x 29 in (L x W x H).
Axes: metres, floor z = 0, along x: the chest pad at -x (the lifter falls forwards onto it), the knee pad, ankle
rollers, placard and wheels at +x.
Structure: two laser-cut side plates (a long web with a splayed foot at each end, a flange folded in along the top)
joined by end plates and a cross tube; the knee pad across the top at the rear; behind it the roller post with the two
ankle rollers; the rear plate with the instruction placard and two transport wheels; the chest pad on a telescoping
post (blue pop pin) pivoting on a bracket on the cross tube; THE NORDIC CURL on the sides.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.42, metal=0.1, coat=0.1, bump=(1400, 0.05)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.5, sheen=0.2, bump=(1500, 0.12)),
    "blue": dict(color=(0.03, 0.08, 0.45), rough=0.35, coat=0.2),
    "gold": dict(color=(0.78, 0.55, 0.16), rough=0.4, coat=0.0),
    "placard": dict(color=(0.08, 0.08, 0.085), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-145, 18, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (40, 18, 1.0)}
DETAILS = {
    "detail_rollers": ((1.25, -0.6, 0.65), (0.64, 0.0, 0.38), 40),      # the knee pad, rollers, placard, wheels
    "detail_post": ((-0.1, -0.8, 0.6), (-0.3, 0.0, 0.35), 40),          # the chest pad's post on its pivot
}

PY, PT = 0.27, 0.008            # side plates: y, thickness
TOPZ, WEBZ = 0.26, 0.10         # the plates' top edge, the web's bottom edge between the feet
X0, X1 = -0.70, 0.66            # the plates' ends
KNEE = (0.20, 0.58)             # the knee pad (x)
PAD_T = 0.07
CHEST_DEG = 50.0                # the chest pad's lean back from horizontal (its face looks back and up)
CHEST_C, CHEST_L, CHEST_W = (-0.48, 0.55), 0.48, 0.46
PIVOT = (-0.25, 0.15)           # the chest post's pivot (x, z), on the cross tube


def side(k, s):
    y = s * PY
    prof = [(X0, TOPZ), (X1, TOPZ), (X1, 0.13), (X1 - 0.05, 0.015), (X1 - 0.16, 0.015), (X1 - 0.19, WEBZ),
            (X0 + 0.19, WEBZ), (X0 + 0.16, 0.015), (X0 + 0.05, 0.015), (X0, 0.13)]
    k.sweep("frame", [(0, y - PT / 2, 0), (0, y + PT / 2, 0)], kit_round(prof), up=(0, 0, 1), soft=0.002)
    k.box("frame", ((X0 + X1) / 2, y - s * 0.016, TOPZ - 0.003), (X1 - X0, 0.024, 0.006), soft=0.001)   # the folded flange
    for fx in (X0 + 0.105, X1 - 0.105):                                                          # rubber feet
        k.box("rubber", (fx, y - s * 0.01, 0.0075), (0.15, 0.07, 0.015), soft=0.004)
    if s < 0:
        fy = y - PT / 2 - 0.0005
        k.text("label", "THE", (0.05, fy, 0.215), 0.03, depth=0.0006)
        k.text("label", "NORDIC", (0.08, fy, 0.18), 0.03, depth=0.0006)
        k.text("gold", "CURL", (0.21, fy, 0.18), 0.03, depth=0.0006)
        k.box("gold", (0.15, fy, 0.207), (0.10, 0.0008, 0.004), soft=0.0)


def kit_round(prof):
    import kit
    return kit._round_poly(prof, 0.008, 3)


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    for s in (1, -1):
        side(k, s)
    yi = PY - PT / 2
    # the end plates and the cross tube between the side plates
    for x_ in (X0 + 0.004, X1 - 0.004):
        k.box("frame", (x_, 0, (WEBZ + TOPZ) / 2 + 0.03), (0.008, 2 * yi, TOPZ - WEBZ - 0.06), soft=0.001)
    k.bar("frame", (PIVOT[0], -yi, PIVOT[1] - 0.01), (PIVOT[0], yi, PIVOT[1] - 0.01), 0.05, 0.05, up=Z,
          cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    # the knee pad across the flanges
    L = KNEE[1] - KNEE[0]; W = 2 * PY + 0.02
    k.shaped_pad("pad", [(-L / 2, -W / 2), (L / 2, -W / 2), (L / 2, W / 2), (-L / 2, W / 2)],
                 ((KNEE[0] + KNEE[1]) / 2, 0, TOPZ + PAD_T / 2), Z, (1, 0, 0), PAD_T, r=0.03, cushion=0.02)
    # the roller post behind it: a bracket on the rear end plate, the post up, the rod across, two rollers
    rx = X1 - 0.045
    k.box("frame", (rx, 0, TOPZ - 0.03), (0.07, 0.10, 0.06), soft=0.003)
    k.bar("frame", (rx, 0, TOPZ), (rx, 0, 0.40), 0.05, 0.05, up=Y)
    k.tube("steel", (rx, -0.215, 0.42), (rx, 0.215, 0.42), 0.0125)
    k.box("frame", (rx, 0, 0.415), (0.05, 0.05, 0.03), soft=0.004)
    for s in (1, -1):
        k.cyl("pad", (rx, s * 0.115, 0.42), 0.06, 0.17, axis="y", seg=40, soft=0.014)
        k.cyl("frame", (rx, s * 0.205, 0.42), 0.035, 0.008, axis="y", seg=28)
        k.bolt((rx, s * 0.004 + s * 0.023, 0.385), "+y" if s > 0 else "-y", size=0.012)
    k.cyl("blue", (rx + 0.03, -0.035, 0.30), 0.012, 0.02, axis="x", seg=20, soft=0.004)
    # the rear plate with its placard, two wheels on brackets under it
    px = X1 + 0.006
    k.box("frame", (px, 0, 0.25), (0.012, 0.34, 0.34), soft=0.003)
    k.box("placard", (px + 0.0065, 0, 0.25), (0.001, 0.30, 0.30), soft=0.0)
    k.text("gold", "THE NORDIC CURL", (px + 0.0072, 0, 0.375), 0.02, rz=math.pi / 2, depth=0.0005)
    for i, (dy, dz) in enumerate(((-0.08, 0.30), (0.06, 0.25), (-0.08, 0.20), (0.06, 0.15))):
        k.box("label", (px + 0.0072, dy, dz), (0.0005, 0.07, 0.04), soft=0.0)
    for s in (1, -1):
        k.box("frame", (px + 0.03, s * 0.15, 0.08), (0.05, 0.012, 0.06), soft=0.002)
        k.cyl("rubber", (px + 0.05, s * 0.15 + s * 0.025, 0.045), 0.045, 0.035, axis="y", seg=32, soft=0.006)
        k.cyl("steel", (px + 0.05, s * 0.15 + s * 0.045, 0.045), 0.012, 0.006, axis="y", seg=20)
    # the chest pad: a pivot bracket on the cross tube, the outer post, the inner one, the pad's back plate, the pad
    A = math.radians(CHEST_DEG)
    up = (-math.cos(A), 0, math.sin(A))                                  # up the pad, towards the front
    n = (math.sin(A), 0, math.cos(A))                                    # its face
    cx, cz = CHEST_C
    back = (cx - n[0] * (PAD_T / 2 + 0.012), 0, cz - n[2] * (PAD_T / 2 + 0.012))
    for s in (1, -1):
        k.box("frame", (PIVOT[0], s * 0.035, PIVOT[1] + 0.04), (0.08, 0.008, 0.08), soft=0.002)
    k.bolt((PIVOT[0], -0.039, PIVOT[1] + 0.05), "-y", size=0.016, nut=0.078)
    p0 = (PIVOT[0], 0, PIVOT[1] + 0.05)
    d = (back[0] - p0[0], 0, back[2] - p0[2]); ln = math.hypot(d[0], d[2]); d = (d[0] / ln, 0, d[2] / ln)
    mid = (p0[0] + d[0] * ln * 0.55, 0, p0[2] + d[2] * ln * 0.55)
    k.bar("frame", p0, mid, 0.06, 0.06, up=Y)
    k.bar("frame", (p0[0] + d[0] * ln * 0.4, 0, p0[2] + d[2] * ln * 0.4), (back[0] + n[0] * 0.006, 0, back[2] + n[2] * 0.006), 0.05, 0.05, up=Y)
    k.cyl("blue", (mid[0] - d[0] * 0.03, -0.045, mid[2] - d[2] * 0.03), 0.014, 0.022, axis="y", seg=20, soft=0.005)
    k.box("frame", (mid[0] - d[0] * 0.03, -0.031, mid[2] - d[2] * 0.03), (0.03, 0.006, 0.03), soft=0.002)
    k.box("frame", (back[0] + n[0] * 0.006, 0, back[2] + n[2] * 0.006), (0.012, 0.16, 0.20), ry=A - math.pi / 2, soft=0.002)
    k.shaped_pad("pad", [(-CHEST_W / 2, -CHEST_L / 2), (CHEST_W / 2, -CHEST_L / 2), (CHEST_W / 2, CHEST_L / 2), (-CHEST_W / 2, CHEST_L / 2)],
                 (cx, 0, cz), n, (0, -1, 0), PAD_T, r=0.06, cushion=0.025)

"""Hammer Strength Seated Arm Curl (the barbell preacher bench), Black frame / Black upholstery.

Built by eye from Life Fitness's one photo (refs/: ref_01, a three-quarter from the front right with an EZ bar on the
catches; the bar and plates are not part of the bench and are left out), held to Life Fitness's 38 x 34 x 42 in
(97 x 86 x 107 cm, L x W x H).
Axes: metres, floor z = 0, the user sits at +y facing -y, arms over the pad; x+ = the user's left.
Structure: a base (side rails, cross bars, feet); two square uprights in front of the seat carrying the pad's frame,
the HAMMER STRENGTH badge on one; a bent leg each side from the base's front corner curving up and back into the
pad's frame; the preacher pad sloping down towards the bar; the bar catches (a bent hook each side on the uprights'
front faces); the seat on its post with the pop-pin height tube.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.42, metal=0.2, coat=0.1, bump=(1400, 0.06)),   # black
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "bolt": dict(color=(0.6, 0.6, 0.62), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 14, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (145, 16, 1.0)}
DETAILS = {"detail_catch": ((0.65, -0.95, 0.95), (0.25, -0.30, 0.78), 45)}   # a bar catch, the pad, the badge

T = 0.076
FOOT_H = 0.012
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
BX = 0.39                          # the base's side rails
Y0, Y1 = -0.48, 0.48               # the base's front and back
UX, UY = 0.30, -0.18               # the uprights
TOP = 42 * IN
PAD_T = math.radians(38)           # the pad's slope (down towards the bar)


def foot(k, x, y):
    k.box("rubber", (x, y, FOOT_H / 2), (0.10, 0.10, FOOT_H), soft=0.002)
    k.box("frame", (x, y, FOOT_H + 0.003), (0.12, 0.12, 0.006), soft=0.001)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    # ---- the base
    for s in (1, -1):
        x = s * BX
        k.bar("frame", (x, Y0, RAIL_Z + 0.006), (x, Y1, RAIL_Z + 0.006), RAIL[0], RAIL[1], r=0.006)
        for y in (Y0 + 0.04, Y1 - 0.04):
            foot(k, x, y)
    for y_ in (Y0 + 0.04, UY, Y1 - 0.04):
        k.bar("frame", (-(BX - T / 2), y_, RAIL_Z + 0.006), (BX - T / 2, y_, RAIL_Z + 0.006), T, RAIL[1],
              cut0=((-(BX - T / 2), 0, 0), (1, 0, 0)), cut1=((BX - T / 2, 0, 0), (1, 0, 0)), weld=True)
    rt = RAIL_TOP + 0.006
    # ---- the pad's frame: a cross tube under the pad's top edge, the pad board on it
    zt = TOP - 0.10
    k.bar("frame", (-(UX + T / 2), UY, zt), (UX + T / 2, UY, zt), T, T)
    c = (0.0, UY - 0.10, TOP - 0.11)
    nrm = (0.0, -math.sin(PAD_T), math.cos(PAD_T))         # the pad's face: up and towards the bar (its high edge at the user)
    k.box("frame", tuple(c[i] - nrm[i] * 0.045 for i in range(3)), (0.56, 0.36, 0.012), rx=PAD_T, soft=0.002)
    k.shaped_pad("pad", [(-0.30, -0.19), (0.30, -0.19), (0.30, 0.19), (-0.30, 0.19)], c, nrm, (1, 0, 0), 0.08,
                 r=0.04, cushion=0.03)
    k.box("frame", (0.0, UY - 0.04, zt + 0.05), (0.40, 0.04, 0.06), soft=0.003)          # the bracket under the board
    for s in (1, -1):
        x = s * UX
        # the upright, capped; the bar catch on its front face
        k.bar("frame", (x, UY, rt), (x, UY, zt + T / 2), T, T, cut0=((0, 0, rt), Z), weld=True)
        for zb in (0.30, 0.55, 0.80):
            k.cyl("bolt", (x + s * (T / 2 + 0.002), UY, zb), 0.007, 0.004, axis="x", seg=14, soft=0.001)
        zc = 0.74
        k.box("frame", (x, UY - T / 2 - 0.004, zc), (0.05, 0.008, 0.12), soft=0.001)
        k.sweep("frame", [(x, UY - T / 2 - 0.008, zc - 0.04), (x, UY - T / 2 - 0.09, zc - 0.04), (x, UY - T / 2 - 0.11, zc + 0.03)],
                k.rect(0.04, 0.012, 0.003), bend=0.02, soft=0.001)
        k.box("plastic", (x, UY - T / 2 - 0.06, zc - 0.03), (0.042, 0.07, 0.004), soft=0.001)
        # the bent leg: from the base's front corner curving up and back into the pad frame's end
        k.sweep("frame", [(s * BX, Y0 + 0.10, rt), (s * BX, Y0 + 0.16, 0.55), (s * (UX + 0.06), UY - 0.06, zt - 0.02)],
                k.rect(0.06, 0.06, 0.008), bend=0.20, up=(1, 0, 0), cut0=((0, 0, rt), Z), soft=0.002)
        k.bar("frame", (s * (UX + 0.06), UY - 0.06, zt - 0.02), (s * (UX + T / 2), UY - 0.03, zt - 0.02), 0.05, 0.05)
    # the badge on the right upright's outer face
    xb = -(UX + T / 2 + 0.002)
    k.box("placard", (xb, UY, 0.45), (0.004, 0.06, 0.16), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (xb - 0.0023, UY + 0.012 - i * 0.024, 0.45), 0.018, rz=-math.pi / 2, spin=math.pi / 2, depth=0.0003)
    # ---- the seat: its sleeve post on the back cross bar's middle bar, the height tube, the pad, the pop pin
    sy = 0.24
    k.bar("frame", (0, sy - 0.05, RAIL_Z + 0.006), (0, Y1 - 0.04 - T / 2, RAIL_Z + 0.006), T, RAIL[1],
          cut1=((0, Y1 - 0.04 - T / 2, 0), Y), weld=True)
    k.bar("frame", (0, UY + T / 2, RAIL_Z + 0.006), (0, sy - 0.05, RAIL_Z + 0.006), T, RAIL[1], cut0=((0, UY + T / 2, 0), Y), weld=True)
    k.bar("frame", (0, sy, rt), (0, sy, 0.36), 0.076, 0.076, cut0=((0, 0, rt), Z), weld=True)
    k.bar("steel", (0, sy, 0.30), (0, sy, 0.50), 0.06, 0.06, r=0.004)
    for i in range(5):
        k.cyl("hole", (0, sy + 0.0305, 0.38 + i * 0.025), 0.005, 0.001, axis="y", seg=12, soft=0.0)
    k.tube("steel", (0, sy + 0.038, 0.33), (0, sy + 0.08, 0.33), 0.007, seg=12)
    k.cyl("redplastic", (0, sy + 0.09, 0.33), 0.016, 0.022, axis="y", seg=20, soft=0.004)
    k.box("frame", (0, sy, 0.51), (0.24, 0.24, 0.02), soft=0.003)
    k.pad("pad", (0, sy, 0.565), (0.34, 0.30, 0.09), r=0.04)

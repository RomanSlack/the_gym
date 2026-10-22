"""Body-Solid GVKR60B Vertical Knee Raise & Dip.

Built by eye from the dealer's photos (refs/: ref_01 the studio three-quarter, ref_02-ref_07 in a gym and in use),
held to Body-Solid's 37 x 27 x 60 in (L x W x H).
Axes: metres, floor z = 0, the user stands facing -x, back to the pad; y across.
Structure: two side frames, each a foot rail along x on the floor, an upright rising at the rear and bending forwards
into the arm rest, and a step arc from the foot's front up into the upright (the step-up entry); a cross tube between
the uprights carrying the back pad on a plate, a cross rail between the feet at the rear (the Body-Solid logo); the
arm pads on the arm rests, a vertical grip and a forward dip handle at the front of each.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.018, 0.020, 0.026), rough=0.35, metal=0.2, coat=0.25, bump=(1400, 0.05)),   # black, a blue cast
    "pad": dict(color=(0.012, 0.012, 0.014), rough=0.45, sheen=0.2, bump=(1500, 0.1)),               # DuraFirm vinyl
    "cap": dict(color=(0.01, 0.01, 0.011), rough=0.35, coat=0.2),
}
VIEWS = {"three_quarter": (-125, 14, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (50, 16, 1.0)}
DETAILS = {
    "detail_arms": ((-0.9, -0.75, 1.65), (-0.22, -0.3, 1.32), 40),      # the arm pad, its grips
    "detail_base": ((-0.95, -0.8, 0.45), (-0.2, -0.3, 0.2), 40),        # the foot, the step arc
}

Y0 = 0.30                       # the side frames (+-y)
T = (2 * IN, 3 * IN)            # tube: across (y) x deep
FOOT_L = 37 * IN - 0.02
UX = 0.15                       # the uprights (x)
ARM_Z, ARM_X = 1.30, -0.33      # the arm rests' height, their front end
BACK = (0.33, 0.48, 0.07)       # back pad: width, height, thickness
BACK_Z = (1.02, 1.50)


def frame(k, s):
    y = s * Y0
    Z = (0, 0, 1)
    fz = 0.003 + T[0] / 2
    k.bar("frame", (-FOOT_L / 2 + 0.02, y, fz), (FOOT_L / 2 - 0.02, y, fz), T[0], T[0], up=(0, 1, 0))
    for d in (1, -1):
        k.box("cap", (d * (FOOT_L / 2 - 0.02), y, fz - 0.0015), (0.04, T[0] + 0.005, T[0] + 0.003), soft=0.004)
    ft = 0.003 + T[0]
    k.sweep("frame", [(UX, y, ft), (UX, y, ARM_Z), (ARM_X, y, ARM_Z)], k.rect(T[1], T[0], 0.008), up=(0, 1, 0), bend=0.12,
            cut0=((0, 0, ft), Z), weld=True)
    k.box("cap", (ARM_X - 0.004, y, ARM_Z), (0.008, T[0] + 0.004, T[1] + 0.004), soft=0.003)
    # the step arc from the foot's front up into the upright
    fx = UX - T[1] / 2
    k.sweep("frame", [(-0.32, y, ft), (-0.32, y, 0.30), (fx, y, 0.47)], k.rect(T[1] * 0.8, T[0], 0.008), up=(0, 1, 0), bend=0.16,
            cut0=((0, 0, ft), Z), cut1=((fx, 0, 0), (1, 0, 0)), weld=True)
    # the arm pad on its board, the grips at its front
    top = ARM_Z + T[1] / 2
    k.box("frame", (-0.12, y, top + 0.005), (0.30, 0.09, 0.01), soft=0.002)
    L, W, th = 0.34, 0.11, 0.065
    k.shaped_pad("pad", [(-L / 2, -W / 2), (L / 2, -W / 2), (L / 2, W / 2), (-L / 2, W / 2)],
                 (-0.13, y, top + 0.01 + th / 2), Z, (1, 0, 0), th, r=0.03, cushion=0.018)
    gy = y - s * 0.075                                                     # the vertical grip, inboard of the pad
    k.box("frame", (ARM_X + 0.03, y - s * 0.04, top - 0.01), (0.04, 0.07, 0.02), soft=0.002)
    k.tube("frame", (ARM_X + 0.03, gy, top - 0.02), (ARM_X + 0.03, gy, top + 0.16), 0.016, seg=24)
    k.tube("rubber", (ARM_X + 0.03, gy, top + 0.04), (ARM_X + 0.03, gy, top + 0.165), 0.02, seg=24)
    k.tube("frame", (ARM_X, y, ARM_Z - 0.01), (ARM_X - 0.16, y, ARM_Z - 0.01), 0.016, seg=24)        # the dip handle
    k.tube("rubber", (ARM_X - 0.03, y, ARM_Z - 0.01), (ARM_X - 0.165, y, ARM_Z - 0.01), 0.02, seg=24)


def build(k):
    Y = (0, 1, 0)
    for s in (1, -1):
        frame(k, s)
    yi = Y0 - T[0] / 2
    # the rear cross rail on the floor, its logo
    k.bar("frame", (0.32, -yi, 0.003 + T[1] / 2), (0.32, yi, 0.003 + T[1] / 2), T[1], T[1] * 0.67, up=(0, 0, 1),
          cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    k.text("label", "Body-Solid", (0.32 - T[1] / 2 - 0.0005, 0, 0.04), 0.022, rz=-math.pi / 2, depth=0.0006)
    # the cross tube between the uprights, the back pad's plate and pad
    cz = BACK_Z[0] + 0.03
    k.bar("frame", (UX, -yi, cz), (UX, yi, cz), T[1], T[0], up=(0, 0, 1), cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    px = UX - T[1] / 2 - 0.006
    k.box("frame", (px, 0, (BACK_Z[0] + BACK_Z[1]) / 2 - 0.02), (0.012, 0.18, 0.36), soft=0.002)
    for bz in (cz - 0.02, cz + 0.02):
        k.bolt((px - 0.006, 0.06, bz), "-x", size=0.01)
    w, h, th = BACK
    k.shaped_pad("pad", [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)],
                 (px - 0.006 - th / 2, 0, (BACK_Z[0] + BACK_Z[1]) / 2), (-1, 0, 0), (0, 1, 0), th, r=0.06, cushion=0.025)

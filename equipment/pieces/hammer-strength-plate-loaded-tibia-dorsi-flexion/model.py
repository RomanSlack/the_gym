"""Hammer Strength Plate-Loaded Tibia Dorsi Flexion (PL-TIB), Charcoal frame / Black upholstery, at rest.

Built by eye from the dealer gallery (refs/: ref_09 / ref_10 true front views, ref_13 / ref_14 the three-quarters,
ref_01 the studio three-quarter in the picked colourway, ref_07 in use from the side), held to Life Fitness's
16 x 34 x 14 in (41 x 86 x 36 cm, L x W x H; W across the horns), max three 10 lb plates a side.
Axes: metres, floor z = 0, the user stands or sits at +y, the foot slid in under the roller from +y; x+ = the user's left.
Structure: the base plate (with its badge and labels); an A of two legs each side up to a pillow-block bearing; the axle
through both bearings and out to the loading horns; the cradle swinging on the axle: two side plates, the top bar (the
warning label), the roller pad over the foot, the two grit foot pads lettered HAMMER STRENGTH.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "emboss": dict(color=(0.03, 0.03, 0.032), rough=0.7, coat=0.0),
    "bolt": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
}
VIEWS = {"three_quarter": (150, 24, 1.0), "front": (180, 10, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-35, 24, 1.0)}
DETAILS = {"detail_bearing": ((0.55, 0.45, 0.50), (0.22, 0.0, 0.28), 45)}   # a bearing, the horn's root, the cradle

PL = 0.008
BASE = (0.50, 0.40)               # the base plate (x, y)
BX = 0.23                         # the bearings (x)
AZ = 0.30                         # the axle's height
CX = 0.18                         # the cradle's side plates (x)


def build(k):
    # the base plate, its badge, labels and anchor holes
    k.box("frame", (0, 0, PL / 2), (BASE[0], BASE[1], PL), soft=0.002)
    k.box("placard", (-0.08, 0.13, PL + 0.001), (0.14, 0.06, 0.002), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (-0.08, 0.13 + 0.012 - i * 0.022, PL + 0.0022), 0.016, rx=0.0, rz=math.pi, depth=0.0003)
    k.box("warn", (0.12, 0.14, PL + 0.001), (0.05, 0.03, 0.002), soft=0.0)
    for sx in (1, -1):
        for sy in (1, -1):
            k.cyl("hole", (sx * 0.22, sy * 0.17, PL + 0.0003), 0.007, 0.0008, seg=14)
    # each side: an A of two legs from the plate up to the bearing's mount, the pillow block, its bolts
    for s in (1, -1):
        x = s * BX
        top = (x, 0.0, AZ - 0.045)
        for fy in (-0.16, 0.16):
            k.bar("frame", (x, fy, PL), top, 0.04, 0.03, up=(1, 0, 0), cut0=((0, 0, PL), (0, 0, 1)),
                  cut1=((0, 0, AZ - 0.045), (0, 0, 1)), weld=True)
        k.box("frame", (x, 0.0, AZ - 0.04), (0.05, 0.14, 0.012), soft=0.002)
        k.box("lever", (x, 0.0, AZ - 0.01), (0.045, 0.11, 0.05), soft=0.004)
        k.cyl("lever", (x, 0.0, AZ), 0.035, 0.045, axis="x", seg=28, soft=0.004)
        for dy in (-0.042, 0.042):
            k.bolt((x, dy, AZ - 0.034 + 0.0), "+z", size=0.01)
    # the axle through both bearings, out to the loading horns, their end caps
    k.tube("steel", (-0.40, 0.0, AZ), (0.40, 0.0, AZ), 0.022, seg=28)
    for s in (1, -1):
        k.cyl("lever", (s * (BX + 0.04), 0.0, AZ), 0.04, 0.02, axis="x", seg=28, soft=0.004)     # the collar
        k.tube("chrome", (s * (BX + 0.05), 0.0, AZ), (s * 0.42, 0.0, AZ), 0.025, seg=28)
        k.cyl("rubber", (s * 0.425, 0.0, AZ), 0.028, 0.012, axis="x", seg=28, soft=0.004)
    # the cradle: two side plates hung on the axle, the top bar, the roller, the two grit foot pads
    prof = [(-0.04, 0.04), (0.04, 0.04), (0.20, -0.02), (0.20, -0.20), (-0.02, -0.22), (-0.06, -0.10)]   # (y, z) off the axle
    for s in (1, -1):
        k.sweep("lever", [(s * CX - PL / 2, 0, AZ), (s * CX + PL / 2, 0, AZ)], [(-y, z) for y, z in prof], up=(0, 0, 1), soft=0.001)
        k.bolt((s * (CX + PL / 2), 0.0, AZ), "+x" if s > 0 else "-x", size=0.014)
    xi = CX - PL / 2
    k.bar("lever", (-xi, 0.10, AZ + 0.005), (xi, 0.10, AZ + 0.005), 0.08, 0.02, cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)), weld=True)
    k.box("warn", (0.0, 0.10, AZ + 0.016), (0.035, 0.035, 0.002), soft=0.0)
    k.tube("steel", (-xi, 0.10, AZ - 0.07), (xi, 0.10, AZ - 0.07), 0.022, seg=20)
    k.tube("pad", (-xi + 0.01, 0.10, AZ - 0.07), (xi - 0.01, 0.10, AZ - 0.07), 0.04, seg=36, soft=0.01)
    for py, pz in ((0.06, AZ - 0.205), (0.17, AZ - 0.205)):
        k.box("lever", (0, py, pz), (2 * xi, 0.09, 0.012), soft=0.002)
        k.box("grip", (0, py, pz + 0.008), (2 * xi - 0.02, 0.08, 0.004), soft=0.001)
        k.text("emboss", "HAMMER STRENGTH", (0, py, pz + 0.0105), 0.022, rx=0.0, rz=math.pi, depth=0.0008)

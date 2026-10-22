"""Hammer Strength Impact Suppression Platform, 6 x 8 ft stand-alone with ramp.

Built by eye from Hammer Strength's render (refs/: ref_01, a three-quarter from the front corner), held to the variant
picked: 8 ft along the bar, 6 ft deep.
Axes: metres, floor z = 0, the bar along x, the lifter stands on the wood facing -y.
Structure: a black steel band round the edge with a flat top rim, silver button-head bolts in its outer face; inside it
the wood centre (strips running along the bar) between two black rubber drop zones, all flush; a black steel gusset in
each corner lettered HAMMER STRENGTH. The variant comes "with ramp", but the only photo (shared by every variant) shows
none, so the ramp is left out until there is a photo of it.
"""
import math

IN = 0.0254
LOOK = {
    "wood": dict(color=(0.62, 0.42, 0.22), rough=0.55, coat=0.0,
                 grain=dict(dark=(0.40, 0.24, 0.10), scale=40.0, distortion=3.0, along="Y")),    # light strip veneer
    "rubber": dict(color=(0.014, 0.014, 0.016), rough=0.85, coat=0.0, bump=(1100, 0.07)),
    "frame": dict(color=(0.02, 0.02, 0.022), rough=0.42, coat=0.1, bump=(900, 0.05)),
    "emboss": dict(color=(0.05, 0.05, 0.055), rough=0.5, coat=0.0),
    "bolt": dict(color=(0.7, 0.7, 0.72), rough=0.25, metal=1.0, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 32, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "top": (0, 89, 1.0)}
DETAILS = {"detail_corner": ((1.55, -1.45, 0.42), (1.12, -0.82, 0.04), 45)}   # a corner gusset, the bolts

LX, LY = 8 * 12 * IN, 6 * 12 * IN    # along the bar, deep
H = 2.5 * IN                          # the platform's height
BAND, RIM = 0.005, 0.028              # the steel band's wall, its top rim's width
WOOD = 1.0                            # the wood centre's width (x)
GUS = 0.20                            # the corner gussets' legs


def build(k):
    # the band round the edge: an outer wall and the flat rim on top, one bent strip
    hx, hy = LX / 2, LY / 2
    loop = [(0, -hy), (hx, -hy), (hx, hy), (-hx, hy), (-hx, -hy), (0, -hy)]
    k.sweep("frame", [(x, y, H - 0.002) for x, y in loop], k.rect(RIM, 0.004), soft=0.001)
    k.sweep("frame", [(x, y, H / 2 - 0.002) for x, y in loop], k.rect(BAND * 2, H - 0.004), soft=0.001)
    # the surfaces inside it, flush with the rim's top
    xi, yi = hx - BAND, hy - BAND
    zt = H - 0.0005
    k.box("wood", (0, 0, zt / 2), (WOOD, 2 * yi, zt), soft=0.0008)
    for s in (1, -1):
        w = xi - WOOD / 2
        k.box("rubber", (s * (WOOD / 2 + w / 2), 0, zt / 2), (w, 2 * yi, zt), soft=0.0008)
    # the corner gussets, lettered along their long edge
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = sx * (hx - BAND), sy * (hy - BAND)
            tri = [(cx, cy), (cx - sx * GUS, cy), (cx, cy - sy * GUS)]
            prof = [(cx - x, y - cy) for x, y in tri]           # a vertical sweep lays (u, v) on (-x, y)
            k.sweep("frame", [(cx, cy, H - 0.002), (cx, cy, H + 0.003)], prof, soft=0.0008)
            ang = math.atan2(-sy, sx) + (math.pi if sx == sy else 0.0)   # along the long edge, its top towards the middle
            ux, uy = -math.sin(ang), math.cos(ang)
            mx, my = cx - sx * GUS / 3, cy - sy * GUS / 3
            for i, line in enumerate(("HAMMER", "STRENGTH")):
                d = (0.5 - i) * 0.018
                k.text("emboss", line, (mx + ux * d, my + uy * d, H + 0.0034), 0.014, rz=ang, rx=0.0, depth=0.0008)
    # silver button heads in the band, on each side
    for s in (1, -1):
        for x in (-0.9, -0.3, 0.3, 0.9):
            k.cyl("bolt", (x, s * (hy + BAND + 0.0012), H * 0.55), 0.007, 0.003, axis="y", seg=20, soft=0.0008)
        for y in (-0.55, 0.0, 0.55):
            k.cyl("bolt", (s * (hx + BAND + 0.0012), y, H * 0.55), 0.007, 0.003, axis="x", seg=20, soft=0.0008)

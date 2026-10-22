"""TITAN Series Power Rack Lifting Platform, for a 36 in deep rack, lying on the floor.

Built by eye from Titan's photos (refs/: ref_01 the whole platform, ref_12 its dimensions, ref_06 a corner plate,
ref_09 the frame's bolted joint, ref_02 / ref_13 in use under a rack), held to Titan's drawing: 120.5 in across, 108.75 in
deep, the wood 41 in wide running the full depth, its tongue 46.5 in out past the rubber into the rack.
Axes: metres, floor z = 0, the bar along x, the lifter on the wide part facing -y, the rack over the tongue at +y.
Structure: a black steel tube frame round the T, bolted at its joints; inside it the hardwood (strips along y, a joint
across where the tongue starts, TITAN burnt in at the front, UNLEASH YOUR TITAN at the tongue's end) between rubber
drop zones of four tiles a side; a black corner plate with the Titan mark at each outer corner.
"""
import math

IN = 0.0254
LOOK = {
    "wood": dict(color=(0.56, 0.35, 0.15), rough=0.5, coat=0.0, spec=0.3,
                 grain=dict(dark=(0.38, 0.21, 0.07), scale=9.0, distortion=2.5, along="X")),     # rubberwood strips
    "burn": dict(color=(0.07, 0.035, 0.012), rough=0.6, coat=0.0),
    "rubber": dict(color=(0.02, 0.02, 0.022), rough=0.85, coat=0.0, spec=0.15, bump=(1600, 0.10)),
    "frame": dict(color=(0.012, 0.012, 0.014), rough=0.4, coat=0.1, bump=(900, 0.06)),
    "emboss": dict(color=(0.05, 0.05, 0.055), rough=0.45, coat=0.0),
    "bolt": dict(color=(0.6, 0.6, 0.62), rough=0.3, metal=1.0, coat=0.0),
    "seam": dict(color=(0.08, 0.05, 0.03), rough=0.8, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 32, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "top": (0, 89, 1.0)}
DETAILS = {"detail_corner": ((1.95, -1.80, 0.45), (1.42, -1.25, 0.03), 45)}   # the front corner plate, a joint's bolt

HX, HW = 120.5 / 2 * IN, 41 / 2 * IN          # half across, the wood's half width
D, TONGUE = 108.75 * IN, 46.5 * IN
Y0, Y2 = -D / 2, D / 2
Y1 = Y2 - TONGUE                               # where the tongue starts
H = 1.75 * IN                                  # the platform's height
FW = 1.0 * IN                                  # the frame tube's width
GUS = 0.17                                     # the corner plates' legs


def build(k):
    e = FW / 2
    # the frame: one tube round the T (its centreline half a tube in from the edge), started mid front
    loop = [(0, Y0 + e), (HX - e, Y0 + e), (HX - e, Y1 - e), (HW - e, Y1 - e), (HW - e, Y2 - e), (-HW + e, Y2 - e),
            (-HW + e, Y1 - e), (-HX + e, Y1 - e), (-HX + e, Y0 + e), (0, Y0 + e)]
    k.sweep("frame", [(x, y, H / 2) for x, y in loop], k.rect(FW, H, 0.002), soft=0.001)
    # the hardwood, flush with the frame: the wide part's run and the tongue, a joint between
    zt = H - 0.0005
    wx = 2 * (HW - FW)
    k.box("wood", (0, (Y0 + FW + Y1 - FW) / 2, zt / 2), (wx, Y1 - Y0 - 2 * FW, zt), soft=0.0006)
    k.box("wood", (0, (Y1 - FW + Y2 - FW) / 2, zt / 2), (wx, Y2 - Y1, zt), soft=0.0006)
    k.box("seam", (0, Y1 - FW, zt), (wx - 0.004, 0.0015, 0.0004), soft=0.0)
    k.text("burn", "TITAN", (0, Y0 + FW + 0.36, zt + 0.00015), 0.21, rz=math.pi / 2, rx=0.0, depth=0.0003)
    k.text("burn", "UNLEASH YOUR TITAN", (0, Y2 - FW - 0.07, zt + 0.00015), 0.05, rz=math.pi, rx=0.0, depth=0.0003)
    # the rubber drop zones: four tiles a side
    rw, rd = HX - HW, Y1 - Y0 - 2 * FW
    for s in (1, -1):
        for i in range(2):
            for j in range(2):
                cx = s * (HW - FW + (i + 0.5) * rw / 2)
                cy = Y0 + FW + (j + 0.5) * rd / 2
                k.box("rubber", (cx, cy, zt / 2), (rw / 2 - 0.0015, rd / 2 - 0.0015, zt), soft=0.0015)
    # the corner plates at the six outer corners, each with the Titan mark
    for cx, cy in ((HX, Y0), (-HX, Y0), (HX, Y1), (-HX, Y1), (HW, Y2), (-HW, Y2)):
        sx, sy = (1 if cx > 0 else -1), (1 if cy > Y0 + 0.01 else -1)
        tri = [(cx, cy), (cx - sx * GUS, cy), (cx, cy - sy * GUS)]
        k.sweep("frame", [(cx, cy, H - 0.001), (cx, cy, H + 0.004)], [(cx - x, y - cy) for x, y in tri], soft=0.0008)
        mx, my = cx - sx * GUS * 0.3, cy - sy * GUS * 0.3
        k.disc("emboss", (mx, my, H + 0.0045), 0.022, 0.016, 0.001, axis="z", seg=40)
        k.box("emboss", (mx, my, H + 0.0045), (0.006, 0.026, 0.001), rz=math.atan2(-sy, sx) + math.pi / 2, soft=0.0)
    # the frame's bolted joints: a button head each side of the wood on the front, and midway along the sides
    for x in (-HW, HW):
        k.cyl("bolt", (x, Y0 - 0.0012, H / 2), 0.0075, 0.003, axis="y", seg=20, soft=0.0008)
    for s in (1, -1):
        k.cyl("bolt", (s * (HX + 0.0012), (Y0 + Y1) / 2, H / 2), 0.0075, 0.003, axis="x", seg=20, soft=0.0008)
        k.cyl("bolt", (s * (HW + 0.0012), (Y1 + Y2) / 2, H / 2), 0.0075, 0.003, axis="x", seg=20, soft=0.0008)

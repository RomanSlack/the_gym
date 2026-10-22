"""Hammer Strength Plate-Loaded Glute Drive (PL-GLD), Charcoal frame / Black upholstery, the lever down on its stops.

Built by eye from the dealer gallery (refs/: ref_14 a true side view, ref_13 a true front view, ref_01 the studio
three-quarter in the picked colourway, ref_11 / ref_12 the three-quarters in silver, ref_08-10 close-ups of the band pegs
and the seat), held to Life Fitness's 68 x 58.5 x 40 in (173 x 149 x 102 cm, L x W x H), four storage horns.
Axes: metres, floor z = 0; the user sits on the seat, upper back on the round back pad at +y, feet on the platform at -y,
hips under the roller, facing -y; x+ = the user's left.
Structure: the base (side rails, cross bars, the centre rail forward to the platform); the angled grit platform on four
legs; the seat on its post; the round back pad on its stand; the rear uprights (two storage horns each), the top cross
tube, the axle at their tops; the lever: two black arms from hubs on the axle forward and down to the double hip roller,
a loading horn and an upright grip at each end, rubber stops under the arms; band pegs on the base.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 16, 1.0), "front": (0, 6, 1.0), "side": (-90, 3, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_roller": ((-0.85, -0.70, 1.20), (0.0, 0.10, 0.70), 45),     # the roller, the grips, the horns
    "detail_pivot": ((1.25, 1.30, 1.10), (0.55, 0.62, 0.65), 45),       # the axle, a hub, the storage horns
}

FOOT_H = 0.02
RAIL = (0.076, 0.10)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
T = 0.076
BX = 0.40                          # base side rails (x)
UX = 0.55                          # rear uprights (x)
UY = 0.62                          # rear uprights (y)
PIV = (UY, 0.86)                   # the axle (y, z)
AX = 0.42                          # the lever's arms (x)
ROLL = (0.03, 0.70)                # the roller's axis (y, z)
Y0, Y1 = -0.32, 0.86               # base side rails


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def bar_x(k, mat, y, z, x0, x1, w=T, h=None):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h or w, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def horn(k, mat, y, z, s, x_face, length):
    k.cyl(mat, (x_face + s * 0.006, y, z), 0.045, 0.012, axis="x", seg=32, soft=0.003)
    k.tube("steel", (x_face + s * 0.012, y, z), (x_face + s * length, y, z), 0.025, seg=32)
    k.cyl(mat, (x_face + s * (length + 0.008), y, z), 0.029, 0.016, axis="x", seg=32, soft=0.004)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    # ---- the base: side rails, cross bars (front, under the uprights), the rails out to the uprights, the centre rail
    for s in (1, -1):
        x = s * BX
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.045)
        k.bar("frame", (x + s * RAIL[0] / 2, UY, RAIL_Z), (s * (UX + T / 2), UY, RAIL_Z), 0.076, RAIL[1],
              cut0=((x + s * RAIL[0] / 2, 0, 0), (1, 0, 0)), weld=True)
        foot(k, s * UX, UY + 0.10)
        # band pegs out of the side rail
        for py in (-0.10, 0.30):
            k.tube("steel", (x + s * RAIL[0] / 2, py, RAIL_Z), (x + s * (RAIL[0] / 2 + 0.10), py, RAIL_Z), 0.012, seg=16)
            k.cyl("plastic", (x + s * (RAIL[0] / 2 + 0.105), py, RAIL_Z), 0.016, 0.01, axis="x", seg=16, soft=0.002)
    xi = BX - RAIL[0] / 2
    for y_ in (Y0 + 0.04, 0.25, UY):
        bar_x(k, "frame", y_, RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    k.bar("frame", (0, Y0 + 0.04 - 0.038, RAIL_Z), (0, -0.88, RAIL_Z), 0.076, RAIL[1], cut0=((0, Y0 + 0.002, 0), Y), weld=True)
    k.box("plastic", (0, -0.884, RAIL_Z), (0.08, 0.008, RAIL[1] + 0.004), soft=0.002)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (BX + RAIL[0] / 2 + 0.0004, 0.45, RAIL_Z + 0.013 - i * 0.026), 0.021, rz=math.pi / 2, depth=0.0004)
    # ---- the angled platform: grit top on its plate, a cross frame, four legs (the front pair on its own cross bar)
    t = math.radians(10)
    pc = (-0.62, 0.45)
    k.box("grip", (0, pc[0], pc[1] + 0.002), (0.60, 0.44, 0.004), rx=-t, soft=0.001)     # the front edge higher
    k.box("frame", (0, pc[0], pc[1] - 0.018), (0.62, 0.46, 0.04), rx=-t, soft=0.004)
    for py in (-0.80, -0.44):
        zt = pc[1] - 0.038 - (py - pc[0]) * math.tan(t)
        bar_x(k, "frame", py, RAIL_Z, -0.25, 0.25, 0.06, RAIL[1])
        for s in (1, -1):
            k.bar("frame", (s * 0.275, py, FOOT_H), (s * 0.275, py, zt + 0.02), 0.05, 0.05,
                  cut1=((0, py, zt), (0, math.sin(t), math.cos(t))))
            foot(k, s * 0.275, py)
    # ---- the seat on its post, on a short rail between the front cross bar and the back pad's cross bar
    k.bar("frame", (0, -0.05, RAIL_TOP), (0, -0.05, 0.35), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.bar("frame", (0, -0.05, RAIL_Z), (0, Y0 + 0.04 + 0.038, RAIL_Z), 0.06, RAIL[1], cut1=((0, Y0 + 0.078, 0), Y), weld=True)
    k.bar("frame", (0, -0.05, RAIL_Z), (0, 0.25 - 0.038, RAIL_Z), 0.06, RAIL[1], cut1=((0, 0.212, 0), Y), weld=True)
    k.box("frame", (0, -0.05, 0.36), (0.30, 0.24, 0.02), soft=0.003)
    k.pad("pad", (0, -0.05, 0.415), (0.40, 0.30, 0.09), r=0.04)
    # ---- the round back pad on its stand (a half round along x, the user's upper back on its front)
    k.bar("frame", (0, 0.25, RAIL_TOP), (0, 0.25, 0.36), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, 0.27, 0.37), (0.40, 0.10, 0.03), soft=0.003)
    k.cyl("pad", (0, 0.27, 0.48), 0.11, 0.52, axis="x", seg=40, soft=0.02)
    # ---- the rear uprights, the top cross tube, the storage horns, the axle
    for s in (1, -1):
        x = s * UX
        k.bar("frame", (x, UY, RAIL_TOP), (x, UY, PIV[1] + 0.07), T, T, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", (x, UY, PIV[1] + 0.075), (T + 0.004, T + 0.004, 0.01), soft=0.002)
        for zh in (0.28, 0.56):
            horn(k, "frame", UY, zh, s, x + s * T / 2, 0.20)
        k.box("warn", (x - s * (T / 2 + 0.001), UY, 0.45), (0.002, 0.05, 0.05), soft=0.0)
        k.box("rubber", (x - s * (T / 2 + 0.03), UY - 0.06, PIV[1] - 0.11), (0.06, 0.05, 0.05), soft=0.006)   # the stop
        k.box("frame", (x - s * (T / 2 + 0.01), UY - 0.06, PIV[1] - 0.14), (0.02, 0.06, 0.03), soft=0.002)
    bar_x(k, "frame", UY, 0.60, -(UX - T / 2), UX - T / 2)
    k.tube("steel", (-UX - 0.06, PIV[0], PIV[1]), (UX + 0.06, PIV[0], PIV[1]), 0.022, seg=28)
    for s in (1, -1):
        k.bolt((s * (UX + 0.06), PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.028)
    # ---- the lever: a hub on the axle each side, the arm forward and down to the roller's end, the roller shaft
    for s in (1, -1):
        x = s * AX
        k.tube("lever", (x - 0.04, PIV[0], PIV[1]), (s * (UX - T / 2), PIV[0], PIV[1]), 0.045, seg=32)
        k.sweep("lever", [(x, PIV[0], PIV[1]), (x, 0.30, 0.86), (x, ROLL[0], ROLL[1])], k.rect(0.06, 0.10, 0.01),
                bend=0.18, up=(1, 0, 0), soft=0.002)
        horn(k, "lever", ROLL[0], ROLL[1], s, x + s * 0.03, 0.28)
        g0 = (x, ROLL[0] + 0.08, ROLL[1] + 0.03)
        k.sweep("lever", [g0, (x, ROLL[0] + 0.12, ROLL[1] + 0.20), (x + s * 0.03, ROLL[0] + 0.06, ROLL[1] + 0.36)],
                k.circle(0.015, 18), bend=0.05, soft=0.0015)
        k.tube("rubber", (x + s * 0.012, ROLL[0] + 0.10, ROLL[1] + 0.26), (x + s * 0.03, ROLL[0] + 0.06, ROLL[1] + 0.36), 0.02, seg=20)
    k.tube("lever", (-AX + 0.03, ROLL[0], ROLL[1]), (AX - 0.03, ROLL[0], ROLL[1]), 0.03, seg=24)     # the roller tube
    for x0, x1 in ((-0.36, -0.005), (0.005, 0.36)):
        k.tube("pad", (x0, ROLL[0], ROLL[1]), (x1, ROLL[0], ROLL[1]), 0.10, seg=40, soft=0.012)

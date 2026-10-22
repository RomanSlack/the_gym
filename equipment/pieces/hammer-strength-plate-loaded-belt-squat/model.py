"""Hammer Strength Plate-Loaded Belt Squat (PL-BSQ), Charcoal, dip attachment not included (the variant picked), the
lever down on its stop.

Built by eye from the dealer gallery (refs/: ref_01 the studio three-quarter (it shows the dip attachment, left out here),
ref_02 / ref_10 true side views, ref_03-09 the three-quarters in use), held to Life Fitness's 78 x 63 x 64 in (198 x 160
x 163 cm, L x W x H), the foot plates 10.75 in off the floor.
Axes: metres, floor z = 0, the user stands on the two foot platforms at +y facing -y (the machine); x+ = the user's left.
Structure: the base (side rails, cross bars); the tower (two posts on the front cross bar, the bolted top beam, the
posts' tops the grips); the rear legs rising and bending forward into the side beams back to the tower; the axle in
blocks under the side beams' rear ends; the lever (one heavy beam) on the axle sloping down to the belt anchor plate with
its four holes between the platforms, a front and a rear weight rod each side, down on a rubber stop; two storage horns
on each rear leg; the platforms (grit tops on frames, legs at their outer ends); band pegs; the belt hook hanger.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal, as its studio photo
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "plate": dict(color=(0.20, 0.205, 0.21), rough=0.4, metal=0.5, coat=0.0),                        # the anchor plate
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "grip": dict(color=(0.05, 0.05, 0.052), rough=0.9, coat=0.0, spec=0.25, bump=(2500, 0.25)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "seam": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-145, 16, 1.1), "front": (180, 6, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (35, 18, 1.1)}
DETAILS = {
    "detail_anchor": ((0.65, 1.05, 0.85), (0.0, 0.35, 0.45), 45),       # the anchor plate between the platforms
    "detail_pivot": ((-0.95, -1.35, 1.45), (0.0, -0.78, 1.05), 45),     # the axle, lever hub, rear legs, horns
}

FOOT_H = 0.02
RAIL = (0.076, 0.10)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
BX = 0.38                          # base side rails (x)
FX = 0.30                          # tower posts, rear legs, side beams (x)
T = 0.076
Y_TOWER, Y_REAR, Y_FRONT = 0.12, -0.95, 0.35
Z_BEAM = 1.20
PIV = (-0.76, 1.05)
TIP = (0.16, 0.50)                 # the lever's front end
PLAT_Z = 10.75 * 0.0254


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
    # ---- the base
    for s in (1, -1):
        x = s * BX
        k.bar("frame", (x, Y_FRONT + 0.04, RAIL_Z), (x, Y_REAR - 0.05, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y_FRONT + 0.04, 1), (Y_REAR - 0.05, -1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.045)
        for by in (0.25, -0.20, -0.60):
            k.cyl("bolt", (x + s * (RAIL[0] / 2 + 0.002), by, RAIL_Z), 0.008, 0.004, axis="x", seg=16, soft=0.001)
        # band pegs out of the rail's outer face
        k.tube("steel", (x + s * RAIL[0] / 2, -0.40, RAIL_Z), (x + s * (RAIL[0] / 2 + 0.11), -0.40, RAIL_Z), 0.012, seg=16)
    xi = BX - RAIL[0] / 2
    for y_ in (Y_FRONT, Y_TOWER, Y_REAR):
        bar_x(k, "frame", y_, RAIL_Z, -xi, xi, RAIL[0], RAIL[1])
    # ---- the tower: two posts on the front cross bar, the top beam bolted across, the posts' tops the grips
    for s in (1, -1):
        x = s * FX
        k.bar("frame", (x, Y_TOWER, RAIL_TOP), (x, Y_TOWER, 1.45), T, T, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", (x, Y_TOWER, 1.455), (T + 0.004, T + 0.004, 0.01), soft=0.002)
        k.tube("rubber", (x, Y_TOWER - T / 2 - 0.022, 1.28), (x, Y_TOWER - T / 2 - 0.022, 1.44), 0.022, seg=22)
        for z in (1.29, 1.43):
            k.box("frame", (x, Y_TOWER - T / 2 - 0.011, z), (0.03, 0.022, 0.02), soft=0.002)
        k.box("warn", (x + s * (T / 2 + 0.001), Y_TOWER, 0.95), (0.002, 0.05, 0.05), soft=0.0)
    bar_x(k, "frame", Y_TOWER, Z_BEAM, -(FX - T / 2), FX - T / 2)
    for bx in (-0.16, -0.05, 0.05, 0.16):
        k.bolt((bx, Y_TOWER + T / 2, Z_BEAM), "+y", size=0.016)
    # ---- the rear legs bending forward into the side beams, onto the tower posts' backs; the axle blocks; storage horns
    for s in (1, -1):
        x = s * FX
        k.sweep("frame", [(x, Y_REAR, RAIL_TOP), (x, Y_REAR, 0.80), (x, -0.70, Z_BEAM), (x, Y_TOWER - T / 2 - 0.01, Z_BEAM)],
                k.rect(T, T, 0.008), bend=0.22, up=(1, 0, 0), cut0=((0, 0, RAIL_TOP), Z),
                cut1=((0, Y_TOWER - T / 2, 0), Y), weld=True, soft=0.002)
        k.box("frame", (x, PIV[0], (PIV[1] + Z_BEAM) / 2 - 0.02), (T, 0.10, Z_BEAM - PIV[1] + 0.04), soft=0.004)
        for zh in (0.30, 0.62):
            horn(k, "frame", Y_REAR, zh, s, x + s * T / 2, 0.24)
    pc = (FX + T / 2 + 0.002, -0.35, Z_BEAM)
    k.box("placard", pc, (0.004, 0.17, 0.06), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("seam", line, (pc[0] + 0.0023, pc[1], pc[2] + 0.011 - i * 0.022), 0.019, rz=math.pi / 2, depth=0.0003)
    k.tube("steel", (-FX - 0.06, PIV[0], PIV[1]), (FX + 0.06, PIV[0], PIV[1]), 0.025, seg=28)
    for s in (1, -1):
        k.bolt((s * (FX + 0.06), PIV[0], PIV[1]), "+x" if s > 0 else "-x", size=0.03)
    # ---- the lever: its hub on the axle, the beam down to the tip, the anchor plate on, two weight rods a side
    k.tube("lever", (-0.07, PIV[0], PIV[1]), (0.07, PIV[0], PIV[1]), 0.05, seg=32)
    t = math.atan2(PIV[1] - TIP[1], TIP[0] - PIV[0])
    k.bar("lever", (0, PIV[0], PIV[1]), (0, TIP[0], TIP[1]), 0.10, 0.14, up=(0, math.sin(t), math.cos(t)))
    yb, zb = TIP[0] - 0.05, TIP[1] - 0.02      # the plate runs back into the beam's tip, welded
    prof = [(0.0, -0.05), (0.71, -0.04), (0.73, 0.02), (0.0, 0.06)]
    k.sweep("plate", [(-0.006, yb, zb), (0.006, yb, zb)], [(-dy, dz) for dy, dz in prof], up=Z, soft=0.001)
    for i in range(4):
        hy = yb + 0.24 + i * 0.13
        k.sweep("hole", [(-0.0075, hy, zb), (0.0075, hy, zb)], [(-0.025, -0.015), (0.025, -0.015), (0.0, 0.03)], up=Z, soft=0.0)
    for f in (0.28, 0.70):
        hy, hz = PIV[0] + (TIP[0] - PIV[0]) * f, PIV[1] - (PIV[1] - TIP[1]) * f
        for s in (1, -1):
            horn(k, "lever", hy, hz, s, s * 0.05, 0.50)
    # its stop: a post on the tower cross bar, a rubber bumper under the beam's tip
    tz = TIP[1] - 0.07 / math.cos(t)
    k.bar("frame", (0, TIP[0] - 0.02, RAIL_TOP), (0, TIP[0] - 0.02, tz - 0.05), 0.06, 0.06, cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("frame", (0, Y_TOWER, RAIL_TOP + 0.006), (0.08, 0.04, 0.012), soft=0.001)
    k.box("rubber", (0, TIP[0] - 0.02, tz - 0.025), (0.07, 0.07, 0.05), soft=0.006)
    # the belt hook hanger on the left tower post
    k.sweep("steel", [(FX + T / 2, Y_TOWER, 1.00), (FX + T / 2 + 0.06, Y_TOWER, 1.00), (FX + T / 2 + 0.07, Y_TOWER, 1.05)],
            k.circle(0.008, 12), bend=0.015, soft=0.001)
    # ---- the platforms: a grit top on a frame each side of the anchor plate, its outer end on two legs
    for s in (1, -1):
        xc = s * 0.26
        y0, y1 = Y_FRONT - 0.05, 1.00
        k.box("grip", (xc, (y0 + y1) / 2, PLAT_Z - 0.002), (0.40, y1 - y0, 0.004), soft=0.001)
        k.box("lever", (xc, (y0 + y1) / 2, PLAT_Z - 0.024), (0.42, y1 - y0 + 0.01, 0.04), soft=0.004)
        for lx in (xc - 0.16, xc + 0.16):
            k.bar("frame", (lx, y1 - 0.08, FOOT_H), (lx, y1 - 0.08, PLAT_Z - 0.044), 0.06, 0.06, cut0=((0, 0, FOOT_H), Z))
            foot(k, lx, y1 - 0.08)
        k.box("frame", (xc, Y_FRONT, (RAIL_TOP + PLAT_Z - 0.044) / 2), (0.30, 0.06, PLAT_Z - 0.044 - RAIL_TOP), soft=0.003)

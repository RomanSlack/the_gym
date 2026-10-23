"""Hammer Strength Plate-Loaded Glute Ham / Reverse Hyper Combo (PL-GHRH), Silver frame / Black arms and upholstery.

Built by eye from the dealer gallery (refs/: ref_02 / ref_03 the true side from the near side, loaded, in use; ref_12
the side empty; ref_09 / ref_10 the three-quarter from the reverse-hyper end; ref_11 / ref_06 / ref_07 square on to the
reverse-hyper end; ref_01 the maker's studio render in Charcoal; ref_13 / ref_14 the foot unit's close-ups; ref_04 /
ref_05 reverse hyper in use; ref_08 the handles). Life Fitness gives 88 x 40 x 53 in (224 x 102 x 135 cm), 2 storage
horns, 2 arms of up to 4 x 45 lb each. The photos agree with the 88 in length and the 40 in width, not with the 53 in
height: in every side photo the pad stands at 0.64 of the length and the foot unit above it. Scale from the people and the
plates instead: ref_02 / ref_03 at 3.3 mm/px (a 1.78 m man kneeling up, knee to crown; the 25 lb plates 0.36 m across),
which puts the pad's top at 1.36 m (53.5 in: the spec's height is likely the pad's) and the foot unit's top at 1.61 m.
Side-view numbers off ref_02 as (y, z): y = (px - 586) * 0.0033, z = (845 - py) * 0.0033.
Axes: metres, floor z = 0; y runs the length, the glute ham's foot unit at -y, the reverse hyper's end at +y; the side
the photos are taken from (the arc plate, the Hammer Strength plate on the rail) is +x.
Use: glute ham: kneel or lie on the pad facing +y, the ankles between the upper pads and the lower rollers, the soles
against the curved foot plate; reverse hyper: lie face down on the pad, head to -y, the hips at its +y end, the ankles in
the straps of the two pendulum arms hanging under it, the hands on the foot unit's handles.
Structure: two side portals (bent tube, legs splayed along the length) on floor rails that curve in to the narrow
glute ham base; a step off each portal leg; the pad frame (bent side plates bolted to the portals' tops, a front bracket,
a rear cross member) and the two cushions with the rolled knee hump at the -y end; the two pendulum arms on one axle
through the portals, each braced to its own outer hub, a loading horn each; the foot unit's column on a pivot yoke, its
angle set by an arc plate bolted to it and pinned through the post at the base's end (the "single pivot adjustment on
an arc"), the post carrying the two storage horns.
"""
import math

LOOK = {
    "frame": dict(color=(0.25, 0.26, 0.275), rough=0.33, metal=0.8, coat=0.0, bump=(1400, 0.05)),   # Silver (ref_12)
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "zinc": dict(color=(0.62, 0.63, 0.66), rough=0.3, metal=1.0, coat=0.0, bump=(900, 0.03)),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "blue": dict(color=(0.05, 0.22, 0.6), rough=0.4, coat=0.0),
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "strap": dict(color=(0.016, 0.016, 0.017), rough=0.75, coat=0.0, sheen=0.4, bump=(2200, 0.1)),
}
VIEWS = {"three_quarter": (125, 16, 1.0), "side": (90, 4, 1.0), "end": (180, 5, 1.0),
         "back_three_quarter": (35, 18, 1.0)}
DETAILS = {
    "detail_foot_unit": ((0.95, -1.35, 1.75), (0.0, -0.55, 1.38), 50),     # the rollers, upper pads, foot plate, handles
    "detail_arc": ((0.95, -1.55, 0.85), (0.04, -0.75, 0.42), 45),          # the pivot yoke, arc plate, post, horns
    "detail_pendulum": ((1.15, 1.45, 0.80), (0.0, 0.32, 0.85), 45),        # the arms' hubs, braces, horns, straps
}

FOOT_H = 0.02
RW, RH = 0.076, 0.10                # floor rails: across, tall (ref_02: 30 px)
RZ = FOOT_H + RH / 2
RT = FOOT_H + RH                    # the rails' top
XP = 0.40                           # the portals' planes (ref_11: their legs under the pad's edges, the feet 1.02 apart)
XG = 0.20                           # the narrow glute ham base's rails
YE = 1.02                           # the rail ends (+/-), the feet under them: 88 in overall with the feet
PW, PT = 0.064, 0.076               # the portal tube: in its plane, across it
# the portal, (y, z) along its centreline (ref_02): the -y leg straight up at px 615, bent at py 590 and running up to
# the top's -y end; the level top; the +y leg's diagonal down to its bend at py 610 and straight down at px 840
PORTAL = [(0.10, RT), (0.10, 0.84), (0.38, 1.17), (0.64, 1.17), (0.84, 0.78), (0.84, RT)]
ZS = 0.44                           # the steps (ref_02: py 705-730), a stub off each leg along the length
STEP = (-0.25, YE)                  # the -y stub's end (ref_02: px 490), the +y one's
XS = XP + PT / 2 + 0.006            # the pad frame's side plates, on the portals' outer faces
SIDE = [(-0.03, 1.07), (0.27, 1.07), (0.37, 1.17), (0.64, 1.17)]   # their path: low under the hump (ref_02: bolts at
                                    # px 600 / 640, py 520), up to the portal top (px 715 / 750, py 490)
ZT = 1.36                           # the cushions' top (ref_02: py 432)
HUMP = (0.06, 1.16, 0.20)           # the knee hump's roll at the -y end: centre (y, z), radius (ref_02: the pad's end at
                                    # px 548, py 500)
PIV = (0.32, 1.10)                  # the pendulum axle (ref_02: the arms' tops), through the portals' -y legs
XA = 0.075                          # the arms (ref_11: 0.15 apart)
XH = 0.30                           # each arm's outer hub, its brace's top
ZH = 0.42                           # the arms' loading horns (ref_02: the plates' centre at py 718)
ZB = 0.16                           # the arms' bottom ends, the straps' shackles
GP = (-0.60, 0.185)                 # the foot unit's column pivot (ref_02 / ref_12: the column's foot in its yoke)
LEAN = math.radians(6)              # the column's lean back to -y at this setting (ref_02: 5-6 deg, ref_12: 9)
C1Z = 1.24                          # the column's straight run ends at the lower rollers' height
YB = -0.50                          # the foot unit's top bar (y), its centre at ZB2
ZB2 = 1.565
UPR = 0.055                         # the upper pads' radius (ref_14), hung from the bar
LR_ = (-0.46, 1.24, 0.085)          # the lower ankle rollers: (y, z, r): 0.09 between them and the upper pads (ref_13)
YPOST = -0.90                       # the post at the base's end (ref_02: the storage plates' centre at px 318)
ARC = (0.50, 0.62, 0.56)            # the arc plate's band round the pivot: inner, outer, the pin holes' radius
ZSH = 0.36                          # the storage horns (ref_02: py 735)


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.09, 0.09, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.19, 0.075, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.072, y, 0.0042), 0.0065, 0.0008, seg=14)


def horn(k, mat, c, axis, length, collar=0.045):
    """A loading / storage horn out of a face at c along axis ('+x' / '-x'): the collar, the steel sleeve, the end disc."""
    s = 1 if axis[0] == "+" else -1
    x, y, z = c
    k.cyl(mat, (x + s * 0.006, y, z), collar, 0.012, axis="x", seg=32, soft=0.003)
    k.tube("chrome", (x + s * 0.012, y, z), (x + s * length, y, z), 0.025, seg=32)
    k.cyl(mat, (x + s * (length + 0.008), y, z), 0.029, 0.016, axis="x", seg=32, soft=0.004)


def build(k):
    Z = (0, 0, 1)
    UPX = (1, 0, 0)
    sn, cs = math.sin(LEAN), math.cos(LEAN)
    # ---- the base: each side's floor rail along its portal, curving in to the narrow glute ham base (ref_09 / ref_12:
    # the near rail's sweep in at px 370-445), on rubber feet under the ends; plastic end caps; the two bolts mid-rail
    # (ref_02: px 545 / 585) and the Hammer Strength plate on the near rail (ref_02: px 700-750)
    for s in (1, -1):
        rail = [(s * XP, YE, RZ), (s * XP, -0.30, RZ), (s * XG, -0.52, RZ), (s * XG, -YE, RZ)]
        k.sweep("frame", rail, k.rect(RW, RH, 0.006), bend=0.16, up=Z)
        for y in (YE, -YE):
            x = s * (XP if y > 0 else XG)
            d = 1 if y > 0 else -1
            k.box("plastic", (x, y + d * 0.004, RZ), (RW + 0.004, 0.008, RH + 0.004), soft=0.002)
            foot(k, x, y - d * 0.06)
        for y in (-0.14, 0.0):
            k.bolt((s * (XP + RW / 2), y, RZ), "+x" if s > 0 else "-x", size=0.016, nut=RW)
    k.box("placard", (XP + RW / 2 + 0.001, 0.46, RZ), (0.002, 0.16, 0.05), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (XP + RW / 2 + 0.0024, 0.46, RZ + 0.011 - i * 0.021), 0.017, rz=math.pi / 2, depth=0.0004)
    # the narrow base's two cross beams: under the column's pivot and under the post
    for y in (GP[0], YPOST):
        k.bar("frame", (-XG + RW / 2, y, RZ), (XG - RW / 2, y, RZ), RH, RW, up=(0, 1, 0),
              cut0=((-XG + RW / 2, 0, 0), (1, 0, 0)), cut1=((XG - RW / 2, 0, 0), (1, 0, 0)), weld=True)
    # ---- the portals, one per side: bent tube from foot to foot, both feet cut onto the rail; the low cross tube
    # between the -y legs (ref_01); the steps, a stub off each leg's outer side along the length, rubber tread, cap
    for s in (1, -1):
        k.sweep("frame", [(s * XP, y, z) for y, z in PORTAL], k.rect(PW, PT, 0.006), bend=0.09, up=UPX,
                cut0=((0, 0, RT), Z), cut1=((0, 0, RT), Z), weld=True)
        for y0, y1 in ((PORTAL[0][0] - PW / 2, STEP[0]), (PORTAL[-1][0] + PW / 2, STEP[1])):
            d = 1 if y1 > y0 else -1
            k.bar("frame", (s * XP, y0, ZS), (s * XP, y1, ZS), PT, PW, up=Z, cut0=((0, y0, 0), (0, 1, 0)), weld=True)
            k.box("plastic", (s * XP, y1 + d * 0.004, ZS), (PT + 0.004, 0.008, PW + 0.004), soft=0.002)
            k.box("rubber", (s * XP, (y0 + y1) / 2 + d * 0.01, ZS + PW / 2 + 0.003), (PT - 0.006, abs(y1 - y0) - 0.05, 0.006),
                  soft=0.002)
    k.bar("frame", (-XP + PT / 2, PORTAL[0][0], 0.22), (XP - PT / 2, PORTAL[0][0], 0.22), PW, PW, up=Z,
          cut0=((-XP + PT / 2, 0, 0), (1, 0, 0)), cut1=((XP - PT / 2, 0, 0), (1, 0, 0)), weld=True)
    # the how-to placard on the far portal's +y leg, up its diagonal, facing the reverse hyper's end (ref_09)
    (ya, za), (yb, zb) = PORTAL[4], PORTAL[3]
    L = math.hypot(yb - ya, zb - za); uy, uz = (yb - ya) / L, (zb - za) / L
    ny, nz = uz, -uy                                   # the diagonal's outward normal (toward +y)
    al = math.atan2(-uy, uz)
    for dz, mat, size in ((0.0, "placard", (0.05, 0.002, 0.24)), (0.05, "blue", (0.036, 0.0008, 0.05)),
                          (-0.02, "blue", (0.036, 0.0008, 0.05)), (-0.08, "blue", (0.036, 0.0008, 0.05))):
        t = 0.5 + dz / L
        off = PW / 2 + 0.001 + (0.0015 if mat == "blue" else 0.0)
        k.box(mat, (-XP, ya + (yb - ya) * t + ny * off, za + (zb - za) * t + nz * off), size, rx=al, soft=0.0)
    # ---- the pad frame: a bent side plate on each portal's outer face (low under the hump, up the ramp, along the
    # portal top), two bolts into the portal top and two into the front bracket; the front bracket across under the
    # hump, a rear cross member between the portal tops
    for s in (1, -1):
        k.sweep("frame", [(s * XS, y, z) for y, z in SIDE], k.rect(0.075, 0.012, 0.003), bend=0.05, up=UPX)
        for y, z, grip in ((0.45, 1.17, 0.012 + PT), (0.56, 1.17, 0.012 + PT), (0.035, 1.07, 0.012), (0.165, 1.07, 0.012)):
            k.bolt((s * (XS + 0.006), y, z), "+x" if s > 0 else "-x", size=0.018, nut=grip)
    k.bar("frame", (-XS + 0.006, 0.10, 1.07), (XS - 0.006, 0.10, 1.07), 0.18, 0.05, up=Z,
          cut0=((-XS + 0.006, 0, 0), (1, 0, 0)), cut1=((XS - 0.006, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (-XP + PT / 2, 0.50, 1.17), (XP - PT / 2, 0.50, 1.17), 0.05, 0.064, up=Z,
          cut0=((-XP + PT / 2, 0, 0), (1, 0, 0)), cut1=((XP - PT / 2, 0, 0), (1, 0, 0)), weld=True)
    # ---- the two cushions side by side, split along the length (ref_11): flat on top, the -y end rolled down over the
    # knee hump onto the front bracket, the +y end square with a rounded edge; the bottom on the bracket (z 1.095) and on
    # the portal tops (z 1.202), the ramp between
    hy, hz, hr = HUMP
    top = [(0.615, ZT), (0.635, ZT - 0.01), (0.64, ZT - 0.03)]
    prof = top + [(0.64, 1.202), (0.38, 1.202), (0.27, 1.095), (-0.07, 1.095), (-0.125, 1.11)]
    prof += [(hy + hr * math.cos(math.radians(a)), hz + hr * math.sin(math.radians(a))) for a in range(180, 85, -10)]
    prof += [(0.12, ZT), (0.40, ZT)]
    uv = [(-y, z) for y, z in prof]
    for x0, x1 in ((0.006, 0.41), (-0.41, -0.006)):
        k.sweep("pad", [(x0, 0, 0), (x1, 0, 0)], uv, up=Z, soft=0.022)
    # ---- the pendulum arms: one axle through both portals' -y legs and the side plates, nuts outside; each arm on an
    # inner hub, braced up and out to its own outer hub (ref_11 / ref_01: the diagonals), spacers between; the arm's
    # loading horn out through a sleeve block with the badge (ref_01); a shackle and the ankle strap at its foot
    py, pz = PIV
    k.tube("steel", (-XS - 0.02, py, pz), (XS + 0.02, py, pz), 0.02, seg=24)
    for s in (1, -1):
        k.bolt((s * (XS + 0.006), py, pz), "+x" if s > 0 else "-x", size=0.03)
        k.tube("steel", (s * (XH + 0.025), py, pz), (s * (XP - PT / 2), py, pz), 0.03, seg=24)       # spacer to the portal
        k.tube("steel", (s * (XA + 0.03), py, pz), (s * (XH - 0.025), py, pz), 0.026, seg=24)         # between the hubs
        k.tube("lever", (s * (XA - 0.03), py, pz), (s * (XA + 0.03), py, pz), 0.045, seg=32, soft=0.003)
        k.tube("lever", (s * (XH - 0.025), py, pz), (s * (XH + 0.025), py, pz), 0.04, seg=32, soft=0.003)
        k.bar("lever", (s * XA, py, pz), (s * XA, py, ZB), 0.05, 0.076, up=(0, 1, 0))
        k.box("plastic", (s * XA, py, ZB - 0.004), (0.054, 0.08, 0.008), soft=0.002)
        k.bar("lever", (s * XA, py, 0.80), (s * XH, py, pz - 0.03), 0.04, 0.04, up=(0, 1, 0),
              cut0=((s * (XA + 0.025), 0, 0), (1, 0, 0)), weld=True)
        k.box("lever", (s * XA, py, ZH + 0.02), (0.07, 0.096, 0.16), soft=0.004)
        k.box("placard", (s * XA, py + 0.049, ZH + 0.05), (0.06, 0.002, 0.03), soft=0.0)
        for i, line in enumerate(("HAMMER", "STRENGTH")):
            k.text("label", line, (s * XA, py + 0.0505, ZH + 0.056 - i * 0.011), 0.0085, rz=math.pi, depth=0.0003)
        horn(k, "lever", (s * (XA + 0.035), py, ZH), "+x" if s > 0 else "-x", 0.26)
        k.tube("steel", (s * (XA + 0.255), py, ZH + 0.02), (s * (XA + 0.255), py, ZH + 0.05), 0.004, seg=10)   # the
        k.box("plastic", (s * (XA + 0.255), py, ZH + 0.058), (0.012, 0.03, 0.012), soft=0.002)                # tip pin
        # the shackle tab under the arm's end, a D ring, the ankle cuff hanging to the floor
        k.box("lever", (s * XA, py, ZB - 0.032), (0.008, 0.04, 0.05), soft=0.001)
        k.disc("chrome", (s * XA, py, ZB - 0.07), 0.028, 0.02, 0.008, axis="x", seg=24)
        k.box("strap", (s * XA, py + 0.01, ZB - 0.12), (0.05, 0.012, 0.06), soft=0.003)
        k.box("strap", (s * XA, py + 0.04, 0.035), (0.11, 0.17, 0.05), rx=-0.5, soft=0.012)
    # ---- the foot unit's column: a yoke of two cheek plates on the pivot beam, the axle and nuts, the hub; the column
    # leaning back up to the lower rollers' height, then curving up and over (ref_12) into the top bar's -y face
    gy, gz = GP
    for s in (1, -1):
        k.box("frame", (s * 0.046, gy, (RT + 0.25) / 2), (0.008, 0.12, 0.25 - RT), soft=0.002)
        k.bolt((s * 0.05, gy, gz), "+x" if s > 0 else "-x", size=0.024)
    k.tube("steel", (-0.054, gy, gz), (0.054, gy, gz), 0.014, seg=16)
    k.tube("frame", (-0.042, gy, gz), (0.042, gy, gz), 0.042, seg=32, soft=0.003)
    c1 = (0.0, gy - (C1Z - gz) * math.tan(LEAN), C1Z)
    hook = [(0.0, gy, gz), c1, (0.0, c1[1] - 0.015, 1.46), (0.0, c1[1] + 0.045, ZB2), (0.0, YB - 0.04, ZB2)]
    k.sweep("frame", hook, k.rect(0.08, 0.076, 0.006), bend=0.07, up=UPX, cut1=((0, YB - 0.04, 0), (0, 1, 0)), weld=True)
    k.bar("frame", (-0.28, YB, ZB2), (0.28, YB, ZB2), 0.08, 0.08, up=Z)
    for s in (1, -1):
        k.box("plastic", (s * 0.284, YB, ZB2), (0.008, 0.084, 0.084), soft=0.002)
        for x in (0.08, 0.20):
            k.bolt((s * x, YB, ZB2 + 0.04), "+z", size=0.014)
        # the upper pads: a roll each side hung under the bar, end caps
        zu = ZB2 - 0.04 - UPR
        k.tube("pad", (s * 0.03, YB, zu), (s * 0.25, YB, zu), UPR, seg=36, soft=0.01)
        k.cyl("plastic", (s * 0.255, YB, zu), 0.032, 0.012, axis="x", seg=24, soft=0.003)
    # the lower rollers: an arm forward off the column's face to the hub, the shaft across, a roller each side
    ly, lz, lr = LR_
    n = (0.0, cs, sn)                                   # the column's +y face normal
    fp = (0.0, c1[1] + 0.04 * cs, C1Z + 0.04 * sn)
    k.bar("frame", (0.0, fp[1] - 0.01, lz), (0.0, ly, lz), 0.06, 0.06, up=Z, cut0=(fp, n), weld=True)
    k.box("frame", (0.0, ly, lz), (0.07, 0.09, 0.09), soft=0.004)
    k.tube("chrome", (-0.30, ly, lz), (0.30, ly, lz), 0.02, seg=20)
    for s in (1, -1):
        k.tube("pad", (s * 0.035, ly, lz), (s * 0.285, ly, lz), lr, seg=40, soft=0.012)
        k.cyl("plastic", (s * 0.29, ly, lz), 0.04, 0.012, axis="x", seg=24, soft=0.003)
    # the curved foot plate behind the ankles (ref_12 / ref_13): from under the hook's top down past the roller arm
    curve = [(-0.565, ZB2 - 0.04), (-0.585, 1.42), (-0.592, 1.30), (-0.578, 1.19), (-0.55, 1.13)]
    band = [(-y + 0.004, z) for y, z in curve] + [(-y - 0.004, z) for y, z in reversed(curve)]
    k.sweep("lever", [(-0.21, 0, 0), (0.21, 0, 0)], band, up=Z, soft=0.002)
    # the handles: a loop off each end of the top bar, out, down and back in to the foot plate's edge (ref_01 / ref_08),
    # a foam grip on the outer upright
    for s in (1, -1):
        loop = [(s * 0.28, YB, ZB2), (s * 0.36, YB, ZB2), (s * 0.36, -0.56, 1.33), (s * 0.20, -0.588, 1.33)]
        k.sweep("frame", loop, k.rect(0.03, 0.03, 0.004), bend=0.035, up=(0, 1, 0), cut0=((s * 0.28, 0, 0), (1, 0, 0)), weld=True)
        g0 = (s * 0.36, YB - 0.006, ZB2 - 0.05); g1 = (s * 0.36, -0.554, 1.37)
        k.tube("rubber", g0, g1, 0.021, seg=24, soft=0.004)
    # ---- the adjustment: the arc plate bolted to the column's +x face, a band round the pivot with the pin holes;
    # the post at the base's end, the pop pin through its top into a hole, the storage horns through it lower down
    # (ref_12 / ref_09: the zinc plate rising to the column, the warning label, the knob), a brace from the post to the
    # pivot beam
    r0, r1, rp = ARC
    a0, a1 = 3.0, 50.0
    pts = [(gy - r1 * math.sin(math.radians(a)), gz + r1 * math.cos(math.radians(a))) for a in range(int(a0), int(a1) + 1, 3)]
    pts += [(gy - r0 * math.sin(math.radians(a)), gz + r0 * math.cos(math.radians(a))) for a in range(int(a1), int(a0) - 1, -3)]
    xa = 0.038
    k.sweep("zinc", [(xa, 0, 0), (xa + 0.01, 0, 0)], [(-y, z) for y, z in pts], up=Z, soft=0.002)
    for r in (0.53, 0.60):
        k.bolt((xa + 0.01, gy - r * sn, gz + r * cs), "+x", size=0.016, nut=0.086)
    apin = math.degrees(math.asin((gy - YPOST) / rp))
    for i in range(-3, 3):
        a = math.radians(apin + 6 * i)
        if i != 0:
            k.cyl("hole", (xa + 0.0105, gy - rp * math.sin(a), gz + rp * math.cos(a)), 0.008, 0.001, axis="x", seg=16)
    aw = math.radians(46)
    k.box("warn", (xa + 0.0105, gy - 0.585 * math.sin(aw), gz + 0.585 * math.cos(aw)), (0.0008, 0.035, 0.035),
          rx=-aw, soft=0.0)
    xpo = xa + 0.01 + 0.038                              # the post, its -x face against the arc plate
    zpin = gz + rp * math.cos(math.radians(apin))
    k.bar("frame", (xpo, YPOST, RT), (xpo, YPOST, zpin + 0.06), 0.076, 0.076, up=(0, 1, 0), cut0=((0, 0, RT), Z), weld=True)
    k.box("plastic", (xpo, YPOST, zpin + 0.064), (0.08, 0.08, 0.008), soft=0.002)
    k.tube("steel", (xpo + 0.038, YPOST, zpin), (xpo + 0.075, YPOST, zpin), 0.008, seg=12)
    k.cyl("plastic", (xpo + 0.08, YPOST, zpin), 0.02, 0.016, axis="x", seg=24, soft=0.004)
    k.box("frame", (xpo + 0.043, YPOST, zpin), (0.01, 0.05, 0.06), soft=0.002)                     # the pin's boss
    horn(k, "frame", (xpo + 0.038, YPOST, ZSH), "+x", 0.24)
    horn(k, "frame", (xa + 0.01, YPOST, ZSH), "-x", 0.27)
    k.bar("frame", (xpo, YPOST + 0.038, 0.48), (xpo, gy - 0.02, RT), 0.038, 0.05, up=(1, 0, 0),
          cut0=((0, YPOST + 0.038, 0), (0, 1, 0)), cut1=((0, 0, RT), Z), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Glute ham (ref_02, the start: lying level on the pad facing +y, the knees over the hump, the ankles between the
    upper pads and the lower rollers, the balls of the feet on the foot plate, toes down) for a short, a middle and a
    tall user at this column setting; reverse hyper (ref_05, at rest: the trunk face down along the pad, head to -y,
    the hips just past its +y end, the legs hanging straight down, the hands on the handles) for the middle user."""
    out = {}
    ly, lz, lr = LR_
    for label, H in (("ghd_short", 1.60), ("ghd_middle", 1.78), ("ghd_tall", 1.95)):
        ank = (ly - 0.01, lz + lr + 0.045)              # between the roller's top and the upper pad's bottom
        ball = (0.0, ank[0] - 0.039 * H, ank[1] - 0.073 * H)
        out[label] = dict(H=H, ball=ball, face=(0, 1), sole=-90, shank=86, thigh=88, trunk=90, neck=95,
                          arm=150, forearm=30, arm_out=40)
    H = 1.78
    hip = (0.66, ZT + 0.10)
    ank = (hip[0], hip[1] - (0.245 + 0.246) * H)
    out["rh_middle"] = dict(H=H, ball=(0.0, ank[0] + 0.039 * H, ank[1] - 0.073 * H), face=(0, -1), sole=-90,
                            shank=0, thigh=0, trunk=90, neck=95, arm=78, forearm=88, arm_out=10)
    return out

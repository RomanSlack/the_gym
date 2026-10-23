"""Hammer Strength Fixed Pad Glute/Ham (BW-GHF), Charcoal frame / Black upholstery.

Built by eye from the one picture there is (refs/ref_01: the maker's studio three-quarter from the near side, the foot
unit on the left; the dealers only carry the same render, GG Fitness in red), held to Life Fitness's 74 x 34 x 51 in
(188 x 86 x 130 cm, D x W x H), and laid out from the user (README 2b) where the shot can't show a size.
Axes: metres, floor z = 0; y runs the length, the foot unit at -y, the hip pad at +y; the side the shot is taken from
(the how-to placard, the Hammer Strength label) is +x.
Use: lie face down over the hip pad facing +y, the ankles between the upper and lower rollers, the soles on the back
plate behind them; raise the trunk from hanging to level about the hips and knees. The handles beside the back plate
serve reverse hyper work with the head at the foot unit.
Structure (ref_01): two side rails on the floor; at the foot unit's end each side a leg leaning in to the top beam and a
brace back down to the rail (the A, the placard on the near leg); the column pivoted on its yoke by the step plate,
leaning back, its top bent over in a C to the upper rollers' hub, the lower rollers on a short arm, the back plate behind
with a handle window each side; its angle (the "horizontal adjustment to fit all users") set by the two zinc arc plates
bolted to the column just under the C and pinned in the clevis on the top beam; at the pad's end a fixed post each side
curving out into an arched leg on its foot (the Hammer Strength label on the near rail here), a notched zinc plate inside each post, the pad's
ladder carriage between them pinned at a notch (the "vertical adjustment for resistance"), the split half-round hip
pad on its top rail, a band peg out past the end; the low step plate between the rails ("walk-through").
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
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
}
VIEWS = {"three_quarter": (62, 14, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-140, 18, 1.0)}
DETAILS = {
    "detail_foot_unit": ((0.85, -1.15, 1.45), (0.0, -0.30, 1.05), 50),     # the rollers, the C, back plate, handles
    "detail_arc": ((0.95, -1.25, 0.95), (0.0, -0.45, 0.70), 45),           # the arc plates, the clevis, the A frame
    "detail_pad": ((1.05, 1.05, 1.25), (0.0, 0.40, 0.85), 45),             # the hip pad, the carriage, notches, peg
}

FOOT_H = 0.02
RW, RH = 0.076, 0.10                # the side rails: across, tall
RZ = FOOT_H + RH / 2
RT = FOOT_H + RH
XR = 0.36                           # the side rails and the pad end's posts (x); the feet flanged out to the 34 in
Y0, Y1 = -0.90, 0.35                # the rails' ends: the foot unit's end (on feet), the pad end's posts
YF = 0.80                           # the pad end's arched legs land here (ref_01: flared well out); the band pegs
                                    # reach 74 in overall
LT = (-0.66, 0.56)                  # the foot unit end's frame: the legs' tops and the top beam (y, z), under the pin
P0 = (-0.05, 0.20)                  # the column's pivot (ref_01: its yoke beside the step plate's -y end)
C1 = (-0.42, 0.90)                  # the column's straight run ends here, under the C (ref_01: leaning ~28 deg)
UH = (-0.42, 1.22, 0.075)           # the upper rollers: (y, z, r); their top 1.295 = the spec's 51 in
LH = (-0.34, 1.00, 0.07)            # the lower rollers on the arm: 0.09 between them for the ankle
YBP = -0.51                         # the back plate (y): behind the upper rollers, the soles on it
ARC = (0.74, 0.81)                  # the arc plates' band round the pivot (inner, outer)
YP = 0.35                           # the pad end's posts and the carriage (y)
XZ = XR - RW / 2 - 0.005            # the notched zinc plates' centre plane (x), on the posts' inner faces
XC = XZ - 0.005 - 0.025             # the carriage's posts (x), 0.05 square, against the zinc plates
ZTR = 0.93                          # the carriage's top rail (centre), the hip pad on it
PADR = 0.17                         # the hip pad halves: half-rounds across, radius
ZS = 0.22                           # the step plate's top


def foot(k, x, y):
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.09, 0.09, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.19, 0.075, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.072, y, 0.0042), 0.0065, 0.0008, seg=14)


def across(k, mat, y, z, x0, x1, w=0.076, h=None):
    """A bar across (along x) between two faces at x = +/-, cut and welded to them."""
    h = h or w
    k.bar(mat, (x0, y, z), (x1, y, z), w, h, up=(0, 0, 1), cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z = (0, 0, 1)
    UPX = (1, 0, 0)
    # ---- the base: the side rails on feet at the foot unit's end, end caps; the low end beam between them there;
    # the column's pivot beam; the step plate's beam and the step plate (rubber tread) with three bolts (ref_01)
    for s in (1, -1):
        k.bar("frame", (s * XR, Y0, RZ), (s * XR, Y1 + 0.035, RZ), RW, RH, up=Z)
        k.box("plastic", (s * XR, Y0 - 0.004, RZ), (RW + 0.004, 0.008, RH + 0.004), soft=0.002)
        foot(k, s * XR, Y0 + 0.06)
    xi = XR - RW / 2
    across(k, "frame", Y0 + 0.05, RZ, -xi, xi, w=0.10, h=RH)
    across(k, "frame", P0[0], RZ, -xi, xi, w=0.076, h=RH)
    across(k, "frame", 0.14, RZ, -xi, xi, w=0.076, h=RH)
    for x in (-0.15, 0.15):                             # the step's four short posts off the two beams
        for y in (-0.04, 0.14):
            k.box("frame", (x, y, (RT + ZS - 0.012) / 2), (0.05, 0.05, ZS - 0.012 - RT), soft=0.002)
    k.box("lever", (0.0, 0.11, ZS - 0.006), (0.50, 0.30, 0.012), soft=0.003)
    k.box("rubber", (0.0, 0.11, ZS + 0.002), (0.48, 0.28, 0.004), soft=0.002)
    for d in (-0.045, 0.0, 0.045):                      # the step beam's three through-bolts in the near rail (ref_01)
        k.bolt((XR + RW / 2, 0.14 + d, RZ), "+x", size=0.016, nut=RW)
    # ---- the foot unit's end: each side's leg leaning in from the rail's end to the top beam, the brace back down to
    # the rail (the A), the top beam across; the how-to placard up the near leg (ref_01)
    ly, lz = LT
    for s in (1, -1):
        leg = [(s * XR, Y0 + 0.04, RT), (s * XR, Y0 + 0.04, 0.30), (s * XR, ly, lz)]   # up, then curving in (ref_01)
        k.sweep("frame", leg, k.rect(0.07, RW, 0.006), bend=0.16, up=UPX, cut0=((0, 0, RT), Z), weld=True)
        k.bar("frame", (s * XR, ly + 0.03, lz - 0.04), (s * XR, -0.32, RT), 0.06, RW - 0.01, up=UPX,
              cut1=((0, 0, RT), Z), weld=True)
    across(k, "frame", ly, lz, -XR + RW / 2, XR - RW / 2)
    ya, za = Y0 + 0.04, 0.30
    L = math.hypot(ly - ya, lz - za); uy, uz = (ly - ya) / L, (lz - za) / L
    al = math.atan2(-uy, uz)
    for t, mat, size, dx in ((0.5, "placard", (0.002, 0.07, 0.24), 0.0), (0.66, "blue", (0.0008, 0.05, 0.06), 0.0012),
                             (0.5, "blue", (0.0008, 0.05, 0.06), 0.0012), (0.34, "blue", (0.0008, 0.05, 0.06), 0.0012)):
        k.box(mat, (XR + RW / 2 + 0.001 + dx, ya + (ly - ya) * t, za + (lz - za) * t), size, rx=al, soft=0.0)
    # ---- the column: the yoke's cheeks on the pivot beam, the axle, the hub; the straight run leaning back to C1,
    # then the C bending back behind the back plate and over to the upper rollers' hub (ref_01)
    py, pz = P0
    for s in (1, -1):
        k.box("frame", (s * 0.046, py, (RT + 0.27) / 2), (0.008, 0.12, 0.27 - RT), soft=0.002)
        k.bolt((s * 0.05, py, pz), "+x" if s > 0 else "-x", size=0.024)
    k.tube("steel", (-0.054, py, pz), (0.054, py, pz), 0.014, seg=16)
    k.tube("frame", (-0.042, py, pz), (0.042, py, pz), 0.042, seg=32, soft=0.003)
    uy_, uz_, ur = UH
    path = [(0.0, py, pz), (0.0, C1[0], C1[1]), (0.0, YBP - 0.04, 1.02), (0.0, YBP - 0.03, 1.15), (0.0, uy_ - 0.04, uz_)]
    k.sweep("frame", path, k.rect(0.076, 0.076, 0.006), bend=0.07, up=UPX)
    k.tube("frame", (-0.045, uy_, uz_), (0.045, uy_, uz_), 0.045, seg=32, soft=0.003)              # the upper hub
    vy, vz, vr = LH
    k.bar("frame", (0.0, C1[0], C1[1]), (0.0, vy, vz), 0.06, 0.06, up=UPX)                          # the lower arm
    k.tube("frame", (-0.045, vy, vz), (0.045, vy, vz), 0.04, seg=32, soft=0.003)                    # the lower hub
    for (cy, cz, r) in (UH, LH):
        k.tube("chrome", (-0.30, cy, cz), (0.30, cy, cz), 0.019, seg=20)
        for s in (1, -1):
            k.tube("pad", (s * 0.05, cy, cz), (s * 0.29, cy, cz), r, seg=40, soft=0.012)
            k.disc("chrome", (s * 0.294, cy, cz), 0.03, 0.02, 0.008, axis="x", seg=28)            # the end bushing
    # the back plate behind the rollers (the soles on it), on the C's front; a handle each side: the plate's two arms
    # out to a round upright, its grip (ref_01: the window frame on the far side)
    k.box("lever", (0.0, YBP, 1.065), (0.44, 0.012, 0.29), soft=0.01)
    for s in (1, -1):
        for z in (1.18, 0.95):
            k.box("lever", (s * 0.27, YBP, z), (0.10, 0.012, 0.04), soft=0.004)
        k.tube("lever", (s * 0.335, YBP, 0.92), (s * 0.335, YBP, 1.21), 0.016, seg=20, soft=0.002)
        k.tube("rubber", (s * 0.335, YBP, 0.985), (s * 0.335, YBP, 1.145), 0.02, seg=24, soft=0.004)
    # ---- the horizontal adjustment: a zinc arc plate bolted to each face of the column just under the C, the band
    # round the pivot with its holes; the clevis on the top beam round both plates, the pop pin through, the knob on +x
    r0, r1 = ARC
    rp = (r0 + r1) / 2
    lean = math.atan2(py - C1[0], C1[1] - pz)
    apin = math.degrees(math.atan2(py - ly, 0.68 - pz))
    zpin = pz + math.sqrt(rp ** 2 - (py - ly) ** 2)
    a0, a1 = math.degrees(lean) - 2, apin + 10
    pts = [(py - r1 * math.sin(math.radians(a)), pz + r1 * math.cos(math.radians(a))) for a in _rng(a0, a1)]
    pts += [(py - r0 * math.sin(math.radians(a)), pz + r0 * math.cos(math.radians(a))) for a in _rng(a1, a0)]
    xa = 0.038
    apin = math.degrees(math.asin((py - ly) / rp))
    for s in (1, -1):
        xo = s * (xa + 0.01)
        k.sweep("zinc", [(s * xa, 0, 0), (xo, 0, 0)] if s > 0 else [(xo, 0, 0), (s * xa, 0, 0)], [(-y, z) for y, z in pts],
                up=Z, soft=0.002)
        for r in (0.755, 0.795):
            k.bolt((xo, py - r * math.sin(lean), pz + r * math.cos(lean)), "+x" if s > 0 else "-x", size=0.016, nut=0.096)
        for i in range(-3, 2):
            a = math.radians(apin + 5 * i)
            if i != 0:
                k.cyl("hole", (xo + s * 0.0005, py - rp * math.sin(a), pz + rp * math.cos(a)), 0.008, 0.001, axis="x", seg=16)
        aw = math.radians(apin - 8)
        k.box("warn", (xo + s * 0.0005, py - 0.74 * math.sin(aw), pz + 0.74 * math.cos(aw)), (0.0008, 0.03, 0.03),
              rx=-aw, soft=0.0)
    xc = xa + 0.01 + 0.003
    ztop = pz + math.sqrt(r1 ** 2 - (py - ly) ** 2) + 0.012
    for s in (1, -1):
        k.box("frame", (s * (xc + 0.005), ly, (lz + 0.038 + ztop) / 2), (0.01, 0.08, ztop - lz - 0.038), soft=0.002)
    k.box("frame", (0.0, ly, ztop + 0.005), (2 * xc + 0.02, 0.08, 0.01), soft=0.002)
    k.tube("steel", (-xc - 0.012, ly, zpin), (xc + 0.05, ly, zpin), 0.008, seg=12)
    k.cyl("frame", (xc + 0.018, ly, zpin), 0.022, 0.016, axis="x", seg=24, soft=0.002)
    k.cyl("plastic", (xc + 0.056, ly, zpin), 0.02, 0.016, axis="x", seg=24, soft=0.004)
    # ---- the pad end: each side's post up from the rail's end, capped; the arched leg out of it to its foot (the
    # Hammer Strength label on the near one, ref_01); the cross beam between the arches
    for s in (1, -1):
        k.bar("frame", (s * XR, YP, RT), (s * XR, YP, 0.82), RW, RW, up=(0, 1, 0), cut0=((0, 0, RT), Z), weld=True)
        k.box("plastic", (s * XR, YP, 0.824), (RW + 0.004, RW + 0.004, 0.008), soft=0.002)
        arch = [(s * XR, YP + RW / 2, 0.64), (s * XR, 0.62, 0.56), (s * XR, YF, 0.30), (s * XR, YF, FOOT_H)]
        k.sweep("frame", arch, k.rect(RW, RW, 0.006), bend=0.12, up=UPX, cut0=((0, YP + RW / 2, 0), (0, 1, 0)), weld=True)
        foot(k, s * XR, YF)
    k.box("placard", (XR + RW / 2 + 0.001, 0.26, RZ), (0.002, 0.16, 0.05), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, (XR + RW / 2 + 0.0024, 0.26, RZ + 0.011 - i * 0.021), 0.017, rz=math.pi / 2, depth=0.0004)
    across(k, "frame", YF, 0.30, -XR + RW / 2, XR - RW / 2, w=0.07)
    # ---- the vertical adjustment: a notched zinc plate bolted inside each post, the carriage's posts riding against
    # them, a pop pin through each into a notch; the carriage: two posts, the top rail, two lower rails (the lower one
    # bent down in the middle, ref_01)
    zc0 = 0.50
    for s in (1, -1):
        k.box("zinc", (s * XZ, YP, 0.77), (0.01, 0.11, 0.50), soft=0.003)        # standing above its post (ref_01)
        for z in (0.58, 0.76):
            k.bolt((s * (XR + RW / 2), YP, z), "+x" if s > 0 else "-x", size=0.016, nut=RW + 0.01)
        for z in (0.66, 0.72, 0.78, 0.84, 0.90):
            k.box("hole", (s * (XZ - 0.0052), YP + 0.03, z), (0.0008, 0.035, 0.03), soft=0.0)
        k.bar("frame", (s * XC, YP, zc0), (s * XC, YP, ZTR + 0.03), 0.05, 0.05, up=(0, 1, 0))
        k.box("plastic", (s * XC, YP, zc0 - 0.004), (0.054, 0.054, 0.008), soft=0.002)
        k.tube("steel", (s * (XZ - 0.005), YP + 0.03, 0.78), (s * (XC - 0.06), YP + 0.03, 0.78), 0.008, seg=12)
        k.cyl("frame", (s * (XC - 0.034), YP + 0.03, 0.78), 0.02, 0.016, axis="x", seg=24, soft=0.002)
        k.cyl("plastic", (s * (XC - 0.066), YP + 0.03, 0.78), 0.018, 0.014, axis="x", seg=24, soft=0.004)
    xi = XC - 0.025
    across(k, "frame", YP, ZTR, -xi, xi, w=0.06)
    across(k, "frame", YP, 0.74, -xi, xi, w=0.05)
    k.sweep("frame", [(-xi, YP, 0.62), (-0.14, YP, 0.62), (-0.06, YP, 0.56), (0.06, YP, 0.56), (0.14, YP, 0.62), (xi, YP, 0.62)],
            k.rect(0.05, 0.05, 0.005), bend=0.05, up=(0, 1, 0), cut0=((-xi, 0, 0), (1, 0, 0)), cut1=((xi, 0, 0), (1, 0, 0)),
            weld=True)
    # the band pegs: a rod off each carriage post's top out past the end, the stop disc at its root (ref_01)
    for s in (1, -1):
        k.tube("lever", (s * XC, YP + 0.025, ZTR), (s * XC, 0.94, ZTR), 0.016, seg=20)
        k.cyl("lever", (s * XC, 0.52, ZTR), 0.035, 0.012, axis="y", seg=28, soft=0.003)
        k.cyl("plastic", (s * XC, 0.944, ZTR), 0.019, 0.008, axis="y", seg=20, soft=0.002)
    # ---- the hip pad: two half-rounds across, split in the middle, on boards on the top rail (ref_01)
    zb = ZTR + 0.03
    half = [(-PADR * math.cos(math.radians(a)), zb + 0.012 + PADR * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    for x0, x1 in ((0.012, 0.27), (-0.27, -0.012)):
        k.box("plastic", ((x0 + x1) / 2, YP, zb + 0.006), (x1 - x0, 2 * PADR - 0.01, 0.012), soft=0.002)
        k.sweep("pad", [(x0, 0, 0), (x1, 0, 0)], [(-(YP + y), z) for y, z in half], up=Z, soft=0.025)


def _rng(a, b, step=3.0):
    n = max(2, int(abs(b - a) / step) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """At the start of a glute ham raise, level: face down facing +y, the ankles between the rollers, the balls of the
    feet on the back plate, toes down, the thighs over the hip pad, the trunk level beyond it; a 1.60, a 1.78 and a
    1.95 m user at this column setting (the arc moves the rollers for them)."""
    out = {}
    (uy, uz, ur), (vy, vz, vr) = UH, LH
    ank = ((uy + vy) / 2 + 0.01, (uz - ur + vz + vr) / 2 + 0.01)
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        out[label] = dict(H=H, ball=(0.0, ank[0] - 0.039 * H, ank[1] - 0.073 * H), face=(0, 1), sole=-90, shank=84,
                          thigh=86, trunk=92, neck=95, arm=150, forearm=30, arm_out=40)
    return out

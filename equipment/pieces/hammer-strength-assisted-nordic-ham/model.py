"""Hammer Strength Plate-Loaded Assisted Nordic Ham (PL-ANH), Charcoal frame / Black lever and upholstery, at rest.

Built by eye from the dealer gallery (refs/: ref_13 / ref_14 the true side from the frame's side, empty and loaded;
ref_12 the true front; ref_01 the studio three-quarter; ref_03, ref_07, ref_09, ref_10 in use at the start of the rep,
ref_08 at the bottom), held to Life Fitness's 77 x 53 x 58 in (196 x 135 x 147 cm, L x W x H; W across the horns).
Side-view numbers off ref_14 at 393 px/m (the 1.96 m between the feet), as (f, z): f forward from the frame's post.
Axes: metres, floor z = 0; the user kneels on the kneeler facing -y, the ankles under the ankle roller at the back,
hugs the chest roller and lowers the body forward and down about the knees; x+ = the user's left.
Handedness: the frame and both levers stand on the user's LEFT (ref_09 / ref_10 from the right show it behind her,
ref_08 / ref_14 from the left show it in front of her); the rollers reach across to the right.
Structure: the base (front and rear cross bars on rubber feet, the A side's floor rails, the outer one rising into the
rear arch, the right side's raised rail, the centre rail); the A frame: two planes of a post (bent forward below the knee
pivot), a front leg and a curved rear brace, gussets at the apex; the kneeler (two cushions on a plate, on two cross
members, the front one on a post); the ankle roller off the inner rear brace; the chest lever on an axle through the
posts' lower legs at the knee, the chest roller on its arm, pinned in a quadrant at the lever's top; the counterweight
arm hung from the apex, its loading horn, the link from the chest lever's tail, the rubber stop; two storage horns.
"""
import math

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
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
VIEWS = {"three_quarter": (-62, 18, 1.0), "front": (0, 6, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_pivot": ((1.25, -0.75, 0.80), (0.42, -0.10, 0.50), 45),      # the knee axle, the link, the counterweight's foot
    "detail_top": ((-0.60, -1.50, 1.75), (0.15, -0.45, 1.30), 45),      # the chest roller, its arm, the quadrant, the apex
}


def P(f, l, z):
    """(forward from the post, toward the user's left, up) -> world."""
    return (l, -f, z)


FOOT_H = 0.02
FR = 0.076                         # floor rails, square
RZ = FOOT_H + FR / 2               # their centre
RT = FOOT_H + FR                   # their top
AW, AT = 0.07, 0.05                # the A members: in their plane, across it
LI, LO = 0.28, 0.56                # the A frame's two planes (l): the inner one beside the kneeler
FX0, FX1 = 0.82, -1.10             # the front and rear cross bars (f): feet 1.96 m apart outside them
FM = -0.50                         # the kneeler's rear cross bar (f), under the right rail's back foot
LR = -0.46                         # the right side's raised rail (l)
RRZ = 0.46                         # its height (ref_10: just under the kneeler)
APEX = (0.0, 1.40)                 # the post's top (ref_14: 510, 320 px)
KNEE = (0.02, 0.80)                # where the post bends forward (ref_13)
PFOOT = (0.22, RT)                 # the post's foot, forward of the bend
FLEG = (0.76, RT)                  # the front leg's foot (ref_14: 200, 860 px)
BRACE = [(-0.22, 0.88), (-0.27, 0.55), (-0.28, RT)]   # the rear brace's curve down from the apex (ref_13)
PIV = (0.12, 0.50)                 # the chest lever's axle: where the lever crosses the posts' lower legs (ref_13), just
                                   # under and behind the knee (a 1.78 m user's knee at f 0.19, z 0.63)
CW = (-0.01, 1.24)                 # the counterweight arm's axle, through the posts under the apex
CWH = (-0.18, 0.31)                # its loading horn at rest (ref_14: 585, 745 px)
LC, LW, LK = 0.36, 0.47, 0.415     # the chest lever, the counterweight arm and the link between the planes (l)
TAIL = (0.03, 0.14)                # the chest lever's tail below the axle (ref_13: 500, 810 px)
LTOP = (0.58, 1.40)                # its top, the quadrant's pin (ref_14: 275, 310 px)
ROLL = (0.395, 1.333)              # the chest roller, in front of the chest of a user kneeling upright (ref_07)
KZ = 0.58                          # the kneeler's top: the shins and knees (ref_12)
KF = (-0.30, 0.16, 0.50)           # the kneeler: its back, the split between the cushions, its front
ANK = (-0.25, 0.72)                # the ankle roller: on the shins just above the ankle (0.58 + the shin + its 0.06 radius)


def foot(k, f, l):
    x, y, _ = P(f, l, 0)
    k.box("rubber", (x, y, 0.004 + (FOOT_H - 0.004) / 2), (0.08, 0.08, FOOT_H - 0.004), soft=0.003)
    k.box("rubber", (x, y, 0.002), (0.17, 0.065, 0.004), soft=0.0015)
    for d in (-1, 1):
        k.cyl("hole", (x + d * 0.064, y, 0.0042), 0.0065, 0.0008, seg=14)


def along_l(k, mat, f, z, l0, l1, w=0.06, h=None, caps=(True, True)):
    """A bar across (along l) between two faces at l0 and l1, cut and welded to them."""
    h = h or w
    k.bar(mat, P(f, l0, z), P(f, l1, z), w, h, cut0=(P(0, l0, 0), (1, 0, 0)) if caps[0] else None,
          cut1=(P(0, l1, 0), (1, 0, 0)) if caps[1] else None, weld=True)


def horn(k, mat, f, z, l_face, length):
    k.cyl(mat, P(f, l_face + 0.006, z), 0.045, 0.012, axis="x", seg=32, soft=0.003)
    k.tube("steel", P(f, l_face + 0.012, z), P(f, l_face + length, z), 0.025, seg=32)
    k.cyl(mat, P(f, l_face + length + 0.008, z), 0.029, 0.016, axis="x", seg=32, soft=0.004)


def lerp_z(a, b, z):
    """The f of segment a-b at height z."""
    return a[0] + (b[0] - a[0]) * (z - a[1]) / (b[1] - a[1])


def build(k):
    Z = (0, 0, 1)
    UPL = (1, 0, 0)                # the A members' across-the-plane axis in world
    # ---- the base (ref_01, ref_04, ref_14): the front cross bar, the kneeler's rear cross bar and the short rear bar,
    # on rubber feet; the inner A floor rail and the centre rail between the first two; the outer A floor rail running
    # on back into the rear arch (ref_14); the right side's rail, raised along the kneeler (ref_01, ref_10)
    for f, l0, l1 in ((FX0, LR - 0.04, LO + 0.04), (FX1, LI - 0.04, LO + 0.04)):
        k.bar("frame", P(f, l0, RZ), P(f, l1, RZ), FR, FR, r=0.006)
        for l, d in ((l0, -1), (l1, 1)):
            k.box("plastic", P(f, l + d * 0.004, RZ), (0.008, FR + 0.004, FR + 0.004), soft=0.002)
            foot(k, f + (0.06 if f > 0 else -0.06), l - d * 0.04)
    k.bar("frame", P(FM, LR - 0.04, RZ), P(FM, LO - FR / 2, RZ), FR, FR, cut1=(P(0, LO - FR / 2, 0), (1, 0, 0)), weld=True)
    k.box("plastic", P(FM, LR - 0.044, RZ), (0.008, FR + 0.004, FR + 0.004), soft=0.002)
    foot(k, FM - 0.06, LR)
    fi, fm = FX0 - FR / 2, FM + FR / 2
    for l in (LI, 0.0):
        k.bar("frame", P(fi, l, RZ), P(fm, l, RZ), FR, FR, cut0=(P(fi, 0, 0), (0, 1, 0)), cut1=(P(fm, 0, 0), (0, 1, 0)), weld=True)
    ra = [P(fi, LO, RZ), P(-0.62, LO, RZ), P(-0.74, LO, 0.34), P(-0.98, LO, 0.34), P(FX1 + FR / 2 + 0.02, LO, RZ)]
    k.sweep("frame", ra, k.rect(FR, FR, 0.006), bend=0.10, up=Z, cut0=(P(fi, 0, 0), (0, 1, 0)),
            cut1=(P(FX1 + FR / 2, 0, 0), (0, -1, 0)), weld=True)
    k.box("placard", P(-0.86, LO + FR / 2 + 0.001, 0.34), (0.002, 0.16, 0.05), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, P(-0.86, LO + FR / 2 + 0.0024, 0.351 - i * 0.021), 0.017, rz=math.pi / 2, depth=0.0004)
    rr = [P(FX0, LR, RT), P(0.70, LR, RRZ), P(-0.38, LR, RRZ), P(FM, LR, RT)]
    k.sweep("frame", rr, k.rect(0.076, 0.05, 0.006), bend=0.12, up=UPL, cut0=(P(0, 0, RT), Z), cut1=(P(0, 0, RT), Z), weld=True)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, P(0.30, LR - 0.0252, RRZ + 0.011 - i * 0.021), 0.017, rz=-math.pi / 2, depth=0.0004)
    # ---- the A frame, each plane: the post (straight down from the apex, bent forward below the knee pivot), the
    # front leg and the curved rear brace, both coped to the post; the gusset at the apex, the post's cap
    for l in (LI, LO):
        k.sweep("frame", [P(APEX[0], l, APEX[1]), P(KNEE[0], l, KNEE[1]), P(PFOOT[0], l, PFOOT[1])],
                k.rect(AW, AT, 0.006), bend=0.14, up=UPL, cut1=(P(0, 0, RT), Z), weld=True)
        k.box("plastic", P(APEX[0], l, APEX[1] + 0.004), (AT + 0.004, AW + 0.004, 0.008), soft=0.002)
        f0 = APEX[0] + AW / 2
        k.bar("frame", P(f0, l, 1.32), P(FLEG[0], l, FLEG[1]), AW, AT, up=UPL,
              cut0=(P(f0, 0, 0), (0, -1, 0)), cut1=(P(0, 0, RT), Z), weld=True)
        b0 = APEX[0] - AW / 2
        k.sweep("frame", [P(b0, l, 1.26)] + [P(f, l, z) for f, z in BRACE], k.rect(AW, AT, 0.006), bend=0.16, up=UPL,
                cut0=(P(b0, 0, 0), (0, 1, 0)), cut1=(P(0, 0, RT), Z), weld=True)
        for s in (1, -1):   # the apex gussets, both faces of the plane
            k.box("frame", P(0.0, l + s * (AT / 2 + 0.003), 1.27), (0.006, 0.20, 0.16), soft=0.002)
            for f, z in ((0.06, 1.30), (-0.06, 1.24)):
                k.bolt(P(f, l + s * (AT / 2 + 0.006), z), "+x" if s > 0 else "-x", size=0.014)
    # the storage horns on the outer front leg's face (ref_13: 45 and 25), the warning label low on the inner post
    for z in (0.70, 0.30):
        horn(k, "frame", lerp_z((f0, 1.32), FLEG, z), z, LO + AT / 2, 0.22)
    k.box("warn", P(lerp_z(KNEE, PFOOT, 0.30), LI - AT / 2 - 0.001, 0.30), (0.002, 0.04, 0.04), soft=0.0)
    # the placard on the inner post's face toward the user (ref_09): the badge, the name, two how-to panels
    pf, pl = 0.0, LI - AT / 2 - 0.0015
    k.box("placard", P(pf, pl, 1.12), (0.003, 0.06, 0.34), soft=0.0)
    for i, line in enumerate(("HAMMER", "STRENGTH")):
        k.text("label", line, P(pf, pl - 0.0018, 1.265 - i * 0.012), 0.009, rz=-math.pi / 2, depth=0.0003)
    for z in (1.16, 1.07):
        k.box("blue", P(pf, pl - 0.0016, z), (0.0008, 0.044, 0.07), soft=0.0)
    # ---- the kneeler: two cross members from the right rail (the rear one to the inner rear brace, the front one on
    # its post off the centre rail), the plate, two cushions split ahead of the knee (ref_09 / ref_10)
    zc = 0.46
    fb = lerp_z(BRACE[1], BRACE[2], zc)
    along_l(k, "frame", fb, zc, LR + 0.025, LI - AT / 2, 0.06)
    along_l(k, "frame", 0.42, zc, LR + 0.025, 0.20, 0.06, caps=(True, False))
    k.box("plastic", P(0.42, 0.204, zc), (0.064, 0.008, 0.064), soft=0.002)
    k.bar("frame", P(0.42, 0.0, RT), P(0.42, 0.0, zc - 0.03), 0.06, 0.06, cut0=(P(0, 0, RT), Z), weld=True)
    k.box("label", P(0.42 - 0.031, 0.0, 0.25), (0.001, 0.035, 0.07), rz=math.pi / 2, soft=0.0)
    k.box("frame", P((KF[0] + KF[2]) / 2, 0.0, zc + 0.036), (0.48, KF[2] - KF[0], 0.012), soft=0.002)
    for a, b in ((KF[0], KF[1]), (KF[1], KF[2])):
        L = b - a - 0.006
        out = [(-L / 2, -0.245), (L / 2, -0.245), (L / 2, 0.245), (-L / 2, 0.245)]   # 0.49 wide (ref_04)
        k.shaped_pad("pad", out, P((a + b) / 2, 0.0, KZ - 0.04), Z, (0, -1, 0), 0.08, r=0.035, cushion=0.03)
    # ---- the ankle roller: a shaft off the inner rear brace's face across to the right, the pad round it
    fa, za = ANK
    k.cyl("frame", P(fa, LI - AT / 2 - 0.008, za), 0.04, 0.016, axis="x", seg=28, soft=0.003)
    k.tube("steel", P(fa, LI - AT / 2 - 0.016, za), P(fa, -0.235, za), 0.02, seg=20)
    k.tube("pad", P(fa, 0.239, za), P(fa, -0.215, za), 0.06, seg=36, soft=0.01)
    k.cyl("plastic", P(fa, -0.222, za), 0.035, 0.014, axis="x", seg=24, soft=0.003)
    # ---- the chest lever's axle through both posts' lower legs, the nuts outside; the counterweight's axle under the
    # apex; spacers from the planes to each hub
    for (pf_, pz), hub_l in ((PIV, LC), (CW, LW)):
        k.tube("steel", P(pf_, LI - AT / 2 - 0.02, pz), P(pf_, LO + AT / 2 + 0.02, pz), 0.02, seg=24)
        for l, ax in ((LI - AT / 2 - 0.006, "-x"), (LO + AT / 2 + 0.006, "+x")):
            k.cyl("frame", P(pf_, l, pz), 0.035, 0.012, axis="x", seg=28, soft=0.003)
            k.bolt(P(pf_, l + (0.006 if ax == "+x" else -0.006), pz), ax, size=0.028)
        k.tube("lever", P(pf_, hub_l - 0.035, pz), P(pf_, hub_l + 0.035, pz), 0.045, seg=32, soft=0.003)
        k.tube("steel", P(pf_, LI + AT / 2, pz), P(pf_, hub_l - 0.035, pz), 0.03, seg=24)
        k.tube("steel", P(pf_, hub_l + 0.035, pz), P(pf_, LO - AT / 2, pz), 0.03, seg=24)
    # ---- the chest lever (ref_13): from its tail below the axle up through the hub, bending forward to the top
    k.sweep("lever", [P(TAIL[0], LC, TAIL[1]), P(PIV[0], LC, PIV[1]), P(0.23, LC, 0.82),
                      P(0.36, LC, 1.16), P(LTOP[0], LC, LTOP[1])], k.rect(0.08, 0.05, 0.008), bend=0.22, up=UPL, soft=0.002)
    td = (PIV[0] - TAIL[0], PIV[1] - TAIL[1]); tn = math.hypot(*td)
    k.box("plastic", P(TAIL[0] - 0.003 * td[0] / tn, LC, TAIL[1] - 0.003 * td[1] / tn), (0.054, 0.084, 0.006),
          rx=math.asin(td[0] / tn), soft=0.002)                         # the tail's end cap
    k.box("warn", P(0.20, LC + 0.026, 0.75), (0.035, 0.002, 0.035), rx=0.0, ry=math.atan2(0.10, 0.30), soft=0.0)
    # the quadrant at its top (ref_13: the black fan with its holes), the roller arm pinned in it, the pop pin
    lq = LC - 0.025 - 0.004
    fan = [(0.0, 0.0)] + [(0.13 * math.cos(math.radians(a)), 0.13 * math.sin(math.radians(a))) for a in range(110, 231, 10)]
    k.sweep("lever", [P(LTOP[0], lq + 0.004, LTOP[1]), P(LTOP[0], lq - 0.004, LTOP[1])], [(-u, v) for u, v in fan],
            up=Z, soft=0.001)
    for a in range(125, 226, 25):
        k.cyl("hole", P(LTOP[0] + 0.10 * math.cos(math.radians(a)), lq - 0.0045, LTOP[1] + 0.10 * math.sin(math.radians(a))),
              0.007, 0.001, axis="x", seg=14)
    la = lq - 0.004 - 0.012
    k.bar("lever", P(LTOP[0], la, LTOP[1]), P(ROLL[0], la, ROLL[1]), 0.05, 0.024, up=UPL)
    k.bolt(P(LTOP[0], la - 0.012, LTOP[1]), "-x", size=0.024)
    pa = math.radians(200)
    k.tube("steel", P(LTOP[0] + 0.10 * math.cos(pa), la + 0.012, LTOP[1] + 0.10 * math.sin(pa)),
           P(LTOP[0] + 0.10 * math.cos(pa), la - 0.04, LTOP[1] + 0.10 * math.sin(pa)), 0.006, seg=12)
    k.cyl("plastic", P(LTOP[0] + 0.10 * math.cos(pa), la - 0.05, LTOP[1] + 0.10 * math.sin(pa)), 0.016, 0.022, axis="x", seg=20)
    # the chest roller: its shaft from the arm across to the right, the long pad (ref_01, ref_12)
    k.tube("steel", P(ROLL[0], la - 0.012, ROLL[1]), P(ROLL[0], -0.255, ROLL[1]), 0.022, seg=20)
    k.cyl("lever", P(ROLL[0], la - 0.02, ROLL[1]), 0.04, 0.016, axis="x", seg=28, soft=0.003)
    k.tube("pad", P(ROLL[0], la - 0.03, ROLL[1]), P(ROLL[0], -0.235, ROLL[1]), 0.065, seg=40, soft=0.012)
    k.cyl("plastic", P(ROLL[0], -0.242, ROLL[1]), 0.04, 0.014, axis="x", seg=24, soft=0.003)
    # ---- the counterweight arm: hung from its hub down and slightly back to the loading horn (out through the outer
    # plane, ref_14), resting back on the rubber stop on a tie between the rear braces
    k.bar("lever", P(CW[0], LW, CW[1]), P(CWH[0], LW, CWH[1] - 0.05), 0.08, 0.05, up=UPL)
    k.cyl("lever", P(CWH[0], LW + 0.03, CWH[1]), 0.045, 0.012, axis="x", seg=32, soft=0.003)
    k.tube("steel", P(CWH[0], LW + 0.036, CWH[1]), P(CWH[0], 0.84, CWH[1]), 0.025, seg=32)
    k.cyl("lever", P(CWH[0], 0.848, CWH[1]), 0.029, 0.016, axis="x", seg=32, soft=0.004)
    zs = 0.50
    fs = lerp_z(BRACE[1], BRACE[2], zs)
    along_l(k, "frame", fs, zs, LI + AT / 2, LO - AT / 2, 0.05)
    farm = lerp_z(CW, CWH, zs) - 0.04                                       # the arm's back face there
    k.box("rubber", P((fs + 0.025 + farm) / 2, LW, zs), ((farm - fs - 0.025), 0.06, 0.05), soft=0.006)
    # ---- the link: a flat bar from a pin in the chest lever's tail back to a pin on the counterweight arm
    fl = lerp_z(CW, CWH, 0.40)
    for l, (ff, zz) in ((LC + 0.02, (TAIL[0], TAIL[1] + 0.04)), (LW - 0.02, (fl, 0.40))):
        k.tube("steel", P(ff, l, zz), P(ff, LK, zz), 0.012, seg=16)
    k.bar("lever", P(TAIL[0], LK, TAIL[1] + 0.04), P(fl, LK, 0.40), 0.05, 0.016, up=UPL)
    for ff, zz in ((TAIL[0], TAIL[1] + 0.04), (fl, 0.40)):   # the link's eyes round the pins
        k.cyl("lever", P(ff, LK, zz), 0.026, 0.016, axis="x", seg=24, soft=0.002)
        k.bolt(P(ff, LK - 0.008, zz), "-x", size=0.018)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """A short, a middle and a tall user kneeling up at the start: the shins on the kneeler, the ankles under the
    ankle roller, the feet pointed back (sole 180: toes behind, the sole up), the thighs and trunk upright, the arms
    wrapped round the chest roller."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        za = KZ + 0.045                                       # the ankle's centre on the shin lying on the pad
        ball = P(ANK[0] - 0.48 * 0.152 * H, 0.0, za + 0.039 * H)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=180, shank=90, thigh=2, trunk=8, neck=5,
                          arm=168, forearm=65, arm_out=8)
    return out

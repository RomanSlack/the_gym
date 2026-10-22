"""Rogue Flat Utility Bench 2.0 (RA1362, textured pad).

Built by eye from Rogue's gallery (refs/: ref_01 the studio three-quarter, ref_05 + ref_02 near side views with a lifter,
ref_04 the foot + leg close-up, ref_03 the pad's embossed logo), held to Rogue's spec: footprint 47 x 14 in, pad top
18 in, pad 12 in wide and 2.5 in thick, 2 x 3 in 11-gauge steel throughout.
Axes: metres, floor z = 0, the bench runs along x (the head end at +x, where the pad's logo is), its feet across y.
Structure (ref_01, ref_04): a 2 x 3 in spine under the pad, two legs leaning in towards the middle, each welded onto
the middle of a 2 x 3 in foot with black plastic end caps; the legs bolt to the spine through ears welded to their
sides (the bench ships flat; the silver bolt heads show under the pad's edge in ref_01).
"""
import math
from pathlib import Path

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.016, 0.016, 0.017), rough=0.45, metal=0.1, coat=0.05, bump=(1400, 0.06)),   # black satin powder coat
    "pad": dict(color=(0.030, 0.030, 0.032), rough=0.8, sheen=0.05, bump=(2600, 0.35)),             # textured grey foam
    "emboss": dict(color=(0.024, 0.024, 0.025), rough=0.55, bump=(2600, 0.1)),                       # the moulded logo, smoother
    "plastic": dict(color=(0.012, 0.012, 0.013), rough=0.7),                                          # the pad's board, matte
    "cap": dict(color=(0.010, 0.010, 0.011), rough=0.22, coat=0.3),                                  # glossy end caps
    "bolt": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-38, 16, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_foot": ((0.95, -0.42, 0.42), (0.56, 0.0, 0.10), 45),        # ref_04: the foot, its caps and the leg's weld
    "detail_leg_top": ((0.78, -0.45, 0.30), (0.51, 0.0, 0.37), 50),     # the ears bolted to the spine under the pad
}

FOOT_X = 47 * IN / 2 - 1.5 * IN  # the feet's centres (x): the footprint's 47 in to the feet's outer faces
FOOT_L = 14 * IN                 # foot length (y), caps included
FOOT = (3 * IN, 2 * IN)          # foot section: 3 in along x, 2 in tall
CAP_L, CAP_T = 0.024, 0.002      # end caps: how far they cover the foot, their wall (they lift the foot off the floor)
TOP = 18 * IN                    # pad top
PAD_L, PAD_W, PAD_T = 1.15, 12 * IN, 2.5 * IN
SPINE = (3 * IN, 2 * IN)         # spine section: 3 in wide (y), 2 in tall
LEG = (2 * IN, 3 * IN)           # leg section: 2 in along x, 3 in across (y)
LEG_TOP_X = 0.51                 # where the legs meet the spine (x): they lean in about 10 deg (ref_05)
SPINE_X = 0.56                   # the spine runs this far each way
EAR_T = 0.006                    # the ears: plates welded to the legs' sides, bolted through the spine


def build(k):
    pad_bot = TOP - PAD_T
    sz = pad_bot - SPINE[1] / 2                                   # the spine's centreline
    s_bot = pad_bot - SPINE[1]
    foot_bot = CAP_T
    foot_top = foot_bot + FOOT[1]
    # the spine under the pad, capped
    k.bar("frame", (-SPINE_X, 0, sz), (SPINE_X, 0, sz), SPINE[1], SPINE[0], up=(0, 1, 0))
    for s in (1, -1):
        k.box("cap", (s * (SPINE_X + 0.002), 0, sz), (0.008, SPINE[0] + 0.003, SPINE[1] + 0.003), soft=0.002)
    for s in (1, -1):
        fx = s * FOOT_X
        # the foot: the tube between its caps, the caps a touch bigger, standing on the floor
        body = FOOT_L / 2 - CAP_T
        k.bar("frame", (fx, -body, foot_bot + FOOT[1] / 2), (fx, body, foot_bot + FOOT[1] / 2), FOOT[0], FOOT[1], up=(0, 0, 1))
        for d in (1, -1):
            k.box("cap", (fx, d * (FOOT_L / 2 - CAP_L / 2), foot_bot + FOOT[1] / 2),
                  (FOOT[0] + 2 * CAP_T, CAP_L, FOOT[1] + 2 * CAP_T), soft=0.004)
        # the leg: welded onto the foot's middle, leaning in, its top cut level under the spine
        p0, p1 = (fx, 0, foot_top), (s * LEG_TOP_X, 0, s_bot)
        k.bar("frame", p0, p1, LEG[0], LEG[1], up=(0, 1, 0),
              cut0=((0, 0, foot_top), (0, 0, 1)), cut1=((0, 0, s_bot), (0, 0, 1)), weld=True)
        # the ears: a plate welded to each side of the leg's top, up past the spine's sides, one bolt through all three
        for e in (1, -1):
            ey = e * (LEG[1] / 2 + EAR_T / 2)
            k.box("frame", (s * LEG_TOP_X, ey, (s_bot - 0.035 + pad_bot - 0.012) / 2), (0.07, EAR_T, pad_bot - 0.012 - s_bot + 0.035),
                  soft=0.0015)
        k.bolt((s * LEG_TOP_X, -(LEG[1] / 2 + EAR_T), sz), "-y", size=0.0127, nut=LEG[1] + 2 * EAR_T)
        sticker(k, s, foot_top, s_bot)
    # the pad: moulded textured foam on its board, no stitching; ROGUE embossed across the head end (ref_03)
    k.shaped_pad("pad", [(-PAD_L / 2, -PAD_W / 2), (PAD_L / 2, -PAD_W / 2), (PAD_L / 2, PAD_W / 2), (-PAD_L / 2, PAD_W / 2)],
                 (0, 0, TOP - PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.012, seam=False)
    k.text("emboss", "ROGUE", (PAD_L / 2 - 0.075, 0.0, TOP - 0.0003), 0.042, rz=math.pi / 2, rx=0.0, depth=0.0016)


def sticker(k, s, z0, z1):
    """The black ROGUE sticker on the leg's outer face, reading upwards (ref_04), tilted with the leg."""
    from mathutils import Matrix, Vector
    lean = math.atan2(FOOT_X - LEG_TOP_X, z1 - z0)
    zc = z0 + 0.13
    xc = FOOT_X - (FOOT_X - LEG_TOP_X) * (zc - z0) / (z1 - z0) + (LEG[0] / 2) / math.cos(lean) + 0.0008
    c = Vector((s * xc, 0, zc))
    ob = k.decal(Path(__file__).parent / "art" / "sticker_v2.png", tuple(c), 0.052, 0.20, facing="+x" if s > 0 else "-x")
    ob.data.transform(Matrix.Translation(c) @ Matrix.Rotation(-s * lean, 4, "Y") @ Matrix.Translation(-c))

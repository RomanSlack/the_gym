"""Atlantis Olympic Incline Bench Press with Pivot (P338), black frame, red upholstery.

Built by eye from Atlantis's four renders (refs/: ref_02 + ref_03 the front three-quarters, ref_04 + ref_05 from behind),
held to Atlantis's 65 x 66 x 57 in (L x W with the horns x H). The towers are the flat bench's (P337's model.py, reused:
same rack posts with the pivot, storage frames and horns), taller, three hooks each.
Axes: metres, floor z = 0, the bench runs along x, the lifter's head at +x under the bar; y across.
Between the towers: a spotter's platform (diamond plate) on two cross bars between the base tubes, a low cross tube
the bench beam runs into, a high one the back frame rests on. The bench: the beam from the front post (disc foot) to
the low cross tube, the back pad at 40 deg on its frame, a strut up to it, the seat on a post at its foot.
"""
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "p337", Path(__file__).resolve().parents[1] / "atlantis-olympic-flat-bench-press-with-pivot-p337" / "model.py")
p337 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(p337)
p337.RACK_TOP, p337.S_TOP = 57 * 0.0254, 1.10
p337.HOOKS = (1.05, 1.19, 1.33)
p337.HORNS = (0.38, 0.78)       # the upper horns below the lower arch's bend
p337.CROSS_Z = 0.25             # the towers' braces run down to the low cross tube

LOOK = dict(p337.LOOK, plate=dict(color=(0.03, 0.03, 0.032), rough=0.4, metal=0.5, bump=(160, 0.4)))   # diamond plate
VIEWS = {"three_quarter": (-40, 14, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (130, 16, 1.0)}
DETAILS = {
    "detail_seat": ((-1.1, -0.7, 0.75), (-0.45, 0.0, 0.4), 40),         # the seat, the back pad's foot, the front post
    "detail_platform": ((1.35, -0.9, 0.9), (0.6, 0.0, 0.1), 35),        # the spotter's platform between the towers
}

XR, TY = p337.XR, p337.TY
SX1 = p337.SX1
BACK_DEG, BACK_L = 40.0, 0.80
P0 = (-0.36, 0.48)              # the back pad's lower end, its underside (x, z)
PAD_T, PAD_W = 0.075, 0.30
SEAT = (-0.66, -0.37)           # the seat pad (x from / to), its top at the back pad's foot
FRONT_X = -0.58                 # the front post
LOW_Z, HIGH_Z = 0.25, 0.93      # the cross tubes' centres


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    for s in (1, -1):
        p337.tower(k, s)
    yi = TY - p337.STORE[1] / 2
    for cz, h in ((LOW_Z, 0.10), (HIGH_Z, 0.07)):
        k.bar("frame", (XR, -yi, cz), (XR, yi, cz), h, 0.07, up=Z, cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    k.text("label", "ATLANTIS", (XR - 0.0355, 0.0, LOW_Z + 0.02), 0.03, rz=-math.pi / 2, depth=0.0008)
    # the spotter's platform: two cross bars between the base tubes, the diamond plate on them
    ub = TY - p337.BASE[1] / 2
    bt = p337.BASE_Z + p337.BASE[0] / 2
    for x_ in (XR + 0.12, SX1 - 0.08):
        k.bar("frame", (x_, -ub, p337.BASE_Z), (x_, ub, p337.BASE_Z), 0.06, 0.04, up=Z, cut0=((0, -ub, 0), Y), cut1=((0, ub, 0), Y), weld=True)
    k.box("plate", ((XR + SX1) / 2 + 0.02, 0, p337.BASE_Z + 0.03 + 0.004), (SX1 - XR - 0.08, 2 * ub - 0.01, 0.008), soft=0.002)
    # the beam: from the front post to the low cross tube's face
    bz = LOW_Z
    k.bar("frame", (FRONT_X - 0.05, 0, bz), (XR - 0.035, 0, bz), 0.10, 0.06, up=Y, cut1=((XR - 0.035, 0, 0), (1, 0, 0)), weld=True)
    k.box("plastic", (FRONT_X - 0.054, 0, bz), (0.008, 0.064, 0.104), soft=0.003)
    k.tube("frame", (FRONT_X, 0, 0.028), (FRONT_X, 0, bz - 0.05), 0.038, seg=32, cut1=((0, 0, bz - 0.05), Z), weld=True)
    p337.disc(k, FRONT_X, 0, 0.0)
    # the back: its frame under the pad from the foot up onto the high cross tube, bolted there; a strut from the beam
    A = math.radians(BACK_DEG)
    u = (math.cos(A), 0, math.sin(A)); n = (-math.sin(A), 0, math.cos(A))
    fh = 0.06
    def on(s_, off):
        return (P0[0] + u[0] * s_ + n[0] * off, 0, P0[1] + u[2] * s_ + n[2] * off)
    s_hi = (XR - P0[0]) / u[0]                                      # the frame's length to over the high cross tube
    k.bar("frame", on(-0.02, -fh / 2), on(s_hi + 0.05, -fh / 2), fh, 0.08, up=Y)
    k.box("plastic", on(s_hi + 0.054, -fh / 2), (0.008, 0.084, fh + 0.004), ry=-A, soft=0.003)
    top_c = on(s_hi, -fh)                                            # its underside over the cross tube
    k.box("frame", (XR, 0, (HIGH_Z + 0.035 + top_c[2]) / 2), (0.08, 0.10, top_c[2] - HIGH_Z - 0.035 + 0.01), soft=0.002)   # the saddle
    k.bolt((XR, -0.05, (HIGH_Z + top_c[2]) / 2 + 0.02), "-y", size=0.012, nut=0.10)
    sx = -0.02
    sz = P0[1] + (sx - P0[0]) * math.tan(A) - fh / math.cos(A)       # the frame's underside above x = sx
    k.bar("frame", (sx, 0, bz + 0.05), (sx, 0, sz + 0.01), 0.06, 0.06, up=Y, cut0=((0, 0, bz + 0.05), Z),
          cut1=(on(0.0, -fh), n), weld=True)
    k.shaped_pad("pad", [(-PAD_W / 2, -BACK_L / 2), (PAD_W / 2, -BACK_L / 2), (PAD_W / 2, BACK_L / 2), (-PAD_W / 2, BACK_L / 2)],
                 on(BACK_L / 2 + 0.01, PAD_T / 2), n, (0, -1, 0), PAD_T, r=0.05, cushion=0.028)
    # the seat: on a bracket on a post from the beam, its top level with the back pad's foot, tipped up at the front
    st = P0[1] + 0.02
    sb = st - PAD_T
    sc = (SEAT[0] + SEAT[1]) / 2
    k.bar("frame", (sc + 0.03, 0, bz + 0.05), (sc + 0.03, 0, sb - 0.012), 0.06, 0.06, up=Y, cut0=((0, 0, bz + 0.05), Z), weld=True)
    k.box("frame", (sc + 0.02, 0, sb - 0.006), (0.22, 0.16, 0.012), soft=0.002)
    L = SEAT[1] - SEAT[0]
    k.shaped_pad("pad", [(-L / 2, -PAD_W / 2), (L / 2, -PAD_W / 2), (L / 2, PAD_W / 2), (-L / 2, PAD_W / 2)],
                 (sc, 0, sb + PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.04, cushion=0.028)

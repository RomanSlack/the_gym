"""Hammer Strength Stackable Plyo Box, the set of five, stacked (ref_01).

Built by eye from the listing's photos (refs/: ref_01 the stack, ref_02-ref_06 levels 1-5, ref_03 level 2 close),
held to Life Fitness's sizes: every level 30 x 36 in, 3 / 6 / 12 / 18 / 24 in tall.
Axes: metres, floor z = 0, the boxes' long side along y, the numbered end facing -y.
Each box: dense foam in black vinyl, softly rounded; the top a black grip mesh inside a grey border band; on the
numbered end its level and HAMMER STRENGTH, on the long sides the height in cm / in, two hook-and-loop tabs each side
(they hold a stack together) and a small yellow warning triangle.
"""
import math

IN = 0.0254
LOOK = {
    "vinyl": dict(color=(0.018, 0.018, 0.019), rough=0.42, sheen=0.15, coat=0.0, bump=(1600, 0.06)),   # black vinyl
    "band": dict(color=(0.16, 0.16, 0.165), rough=0.45, coat=0.0),                                      # grey top border
    "mesh": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, bump=(2400, 0.5)),                  # grip mesh
    "velcro": dict(color=(0.008, 0.008, 0.008), rough=0.9, coat=0.0, bump=(3000, 0.3)),
    "print": dict(color=(0.62, 0.62, 0.62), rough=0.5, coat=0.0),                                      # the grey print
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-38, 18, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {"detail_level2": ((-0.85, -1.0, 1.75), (0.0, -0.2, 1.48), 45)}

W, L = 30 * IN, 36 * IN         # across x, along y
LEVELS = [(5, 24, 60), (4, 18, 45), (3, 12, 30), (2, 6, 15), (1, 3, 7)]   # bottom to top: level, in, cm


def box(k, z0, level, h_in, cm):
    h = h_in * IN
    zc = z0 + h / 2
    k.box("vinyl", (0, 0, zc), (W, L, h), soft=min(0.012, h / 4))
    top = z0 + h
    k.box("band", (0, 0, top + 0.0005), (W - 0.01, L - 0.01, 0.001), soft=0.0)
    k.box("mesh", (0, 0, top + 0.0012), (W - 0.09, L - 0.09, 0.001), soft=0.0)
    # the numbered end (-y): the level big at the left, HAMMER STRENGTH beside it
    fy = -L / 2 - 0.0006
    big = min(0.75 * h, 0.16)
    k.text("print", str(level), (-0.17, fy, zc), big, depth=0.001)
    ts = min(0.045, 0.32 * h)
    k.text("print", "HAMMER", (0.05, fy, zc + 0.55 * ts), ts, depth=0.001)
    k.text("print", "STRENGTH", (0.05, fy, zc - 0.55 * ts), ts, depth=0.001)
    # the long sides: the height in cm / in at the numbered end, two hook-and-loop tabs, the warning triangle
    for s in (1, -1):
        fx = s * (W / 2 + 0.0006)
        rz = math.pi / 2 if s > 0 else -math.pi / 2
        ny = -L / 2 + 0.07
        hs = min(0.035, 0.3 * h)
        if h_in >= 6:
            k.text("print", str(cm), (fx, ny, top - 0.6 * hs), hs, rz=rz, depth=0.001)
            k.text("print", str(h_in), (fx, ny, top - 1.9 * hs), hs, rz=rz, depth=0.001)
        else:
            k.text("print", f"{cm} / {h_in}", (fx, ny + 0.03, zc), 0.6 * h, rz=rz, depth=0.001)
        for ty in (-0.22, 0.22):
            k.box("velcro", (s * (W / 2 + 0.0015), ty, top - min(0.035, h / 2 - 0.004)), (0.003, 0.10, min(0.06, h - 0.012)), soft=0.0)
        k.box("warn", (s * (W / 2 + 0.0008), -0.10, zc - h / 6), (0.0015, 0.03, 0.026), soft=0.0)
    return top


def build(k):
    z = 0.0
    for level, h_in, cm in LEVELS:
        z = box(k, z, level, h_in, cm)

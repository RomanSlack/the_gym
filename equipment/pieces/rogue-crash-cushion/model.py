"""Rogue Crash Cushion, the pair (ref_01, ref_02: two set side by side).

Built by eye from Rogue's photos (refs/: ref_02 the pair, ref_03 + ref_04 close, ref_05 the printed side), held to
Rogue's 30 x 24 x 6 in each.
Axes: metres, floor z = 0, each cushion's long side along y, the two side by side across x.
Each: dense foam in black vinyl, the top's edge a sewn welt, ROGUE big in white along one long edge of the top,
CRASH CUSHION on the end.
"""
import math

IN = 0.0254
LOOK = {
    "vinyl": dict(color=(0.008, 0.008, 0.009), rough=0.35, sheen=0.2, coat=0.0, bump=(1500, 0.08)),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-38, 24, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 24, 1.0)}
DETAILS = {"detail_corner": ((-0.75, -0.75, 0.45), (-0.2, -0.3, 0.08), 45)}

L, W, H = 30 * IN, 24 * IN, 6 * IN
GAP = 0.18                       # between the pair


def cushion(k, x):
    k.box("vinyl", (x, 0, H / 2), (W, L, H), soft=0.006)
    # the welt round the top edge
    pts = [(x - W / 2, -L / 2, H - 0.002), (x + W / 2, -L / 2, H - 0.002), (x + W / 2, L / 2, H - 0.002), (x - W / 2, L / 2, H - 0.002)]
    k.sweep("vinyl", pts + [pts[0]], k.circle(0.0035, 8), caps=False, soft=0)
    k.text("print", "ROGUE", (x + W / 2 - 0.085, 0.03, H + 0.0003), 0.10, rz=math.pi / 2, rx=0.0, depth=0.001)
    k.text("print", "CRASH CUSHION", (x - 0.03, -L / 2 - 0.0006, 0.045), 0.026, depth=0.001)


def build(k):
    for s in (1, -1):
        cushion(k, s * (W + GAP) / 2)

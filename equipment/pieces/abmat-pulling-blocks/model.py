"""AbMat Pulling Blocks, two stacks of the full set (12 + 8 + 4 + 2 in = the 26 in max) as in the photo.

Built by eye from AbMat's photo (refs/: ref_01, two stacks under a bar's ends), held to the listing: 30 x 20 in, 26 in
at most.
Axes: metres, floor z = 0, each stack's long side along y, the pair across x.
Each block: dense foam in black vinyl, a welt round its top and bottom edges, a seam round the middle of the taller
ones; stacked a few millimetres out of line, as foam blocks are.
"""
IN = 0.0254
LOOK = {
    "vinyl": dict(color=(0.009, 0.009, 0.010), rough=0.5, sheen=0.15, coat=0.0, bump=(1500, 0.08)),
}
VIEWS = {"three_quarter": (-38, 18, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {"detail_stack": ((-1.2, -0.9, 0.85), (-0.62, 0.0, 0.45), 40)}

L, W = 30 * IN, 20 * IN
STACK = (12, 8, 4, 2)            # bottom up, inches
CENTRES = 0.62
JOG = ((0.0, 0.0), (0.004, -0.006), (-0.005, 0.003), (0.003, 0.005))   # each block a little out of line (x, y)


def welt(k, x, y, z):
    pts = [(x - W / 2, y - L / 2, z), (x + W / 2, y - L / 2, z), (x + W / 2, y + L / 2, z), (x - W / 2, y + L / 2, z)]
    k.sweep("vinyl", pts + [pts[0]], k.circle(0.0025, 8), caps=False, soft=0)


def build(k):
    for s in (1, -1):
        z = 0.0
        for (h_in, (jx, jy)) in zip(STACK, JOG):
            h = h_in * IN
            x, y = s * CENTRES + jx, jy
            k.box("vinyl", (x, y, z + h / 2), (W, L, h), soft=min(0.008, h / 5))
            welt(k, x, y, z + h - 0.003)
            welt(k, x, y, z + 0.003)
            if h_in >= 8:
                welt(k, x, y, z + h / 2)
            z += h

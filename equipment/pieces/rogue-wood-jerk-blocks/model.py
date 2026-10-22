"""Rogue Wood Jerk Blocks, a pair of stacks (12 + 6 + 6 in blocks under the 2.25 in top), as set up for jerks.

Built by eye from Rogue's photo (refs/: ref_01, one stack), held to Rogue's spec: every block 36 x 20 in, the
blocks 15 / 12 / 6 in, the 2.25 in block always on top.
Axes: metres, floor z = 0, each stack's long side along y, the pair side by side across x under the bar's ends.
Each block: a plywood box (pine faces, the plies showing along the top panel's edge), ROGUE stencilled on both long
faces, a hand slot in each end; the top block solid ply with a raised landing strip at each end.
"""
IN = 0.0254
LOOK = {
    "pine": dict(color=(0.62, 0.48, 0.30), rough=0.65, coat=0.0, bump=(900, 0.05),
                 grain=dict(dark=(0.52, 0.38, 0.21), scale=11.0, distortion=7.0, along="Z")),       # pine-faced ply
    "ply": dict(color=(0.66, 0.52, 0.33), rough=0.7, coat=0.0,
                grain=dict(dark=(0.36, 0.25, 0.12), scale=160.0, distortion=0.4, along="Z")),        # the plies' edges
    "burn": dict(color=(0.07, 0.045, 0.025), rough=0.8, coat=0.0),                                      # the stencil
    "hole": dict(color=(0.03, 0.022, 0.015), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-38, 18, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {"detail_top": ((-1.05, -0.75, 1.0), (-0.62, 0.0, 0.62), 45)}

L, W = 36 * IN, 20 * IN          # along y, across x
STACK = (12, 6, 6)               # bottom up, inches, then the 2.25 in top
TOP = 2.25 * IN
PANEL = 0.019                    # the top panels' ply
CENTRES = 0.62                   # each stack's centre off the middle (x): under a bar's plates


def block(k, x, z0, h_in):
    h = h_in * IN
    k.box("pine", (x, 0, z0 + (h - PANEL) / 2), (W, L, h - PANEL), soft=0.0015)
    k.box("ply", (x, 0, z0 + h - PANEL / 2), (W + 0.002, L + 0.002, PANEL), soft=0.0015)
    zc = z0 + (h - PANEL) / 2
    size = min(0.13, 0.5 * h)
    for s in (1, -1):
        rz = 1.5708 if s > 0 else -1.5708
        k.text("burn", "ROGUE", (x + s * (W / 2 + 0.0004), 0, zc), size, rz=rz, depth=0.0006)
        k.box("hole", (x, s * (L / 2 + 0.0004), z0 + h - PANEL - min(0.05, h / 3)), (0.11, 0.0008, 0.035), soft=0.0)
    return z0 + h


def build(k):
    for s in (1, -1):
        x = s * CENTRES
        z = 0.0
        for h_in in STACK:
            z = block(k, x, z, h_in)
        # the top: solid ply, a raised landing strip across each end
        k.box("ply", (x, 0, z + TOP / 2), (W, L, TOP), soft=0.0015)
        for d in (1, -1):
            k.box("ply", (x, d * (L / 2 - 0.05), z + TOP + 0.009), (W, 0.10, 0.018), soft=0.002)

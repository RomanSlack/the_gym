"""Manduka enlight Rectangular Bolster (refs/: ref_01 two: a patterned one and a natural canvas one, rectangular with
rounded edges, a carry loop at one end). The linked page (manduka.com) was not fetched: the size (about 24 x 12 x 6 in)
is an estimate; the natural (undyed) one shown. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Restorative yoga and recovery: under the back, the knees or the hips.
2. Each mass named (ref_01): the bolster, a cotton canvas cover over a firm fill, its edges rounded full; the loop.
3. Adjustments. None.
4. Load path. The body on the fill, the floor.
5. Fit range. 24 in: across any user's back or under the knees (1.55-1.95 m). No figure.
6. Size. 0.61 x 0.30 x 0.15 m.
Axes: metres, floor z = 0; the long side along x, the loop at +x.
"""
IN = 0.0254
L, W, H = 24 * IN, 12 * IN, 6 * IN

LOOK = {
    "canvas": dict(color=(0.55, 0.50, 0.42), rough=0.9, coat=0.0, bump=(2500, 0.1)),
    "seam": dict(color=(0.48, 0.43, 0.36), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 25, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_loop": ((0.55, -0.35, 0.25), (0.28, 0.0, 0.08), 30),        # the loop at the end
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.box("canvas", (0, 0, H / 2), (L, W, H), soft=0.055)                                          # the bolster
    loop = [(L / 2 - 0.01, -0.03, H * 0.55), (L / 2 + 0.03, -0.03, H * 0.55), (L / 2 + 0.03, 0.03, H * 0.55),
            (L / 2 - 0.01, 0.03, H * 0.55)]
    k.sweep("seam", loop, k.rect(0.004, 0.025, 0.001), bend=0.012, up=(0, 0, 1), soft=0.0)          # the carry loop

"""Rogue Gym Chalk (refs/: ref_01 the case: a kraft cardboard box printed ROGUE / CHALK in black in a box outline). The
linked page was not fetched: the case (an 8 lb case of 1 lb blocks, about 10 x 10 x 9 in) and the blocks (about 2 x
2.75 x 4.5 in) are the usual and estimates. Shown closed, with two blocks out beside it. Built to the two gates and
README point 9.

DESIGN SPEC (gate 1)
1. Use. Magnesium carbonate blocks broken into the chalk bowl (the chalk stand's) as needed.
2. Each mass named (ref_01): the case, kraft cardboard, its flaps closed and taped, the print; two blocks of chalk.
3. Adjustments. None.
4. Load path. None.
5. Fit range. Not worn or used on the body. No figure.
6. Size. The case 0.25 x 0.25 x 0.23 m.
Axes: metres, floor z = 0; the print toward -y.
"""
IN = 0.0254
B = (10 * IN, 10 * IN, 9 * IN)

LOOK = {
    "kraft": dict(color=(0.45, 0.30, 0.15), rough=0.9, coat=0.0, bump=(2000, 0.05)),
    "ink": dict(color=(0.02, 0.02, 0.022), rough=0.8, coat=0.0),
    "tape": dict(color=(0.55, 0.45, 0.30), rough=0.4, coat=0.2),
    "chalk": dict(color=(0.85, 0.85, 0.84), rough=0.95, coat=0.0, bump=(1500, 0.2)),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_print": ((0.0, -0.65, 0.15), (0.0, 0.0, 0.11), 30),         # the print, as ref_01
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x, y, z = B
    k.box("kraft", (0, 0, z / 2), B, soft=0.002)                                                    # the case
    k.box("tape", (0, 0, z + 0.0003), (0.05, y + 0.002, 0.0008), soft=0.0)                          # the tape
    yf = -y / 2 - 0.0004
    for zz in (z * 0.33, z * 0.73):                     # the outline's long edges
        k.box("ink", (0, yf, zz), (x * 0.72, 0.0008, 0.006), soft=0.0)
    for xx in (-x * 0.36, x * 0.36):
        k.box("ink", (xx, yf, z * 0.53), (0.006, 0.0008, z * 0.40 + 0.006), soft=0.0)
    k.text("ink", "ROGUE", (0, yf, z * 0.58), 0.040, depth=0.0006)
    k.text("ink", "CHALK", (0, yf, z * 0.40), 0.040, depth=0.0006)
    for i, (bx, by) in enumerate(((0.22, -0.06), (0.25, 0.06))):       # two blocks out beside it
        k.box("chalk", (bx, by, 1.375 * IN), (4.5 * IN, 2 * IN, 2.75 * IN), rz=0.3 * i, soft=0.004)

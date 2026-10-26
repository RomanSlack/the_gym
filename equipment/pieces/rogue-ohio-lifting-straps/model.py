"""Rogue Ohio Lifting Straps (refs/: ref_01 a pair: black cotton webbing, a loop at one end with a red patch and ROGUE
in white; ref_02 / ref_03 laid flat: the patch over the sewn end; ref_04 the webbing; ref_05 looped as worn). The
linked page was not fetched (the refs carry it): the size, 1.5 in webbing about 21 in long, is the usual strap and an
estimate. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Grip help for heavy pulls: the hand through the loop, the tail wound round the bar.
2. Each mass named (ref_02): the strap, 1.5 in black cotton webbing; its end folded back and sewn into a loop under a
   red patch with ROGUE in white.
3. Adjustments. How many turns round the bar.
4. Load path. The bar, the tail's turns, the loop round the wrist.
5. Fit range. A loop round any wrist (1.55-1.95 m users) and a tail for one and a half turns on a 28-32 mm bar. No
   figure.
6. Size. A pair laid flat, 0.53 x 0.038 m each.
Axes: metres, floor z = 0; the straps along x, the loops toward -x.
"""
IN = 0.0254
L, W, T = 21 * IN, 1.5 * IN, 0.003

LOOK = {
    "web": dict(color=(0.010, 0.010, 0.011), rough=0.9, coat=0.0, spec=0.2, bump=(3000, 0.2)),
    "red": dict(color=(0.38, 0.008, 0.008), rough=0.6, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_patch": ((-0.35, -0.30, 0.22), (-0.20, -0.03, 0.0), 30),    # the loop end, the red patch
}


def strap(k, y):
    k.box("web", (0, y, T / 2), (L, W, T), soft=0.001)                                              # the strap
    x0 = -L / 2
    k.sweep("web", [(x0 + 0.12, y, T * 1.5), (x0, y, T * 1.5), (x0 - 0.012, y, T), (x0, y, T * 0.4)],
            k.rect(T, W, 0.0008), bend=0.008, up=(0, 1, 0), soft=0.0)                              # the end folded back
    k.box("red", (x0 + 0.075, y, T * 2 + 0.0006), (0.085, W - 0.004, 0.0012), soft=0.0004)          # the patch
    k.text("white", "ROGUE", (x0 + 0.075, y, T * 2 + 0.0013), 0.016, rx=0.0, depth=0.0004)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    strap(k, -0.04)
    strap(k, 0.04)

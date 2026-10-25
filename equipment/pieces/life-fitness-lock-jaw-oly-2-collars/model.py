"""Lock-Jaw Oly 2 Collars, a pair (refs/: ref_01 one collar closed: a moulded black hex-sided body in two halves hinged
at the bottom, the red rubber liner, the latch lever folded down over its side from a pinned boss at the top, the
steel pins, the red Lock-Jaw badge). The linked shop page refused further requests (HTTP 429): the sizes are ours, for
a 50 mm sleeve: the bore 50 mm with the liner, the body 112 mm across its flats, 60 mm wide (estimates). Built to the
two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Opened (the lever up, the halves apart on the hinge), slid onto a 50 mm sleeve against the plates, closed: the
   lever pulls the halves together and the liner grips the sleeve.
2. Each mass named (ref_01): the body, two moulded halves hex-sided outside, hinged on a steel pin at the bottom; the
   red rubber liner round the bore; the latch lever, an arm pinned to the upper half's boss at the top, folding down
   over the body's side to close it (an over-centre latch); the badge on the lever.
3. Adjustments. Open / closed.
4. Load path. The plates' push on the body's face, the liner's grip on the sleeve, held by the latch.
5. Fit range. The lever opened by a thumb; nothing else to fit.
6. Size. 112 mm across, 60 mm wide; the pair side by side.
Axes: metres, floor z = 0; each collar's axis along x, standing on its flats.
"""
import math

R_IN = 0.025                          # the bore (the liner's inside)
R_BODY_IN = 0.035                     # the body's inside, the thick red liner between (ref_01)
APO = 0.056                           # the hex's apothem (112 mm across the flats)
W = 0.060                             # front to back (ref_01: about half the width across)

LOOK = {
    "body": dict(color=(0.012, 0.012, 0.013), rough=0.35, coat=0.3),                          # moulded nylon
    "red": dict(color=(0.45, 0.02, 0.02), rough=0.6, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.25, metal=1.0),
    "badge": dict(color=(0.55, 0.03, 0.03), rough=0.4),
    "gap": dict(color=(0.002, 0.002, 0.002), rough=0.9),
}
VIEWS = {"three_quarter": (-40, 18, 1.0), "front": (-90, 6, 1.0), "side": (0, 6, 1.0), "back_three_quarter": (140, 22, 1.0)}
DETAILS = {
    "detail_ref": ((-0.33, -0.12, 0.16), (-0.05, 0.0, 0.056), 26),      # ref_01: the bore face on, the lever side a little
}


def collar(k, x0):
    zc = APO
    R_OUT = APO / math.cos(math.radians(30))
    for i in range(6):                                  # the body: six hex segments round the bore (the flats down/up)
        a0, a1 = math.radians(-60 + 60 * i), math.radians(60 * i)
        am = (a0 + a1) / 2

        def seg(cx, cy, cz, a0=a0, a1=a1):
            a = a1 if cy > 0 else a0
            r = R_OUT if cz > 0 else R_BODY_IN
            return (x0 + cx * W / 2, r * math.cos(a), zc + r * math.sin(a))
        k.block("body", seg, soft=0.003)
    k.disc("red", (x0, 0, zc), R_BODY_IN + 0.0005, R_IN, W - 0.006, axis="x", seg=48, soft=0.002)    # the liner
    # the pins: the lever's pivot at the top, the halves' hinge at the bottom right (ref_01), each in a boss
    top, hinge = (-0.012, zc + 0.050), (0.034, zc - 0.044)
    for yy, zz in (top, hinge):
        k.cyl("body", (x0, yy, zz), 0.011, W + 0.002, axis="x", seg=24, soft=0.002)
        for s in (1, -1):
            k.cyl("steel", (x0 + s * (W / 2 + 0.0015), yy, zz), 0.004, 0.001, axis="x", seg=16, soft=0.0)
    # the split between the halves, from the lever's pivot down to the bore
    k.box("gap", (x0, 0.004, zc + 0.04), (W + 0.001, 0.003, 0.018), rx=math.radians(-20), soft=0.0)
    # the lever: from its pivot at the top, folded down over the upper left flat, a little proud of it
    k.bar("body", (x0, top[0] - 0.004, top[1] + 0.004), (x0, -R_OUT * 0.95 - 0.006, zc - 0.012), W + 0.006, 0.010,
          up=(0, -0.5, 0.87), r=0.003)
    k.box("badge", (x0 - W / 2 - 0.0032, -0.055, zc + 0.01), (0.001, 0.016, 0.016), soft=0.0003)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    collar(k, -0.05)
    collar(k, 0.05)

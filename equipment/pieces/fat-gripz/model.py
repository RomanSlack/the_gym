"""Fat Gripz Pro, a pair (refs/: ref_01 the pair, blue, one standing and one lying, FAT GRIPZ and THE ULTIMATE ARM
BUILDER in black along them; ref_02 the box; ref_03 one opened onto a dumbbell handle, the split down its length; ref_04
on a barbell; ref_05 the three sizes with their sizes). ref_05: all 1.1 in inside, 4.75 in long; One 1.75 in, Pro 2.25
in, Extreme 2.75 in outside; sold as a pair of one colour; the Pro (blue) is the one recommended and the one in
ref_01. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Thick-grip training: each sleeve opened along its split and pushed onto a bar or handle, the hand then wraps
   2.25 in.
2. Each mass named (ref_01 / ref_03): a tube of blue silicone, 2.25 in outside, 1.1 in inside, 4.75 in long, split
   along its length (the split closes when it is off a bar), the lettering in black along it.
3. Adjustments. None: the size is the product.
4. Load path. The hand on the silicone, the bar inside it.
5. Fit range. 2.25 in across: every user (1.55 / 1.78 / 1.95 m) wraps it, the smaller hand not closing (the point).
   No figure.
6. Size. Each 57 x 121 mm.
Axes: metres, floor z = 0; one standing at -x, one lying along y at +x.
"""
import math

IN = 0.0254
RO, RI, L = 2.25 * IN / 2, 1.1 * IN / 2, 4.75 * IN
GAP = 0.0015                          # the split, closed up off the bar

LOOK = {
    "silicone": dict(color=(0.004, 0.06, 0.42), rough=0.55, coat=0.0, spec=0.35, bump=(5000, 0.08)),
    "ink": dict(color=(0.01, 0.01, 0.012), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 25, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_lettering": ((0.10, -0.25, 0.12), (0.04, 0.0, 0.03), 30),  # FAT GRIPZ along the lying one
}


def profile():
    """The section: an annulus cut through by the split (at angle 0)."""
    gi, go = GAP / 2 / RI, GAP / 2 / RO
    n = 40
    outer = [(RO * math.cos(go + (2 * math.pi - 2 * go) * i / n), RO * math.sin(go + (2 * math.pi - 2 * go) * i / n))
             for i in range(n + 1)]
    inner = [(RI * math.cos(gi + (2 * math.pi - 2 * gi) * i / n), RI * math.sin(gi + (2 * math.pi - 2 * gi) * i / n))
             for i in range(n, -1, -1)]
    return outer + inner


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    # standing on end, the split toward the back
    k.sweep("silicone", [(-0.06, 0, 0), (-0.06, 0, L)], profile(), up=(0, 1, 0), soft=0.0015)
    # lying along y, the split underneath, the lettering on top
    k.sweep("silicone", [(0.06, -L / 2, RO), (0.06, L / 2, RO)], profile(), up=(1, 0, 0), soft=0.0015)
    for text, size, dx in (("FAT GRIPZ", 0.02, 0.007), ("THE ULTIMATE ARM BUILDER", 0.0065, -0.011)):
        k.text("ink", text, (0.06 + dx, 0, 2 * RO + 0.0002), size, rx=0.0, rz=math.pi / 2, depth=0.0005)
    z0 = 2 * RO + 0.0002
    for v in k.bm("ink", 0).verts:                      # wrapped round the curve
        dx = v.co.x - 0.06
        h = v.co.z - z0
        a = dx / RO
        v.co.x = 0.06 + (RO + h + 0.0002) * math.sin(a)
        v.co.z = RO + (RO + h + 0.0002) * math.cos(a)
    for text, size, dz in (("FAT GRIPZ", 0.016, 0.0), ):  # up the standing one
        k.text("ink", text, (-0.06, -RO - 0.0002, L / 2), size, spin=math.pi / 2, depth=0.0005)

"""Rogue Sandbag 2.0, the S / M / L (refs/: ref_01 the three together; ref_02 the M on a step: the soft cylinder, the
filler flap on top with the grey ROGUE patch, the handles: a carry handle on top, loops at the ends and along the
sides; ref_03 / ref_04 carried; ref_05 the flap's zip). The linked page: S 19.5 x 7 in (40 lb of sand), M 24 x 9 in
(80 lb), L 35 x 10.5 in (150 lb), seven nylon webbing handles, 1000D Cordura, black, a grey laser-cut ROGUE on the
flap. Fetched 2026-10-24 / 25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Carries, cleans, shoulders, drags, throws: the bag picked up by its handles or bear-hugged; it shifts.
2. Each mass named (ref_02): the bag, a black Cordura cylinder (the filler bags of sand inside), soft: it settles
   flat where it rests and its ends round over; the flap down its front side (zipped) with the grey ROGUE on it; seven
   webbing handles: one across the top's middle, one at each end, two along each side.
3. Adjustments. The fill (sand or crumb rubber, by the filler bags).
4. Load path. The sand, the Cordura, the stitched handles, the hands.
5. Fit range. 7-10.5 in round: every user (1.55 / 1.78 / 1.95 m) bear-hugs the L and grips the S one-handed. No
   figure.
6. Size. The three side by side: 0.50 / 0.61 / 0.89 m long.
Axes: metres, floor z = 0; the bags along x, side by side along y.
"""
import math

IN = 0.0254
BAGS = (("S", 19.5 * IN, 7 * IN), ("M", 24 * IN, 9 * IN), ("L", 35 * IN, 10.5 * IN))
SQUASH = 0.82                         # the bag settles: its height over its width

LOOK = {
    "cordura": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(2400, 0.15)),
    "web": dict(color=(0.010, 0.010, 0.011), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "patch": dict(color=(0.28, 0.28, 0.29), rough=0.55),                                           # the grey ROGUE
    "ink": dict(color=(0.014, 0.014, 0.015), rough=0.6),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_bag": ((-0.45, -0.95, 0.55), (0.0, -0.40, 0.10), 35),       # ref_02: the M, its flap, its handles
}


def bag(k, y, L, d):
    r = d / 2
    h = d * SQUASH
    zc = h / 2
    sf = round(r * 0.35, 4)
    before = set(k.bm("cordura", sf).verts)
    k.cyl("cordura", (0, y, zc), r, L, axis="x", seg=48, soft=sf)          # a soft cylinder, its end panels rounded over
    for v in k.bm("cordura", sf).verts:                 # settled: squashed and flat where it rests
        if v not in before:
            v.co.z = zc + (v.co.z - zc) * SQUASH
            v.co.z = max(v.co.z, 0.0)
    top = h
    # the flap down the front side, a little up, the grey ROGUE on it (ref_02)
    a = math.radians(25)                                # the flap faces front and a little up
    fy, fz = y - (r - 0.004) * math.cos(a), zc + (h / 2 - 0.004) * math.sin(a) * 1.2
    k.box("cordura", (0, fy, fz), (L * 0.6, 0.008, h * 0.48), rx=-a, soft=0.003)
    k.text("patch", "ROGUE", (-L * 0.05, fy - 0.0045 * math.cos(a), fz + 0.0045 * math.sin(a)), min(0.06, d * 0.24),
           rx=math.pi / 2 - a, depth=0.0005)
    w = 0.038                                           # the webbing
    prof = k.rect(w, 0.004, 0.0015)
    # the top carry handle, across the middle (over the flap's far end)
    xt = L * 0.22
    k.sweep("web", [(xt, y - r * 0.55, top - 0.004), (xt, y - r * 0.35, top + 0.045), (xt, y + r * 0.35, top + 0.045),
                    (xt, y + r * 0.55, top - 0.004)], prof, bend=0.02, up=(1, 0, 0), soft=0.0)
    for s in (1, -1):                                   # a loop at each end
        xe = s * L / 2
        k.sweep("web", [(xe - s * 0.04, y, zc + h * 0.25), (xe + s * 0.035, y, zc + h * 0.15), (xe + s * 0.035, y, zc - h * 0.15),
                        (xe - s * 0.04, y, zc - h * 0.25)], k.rect(0.004, w, 0.0015), bend=0.02, soft=0.0)
    for sy in (1, -1):                                  # two along each side
        for xs in (-L * 0.25, L * 0.25):
            yy = y + sy * r * 0.98
            zl = zc - h * 0.05                          # long loops hanging loose along the side (ref_02)
            ys = yy + sy * 0.006
            k.sweep("web", [(xs - 0.11, ys, zl), (xs - 0.08, ys + sy * 0.008, zl - h * 0.38), (xs + 0.08, ys + sy * 0.008, zl - h * 0.38),
                            (xs + 0.11, ys, zl)], k.rect(w, 0.004, 0.0015), bend=0.025, up=(0, 1, 0), soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    y = -0.45
    for _, L, d in BAGS:
        y += d / 2
        bag(k, y, L, d)
        y += d / 2 + 0.12

"""Rogue 7mm Knee Sleeves, a pair, black (refs/: ref_01 the pair standing: black neoprene tubes shaped to the bent
knee, a seam curving round each, ROGUE in white up the side; ref_02 the bound edge; ref_03 the logo; ref_04 worn in a
squat). The linked page was not fetched (the refs carry it): 7 mm neoprene, the height about 30 cm, sizes XS-3XL; the
M shown, an estimate. Built to the two gates and README point 9 (kit.lathe, open ended).

DESIGN SPEC (gate 1)
1. Use. Squats and pulls: pulled up over the knee for warmth and support.
2. Each mass named (ref_01): a tube of 7 mm neoprene, wider at the thigh end, its edges bound; the seam; ROGUE.
3. Adjustments. The size (by the knee's girth).
4. Load path. The sleeve's compression round the knee.
5. Fit range. Sized XS-3XL by girth: the M fits the 1.78 m user, others a size either side. No figure.
6. Size. A pair standing, 0.30 m high, 0.13 m across.
Axes: metres, floor z = 0.
"""
import math

H, TH = 0.30, 0.007

LOOK = {
    "neo": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.3, bump=(2500, 0.08)),
    "bind": dict(color=(0.006, 0.006, 0.007), rough=0.85, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 15, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_logo": ((0.0, -0.55, 0.25), (0.08, 0.0, 0.15), 30),         # ROGUE up the side, the bound top
}


def radius(t):
    return 0.060 + 0.010 * t - 0.006 * math.sin(math.pi * t)          # wider at the top (the thigh), a waist


def sleeve(k, x):
    n = 24
    out = [(radius(i / n), H * i / n) for i in range(n + 1)]
    inn = [(radius(1 - i / n) - TH, H * (1 - i / n)) for i in range(n + 1)]
    k.lathe("neo", (x, 0, 0), out + inn, seg=64, caps=False)
    for z, r in ((H - 0.004, radius(1.0)), (0.004, radius(0.0))):      # the bound edges
        k.disc("bind", (x, 0, z), r + 0.0015, r - TH - 0.0015, 0.008, axis="z", seg=64, soft=0.002)
    r = radius(0.5)
    a = 0.35                                            # ROGUE up the side, flat on the tangent
    k.text("white", "ROGUE", (x + (r + 0.0002) * math.sin(a), -(r + 0.0002) * math.cos(a), H * 0.45), 0.024, rz=a,
           spin=math.pi / 2, depth=0.0016)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    sleeve(k, -0.08)
    sleeve(k, 0.08)

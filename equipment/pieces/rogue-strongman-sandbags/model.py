"""Rogue Strongman Sandbags, the eight sizes 25-400 lb (refs/: ref_01 the bags; ref_02 the range standing: black drums, a
flap across each top with the white ROGUE, the weights 25 / 50 / 100 / 150 below and 200 / 250 / 300 / 400 behind;
ref_03 the top's flap and ROGUE close; ref_04 / ref_05 lifted and loaded). The linked page: 1000D Cordura, black, a zip
under a hook-and-loop flap, the white ROGUE on the flap; 25 lb 11.5 x 4.5 in, 50 lb 13 x 6, 100 lb 16 x 7.5, 150 lb
16 x 11.5, 200 lb 16 x 15.5, 250 lb 16 x 19.5, 300 lb 16 x 22.5, 400 lb 16 x 36 (diameter x height). Fetched 2026-10-24
/ 25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Strongman sandbag lifts and carries: hugged off the floor, lapped, shouldered or loaded over a bar.
2. Each mass named (ref_02 / ref_03): the bag, a Cordura drum (sand in inner bags), soft: its top and bottom rounded
   over, its sides bulging a little; the flap across the top (a hook-and-loop strip over the zip) with the white
   ROGUE.
3. Adjustments. The fill.
4. Load path. The sand, the Cordura, the arms round it.
5. Fit range. 16 in across (the heavy ones): every user (1.55 / 1.78 / 1.95 m) wraps it, the 1.55 m user's hands
   meeting under it (1.28 m round against a 1.55 m span). No figure.
6. Size. Eight drums in two rows, as ref_02.
Axes: metres, floor z = 0; the rows along x, the flaps' lettering read from -y.
"""

IN = 0.0254
BAGS = ((25, 11.5, 4.5), (50, 13, 6), (100, 16, 7.5), (150, 16, 11.5), (200, 16, 15.5), (250, 16, 19.5), (300, 16, 22.5),
        (400, 16, 36))

LOOK = {
    "cordura": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(2400, 0.15)),
    "flap": dict(color=(0.015, 0.015, 0.016), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "white": dict(color=(0.85, 0.85, 0.86), rough=0.5),
}
VIEWS = {"three_quarter": (-30, 22, 1.0), "front": (0, 12, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_top": ((0.20, -0.75, 0.85), (0.25, 0.0, 0.40), 35),         # ref_03: a top's flap and ROGUE
}


def drum(k, x, y, d, h):
    r = d / 2
    sf = round(min(r, h / 2) * 0.35, 4)
    k.cyl("cordura", (x, y, h / 2), r, h, seg=64, soft=sf)                   # the drum, top and bottom rounded over
    w = min(0.11, d * 0.3)                              # the flap across the top
    k.box("flap", (x, y, h + 0.0012), (2 * (r - sf) - 0.01, w, 0.003), soft=0.001)   # sewn on the top's flat
    k.text("white", "ROGUE", (x, y, h + 0.0029), w * 0.42, rx=0.0, depth=0.0004)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    rows = (BAGS[:4], BAGS[4:])
    for i, row in enumerate(rows):                      # the light four in front, the tall four behind (ref_02)
        x = -0.85
        y = -0.25 + i * 0.55
        for lb, d, h in row:
            x += d * IN / 2
            drum(k, x, y, d * IN, h * IN)
            x += d * IN / 2 + 0.06

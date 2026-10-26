"""Rogue Rubber Atlas Stones, the 225 lb set: 50 / 75 / 100 lb (refs/: ref_01 / ref_02 the stones from 50 to 200 lb, black,
ROGUE and the weight embossed; ref_03 / ref_04 a stone lapped and loaded; ref_05 the embossing close; ref_06 on a
platform). The linked page: rubber over a cast iron core, black, the edges recessed against rolling, ROGUE and the
weight embossed on one side; 50 lb 10 in, 75 lb 12 in, 100 lb 14 in, 150 lb 16 in, 200 lb 18 in; the 225 lb set (the
first three) preselected. Fetched 2026-10-24 / 25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Stone lifts: the lifter straddles the stone, wraps it, laps it, stands and loads it over a bar or onto a
   platform.
2. Each mass named (ref_01 / ref_05): a ball of black rubber over its iron core, flattened a little at its poles (the
   recessed edges it rests on, so it doesn't roll), the weight embossed in a raised ring on one side, ROGUE over it
   and turned over under it.
3. Adjustments. None (a weight per stone).
4. Load path. The arms and chest round the stone.
5. Fit range. 10-14 in across: the 1.55 m user's arms (1.55 m span) wrap the 14 in (1.10 m round) with the hands
   meeting under; every user (1.55 / 1.78 / 1.95 m) laps them. No figure.
6. Size. Three stones in a row, 254 / 305 / 356 mm.
Axes: metres, floor z = 0; the row along x, the embossing toward -y.
"""
import math

IN = 0.0254
STONES = ((50, 10 * IN), (75, 12 * IN), (100, 14 * IN))
FLAT = 0.94                           # the poles flattened to this fraction of the radius

LOOK = {
    "rubber": dict(color=(0.009, 0.009, 0.010), rough=0.72, coat=0.0, spec=0.3, bump=(900, 0.05)),      # matte
    "ink": dict(color=(0.008, 0.008, 0.009), rough=0.55, coat=0.05),
}
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_stone": ((0.35, -0.75, 0.40), (0.33, 0.0, 0.17), 30),       # ref_05: the 100 lb's embossing
}


def stone(k, x, lb, d):
    r = d / 2
    zc = r * FLAT
    before = set(k.bm("rubber", 0.002).verts)
    k.sphere("rubber", (x, 0, zc), r, seg=64, soft=0.002)
    for v in k.bm("rubber", 0.002).verts:               # the flattened poles
        if v not in before:
            v.co.z = max(zc - r * FLAT, min(zc + r * FLAT, v.co.z))
    rho = r * 0.36                                      # the raised ring round the weight (ref_05)
    ring = [(x + rho * math.cos(a), -math.sqrt(r * r - rho * rho) - 0.0008, zc + rho * math.sin(a))
            for a in [2 * math.pi * i / 48 for i in range(49)]]
    k.sweep("ink", ring, k.circle(0.0025, 8), soft=0.0)
    k.text("ink", f"{lb}LB", (x, -r - 0.0002, zc), r * 0.26, depth=0.0015)
    for h, spin in ((0.56, 0.0), (-0.56, math.pi)):     # ROGUE over the ring and, turned over, under it
        z = zc + h * r
        tilt = math.asin(h)
        y = -math.sqrt(max(r * r - (h * r) ** 2, 0.0)) - 0.0002
        k.text("ink", "ROGUE", (x, y, z), r * 0.26, rx=math.pi / 2 - tilt, depth=0.0015, spin=spin)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = -0.40
    for lb, d in STONES:
        x += d / 2
        stone(k, x, lb, d)
        x += d / 2 + 0.10

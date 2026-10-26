"""Rogue Chain Kit, the 5/8 in (refs/: ref_01-04 hung off a barbell's sleeves on the bench: each heavy chain doubled
through a carabiner on a light lead chain round the sleeve, its ends on the floor; ref_05 the links close: zinc-plated,
long links alternating flat and edge on). The linked page: the 5/8 in kit, (2) 15 lb lengths of 5/8 in chain (29
links, about 4 ft) with carabiners, (2) 4 ft lengths of 1/4 in chain with carabiners. Fetched 2026-10-25. The links'
proportions (5/8 in wire, 1.65 in pitch) from the 29 links in 4 ft. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Accommodating resistance: a lead chain round each sleeve, the heavy chain through its carabiner, so the load
   comes off the floor link by link as the bar rises.
2. Each mass named (ref_05): the heavy chains, 29 links each of 5/8 in wire, zinc-plated, a carabiner clipped at the
   middle; the lead chains, 1/4 in, 4 ft, a carabiner on each.
3. Adjustments. The lead chain's length (where the carabiner clips) sets how much hangs.
4. Load path. The bar's sleeve, the lead chain, the carabiner, the heavy chain, the floor.
5. Fit range. A 4 ft lead and 4 ft heavy chain reach the floor from a squat or bench bar for every user (1.55 / 1.78 /
   1.95 m); the lead shortened for the short user's squat. No figure.
6. Size. The kit laid out on the floor: two heavy chains in loose U's, two lead chains coiled beside.
Axes: metres, floor z = 0.
"""
import math
from mathutils import Vector

IN = 0.0254

LOOK = {
    "zinc": dict(color=(0.62, 0.62, 0.64), rough=0.3, metal=1.0),
    "biner": dict(color=(0.70, 0.70, 0.72), rough=0.2, metal=1.0),
}
VIEWS = {"three_quarter": (-30, 35, 1.0), "front": (0, 25, 1.0), "side": (90, 25, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_links": ((-0.15, -0.55, 0.30), (-0.05, -0.20, 0.0), 30),   # the links, a carabiner
}


def link(k, c, t, flat, wire, pitch, width):
    """One link centred at c along the unit tangent t (in the floor plane); flat on the floor or standing on edge."""
    t = Vector((t[0], t[1], 0.0)).normalized()
    n = Vector((-t.y, t.x, 0.0)) if flat else Vector((0.0, 0.0, 1.0))
    half = pitch / 2 + wire                             # the centreline end to end: the inside is the pitch
    rr = width / 2 - wire
    pts = []
    for cx, a0 in ((half - rr, -90), (-half + rr, 90)):
        for i in range(9):
            a = math.radians(a0 + 180 * i / 8)
            pts.append(c + t * (cx + rr * math.cos(a)) + n * (rr * math.sin(a)))
    pts.append(pts[0])
    k.sweep("zinc", [tuple(p) for p in pts], k.circle(wire, 10), soft=0.0)


def chain(k, path, n, wire, pitch, width):
    """n links along a floor polyline, alternating flat and on edge."""
    P = [Vector(p) for p in path]
    seg = [(a, b, (b - a).length) for a, b in zip(P, P[1:])]
    total = sum(s[2] for s in seg)
    step = total / n
    out = []
    for i in range(n):
        s = (i + 0.5) * step
        for a, b, L in seg:
            if s <= L:
                p = a + (b - a) * (s / L)
                t = (b - a).normalized()
                break
            s -= L
        flat = i % 2 == 0
        z = wire if flat else width / 2
        link(k, Vector((p.x, p.y, z)), t, flat, wire, pitch, width)
        out.append((p, t))
    return out


def carabiner(k, c, t, size=0.08):
    """A carabiner lying flat at c along t."""
    t = Vector((t[0], t[1], 0.0)).normalized()
    n = Vector((-t.y, t.x, 0.0))
    pts = []
    for i in range(33):
        a = 2 * math.pi * i / 32
        r = size / 2 * (1.0 + 0.15 * math.cos(a))
        pts.append(tuple(Vector(c) + t * (r * math.cos(a)) + n * (size * 0.3 * math.sin(a)) + Vector((0, 0, 0.0055))))
    k.sweep("biner", pts, k.circle(0.0055, 10), soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    heavy = (5 / 8 * IN / 2, 1.65 * IN, 2.2 * IN)      # wire radius, pitch, outer width
    light = (1 / 4 * IN / 2, 0.85 * IN, 0.95 * IN)
    for y0 in (-0.30, 0.30):
        mid = chain(k, [(-0.55, y0 - 0.05, 0), (-0.15, y0 + 0.10, 0), (0.15, y0 + 0.10, 0), (0.55, y0 - 0.05, 0)], 29, *heavy)
        p, t = mid[14]
        carabiner(k, (p.x, p.y - 0.06, 0), (0, 1, 0))
        lead = [(0.70 + 0.12 * math.cos(a), y0 + 0.10 * math.sin(a), 0) for a in [2 * math.pi * i / 40 for i in range(41)]]
        lead += [(0.70 + 0.12 - 0.06 * i, y0 - 0.04 * i, 0) for i in range(1, 6)]
        lp = chain(k, lead, 56, *light)
        carabiner(k, (lp[-1][0].x - 0.04, lp[-1][0].y - 0.02, 0), lp[-1][1], size=0.07)

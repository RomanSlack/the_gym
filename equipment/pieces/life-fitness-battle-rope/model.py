"""Life Fitness Battle Rope with its anchor (refs/: ref_01 the rope coiled: dark grey, three strands twisted, grey
heat-shrink sleeves on its ends; ref_02-04 in use, its middle round an anchor, the two ends in the hands). The shop
page refuses requests (HTTP 429): the rope's size, 1.5 in and 50 ft, is the usual one and an estimate; the anchor is
not in the refs: a bolted floor anchor plate with an eye, ours. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Waves, slams, whips: the rope's middle round the anchor, an end in each hand, the user 7 m back from it.
2. Each mass named (ref_01): the rope, 38 mm, three strands laid in a twist, 15 m; a heat-shrink sleeve on each end (the
   grips); the anchor: a steel plate bolted to the floor, an eye standing on it.
3. Adjustments. How far back the user stands (the slack).
4. Load path. The hands, the rope, the anchor's eye, its bolts into the floor.
5. Fit range. 38 mm in the hand: every user (1.55 / 1.78 / 1.95 m) grips the sleeves in an athletic squat. No figure.
6. Size. The rope coiled (as ref_01) by the anchor.
Axes: metres, floor z = 0.
"""
import math

IN = 0.0254
R = 0.75 * IN
LENGTH = 50 * 0.3048
PITCH = 0.12                          # a strand's lay length

LOOK = {
    "rope": dict(color=(0.035, 0.035, 0.038), rough=0.95, coat=0.0, spec=0.2, bump=(3000, 0.3)),
    "sleeve": dict(color=(0.06, 0.06, 0.065), rough=0.45, coat=0.1),
    "steel": dict(color=(0.45, 0.45, 0.47), rough=0.35, metal=1.0),
}
VIEWS = {"three_quarter": (-30, 30, 1.0), "front": (0, 15, 1.0), "side": (90, 15, 1.0), "back_three_quarter": (150, 30, 1.0)}
DETAILS = {
    "detail_coil": ((-0.55, -0.85, 0.55), (0.0, -0.05, 0.05), 35),      # the coil, the strands, an end
}


def strands(n=30):
    """The rope's section: three strands (a trefoil)."""
    return [((R * (0.76 + 0.24 * math.cos(3 * t))) * math.cos(t), (R * (0.76 + 0.24 * math.cos(3 * t))) * math.sin(t))
            for t in [2 * math.pi * i / n for i in range(n)]]


def coil_path():
    """Three layers of a flat spiral, then the ends out across the floor."""
    pts = []
    tail = 1.1                                          # each end's run out of the coil
    left = LENGTH - 2 * tail
    layer = 0
    a, r, z = 0.0, 0.34, R
    while left > 0:
        x, y = r * math.cos(a), 0.78 * r * math.sin(a)
        if pts:
            left -= math.dist(pts[-1], (x, y, z))
        pts.append((x, y, z))
        a += 0.04
        r -= 0.04 * 2 * R * 1.05 / (2 * math.pi)        # inward a rope's width a turn
        if r < 0.20:                                    # next layer up, starting outside again
            r, layer, z = 0.34, layer + 1, z + 2 * R * 0.9
    start = [(0.34 + tail - 0.05 * i, 0.0, R) for i in range(int(tail / 0.05), 0, -1)]
    end = [(pts[-1][0] + (0.9 * i / 20) * 1.0, pts[-1][1] - 0.6 * i / 20, max(R, pts[-1][2] - 0.08 * i)) for i in range(1, 21)]
    return start + pts + end


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    raw = coil_path()
    path = [raw[0]]                                     # resampled every 8 mm: the twist evenly along it
    for p, q in zip(raw, raw[1:]):
        n = max(1, int(math.dist(p, q) / 0.008))
        path += [tuple(p[i] + (q[i] - p[i]) * j / n for i in range(3)) for j in range(1, n + 1)]
    L = sum(math.dist(p, q) for p, q in zip(path, path[1:]))
    k.sweep("rope", path, strands(), twist=2 * math.pi * L / PITCH, soft=0.0)
    for p, q in ((path[0], path[1]), (path[-1], path[-2])):  # the sleeves on the ends
        d = [(q[i] - p[i]) / math.dist(p, q) for i in range(3)]
        e = tuple(p[i] + d[i] * 0.25 for i in range(3))
        k.tube("sleeve", (p[0] - d[0] * 0.01, p[1] - d[1] * 0.01, p[2]), e, R * 1.12, seg=24)
    # the anchor: a plate bolted to the floor, an eye on it
    ax = 0.85
    k.box("steel", (ax, -0.40, 0.005), (0.14, 0.14, 0.01), soft=0.002)
    for dx in (-0.05, 0.05):
        for dy in (-0.05, 0.05):
            k.cyl("steel", (ax + dx, -0.40 + dy, 0.012), 0.009, 0.006, seg=6, soft=0.0005)
    eye = [(ax + 0.045 * math.cos(t), -0.40, 0.01 + 0.06 * math.sin(t)) for t in [math.pi * i / 20 for i in range(21)]]
    k.sweep("steel", eye, k.circle(0.008, 12), soft=0.0)

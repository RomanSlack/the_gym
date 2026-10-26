"""Rogue Manila Climbing Rope, braided eyelet, 1.5 in x 15 ft (refs/: ref_01-04 climbed: tan manila, three strands
laid in a twist, hung from a rig; ref_05 coiled: the braided eyelet at one end, the other end whipped black). The
linked page: manila, 1.5 in, 6 / 15 / 20 / 25 / 30 ft, a braided eyelet (no bracket needed). Fetched 2026-10-25. The
15 ft for a 4.5 m mount. Built to the two gates and README point 9. Hung from a display section of a red Monster
upright with a crossmember stub, an eye bolt and a shackle (not the piece; the rig's colours, Roman's rule).

DESIGN SPEC (gate 1)
1. Use. Rope climbs (J-hook or S-wrap the feet, pull, stand), legless climbs; the rope's tail on the floor.
2. Each mass named (ref_05): the rope, 38 mm manila, three strands laid in a twist; the braided eyelet at the top (a
   loop of the rope spliced back into itself); the bottom end whipped black.
3. Adjustments. None (a length).
4. Load path. The hands and feet on the rope, the eyelet, the shackle, the eye bolt, the rig.
5. Fit range. The top at 4.45 m: every user (1.55 / 1.78 / 1.95 m) starts seated or standing at its foot and climbs
   to touch the stub. No figure.
6. Size. 4.57 m, 0.3 m of it lying on the floor.
Axes: metres, floor z = 0; the rope hanging at the origin, the upright at +y.
"""
import math
from mathutils import Vector

IN = 0.0254
R = 0.75 * IN
L = 15 * 0.3048
Z_TOP = 4.45
PITCH = 0.13

LOOK = {
    "manila": dict(color=(0.30, 0.19, 0.08), rough=0.95, coat=0.0, spec=0.2, bump=(3000, 0.4)),
    "whip": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.1),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.2),
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15),
    "steel": dict(color=(0.55, 0.55, 0.57), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-35, 10, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_top": ((-0.6, -0.8, 4.6), (0.0, 0.0, 4.25), 35),           # the eyelet, the shackle, the eye bolt
    "detail_foot": ((-0.6, -0.8, 0.5), (0.0, -0.10, 0.15), 35),        # the tail on the floor, the whipped end
}


def strands(n=30):
    return [((R * (0.78 + 0.22 * math.cos(3 * t))) * math.cos(t), (R * (0.78 + 0.22 * math.cos(3 * t))) * math.sin(t))
            for t in [2 * math.pi * i / n for i in range(n)]]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    # the display: a red Monster upright, a black stub out over the rope
    k.bar("red", (0, 0.45, 0.0), (0, 0.45, Z_TOP + 0.25), 3 * IN, 3 * IN, r=0.004)
    k.bar("frame", (0, 0.45 - 1.5 * IN, Z_TOP + 0.16), (0, -0.06, Z_TOP + 0.16), 2 * IN, 3 * IN, r=0.004)
    k.tube("steel", (0, 0, Z_TOP + 0.16), (0, 0, Z_TOP + 0.10), 0.008, seg=12)                       # the eye bolt
    eye = [(0.0, 0.022 * math.cos(t), Z_TOP + 0.078 + 0.022 * math.sin(t)) for t in [2 * math.pi * i / 24 for i in range(25)]]
    k.sweep("steel", eye, k.circle(0.006, 10), soft=0.0)
    shackle = [(-0.025, 0, Z_TOP + 0.03)] + [(0.025 * math.cos(t), 0.0, Z_TOP + 0.045 + 0.03 * math.sin(t))
                                             for t in [math.pi * i / 16 for i in range(17)]][::-1] + [(0.025, 0, Z_TOP + 0.03)]
    k.sweep("steel", shackle, k.circle(0.006, 10), soft=0.0)
    k.tube("steel", (-0.032, 0, Z_TOP + 0.03), (0.032, 0, Z_TOP + 0.03), 0.007, seg=12)             # its pin
    # the braided eyelet round the shackle's pin, the rope down from it and its tail across the floor
    loop = [(0.0, 0.0, Z_TOP - 0.05)] + [(0.035 * math.sin(t), 0.0, Z_TOP - 0.02 + 0.05 * (1 - math.cos(t)) * 0.5)
                                        for t in [2 * math.pi * i / 24 for i in range(25)]] + [(0.0, 0.0, Z_TOP - 0.05)]
    k.sweep("manila", loop, k.circle(R * 0.8, 14), soft=0.0)
    splice = [(0, 0, Z_TOP - 0.02 - 0.2 * i / 20) for i in range(21)]                              # the splice
    k.sweep("manila", splice, [(1.2 * x, 1.2 * y) for x, y in strands()], twist=2 * math.pi * 0.2 / (PITCH * 0.7), soft=0.0)
    raw = [(0, 0, Z_TOP - 0.05), (0, 0, R + 0.25), (0, -0.04, R + 0.05), (0, -0.30, R)]
    path = []
    pts = [Vector(p) for p in raw]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int((b - a).length / 0.01))
        path += [tuple(a + (b - a) * j / n) for j in range(n)]
    path.append(tuple(pts[-1]))
    length = sum(math.dist(p, q) for p, q in zip(path, path[1:]))
    k.sweep("manila", path, strands(), twist=2 * math.pi * length / PITCH, soft=0.0)
    k.tube("whip", (0, -0.30 + 0.002, R), (0, -0.30 + 0.06, R), R * 1.05, seg=20)                    # the whipped end

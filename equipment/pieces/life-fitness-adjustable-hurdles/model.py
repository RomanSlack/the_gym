"""Life Fitness Adjustable Hurdles (refs/: ref_01 / ref_02 one: a lime-green tube bent into the top, its ends sliding
down into black legs, each leg an L to a foot along the floor with lime end caps, a green collar where the tube goes
in, the LifeFitness script on the top bar; ref_03 from the side). The shop page refuses requests (HTTP 429): the
sizes are estimates (0.60 m wide, the top set 6, 9 or 12 in up by how far the green slides out). Built to the two gates
and README point 9.

DESIGN SPEC (gate 1)
1. Use. Agility and plyometric drills: stepped or hopped over in a line; they tip if hit.
2. Each mass named (ref_01): the top, lime-green tube bent into an inverted U; two black legs, each a tube rising from
   a foot along the floor (lime caps), the green tube slid into it to a collar; the script on the top.
3. Adjustments. The height: the green slides in the legs, 6 / 9 / 12 in.
4. Load path. Nothing carries load: it stands on its feet and tips when struck.
5. Fit range. 6-12 in: every user (1.55 / 1.78 / 1.95 m) steps or hops it (0.10-0.20 H). No figure.
6. Size. Three in a line, one at each height, 0.60 x 0.30 m each.
Axes: metres, floor z = 0; the tops along x, the line along y.
"""
import math

IN = 0.0254
W = 0.60
R_G, R_B = 0.011, 0.013
FOOT = 0.30
HEIGHTS = (6 * IN, 9 * IN, 12 * IN)

LOOK = {
    "lime": dict(color=(0.35, 0.65, 0.02), rough=0.45, coat=0.0, spec=0.4),
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.1),
    "ink": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_leg": ((-0.65, -0.55, 0.35), (-0.30, -0.10, 0.12), 35),     # a leg, its collar, the foot's caps
}


def hurdle(k, y, h):
    zl = 0.12                                           # the legs' tops
    for sx in (1, -1):
        x = sx * W / 2
        k.sweep("black", [(x, y - FOOT / 2, R_B), (x, y, R_B), (x, y, zl)], k.circle(R_B, 16), bend=0.04, soft=0.0)
        k.cyl("lime", (x, y - FOOT / 2 - 0.008, R_B), R_B + 0.002, 0.02, axis="y", seg=16, soft=0.002)      # its cap
        k.cyl("lime", (x, y, zl + 0.01), R_B + 0.003, 0.03, seg=16, soft=0.002)                           # the collar
    zt = max(h, zl + 0.04)                              # the top at the set height (the green slid out to it)
    k.sweep("lime", [(-W / 2, y, zl - 0.03), (-W / 2, y, zt), (W / 2, y, zt), (W / 2, y, zl - 0.03)], k.circle(R_G, 16),
            bend=0.06, soft=0.0)
    k.text("ink", "LifeFitness", (0.10, y, zt + R_G + 0.0002), 0.018, rx=0.0, depth=0.0004)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, h in enumerate(HEIGHTS):
        hurdle(k, (i - 1) * 0.55, h)

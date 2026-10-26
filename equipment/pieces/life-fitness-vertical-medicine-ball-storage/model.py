"""Life Fitness Vertical Medicine Ball Storage (refs/: ref_01 black, ref_02 silver, loaded with five balls in a column;
ref_03 empty: one post on a base of two feet, five ring cradles up it, each a loop of rod on a short arm, the balls
sitting in them one above the other). The shop page refuses requests (HTTP 429): every size is an estimate off the
refs against the balls (about 1.40 m high). Built to the two gates and README point 9. Shown black, loaded with five
of the LF medicine balls (their builder: pieces/life-fitness-medicine-balls), the lightest on top.

DESIGN SPEC (gate 1)
1. Use. Medicine ball storage in a column: a ball lifted out of its ring and set back.
2. Each mass named (ref_03): the base, a foot along x and one along y, end caps; the post, square tube, leaning
   back a little; five ring cradles, a loop of rod on an arm out from the post's front; the plate on the foot.
3. Adjustments. None.
4. Load path. The balls in the rings, the arms, the post, the feet.
5. Fit range. Rings at 0.06-1.14 m: the heavy balls low (a hinge for every user, 1.55-1.95 m), the light ones at
   chest height. No figure.
6. Size. 0.55 x 0.60 x 1.40 m.
Axes: metres, floor z = 0; the post at the origin, the balls at -y in front of it.
"""
import importlib.util
import math
import os

H = 1.40
LEAN = 0.08                           # the post's top back of its foot (ref_01)
POST = 0.05
R_RING = 0.085
LEVELS = (0.06, 0.33, 0.60, 0.87, 1.14)     # the balls close in a column (ref_01)
LOAD = (12, 10, 8, 6, 4)              # low to high
Y_BALL = -0.19


def _balls():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "life-fitness-medicine-balls", "model.py")
    spec = importlib.util.spec_from_file_location("lfmb", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MB = _balls()
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "badge": dict(color=(0.55, 0.40, 0.15), rough=0.35, metal=0.8),
}
LOOK.update({r: v for r, v in MB.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_ring": ((-0.55, -0.75, 0.75), (0.0, -0.15, 0.55), 35),      # a ring cradle with its ball
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.bar("frame", (-0.27, 0, 0.025), (0.27, 0, 0.025), 0.05, 0.05, r=0.004)                         # a foot along x
    k.bar("frame", (0, -0.42, 0.025), (0, 0.18, 0.025), 0.05, 0.05, r=0.004)                         # one along y
    k.box("badge", (0.0, 0.10, 0.051), (0.03, 0.08, 0.002), soft=0.0)
    k.bar("frame", (0, 0, 0.05), (0, LEAN, H), POST, POST, r=0.004)                                  # the post
    for z, lb in zip(LEVELS, LOAD):
        ring = [(R_RING * math.cos(t), Y_BALL + R_RING * math.sin(t), z) for t in [2 * math.pi * i / 40 for i in range(41)]]
        k.sweep("frame", ring, k.circle(0.006, 10), soft=0.0)                                        # the ring
        k.tube("frame", (0, LEAN * z / H - POST / 2 + 0.005, z), (0, Y_BALL + R_RING - 0.002, z), 0.008, seg=12)  # its arm
        r = MB.diameter(lb) / 2
        zc = z + math.sqrt(r * r - R_RING ** 2) + 0.004
        before = {key: set(g.verts) for key, g in k.groups.items()}
        MB.ball(k, 0.0, Y_BALL, lb)                    # built resting at z = r; lifted into its ring
        for key, g in k.groups.items():
            for v in g.verts:
                if v not in before.get(key, ()):
                    v.co.z += zc - r

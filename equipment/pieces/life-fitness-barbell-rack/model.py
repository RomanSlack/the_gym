"""Life Fitness Barbell Rack (refs/: ref_01 black, loaded with ten fixed barbells; ref_02 black, empty; ref_03 silver,
loaded; ref_04 / ref_05 silver, empty: two A-frames, each a front and a rear post leaning together toward the top on a
foot running front to back, five cradles up the outside of each post, the frames joined by a crossmember at the back
with the Life Fitness plate and by a top bar). The shop page refuses requests (HTTP 429): every size is an estimate
off the refs against the barbells (about 1.45 m high, 0.80 m between the frames, 0.80 m deep). Built to the two gates
and README point 9. Shown black (ref_01 / ref_02, Roman's metal palette), loaded with the 12-sided EZ set (its
builder: pieces/life-fitness-12-sided-fixed-urethane-barbells).

DESIGN SPEC (gate 1)
1. Use. Vertical storage for ten fixed barbells: each racked across the two frames on a pair of cradles, front or
   back, the heads outside the frames.
2. Each mass named (ref_02 / ref_04): two frames, each a foot (oval tube, front to back, end caps) and two posts
   leaning in to meet a short top; five cradles on the outside of each post (a J bent out and up, a plastic liner);
   the rear crossmember with the Life Fitness plate; the top bar.
3. Adjustments. None.
4. Load path. The bars on the cradles, the posts, the feet.
5. Fit range. The cradles from 0.30 to 1.30 m: every user (1.55 / 1.78 / 1.95 m) lifts the lowest with a hinge and the
   top one at chest height. No figure.
6. Size. 0.90 x 0.80 x 1.45 m.
Axes: metres, floor z = 0; the frames at x = +-0.40, the front toward -y.
"""
import importlib.util
import math
import os

XF = 0.40                             # the frames
H = 1.45
Y_FOOT, Y_TOP = 0.40, 0.10            # the posts' feet and tops (+-y)
LEVELS = (0.30, 0.55, 0.80, 1.05, 1.30)
R_P = 0.030

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "liner": dict(color=(0.02, 0.02, 0.022), rough=0.8, coat=0.0),
    "plate": dict(color=(0.5, 0.5, 0.52), rough=0.3, metal=1.0),
    "lfink": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_cradle": ((-0.95, -1.0, 1.25), (-0.40, -0.25, 1.0), 35),    # a post, its cradles, a bar on them
}


def _bars():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "life-fitness-12-sided-fixed-urethane-barbells",
                     "model.py")
    spec = importlib.util.spec_from_file_location("lf12", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BARS = _bars()
LOOK.update({r: v for r, v in BARS.LOOK.items() if r not in LOOK})      # the bars' chrome, knurl, urethane, print


def post_y(z, s):
    """A post's y at height z (s = -1 front, +1 rear)."""
    return s * (Y_FOOT - (Y_FOOT - Y_TOP) * z / H)


def cradle(k, x, z, s):
    """A J-cradle out from the post at height z."""
    y0 = post_y(z, s)
    k.sweep("frame", [(x, y0, z), (x, y0 + s * 0.085, z), (x, y0 + s * 0.11, z + 0.04)], k.rect(0.035, 0.008, 0.002),
            bend=0.02, up=(0, 0, 1), soft=0.0)
    k.box("liner", (x, y0 + s * 0.06, z + 0.006), (0.036, 0.05, 0.004), soft=0.001)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sx in (1, -1):
        x = sx * XF
        k.sweep("frame", [(x, -Y_FOOT - 0.06, 0.025), (x, Y_FOOT + 0.06, 0.025)], k.oval(0.05, 0.05, 20), soft=0.0)  # foot
        for s in (-1, 1):
            k.tube("frame", (x, post_y(0.0, s), 0.04), (x, post_y(H, s), H), R_P, seg=24)           # a post
            for z in LEVELS:
                cradle(k, x + sx * (R_P + 0.0), z, s)
        k.tube("frame", (x, -Y_TOP - R_P, H - 0.01), (x, Y_TOP + R_P, H - 0.01), R_P, seg=24)       # the posts' top
    k.bar("frame", (-XF, post_y(0.75, 1), 0.75), (XF, post_y(0.75, 1), 0.75), 0.05, 0.075, r=0.004)  # rear crossmember
    k.box("plate", (0, post_y(0.75, 1) - 0.030, 0.75), (0.24, 0.020, 0.05), soft=0.001)
    k.text("lfink", "LifeFitness", (0, post_y(0.75, 1) - 0.0402, 0.75), 0.03, depth=0.0004)
    k.tube("frame", (-XF, 0.0, H - 0.01), (XF, 0.0, H - 0.01), R_P, seg=24)                         # the top bar
    # loaded: the nine EZ bars, the heaviest low, front then back
    m = BARS
    slots = [(z, s) for z in LEVELS for s in (-1, 1)]
    for (z, s), kg in zip(slots, sorted(m.WEIGHTS, reverse=True)):
        before = {key: set(g.verts) for key, g in k.groups.items()}
        size, _ = m.size(kg)
        m.bar(k, kg, 0.0)                               # built lying at y = 0, its axis at size / 2
        yc = post_y(z, s) + s * 0.075
        zc = z + 0.008 + m.R_SH
        for key, g in k.groups.items():
            for v in g.verts:
                if v not in before.get(key, ()):
                    v.co.z += zc - size / 2
                    v.co.y += yc

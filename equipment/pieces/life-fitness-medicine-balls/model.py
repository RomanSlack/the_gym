"""Life Fitness medicine balls (refs/: ref_01 one close: black textured rubber, two broad coloured stripes across it,
the Life Fitness script between them; ref_02 / ref_03 the range: 4 lb yellow, 6 green, 8 orange, 10 red, 12 blue,
15 red, 18 purple, 20 / 25 grey, 30 black, the weight in white with "lb", the balls growing with the weight). The
linked page (shop.lifefitness.com) has rate-limited us: the diameters (7.5 in at 4 lb to 11 in at 30) are read off
ref_02 / ref_03, estimates. Built to the two gates and README point 9 (wrapped print: equipment/blender/balls.py).

DESIGN SPEC (gate 1)
1. Use. Throws, slams, passes, rotational work, med ball cleans; it bounces.
2. Each mass named (ref_01): a hollow ball of textured rubber, two coloured stripes round it (straight here; ref_01's kink
   left out), the weight and the script on the black between.
3. Adjustments. None: a weight per ball, ten from 4 to 30 lb.
4. Load path. The hands on the rubber, the throw.
5. Fit range. 7.5-11 in: every user (1.55 / 1.78 / 1.95 m) holds them in two hands, the light ones in one. No figure.
6. Size. Ten balls in two rows, 0.19-0.28 m.
Axes: metres, floor z = 0; the weights toward -y.
"""
import math
import balls

IN = 0.0254
SET = ((4, (0.75, 0.55, 0.0)), (6, (0.10, 0.40, 0.05)), (8, (0.75, 0.22, 0.0)), (10, (0.55, 0.03, 0.03)),
       (12, (0.02, 0.15, 0.62)), (15, (0.55, 0.03, 0.05)), (18, (0.25, 0.08, 0.50)), (20, (0.22, 0.22, 0.23)),
       (25, (0.22, 0.22, 0.23)), (30, (0.05, 0.05, 0.055)))

LOOK = {
    "rubber": dict(color=(0.012, 0.012, 0.013), rough=0.75, coat=0.0, spec=0.3, bump=(900, 0.4)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "script": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0, spec=0.5),
}
for lb, col in SET:
    LOOK[f"stripe{lb}"] = dict(color=col, rough=0.7, coat=0.0, spec=0.3, bump=(900, 0.3))
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_ball": ((-0.35, -0.95, 0.25), (-0.35, -0.15, 0.12), 30),    # the 12 lb, as ref_01
}


def diameter(lb):
    return (7.5 + 3.5 * (lb - 4) / 26) * IN


def ball(k, x, y, lb):
    r = diameter(lb) / 2
    c = (x, y, r)
    k.sphere("rubber", c, r, seg=64, soft=0.002)
    for lat0, lat1 in ((0.30, 0.62), (-0.62, -0.30)):    # the two stripes (ref_01)
        balls.zone(k, f"stripe{lb}", c, r, lat0, lat1)
    balls.label(k, "white", f"{lb}", c, r + 0.0006, r * 0.62, lat=-0.02, lon=math.radians(-20), depth=0.0006)
    balls.label(k, "white", "lb", c, r + 0.0006, r * 0.18, lat=-0.12, lon=math.radians(-20) + 0.42, depth=0.0005)
    balls.label(k, "script", "LifeFitness", c, r + 0.0006, r * 0.22, lat=0.0, lon=math.radians(70), depth=0.0005)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for row, part in enumerate((SET[:5], SET[5:])):
        x = -0.75
        for lb, _ in part:
            d = diameter(lb)
            x += d / 2
            ball(k, x, row * 0.40, lb)
            x += d / 2 + 0.07

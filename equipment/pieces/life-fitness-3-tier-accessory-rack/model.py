"""Life Fitness 3-Tier Accessory Rack, as the kettlebell rack (refs/: ref_01 black, ref_02 silver: three steel shelves
stepping back as they rise, a lip at each shelf's front and back, carried on two side frames: a foot front to back, a
rear post rising and bending forward, a strut to each shelf's front). The shop page refuses requests (HTTP 429): every
size is an estimate off the refs (about 1.10 m wide, 0.70 m deep, 0.80 m high). Built to the two gates and README
point 9. Shown black, loaded with the LF cast iron kettlebells (their builder: equipment/blender/kettlebell.py, sizes
from that piece).

DESIGN SPEC (gate 1)
1. Use. Kettlebell (and dumbbell) storage at three heights: lifted off and set back by the handle.
2. Each mass named (ref_01): three shelves, steel sheet with a raised lip front and back, each wider than deep; two side
   frames: a foot on the floor front to back, a rear post up from its back end, the shelves' side rails from the post
   forward, a strut down from each rail's front; the Life Fitness badge on a foot.
3. Adjustments. None.
4. Load path. The bells on the shelves, the rails, the posts and struts, the feet.
5. Fit range. Shelves at 0.20 / 0.48 / 0.76 m: the heaviest low (a hinge for every user, 1.55-1.95 m), the light ones
   at hip height. No figure.
6. Size. 1.10 x 0.70 x 0.80 m.
Axes: metres, floor z = 0; the shelves along x, the front toward -y.
"""
import importlib.util
import os
import kettlebell as kb

W = 1.10
XS = W / 2 - 0.03                     # the side frames
SHELVES = ((0.20, -0.24), (0.48, -0.09), (0.76, 0.06))     # (top z, centre y)
DEP = 0.28
TUBE = 0.05


def _bells():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "life-fitness-cast-iron-kettlebells", "model.py")
    spec = importlib.util.spec_from_file_location("lfkb", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BELLS = _bells()
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "shelf": dict(color=(0.02, 0.02, 0.021), rough=0.6, coat=0.0, bump=(2500, 0.15)),
    "badge": dict(color=(0.55, 0.40, 0.15), rough=0.35, metal=0.8),
}
LOOK.update({r: v for r, v in BELLS.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_shelf": ((-0.9, -1.0, 0.95), (-0.35, -0.10, 0.45), 35),     # a side frame, the shelves, bells
}
LOADS = ((24, 28, 32), (12, 16, 20), (4, 8))          # by shelf, low to high


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    y_post = SHELVES[-1][1] + DEP / 2 + TUBE / 2
    for sx in (1, -1):
        x = sx * XS
        k.bar("frame", (x, -0.40, TUBE / 2), (x, y_post + 0.05, TUBE / 2), TUBE, TUBE, r=0.004)                  # the foot
        k.sweep("frame", [(x, y_post, TUBE), (x, y_post, 0.62), (x, y_post - 0.10, 0.80)], k.rect(TUBE, TUBE, 0.004),
                bend=0.12, up=(1, 0, 0), soft=0.0)                                                                # the post
        for z, yc in SHELVES:
            yf = yc - DEP / 2
            k.bar("frame", (x, yf, z - 0.02), (x, y_post, z - 0.02), TUBE * 0.8, 0.04, r=0.003)                # a rail
            k.tube("frame", (x, yf + 0.02, z - 0.04), (x, max(yf - 0.10, -0.38), TUBE), 0.016, seg=16)          # a strut
    k.box("badge", (XS + TUBE / 2 + 0.001, -0.30, TUBE / 2), (0.002, 0.06, 0.018), soft=0.0)
    for (z, yc), load in zip(SHELVES, LOADS):
        k.box("shelf", (0, yc, z - 0.003), (2 * XS + TUBE, DEP, 0.006), soft=0.001)                          # the shelf
        for dy in (-DEP / 2, DEP / 2):                  # its lips
            k.box("shelf", (0, yc + dy, z + 0.012), (2 * XS + TUBE, 0.006, 0.03), soft=0.001)
        sizes = [BELLS.size(kg)[0] for kg in load]
        gap = (2 * XS - 0.08 - 2 * sum(sizes)) / (len(load) + 1)
        x = -XS + 0.04 + gap
        for kg, R in zip(load, sizes):
            col = dict(BELLS.BELLS)[kg]
            _, hr, hw, hh = BELLS.size(kg)
            kb.bell(k, (x + R, yc, z), R, hr, hw, hh, "iron", "iron", col,
                    [(f"{kg}KG", R * 0.24, 0.12), (f"{round(kg * 2.2046)}LB", R * 0.24, -0.20)], arch=hw * 0.9, face=R * 0.45)
            x += 2 * R + gap

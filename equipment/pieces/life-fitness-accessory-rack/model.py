"""Life Fitness Accessory Rack (refs/: ref_01 the tower empty: two square uprights on feet front to back, three
perforated shelves with lips between them, a top bar with hooks out at the top; ref_02 with its attachments: two
ring cradles out one side for stability balls, a wire roller holder at the foot of the other, a hook arm at the top;
ref_03 loaded: balls, kettlebells, stability balls, rollers, a mat). The shop page refuses requests (HTTP 429): every
size is an estimate off the refs (about 0.70 m between the uprights' outsides, 1.75 m high). Built to the two gates
and README point 9. Shown black with ref_02's attachments, loaded from the pieces' own builders: LF medicine balls,
LF kettlebells, HS stability balls (55 cm), LF foam rollers (18 in).

DESIGN SPEC (gate 1)
1. Use. One tower for the small kit (the brief: rollers, bands, guns): balls and bells on the shelves, stability balls
   in the rings, rollers standing in the holder, bands and straps on the top hooks.
2. Each mass named (ref_01 / ref_02): two uprights, 50 mm square, on feet front to back with end caps; three shelves,
   perforated steel with a lip front and back; the top bar; a hook out each side at the top; two ring cradles on arms
   out the right upright; the roller holder, a rod basket at the left foot.
3. Adjustments. The attachments go either side.
4. Load path. The kit on the shelves and cradles, the uprights, the feet.
5. Fit range. Shelves at 0.12 / 0.48 / 0.86 m, hooks at 1.60 m: every user (1.55 / 1.78 / 1.95 m) reaches all of it
   (the 1.55 m user's reach about 2.0 m). No figure.
6. Size. 1.45 x 0.45 x 1.75 m with the attachments.
Axes: metres, floor z = 0; the uprights at x = +-0.33, the shelves facing -y.
"""
import importlib.util
import math
import os
import kettlebell as kb

XU, H, TUBE = 0.33, 1.75, 0.05
SHELVES = (0.12, 0.48, 0.86)
DEP = 0.32
RINGS = (0.42, 1.02)
R_RING = 0.16
IN = 0.0254


def _load(piece, name):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", piece, "model.py")
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MB = _load("life-fitness-medicine-balls", "lfmb")
KB = _load("life-fitness-cast-iron-kettlebells", "lfkb")
SB = _load("hammer-strength-stability-ball", "hssb")
FR = _load("life-fitness-foam-roller", "lffr")
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "shelf": dict(color=(0.02, 0.02, 0.021), rough=0.6, coat=0.0, bump=(2500, 0.15)),
    "cap": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0),
}
for m in (MB, KB, SB, FR):
    LOOK.update({r: v for r, v in m.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_shelves": ((-0.9, -1.4, 1.2), (0.0, -0.05, 0.65), 35),      # the shelves loaded
}


def moved(k, fn, d):
    """Run fn() and move what it added by d."""
    before = {key: set(g.verts) for key, g in k.groups.items()}
    fn()
    for key, g in k.groups.items():
        for v in g.verts:
            if v not in before.get(key, ()):
                v.co.x += d[0]; v.co.y += d[1]; v.co.z += d[2]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sx in (1, -1):
        x = sx * XU
        k.bar("frame", (x, -0.22, TUBE / 2), (x, 0.22, TUBE / 2), TUBE, TUBE, r=0.004)                 # a foot
        for sy in (1, -1):
            k.box("cap", (x, sy * 0.225, TUBE / 2), (TUBE + 0.004, 0.012, TUBE + 0.004), soft=0.003)
        k.bar("frame", (x, 0, TUBE), (x, 0, H), TUBE, TUBE, r=0.004)                                     # an upright
        k.tube("frame", (x + sx * TUBE / 2, 0, 1.60), (x + sx * 0.13, 0, 1.60), 0.009, seg=12)          # a top hook
        k.tube("frame", (x + sx * 0.13, 0, 1.60), (x + sx * 0.13, 0, 1.64), 0.009, seg=12)
    k.bar("frame", (-XU, 0, 1.45), (XU, 0, 1.45), TUBE, TUBE, r=0.004)                                   # the top bar
    for z in SHELVES:                                   # the shelves, perforated, lipped
        k.box("shelf", (0, 0, z - 0.003), (2 * XU - TUBE, DEP, 0.006), soft=0.001)
        for sy in (1, -1):
            k.box("shelf", (0, sy * DEP / 2, z + 0.012), (2 * XU - TUBE, 0.006, 0.03), soft=0.001)
    # the ring cradles out the right upright, a 55 cm stability ball in each
    for z in RINGS:
        xr = XU + TUBE / 2 + 0.06 + R_RING
        ring = [(xr + R_RING * math.cos(t), R_RING * math.sin(t), z) for t in [2 * math.pi * i / 48 for i in range(49)]]
        k.sweep("frame", ring, k.circle(0.007, 10), soft=0.0)
        k.tube("frame", (XU + TUBE / 2 - 0.004, 0, z), (xr - R_RING + 0.003, 0, z), 0.012, seg=12)
        r = 0.275
        zc = z + math.sqrt(r * r - R_RING ** 2)
        moved(k, lambda: SB.ball(k, 0.0, 55), (xr, 0.0, zc - r))
    # the roller holder at the left foot, three 18 in rollers standing in it
    xh = -XU - TUBE / 2 - 0.13
    for zz in (0.02, 0.16):
        loop = [(xh + 0.115 * math.cos(t), 0.10 * math.sin(t), zz) for t in [2 * math.pi * i / 40 for i in range(41)]]
        k.sweep("frame", loop, k.circle(0.005, 10), soft=0.0)
    for sy in (1, -1):
        k.tube("frame", (xh + 0.115, sy * 0.03, 0.02), (xh + 0.115, sy * 0.03, 0.16), 0.006, seg=10)
    k.tube("frame", (-XU - TUBE / 2 + 0.003, 0, 0.16), (xh + 0.115, 0, 0.16), 0.008, seg=10)
    k.tube("frame", (xh - 0.115, 0, 0.0), (xh - 0.115, 0, 0.16), 0.006, seg=10)
    for i, (dx, dy) in enumerate(((-0.04, -0.035), (0.045, -0.02), (0.0, 0.05))):
        k.cyl("grey" if i != 1 else "black", (xh + dx, dy, 18 * IN / 2 + 0.004), FR.R - 0.004, 18 * IN, seg=40, soft=0.004)
    # the shelves loaded: two medicine balls up top, kettlebells below
    x = -0.18
    for lb in (6, 10):
        r = MB.diameter(lb) / 2
        moved(k, lambda lb=lb: MB.ball(k, 0.0, 0.0, lb), (x, -0.02, SHELVES[2]))
        x += 0.32
    for z, load in ((SHELVES[1], (8, 12, 16)), (SHELVES[0], (20, 24))):
        sizes = [KB.size(kg)[0] for kg in load]
        gap = (2 * XU - TUBE - 0.04 - 2 * sum(sizes)) / (len(load) + 1)
        x = -XU + TUBE / 2 + 0.02 + gap
        for kg, R in zip(load, sizes):
            _, hr, hw, hh = KB.size(kg)
            kb.bell(k, (x + R, -0.02, z), R, hr, hw, hh, "iron", "iron", dict(KB.BELLS)[kg],
                    [(f"{kg}KG", R * 0.24, 0.12), (f"{round(kg * 2.2046)}LB", R * 0.24, -0.20)], arch=hw * 0.9, face=R * 0.45)
            x += 2 * R + gap

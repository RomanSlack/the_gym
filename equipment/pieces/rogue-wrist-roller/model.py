"""Rogue Wrist Roller, rack mount (refs/: ref_01 the handheld: two black 2 in handles either side of a strap housing
with two flanges, the strap hanging, a carabiner; ref_02 / ref_04 in use with a kettlebell; ref_03 the rack mount: the
mounting panel and its shaft on the end, the detent pin; ref_05 mounted on an upright). The linked page: 15.5 in
handheld, 17.5 in rack mount, 2 in handles 6 in either side of the strap housing, a 58.5 in black nylon strap, a
carabiner, a mounting panel and detent pin for 3 x 3 in uprights, black. Fetched 2026-10-25. Built to the two gates and
README point 9. Mounted on a display section of a red Monster upright (not the piece), a 16 kg kettlebell on the
carabiner (from the LF kettlebells' builder).

DESIGN SPEC (gate 1)
1. Use. Forearm work: arms out, the handles turned hand over hand to wind the strap up and lift the load, then let
   down under control.
2. Each mass named (ref_03 / ref_05): the mounting panel on the upright's face with its detent pin, the shaft out from
   it with a collar; the roller on the shaft: two 2 in handles, the strap housing between with two flanges; the strap,
   58.5 in black nylon, down from the housing; the carabiner on its end.
3. Adjustments. The mount's height on the upright (by its hole); the load.
4. Load path. The load, the carabiner, the strap, the housing, the shaft, the panel and pin, the upright.
5. Fit range. Mounted at 1.40 m (about shoulder height for the 1.78 m user, chest for the 1.95, chin for the 1.55):
   the hands on the handles, arms out. No figure.
6. Size. The roller 0.44 m across, the strap to the floor.
Axes: metres, floor z = 0; the upright at the origin, the roller out to +x.
"""
import importlib.util
import math
import os
import kettlebell as kb

IN = 0.0254
Z = 1.40
R_H, L_H = 1 * IN, 6 * IN


def _bells():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "life-fitness-cast-iron-kettlebells", "model.py")
    spec = importlib.util.spec_from_file_location("lfkb", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KB = _bells()
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.2),
    "web": dict(color=(0.010, 0.010, 0.011), rough=0.9, coat=0.0, bump=(3000, 0.12)),
    "steel": dict(color=(0.65, 0.65, 0.67), rough=0.25, metal=1.0),
    "pin": dict(color=(0.75, 0.30, 0.02), rough=0.5, coat=0.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
}
LOOK.update({r: v for r, v in KB.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_mount": ((0.35, -0.65, 1.60), (0.12, 0.0, 1.38), 35),      # the panel, the pin, the housing
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    U = 3 * IN
    k.bar("red", (0, 0, 0), (0, 0, 2.0), U, U, r=0.004)                                           # display upright
    z = 0.20
    while z < 1.95:
        k.cyl("hole", (U / 2 + 0.0003, 0, z), 0.0125, 0.0008, axis="x", seg=14, soft=0.0)
        z += 2 * IN
    k.box("frame", (U / 2 + 0.005, 0, Z), (0.010, U + 0.02, 0.16), soft=0.002)                    # the mounting panel
    k.cyl("pin", (U / 2 + 0.014, 0, Z - 0.05), 0.012, 0.012, axis="x", seg=16, soft=0.002)        # the detent pin's ring
    x0 = U / 2 + 0.010
    k.tube("frame", (x0, 0, Z), (x0 + 0.47, 0, Z), 0.010, seg=16)                                   # the shaft
    k.cyl("frame", (x0 + 0.012, 0, Z), 0.020, 0.024, axis="x", seg=24, soft=0.002)                    # its collar
    xh = x0 + 0.03                                       # the roller
    k.tube("frame", (xh, 0, Z), (xh + L_H, 0, Z), R_H, seg=28)                                       # a handle
    xc = xh + L_H + 0.04
    for dx in (-0.032, 0.032):
        k.cyl("frame", (xc + dx, 0, Z), 0.042, 0.006, axis="x", seg=32, soft=0.0015)                 # the flanges
    k.tube("frame", (xc - 0.032, 0, Z), (xc + 0.032, 0, Z), 0.018, seg=24)                          # the housing
    k.tube("frame", (xc + 0.035, 0, Z), (xc + 0.035 + L_H, 0, Z), R_H, seg=28)                      # the other handle
    # the strap: a few turns wound on, then down to the carabiner and the bell
    zb = 0.42
    k.sweep("web", [(xc, -0.021, Z), (xc, -0.022, zb + 0.07)], k.rect(0.003, 0.045, 0.001), up=(1, 0, 0), soft=0.0)
    k.cyl("web", (xc, 0, Z), 0.024, 0.045, axis="x", seg=28, soft=0.002)                             # wound on
    biner = [(xc, -0.022 + 0.02 * math.sin(t), zb + 0.04 + 0.038 * math.cos(t)) for t in [2 * math.pi * i / 32 for i in range(33)]]
    k.sweep("steel", biner, k.circle(0.005, 10), soft=0.0)
    R, hr, hw, hh = KB.size(16)
    top = R * 2 + hh + hr                                # roughly the bell's handle top
    before = {key: set(g.verts) for key, g in k.groups.items()}
    kb.bell(k, (xc, -0.022, 0.0), R, hr, hw, hh, "iron", "iron", dict(KB.BELLS)[16],
            [("16KG", R * 0.24, 0.12), ("35LB", R * 0.24, -0.20)], arch=hw * 0.9, face=R * 0.45)
    zmax = max(v.co.z for key, g in k.groups.items() for v in g.verts if v not in before.get(key, ()))
    lift = zb + 0.006 - zmax                            # the bell hung by its handle's top on the carabiner
    for key, g in k.groups.items():
        for v in g.verts:
            if v not in before.get(key, ()):
                v.co.z += lift

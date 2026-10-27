"""Beastmaker 2000 Series hangboard (refs/: ref_01 / ref_02 / ref_03 the board face on: pale wood, the top a rounded
sloper with a pocket in the middle and "beastmaker" / "2000 series" burnt in either side; two rows of holds below,
each a long edge at the ends, slots and round pockets between, the rows split by a groove; screw holes in the slots).
The linked page (madrock.com) answered HTTP 429: the size is Beastmaker's published 580 x 150 mm, the depth an estimate
off ref_02. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Finger training: dead hangs and repeaters off the edges, slots and pockets, two hands or one.
2. Each mass named (ref_02): one block of pale wood, 580 x 150 mm, about 55 mm deep; its top a rounded sloper with a
   pocket in the middle; the upper row (an end edge each side, slots, round pockets), a groove, the lower row the same
   pattern; the lettering burnt into the top. Mounted on a plywood backing board on a wall (a display wall section,
   not part of the piece).
3. Adjustments. None: the hold changes the load.
4. Load path. The fingers on the edge, the board, its screws into the backing board, the wall.
5. Fit range. Roman's rule for bars, held here too: a 6 ft 3 in (1.905 m) user dead-hangs off the upper row legs long
   with the toes clear; so the upper row's end edges sit at 2.47 m. 1.55 / 1.78 / 1.95 m (hang_short / hang_middle /
   hang_tall) hang off them (the toes' clearance printed); the shorter step up to it on a box.
6. Size. 0.58 x 0.055 x 0.15 m.
Axes: metres, floor z = 0; the wall's face at y = 0, the board on it facing -y.
"""
import math

W, HB, D = 0.58, 0.15, 0.055
Z_EDGE = 2.47                         # the upper row's end edges
ZC = Z_EDGE - 0.025                   # the board's middle (the upper row 25 mm over it)
BACK = 0.018                          # the backing board
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
CLEAR_H = 1.905
SHOW = ()

LOOK = {
    "wood": dict(color=(0.50, 0.30, 0.12), rough=0.6, coat=0.0),
    "hold": dict(color=(0.08, 0.045, 0.015), rough=0.8, coat=0.0),                                  # the recesses' shade
    "burn": dict(color=(0.10, 0.05, 0.02), rough=0.8, coat=0.0),
    "ply": dict(color=(0.45, 0.36, 0.24), rough=0.7, coat=0.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
    "hole": dict(color=(0.02, 0.015, 0.01), rough=1.0),
}
VIEWS = {"three_quarter": (-30, 10, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-60, 30, 1.0)}
DETAILS = {
    "detail_board": ((0.0, -0.75, 2.62), (0.0, -0.05, 2.47), 40),      # the board face on, as ref_02
}
SETTINGS = ("hang_short", "hang_middle", "hang_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "front")

# a row of holds, left to right: (kind, x, width) -- 'edge' a long slot, 'pocket' round
ROW = (("edge", -0.235, 0.085), ("pocket", -0.165, 0.022), ("edge", -0.11, 0.05), ("edge", -0.05, 0.04),
       ("pocket", 0.0, 0.016), ("edge", 0.05, 0.04), ("edge", 0.11, 0.05), ("pocket", 0.165, 0.022), ("edge", 0.235, 0.085))


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if getattr(k, "display", True):                                  # the display wall (not the piece: off when it hangs on a real wall)
        k.box("wall", (0, 0.05, 1.4), (1.2, 0.10, 2.8), soft=0.0)                                      # display wall
    k.box("ply", (0, -BACK / 2, ZC), (0.76, BACK, 0.34), soft=0.002)                                # the backing board
    yf = -BACK - D                                      # the board's face
    zt, zm = ZC + HB / 2, ZC - 0.005                    # its top, the split between the tiers
    z_up, z_lo = ZC + 0.025, ZC - 0.040                 # the rows' centres
    k.box("wood", (0, -BACK - D / 2, (zm + zt) / 2), (W, D, zt - zm), soft=0.012)                   # the upper tier
    k.box("wood", (0, -BACK - D / 2 + 0.004, (ZC - HB / 2 + zm) / 2 + 0.002), (W - 0.004, D - 0.008, zm - ZC + HB / 2 + 0.004),
          soft=0.010)                                   # the lower tier, set back
    for z, yy in ((z_up, yf), (z_lo, yf + 0.008)):
        for kind, x, w in ROW:
            if kind == "pocket":
                k.cyl("hold", (x, yy, z), w / 2, 0.0016, axis="y", seg=24, soft=0.0)
            else:
                r = 0.012
                k.box("hold", (x, yy, z), (w - 2 * r, 0.0016, 2 * r), soft=0.0)                         # a slot
                for sx in (1, -1):
                    k.cyl("hold", (x + sx * (w / 2 - r), yy, z), r, 0.0016, axis="y", seg=20, soft=0.0)
                k.cyl("hole", (x, yy - 0.0008, z), 0.003, 0.0006, axis="y", seg=12, soft=0.0)        # its screw
    k.box("hold", (0, -BACK - D * 0.55, ZC + HB / 2), (0.06, 0.022, 0.0016), soft=0.0)        # the top pocket
    for text, x in (("beastmaker", -0.12), ("2000 series", 0.12)):
        k.text("burn", text, (x, -BACK - D * 0.55, ZC + HB / 2), 0.016, rx=0.0, depth=0.0004)


def _hang(Hu, z):
    import reach
    lat = math.degrees(math.asin((0.25 - 0.1105 * Hu) / (0.372 * Hu)))
    for legs in (dict(sole=-60, shank=0, thigh=0), dict(sole=-90, shank=90, thigh=0), dict(sole=-90, shank=110, thigh=30)):
        base = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), **legs)
        sh = reach.shoulder(base)
        zb = z - (sh[2] + 0.372 * Hu * math.cos(math.radians(lat)))
        clear = zb - 0.27 * 0.152 * Hu * math.sin(math.radians(-legs["sole"]))
        if clear >= 0.02:
            break
    return base, sh, zb, clear, lat


# ---- the fit check (spec 5)
def fit():
    out = {}
    _, _, _, c, _ = _hang(CLEAR_H, Z_EDGE)
    print(f"fit 6 ft 3 in: hanging legs long off the upper row, the toes {c:.2f} m clear", flush=True)
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        base, sh, zb, clear, lat = _hang(Hu, Z_EDGE)
        print(f"fit {label}: hanging off the end edges at {Z_EDGE:.2f} m, "
              f"{'legs long' if not base['shank'] else 'knees bent'}, the toes {clear:.2f} m clear", flush=True)
        out[label] = dict(base, ball=(0.0, -BACK - D - 0.02 - sh[1], zb), arm=0, forearm=0, arm_lat=lat, fore_lat=lat,
                          neck=0, trunk=0, stance=0.18)
    return out

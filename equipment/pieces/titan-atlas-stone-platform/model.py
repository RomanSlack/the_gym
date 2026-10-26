"""Titan Atlas Stone Platform on its T-3 yoke (refs/: ref_01 the T-3 yoke it hangs on: two 2 x 3 in uprights, each on a
base running front to back with a plate post at each end, the crossbar on sleeves with red pop pins, holes up the
uprights). The platform page (titan.fitness, by search 2026-10-25; the page itself rate-limited us): a 23.5 x 23 in tray
with a 1.5 in barrier on three sides, a 42 in bracket that slides over the T-3 uprights and pins at any hole, 200 lb
rated, 70 lb, black powder coat. The T-3 yoke: 72 in high, 52 x 53 in, 45 in inside, 2 x 3 in 11-gauge uprights.
Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Atlas stone loading: the stone lapped, stood up with and loaded onto the tray at about chest height; the tray
   open toward the lifter, its barrier on the other three sides keeps the stone on.
2. Each mass named: the yoke (ref_01): two bases, 2 x 3 in tube front to back on the floor, a plate post up near each
   end; an upright from each base's middle, 2 x 3 in, holes up its front. The platform: a bracket, 2 x 3 in tube
   across, a sleeve over each upright with a red T-handled pop pin; the tray on two arms out in front of it, its
   barrier on three sides, the side toward the lifter open. Black, the pins red.
3. Adjustments. The platform's height by the hole (2 in steps).
4. Load path. The stone on the tray, the arms, the bracket, the sleeves and pins, the uprights, the bases.
5. Fit range. 1.55 / 1.78 / 1.95 m (load_short / load_middle / load_tall): the tray pinned near each user's lower
   chest (0.68 H, on the nearest hole), the 100 lb stone (14 in) on it, the lifter behind it, the arms round the
   stone's sides (reach.py; the tray's height and the elbows printed).
6. Size. 1.32 x 1.35 x 1.83 m (52 x 53 x 72 in); the tray 0.60 x 0.58 m.
Axes: metres, floor z = 0; the uprights at x = +-0.60, the tray toward -y, the lifter at -y facing +y.
"""
import math

IN = 0.0254
H = 72 * IN
XU = 22.5 * IN + 1 * IN               # the uprights' centres: 45 in inside
DEP = 53 * IN
TW, TD = 2 * IN, 3 * IN               # the uprights (x across, y deep)
TRAY_W, TRAY_D, LIP = 23.5 * IN, 23 * IN, 1.5 * IN
R_STONE = 7 * IN
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "red": dict(color=(0.6, 0.02, 0.02), rough=0.4, coat=0.2),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
    "stone": dict(color=(0.009, 0.009, 0.010), rough=0.72, coat=0.0, spec=0.3, bump=(900, 0.05)),
}
VIEWS = {"three_quarter": (-35, 16, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_tray": ((-0.9, -1.4, 1.9), (0.0, -0.25, 1.2), 40),          # the tray, its barrier, the bracket and pins
}
SETTINGS = ("load_short", "load_middle", "load_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def tray_z(Hu):
    """The tray's top for a user: 0.68 H, on the nearest 2 in hole."""
    return 0.20 + round((0.68 * Hu - 0.20) / (2 * IN)) * 2 * IN


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zt = tray_z(dict(USERS)[SHOW[0] if SHOW else "middle"])
    for s in (1, -1):
        x = s * XU
        k.bar("frame", (x, -DEP / 2, TW / 2), (x, DEP / 2, TW / 2), TD, TW, r=0.004)                 # the base
        for sy in (1, -1):
            k.tube("frame", (x, sy * (DEP / 2 - 0.12), TW), (x, sy * (DEP / 2 - 0.12), 0.34), 1.0 * IN, seg=24)  # plate post
        k.bar("frame", (x, 0, TW), (x, 0, H), TW, TD, r=0.004)                                      # the upright
        for sx in (1, -1):                              # a gusset each side of its foot
            xg = x + sx * (TW / 2 + 0.003)
            k.block("frame", lambda cx, cy, cz, xg=xg: (xg + cx * 0.003, cy * (0.16 if cz < 0 else TD / 2),
                                                         TW if cz < 0 else TW + 0.22), soft=0.001)
        z = 0.20
        while z < H - 0.04:                             # its holes, 2 in apart
            k.cyl("hole", (x, -TD / 2 - 0.0003, z), 0.5 * IN, 0.0008, axis="y", seg=14, soft=0.0)
            z += 2 * IN
        # the platform's sleeve on the upright, its red pin
        zs = zt - 0.12
        k.box("frame", (x, 0, zs), (TW + 0.012, TD + 0.012, 0.16), soft=0.003)
        k.cyl("red", (x, TD / 2 + 0.018, zs), 0.016, 0.024, axis="y", seg=24, soft=0.003)
        k.box("red", (x, TD / 2 + 0.034, zs), (0.05, 0.012, 0.012), soft=0.003)
    zs = zt - 0.12
    k.bar("frame", (-XU + TW / 2 + 0.006, -TD / 2 - 0.006 - TD / 2, zs), (XU - TW / 2 - 0.006, -TD / 2 - 0.006 - TD / 2, zs),
          TD, TW, r=0.003)                              # the bracket across the front of the sleeves
    for s in (1, -1):                                   # its ends wrapped onto the sleeves' fronts
        k.box("frame", (s * XU, -TD / 2 - 0.006 - TD / 4, zs), (TW + 0.012, TD / 2, 0.08), soft=0.002)
    y1 = -TD - 0.012                                    # the tray's back edge on the bracket
    for s in (1, -1):                                   # two arms out to carry it
        xa = s * (TRAY_W / 2 - 0.05)
        k.block("frame", lambda cx, cy, cz, xa=xa: (xa + cx * 0.025, y1 - (TRAY_D if cy < 0 else 0.0),
                                                     zt - 0.006 if cz > 0 else (zt - 0.04 if cy < 0 else zs - 0.04)), soft=0.002)
    yc = y1 - TRAY_D / 2
    k.box("frame", (0, yc, zt - 0.003), (TRAY_W, TRAY_D, 0.006), soft=0.001)                         # the tray
    for s in (1, -1):                                   # its barrier, the lifter's side (-y) open
        k.box("frame", (s * (TRAY_W / 2 - 0.003), yc, zt + LIP / 2), (0.006, TRAY_D, LIP), soft=0.001)
    k.box("frame", (0, y1 - 0.003, zt + LIP / 2), (TRAY_W, 0.006, LIP), soft=0.001)
    if SHOW:                                            # the 100 lb stone on it
        k.sphere("stone", (0, yc, zt + R_STONE * 0.94), R_STONE, seg=48, soft=0.002)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    yc = -TD - 0.012 - TRAY_D / 2
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        zt = tray_z(Hu)
        zs = zt + R_STONE * 0.94                        # the stone's middle
        pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), sole=0, shank=6, thigh=-4, trunk=8, neck=0, stance=0.30)
        sh = reach.shoulder(pose)
        pose["ball"] = (0.0, yc - R_STONE - 0.06 - sh[1], 0.0)  # the chest close behind the stone
        a = reach.reach(pose, (R_STONE * 0.97, yc, zs - 0.04), elbow=110, low=3.0)
        print(f"fit {label}: the tray at {zt:.2f} m, the stone's middle at {zs:.2f} m; the arms round it, elbows "
              f"{a['elbow']:.0f} deg (miss {a['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

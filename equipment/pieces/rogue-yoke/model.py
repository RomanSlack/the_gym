"""Rogue Y-1 Yoke (refs/: ref_01 with Rogue's callouts: 72 in, 2 x 3 in tube, the adjustable crossbar, 1 in hole spacing
high and 2 in low, the 50 x 48 in footprint, loaded on its base posts; ref_02 empty: the bases, the skid feet, the four
posts, a J-cup, ROGUE up an upright; ref_03 the Y-1 beside the taller Y-2). The linked page: 72 in, 2 x 3 in 11-gauge
uprights, a 3 in OD crossbar at any height, 2 bases with 4 skid feet and a plate post each, 2 J-cups, 185 lb, 750 lb
rated. Fetched 2026-10-24 / 25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Yoke carries: the lifter steps under the crossbar, sets it on the upper back, stands it up off the floor
   (the skids clear) and walks, hands on the uprights; also a squat stand on its J-cups.
2. Each mass named (ref_01 / ref_02): two bases, a 2 x 3 in tube each running front to back on two skid feet, a plate
   post near each end; an upright from each base's middle, 2 x 3 in, a gusset either side of its foot, holes up its faces (1 in apart high, 2 in low),
   ROGUE up one; the crossbar, a 3 in round tube on a sleeve and a triangular gusset inside each upright, held by red T-handled pop pins; two
   J-cups. Black, the pins red.
3. Adjustments. The crossbar's height by the hole (1 in steps up top); the J-cups by the hole.
4. Load path. The plates on the posts, the bases, the uprights, the crossbar, the lifter's back, the legs.
5. Fit range. 1.55 / 1.78 / 1.95 m (carry_short / carry_middle / carry_tall): the crossbar pinned 4 cm under the
   standing lifter's upper back so standing up lifts the skids; the hands on the uprights at the chest (reach.py).
6. Size. 1.27 x 1.22 x 1.83 m (50 x 48 x 72 in).
Axes: metres, floor z = 0; the uprights at x = +-0.60, the lifter at the middle facing -y.
"""
import math

IN = 0.0254
H = 72 * IN
XU = 0.60                             # the uprights' centres (x)
DEP = 48 * IN
TW, TD = 2 * IN, 3 * IN               # the tube (x across, y deep)
Z_BASE = 0.065                        # the bases' centre (on the skids)
HOLE_HI = 1.20                        # 1 in spacing above, 2 in below (ref_01)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.35, coat=0.25, bump=(900, 0.05)),
    "red": dict(color=(0.6, 0.02, 0.02), rough=0.4, coat=0.2),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.45),
    "uhmw": dict(color=(0.03, 0.03, 0.032), rough=0.6),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_bar": ((-0.25, -0.75, 2.0), (-0.55, 0.0, 1.70), 40),        # the crossbar's bracket, the red pins
    "detail_base": ((-1.2, -1.0, 0.55), (-0.6, -0.3, 0.12), 40),        # a base, a skid, a post
}
SETTINGS = ("carry_short", "carry_middle", "carry_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def bar_z(Hu):
    """The crossbar's centre for a user: 4 cm under the standing back, on the nearest 1 in hole."""
    import reach
    sh = reach.shoulder(dict(H=Hu, ball=(0, 0, 0), face=(0, -1)))[2]
    z = sh                                              # the back's top 4 cm over the shoulder joints: 4 cm to lift
    return HOLE_HI + round((z - HOLE_HI) / IN) * IN if z > HOLE_HI else z


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zb = bar_z(dict(USERS)[SHOW[0] if SHOW else "middle"])
    for s in (1, -1):
        x = s * XU
        k.bar("frame", (x, -DEP / 2, Z_BASE), (x, DEP / 2, Z_BASE), TW * 1.5, TD * 0.8, r=0.004)    # the base
        for sy in (1, -1):
            y = sy * (DEP / 2 - 0.06)
            k.block("frame", lambda cx, cy, cz, y=y, sy=sy: (x + cx * 0.05, y + cy * 0.06 + (sy * 0.03 if cz < 0 and cy * sy > 0 else 0),
                                                              0.0 if cz < 0 else Z_BASE - TD * 0.4), soft=0.003)   # skid
            k.tube("frame", (x, sy * (DEP / 2 - 0.18), Z_BASE + TD * 0.4), (x, sy * (DEP / 2 - 0.18), 0.42), 1.0 * IN, seg=24)
        k.bar("frame", (x, 0, Z_BASE + TD * 0.4), (x, 0, H), TW, TD, r=0.004)                         # the upright
        zt = Z_BASE + TD * 0.4
        for sx in (1, -1):                              # the gussets either side of its foot (ref_02)
            xg = x + sx * (TW / 2 + 0.004)
            k.block("frame", lambda cx, cy, cz, xg=xg: (xg + cx * 0.004, cy * (0.14 if cz < 0 else TD / 2),
                                                         zt if cz < 0 else zt + 0.30), soft=0.001)
        z = 0.20                                        # its holes: 2 in apart low, 1 in high
        while z < H - 0.05:
            for ax, sg in (("x", 1), ("x", -1), ("y", -1)):
                c = (x + sg * (TW / 2 + 0.0003), 0, z) if ax == "x" else (x, sg * (TD / 2 + 0.0003), z)
                k.cyl("hole", c, 0.3 * IN, 0.0008, axis=ax, seg=12, soft=0.0)
            z += IN if z > HOLE_HI else 2 * IN
        # the crossbar's bracket inside the upright, its red pins
        xi = x - s * TW / 2
        k.box("frame", (xi - s * 0.025, 0, zb), (0.05, TD + 0.01, 0.07), soft=0.004)                   # the sleeve
        k.block("frame", lambda cx, cy, cz, xi=xi: (xi - s * (0.004 if cx * s < 0 else 0.0) - s * (0.0 if cz > 0 else 0.0),
                                                     cy * (TD / 2 - 0.004),
                                                     zb - 0.035 if cz > 0 else zb - 0.16), soft=0.001)   # its gusset
        k.block("frame", lambda cx, cy, cz, xi=xi: (xi - s * ((0.05 if cz > 0 else 0.004) if cx * s < 0 else 0.0),
                                                     cy * 0.004, zb - 0.035 if cz > 0 else zb - 0.16), soft=0.001)
        for dz in (0.045, -0.045):
            k.cyl("red", (x + s * (TW / 2 + 0.012), 0, zb + dz), 0.016, 0.024, axis="x", seg=24, soft=0.003)
            k.box("red", (x + s * (TW / 2 + 0.028), 0, zb + dz), (0.012, 0.05, 0.012), soft=0.003)            # its T
            k.tube("frame", (x - s * TW / 2, 0, zb + dz), (x + s * (TW / 2 + 0.002), 0, zb + dz), 0.007, seg=12)
        # a J-cup on the upright's front face
        zj = zb - 0.55
        k.box("frame", (x, -TD / 2 - 0.003, zj), (TW + 0.012, 0.006, 0.13), soft=0.001)
        k.sweep("frame", [(x, -TD / 2 - 0.006, zj - 0.04), (x, -TD / 2 - 0.06, zj - 0.04), (x, -TD / 2 - 0.07, zj)],
                k.rect(0.05, 0.006, 0.002), bend=0.01, soft=0.001)
    k.tube("frame", (-XU + TW / 2 + 0.045, 0, zb), (XU - TW / 2 - 0.045, 0, zb), 1.5 * IN, seg=40)     # the crossbar, into its sleeves
    k.text("label", "ROGUE", (-XU, -TD / 2 - 0.0004, 1.45), 0.05, depth=0.0005, spin=math.pi / 2)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        zb = bar_z(Hu)
        pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1), sole=0, shank=4, thigh=-2, trunk=4, neck=-5, stance=0.36)
        sh = reach.shoulder(pose)
        pose["ball"] = (0.0, -0.07 - sh[1], 0.0)        # standing under it, the crossbar behind the neck
        zc = 0.72 * Hu
        a = reach.reach(pose, (XU - TW / 2 - 0.02, 0.0, zc), elbow=110, low=3.0)
        print(f"fit {label}: the crossbar on its hole at {zb:.2f} m; the hands on the uprights at {zc:.2f} m, elbows "
              f"{a['elbow']:.0f} deg (miss {a['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

"""Rogue CB-1 Camber Bar (refs/: ref_01 loaded in a rack, red bumpers; ref_02 square on in J-cups, the geometry read off
it at 644 px/m from the 88 in length; ref_03 loaded, square on). The linked page: 88 in overall, 85 lb, a 1.5 in solid
formed steel shaft, fully welded, machined Olympic sleeves, no knurl (a reviewer). Fetched 2026-10-24 / 25. Built to the
two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Squats and good mornings with the load hung low: the drops put the plates 0.39 m under the shoulders, so the
   bar swings and the trunk must hold it; the hands hold the straight top shaft wide.
2. Each mass named (ref_02): the top shaft, 1.5 in solid steel, 1.60 m, its ends rounded; the two drops, welded
   under it 0.87 m apart, falling 0.39 m and splaying out a little; at each drop's foot an arm out to the collar; the
   collar; the machined sleeve (50 mm) to the end. Grey steel, unknurled.
3. Adjustments. None.
4. Load path. The plates on the sleeves, the collars, the arms, the drops' welds, the top shaft, the lifter's back.
5. Fit range. 1.55 / 1.78 / 1.95 m standing at the top of a squat, the shaft on the upper back, the hands on it 0.55 m
   out each side (squat_short / squat_middle / squat_tall): the plates' centres 0.39 m under the shaft, 1.0 / 1.2 /
   1.3 m up, clear of the thighs (they hang outside the hips).
6. Size. 2.24 m overall (88 in), the drops 0.39 m.
Axes: metres, floor z = 0, the bar along x; at rest it lies on its collars, the top shaft up.
"""

IN = 0.0254
L = 88 * IN
X_TOP = 0.80                          # the top shaft's half length
X_DROP_T, X_DROP_B = 0.435, 0.475     # the drops at the top and the foot (ref_02)
DROP = 0.39
X_COLLAR = 0.70                       # the collar's inner face
R_SH, R_SL, R_COL, T_COL = 0.75 * IN, 0.025, 0.036, 0.022
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "steel": dict(color=(0.13, 0.13, 0.14), rough=0.4, metal=0.7, coat=0.1),                 # grey steel (ref_02)
    "sleeve": dict(color=(0.16, 0.16, 0.17), rough=0.35, metal=0.8, bump=(2600, 0.05)),
    "gap": dict(color=(0.01, 0.01, 0.01), rough=0.6),
}
VIEWS = {"three_quarter": (-30, 18, 1.2), "front": (0, 4, 1.2), "side": (90, 6, 1.0), "back_three_quarter": (150, 22, 1.2)}
DETAILS = {
    "detail_drop": ((0.30, -0.65, 0.45), (0.55, 0.0, 0.22), 45),        # a drop's welds, the arm, the collar
}
SETTINGS = ("squat_short", "squat_middle", "squat_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def back(Hu):
    """The squat's top: (the pose, the shaft's (y, z))."""
    import reach
    pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1), sole=0, shank=6, thigh=-4, trunk=12, neck=-5, stance=0.36)
    sh = reach.shoulder(pose)
    return pose, (sh[1] + 0.05, sh[2] + 0.04)            # on the upper back, behind the neck (the lifter faces -y)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if SHOW:
        _, (y, zt) = back(dict(USERS)[SHOW[0]])
    else:
        y, zt = 0.0, R_COL + DROP                       # lying on its collars, the top shaft up
    zb = zt - DROP
    k.tube("steel", (-X_TOP, y, zt), (X_TOP, y, zt), R_SH, seg=32)
    for s in (1, -1):
        k.sphere("steel", (s * X_TOP, y, zt), R_SH, seg=24)                                           # rounded ends
        k.tube("steel", (s * X_DROP_T, y, zt), (s * X_DROP_B, y, zb), R_SH, seg=28)                    # the drop
        k.sphere("steel", (s * X_DROP_B, y, zb), R_SH * 1.05, seg=24)                                  # its foot's weld
        k.tube("steel", (s * X_DROP_B, y, zb), (s * X_COLLAR, y, zb), R_SH, seg=28)                    # the arm
        k.disc("steel", (s * (X_COLLAR + T_COL / 2), y, zb), R_COL, R_SH * 0.9, T_COL, axis="x", seg=48, soft=0.002)
        k.disc("gap", (s * (X_COLLAR + T_COL + 0.0003), y, zb), R_SL + 0.003, R_SL, 0.0006, axis="x", seg=40)
        k.tube("sleeve", (s * (X_COLLAR + T_COL), y, zb), (s * L / 2, y, zb), R_SL, seg=40)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        pose, (y, zt) = back(Hu)
        a = reach.reach(pose, (0.55, y, zt + 0.01), elbow=80, low=3.0)
        print(f"fit {label}: the shaft at {zt:.2f} m, the plates' centres at {zt - DROP:.2f} m; elbows "
              f"{a['elbow']:.0f} deg (miss {a['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

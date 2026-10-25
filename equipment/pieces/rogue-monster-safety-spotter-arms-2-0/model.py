"""Rogue Monster Safety Spotter Arms 2.0, a pair (refs/: ref_01 / ref_05 on a Monster rack; ref_02 the end lip and the
angled face saver; ref_03 the clasp, the numbered holes, the ROGUE gusset, the detent pin; ref_04 / ref_06 the pair
alone, the pins out). The linked page: 24 in from the upright (a 19 in flat), 3 x 3 in 11-gauge, a 3/8 in laser-cut
clasp, a 3/16 in gusset, UHMW liners and the face saver, two 1 in detent pins, 2 in hole centres with laser-cut numbers,
the lip at the end, MG black, 54 lb the pair, Monster uprights only. Fetched 2026-10-24 / 25. Built to the two gates and
README point 9. Shown on two 60 in sections of Monster uprights, 52 in apart (display only).

DESIGN SPEC (gate 1)
1. Use. Set a hole under the bar's lowest point, the arms catch a missed squat or bench press; the lifter works between
   them and dumps the bar onto them.
2. Each mass named (ref_03 / ref_06): the clasp, a 3/8 in plate C hooked round the upright (UHMW inside), a detent pin
   through its sides and the upright's hole; the arm, a 3 x 3 in tube 24 in out from the upright's face, its top lined
   with UHMW, ten 1 in holes along its sides numbered from the tip, the angled face saver over its root and the lip at
   its tip; the gusset, a 3/16 in plate tapering from the clasp's foot out under the arm, ROGUE cut through it.
3. Adjustments. The height, by the hole (2 in steps): the pin.
4. Load path. A dropped bar on the arm's UHMW, the tube, the gusset and the clasp's top bearing on the upright's face,
   the pin in shear, the upright.
5. Fit range. 1.55 / 1.78 / 1.95 m at the bottom of a parallel back squat between the arms (squat_short / squat_middle /
   squat_tall): the bar on the upper back 4 cm over the arms' tops, the hole per user printed by fit(); the default
   build at the middle user's hole. A bench (not drawn) would want the arms at the chest's height lying down.
6. Size. Each arm 0.61 m out, 0.30 m tall over the clasp and gusset.
Axes: metres, floor z = 0; the uprights at y = 0, x = +-0.66, the arms out toward +y (the lifter between them).
"""
import math

IN = 0.0254
TB = 3 * IN
H_UP = 60 * IN                        # the display sections
XU = (52 / 2) * IN                    # the uprights' centres (x)
L_ARM = 24 * IN                       # out from the upright's face
HOLE0, PITCH = 4 * IN, 2 * IN
TOP_OVER_PIN = 6 * IN                 # the arm's top over the pin's hole (ref_03: the pin low in the clasp)
CL = 0.375 * IN
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()
HOLE = None

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # MG black
    "upright": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),       # the rig's red
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "uhmw": dict(color=(0.04, 0.04, 0.042), rough=0.55, coat=0.0),
    "steel": dict(color=(0.65, 0.65, 0.66), rough=0.25, metal=1.0),
    "label": dict(color=(0.55, 0.55, 0.56), rough=0.4, coat=0.0),
    "p_green": dict(color=(0.02, 0.32, 0.05), rough=0.6, coat=0.0, spec=0.3),
}
VIEWS = {"three_quarter": (-145, 14, 1.0), "front": (180, 6, 1.0), "side": (-90, 4, 1.0), "back_three_quarter": (35, 16, 1.0)}
DETAILS = {
    "detail_clasp": ((-0.20, 0.55, 1.05), (-0.62, 0.15, 0.80), 40),     # ref_03: the clasp, the numbers, ROGUE, the pin
    "detail_tip": ((-0.30, 0.95, 1.10), (-0.66, 0.55, 0.85), 40),       # the lip, the UHMW, the face saver
}
SETTINGS = ("squat_short", "squat_middle", "squat_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def hole_z(n):
    return HOLE0 + (n - 1) * PITCH


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    uprights(k)
    n = HOLE or squat(dict(USERS)[SHOW[0] if SHOW else "middle"])[2]
    for s in (1, -1):
        arm(k, s * XU, hole_z(n))
    if SHOW:
        bar(k, squat(dict(USERS)[SHOW[0]])[1])


def uprights(k):
    bp = 0.0095
    for s in (1, -1):
        x = s * XU
        k.box("upright", (x, 0, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)
        k.bar("upright", (x, 0, bp), (x, 0, H_UP), TB, TB, r=0.004)
        k.box("upright", (x, 0, H_UP + 0.0015), (TB - 0.001, TB - 0.001, 0.003), soft=0.001)
        for ax, sg in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
            z = HOLE0
            while z < H_UP - 2 * IN:
                c = (x + sg * (TB / 2 + 0.0003), 0, z) if ax == "x" else (x, sg * (TB / 2 + 0.0003), z)
                k.cyl("hole", c, 0.5 * IN, 0.0008, axis=ax, seg=14, soft=0.0)
                z += PITCH


def arm(k, x, zp):
    """One arm on the upright at x, its pin in the hole at zp."""
    zt = zp + TOP_OVER_PIN                                  # the arm's top
    yf = TB / 2                                             # the upright's front face
    zc0, zc1 = zp - 2.2 * IN, zt                            # the clasp's height
    # the clasp: the front plate on the upright's face, the side plates round it (UHMW inside), the pin through
    k.box("frame", (x, yf + CL / 2, (zc0 + zc1) / 2), (TB + 2 * CL + 0.004, CL, zc1 - zc0), soft=0.002)
    for s in (1, -1):
        k.box("frame", (x + s * (TB / 2 + 0.002 + CL / 2), 0.0, (zc0 + zc1) / 2), (CL, TB + 0.004, zc1 - zc0), soft=0.002)
        k.box("uhmw", (x + s * (TB / 2 + 0.001), 0.0, (zc0 + zc1) / 2), (0.002, TB * 0.8, (zc1 - zc0) * 0.8), soft=0.0005)
    k.tube("steel", (x - TB / 2 - CL - 0.03, 0.0, zp), (x + TB / 2 + CL + 0.012, 0.0, zp), 0.5 * IN, seg=20)    # the pin
    k.cyl("steel", (x - TB / 2 - CL - 0.03, 0.0, zp), 0.016, 0.012, axis="x", seg=24, soft=0.002)              # its head
    k.sweep("steel", [(x - TB / 2 - CL - 0.036, 0.0, zp + 0.01), (x - TB / 2 - CL - 0.05, 0.0, zp + 0.03),
                      (x - TB / 2 - CL - 0.05, 0.0, zp + 0.06), (x - TB / 2 - CL - 0.036, 0.0, zp + 0.075),
                      (x - TB / 2 - CL - 0.036, 0.0, zp + 0.01)], k.circle(0.0025, 8), bend=0.01, soft=0.0)     # its ring
    # the arm: the 3 x 3 tube out from the clasp, its numbered holes, the UHMW on top
    y0, y1 = yf + CL, yf + CL + L_ARM - CL
    k.bar("frame", (x, y0, zt - TB / 2), (x, y1, zt - TB / 2), TB, TB, r=0.004)
    k.box("uhmw", (x, (y0 + y1) / 2 + 0.03, zt + 0.003), (TB - 0.012, y1 - y0 - 0.10, 0.006), soft=0.001)
    for i in range(10):                                     # 1 from the tip, 2 in centres
        y = y1 - 0.06 - i * PITCH
        for s in (1, -1):
            k.cyl("hole", (x + s * (TB / 2 + 0.0003), y, zt - TB / 2 + 0.006), 0.5 * IN, 0.0008, axis="x", seg=16, soft=0.0)
        k.text("label", str(i + 1), (x - TB / 2 - 0.0004, y, zt - TB + 0.012), 0.011, rz=-math.pi / 2, depth=0.0003)
    # the face saver over the arm's root (angled UHMW) and the lip at its tip
    k.block("uhmw", lambda sx, sy, sz: (x + sx * (TB / 2 - 0.004), y0 + (0.0 if sy < 0 else 0.10),
                                        zt + (0.0 if sz < 0 else (0.05 if sy < 0 else 0.008))), soft=0.002)
    k.box("frame", (x, y1 + 0.005, zt + 0.005), (TB, 0.01, TB + 0.03), soft=0.002)
    # the gusset: from the clasp's foot out under the arm, ROGUE cut through
    zg = zt - TB
    k.block("frame", lambda sx, sy, sz: (x + sx * 0.0024, y0 + (0.0 if sy < 0 else 0.36),
                                         zg if sz > 0 else (zc0 if sy < 0 else zg - 0.012)), soft=0.001)
    k.text("hole", "ROGUE", (x - 0.0028, y0 + 0.13, zg - 0.045), 0.032, rz=-math.pi / 2, depth=0.0006)


def bar(k, bz):
    """The fit's barbell (not part of the piece) at the squat's bottom, a green 10 kg bumper each side."""
    y = BAR_Y
    k.tube("steel", (-0.655, y, bz), (0.655, y, bz), 0.014, seg=24)
    for s in (1, -1):
        k.tube("steel", (s * 0.655, y, bz), (s * 0.685, y, bz), 0.026, seg=28)
        k.tube("steel", (s * 0.685, y, bz), (s * 1.10, y, bz), 0.0245, seg=28)
        k.disc("p_green", (s * 0.73, y, bz), 0.225, 0.0255, 0.04, axis="x", seg=72)


# ---- the fit check (spec 5)
BAR_Y = 0.36                          # the bar over the arms' middle


def squat(Hu):
    """The bottom of a parallel back squat: (the pose, the bar's height, the hole that puts the arms 4 cm under it)."""
    import reach
    pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), sole=0, shank=38, thigh=-85, trunk=42, neck=-20, stance=0.40)
    sh = reach.shoulder(pose)
    bar_y, bz = sh[1] - 0.05, sh[2] + 0.04                                        # on the upper back, behind the neck
    pose["ball"] = (0.0, BAR_Y - bar_y, 0.0)
    top = bz - 0.014 - 0.04
    n = max(1, int((top - TOP_OVER_PIN - HOLE0) // PITCH) + 1)
    return pose, bz, n


def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        pose, bz, n = squat(Hu)
        print(f"fit {label}: the bar at {bz:.2f} m at the squat's bottom, the arms on hole {n} (their tops "
              f"{hole_z(n) + TOP_OVER_PIN:.2f} m)", flush=True)
        if label not in SHOW:
            continue
        a = reach.reach(pose, (0.40, BAR_Y, bz + 0.015), elbow=60)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

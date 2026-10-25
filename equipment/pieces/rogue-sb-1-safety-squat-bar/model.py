"""Rogue SB-1 Safety Squat Bar (refs/: ref_01 loaded in a rack, black and red bumpers; ref_02 the handles' foam and steel
ends; ref_03 the pad's leather grain; ref_04 a camber's bend into the collar; ref_05 square on in J-cups, the geometry
read off it against the pad). The linked page is gone (404): the sizes are ours from ref_05 / ref_01 (estimates): the
main shaft 1.06 m between the bends, each camber bending 0.18 m forward and 0.09 m down to its collar, the sleeves to
2.2 m overall, the yoke pad 0.28 m wide, the handles 0.40 m forward and down from the pad's ends. Built to the two gates
and README point 9.

DESIGN SPEC (gate 1)
1. Use. Squats with the load carried high on the back and the hands free in front: the pad sits on the upper back, the
   handles come over the shoulders to the hands in front of the chest; the cambers put the plates in front of the
   shoulders' line, so the bar pitches forward and the trunk stays upright against it.
2. Each mass named (ref_05 / ref_01): the main shaft across the back; at each end the camber bend forward and down,
   the collar, the sleeve; the yoke pad wrapped round the middle of the shaft (ROGUE / MADE IN THE U.S.A. on its
   front); the two handles welded to the shaft at the pad's ends, angled forward and down, in foam sleeves (ref_02), the
   steel ends bare.
3. Adjustments. None.
4. Load path. The plates on the sleeves, the cambers, the shaft, the pad on the lifter's traps; the hands steady the
   handles (the bar's forward pitch into them).
5. Fit range. 1.55 / 1.78 / 1.95 m standing at the top of a squat (squat_short / squat_middle / squat_tall): the pad
   on the upper back, the hands on the handles' foam (reach.py: the elbows printed).
6. Size. 2.2 m overall (estimate).
Axes: metres, floor z = 0, the bar along x; the handles toward -y (the lifter faces -y); at rest it lies upside down on
its pad and collars, the handles up (the tilt solved).
"""
import math

X_BEND = 0.53                         # the main shaft's half length to the bends
CAMB = (0.18, 0.09)                   # each camber: forward (-y), down
X_COLLAR = 0.70
L = 2.20
R_SH, R_SL, R_COL, T_COL = 0.016, 0.025, 0.036, 0.022
PAD = (0.28, 0.105, 0.10)             # the yoke pad: width, depth, height
H_LEN, H_ANG = 0.40, math.radians(40) # the handles: length, below level
X_H = 0.13                            # the handles' roots (x)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "steel": dict(color=(0.02, 0.02, 0.022), rough=0.4, metal=0.5, coat=0.15),               # black (ref_01)
    "sleeve": dict(color=(0.03, 0.03, 0.032), rough=0.35, metal=0.7, coat=0.2),
    "bare": dict(color=(0.6, 0.6, 0.61), rough=0.25, metal=1.0),
    "pad": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.1, bump=(1600, 0.2)),        # leather grain (ref_03)
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.55, coat=0.0, bump=(900, 0.15)),
    "ink": dict(color=(0.88, 0.88, 0.88), rough=0.45),
    "gap": dict(color=(0.005, 0.005, 0.005), rough=0.6),
}
VIEWS = {"three_quarter": (-30, 22, 1.2), "front": (0, 6, 1.2), "side": (90, 6, 1.0), "back_three_quarter": (150, 22, 1.2)}
DETAILS = {
    "detail_yoke": ((-0.35, -0.75, 0.55), (0.0, -0.10, 0.12), 40),      # the pad, the handles
}
SETTINGS = ("squat_short", "squat_middle", "squat_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def handle_end():
    return (0.0, -H_LEN * math.cos(H_ANG), -H_LEN * math.sin(H_ANG))


def frame(phi, origin):
    """Rotate about x by phi (radians), then move to origin: the bar's local (x, y, z) to the world."""
    c, s = math.cos(phi), math.sin(phi)
    return lambda p: (p[0] + origin[0], p[1] * c - p[2] * s + origin[1], p[1] * s + p[2] * c + origin[2])


def rest():
    """The tilt and the height at which the bar lies on its pad and its collars, the handles up."""
    w, d, h = PAD
    best = None
    for i in range(0, 361):
        phi = math.radians(i)
        T = frame(phi, (0, 0, 0))
        pad_low = min(T((0, sy * d / 2, sz * h / 2))[2] for sy in (1, -1) for sz in (1, -1))
        col_low = min(T((0, -CAMB[0] + R_COL * math.sin(a), -CAMB[1] + R_COL * math.cos(a)))[2]
                      for a in [math.radians(j) for j in range(0, 360, 10)])
        tip = T(handle_end())[2]
        if tip > max(pad_low, col_low) + 0.1:              # handles up
            err = abs(pad_low - col_low)
            if best is None or err < best[0]:
                best = (err, phi, min(pad_low, col_low))
    return best[1], -best[2]


def back(Hu):
    import reach
    pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1), sole=0, shank=6, thigh=-4, trunk=10, neck=-5, stance=0.36)
    sh = reach.shoulder(pose)
    return pose, (0.0, sh[1] + 0.03, sh[2] + 0.05)       # the shaft on the upper back


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if SHOW:
        _, o = back(dict(USERS)[SHOW[0]])
        T = frame(math.radians(-8), o)                   # pitched a little forward into the hands
    else:
        phi, z = rest()
        T = frame(phi, (0.0, 0.0, z))
    fy, fz = -CAMB[0], -CAMB[1]
    k.tube("steel", T((-X_BEND, 0, 0)), T((X_BEND, 0, 0)), R_SH, seg=28)
    for s in (1, -1):
        k.sweep("steel", [T((s * (X_BEND - 0.04), 0, 0)), T((s * (X_BEND + 0.05), 0, 0)),
                          T((s * (X_BEND + 0.12), fy, fz)), T((s * X_COLLAR, fy, fz))],
                k.circle(R_SH, 20), bend=0.05, soft=0.0)                                      # the camber
        k.tube("steel", T((s * X_COLLAR, fy, fz)), T((s * (X_COLLAR + T_COL), fy, fz)), R_COL, seg=40)   # the collar
        k.tube("sleeve", T((s * (X_COLLAR + T_COL), fy, fz)), T((s * L / 2, fy, fz)), R_SL, seg=40)
        # the handle from the shaft at the pad's end, forward and down, its foam, its bare end
        e = handle_end()
        p0 = (s * X_H, 0, 0)
        pe = (s * X_H, e[1], e[2])
        pm = (s * X_H, e[1] * 0.25, e[2] * 0.25)
        pf = (s * X_H, e[1] * 0.72, e[2] * 0.72)
        k.tube("steel", T(p0), T(pe), R_SH * 0.85, seg=24)
        k.tube("foam", T(pm), T(pf), 0.024, seg=28)
        k.tube("bare", T(pf), T(pe), R_SH * 0.86, seg=24)
    # the yoke pad round the shaft's middle, its lettering on the front
    w, d, h = PAD
    k.block("pad", lambda cx, cy, cz: T((cx * w / 2, cy * d / 2, cz * h / 2)), soft=0.012)
    xf = T((0, -d / 2 - 0.0004, 0.012))
    fwd = T((0, -1, 0))
    org = T((0, 0, 0))
    tilt = math.atan2(fwd[2] - org[2], -(fwd[1] - org[1]))   # the front's tilt from vertical
    k.text("ink", "ROGUE", xf, 0.034, rx=math.pi / 2 - tilt, depth=0.0005)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        pose, o = back(Hu)
        T = frame(math.radians(-8), o)
        e = handle_end()
        g = T((X_H, e[1] * 0.68, e[2] * 0.68))          # the foam's far end, where the hands hold it
        a = reach.reach(pose, g, elbow=60, low=3.0)
        print(f"fit {label}: the pad at {o[2]:.2f} m, the hands at {g[2]:.2f} m, {o[1] - g[1]:.2f} m in front of the "
              f"shaft; elbows {a['elbow']:.0f} deg (miss {a['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

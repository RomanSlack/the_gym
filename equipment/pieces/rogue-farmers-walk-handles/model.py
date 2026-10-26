"""Rogue Farmers Walk handles, a pair (refs/: ref_01 a loaded pair, red collars; ref_02 / ref_03 a carry, the shafts front
to back beside the legs; ref_04 the grip in the hand; ref_05 one handle side on: the shaft, the raised grip on its two
posts, a flange each side where the loading starts). The linked page: 60 in long, a 1.5 in schedule 80 shaft, a 1 in
schedule 40 grip, 12 in to load at each end, Signature Texture black, 21.5 lb each, sold as a pair. Fetched 2026-10-24 /
25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Farmers carries: plates on both ends of each handle, the lifter stands between the pair, deadlifts them by the
   raised grips and walks.
2. Each mass named (ref_05): the shaft, 1.5 in schedule 80 pipe (1.9 in outside), 60 in; at its middle two flat posts
   and the 1 in grip across their tops, parallel to the shaft; a flange each side 18 in from the middle (the loading
   starts there); the sleeves to the ends. Textured black.
3. Adjustments. The load.
4. Load path. The plates on the sleeves, the shaft, the posts, the grip, the hand.
5. Fit range. 1.55 / 1.78 / 1.95 m (carry_short / carry_middle / carry_tall): standing between the pair, arms long at
   the sides, the grips in the palms (the hands' height printed); loaded with 450 mm plates the grips start 0.36 m up:
   a deadlift for every user.
6. Size. Each 1.52 m long, the grip 0.13 m over the shaft.
Axes: metres, floor z = 0; the shafts along y, side by side.
"""
import math

IN = 0.0254
L = 60 * IN
R_SH = 1.9 * IN / 2
R_GRIP = 1.315 * IN / 2
H_GRIP = 0.13                         # the grip's axis over the shaft's
POSTS = 0.17                          # the posts apart (y)
X_FL = 18 * IN                        # the flanges from the middle
R_FL = 0.034
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.65, metal=0.2, coat=0.0, bump=(2200, 0.15)),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 8, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_grip": ((0.55, -0.35, 0.35), (0.30, 0.0, 0.10), 40),        # ref_05: the grip on its posts, a flange
}
SETTINGS = ("carry_short", "carry_middle", "carry_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def handle(k, x, zc):
    """One handle at x, its shaft's axis zc."""
    k.tube("black", (x, -L / 2, zc), (x, L / 2, zc), R_SH, seg=28)
    for s in (1, -1):
        k.cyl("black", (x, s * X_FL, zc), R_FL, 0.012, axis="y", seg=32, soft=0.002)                 # a flange
        y = s * POSTS / 2
        k.box("black", (x, y, zc + H_GRIP / 2), (0.032, 0.010, H_GRIP + 0.02), soft=0.002)          # a post
    k.tube("black", (x, -POSTS / 2 - 0.03, zc + H_GRIP), (x, POSTS / 2 + 0.03, zc + H_GRIP), R_GRIP, seg=24)  # the grip


def hands(Hu):
    """The palms' (x, height) when standing, arms long at the sides."""
    import reach
    pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1))
    sh = reach.shoulder(pose)
    L_arm = 0.372 * Hu
    xh = abs(sh[0]) + 0.05
    lat = math.asin((xh - abs(sh[0])) / L_arm)
    return xh, sh[2] - L_arm * math.cos(lat), sh[1]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if SHOW:
        xh, zh, yh = hands(dict(USERS)[SHOW[0]])
        for s in (1, -1):                               # carried: the grips in the palms (the grip's top under them)
            handle(k, s * xh, zh - H_GRIP - R_GRIP * 0.5)
    else:
        for s in (1, -1):                               # on the floor on their flanges
            handle(k, s * 0.30, R_FL)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        xh, zh, yh = hands(Hu)
        pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1), sole=0, shank=0, thigh=0, trunk=0, neck=0, stance=0.26)
        sh = reach.shoulder(pose)
        pose["ball"] = (0.0, -sh[1], 0.0)               # the shoulders over the grips' middle
        a = reach.reach(pose, (xh, 0.0, zh), elbow=178)
        print(f"fit {label}: the grips at {zh:.2f} m, {2 * xh:.2f} m apart (loaded: lifted from 0.36 m)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

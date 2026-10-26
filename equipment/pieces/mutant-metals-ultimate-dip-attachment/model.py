"""Mutant Metals Ultimate Dip Attachment, 1 in pin, textured black with matte black handles (refs/: ref_01 on a Monster
upright: a cradle round the upright, a bent plate wing either side, two handles forward from the wing's ends; ref_02
from the front, the handles splayed; ref_03 stored, the handles up; ref_04 / ref_05 the cradle close, its pin). The
linked page: 21.25 x 6.75 x 24.5 in, the handles 1-3/8 in (35 mm) with 18 in usable, three hole positions (narrow 11.5-
20 in, mid 15-24, wide 19-27.5), a 1 in stainless pin for 3 x 3 Monster uprights, 550 lb. Fetched 2026-10-25. Built to
the two gates and README point 9. On a display section of a red Monster upright (not the piece).

DESIGN SPEC (gate 1)
1. Use. Dips off a rig upright: the hands on the handles, the body between them, lowered and pressed; stored with the
   handles flipped up.
2. Each mass named (ref_01 / ref_04): the cradle, plates wrapping the upright's sides and front, its pin through the
   upright; the wing, a 2 x 3 in bar across with three holes each side (the ref's slight bend left straight); the handles, 35 mm, in the holes with knobs, out
   forward 24.5 in, splayed a little (narrow at the upright, wide at the ends).
3. Adjustments. The height (the pin's hole); the handles' hole (narrow / mid / wide) and turn; stored up.
4. Load path. The hands on the handles, the wing, the cradle bearing on the upright's face, the pin.
5. Fit range. 1.55 / 1.78 / 1.95 m (dip_short / dip_middle / dip_tall): set at 1.30 m on the mid holes, each user in
   support, arms straight, knees bent, the toes clear (printed). The narrow end suits the short user, the wide the
   tall: the hands slide along the splay.
6. Size. 0.54 x 0.62 x 0.17 m.
Axes: metres, floor z = 0; the upright at the origin, the handles out toward -y.
"""
import math

IN = 0.0254
U = 3 * IN
Z = 1.30
R_H, L_H = 1.375 * IN / 2, 24.5 * IN
X0, X1 = 15 * IN / 2, 24 * IN / 2                     # the mid holes: the handles' spacing at the wing and at the ends
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.015), rough=0.6, coat=0.05, bump=(1500, 0.15)),
    "handle": dict(color=(0.010, 0.010, 0.011), rough=0.5, coat=0.0, bump=(3000, 0.1)),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.2),
    "steel": dict(color=(0.7, 0.7, 0.72), rough=0.2, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
}
VIEWS = {"three_quarter": (-35, 20, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_cradle": ((-0.45, -0.55, 1.55), (0.0, -0.05, 1.30), 35),    # the cradle, the wing, the pin
}
SETTINGS = ("dip_short", "dip_middle", "dip_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.bar("red", (0, 0, 0), (0, 0, 2.2), U, U, r=0.004)                                            # display upright
    z = 0.20
    while z < 2.15:
        k.cyl("hole", (0, -U / 2 - 0.0003, z), 0.0127, 0.0008, axis="y", seg=14, soft=0.0)
        z += 2 * IN
    t = 0.008
    for sx in (1, -1):                                  # the cradle's side plates
        k.box("frame", (sx * (U / 2 + t / 2), -0.01, Z), (t, U + 0.04, 0.17), soft=0.002)
    k.box("frame", (0, -U / 2 - t / 2 - 0.002, Z), (U + 2 * t, t, 0.17), soft=0.002)               # its front plate
    k.tube("steel", (-U / 2 - 0.03, 0, Z + 0.05), (U / 2 + 0.03, 0, Z + 0.05), 0.0125, seg=16)      # the pin
    yw = -U / 2 - t - 1.5 * IN + 0.002                  # the wing: a 2 x 3 in bar across, on the cradle's front
    k.bar("frame", (-X0 - 0.08, yw, Z), (X0 + 0.08, yw, Z), 3 * IN, 2 * IN, r=0.004)
    for sx in (1, -1):
        for j, xh in enumerate((X0 - 0.06, X0, X0 + 0.06)):          # its three holes, the mid one in use
            if j != 1:
                k.cyl("hole", (sx * xh, yw - 1.5 * IN - 0.0003, Z), 0.018, 0.0008, axis="y", seg=16, soft=0.0)
        # the handle: from the mid hole forward, splayed to the end spacing
        k.tube("handle", (sx * X0, yw, Z), (sx * X1, yw - L_H, Z), R_H, seg=28)
        k.cyl("frame", (sx * X0, yw, Z + IN + 0.008), 0.022, 0.016, seg=20, soft=0.002)                 # its knob, on top
        for f in (0.33, 0.66):                          # the knurl marks every 6 in
            xa = sx * (X0 + (X1 - X0) * f)
            ya = yw - L_H * f
            k.cyl("steel", (xa, ya, Z), R_H + 0.0004, 0.003, axis="y", seg=28, soft=0.0)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        yh = -U / 2 - 0.05 - L_H * 0.55               # the hands along the handles
        f = (yh - (-U / 2 - 0.05)) / -L_H
        xh = X0 + (X1 - X0) * f
        legs = dict(sole=-80, shank=95, thigh=-5)      # knees bent, the shins back (in support)
        base = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), trunk=8, neck=0, **legs)   # facing the upright
        sh = reach.shoulder(base)
        arm = 0.372 * Hu + 0.04 * Hu
        lat = math.degrees(math.asin(max(-1.0, min(1.0, (xh - abs(sh[0])) / arm))))
        zb = Z + arm * math.cos(math.radians(lat)) - sh[2]
        clear = zb - 0.27 * 0.152 * Hu
        base["ball"] = (0.0, yh - sh[1] - 0.03, zb)
        print(f"fit {label}: in support on the handles at {Z:.2f} m, {2 * xh:.2f} m apart, knees bent, the toes "
              f"{clear:.2f} m clear", flush=True)
        out[label] = dict(base, arm=180 - 8, forearm=180 - 8, arm_lat=lat, fore_lat=lat, stance=0.18)
    return out

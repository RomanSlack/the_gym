"""Gymleco Wooden Wall Bars with Chins Rack (refs/: ref_01 is only Gymleco's logo card, no product photo; gymleco.com
answered HTTP 429). The product by search, 2026-10-25 (gymleco.com/products/wooden-wall-bars-with-chins-rack): SKU 775W,
220 cm high, 80 cm wide, 53 cm deep, wooden, 120 kg, the chins rack movable in height. The rest is the standard Swedish
wall bar (ribbevegg): two pine stiles, oval beech rungs about 40 x 30 mm at about 15 cm, the top rung set forward;
the chins rack a black steel bracket hooked over the rungs, the pull-up bar at its front. Every size beyond the four
published is an estimate. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Wall bar work (hanging leg raises, stretches, climbing, step-ups) and chin-ups off the rack's bar.
2. Each mass named: two stiles, pine, 2.20 m x 110 x 40 mm, 0.80 m apart outside, fixed to the wall at top and bottom
   (black brackets, 0.10 m off it); 15 oval beech rungs between them, the top one set forward; the chins rack: two
   black steel arms hooked over the top rung and braced down to a lower rung, the pull-up bar across their front ends,
   0.53 m out from the wall.
3. Adjustments. The rack hooks over any rung (its height).
4. Load path. The hands on a rung or the bar, the rack's hooks and braces, the stiles, the wall brackets.
5. Fit range. 1.55 / 1.78 / 1.95 m (hang_short / hang_middle / hang_tall) hang off the rack's bar on its top setting
   (the toes' clearance printed). Roman's rule (a 6 ft 3 in user dead-hangs legs long) cannot be met by a 2.20 m wall
   bar: on its top setting the bar is at 2.24 m; the rule's answer is the rigs' bars.
6. Size. 0.80 x 0.53 x 2.20 m.
Axes: metres, floor z = 0; the wall's face at y = 0, the bars on it facing -y.
"""
import math

H, W, DEP = 2.20, 0.80, 0.53
SW, ST = 0.040, 0.110                 # a stile: across x, deep y
GAP = 0.10                            # the stiles off the wall
N = 15
Z0, PITCH = 0.15, 0.142               # the rungs
RX, RY = 0.020, 0.015                 # a rung's half sizes (40 x 30 oval)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
CLEAR_H = 1.905
SHOW = ()

LOOK = {
    "pine": dict(color=(0.55, 0.38, 0.20), rough=0.55, coat=0.15),
    "beech": dict(color=(0.58, 0.40, 0.22), rough=0.45, coat=0.2),
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (-70, 25, 1.0)}
DETAILS = {
    "detail_rack": ((-0.8, -1.3, 2.5), (0.0, -0.30, 2.10), 40),        # the chins rack on the top rung
}
SETTINGS = ("hang_short", "hang_middle", "hang_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def rung_z(i):
    return Z0 + i * PITCH


YC = -GAP - ST / 2                    # the stiles' middle (y)
Y_TOP = -GAP - ST + 0.01              # the top rung set forward
Z_BAR = rung_z(N - 1) + 0.12          # the rack's bar
Y_BAR = -DEP + 0.02


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if getattr(k, "display", True):                                  # the display wall (not the piece: off when it hangs on a real wall)
        k.box("wall", (0, 0.05, 1.4), (1.4, 0.10, 2.8), soft=0.0)                                      # display wall
    xs = W / 2 - SW / 2
    for s in (1, -1):
        k.box("pine", (s * xs, YC, H / 2), (SW, ST, H), soft=0.004)                                 # a stile
        for z in (0.30, H - 0.15):                      # its wall brackets
            k.box("frame", (s * xs, -GAP / 2, z), (SW + 0.01, GAP, 0.05), soft=0.002)
    for i in range(N):
        z = rung_z(i)
        y = Y_TOP if i == N - 1 else YC
        k.sweep("beech", [(-xs, y, z), (xs, y, z)], k.oval(2 * RY, 2 * RX, 20), up=(0, 0, 1), soft=0.0)
    # the chins rack, hooked over the top rung and braced to the fourth from the top
    zt, zb = rung_z(N - 1), rung_z(N - 4)
    for s in (1, -1):
        x = s * (xs - SW / 2 - 0.03)
        k.sweep("frame", [(x, Y_TOP + RY + 0.012, zt - 0.04), (x, Y_TOP + RY + 0.012, zt + RX + 0.012),
                          (x, Y_TOP - 0.03, zt + RX + 0.012), (x, Y_BAR, Z_BAR)], k.rect(0.012, 0.04, 0.002), bend=0.02,
                up=(1, 0, 0), soft=0.0)                 # the arm, its hook over the top rung
        k.box("frame", (x, Y_TOP, zt + RX + 0.005), (0.04, 2 * RY + 0.03, 0.012), soft=0.002)           # its hook, on the rung
        k.box("frame", (x, YC - RY - 0.004, zb), (0.04, 0.012, 2 * RX), soft=0.002)                     # its foot, on the lower
        k.sweep("frame", [(x, YC - RY - 0.006, zb + 0.02), (x, YC - RY - 0.02, zb), (x, Y_BAR + 0.06, Z_BAR - 0.03)],
                k.rect(0.012, 0.03, 0.002), bend=0.02, up=(1, 0, 0), soft=0.0)   # its brace, seated on a lower rung
    k.tube("frame", (-xs + 0.02, Y_BAR, Z_BAR), (xs - 0.02, Y_BAR, Z_BAR), 0.016, seg=24)            # the pull-up bar


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
    _, _, _, c, _ = _hang(CLEAR_H, Z_BAR)
    print(f"fit 6 ft 3 in: off the rack's bar at {Z_BAR:.2f} m the toes {c:.2f} m clear only with knees bent "
          f"(a 2.20 m wall bar)", flush=True)
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        base, sh, zb, clear, lat = _hang(Hu, Z_BAR)
        print(f"fit {label}: hanging off the rack's bar at {Z_BAR:.2f} m, "
              f"{'legs long' if not base['shank'] else 'knees bent'}, the toes {clear:.2f} m clear", flush=True)
        out[label] = dict(base, ball=(0.0, Y_BAR - sh[1], zb), arm=0, forearm=0, arm_lat=lat, fore_lat=lat,
                          neck=0, trunk=0, stance=0.18)
    return out

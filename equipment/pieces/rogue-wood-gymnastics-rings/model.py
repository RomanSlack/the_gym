"""Rogue Gymnastic Wood Rings (refs/: ref_01 a pair hung: pale Baltic birch rings on black straps with ROGUE in white;
ref_02 the ring's laminations; ref_03 the cam buckle; ref_04 a pair lying; ref_05 a strap with its buckle). The linked
page: Baltic birch, textured, 1.25 in grip (1.11 in FIG optional), 1.5 in nylon straps 16 ft with buckles and a
hook-and-loop keeper, a set of two. Fetched 2026-10-25. The ring's inside, 7.2 in, is the standard and an estimate.
Built to the two gates and README point 9. Hung from a black crossmember between two red Monster upright sections
(not the piece; the rig's colours).

DESIGN SPEC (gate 1)
1. Use. Ring work: muscle-ups, dips, rows, support holds; the straps set the height.
2. Each mass named (ref_01 / ref_05): two rings, laminated birch, a 32 mm grip round a 7.2 in inside; two straps, black
   nylon, each looped over the crossmember, through its cam buckle, down to wrap the ring's top; ROGUE in white.
3. Adjustments. The height, by the strap through the buckle.
4. Load path. The hands on the rings, the straps, the buckles, the crossmember.
5. Fit range. Hung high here (the grips 2.47 m, Roman's bar rule): a 6 ft 3 in user dead-hangs legs long, toes clear;
   1.55 / 1.78 / 1.95 m (hang_short / hang_middle / hang_tall) hang (the toes' clearance printed). Lowered by the
   buckles for dips and rows.
6. Size. Two rings 0.50 apart, each 0.24 m across.
Axes: metres, floor z = 0; the crossmember along x, the rings' planes facing -y.
"""
import math

IN = 0.0254
R_IN = 7.2 * IN / 2
R_G = 1.25 * IN / 2
RC = R_IN + R_G                      # the ring's centreline radius
XR = 0.25
Z_BAR = 2.95
Z_GRIP = 2.47                        # the ring's bottom inside (where the hands are)
ZC = Z_GRIP - R_G + RC               # the ring's centre
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
CLEAR_H = 1.905
SHOW = ()

LOOK = {
    "birch": dict(color=(0.62, 0.48, 0.30), rough=0.55, coat=0.0, bump=(1500, 0.05)),
    "strap": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, spec=0.2, bump=(3000, 0.1)),
    "buckle": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.1),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.2),
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15),
}
VIEWS = {"three_quarter": (-35, 10, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_ring": ((-0.55, -0.85, 2.75), (-0.25, 0.0, 2.55), 35),     # a ring, its strap's wrap, ROGUE
}
SETTINGS = ("hang_short", "hang_middle", "hang_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "front")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sx in (1, -1):                                  # the display: two red uprights, the black crossmember
        k.bar("red", (sx * 0.55, 0, 0.0), (sx * 0.55, 0, Z_BAR + 0.10), 3 * IN, 3 * IN, r=0.004)
    k.tube("frame", (-0.55, 0, Z_BAR), (0.55, 0, Z_BAR), 1.0 * IN, seg=28)
    for sx in (1, -1):
        x = sx * XR
        ring = [(x + RC * math.sin(t), 0.0, ZC + RC * math.cos(t)) for t in [2 * math.pi * i / 64 for i in range(65)]]
        k.sweep("birch", ring, k.circle(R_G, 20), soft=0.0)                                           # the ring
        w = 1.5 * IN
        top = ZC + RC + R_G
        bar_r = 1.0 * IN
        strap = [(x, -0.004, top + 0.002), (x, -0.006, Z_BAR - 0.12), (x, -bar_r - 0.003, Z_BAR),
                 (x, 0.0, Z_BAR + bar_r + 0.003), (x, bar_r + 0.003, Z_BAR), (x, 0.006, Z_BAR - 0.12),
                 (x, 0.004, top + 0.002)]
        k.sweep("strap", strap, k.rect(0.003, w, 0.001), bend=0.02, up=(1, 0, 0), soft=0.0)          # over the bar
        wrap = [(x + 0.0, -R_G - 0.002, top - 0.03), (x, -R_G - 0.002, top), (x, 0, top + 0.004),
                (x, R_G + 0.002, top), (x, R_G + 0.002, top - 0.03)]
        k.sweep("strap", wrap, k.rect(0.003, w, 0.001), bend=0.01, up=(1, 0, 0), soft=0.0)          # round the ring
        zb = top + 0.07                                 # the cam buckle on the front run, ROGUE above it
        k.box("buckle", (x, -0.010, zb), (w + 0.012, 0.010, 0.055), soft=0.004)
        k.text("white", "ROGUE", (x, -0.0080, zb + 0.10), 0.026, spin=math.pi / 2, depth=0.0008)


def _hang(Hu, z):
    import reach
    lat = math.degrees(math.asin((XR - 0.1105 * Hu) / (0.372 * Hu))) if XR > 0.1105 * Hu else 0.0
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
    _, _, _, c, _ = _hang(CLEAR_H, Z_GRIP)
    print(f"fit 6 ft 3 in: hanging legs long from the rings at {Z_GRIP:.2f} m, the toes {c:.2f} m clear", flush=True)
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        base, sh, zb, clear, lat = _hang(Hu, Z_GRIP)
        print(f"fit {label}: hanging from the rings, {'legs long' if not base['shank'] else 'knees bent'}, "
              f"the toes {clear:.2f} m clear", flush=True)
        out[label] = dict(base, ball=(0.0, -sh[1], zb), arm=0, forearm=0, arm_lat=lat, fore_lat=lat, neck=0, trunk=0,
                          stance=0.18)
    return out

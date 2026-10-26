"""Life Fitness ACFT Sled with Strap (refs/: ref_01 the spec sheet's photo: a black drag mat, its edges bound in webbing
with white stitching, a corner to the front; two 45 lb bumpers on it, held by a strap from the hub down the front to
a cam buckle; a D-ring at the front where the tow strap clips on; the tow strap, grey webbing, doubled, a sewn loop at
each end). The linked page gives no sizes (shop.lifefitness.com rate-limited us, its cached record has the title, the
price and the photo only): every size here is read off ref_01 against the 450 mm bumpers and marked an estimate. Built
to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. The ACFT sprint-drag-carry drag: two 45 lb plates strapped on (90 lb with the sled), the soldier takes the
   strap's loops in both hands and drags the sled backward, then turns and pulls it.
2. Each mass named (ref_01): the mat (estimate 0.56 m square, 6 mm), set corner-first, its edges bound; the
   two bumpers (450 mm, 85 mm each) flat on it, the "45" on top; the hold-down strap from the hub hole over the top
   plate and down the front to its buckle; the D-ring at the front corner; the tow strap (estimate 2.4 m doubled, 45 mm
   webbing) lying out ahead, a loop at each end.
3. Adjustments. The plates (the strap cinches any stack).
4. Load path. The hands in the loops, the strap, the D-ring, the mat, the plates' weight on the floor.
5. Fit range. The loops are hand-held, the strap's length the same for all: every user (1.55 / 1.78 / 1.95 m) drags
   it backward low, hands at the hips. No figure.
6. Size. The mat 0.56 m square, the plates 0.18 m up; the strap 1.2 m ahead.
Axes: metres, floor z = 0; the front (the D-ring, the strap) toward -y.
"""
import math

MAT, MT = 0.56, 0.006
R_PL, T_PL = 0.225, 0.085
WEB = 0.045

LOOK = {
    "mat": dict(color=(0.010, 0.010, 0.011), rough=0.9, coat=0.0, spec=0.2, bump=(2400, 0.12)),
    "bind": dict(color=(0.014, 0.014, 0.015), rough=0.75, bump=(3000, 0.1)),
    "stitch": dict(color=(0.75, 0.75, 0.76), rough=0.6),
    "bumper": dict(color=(0.016, 0.016, 0.017), rough=0.75, coat=0.0, bump=(1200, 0.08)),
    "steel": dict(color=(0.55, 0.55, 0.57), rough=0.25, metal=1.0),
    "web": dict(color=(0.008, 0.008, 0.009), rough=0.95, spec=0.15, bump=(3000, 0.1)),
    "grey": dict(color=(0.03, 0.03, 0.032), rough=0.95, spec=0.15, bump=(3000, 0.15)),
    "yellow": dict(color=(0.55, 0.45, 0.04), rough=0.6),
}
VIEWS = {"three_quarter": (-35, 25, 1.0), "front": (0, 12, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_front": ((0.25, -0.85, 0.45), (0.0, -0.25, 0.08), 35),      # the strap, the buckle, the D-ring
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    h = MAT / 2
    q = math.pi / 4                                     # the mat set corner-first: the D-ring at its front corner (ref_01)
    k.box("mat", (0, 0, MT / 2), (MAT, MAT, MT), rz=q, soft=0.001)
    for i in range(4):                                  # the bound edges, white stitching along them
        t = q + i * math.pi / 2
        c, s_ = math.cos(t), math.sin(t)
        e = h - 0.012
        k.box("bind", (e * c, e * s_, MT + 0.001), (0.024, MAT, 0.003), rz=t, soft=0.0008)
        k.box("stitch", (e * c, e * s_, MT + 0.0026), (0.002, MAT - 0.03, 0.0006), rz=t, soft=0.0)
    # the two bumpers flat on the mat
    yc = 0.0
    for i in range(2):
        z = MT + T_PL / 2 + i * T_PL
        k.disc("bumper", (0, yc, z), R_PL, 0.026, T_PL - 0.002, axis="z", seg=64, soft=0.004)
        k.disc("steel", (0, yc, z), 0.040, 0.026, T_PL, axis="z", seg=40, soft=0.001)                 # its hub
    top = MT + 2 * T_PL
    for ang in (math.radians(140), math.radians(320)):
        r = 0.15
        k.text("bumper", "45", (r * math.cos(ang), yc + r * math.sin(ang), top + 0.0008), 0.045, rx=0.0,
               rz=ang - math.pi / 2, depth=0.0016)
    k.tube("steel", (0, yc, MT), (0, yc, top + 0.01), 0.022, seg=24)                               # the post
    # the hold-down strap: from the post over the top plate and down the front to the buckle
    zt = top + 0.002
    yf = yc - R_PL - 0.003
    k.sweep("web", [(0, yc - 0.03, zt), (0, yf + 0.01, zt), (0, yf, zt - 0.02), (0, yf, MT + 0.03), (0, yf - 0.01, MT + 0.004),
                    (0, -h * math.sqrt(2) + 0.06, MT + 0.004)], k.rect(WEB, 0.003, 0.001), bend=0.01, up=(0, 0, 1), soft=0.0)
    k.box("steel", (0, yf - 0.006, MT + 0.075), (0.05, 0.010, 0.035), soft=0.002)                  # the cam buckle
    # the D-ring at the front edge
    yd = -h * math.sqrt(2) + 0.02
    ring = [(0.035 * math.cos(t), yd - 0.035 * (1 + math.sin(t)) * 0.9, MT + 0.008) for t in
            [math.pi * i / 16 - math.pi for i in range(17)]]
    k.sweep("steel", ring + [ring[0]], k.circle(0.005, 10), soft=0.0)
    # the tow strap, doubled, lying out ahead, a sewn loop at each end (ref_01)
    y0 = yd - 0.07
    for sx, L in ((-1, 1.05), (1, 1.25)):
        path = [(0, y0, 0.0045), (sx * 0.05, y0 - 0.15, 0.0025), (sx * 0.12, y0 - L * 0.5, 0.0025), (sx * 0.10, y0 - L, 0.0025)]
        k.sweep("grey", path, k.rect(WEB, 0.003, 0.001), bend=0.15, up=(0, 0, 1), soft=0.0)
        xe, ye = sx * 0.10, y0 - L                      # its loop, a flat teardrop
        loop = [(xe + 0.045 * math.sin(t), ye - 0.11 * (1 - math.cos(t)), 0.0025) for t in
                [2 * math.pi * i / 24 for i in range(25)]]
        k.sweep("grey", loop, k.rect(WEB * 0.7, 0.003, 0.001), up=(0, 0, 1), soft=0.0)
        k.box("yellow", (xe, ye + 0.03, 0.0045), (0.02, 0.04, 0.0006), soft=0.0)                    # its tag

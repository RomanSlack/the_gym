"""Woodway 4Front with the 21 in touchscreen (the variant Roman linked), black.

Built by eye from the dealer's gallery (refs/: ref_02 the true profile, ref_01 the 21 in display three-quarter, ref_03
in use, ref_04 / ref_05 the three-quarters with the other consoles), held to Woodway's spec: the 4Front 72 x 35 x 64 in
(183 x 89 x 163 cm) with a 68 x 22 in running surface; with the 21 in screen (the 4Front View) 76 x 35 x 74 in. Side-view
numbers off ref_02 at 2.6 mm/px (its 72 in overall), as (y, z): y = (410 - px) * 0.0026, z = (725 - py) * 0.0026.
DESIGN SPEC (gate 1, written 2026-10-25 for v004: the piece predates the gates)
1. Use. The user steps up onto the deck and runs or walks facing the screen; the motor drives the belt at the set
   speed and the deck lifts for elevation. Hands free; the yoke's ends for a steadying hand, the stop and the lanyard.
2. Moving parts, each mass named: the belt, rubber-topped slats on ball bearings over the front and back drums (the
   motor and the lift inside the deck); the side frames, the deck's carriers, with the foot rails to stand on beside
   the belt; the handrail arches, one each side bolted to its side frame behind the middle and sweeping up and forward
   to the yoke; the yoke: the cup holders, the control strip, the 21 in screen on its stem.
3. Adjustments. Speed and elevation (the control strip, the screen); nothing on the frame.
4. Load path. The feet on the slats, their bearings in the side frames' tracks, the feet. A hand on the yoke into the
   arches and the side frames.
5. Fit range. 1.55 / 1.78 / 1.95 m running mid-stance mid-deck, between the arches (ref_03 in use): the arm swing
   inside the arches (x 0.34 at the deck, the hands at 0.2), the yoke 1.31 m up ahead of the runner within a steadying
   reach, the screen a little below the eyes, tilted back to them (its centre 1.59 m; the middle user's eyes about
   1.96 with the deck).
6. Size. 193 x 89 x 188 cm with the 21 in screen (76 x 35 x 74 in), as above.
Axes: metres, floor z = 0; the user runs facing +y toward the console; +x is the side ref_02 shows.
Structure: the low deck (two side frames with rounded ends on feet, the WOODWAY mark; the flat foot rails each side of
the belt; the slatted rubber belt over its drums, the rounded rear wrap); a handrail arch each side landing on its side
frame behind the middle and sweeping up and forward to the handlebar yoke; the yoke with the cup holders, the control
strip (the red stop, the speed and elevation keys, the safety lanyard) and the 21 in screen on its stem.
"""
import math

LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.015), rough=0.4, metal=0.2, coat=0.15, bump=(1000, 0.04)),   # black
    "rail": dict(color=(0.012, 0.012, 0.013), rough=0.35, metal=0.3, coat=0.3),
    "belt": dict(color=(0.022, 0.022, 0.023), rough=0.8, coat=0.0, spec=0.25, bump=(3000, 0.18)),
    "tread": dict(color=(0.03, 0.03, 0.032), rough=0.75, coat=0.0, spec=0.3, bump=(2600, 0.16)),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.87), rough=0.4, coat=0.0),
    "red": dict(color=(0.7, 0.04, 0.03), rough=0.4, coat=0.0),
    "yellow": dict(color=(0.8, 0.6, 0.05), rough=0.4, coat=0.0),
    "glass": dict(color=(0.004, 0.004, 0.005), rough=0.5, coat=0.0, spec=0.25),
    "screen": dict(color=(0.2, 0.45, 0.8), rough=0.4, emit=0.6),
    "screen2": dict(color=(0.75, 0.55, 0.3), rough=0.4, emit=0.5),
    "steel": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-145, 14, 1.0), "side": (90, 3, 1.0), "front": (180, 5, 1.0), "back_three_quarter": (40, 16, 1.0)}
DETAILS = {
    "detail_console": ((-0.55, -0.35, 1.95), (0.0, 0.48, 1.45), 45),     # the screen, the control strip, cup holders
    "detail_deck": ((0.80, -1.45, 0.75), (0.0, -0.70, 0.25), 40),         # the slats, the rear wrap, a foot rail
}

S = 0.0026
YF, YR = 0.876, -0.879              # the deck's front and rear ends (ref_02: px 73, 748)
ZD = 0.30                           # the foot rails' top (ref_02: py 603)
RD = 0.15                           # the deck ends' radius
XB, XO = 0.28, 0.40                 # the belt's half width (22 in) and the side frames' outer face
ARCH = [(-0.356, ZD), (-0.32, 0.67), (-0.216, 0.915), (-0.044, 1.105), (0.164, 1.227), (0.338, 1.313)]   # ref_02
XL, XT = 0.34, 0.33                 # the arches' x at the deck and at the yoke (ref_01: about as wide at the top)
SCREEN = (0.50, 1.585, 0.50, 0.30, math.radians(16))   # the 21 in screen: y, z centre, width, height, tilt back


def spline(pts, n=10):
    """A Catmull-Rom curve through the points (any dimension), n samples per span."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(pts[-1]))
    return out


def deck_profile(top, inset=0.0):
    """The deck's side outline (y, z): flat on top at `top`, round ends of radius RD, flat underneath at the feet."""
    zc = top - RD
    pts = []
    for a in range(90, -91, -15):
        pts.append((YF - RD - inset + RD * math.cos(math.radians(a)), zc + RD * math.sin(math.radians(a))))
    for a in range(270, 89, -15):
        pts.append((YR + RD + inset + RD * math.cos(math.radians(a)), zc + RD * math.sin(math.radians(a))))
    return pts


def build(k):
    Z = (0, 0, 1)
    # ---- the deck: the side frames (round-ended slabs), the WOODWAY mark; the foot rails on top; feet
    for s in (1, -1):
        prof = deck_profile(ZD - 0.012)
        x0, x1 = (XB, XO) if s > 0 else (-XO, -XB)
        k.sweep("frame", [(x0, 0, 0), (x1, 0, 0)], [(-y, z + 0.0) for y, z in prof], up=Z, soft=0.02)
        k.box("tread", (s * (XB + XO) / 2, (YF + YR) / 2 + 0.02, ZD - 0.006), (XO - XB - 0.02, YF - YR - 2 * RD + 0.12, 0.012),
              soft=0.004)
        k.text("label", "WOODWAY", (s * (XO + 0.0012), 0.43, 0.125), 0.065, rz=s * math.pi / 2, depth=0.0006)
        for y in (0.62, -0.58):
            k.cyl("rubber", (s * (XO - 0.06), y, 0.0075), 0.03, 0.015, seg=24, soft=0.003)
    # the belt: its body round the drums (the rear wrap shows), the rubber slats across the top run (ref_01 / ref_02)
    k.sweep("belt", [(-XB, 0, 0), (XB, 0, 0)], [(-y, z) for y, z in deck_profile(ZD - 0.022, inset=0.01)], up=Z, soft=0.01)
    k.box("frame", (0.0, (YF + YR) / 2, 0.0075 + 0.0), (2 * XB, YF - YR - 2 * RD, 0.015), soft=0.002)        # the pan
    y = YR + RD + 0.02
    while y < YF - RD - 0.02:
        k.box("tread", (0.0, y, ZD - 0.017), (2 * XB - 0.01, 0.052, 0.012), soft=0.002)
        y += 0.0575
    # ---- the handrail arches: each from its side frame behind the middle, sweeping up and forward to the yoke
    n = len(ARCH)
    for s in (1, -1):
        pts = [(s * (XL + (XT - XL) * i / (n - 1)), y_, z_) for i, (y_, z_) in enumerate(ARCH)]
        k.sweep("rail", spline(pts), k.circle(0.031, 28), soft=0.0)      # one smooth sweep (ref_02)
        k.cyl("plastic", (s * XL, ARCH[0][0], ZD + 0.012), 0.04, 0.024, seg=28, soft=0.004)            # the boot
    # the handlebar yoke across between the arches' tops, curving forward at the middle; the cup holders at its ends;
    # the control strip on it with the red stop, the keys, the lanyard's clip
    yt, zt = ARCH[-1]
    yoke = [(-XT, yt, zt), (-0.16, yt + 0.06, zt + 0.02), (0.0, yt + 0.09, zt + 0.03), (0.16, yt + 0.06, zt + 0.02), (XT, yt, zt)]
    k.sweep("rail", spline(yoke, 8), k.circle(0.032, 28), soft=0.0)
    for s in (1, -1):
        k.cyl("plastic", (s * (XT + 0.03), yt + 0.03, zt - 0.02), 0.045, 0.09, seg=28, soft=0.006)
        k.cyl("frame", (s * (XT + 0.03), yt + 0.03, zt + 0.026), 0.035, 0.002, seg=24)
        k.box("plastic", (s * (XT + 0.01), yt + 0.02, zt - 0.01), (0.04, 0.04, 0.03), soft=0.004)
        k.box("rubber", (s * 0.10, yt + 0.075, zt + 0.02), (0.10, 0.03, 0.03), soft=0.008)              # HR pads
    k.box("plastic", (0.0, yt + 0.10, zt + 0.055), (0.34, 0.13, 0.05), rx=-0.35, soft=0.01)
    k.cyl("red", (0.03, yt + 0.095, zt + 0.087), 0.016, 0.01, seg=24, soft=0.002)
    for i in range(4):
        k.box("frame", (-0.09 + i * 0.025, yt + 0.10, zt + 0.083), (0.018, 0.018, 0.006), rx=-0.35, soft=0.002)
    k.box("yellow", (0.075, yt + 0.09, zt + 0.08), (0.014, 0.008, 0.014), soft=0.001)
    # ---- the 21 in screen on its stem from the yoke, tilted back to the runner
    cy, cz, w, h, tilt = SCREEN
    k.bar("frame", (0.0, yt + 0.12, zt + 0.07), (0.0, cy + 0.02, cz - h / 2 + 0.03), 0.06, 0.05, up=(0, 1, 0))
    k.box("frame", (0.0, cy + 0.02 * math.cos(tilt), cz - 0.02 * math.sin(tilt)), (w + 0.03, 0.04, h + 0.03), rx=-tilt,
          soft=0.01)
    nrm = (0.0, -math.cos(tilt), math.sin(tilt)); up = (0.0, math.sin(tilt), math.cos(tilt))
    def on(u, v, off):
        return (u, cy + nrm[1] * off + up[1] * v, cz + nrm[2] * off + up[2] * v)
    k.box("glass", on(0.0, 0.0, 0.001), (w, 0.002, h), rx=-tilt, soft=0.0)
    for i, (u, v, ww, hh, m) in enumerate(((-0.15, 0.04, 0.14, 0.09, "screen2"), (0.0, 0.05, 0.12, 0.12, "screen"),
                                           (0.15, 0.04, 0.14, 0.09, "screen2"), (-0.08, -0.08, 0.12, 0.05, "screen"),
                                           (0.08, -0.08, 0.12, 0.05, "screen2"))):
        k.box(m, on(u, v, 0.0025), (ww, 0.001, hh), rx=-tilt, soft=0.0)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Running on the belt's middle, mid-stance, upright with the slight forward lean, the arms bent; a short, a middle
    and a tall user."""
    out = {}
    for label, H in (("short", 1.55), ("middle", 1.78), ("tall", 1.95)):
        out[label] = dict(H=H, ball=(0.0, -0.15, ZD - 0.005), face=(0, 1), sole=0, shank=10, thigh=-6, trunk=8, neck=4,
                          arm=195, forearm=100, arm_out=8)
    return out

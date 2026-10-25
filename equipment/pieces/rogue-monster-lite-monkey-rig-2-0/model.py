"""Rogue Monster Lite Monkey Rig 2.0 (refs/: ref_01 the rig from the front left with three loaded bars, ref_02 the same
with Rogue's callouts: 24 ft 3 in long, 6 ft 8 in deep, 108 in uprights, 144 in uprights at the peak, 24 monkey bars,
black zinc hardware). Fetched 2026-10-24 off the linked page. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. A long rig to train under and on: three squat / press stations along the front (the bars on J-cups in front of
   the front row, ref_01), pull-ups on the long bars along both rows, and the monkey bars overhead: a ladder across
   the rig's depth that runs level over the ends, climbs to the ridge, runs level over it and falls again, travelled
   hand over hand.
2. Each mass named (ref_01 / ref_02): twelve 3 x 3 in uprights in two rows of six, 108 in tall but the ridge pair at
   144 in; along the length five bays: a 43 in squat bay at each end and at the ridge, a 72 in bay climbing to the
   ridge and one falling from it (3 x 46 + 2 x 75 + 3 = 291 in: Rogue's 24 ft 3 in); 72 in deep; the top rails
   along each row, square tubes with holes, level over the squat bays and sloped over the climbing ones, and a cross
   rail over every pair; the 24 monkey bars across the depth between the top rails; the long pull-up bars along both
   rows on triangular brackets (ref_01's ROGUE gussets); the ROGUE plates up the front uprights; Monster Lite J-cups
   on the squat bays' front uprights; base plates anchored. Roman's colour (2026-10-25, on the Monster Rig): the
   uprights red, the rails, bars, brackets and J-cups black (ref_01 is all black).
3. Adjustments. The J-cups by the hole (2 in steps); the pull-up bars by the hole.
4. Load path. The bar on the J-cups, the pins in the holes, the uprights, the base plates and anchors. A swing on the
   monkey bars into the top rails, the uprights; the top rails and the cross rails tie the twelve uprights.
5. Fit range. 1.55 / 1.78 / 1.95 m and Roman's rule: a 6 ft 3 in (1.905 m) user dead-hangs legs long with the feet
   clear. The pull-up bars at 2.47 m (ref_01 has them at about 2.08: raised for the rule); the monkey bars at 2.70 m
   over the ends and 3.61 over the ridge (reached by a jump or a box, then travelled). J-cups at the lifter's
   mid-chest, holes per user (fit() prints them); hang_short / hang_middle / hang_tall hang each user from the front
   pull-up bar of the middle squat bay.
6. Size. 7.39 x 2.10 x 3.66 m (291 x 78 in between the uprights' outer faces, the ridge uprights 144 in): the ceiling
   where it stands must clear 3.66 m.
Axes: metres, floor z = 0; the length along x, the front row (the J-cups) at -y.
"""
import math

import rack

IN = 0.0254
TB = 3 * IN
BAYS = (43, 72, 43, 72, 43)                          # between the uprights' faces (in)
_xs = [0.0]
for b in BAYS:
    _xs.append(_xs[-1] + (b + 3) * IN)
XS = tuple(x - _xs[-1] / 2 for x in _xs)             # the six pairs along x, centred
HS = tuple(h * IN for h in (108, 108, 144, 144, 108, 108))
DEP = 72 * IN + TB
YS = (-DEP / 2, DEP / 2)
SQUAT = (0, 2, 4)                                    # the squat bays (index of their first pair)
Z_PU = 2.47                                          # the pull-up bars (Roman's 6 ft 3 in rule; ref_01 about 2.08)
R_PU = 1.0 * IN                                      # 2 in pull-up bars
R_MB = 0.625 * IN                                    # 1.25 in monkey bars
N_MB = (4, 6, 4, 6, 4)                               # the monkey bars per bay: 24
HOLE0, PITCH = 4 * IN, 2 * IN
S = dict(TB=TB, hole=(0.5 * IN, PITCH))
PL = 0.0048
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
CLEAR_H = 75 * IN
SHOW = ()

LOOK = {
    "frame": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),        # Rogue red (Roman)
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.03, 0.03, 0.035), rough=0.3, metal=1.0, coat=0.0),                  # black zinc (ref_02)
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
    "uhmw": dict(color=(0.03, 0.03, 0.032), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0),
         "ref_view": (-42, 6, 1.0)}                   # ref_01: from the front left, about head height
DETAILS = {
    "detail_ridge": ((-0.6, -2.4, 3.2), (0.0, 0.0, 3.2), 45),            # the ridge, the slopes, the monkey bars
    "detail_jcup": ((-3.2, -1.6, 1.6), (XS[0], YS[0], 1.35), 40),         # a squat bay's J-cup, the pull-up bracket
}
SETTINGS = ("hang_short", "hang_middle", "hang_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def hole_z(n):
    return HOLE0 + (n - 1) * PITCH


def jcup_hole(Hu):
    return max(1, round((0.72 * Hu + 1.6 * IN - HOLE0) / PITCH) + 1)


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def rail_z(i):
    """The top rails' centre at pair i."""
    return HS[i] - TB / 2


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    uprights(k)
    top(k)
    pullups(k)
    jcups(k)


def uprights(k):
    bp = 0.0095
    for i, x in enumerate(XS):
        for y in YS:
            k.box("frame", (x, y, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)
            for dx in (-2.4 * IN, 2.4 * IN):
                k.bolt((x + dx, y + (2.4 * IN if dx > 0 else -2.4 * IN), bp), "+z", size=0.016)
            k.bar("frame", (x, y, bp), (x, y, HS[i] - TB - 0.002), TB, TB, r=0.004)
            for face in ("+x", "-x", "+y", "-y"):
                rack.holes(k, x, y, HOLE0, HS[i] - TB - 4 * IN, face, S, numbers=(face == "-y" and y < 0))
    for i in (0, 1, 2, 3, 4, 5):                        # the ROGUE plates up the front uprights (ref_01)
        x, y = XS[i], YS[0]
        k.box("black", (x, y - TB / 2 - 0.0015, 1.78), (TB - 0.01, 0.003, 0.40), soft=0.001)
        k.text("label", "ROGUE", (x, y - TB / 2 - 0.0033, 1.78), 0.048, depth=0.0006, spin=math.pi / 2)


def top(k):
    """The top rails along each row (level or sloped, on the uprights' tops), the cross rail over every pair, the
    monkey bars across the depth."""
    for y in YS:
        for i in range(6):                              # a cap block over each upright, the rails meet on it
            k.box("black", (XS[i], y, rail_z(i)), (TB, TB, TB), soft=0.003)
        for i in range(5):
            p0 = (XS[i] + TB / 2, y, rail_z(i))
            p1 = (XS[i + 1] - TB / 2, y, rail_z(i + 1))
            k.bar("black", p0, p1, TB, TB, up=(0, 1, 0), r=0.004)
            for t in (0.25, 0.5, 0.75):                 # holes along its side faces
                for s in (1, -1):
                    c = (p0[0] + (p1[0] - p0[0]) * t, y + s * (TB / 2 + 0.0003), p0[2] + (p1[2] - p0[2]) * t)
                    k.cyl("hole", c, 0.5 * IN, 0.0008, axis="y", seg=14, soft=0.0)
    for i in range(6):                                  # the cross rails
        k.bar("black", (XS[i], YS[0] + TB / 2, rail_z(i)), (XS[i], YS[1] - TB / 2, rail_z(i)), TB, TB, r=0.004)
    for i, n in enumerate(N_MB):                        # the monkey bars, evenly along each bay's rails
        x0, x1 = XS[i] + TB / 2, XS[i + 1] - TB / 2
        for j in range(n):
            t = (j + 0.5) / n
            x = x0 + (x1 - x0) * t
            z = rail_z(i) + (rail_z(i + 1) - rail_z(i)) * t
            k.tube("black", (x, YS[0] + TB / 2, z), (x, YS[1] - TB / 2, z), R_MB, seg=20)


def pullups(k):
    """A pull-up bar in every bay along both rows, face to face between the uprights, each end on a triangular gusset
    bolted to the upright's face under it (ref_01's ROGUE gussets)."""
    G = 0.18                                            # the gussets' legs
    for y in YS:
        for i in range(5):
            xa, xb = XS[i] + TB / 2, XS[i + 1] - TB / 2
            for xf, sg in ((xa, 1), (xb, -1)):
                zt = Z_PU - R_PU                        # the gusset's top edge under the bar

                def corner(sx, sy, sz, xf=xf, sg=sg, zt=zt):
                    out = sx * sg > 0
                    x = xf + (sg * G if out and sz > 0 else 0.0)
                    z = zt if sz > 0 else zt - G
                    return (x, y + sy * PL / 2, z)
                k.block("black", corner, soft=0.0008)
                k.box("black", (xf + sg * PL / 2, y, zt - G / 2), (PL, TB, G + 0.02), soft=0.001)     # its plate
                for dz in (-G * 0.75, -G * 0.25):
                    rack.through(k, xf - sg * TB, y, zt + dz, "-x" if sg > 0 else "+x", TB + PL, size=0.019)
            k.tube("black", (xa + PL, y, Z_PU), (xb - PL, y, Z_PU), R_PU, seg=28)


def jcups(k):
    """Monster Lite J-cups on the squat bays' front uprights, on their front faces, the hooks out to the lifter."""
    zj = hole_z(jcup_hole(1.78))
    y = YS[0]
    yf = y - TB / 2
    for b in SQUAT:
        for x in (XS[b], XS[b + 1]):
            k.box("black", (x, yf - PL / 2, zj), (TB + 2 * PL, PL, 6 * IN), soft=0.001)
            for sx in (1, -1):
                k.box("black", (x + sx * (TB / 2 + PL / 2), y, zj), (PL, TB + PL, 6 * IN), soft=0.001)
            hy = yf - PL
            prof = k.rect(2.5 * IN, 0.25 * IN, 0.002)
            k.sweep("black", [(x, hy, zj - 1.6 * IN), (x, hy - 2.2 * IN, zj - 1.6 * IN), (x, hy - 2.6 * IN, zj - 0.2 * IN)],
                    prof, bend=0.012, soft=0.001)
            k.box("uhmw", (x, hy - 1.1 * IN, zj - 1.6 * IN + 0.25 * IN / 2 + 0.002), (2.4 * IN, 2.0 * IN, 0.004), soft=0.001)


# ---- the fit check (spec 5)
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


def fit():
    out = {}
    _, _, _, c, _ = _hang(CLEAR_H, Z_PU)
    print(f"fit 6 ft 3 in: hanging legs long from a pull-up bar, the toes {c:.2f} m clear", flush=True)
    for label, Hu in USERS:
        print(f"fit {label}: the J-cups on hole {jcup_hole(Hu)} (the seat {hole_z(jcup_hole(Hu)) - 1.6 * IN:.2f} m)",
              flush=True)
        if label not in SHOW:
            continue
        base, sh, zb, clear, lat = _hang(Hu, Z_PU)
        print(f"fit {label}: hanging from the pull-up bar at {Z_PU:.2f} m, "
              f"{'legs long' if not base['shank'] else 'knees bent'}, the toes {clear:.2f} m clear", flush=True)
        out[label] = dict(base, ball=((XS[2] + XS[3]) / 2, YS[0] - sh[1], zb), arm=0, forearm=0, arm_lat=lat,
                          fore_lat=lat, neck=0, trunk=0, stance=0.18)
    return out

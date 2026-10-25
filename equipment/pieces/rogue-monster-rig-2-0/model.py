"""Rogue Monster Rig 2.0, black, as the linked page's configurator builds it (refs/: ref_01 the configured rig, the one
the listed price buys; ref_02-ref_06 Rogue's red and black two-cell rigs, the same uprights, crossmembers, hardware and
J-cups close up). Fetched 2026-10-24 off the linked page. Claude's read of ref_01. Built to the two gates and README
point 9.

DESIGN SPEC (gate 1)
1. Use. A bolted-down frame to train in and on: pull-ups and hangs on the double crossmembers along the top, a squat /
   press station on the J-cups of the end pair (the bar across the rig's depth, the lifter outside the end facing in,
   ref_01), and the holes for every Monster attachment (spotter arms, landmine, band pegs, dip bars).
2. Each mass named (ref_01): six 3 x 3 in 11-gauge uprights, 108 in tall (Rogue's tall option; ref_01's are 90 in:
   Roman, 2026-10-25, "make it so even a 6ft 3 persons feet dont touch"), in two rows of three: two bays along the
   front, unequal (ref_01: the far bay reads longer than the near one: a square 49 x 49 in squat cell at the J-cup
   end, then a 72 in pull-up bay) and one bay deep (49 in); 1 in holes on a 2 in pitch up every face, numbered up the faces
   the J-cups ride; a 7 in base plate under each, anchored to the floor (the rig stands by its anchors and its top
   frame, no feet); the top frame: a double crossmember (two 2 in pull-up bars one above the other, a rung between
   them near the middle) on every side between neighbouring uprights, seven in all, each bar on an end plate bolted
   through its upright with two 1 in bolts; the ROGUE plate up the front corner upright's face (ref_01); a pair of
   Monster J-cups on the end pair.
3. Adjustments. The J-cups by the hole (2 in steps); every attachment by the hole.
4. Load path. The bar on the J-cups, their sleeves round the uprights, the pins through the holes, the uprights, the
   base plates, the anchors. A hang on a crossmember: its end plates, the bolts, the uprights; the top frame ties the
   six uprights against racking.
5. Fit range. 1.55 / 1.78 / 1.95 m, and a 1.905 m (6 ft 3 in) user who must hang with the legs long and the feet
   clear. Pull-ups: each user hangs from a lower bar (2.47 m; the upper bar, 2.70, is in the same plane, over it: for
   muscle-ups and the attachments), arms long, a grip a little wider than the shoulders, legs long; the short users
   jump (or step off a box) to reach it (hang_short / hang_middle / hang_tall), in the pull-up bay. The J-cups: the seat at the lifter's mid-chest (0.72 H):
   holes 21 / 24 / 27 (fit() prints them); the default build has the middle user's.
6. Size. Ours 3.31 x 1.40 x 2.74 m (a 49 in and a 72 in bay and a 49 in depth between the uprights' faces, 108 in
   uprights): check the ceiling where it stands (2.74 m, and a muscle-up over the 2.70 m bar needs about 0.9 m more). The bays read off ref_01's perspective: the configurator's exact lengths are not given.
Axes: metres, floor z = 0; the long side along x, the front row at -y (ref_01's near side), the J-cup end at -x.
"""
import math

import rack

IN = 0.0254
TB = 3 * IN
H = 108 * IN                        # Roman, 2026-10-25: a 6 ft 3 in user hangs with the feet clear (ref_01 has 90 in)
BAYS = (49 * IN + TB, 72 * IN + TB)  # upright centres along x: the square squat cell at the J-cup end, the pull-up bay
DEP = 49 * IN + TB                  # and across y (49 in)
_L = sum(BAYS)
XS = (-_L / 2, -_L / 2 + BAYS[0], _L / 2)
YS = (-DEP / 2, DEP / 2)
Z_BARS = (H - 0.045, H - 0.27)      # the double crossmembers' bars on the top holes, 9 in apart (ref_01 sets them a
                                    # little lower: here the lower bar clears a 6 ft 3 in hang)
R_BAR = 1.0 * IN                    # 2 in pull-up bars
HOLE0, PITCH = 4 * IN, 2 * IN       # the first hole and the pitch (hole 1 at 4 in)
S = dict(TB=TB, hole=(0.5 * IN, PITCH))
PL = 0.0048
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
CLEAR_H = 75 * IN                   # the user who must hang legs long, feet off the floor (6 ft 3 in)
SHOW = ()
JHOLE = None                        # the J-cups' hole; None: the middle user's

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # black powder coat
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
    "uhmw": dict(color=(0.03, 0.03, 0.032), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0),
         "ref_view": (-62, 4, 1.0)}                   # ref_01: from the J-cup end, the front row receding
DETAILS = {
    "detail_top": ((-2.6, -1.6, 2.65), (-1.9, -0.66, 2.10), 40),        # a corner: the double crossmembers, their bolts
    "detail_jcup": ((-2.6, -1.3, 1.55), (-1.9, -0.66, 1.30), 40),       # a J-cup, the numbered holes
}
SETTINGS = ("hang_short", "hang_middle", "hang_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def hole_z(n):
    return HOLE0 + (n - 1) * PITCH


def jcup_hole(Hu):
    """The hole whose J-cup seat is nearest the lifter's mid-chest (0.72 H): the seat 1.6 in under the hole's centre."""
    return max(1, round((0.72 * Hu + 1.6 * IN - HOLE0) / PITCH) + 1)


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    uprights(k)
    top(k)
    jcups(k)


def uprights(k):
    bp = 0.0095
    for x in XS:
        for y in YS:
            k.box("frame", (x, y, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)                       # the base plate
            for dx in (-2.4 * IN, 2.4 * IN):                                                        # its anchors
                k.bolt((x + dx, y + (2.4 * IN if dx > 0 else -2.4 * IN), bp), "+z", size=0.016)
            k.bar("frame", (x, y, bp), (x, y, H - 0.003), TB, TB, r=0.004)
            k.box("plastic", (x, y, H - 0.0015), (TB - 0.001, TB - 0.001, 0.003), soft=0.001)
            for face in ("+x", "-x", "+y", "-y"):
                rack.holes(k, x, y, HOLE0, H - 6 * IN, face, S, numbers=(face == "-x" and x == XS[0]))
    # the ROGUE plate up the front corner's end face, over the J-cup (ref_01)
    x, y = XS[0], YS[0]
    k.box("frame", (x - TB / 2 - 0.0015, y, H - 0.42), (0.003, TB - 0.01, 0.46), soft=0.001)
    k.text("label", "ROGUE", (x - TB / 2 - 0.0033, y, H - 0.42), 0.052, rz=-math.pi / 2, depth=0.0006, spin=math.pi / 2)


def top(k):
    """A double crossmember on every side between neighbouring uprights: two bars on end plates, a rung between."""
    runs = []
    for y in YS:
        for x0, x1 in zip(XS, XS[1:]):
            runs.append(((x0, y), (x1, y)))
    for x in XS:
        runs.append(((x, YS[0]), (x, YS[1])))
    for i, ((x0, y0), (x1, y1)) in enumerate(runs):
        along = "x" if y0 == y1 else "y"
        d = (1, 0) if along == "x" else (0, 1)
        a = (x0 + d[0] * TB / 2, y0 + d[1] * TB / 2)          # the faces the plates sit on
        b = (x1 - d[0] * TB / 2, y1 - d[1] * TB / 2)
        for z in Z_BARS:
            for (px, py), sg in ((a, 1), (b, -1)):
                c = (px + d[0] * sg * PL / 2, py + d[1] * sg * PL / 2, z)
                size = (PL, TB, 4 * IN) if along == "x" else (TB, PL, 4 * IN)
                k.box("frame", c, size, soft=0.001)                                   # the end plate
                for off in (-0.9 * IN, 0.9 * IN):                                      # its two bolts, side by side
                    bx = (px + d[0] * sg * PL, py + d[1] * sg * PL)
                    pos = (bx[0] + d[1] * off, bx[1] + d[0] * off, z)
                    # the head on the upright's far face (axis: its outward normal), through it and the plate
                    rack.through(k, pos[0] - d[0] * sg * (PL + TB), pos[1] - d[1] * sg * (PL + TB), z,
                                 ("-x" if sg > 0 else "+x") if along == "x" else ("-y" if sg > 0 else "+y"),
                                 TB + PL, size=0.019)
            k.tube("frame", (a[0] + d[0] * PL, a[1] + d[1] * PL, z), (b[0] - d[0] * PL, b[1] - d[1] * PL, z), R_BAR, seg=28)
        t = 0.42 if i % 2 == 0 else 0.55                       # the rung, near the middle (ref_01)
        rx, ry = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        k.tube("frame", (rx, ry, Z_BARS[1] + R_BAR * 0.6), (rx, ry, Z_BARS[0] - R_BAR * 0.6), 0.6 * IN, seg=20)


def jcups(k):
    """A Monster J-cup on each upright of the end pair, on its outer (-x) face: the sleeve round the upright, the pin
    in its hole, the hook out toward the lifter, a UHMW liner."""
    n = JHOLE or jcup_hole(1.78)
    zj = hole_z(n)
    x = XS[0]
    xf = x - TB / 2
    for y in YS:
        k.box("frame", (xf - PL / 2, y, zj), (PL, TB + 2 * PL, 6 * IN), soft=0.001)                  # the front plate
        for sy in (1, -1):
            k.box("frame", (x, y + sy * (TB / 2 + PL / 2), zj), (TB + PL, PL, 6 * IN), soft=0.001)  # the wings
        hx = xf - PL
        prof = k.rect(0.25 * IN, 2.5 * IN, 0.002)
        k.sweep("frame", [(hx, y, zj - 1.6 * IN), (hx - 2.2 * IN, y, zj - 1.6 * IN), (hx - 2.6 * IN, y, zj - 0.2 * IN)],
                prof, bend=0.012, soft=0.001)
        k.box("uhmw", (hx - 1.1 * IN, y, zj - 1.6 * IN + 0.25 * IN / 2 + 0.002), (2.0 * IN, 2.4 * IN, 0.004), soft=0.001)


# ---- the fit check (spec 5)
def fit():
    """Each user hangs in the pull-up bay from a lower bar (the upper one is in the same plane, so a hang from it would
    put the lower bar through the arms): the legs long if the toes clear the floor by 2 cm, else the knees bent, the
    shins back level, else tucked (the knees up a little). The grip 0.25 m each side of the middle, the arms long."""
    import reach
    out = {}
    for label, Hu in USERS + (("6ft3", CLEAR_H),):
        if label == "6ft3":
            import reach as _r
            legs = dict(sole=-60, shank=0, thigh=0)
            lat = math.degrees(math.asin((0.25 - 0.1105 * Hu) / (0.372 * Hu)))
            sh = _r.shoulder(dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), **legs))
            toes = min(Z_BARS) - (sh[2] + 0.372 * Hu * math.cos(math.radians(lat))) - 0.27 * 0.152 * Hu * math.sin(math.radians(60))
            print(f"fit 6 ft 3 in: hanging legs long from the lower bar, the toes {toes:.2f} m clear of the floor", flush=True)
            continue
        print(f"fit {label}: the J-cups on hole {jcup_hole(Hu)} (the seat {hole_z(jcup_hole(Hu)) - 1.6 * IN:.2f} m)",
              flush=True)
        if label not in SHOW:
            continue
        lat = math.degrees(math.asin((0.25 - 0.1105 * Hu) / (0.372 * Hu)))
        Lf = 0.152 * Hu
        z = min(Z_BARS)
        for legs in (dict(sole=-60, shank=0, thigh=0), dict(sole=-90, shank=90, thigh=0),
                     dict(sole=-90, shank=110, thigh=30)):           # long, the shins back, a tuck
            base = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), **legs)
            sh = reach.shoulder(base)
            zb = z - (sh[2] + 0.372 * Hu * math.cos(math.radians(lat)))          # the ball's height when hanging
            clear = zb - 0.27 * Lf * math.sin(math.radians(-legs["sole"]))      # the toes
            if clear >= 0.02:
                break
        print(f"fit {label}: hanging from the lower bar at {z:.2f} m, the "
              f"{['legs long', 'knees bent', 'knees tucked'][(legs['shank'] > 0) + (legs['thigh'] > 0)]}, the toes {clear:.2f} m clear of the floor", flush=True)
        out[label] = dict(base, ball=((XS[1] + XS[2]) / 2, YS[0] - sh[1], zb), arm=0, forearm=0, arm_lat=lat, fore_lat=lat, neck=0,
                          trunk=0, stance=0.18)
    return out

"""Life Fitness Resistance Tubes (refs/: ref_01-05 the five: Extra Light yellow, Light green, Medium red, Heavy blue,
Extra Heavy black: a latex tube inside a grey braided safety sleeve, at each end a handle: a webbing strap in the
strength's colour, printed with LifeFitness and the strength, round a grey grip with a black rubber middle and dark end caps). The shop
page refuses requests (HTTP 429): the sizes are estimates (the tube 1.2 m, 24 mm in its sleeve; the grips 120 mm).
Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Rows, presses, curls, rotations: the tube anchored (under a foot, in a door, round a post), a handle in each
   hand.
2. Each mass named (ref_03): the tube in its braided sleeve; two handles, each a webbing strap looped from the tube's
   end round a grip (grey, a black rubber middle, end caps); the print on the straps.
3. Adjustments. The tube (the strength): five, by colour.
4. Load path. The hands on the grips, the straps, the tube, the anchor.
5. Fit range. 1.2 m under both feet: the handles reach the hips of every user (1.55 / 1.78 / 1.95 m) for curls. No
   figure.
6. Size. Five lying, each a loop about 0.55 x 0.25 m with its handles together in front.
Axes: metres, floor z = 0.
"""
import math

SET = (("yellow", "Extra Light"), ("green", "Light"), ("red", "Medium"), ("blue", "Heavy"), ("black", "Extra Heavy"))
R_T, R_G, L_G = 0.012, 0.016, 0.12

LOOK = {
    "sleeve": dict(color=(0.10, 0.10, 0.105), rough=0.9, coat=0.0, spec=0.2, bump=(2500, 0.5)),
    "grip": dict(color=(0.16, 0.16, 0.165), rough=0.85, coat=0.0, bump=(3000, 0.2)),
    "capr": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
    "yellow": dict(color=(0.75, 0.50, 0.01), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "green": dict(color=(0.03, 0.40, 0.04), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "red": dict(color=(0.50, 0.015, 0.02), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "blue": dict(color=(0.02, 0.18, 0.55), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.7, coat=0.0, bump=(3000, 0.1)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 35, 1.0), "front": (0, 25, 1.0), "side": (90, 25, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_handle": ((0.15, -0.45, 0.30), (0.0, 0.06, 0.0), 30),     # the medium's handles, the print
}


def handle(k, col, label, x, y, ang):
    """A handle lying at (x, y), the grip across, the strap's apex toward ang (radians) where the tube joins."""
    ca, sa = math.cos(ang), math.sin(ang)
    ux, uy = -sa, ca                                    # along the grip
    k.cyl("grip", (x, y, R_G), R_G, L_G, axis="x", seg=24, soft=0.004)
    k.cyl("capr", (x, y, R_G), R_G * 1.08, 0.065, axis="x", seg=24, soft=0.006)                   # the rubber middle
    for s in (1, -1):
        k.cyl("capr", (x + s * (L_G / 2 + 0.006), y, R_G), R_G * 1.05, 0.012, axis="x", seg=24, soft=0.003)
    apex = (x, y + 0.11, R_T)
    path = [(x - L_G / 2 - 0.004, y, R_G), apex, (x + L_G / 2 + 0.004, y, R_G)]
    k.sweep(col, path, k.rect(0.025, 0.002, 0.0006), bend=0.02, up=(0, 0, 1), soft=0.0)          # the strap
    k.text("white", label, (x + 0.028, y + 0.055, (R_G + R_T) / 2 + 0.001), 0.008, rx=0.0,
           rz=math.atan2(0.11, L_G / 2) - math.pi, depth=0.002)
    return apex


def tube_set(k, col, label, x0, y0):
    a1 = handle(k, col, label, x0 - 0.08, y0, 0.0)
    a2 = handle(k, col, label, x0 + 0.08, y0 - 0.03, 0.0)
    pts = [a1]
    cx, cy = x0, y0 + 0.24
    for i in range(41):                                 # round a loose loop behind and back
        t = math.pi * 1.25 - 2 * math.pi * 0.95 * i / 40
        pts.append((cx + 0.27 * math.cos(t), cy + 0.12 * math.sin(t), R_T))
    pts.append(a2)
    k.sweep("sleeve", pts, k.circle(R_T, 14), bend=0.02, soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, (col, label) in enumerate(SET):
        tube_set(k, col, label, (i - 2) * 0.65, 0.0)

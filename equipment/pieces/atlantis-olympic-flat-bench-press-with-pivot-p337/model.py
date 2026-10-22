"""Atlantis Olympic Flat Bench Press with Pivot (P337), black frame, red upholstery.

Built by eye from Atlantis's four renders (refs/: ref_02 + ref_05 from behind the towers, ref_03 the rear three-quarter,
ref_04 the front three-quarter), held to Atlantis's 71 x 66 x 49 in (L x W with the horns x H).
Axes: metres, floor z = 0, the bench runs along x, the lifter's head at +x under the bar; y across.
Structure: two towers, each a rack post (the bar catches: two stepped J hooks on its face towards the lifter, its foot
in a pivot bracket on the base tube) in front of a bent storage frame (a front leg up, a big bend back, the rear leg
down) with two horn brackets on the rear leg, a horn out each side of each; a base tube under each tower on disc feet.
Between the towers: a cross tube the bench beam runs into, braces up to the towers, and a low U frame round under the
pad with a post up to the beam. The beam runs back to the tail post on its disc foot.
The tower and the bench parts are functions so the incline (P338) and decline (P339) can reuse them.
"""
import math

import kit

LOOK = {
    "frame": dict(color=(0.02, 0.02, 0.022), rough=0.42, metal=0.2, coat=0.1, bump=(1400, 0.06)),     # black powder coat
    "pad": dict(color=(0.42, 0.012, 0.014), rough=0.5, sheen=0.25, bump=(1500, 0.12)),               # red vinyl
    "seam": dict(color=(0.2, 0.005, 0.006), rough=0.7),
    "steel": dict(color=(0.75, 0.75, 0.76), rough=0.12, metal=1.0, aniso=0.3),                         # chromed horns
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, bump=(700, 0.15)),
    "plastic": dict(color=(0.015, 0.015, 0.016), rough=0.55),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-40, 14, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (130, 16, 1.0)}
DETAILS = {
    "detail_hooks": ((0.0, -1.0, 1.15), (0.28, -0.55, 0.85), 40),       # the stepped J hooks on the near rack post
    "detail_pivot": ((-0.05, -0.95, 0.35), (0.30, -0.55, 0.12), 40),    # the rack post's foot in its pivot bracket
    "detail_under": ((-0.45, -0.9, 0.45), (0.15, 0.0, 0.2), 35),        # the cross tube, the U frame, the beam
}

XR = 0.30                       # the rack posts (x)
TY = 0.55                       # the towers' plane (+-y)
RACK = (0.085, 0.06)            # rack post section: along x, across y
RACK_TOP, RACK_LEAN = 49 * 0.0254, 3.0   # its top, its lean back (deg) from the pivot
STORE = (0.075, 0.06)           # storage frame tube
SX0, SX1, S_TOP = XR, XR + 0.58, 1.17   # the storage frame's front leg is beside the rack post   # the storage frame's legs (x) and the top of its bend
BASE_Z, BASE = 0.10, (0.08, 0.06)   # the base tubes: centre height, section (tall x across)
DISC_R = 0.07
HOOKS = (0.71, 0.90)            # the J hooks' cradle heights
HORNS = (0.40, 0.95)            # horn brackets on the rear leg (z)
HORN_OUT = 0.29                 # horns' length each way from the bracket
PAD_TOP, PAD_T, PAD_W = 0.44, 0.075, 0.30
PAD = (-0.86, 0.24)             # the flat pad (x from / to)
TAIL_X = -0.76                  # the tail post
CROSS_X, CROSS_Z = SX0, 0.30    # the cross tube between the towers


def disc(k, x, y, top):
    """A round disc foot: a rubber pad, a steel flange, a stub up to the member above (ref_03)."""
    k.cyl("rubber", (x, y, 0.009), DISC_R, 0.018, seg=40, soft=0.004)
    k.cyl("frame", (x, y, 0.023), DISC_R - 0.012, 0.01, seg=40, soft=0.002)
    if top > 0.028:
        k.cyl("frame", (x, y, (0.028 + top) / 2), 0.032, top - 0.028, seg=28, soft=0.002)


def tower(k, s):
    """One tower at y = s * TY."""
    y = s * TY
    Z = (0, 0, 1)
    bt = BASE_Z + BASE[0] / 2                                         # the base tube's top
    # the base tube, along x from the rack post's foot to the rear leg, on disc feet
    k.bar("frame", (XR - 0.03, y, BASE_Z), (SX1 + 0.03, y, BASE_Z), BASE[0], BASE[1], up=(0, 1, 0), r=0.01)
    for x_, cap in ((XR - 0.03, -1), (SX1 + 0.03, 1)):
        k.box("plastic", (x_ + cap * 0.004, y, BASE_Z), (0.008, BASE[1] + 0.004, BASE[0] + 0.004), soft=0.003)
    disc(k, SX1, y, BASE_Z - BASE[0] / 2)
    # the storage frame: front leg up, a big bend back, the rear leg down; welded onto the base tube
    k.sweep("frame", [(SX0, y, bt), (SX0, y, S_TOP), (SX1, y, S_TOP), (SX1, y, bt)], k.rect(STORE[0], STORE[1], 0.022),
            up=(0, 1, 0), bend=0.27, cut0=((0, 0, bt), Z), cut1=((0, 0, bt), Z), weld=True)
    # the horn brackets on the rear leg: a plate each side of the leg, a horn through, out both ways, collars
    for hz in HORNS:
        for d in (1, -1):
            k.box("frame", (SX1 + d * (STORE[0] / 2 + 0.005), y, hz), (0.01, 0.10, 0.14), soft=0.002)
        k.box("frame", (SX1 + STORE[0] / 2 + 0.0115, y, hz), (0.024, 0.06, 0.08), soft=0.004)
        hx = SX1 + STORE[0] / 2 + 0.012
        for d in (1, -1):
            k.cyl("frame", (hx, y + d * 0.035, hz), 0.032, 0.012, axis="y", seg=32, soft=0.002)
            k.tube("steel", (hx, y + d * 0.04, hz), (hx, y + d * HORN_OUT, hz), 0.025, seg=32)
            k.cyl("plastic", (hx, y + d * (HORN_OUT + 0.004), hz), 0.027, 0.008, axis="y", seg=32, soft=0.002)
        for d in (1, -1):
            k.bolt((SX1 + d * (STORE[0] / 2 + 0.01), y - 0.03, hz + 0.045), "+x" if d > 0 else "-x", size=0.01)
    # the rack post, beside the storage frame's front leg on the outside (ref_03, ref_04): its own disc foot, a floor
    # plate welded to the base tube's side, its foot between two plates (the pivot), leaning back, a cap on top
    yr = y + s * (STORE[1] / 2 + RACK[1] / 2 + 0.006)
    fz = 0.075
    disc(k, XR, yr, fz - 0.006)
    k.box("frame", (XR, (yr + y) / 2 + s * 0.012, fz), (0.11, abs(yr - y) + RACK[1] / 2 + 0.024, 0.012), soft=0.002)
    for d in (1, -1):
        k.box("frame", (XR, yr + d * (RACK[1] / 2 + 0.005), fz + 0.09), (0.11, 0.01, 0.17), soft=0.002)
    pz = fz + 0.12
    lean = math.radians(RACK_LEAN)
    top = (XR + math.sin(lean) * (RACK_TOP - pz), yr, RACK_TOP - 0.01)
    k.bar("frame", (XR, yr, fz + 0.006), top, RACK[0], RACK[1], up=(0, 1, 0), r=0.014, cut0=((0, 0, fz + 0.006), Z))
    k.box("plastic", (top[0], yr, RACK_TOP - 0.005), (RACK[0] + 0.006, RACK[1] + 0.006, 0.012), soft=0.004)
    k.tube("steel", (XR, yr - (RACK[1] / 2 + 0.02), pz), (XR, yr + RACK[1] / 2 + 0.02, pz), 0.009)
    for d in (1, -1):
        k.bolt((XR, yr + d * (RACK[1] / 2 + 0.01), pz), "+y" if d > 0 else "-y", size=0.024)
    # the pivot's lock: a black lever out of the bracket towards the lifter, a knob
    k.box("plastic", (XR - 0.07, yr, fz + 0.05), (0.07, 0.04, 0.03), soft=0.006)
    k.cyl("plastic", (XR - 0.115, yr, fz + 0.05), 0.02, 0.04, axis="x", seg=24, soft=0.008)
    # the J hooks on its face towards the lifter (stepped teeth, ref_04), bolted
    for hz in HOOKS:
        fx = XR - RACK[0] / 2 + math.sin(lean) * (hz - pz)
        prof = [(0.0, -0.12), (-0.05, -0.05), (-0.075, -0.012), (-0.075, 0.03), (-0.058, 0.03), (-0.05, 0.004),
                (-0.022, 0.004), (0.0, 0.03)]
        k.sweep("plastic", [(fx, yr - 0.03, hz), (fx, yr + 0.03, hz)], kit._round_poly(prof, 0.005, 3), up=(0, 0, 1), soft=0.003)
        k.bolt((fx - 0.025, yr - 0.03, hz - 0.05), "-y", size=0.01, nut=0.06)
    # bolted to the storage frame's front leg higher up: a spacer block and a through-bolt
    k.box("frame", (XR + math.sin(lean) * (1.0 - pz), (yr + y) / 2, 1.0), (0.05, 0.016, 0.06), soft=0.002)
    # the brace from the storage frame's front leg down and in to the cross tube
    k.bar("frame", (SX0, y - s * STORE[1] / 2, 0.62), (CROSS_X, s * 0.32, CROSS_Z + 0.04), 0.05, 0.05, up=(1, 0, 0),
          cut0=((0, y - s * STORE[1] / 2, 0), (0, 1, 0)), weld=True)


def middle(k, beam_from):
    """Between the towers: the cross tube (welded into the storage frames' front legs), the low U frame and its post,
    the beam from `beam_from` (x) to the cross tube. Returns the beam's top height."""
    Y = (0, 1, 0)
    yi = TY - STORE[1] / 2
    k.bar("frame", (CROSS_X, -yi, CROSS_Z), (CROSS_X, yi, CROSS_Z), 0.10, 0.07, up=(0, 0, 1),
          cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    k.text("label", "ATLANTIS", (CROSS_X - 0.0355, 0.0, CROSS_Z + 0.025), 0.03, rz=-math.pi / 2, depth=0.0008)
    ub = TY - BASE[1] / 2
    uz = 0.14
    ux = XR - 0.30
    k.sweep("frame", [(XR + 0.30, -ub, uz), (ux, -0.30, uz), (ux, 0.30, uz), (XR + 0.30, ub, uz)], k.rect(0.07, 0.05, 0.012),
            up=(0, 0, 1), bend=0.14, cut0=((0, -ub, 0), Y), cut1=((0, ub, 0), Y), weld=True)
    btop = PAD_TOP - PAD_T - 0.01
    bz = btop - 0.05
    k.bar("frame", (beam_from, 0, bz), (CROSS_X - 0.035, 0, bz), 0.10, 0.06, up=Y,
          cut1=((CROSS_X - 0.035, 0, 0), (1, 0, 0)), weld=True)
    k.bar("frame", (ux - 0.01, 0, uz + 0.025), (ux - 0.01, 0, bz - 0.05), 0.06, 0.06, up=Y,
          cut0=((0, 0, uz + 0.025), (0, 0, 1)), cut1=((0, 0, bz - 0.05), (0, 0, 1)), weld=True)
    disc(k, ux - 0.01, 0.0, uz - 0.025)
    return btop, bz


def build(k):
    for s in (1, -1):
        tower(k, s)
    btop, bz = middle(k, PAD[0] + 0.02)
    k.box("plastic", (PAD[0] + 0.016, 0, bz), (0.008, 0.064, 0.104), soft=0.003)
    # the tail post on its disc, welded under the beam
    k.tube("frame", (TAIL_X, 0, 0.028), (TAIL_X, 0, bz - 0.05), 0.038, seg=32, cut1=((0, 0, bz - 0.05), (0, 0, 1)), weld=True)
    disc(k, TAIL_X, 0, 0.0)
    # the pad on two mount plates on the beam
    for x_ in (PAD[0] + 0.25, PAD[1] - 0.25):
        k.box("frame", (x_, 0, btop + 0.005), (0.20, 0.16, 0.01), soft=0.002)
    L = PAD[1] - PAD[0]
    k.shaped_pad("pad", [(-L / 2, -PAD_W / 2), (L / 2, -PAD_W / 2), (L / 2, PAD_W / 2), (-L / 2, PAD_W / 2)],
                 ((PAD[0] + PAD[1]) / 2, 0, PAD_TOP - PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.04, cushion=0.028)

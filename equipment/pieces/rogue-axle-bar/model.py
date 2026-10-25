"""Rogue Axle Bar, lying on the floor (refs/: ref_01 loaded in a rack, Rogue's colour bumpers and red collars; ref_02
the whole bar on the floor; ref_03 the ROGUE label at its middle; ref_04 a collar ring; ref_05 in use). The linked page
is gone (404): Rogue's standard axle, 7 ft long, a 2 in shaft with no knurl and no rotating sleeves (the plates load on
the same 2 in bar outside a thin ring each side), 16 in to load each side, black. Built to the two gates and README
point 9 on the shared builder (equipment/blender/barbell.py).

DESIGN SPEC (gate 1)
1. Use. Strongman pressing, deadlifts and cleans on a fat, unknurled bar that doesn't spin: the grip is the work.
2. Each mass named (ref_02 / ref_04): one 2 in black steel bar end to end; a thin ring each side (a flange 64 mm
   across) where the loading begins, the plates stopping against it; the white ROGUE label at the middle (ref_03).
3. Adjustments. None.
4. Load path. The plates on the 2 in ends against the rings, the bar.
5. Fit range. A 2 in bar fills any user's (1.55 / 1.78 / 1.95 m) grip; the 1.30 m between the rings takes the widest
   pressing grip.
6. Size. 2.13 m long, 2 in, 16 in loadable each side (estimates from Rogue's standard axle; the page is gone).
Axes: metres, floor z = 0, the bar along x, centred on x = 0, lying on its rings.
"""

import math

import barbell

IN = 0.0254
S = dict(
    L=84 * IN, G=84 * IN - 2 * (16 * IN + 0.008), shaft=2 * IN, sleeve=2 * IN,
    collar=[(0.0, 0.032), (0.008, 0.032)],
    knurl=[], centre=0.0, marks=[],
    badge=dict(text=[], size=0.004, r=0.020),
)
BLACK = dict(color=(0.008, 0.008, 0.009), rough=0.75, metal=0.1, coat=0.0, bump=(2200, 0.1))   # textured black
LOOK = {
    "shaft": BLACK,
    "knurl": BLACK,
    "sleeve": BLACK,
    "collar": dict(BLACK, rough=0.35),
    "gap": dict(color=(0.005, 0.005, 0.005), rough=0.6),
    "badge": dict(color=(0.02, 0.02, 0.022), rough=0.4),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4),
    "label": dict(color=(0.88, 0.88, 0.88), rough=0.45),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_label": ((-0.05, -0.25, 0.20), (0.0, 0.0, 0.032), 40),      # ref_03: the label
    "detail_ring": ((0.55, -0.25, 0.15), (0.65, 0.0, 0.032), 45),       # ref_04: a ring
}


def build(k):
    barbell.build(k, S)
    zc = barbell.z_axis(S)
    k.tube("shaft", (-S["G"] / 2, 0, zc), (S["G"] / 2, 0, zc), IN + 0.0002, seg=64)    # one piece over the middle
    a = math.radians(20)                                # the label on the side toward the camera, tipped up a little
    r = IN + 0.0006
    k.text("label", "ROGUE", (0.0, -r * math.cos(a), zc + r * math.sin(a)), 0.019, rx=math.pi / 2 - a, depth=0.0004)

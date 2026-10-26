"""Hammer Strength 3-in-1 Wood Plyo Box (refs/: ref_01 the box, pale plywood, a hand hole in each face, the height each
face gives printed in black at its top corner (60 cm / 24 in seen) with ticks down the edge, HAMMER STRENGTH low). The
linked page (shop.lifefitness.com) has rate-limited us: the heights 50 / 60 / 76 cm, as the soft box's, give its size.
Built to the two gates and README point 9 (the shared box: equipment/blender/plyo.py).

DESIGN SPEC (gate 1)
1. Use. Box jumps, step-ups, step-downs: turned to give 50, 60 or 76 cm.
2. Each mass named (ref_01): a box of plywood panels, 50 x 76 x 60 cm, its edges eased; a hand hole in each face
   (a slot); the print in black.
3. Adjustments. The face it stands on: 50 / 60 / 76 cm.
4. Load path. The feet on the top panel, the panels, the floor.
5. Fit range. 50 / 60 / 76 cm: 0.39 H for the 1.55 m user at 60 cm and the 1.95 m user at 76 cm. No figure.
6. Size. 0.50 x 0.76 x 0.60 m (standing at 60).
Axes: metres, floor z = 0; its ends facing +-y.
"""
import plyo

LOOK = {
    "ply": dict(color=(0.62, 0.45, 0.24), rough=0.6, coat=0.0,
                grain=dict(dark=(0.45, 0.28, 0.12), scale=7.0, distortion=2.5, along="X")),
    "print": dict(color=(0.02, 0.02, 0.022), rough=0.6, coat=0.0),
    "hole": dict(color=(0.03, 0.02, 0.012), rough=1.0, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_corner": ((-0.55, -0.85, 0.75), (-0.10, -0.30, 0.45), 35),   # the print, a hand hole
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    plyo.box(k, "ply", "print", soft=0.004, holes="hole")

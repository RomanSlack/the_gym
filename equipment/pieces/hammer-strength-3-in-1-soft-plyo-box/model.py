"""Hammer Strength 3-in-1 Soft Plyo Box (refs/: ref_01 / ref_02 the box, black vinyl over foam, a darker textured grip
panel inset on each face, white ticks down an edge with the height each face gives (76 / 30, 60 / 24, 50 / 20), HAMMER
STRENGTH low, the yellow triangle; ref_03 a corner close; ref_04 stepped on; ref_05 in a gym). The linked page
(shop.lifefitness.com) has rate-limited us: the three heights printed on it, 50 / 60 / 76 cm, give its size. Built to
the two gates and README point 9 (the shared box: equipment/blender/plyo.py).

DESIGN SPEC (gate 1)
1. Use. Box jumps, step-ups, Bulgarian split squats, seated work: turned to give 50, 60 or 76 cm.
2. Each mass named (ref_01 / ref_02): one foam block in black vinyl, 50 x 76 x 60 cm, its edges soft; a grip panel on
   each face; the print: each face's height, the ticks, HAMMER STRENGTH, the triangle.
3. Adjustments. The face it stands on: 50 / 60 / 76 cm.
4. Load path. The feet on the top, the foam, the floor.
5. Fit range. 50 / 60 / 76 cm: the 1.55 m user's box jump top at 60 cm is 0.39 H, the 1.95 m user's 76 cm is 0.39 H:
   each user has a height. No figure.
6. Size. 0.50 x 0.76 x 0.60 m (standing at 60).
Axes: metres, floor z = 0; its ends facing +-y.
"""
import plyo

LOOK = {
    "vinyl": dict(color=(0.010, 0.010, 0.011), rough=0.5, coat=0.0, spec=0.35, bump=(1500, 0.03)),
    "grip": dict(color=(0.006, 0.006, 0.007), rough=0.9, coat=0.0, spec=0.2, bump=(5000, 0.3)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "yellow": dict(color=(0.75, 0.55, 0.02), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_corner": ((-0.55, -0.85, 0.75), (-0.10, -0.30, 0.45), 35),   # the 76 / 30 corner, the ticks
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    plyo.box(k, "vinyl", "white", soft=0.012, inset="grip", logo="yellow")

"""Life Fitness Mini Power Bands (refs/: ref_01 the five, flat loops of latex in red, blue, green, black and purple;
ref_02-06 each alone; ref_07-09 in use round the knees on a hip thrust). The shop page refuses requests (HTTP 429): the
size, a 12 in loop (30 cm flat), is the usual mini band and an estimate; the strength goes with the colour and the
width (red light and narrow to purple heaviest and widest, ref_01). Built to the two gates and README point 9 (equipment/blender/bands.py).

DESIGN SPEC (gate 1)
1. Use. Hip circles: round the thighs above the knees or the ankles, for glute work, walks and activation.
2. Each mass named (ref_02): one loop of latex lying flat, its ends open, 15-50 mm wide by its strength, about 1 mm
   thick, in its colour.
3. Adjustments. The colour (the strength): red, blue, green, black, purple.
4. Load path. The band round the legs, pulling them together.
5. Fit range. A 12 in loop goes round the thighs of every user (1.55 / 1.78 / 1.95 m) above the knee. No figure.
6. Size. Five lying fanned, 0.30 x 0.05 m each.
Axes: metres, floor z = 0.
"""
import bands

SET = (("red", 0.015), ("blue", 0.02), ("green", 0.028), ("black", 0.04), ("purple", 0.05))     # widths (ref_01)
T = 0.0012

LOOK = {
    "red": dict(color=(0.45, 0.012, 0.012), rough=0.5, coat=0.0, spec=0.4),
    "blue": dict(color=(0.01, 0.025, 0.20), rough=0.5, coat=0.0, spec=0.4),
    "green": dict(color=(0.01, 0.20, 0.05), rough=0.5, coat=0.0, spec=0.4),
    "black": dict(color=(0.010, 0.010, 0.011), rough=0.5, coat=0.0, spec=0.4),
    "purple": dict(color=(0.10, 0.02, 0.24), rough=0.5, coat=0.0, spec=0.4),
}
VIEWS = {"three_quarter": (-30, 35, 1.0), "front": (0, 25, 1.0), "side": (90, 25, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_band": ((0.25, -0.35, 0.20), (0.0, -0.10, 0.0), 30),        # a band's folded end
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, (col, w) in enumerate(SET):
        bands.flat_loop(k, col, (0.04 * i, -0.18 + 0.09 * i, 0.0), 0.30, w, T, rz=0.15 - 0.07 * i,
                        fold=0.006 + 0.12 * w)

"""Life Fitness Power Bands (refs/: ref_01 the range bundled; ref_02-09 each: orange, red, blue, green, black,
purple, black and grey, each a long latex loop folded into a bundle, the widths from about 13 to 100 mm). The shop page
refuses requests (HTTP 429): the loop, 41 in (1.04 m round, 0.52 m flat), and the widths and 4.5 mm are the usual
power band and estimates off the refs. Built to the two gates and README point 9 (equipment/blender/bands.py).

DESIGN SPEC (gate 1)
1. Use. Assisted pull-ups, banded lifts, mobility and stretching: looped over a bar or a foot, or round a barbell's
   sleeve and a peg.
2. Each mass named (ref_02-09): one loop of layered latex, 4.5 mm thick, its width by its strength, in its colour.
3. Adjustments. The band (the strength): orange lightest and narrowest to grey heaviest and widest.
4. Load path. The band stretched between the bar or peg and the body.
5. Fit range. A 41 in loop over a pull-up bar reaches a knee or a foot of every user (1.55 / 1.78 / 1.95 m). No figure.
6. Size. Seven lying flat in a row, 0.52 m long.
Axes: metres, floor z = 0; the bands along x.
"""
import bands

SET = (("orange", 0.013), ("red", 0.022), ("blue", 0.032), ("green", 0.044), ("black", 0.064), ("purple", 0.083),
       ("grey", 0.100))
T = 0.0045

LOOK = {
    "orange": dict(color=(0.55, 0.15, 0.01), rough=0.5, coat=0.0, spec=0.4),
    "red": dict(color=(0.45, 0.012, 0.012), rough=0.5, coat=0.0, spec=0.4),
    "blue": dict(color=(0.02, 0.06, 0.16), rough=0.5, coat=0.0, spec=0.4),
    "green": dict(color=(0.01, 0.22, 0.04), rough=0.5, coat=0.0, spec=0.4),
    "black": dict(color=(0.010, 0.010, 0.011), rough=0.5, coat=0.0, spec=0.4),
    "purple": dict(color=(0.10, 0.03, 0.24), rough=0.5, coat=0.0, spec=0.4),
    "grey": dict(color=(0.13, 0.13, 0.12), rough=0.5, coat=0.0, spec=0.4),
}
VIEWS = {"three_quarter": (-30, 35, 1.0), "front": (0, 25, 1.0), "side": (90, 25, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_band": ((0.45, -0.45, 0.30), (0.20, 0.0, 0.0), 30),         # the folded ends
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    y = -0.30
    for col, w in SET:
        y += w / 2
        bands.flat_loop(k, col, (0.0, y, 0.0), 0.52, w, T, fold=0.012 + 0.05 * w)
        y += w / 2 + 0.03

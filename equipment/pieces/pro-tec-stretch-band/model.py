"""Pro-Tec Stretch Band (refs/: ref_01 the band coiled: a blue strap with grey edges, sewn into a chain of loops; ref_02
/ ref_05 in use; ref_03 laid flat, doubled: blue, grey edges, a white end tab each end; ref_04 a hand in a loop). The
linked page was not fetched: the size (about 1.0 m doubled, 50 mm wide) is an estimate off ref_03. Laid flat as
ref_03. Built to the two gates and README point 9 (equipment/blender/bands.py).

DESIGN SPEC (gate 1)
1. Use. Assisted stretching: a foot or hand in a loop, the other end pulled to deepen the stretch, a loop at a time.
2. Each mass named (ref_03): the strap, blue webbing with grey edges, sewn across into loops along its length; the
   white tabs at the ends.
3. Adjustments. Which loop is held.
4. Load path. The hands, the strap, the foot.
5. Fit range. Loops along its length suit every user's reach (1.55 / 1.78 / 1.95 m). No figure.
6. Size. Laid flat, 1.0 x 0.05 m.
Axes: metres, floor z = 0; the strap along x.
"""
import bands

LOOK = {
    "blue": dict(color=(0.02, 0.06, 0.45), rough=0.85, coat=0.0, bump=(3000, 0.1)),
    "grey": dict(color=(0.20, 0.20, 0.21), rough=0.85, coat=0.0, bump=(3000, 0.1)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.7, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_end": ((-0.45, -0.25, 0.20), (-0.40, 0.0, 0.0), 30),        # an end tab, the edges
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    bands.flat_loop(k, "grey", (0, 0, 0), 1.0, 0.05, 0.003, fold=0.008)                             # the strap's edges
    bands.flat_loop(k, "blue", (0, 0, 0.0002), 0.985, 0.036, 0.0034, fold=0.0082)                   # its blue middle
    for s in (1, -1):
        k.box("white", (s * 0.47, 0, 0.0075), (0.05, 0.052, 0.0012), soft=0.0)                       # the end tabs

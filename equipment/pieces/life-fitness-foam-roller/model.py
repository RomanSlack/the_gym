"""Life Fitness Foam Roller (refs/: ref_01 / ref_02 grey, the long one, a fine diamond texture all over, the LifeFitness
script in white on its end; ref_03 black). The shop page refuses requests (HTTP 429): the sizes, 6 in across, 36 and
18 in long (the two usual lengths), are estimates off the refs' proportions. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Self-myofascial release and mobility: lain on and rolled along under the back, legs, lats.
2. Each mass named (ref_01): one cylinder of firm moulded foam, 6 in, its surface in a fine diamond texture, its ends
   flat with the script on one.
3. Adjustments. None (two lengths, two colours).
4. Load path. The body on the roller, the floor.
5. Fit range. 36 in spans any user's back across (1.55-1.95 m: shoulders 0.35-0.45 m); the 18 in for legs. No figure.
6. Size. Three: grey 36 in, grey 18 in, black 18 in, lying.
Axes: metres, floor z = 0; the rollers along x.
"""
import math

IN = 0.0254
R = 3 * IN
ROLLERS = (("grey", 36 * IN, -0.25), ("grey", 18 * IN, 0.0), ("black", 18 * IN, 0.25))

LOOK = {
    "grey": dict(color=(0.12, 0.12, 0.125), rough=0.8, coat=0.0, spec=0.25, bump=(600, 0.7)),
    "black": dict(color=(0.014, 0.014, 0.015), rough=0.8, coat=0.0, spec=0.25, bump=(600, 0.7)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_end": ((-0.85, -0.55, 0.25), (-0.45, -0.25, 0.08), 30),     # the long one's end, the script
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for col, L, y in ROLLERS:
        k.cyl(col, (0.0, y, R), R, L, axis="x", seg=48, soft=0.004)
        if col == "grey":
            k.text("white", "LifeFitness", (-L / 2 - 0.0001, y, R), R * 0.42, rz=-math.pi / 2, depth=0.0004)

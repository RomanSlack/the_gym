"""Rogue Wrist Wraps, black / white, 18 in (refs/: ref_01 a pair rolled and closed; ref_02 a pair laid flat: black
elastic, two white stripes along most of each, a black hook-and-loop patch, the thumb loop at one end, ROGUE in white
across it by the loop; ref_03-05 the patch, the stripes, the thumb loop close). The linked page: 12, 18 and 24 in, 3 in
wide, 40 % elastic, black / white, a thumb loop, hook-and-loop closure. Fetched 2026-10-25. The 18 in. Built to the
two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Wrist support for pressing and jerks: the thumb through the loop, the wrap wound tight round the wrist, the
   end closed on the patch.
2. Each mass named (ref_02): the wrap, 3 in elastic, black with two white stripes; the hook-and-loop patch; the thumb
   loop, a narrow strip sewn on the end; ROGUE across the wrap by the loop.
3. Adjustments. The tension wound in.
4. Load path. The wrap round the wrist, its patch.
5. Fit range. 18 in winds two to three turns round any wrist (1.55-1.95 m users: 15-19 cm round). No figure.
6. Size. A pair laid flat, 0.46 x 0.076 m each.
Axes: metres, floor z = 0; the wraps along x, the loops toward -x.
"""
IN = 0.0254
L, W, T = 18 * IN, 3 * IN, 0.003

LOOK = {
    "black": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, spec=0.2, bump=(3000, 0.15)),
    "white": dict(color=(0.75, 0.75, 0.75), rough=0.8, coat=0.0, bump=(3000, 0.15)),
    "hook": dict(color=(0.02, 0.02, 0.022), rough=0.95, coat=0.0, bump=(5000, 0.4)),
    "grey": dict(color=(0.05, 0.05, 0.055), rough=0.85, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_loop": ((-0.35, -0.30, 0.25), (-0.18, -0.05, 0.0), 30),     # the thumb loop, ROGUE, the stripes
}


def wrap(k, y):
    k.box("black", (0, y, T / 2), (L, W, T), soft=0.001)                                           # the wrap
    for dy in (0.010, -0.010):                          # the white stripes, the patch end left plain
        k.box("white", (0.06, y + dy, T + 0.0003), (L - 0.20, 0.008, 0.0006), soft=0.0)
    k.box("hook", (L / 2 - 0.06, y, T + 0.0006), (0.10, W - 0.012, 0.0012), soft=0.0005)            # the patch
    k.text("white", "ROGUE", (-L / 2 + 0.045, y, T + 0.0003), 0.022, rx=0.0, rz=1.5708, depth=0.0006)
    k.box("grey", (-L / 2 - 0.035, y, 0.0008), (0.09, 0.022, 0.0016), soft=0.0005)                   # the thumb loop
    k.box("grey", (-L / 2 - 0.005, y, T / 2), (0.02, 0.022, T + 0.002), soft=0.0005)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    wrap(k, -0.06)
    wrap(k, 0.06)

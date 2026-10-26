"""The Tib Bar Guy Slant Board (refs/: ref_01 the board: a black moulded wedge, grip tape on its slope, the TIB BAR GUY
mark in white; ref_02-12 the exercises it opens, the slant stack, in use). The linked page (thetibbarguy.com) was not
fetched: the size (about 15 x 13 in and 4 in at the high edge, a 17 degree slope) is an estimate off ref_01 and the
shoes in ref_09. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Heels-raised squats, split squats, Patrick steps, calf and ankle stretches: the heels up the slope.
2. Each mass named (ref_01): the wedge, dense moulded foam, its edges eased; the grip tape on the slope; the mark.
3. Adjustments. Turned for heels up or toes up; stacked for more height (sold separately).
4. Load path. The feet on the tape, the wedge, the floor.
5. Fit range. 15 in long: any user's (1.55 / 1.78 / 1.95 m) foot fits on it, heels high. No figure.
6. Size. 0.38 x 0.33 x 0.10 m.
Axes: metres, floor z = 0; the slope rising toward +y.
"""
import math

IN = 0.0254
W, L, HH = 15 * IN, 13 * IN, 4 * IN

LOOK = {
    "foam": dict(color=(0.014, 0.014, 0.015), rough=0.7, coat=0.0, bump=(1500, 0.05)),
    "tape": dict(color=(0.02, 0.02, 0.022), rough=0.95, coat=0.0, bump=(6000, 0.5)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 25, 1.0), "front": (0, 10, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_mark": ((0.0, -0.55, 0.40), (0.0, 0.0, 0.05), 30),          # the slope, the tape, the mark
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    lo = 0.008
    k.slab("foam", [(-L / 2, 0.0), (L / 2, 0.0), (L / 2, HH), (-L / 2, lo)], -W / 2, W / 2, 0.006, seg=3)   # the wedge
    a = math.atan2(HH - lo, L)
    zc = (HH + lo) / 2
    k.box("tape", (0, 0, zc + 0.0006), (W - 0.03, L / math.cos(a) - 0.03, 0.0012), rx=a, soft=0.0)
    k.text("white", "TIB BAR GUY", (0, 0.0, zc + 0.0014), 0.035, rx=a, depth=0.0005)

"""BOSU Pro Balance Trainer (refs/: ref_01 grey dome on a black platform, rings moulded round the dome, the BOSU mark
in a circle at its top, a hand grip in the platform's rim each side). The shop page refuses requests (HTTP 429): the
size, 26 in across and about 10 in high, is BOSU's usual and an estimate. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Balance and core work: stood, knelt or sat on the dome, or turned over (platform up) for push-ups and squats.
2. Each mass named (ref_01): the dome, inflated PVC, a spherical cap with moulded rings; the platform, a black disc
   with a raised rim, a grip let into it each side; the mark at the dome's top.
3. Adjustments. The inflation; dome up or down.
4. Load path. The feet on the dome, the air, the platform, the floor.
5. Fit range. 26 in: every user (1.55 / 1.78 / 1.95 m) stands on it feet hip-width. No figure.
6. Size. 0.66 m across, 0.25 m high.
Axes: metres, floor z = 0; the grips at +-x.
"""
import math
import balls

IN = 0.0254
A, H, TB = 13 * IN, 0.25, 0.045      # the dome's base radius, the height, the platform
RS = (A ** 2 + (H - TB) ** 2) / (2 * (H - TB))
ZC = H - RS

LOOK = {
    "dome": dict(color=(0.075, 0.075, 0.08), rough=0.45, coat=0.0, spec=0.45, bump=(1500, 0.02)),
    "ring": dict(color=(0.06, 0.06, 0.065), rough=0.45, coat=0.0),
    "base": dict(color=(0.012, 0.012, 0.013), rough=0.5, coat=0.1),
    "mark": dict(color=(0.30, 0.30, 0.31), rough=0.5, coat=0.0),
    "hole": dict(color=(0.002, 0.002, 0.002), rough=1.0, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_grip": ((0.70, -0.55, 0.35), (0.30, 0.0, 0.05), 30),        # a grip in the rim, the dome's edge
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    a0 = math.asin(A / RS)
    prof = [(RS * math.sin(a0 * (1 - i / 30)), ZC + RS * math.cos(a0 * (1 - i / 30))) for i in range(31)]
    prof = [(A + 0.004, TB - 0.003)] + prof + [(0.0, H)]
    k.lathe("dome", (0, 0, 0), prof, seg=72)                                                         # the dome
    for f in (0.35, 0.55, 0.75, 0.92):                  # the moulded rings
        a = a0 * f
        balls.band(k, "ring", (0, 0, ZC), RS, math.pi / 2 - a, 0.004, h=0.0012)
    k.cyl("mark", (0, 0, H - 0.0015), 0.035, 0.0035, seg=40, soft=0.0)                               # the mark
    k.text("dome", "BOSU", (0, 0, H + 0.0002), 0.018, rx=0.0, depth=0.0006)
    k.cyl("base", (0, 0, TB / 2), A + 0.02, TB, seg=72, soft=0.006)                                    # the platform
    k.lathe("base", (0, 0, TB - 0.002), [(A + 0.02, 0.0), (A + 0.02, 0.012), (A + 0.006, 0.014), (A + 0.002, 0.0)], seg=72)
    for s in (1, -1):                                   # a grip let into the rim each side
        k.box("base", (s * (A + 0.022), 0, TB / 2 + 0.004), (0.045, 0.24, TB + 0.008), soft=0.02)     # its bulge
        k.box("hole", (s * (A + 0.036), 0, TB / 2 + 0.004), (0.022, 0.12, TB - 0.014), soft=0.008)     # the hand hole

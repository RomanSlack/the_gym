"""Life Fitness Multi Grip Bar (refs/: ref_01 the bar from above at an angle: a black frame of tube tapering into the end
shafts, inside it per side two straight rungs and one angled rung splaying out from the middle; collar rings, plain
sleeves). The shop refused further requests (HTTP 429): the sizes are ours from ref_01 (estimates): 2.08 m overall,
the frame 0.95 m along its rails and 0.31 m across, 1.25 in rungs, 14 in sleeves. Built to the two gates and README
point 9 (the layout as the Rogue MG-1's).

DESIGN SPEC (gate 1)
1. Use. Neutral-grip presses, rows and curls; the angled pair turns the wrists part way between neutral and pronated.
2. Each mass named (ref_01): the frame, two straight rails of tube and the tapers converging on each end shaft; the
   rungs across it: per side two straight ones near the end and one angled one inside; the end shafts, collar rings,
   sleeves. Black.
3. Adjustments. Which pair.
4. Load path. The plates on the sleeves, the end shafts, the tapers, the rails, the rungs, the hands.
5. Fit range. The straight pairs 0.58 / 0.72 m apart (wide), the angled pair about 0.30 m at its middle: shoulder-width
   for 1.55 / 1.78 / 1.95 m users. No figure.
6. Size. 2.08 m (estimate).
Axes: metres, floor z = 0, the bar along x lying flat on its collars and the frame.
"""

IN = 0.0254
L = 82 * IN
R_COL = 0.031
ZC = R_COL
Y_RAIL = 0.135                         # (ref_01: the frame wide for its length)
X_RAIL = 0.40
X_TIP = 0.52
RW, RH = 1.5 * IN, 1.5 * IN            # heavy square tube, its corners well rounded
STRAIGHT = (0.29, 0.36)               # the straight rungs (x)
ANGLED = (0.20, 0.10)                 # the angled rung: its x at the far rail, at the near rail
R_RUNG = 0.016
X_COL = L / 2 - 14 * IN
R_SH, R_SL = 0.020, 0.025

LOOK = {
    "frame": dict(color=(0.018, 0.020, 0.019), rough=0.45, metal=0.3, coat=0.15),
    "sleeve": dict(color=(0.025, 0.026, 0.026), rough=0.35, metal=0.6, coat=0.2),
    "gap": dict(color=(0.005, 0.005, 0.005), rough=0.6),
}
VIEWS = {"three_quarter": (-30, 28, 1.2), "front": (0, 6, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.2),
         "top": (0, 88, 1.2)}
DETAILS = {"detail_frame": ((0.10, -0.70, 0.45), (0.0, 0.0, 0.03), 40)}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    prof = k.rect(RW, RH, 0.012)                        # the frame's tube, rounded
    for sy in (1, -1):
        y = sy * Y_RAIL
        k.sweep("frame", [(-X_TIP, sy * R_SH, ZC), (-X_RAIL, y, ZC), (X_RAIL, y, ZC), (X_TIP, sy * R_SH, ZC)], prof,
                bend=0.05, up=(0, 0, 1))
    yi = Y_RAIL - RW / 2
    for sx in (1, -1):
        k.tube("frame", (sx * (X_TIP - 0.03), 0, ZC), (sx * X_COL, 0, ZC), R_SH, seg=28)              # the end shaft
        k.tube("sleeve", (sx * X_COL, 0, ZC), (sx * (X_COL + 0.014), 0, ZC), R_COL, seg=40)           # the collar
        k.disc("gap", (sx * (X_COL + 0.0143), 0, ZC), R_SL + 0.003, R_SL, 0.0006, axis="x", seg=40)
        k.tube("sleeve", (sx * (X_COL + 0.014), 0, ZC), (sx * L / 2, 0, ZC), R_SL, seg=40)
        for x in STRAIGHT:
            k.tube("frame", (sx * x, -yi, ZC), (sx * x, yi, ZC), R_RUNG, seg=24)
        k.tube("frame", (sx * ANGLED[1], -yi, ZC), (sx * ANGLED[0], yi, ZC), R_RUNG, seg=24)          # the angled one

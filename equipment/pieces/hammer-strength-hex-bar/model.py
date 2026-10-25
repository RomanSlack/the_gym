"""Hammer Strength Hex Bar (refs/: ref_01 the bar from above at an angle: a hexagon of rectangular tube, black, meeting at a
Y each end; a straight grip across each side near the Ys; a stub to a thin collar ring and the sleeve; HAMMER STRENGTH
printed on the frame). The shop refused further requests (HTTP 429): the sizes are ours from ref_01 (estimates): 2.0 m
overall, the hexagon 1.0 m tip to tip and 0.56 m across, the frame 2 x 1 in tube on edge, the grips 1.25 in, 0.58 m
apart, the sleeves 0.38 m. Built to the two gates and README point 9 (the layout as the Life Fitness Dual-Height Hex
Bar's, single height).

DESIGN SPEC (gate 1)
1. Use. Deadlifts, shrugs and carries standing inside the hexagon: the load's line runs through the lifter, the hands
   at their sides on the neutral grips.
2. Each mass named (ref_01): the hexagon, two halves of rectangular tube on edge meeting at a Y each end; a plate
   across the inside of each Y; the grips, straight round tubes across the hexagon near the Ys; the stub from each Y to
   the collar ring; the sleeve. Matte black.
3. Adjustments. None.
4. Load path. The plates on the sleeves, the stubs, the Ys, the hexagon's halves, the grips, the hands.
5. Fit range. The hexagon's 0.56 m inside takes any user's (1.55 / 1.78 / 1.95 m) stance; the grips 0.58 m apart sit
   by the hips; on the floor they stand at the collars' height, so a loaded bar's grips are 225 mm up less the frame.
6. Size. 2.0 m x 0.60 m (estimates).
Axes: metres, floor z = 0, the bar along x lying on its collars, the lifter stands in the hexagon facing -y.
"""
import math

IN = 0.0254
L = 2.0
APEX, SHX, HY = 0.50, 0.25, 0.28      # the Y's apex (x), the shoulders (x), the long sides (y)
GX = 0.29                             # the grips (x)
R_COL = 0.035
Z0 = R_COL
SLEEVE = 0.38

LOOK = {
    "frame": dict(color=(0.010, 0.010, 0.011), rough=0.55, metal=0.2, coat=0.0, bump=(1200, 0.07)),  # matte black
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.45),
}
VIEWS = {"three_quarter": (-35, 28, 1.2), "front": (0, 8, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 30, 1.2)}
DETAILS = {"detail_y": ((0.85, -0.45, 0.32), (0.45, 0.0, 0.05), 45)}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    prof = k.rect(1.0 * IN, 2.0 * IN, 0.004)          # the frame tube on edge
    for s in (1, -1):
        k.sweep("frame", [(-APEX, 0, Z0), (-SHX, s * HY, Z0), (SHX, s * HY, Z0), (APEX, 0, Z0)], prof, bend=0.06,
                up=(0, 0, 1))
    x_col = L / 2 - SLEEVE - 0.012
    for s in (1, -1):
        k.box("frame", (s * (APEX - 0.03), 0, Z0), (0.008, 0.07, 0.045), soft=0.002)                 # the Y's plate
        k.tube("frame", (s * (APEX - 0.02), 0, Z0), (s * x_col, 0, Z0), 0.021, seg=32)               # the stub
        k.cyl("frame", (s * (x_col + 0.006), 0, Z0), R_COL, 0.012, axis="x", seg=48, soft=0.002)      # the collar
        k.tube("frame", (s * (x_col + 0.012), 0, Z0), (s * L / 2, 0, Z0), 0.025, seg=40)             # the sleeve
        # the grip across the hexagon near the Y (between the long sides' slopes)
        yg = HY * (APEX - GX) / (APEX - SHX) - 0.5 * IN
        k.tube("frame", (s * GX, -yg, Z0), (s * GX, yg, Z0), 0.625 * IN, seg=24)
    k.text("label", "HAMMER STRENGTH", (0.0, -HY, Z0 + IN + 0.0003), 0.014, rx=0.0, depth=0.0003)   # on a long side's top

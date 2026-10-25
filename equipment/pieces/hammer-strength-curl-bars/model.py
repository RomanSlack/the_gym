"""Hammer Strength Curl Bars: the Olympic EZ curl bar (refs/: ref_01 the listing's photo, which shows the straight
variant: brushed stainless, knurled grips with smooth rings, round collars with a bearing face, plain sleeves, the black
end cap with HAMMER STRENGTH; the piece is the EZ, the list's item). The shop refused further requests (HTTP 429): the
EZ's sizes are ours (estimates): 1.20 m overall (47 in), 0.66 m between the collars, the bends' grips angled about 15
deg, 25 mm shaft, 50 mm sleeves 0.24 m long. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Curls, skull crushers, upright rows with the wrists turned in a little: the hands take the angled grips.
2. Each mass named (ref_01's finish): the shaft, stainless, bent twice each side of the middle into two pairs of
   angled grips (narrow inside, wide outside), knurled on the grips; the collars, round with a bearing face; the
   sleeves to the ends; the black end caps, HAMMER STRENGTH.
3. Adjustments. None.
4. Load path. Plates on the sleeves, the collars, the shaft's bends, the hands.
5. Fit range. The inner grips about 0.24 m apart, the outer about 0.44: narrow and shoulder-width grips for 1.55 /
   1.78 / 1.95 m users. No figure.
6. Size. 1.20 m overall (estimate).
Axes: metres, floor z = 0, the bar along x lying on its collars, the bends flat.
"""
import math

L = 1.20
X_COL = 0.33                          # the collars' inner faces
R_SH, R_SL, R_COL, T_COL = 0.0125, 0.025, 0.038, 0.035
ZC = R_COL

LOOK = {
    "steel": dict(color=(0.55, 0.55, 0.56), rough=0.36, metal=1.0, aniso=0.5),                 # brushed stainless
    "knurl": dict(color=(0.42, 0.42, 0.43), rough=0.55, metal=1.0, bump=(4000, 0.4)),
    "collar": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0, aniso=0.7),
    "cap": dict(color=(0.02, 0.02, 0.022), rough=0.35, coat=0.3),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4),
    "gap": dict(color=(0.01, 0.01, 0.01), rough=0.6),
}
VIEWS = {"three_quarter": (-30, 25, 1.2), "front": (0, 6, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.2),
         "top": (0, 88, 1.2)}
DETAILS = {
    "detail_collar": ((-0.30, -0.25, 0.15), (-0.40, 0.0, 0.04), 45),    # ref_01: a collar, a sleeve, the cap
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    pts = [(-X_COL - 0.01, 0), (-0.30, 0), (-0.24, 0.035), (-0.14, -0.030), (-0.06, 0.0), (0.06, 0.0), (0.14, -0.030),
           (0.24, 0.035), (0.30, 0), (X_COL + 0.01, 0)]
    k.sweep("steel", [(x, y, ZC) for x, y in pts], k.circle(R_SH, 20), bend=0.025, soft=0.0)
    for s in (1, -1):                                   # knurl sleeves over the two grips each side (the angled runs)
        for (x0, y0), (x1, y1) in (((0.06, 0.0), (0.14, -0.030)), ((0.14, -0.030), (0.24, 0.035))):
            a, b = 0.2, 0.8
            p0 = (s * (x0 + (x1 - x0) * a), y0 + (y1 - y0) * a, ZC)
            p1 = (s * (x0 + (x1 - x0) * b), y0 + (y1 - y0) * b, ZC)
            k.tube("knurl", p0, p1, R_SH + 0.0003, seg=20)
        k.tube("collar", (s * X_COL, 0, ZC), (s * (X_COL + T_COL), 0, ZC), R_COL, seg=48)
        k.disc("gap", (s * (X_COL - 0.0003), 0, ZC), R_SH + 0.004, R_SH, 0.0006, axis="x", seg=40)
        k.tube("steel", (s * (X_COL + T_COL), 0, ZC), (s * L / 2, 0, ZC), R_SL, seg=48)
        k.cyl("cap", (s * (L / 2 + 0.0003), 0, ZC), R_SL - 0.003, 0.0008, axis="x", seg=40)
        k.text("print", "HAMMER", (s * (L / 2 + 0.0008), 0, ZC + 0.006), 0.0065, rz=s * math.pi / 2, depth=0.0003)
        k.text("print", "STRENGTH", (s * (L / 2 + 0.0008), 0, ZC - 0.004), 0.0055, rz=s * math.pi / 2, depth=0.0003)

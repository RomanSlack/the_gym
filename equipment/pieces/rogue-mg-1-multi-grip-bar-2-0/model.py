"""Rogue MG-1 Multi-Grip Bar 2.0 (refs/: ref_01 in J-cups; ref_02 from above with Rogue's callouts, the geometry read
off it at 1.32 mm/px from the 82 in: 82 in overall, 14 in sleeves, 39 lb, the neutral grips 5.5 / 13.5 / 21.5 in apart;
ref_03 the frame square on, ROGUE on its rail; ref_04 the rungs' welds; ref_05 a sleeve and collar). Fetched
2026-10-24. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Presses, rows and curls with the palms facing each other: the hands take a pair of rungs, narrow, medium or
   wide, inside a frame that carries the load from sleeve to sleeve round them.
2. Each mass named (ref_02 / ref_03): the frame, two straight rails 0.78 m long (2 x 1 in tube standing on edge) and
   the tapered ends converging on each end shaft, a short stub and a gusset at each tip; six round rungs across the
   frame, three pairs symmetric about the middle; the end shaft out to the collar; the sleeve, 14 in, to the end. Black;
   ROGUE on the near rail.
3. Adjustments. Which pair of rungs.
4. Load path. The plates on the sleeves, the collars, the end shafts, the frame's tapers and rails, the rungs, the
   hands.
5. Fit range. The pairs' 140 / 343 / 546 mm centre to centre: narrow inside the shoulders, medium about them, wide
   outside, for 1.55 / 1.78 / 1.95 m users' 0.40-0.51 m shoulders. No figure (pressing needs a bench, not drawn).
6. Size. 2.08 m overall, the frame 0.25 m across.
Axes: metres, floor z = 0, the bar along x, lying flat on its collars and the frame's lower edges.
"""

IN = 0.0254
L = 82 * IN
R_COL = 0.033                         # the collars (the bar rests on them)
ZC = R_COL
Y_RAIL = 0.1115                       # the rails' centre lines (y): the frame 0.247 m over the outsides
X_RAIL = 0.39                         # the rails' half length (ref_02: 495-1085 px)
X_TIP = 0.51                          # the tapers meet the end shaft (ref_02: 405 / 1175 px)
RW, RH = 1.0 * IN, 2.0 * IN           # the rails' tube: across (plan), tall
RUNGS = (2.75 * IN, 6.75 * IN, 10.75 * IN)   # each pair's half spacing (5.5 / 13.5 / 21.5 in)
R_RUNG = 0.0165
X_COL = L / 2 - 14 * IN               # the collars' inner faces
R_SH, R_SL = 0.020, 0.025              # the end shafts as stout as the sleeves (ref_02: x 1.2 below)

LOOK = {
    "frame": dict(color=(0.02, 0.02, 0.022), rough=0.45, metal=0.4, coat=0.15),              # black
    "sleeve": dict(color=(0.03, 0.03, 0.032), rough=0.35, metal=0.7, coat=0.2),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.45),
    "gap": dict(color=(0.005, 0.005, 0.005), rough=0.6),
}
VIEWS = {"three_quarter": (-30, 25, 1.2), "front": (0, 6, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.2),
         "top": (0, 88, 1.2)}                         # ref_02
DETAILS = {
    "detail_frame": ((0.05, -0.75, 0.40), (0.0, 0.0, 0.03), 40),        # ref_03: the frame, the rungs, ROGUE
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for sy in (1, -1):                                  # the rails, standing on edge
        y = sy * Y_RAIL
        k.bar("frame", (-X_RAIL, y, ZC), (X_RAIL, y, ZC), RW, RH, up=(0, 0, 1), r=0.003)
        for sx in (1, -1):                              # the tapers to the end shaft
            k.bar("frame", (sx * X_RAIL, y, ZC), (sx * X_TIP, sy * R_SH, ZC), RW, RH, up=(0, 0, 1), r=0.003)
    for sx in (1, -1):
        # the end plate across the frame's tip, the stub and the gussets
        k.box("frame", (sx * (X_RAIL + 0.005), 0, ZC), (0.012, 2 * Y_RAIL - RW, RH * 0.6), soft=0.002)
        k.tube("frame", (sx * (X_RAIL + 0.011), 0, ZC), (sx * X_TIP, 0, ZC), R_SH * 1.2, seg=28)
        # the end shaft to the collar, the collar, the sleeve
        k.tube("frame", (sx * X_TIP, 0, ZC), (sx * X_COL, 0, ZC), R_SH * 1.2, seg=28)
        k.tube("sleeve", (sx * X_COL, 0, ZC), (sx * (X_COL + 0.016), 0, ZC), R_COL, seg=40)
        k.disc("gap", (sx * (X_COL + 0.0163), 0, ZC), R_SL + 0.003, R_SL, 0.0006, axis="x", seg=40)
        k.tube("sleeve", (sx * (X_COL + 0.016), 0, ZC), (sx * L / 2, 0, ZC), R_SL, seg=40)
        for x in RUNGS:                                 # the rungs across between the rails
            k.tube("frame", (sx * x, -Y_RAIL + RW / 2, ZC), (sx * x, Y_RAIL - RW / 2, ZC), R_RUNG, seg=24)
    k.text("label", "ROGUE", (0.0, -Y_RAIL - RW / 2 - 0.0003, ZC + 0.004), 0.026, depth=0.0004)

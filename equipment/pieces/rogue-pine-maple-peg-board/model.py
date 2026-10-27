"""Rogue Peg Board, the PB-2M maple (refs/: ref_01 the three on a wall; ref_02 the bottoms of each, the black washer
plates with ROGUE cut through; ref_03-05 the unfinished pine, finished pine and maple close: the board's rounded
corners, peg holes, counter-bored mounting screws, two hickory pegs). The linked page: 89.75 x 11.75 x 1.5 in, 32
staggered holes (the description says 35), six counter-bored mounting holes 40 in apart and 9.25 in across, hickory
pegs 6.5 in long and 1.19 in across, a pair; the PB-2M maple with the black washer plates at both ends, polyurethane
finish. Fetched 2026-10-25. Built to the two gates and README point 9. On a display wall section (not the piece).

DESIGN SPEC (gate 1)
1. Use. Pegboard climbs: hanging on the two pegs, moving one peg at a time up the holes.
2. Each mass named (ref_05): the board, maple, rounded corners, the peg holes in two staggered columns; six mounting
   screws in counter-bores; a black steel washer plate at each end with ROGUE cut through; two hickory pegs.
3. Adjustments. The pegs move hole to hole (the climb).
4. Load path. The hands on the pegs, the pegs in the holes, the board, its six screws into the wall.
5. Fit range. Mounted with its foot at 0.75 m, the top at 3.03 m: every user (1.55 / 1.78 / 1.95 m) starts from a
   hang with the feet off the floor on pegs at 1.9-2.3 m and climbs to the top. No figure.
6. Size. 0.30 x 0.04 x 2.28 m.
Axes: metres, floor z = 0; the wall's face at y = 0, the board on it facing -y.
"""
import math

IN = 0.0254
H, W, T = 89.75 * IN, 11.75 * IN, 1.5 * IN
Z0 = 0.75
R_HOLE, R_PEG, L_PEG = 0.6 * IN, 1.19 * IN / 2, 6.5 * IN

LOOK = {
    "maple": dict(color=(0.55, 0.36, 0.20), rough=0.35, coat=0.3,
                  grain=dict(dark=(0.46, 0.29, 0.15), scale=5.0, distortion=2.0, along="X")),
    "hickory": dict(color=(0.50, 0.33, 0.18), rough=0.5, coat=0.0),
    "hole": dict(color=(0.08, 0.05, 0.025), rough=1.0, coat=0.0),
    "plate": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15),
    "bolt": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 10, 1.0), "front": (0, 4, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-70, 20, 1.0)}
DETAILS = {
    "detail_foot": ((-0.35, -0.70, 1.15), (0.0, -0.03, 0.90), 35),     # the plate, a peg, the holes (ref_05)
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if getattr(k, "display", True):                                  # the display wall (not the piece: off when it hangs on a real wall)
        k.box("wall", (0, 0.05, 1.6), (1.0, 0.10, 3.2), soft=0.0)                                      # display wall
    k.box("maple", (0, -T / 2, Z0 + H / 2), (W, T, H), soft=0.01)                                   # the board
    yf = -T - 0.0004
    pitch = (H - 0.36) / 15.5                           # 32 holes, two staggered columns
    holes = []
    for i in range(32):
        z = Z0 + 0.20 + pitch * i / 2
        x = (0.055 if i % 2 else -0.055)
        holes.append((x, z))
        k.cyl("hole", (x, yf, z), R_HOLE, 0.001, axis="y", seg=24, soft=0.0)
    for z in (Z0 + 0.10, Z0 + 0.10 + 40 * IN, Z0 + 0.10 + 80 * IN):         # the mounting screws
        for sx in (1, -1):
            k.cyl("hole", (sx * 9.25 * IN / 2, yf, z), 0.011, 0.001, axis="y", seg=20, soft=0.0)
            k.cyl("bolt", (sx * 9.25 * IN / 2, yf + 0.004, z), 0.007, 0.004, axis="y", seg=16, soft=0.0008)
    for z in (Z0 + 0.045, Z0 + H - 0.045):              # the washer plates, ROGUE cut through
        k.box("plate", (0, -T - 0.002, z), (W - 0.004, 0.004, 0.09), soft=0.002)
        k.text("maple", "ROGUE", (0, -T - 0.0042, z - 0.018), 0.05, depth=0.0006)
        for sx in (1, -1):
            k.cyl("bolt", (sx * (W / 2 - 0.025), -T - 0.0045, z), 0.006, 0.002, axis="y", seg=12, soft=0.0005)
    for x, z in (holes[2], holes[3]):                    # the two pegs, stored low (ref_01)
        k.cyl("hickory", (x, -T - L_PEG / 2 + 0.065, z), R_PEG, L_PEG, axis="y", seg=24, soft=0.002)

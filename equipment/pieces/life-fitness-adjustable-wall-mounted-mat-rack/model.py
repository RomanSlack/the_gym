"""Life Fitness Adjustable Wall-Mounted Mat Rack (refs/: ref_01 the rack: a black square-tube rail, a slotted mounting
foot bolted to the wall at each end, two pegs rising from the rail; ref_02 a mat hung on it: each peg runs out from the
rail and turns up at its end, the mat's grommets on the pegs, the mat hanging flat down the wall). The shop page
refuses requests (HTTP 429): every size is an estimate (the rail 0.90 m, the pegs 0.10 m out); "adjustable": the pegs
slide along the rail to the mats' grommet spacing. Built to the two gates and README point 9. Shown on a display wall
section (not part of the piece), hung with two LF core mats and two yoga mats (the shared equipment/blender/mats.py).

DESIGN SPEC (gate 1)
1. Use. Mats hung off the floor by their grommets: lifted off the pegs and hung back.
2. Each mass named (ref_01 / ref_02): the rail, square tube, on two feet (plates with slots, two bolts each) against the
   wall; two pegs, each a clamp on the rail with a rod out from it turned up at the end.
3. Adjustments. The pegs along the rail (here 0.50 m apart, the mats' grommets).
4. Load path. The mats on the pegs, the clamps, the rail, the feet's bolts into the wall.
5. Fit range. The pegs at 1.95 m: every user (1.55 / 1.78 / 1.95 m) reaches them (the 1.55 m user's reach is about
   2.0 m); the 1.83 m yoga mats hang clear of the floor. No figure.
6. Size. 0.90 x 0.15 x 0.10 m (the rack).
Axes: metres, floor z = 0; the wall's face at y = 0, the rack on it facing -y.
"""
import mats

W_RAIL, Z = 0.90, 1.95
TUBE = 0.04
XP = 0.25                             # the pegs
OUT = 0.11
HUNG = (("black", 1.40, 0.60, 0.015), ("blue", 1.40, 0.60, 0.015), ("yoga", 1.83, 0.61, 0.008), ("yoga", 1.83, 0.61, 0.008))

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "bolt": dict(color=(0.5, 0.5, 0.52), rough=0.3, metal=1.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.8, coat=0.0, spec=0.25, bump=(3000, 0.15)),
    "blue": dict(color=(0.02, 0.10, 0.45), rough=0.8, coat=0.0, spec=0.25, bump=(3000, 0.15)),
    "yoga": dict(color=(0.016, 0.016, 0.017), rough=0.8, coat=0.0, spec=0.25, bump=(4000, 0.2)),
    "grommet": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (-70, 25, 1.0)}
DETAILS = {
    "detail_peg": ((-0.75, -0.75, 2.15), (-0.25, -0.06, 1.93), 35),     # a peg, the grommets on it
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.box("wall", (0, 0.05, 1.4), (1.4, 0.10, 2.8), soft=0.0)                                      # display wall
    k.bar("frame", (-W_RAIL / 2, -TUBE / 2, Z), (W_RAIL / 2, -TUBE / 2, Z), TUBE, TUBE, r=0.003)     # the rail
    for sx in (1, -1):
        x = sx * (W_RAIL / 2 - 0.03)
        k.box("frame", (x, -0.003, Z), (0.06, 0.006, 0.12), soft=0.002)                             # a foot on the wall
        for dz in (0.04, -0.04):
            k.cyl("bolt", (x, -0.0065, Z + dz), 0.007, 0.002, axis="y", seg=16, soft=0.0005)
    y_front = -TUBE
    z_rod = Z + TUBE / 2 - 0.006
    for sx in (1, -1):                                  # the pegs: a clamp on the rail, a rod out and turned up
        x = sx * XP
        k.box("frame", (x, -TUBE / 2, Z), (0.03, TUBE + 0.008, TUBE + 0.008), soft=0.002)
        k.sweep("frame", [(x, y_front - 0.004, z_rod), (x, y_front - OUT, z_rod), (x, y_front - OUT - 0.01, z_rod + 0.05)],
                k.circle(0.005, 12), bend=0.012, soft=0.0)
    y = y_front - 0.006                                 # the mats on the rods, the first against the clamps
    for role, L, W, T in HUNG:
        top = z_rod + 0.045 - 0.001                     # the grommets' top on the rod
        mats.hanging(k, role, "grommet", 0.0, y, top, L, W, T)
        y -= T + 0.002

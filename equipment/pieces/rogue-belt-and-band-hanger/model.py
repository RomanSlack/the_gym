"""Rogue Belt & Band Hanger, the 8 in H-81 (refs/: ref_01 hung with bands and belts; ref_02 empty on a wall: a black
plate with ROGUE cut through, ten flat prongs out of its bottom edge, bent out and up; ref_03 the 5 and 8 in side by
side). The linked page: 23.5 x 4 in, ten 1 in prongs 5 in (H-51) or 8 in (H-81) deep, 11-gauge laser-cut steel,
black, mounting holes 22.5 in apart and 2.5 in apart vertically. Fetched 2026-10-25. The 8 in: deep enough for a
lifting belt (ref_01). Built to the two gates and README point 9. On a display wall section (not the piece).

DESIGN SPEC (gate 1)
1. Use. The loaner wall: belts, bands, straps, wraps hung over the prongs.
2. Each mass named (ref_02): one piece of 11-gauge steel: the plate on the wall with ROGUE cut through and four
   mounting screws at its corners, its bottom edge bent out into ten prongs that turn up at the tips.
3. Adjustments. None.
4. Load path. The kit on the prongs, the plate, its four screws into the wall.
5. Fit range. Mounted at 1.60 m: every user (1.55 / 1.78 / 1.95 m) reaches it, the 1.55 m user at the eyes. No figure.
6. Size. 0.60 x 0.20 x 0.10 m.
Axes: metres, floor z = 0; the wall's face at y = 0, the hanger on it facing -y.
"""
IN = 0.0254
L, HP, T = 23.5 * IN, 4 * IN, 0.003
DEPTH = 8 * IN
Z = 1.60

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15),
    "cut": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
    "bolt": dict(color=(0.45, 0.45, 0.47), rough=0.3, metal=1.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 15, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (-70, 25, 1.0)}
DETAILS = {
    "detail_prongs": ((-0.55, -0.65, 1.85), (0.0, -0.10, 1.55), 35),   # the plate, ROGUE, the prongs
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.box("wall", (0, 0.05, 1.4), (1.2, 0.10, 2.8), soft=0.0)                                      # display wall
    zc = Z + HP / 2
    k.box("frame", (0, -T / 2, zc), (L, T, HP), soft=0.001)                                         # the plate
    k.text("cut", "ROGUE", (0, -T - 0.0002, zc - 0.026), 0.068, depth=0.0006)                       # cut through: the wall
    for sx in (1, -1):
        for dz in (1.25 * IN, -1.25 * IN):
            k.cyl("bolt", (sx * 22.5 * IN / 2, -T - 0.002, zc + dz), 0.007, 0.004, axis="y", seg=16, soft=0.0008)
    pitch = (L - 1 * IN) / 9
    for i in range(10):                                 # the prongs: out of the bottom edge, bent out and up
        x = -L / 2 + 0.5 * IN + pitch * i
        pts = [(x, -T / 2, Z + 0.02), (x, -T / 2, Z), (x, -DEPTH, Z - 0.005), (x, -DEPTH - 0.008, Z + 0.012)]
        k.sweep("frame", pts, k.rect(T, 1 * IN, 0.0008), bend=0.012, up=(1, 0, 0), soft=0.0)

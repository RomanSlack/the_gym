"""Rogue Deadlift Platform, with its eight rubber tiles, lying on the floor.

Built by eye from Rogue's photo (refs/: ref_01, a three-quarter from the front), held to Rogue's spec: 8 ft 4 in x 4 ft
4 in, a 2 x 2 in 11-gauge steel frame, eight 24 x 24 x 1.5 in rubber tiles, extra-long band pegs, a floor clip at each end.
Axes: metres, floor z = 0, the bar along x, the lifter faces -y.
Structure: two long tubes between two end tubes, each joint held by a bent gusset bolted across it on the outside; the
tiles in the frame, a little below its top; the band pegs on upright plates bolted to the long tubes near each end,
reaching in towards the middle; a floor clip bolted to each end tube; ROGUE on the front tube.
"""
IN = 0.0254
LOOK = {
    "rubber": dict(color=(0.035, 0.032, 0.030), rough=0.85, coat=0.0, bump=(1800, 0.14)),   # coarse recycled rubber
    "frame": dict(color=(0.014, 0.014, 0.016), rough=0.45, coat=0.08, bump=(900, 0.06)),     # textured black
    "bolt": dict(color=(0.62, 0.62, 0.64), rough=0.3, metal=1.0, coat=0.0),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 32, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "top": (0, 89, 1.0)}
DETAILS = {"detail_peg": ((-0.55, -1.05, 0.40), (-0.95, -0.62, 0.06), 45)}   # the front-left gusset, peg, floor clip

LX, LY = 100 * IN, 52 * IN
TB = 2 * IN                     # the frame tube
TILE, TT = 24 * IN, 1.5 * IN    # the tiles
PL = 0.0048                     # 3/16 in plate
PEG_X = LX / 2 - 14 * IN        # the band pegs' plates
PEG_L, PEG_R = 14 * IN, 0.5 * IN


def build(k):
    hx, hy = LX / 2, LY / 2
    # the end tubes the full depth, the long tubes between them
    for s in (1, -1):
        k.bar("frame", (s * (hx - TB / 2), -hy, TB / 2), (s * (hx - TB / 2), hy, TB / 2), TB, TB, r=0.004)
        k.bar("frame", (-(hx - TB), s * (hy - TB / 2), TB / 2), (hx - TB, s * (hy - TB / 2), TB / 2), TB, TB, r=0.004)
    # the tiles, 4 x 2, in the frame
    for i in range(4):
        for j in range(2):
            k.sweep("rubber", [((i - 1.5) * TILE, (j - 0.5) * TILE, 0.0), ((i - 1.5) * TILE, (j - 0.5) * TILE, TT)],
                    k.rect(TILE - 0.002, TILE - 0.002, 0.006, 3), soft=0.002)
    for sx in (1, -1):
        for sy in (1, -1):
            yf = sy * (hy + PL / 2)
            # the gusset across the corner joint, two bolts into the long tube, one into the end tube
            k.box("frame", (sx * (hx - 3 * IN), yf, TB / 2), (6 * IN, PL, TB - 0.004), soft=0.001)
            for x in (hx - 5 * IN, hx - 3.5 * IN, hx - 1 * IN):
                k.bolt((sx * x, sy * (hy + PL), TB / 2), ("+y" if sy > 0 else "-y"), size=0.0095, mat="bolt")
            # the band peg: an upright plate bolted to the long tube, the peg welded to it reaching in
            px = sx * PEG_X
            k.box("frame", (px, yf, TB / 2 + 1.5 * IN), (3 * IN, PL, TB + 3 * IN - 0.004), soft=0.001)
            for x in (px - sx * 0.8 * IN, px + sx * 0.8 * IN):
                k.bolt((x, sy * (hy + PL), TB / 2), ("+y" if sy > 0 else "-y"), size=0.0095, mat="bolt")
            yp = sy * (hy + PL + PEG_R)
            zp = TB + 2.2 * IN
            k.tube("frame", (px + sx * 1.5 * IN, yp, zp), (px - sx * PEG_L, yp, zp), PEG_R, seg=24)
            # the floor clip: a bent strap bolted to the end tube's outer face, its foot on the floor with a hole
            yc = sy * (hy - 7 * IN)
            k.box("frame", (sx * (hx + PL / 2), yc, 0.75 * IN), (PL, 1.5 * IN, 1.5 * IN), soft=0.0008)
            k.box("frame", (sx * (hx + 1.25 * IN), yc, PL / 2), (2.5 * IN, 1.5 * IN, PL), soft=0.0008)
            k.cyl("hole", (sx * (hx + 1.6 * IN), yc, PL + 0.0002), 0.0045, 0.0006, seg=16, soft=0.0)
            k.bolt((sx * (hx + PL), yc, 0.9 * IN), ("+x" if sx > 0 else "-x"), size=0.0095, mat="bolt")
    k.text("print", "ROGUE", (0, -hy - 0.0003, TB / 2), 0.026, depth=0.0004)

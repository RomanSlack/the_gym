"""Rogue LB-1 10 in Log Bar (refs/: ref_01 a window and its handle close up, the internal plate, ROGUE cut in the log's
end; ref_02 the LB-3 / LB-1 / LB-2 with Rogue's lengths (80.75 / 77 / 71 in) and weights; ref_03 the LB-1 from the front,
two windows, the small holes). The linked page: the LB-1, a 10 in laser-cut steel tube (1/8 in wall), 77 in overall,
14 in loadable sleeves, neutral handles 1.66 in thick 26 in on centre, ends and internal plates fully welded, 0.375 in
round bar over the openings, 72 lb. Fetched 2026-10-24 / 25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Strongman log clean and press: the lifter faces the log, hands through the windows on the neutral handles,
   rolls it up the thighs to the chest and presses it overhead.
2. Each mass named (ref_01 / ref_03): the log, a 10 in steel tube; a window cut out of its front (facing a little up) on each side, a welded
   internal plate closing each window's inner end and the log's ends, a round bar edging each opening; a neutral handle
   across each window, front to back; the sleeves out of the log's ends; ROGUE cut in the log near each end; the small
   holes. Black.
3. Adjustments. None (plates on the sleeves).
4. Load path. The plates on the sleeves, the end plates, the tube, the internal plates and the handles, the hands.
5. Fit range. The handles 26 in (0.66 m) on centre: about shoulder width for 1.55 / 1.78 / 1.95 m users; the log
   127 mm in radius, so the handles sit 0.13 m out from the chest in the rack.
6. Size. 1.96 m overall, the log 1.25 m x 254 mm.
Axes: metres, floor z = 0, the log along x lying on the floor, its windows toward -y (the lifter).
"""
import math

IN = 0.0254
L = 77 * IN
R = 5 * IN
WALL = 0.004
L_LOG = L - 2 * 14 * IN - 0.02        # between the end plates
X_H = 13 * IN                         # the handles (x): 26 in on centre
WIN = 0.20                            # a window's length along x
WIN_HALF = math.radians(55)           # its half-opening round the front
T_WIN = math.radians(150)             # the opening's middle: to the front (-y, 180 deg) and a little up (ref_03)
ZC = R

LOOK = {
    "black": dict(color=(0.014, 0.014, 0.015), rough=0.6, metal=0.2, coat=0.0, bump=(1400, 0.08)),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
    "sleeve": dict(color=(0.03, 0.03, 0.032), rough=0.4, metal=0.6),
}
VIEWS = {"three_quarter": (-30, 22, 1.2), "front": (0, 8, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.2)}
DETAILS = {
    "detail_window": ((-0.15, -0.55, 0.45), (0.33, -0.05, 0.13), 40),   # ref_01: a window, its handle, ROGUE
}


def ring(k, x0, x1):
    k.disc("black", ((x0 + x1) / 2, 0, ZC), R, R - WALL, x1 - x0, axis="x", seg=128, soft=0.0008)


def shell(k, x0, x1):
    """The log over a window: the tube round its back, open to the front (-y) by +-WIN_HALF."""
    n = 44
    a0, a1 = T_WIN + WIN_HALF, T_WIN + 2 * math.pi - WIN_HALF        # from the opening's edge round the back
    for i in range(n):
        t0, t1 = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n

        def corner(cx, cy, cz, t0=t0, t1=t1):
            t = t1 if cy > 0 else t0
            r = R if cz > 0 else R - WALL
            return (x1 if cx > 0 else x0, r * math.cos(t), ZC + r * math.sin(t))
        k.block("black", corner, soft=0.0)
    for sz in (1, -1):                                  # the round bar along the opening's edges
        t = T_WIN + sz * WIN_HALF
        k.tube("black", (x0, (R - WALL / 2) * math.cos(t), ZC + (R - WALL / 2) * math.sin(t)),
               (x1, (R - WALL / 2) * math.cos(t), ZC + (R - WALL / 2) * math.sin(t)), 0.375 * IN / 2, seg=12)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    e = L_LOG / 2
    xs = [-e, -X_H - WIN / 2, -X_H + WIN / 2, X_H - WIN / 2, X_H + WIN / 2, e]
    ring(k, xs[0], xs[1]); shell(k, xs[1], xs[2]); ring(k, xs[2], xs[3]); shell(k, xs[3], xs[4]); ring(k, xs[4], xs[5])
    for x in (-e, e, -X_H - WIN / 2, -X_H + WIN / 2, X_H - WIN / 2, X_H + WIN / 2):   # the end and internal plates
        k.cyl("black", (x, 0, ZC), R - WALL + 0.0005, 0.0095, axis="x", seg=64, soft=0.0)
    for s in (1, -1):
        k.tube("black", (s * X_H, -(R - WALL - 0.002), ZC), (s * X_H, R - WALL - 0.002, ZC), 1.66 * IN / 2, seg=24)  # handle
        k.tube("sleeve", (s * e, 0, ZC), (s * L / 2, 0, ZC), 0.95 * IN, seg=32)                                      # sleeve
        k.cyl("sleeve", (s * (e + 0.008), 0, ZC), 0.032, 0.012, axis="x", seg=32, soft=0.002)                       # its collar
        for dx in (0.16, 0.30):                         # the small holes either side of the window
            k.disc("hole", (s * (X_H - WIN / 2 - dx) if dx < 0.2 else s * (X_H + WIN / 2 + 0.08), -R - 0.0003, ZC - 0.03),
                   0.012, 0.0, 0.001, axis="y", seg=20, soft=0.0)
        size = 0.058                                    # ROGUE cut round the log near the end (ref_01), letter by letter
        step = size * 0.6 / R
        for i, ch in enumerate("ROGUE"):
            ph = (2 - i) * step + 0.25                  # up round the front
            k.text("hole", ch, (s * (e - 0.09), -(R + 0.0003) * math.cos(ph), ZC + (R + 0.0003) * math.sin(ph)), size,
                   rx=math.pi / 2 - ph, depth=0.0005, spin=-math.pi / 2)

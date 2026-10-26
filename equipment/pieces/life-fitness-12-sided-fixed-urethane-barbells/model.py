"""Life Fitness 12-Sided Fixed Urethane Barbells, the EZ-curl set 10-50 kg (refs/: ref_01 a straight 40; ref_02-04 EZs
20 / 40 / 60: a chrome EZ shaft, at each end a black twelve-sided urethane head, HAMMER STRENGTH over the weight in
white, MADE IN USA small under it). The shop page refuses requests (HTTP 429): the brief asks the EZ set 10-50 kg; the
sizes are ours, as the 4-sided set's (estimates): the EZ 1.15 m, a 28 mm chrome shaft knurled at the grips, the heads
from 150 mm across and 55 mm thick at 10 kg growing with the cube root of the weight. Built to the two gates and
README point 9.

DESIGN SPEC (gate 1)
1. Use. Grab-and-go EZ bars for curls, skull crushers, upright rows: no loading; racked on the barbell rack, set down on
   a flat of the heads (twelve flats: it doesn't roll).
2. Each mass named (ref_02): the EZ shaft, chrome, knurled through its angled grips; at each end a head: a steel core
   in a black urethane shell, twelve-sided, its faces flat, a chrome hub on the inner face; HAMMER STRENGTH, the kilos
   and MADE IN USA in white on the outer face.
3. Adjustments. None: a weight per bar, 10-50 kg in 5 kg steps.
4. Load path. The hands on the knurled grips, the shaft, the heads' cores.
5. Fit range. The EZ's grips angled for curls at about shoulder width for every user (1.55 / 1.78 / 1.95 m). On the
   floor the shaft stands 70-120 mm up: picked up with a hinge.
6. Size. Nine bars in a row on the floor.
Axes: metres, floor z = 0; the bars along x, the lightest at -y.
"""
import math

WEIGHTS = tuple(range(10, 55, 5))
L = 1.15
R_SH = 0.014

LOOK = {
    "chrome": dict(color=(0.82, 0.82, 0.83), rough=0.08, metal=1.0),
    "knurl": dict(color=(0.7, 0.7, 0.71), rough=0.35, metal=1.0, bump=(4000, 0.25)),
    "ure": dict(color=(0.014, 0.014, 0.015), rough=0.45, coat=0.2, spec=0.4),
    "ink": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 28, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "back_three_quarter": (150, 28, 1.0)}
DETAILS = {
    "detail_head": ((-0.95, -0.45, 0.40), (-0.55, -0.10, 0.08), 35),    # ref_02: a head's outer face
}


def size(kg):
    f = (kg / 10) ** (1 / 3)
    return 0.15 * f, 0.055 * f


def head(k, x, s, t, y, zc, kg, sgn):
    """A twelve-sided head at x (its inner face), outward along sgn."""
    R = s / 2 / math.cos(math.pi / 12)                  # s across the flats
    out = [(y + R * math.cos(math.pi / 12 + i * math.pi / 6), zc + R * math.sin(math.pi / 12 + i * math.pi / 6))
           for i in range(12)]
    x0, x1 = (x, x + t) if sgn > 0 else (x - t, x)
    k.slab("ure", out, x0, x1, 0.005)
    xo, xi = (x1, x0) if sgn > 0 else (x0, x1)
    k.disc("chrome", (xi - sgn * 0.0006, y, zc), 0.03, R_SH, 0.0012, axis="x", seg=32, soft=0.0)          # the hub
    rz = sgn * math.pi / 2
    k.text("ink", "HAMMER", (xo + sgn * 0.0003, y, zc + s * 0.27), s * 0.15, rz=rz, depth=0.0006)
    k.text("ink", "STRENGTH", (xo + sgn * 0.0003, y, zc + s * 0.13), s * 0.14, rz=rz, depth=0.0006)
    k.text("ink", str(kg), (xo + sgn * 0.0003, y, zc - s * 0.12), s * 0.30, rz=rz, depth=0.0008)
    k.text("ink", "MADE IN USA", (xo + sgn * 0.0003, y, zc - s * 0.33), s * 0.06, rz=rz, depth=0.0004)


def bar(k, kg, y):
    s, t = size(kg)
    zc = s / 2                                          # lying on a flat of the heads
    xi = L / 2 - t
    pts = [(-xi - 0.01, 0), (-0.34, 0), (-0.27, 0.045), (-0.17, -0.035), (-0.07, 0.0), (0.07, 0.0), (0.17, -0.035),
           (0.27, 0.045), (0.34, 0), (xi + 0.01, 0)]
    k.sweep("knurl", [(x, y + dy, zc) for x, dy in pts], k.circle(R_SH, 16), bend=0.03, soft=0.0)
    for sx in (1, -1):
        head(k, sx * xi, s, t, y, zc, kg, sx)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    y = -0.60
    for kg in WEIGHTS:
        s, _ = size(kg)
        y += s / 2
        bar(k, kg, y)
        y += s / 2 + 0.06

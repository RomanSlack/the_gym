"""Captains of Crush hand grippers (refs/: ref_01 one squeezed in the hand; ref_02 one standing: two knurled aluminium
handles, a ring band round each, the coil of black spring wire at the top with its legs down into the handles). The
linked page: Guide 60 lb, Sport 80, Trainer 100, No. 1 140, No. 1.5 167.5, No. 2 195, No. 2.5 237.5, No. 3 280,
No. 3.5 322.5, No. 4 365; knurled aircraft-grade aluminium handles, GR8 springs; no sizes given: the handles (100 mm,
25 mm across) and coil read off ref_02, estimates. Fetched 2026-10-25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Crushing grip: the gripper in one hand, the handles squeezed shut against the spring.
2. Each mass named (ref_02): two aluminium handles, knurled, a polished ring band round each middle; the spring, black
   wire wound two turns into a coil, its legs running into the handles' ends. The set kept: Guide, Sport, Trainer,
   No. 1, No. 2 (60-195 lb), the wire thicker as they get stronger, lying in a row.
3. Adjustments. None: a gripper per strength.
4. Load path. The fingers and the palm on the handles, the spring's coil.
5. Fit range. The handles 100 mm long in a 1.55-1.95 m user's hand (palm width 75-95 mm): every user. No figure.
6. Size. Each about 0.16 x 0.09 x 0.025 m lying.
Axes: metres, floor z = 0; each lying flat, its coil toward +x, the row along y.
"""
import math

SET = (("GUIDE", 0.0050), ("SPORT", 0.0055), ("TRAINER", 0.0060), ("No.1", 0.0066), ("No.2", 0.0072))
R_H, L_H = 0.0125, 0.100              # the handles
R_C = 0.019                           # the coil
HALF = math.radians(19)               # each handle off the gripper's axis

LOOK = {
    "alu": dict(color=(0.38, 0.38, 0.40), rough=0.6, metal=1.0, bump=(9000, 0.6)),                  # knurled
    "band": dict(color=(0.75, 0.75, 0.77), rough=0.15, metal=1.0),
    "spring": dict(color=(0.02, 0.02, 0.022), rough=0.25, metal=0.8, coat=0.3),
}
VIEWS = {"three_quarter": (-35, 35, 1.0), "front": (0, 20, 1.0), "side": (90, 20, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_coil": ((0.20, -0.25, 0.20), (0.07, -0.10, 0.01), 30),     # a coil, its legs into the handles
}


def gripper(k, y, wire):
    zc = R_H
    # the coil, axis z at x = 0, two turns less a gap, its ends toward -x
    a0, a1 = math.radians(150), math.radians(150 + 690)
    n = 80
    pitch = wire * 0.55                                # the turns wound close (ref_02)
    coil = [(R_C * math.cos(a0 + (a1 - a0) * i / n), y + R_C * math.sin(a0 + (a1 - a0) * i / n),
             wire / 2 + 2 * pitch * i / n) for i in range(n + 1)]          # resting on the floor
    k.sweep("spring", coil, k.circle(wire / 2, 10), soft=0.0)
    for s, end in ((1, coil[0]), (-1, coil[-1])):      # each handle, its leg from the coil into its end
        d = (-math.cos(HALF), s * math.sin(HALF))
        p0 = (-0.040 * math.cos(HALF), y + s * 0.040 * math.sin(HALF))
        k.sweep("spring", [end, (p0[0] + d[0] * 0.012, p0[1] + d[1] * 0.012, zc)], k.circle(wire / 2, 10), soft=0.0)
        a = (p0[0], p0[1], zc)
        b = (p0[0] + d[0] * L_H, p0[1] + d[1] * L_H, zc)
        k.tube("alu", a, b, R_H, seg=28)
        m = 0.45
        k.tube("band", (a[0] + d[0] * L_H * m, a[1] + d[1] * L_H * m, zc), (a[0] + d[0] * L_H * (m + 0.06), a[1] + d[1] * L_H * (m + 0.06), zc),
               R_H + 0.0005, seg=28)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for i, (_, wire) in enumerate(SET):
        gripper(k, -0.24 + i * 0.12, wire)

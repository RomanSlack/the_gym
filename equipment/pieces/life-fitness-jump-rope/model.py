"""Life Fitness Jump Rope (refs/: ref_01-03 blue, grey and red: a PVC cable in loose loops, two black handles, a
swivel cap where the cable goes in, the LifeFitness script in white along each handle). The shop page refuses requests
(HTTP 429): the sizes are estimates (the cable 3 m, 5 mm; the handles 160 mm). The brief's "speed + weighted": the
page sells this one in three colours; these are speed ropes. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Skipping: a handle in each hand, the cable turned overhead and under the feet.
2. Each mass named (ref_01): the cable, PVC, 5 mm; two handles, black, tapering a little to a swivel cap at the
   cable's end; the script along each.
3. Adjustments. The cable's length (cut to the user, here left long).
4. Load path. The hands on the handles, the swivels, the cable.
5. Fit range. 3 m: standing on its middle, the handles reach the armpits of the 1.95 m user (the longest); shortened
   for the others. No figure.
6. Size. Three ropes lying, about 0.45 x 0.35 m each.
Axes: metres, floor z = 0.
"""
import math

ROPES = (("blue", -0.45), ("grey", 0.0), ("red", 0.45))
R_C = 0.0035
L_H, R_H = 0.16, 0.016

LOOK = {
    "blue": dict(color=(0.02, 0.10, 0.50), rough=0.35, coat=0.1),
    "grey": dict(color=(0.30, 0.30, 0.31), rough=0.35, coat=0.1),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.35, coat=0.1),
    "handle": dict(color=(0.008, 0.008, 0.009), rough=0.35, coat=0.0, spec=0.5),
    "cap": dict(color=(0.35, 0.35, 0.37), rough=0.3, metal=1.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 35, 1.0), "front": (0, 25, 1.0), "side": (90, 25, 1.0), "back_three_quarter": (150, 35, 1.0)}
DETAILS = {
    "detail_handle": ((0.30, -0.35, 0.30), (0.10, 0.0, 0.02), 30),      # a handle, its swivel, the script
}


def rope(k, col, x0):
    for i, dx in enumerate((-0.03, 0.03)):              # the handles, lying along y
        x = x0 + 0.16 + dx
        k.cyl("handle", (x, 0.02 + L_H / 2, R_H), R_H, L_H, axis="y", seg=24, soft=0.004, r2=R_H * 0.85)
        k.cyl("handle", (x, 0.02 - 0.012, R_H), R_H * 1.12, 0.026, axis="y", seg=24, soft=0.004)        # the swivel head
        k.cyl("cap", (x, 0.02 - 0.0255, R_H), R_H * 0.6, 0.003, axis="y", seg=20, soft=0.001)
        k.text("white", "LifeFitness", (x, 0.02 + L_H / 2, 2 * R_H - 0.0004), 0.012, rx=0.0, rz=math.pi / 2, depth=0.0004)
    # the cable: from one cap round two loose loops and back into the other
    pts = [(x0 + 0.16 - 0.03, -0.006, R_H)]
    cx, cy = x0 - 0.02, -0.12
    n = 300
    for i in range(n + 1):
        t = 2 * math.pi * 4.25 * i / n                  # a 3 m cable in loose loops (ref_01)
        r = 0.135 - 0.04 * i / n
        pts.append((cx + r * math.cos(t + 0.3), cy + 0.8 * r * math.sin(t + 0.3), R_C + 0.012 * i / n))
    pts.append((x0 + 0.16 + 0.03, -0.006, R_H))
    k.sweep(col, pts, k.circle(R_C, 8), soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for col, x0 in ROPES:
        rope(k, col, x0)

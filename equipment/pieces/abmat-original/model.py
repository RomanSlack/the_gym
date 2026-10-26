"""The Original AbMat (refs/: ref_01 / ref_02 the mat, black vinyl, ROGUE in red along its slope with MADE IN THE U.S.A.
under it; ref_03 its underside, a hook-and-loop panel; ref_04 / ref_05 in use under the lower back). The linked page:
15 x 12 x 2.5 in, low compression-set foam in black vinyl, the Rogue logo red. Fetched 2026-10-25. Built to the two
gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Sit-ups: under the lumbar curve, the thin edge toward the hips, so the back starts the sit-up from below
   parallel.
2. Each mass named (ref_01): one foam wedge in vinyl, its top a convex curve from a thin front edge up to 2.5 in at the
   back, the back end rounded down; ROGUE red along the slope.
3. Adjustments. None.
4. Load path. The lower back on the curve, the foam, the floor.
5. Fit range. 15 in long under the lumbar curve: every user (1.55 / 1.78 / 1.95 m). No figure.
6. Size. 0.38 x 0.30 x 0.064 m.
Axes: metres, floor z = 0; the thin edge toward -y, the 12 in across x.
"""
import math

IN = 0.0254
L, W, T = 15 * IN, 12 * IN, 2.5 * IN

LOOK = {
    "vinyl": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.0, spec=0.4, bump=(1500, 0.03)),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 25, 1.0), "front": (0, 8, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_logo": ((0.25, -0.35, 0.30), (0.0, 0.0, 0.04), 35),        # ROGUE along the slope
}


def top(y):
    """The top's height at y (before the rounded back end)."""
    u = min(max((y + L / 2) / (L * 0.86), 0.0), 1.0)
    return 0.013 + (T - 0.013) * math.sin(math.pi / 2 * u) ** 0.9


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    yb = -L / 2 + L * 0.86                              # where the back end starts rounding down
    rb = T * 0.55
    pts = [(-L / 2 + L * 0.86 * i / 30, top(-L / 2 + L * 0.86 * i / 30)) for i in range(31)]
    for i in range(1, 11):                              # the back rounded over
        a = math.pi / 2 * i / 10
        pts.append((yb + (L / 2 - yb) * math.sin(a), T - rb + rb * math.cos(a)))
    pts += [(L / 2, 0.0), (-L / 2, 0.0)]
    k.slab("vinyl", pts, -W / 2, W / 2, 0.006, seg=4)
    y0 = 0.03                                           # ROGUE along the slope, MADE IN THE U.S.A. under it
    z0 = top(y0) + 0.0004
    for text, x, size in (("ROGUE", 0.075, 0.06), ("MADE IN THE U.S.A.", 0.03, 0.018)):
        k.text("red", text, (x, y0, z0), size, rx=0.0, rz=math.pi / 2, depth=0.0006)
    for v in k.bm("red", 0).verts:                      # laid onto the curve
        v.co.z = top(v.co.y) + 0.0004 + (v.co.z - z0)

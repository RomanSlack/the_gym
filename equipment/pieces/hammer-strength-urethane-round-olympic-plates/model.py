"""Hammer Strength Urethane Round Olympic Plates (refs/: ref_01 the 45 lb face on at an angle: the round urethane rim
cut by four grip windows, the cross between them, HAMMER over the insert and STRENGTH under it, 45 either side, the
steel insert in a black collar; ref_02-ref_14 in use on Hammer Strength racks and plate-loaded machines). The shop page
refused a second request (HTTP 429), so the sizes are ours, read against the 45's 450 mm and the photos: 45 / 35 / 25
/ 10 / 5 / 2.5 lb at 450 / 410 / 345 / 265 / 210 / 165 mm, 60 / 54 / 45 / 34 / 28 / 22 mm thick (estimates). Built to
the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Loaded on 50 mm sleeves and plate horns, carried by the grips, racked on posts; not for dropping.
2. Each mass named (ref_01): a urethane-coated plate: the round rim (rounded, a groove where each spoke meets it), four
   grip windows inside it, the cross of four spokes between the windows carrying the centre; the steel insert (a
   stainless sleeve) in a black collar; the markings raised in grey: HAMMER, STRENGTH, the weight twice. The 5 and
   2.5 lb plain discs (too small for windows).
3. Adjustments. None.
4. Load path. The sleeve on the insert; carried, the fingers through a window round the rim.
5. Fit range. A window's 55 mm across the grip takes any user's four fingers (1.55 / 1.78 / 1.95 m hands); the 45 lb
   is carried at the side by the rim.
6. Size. 450 mm the 45 lb; the six on edge side by side.
Axes: metres, floor z = 0; the plates on edge, faces along x (the front toward -x), the 45 first.
"""
import math

R_INS = 0.0254
# (lb, radius, thickness, windows?)
PLATES = ((45, 0.225, 0.060, True), (35, 0.205, 0.054, True), (25, 0.1725, 0.045, True), (10, 0.1325, 0.034, True),
          (5, 0.105, 0.028, False), (2.5, 0.0825, 0.022, False))
GAP = 0.07

LOOK = {
    "ure": dict(color=(0.014, 0.014, 0.015), rough=0.5, coat=0.15, spec=0.4),                 # black urethane
    "collar": dict(color=(0.02, 0.02, 0.021), rough=0.35, coat=0.3),
    "steel": dict(color=(0.75, 0.75, 0.76), rough=0.18, metal=1.0),
    "groove": dict(color=(0.004, 0.004, 0.004), rough=0.8),
    "ink": dict(color=(0.62, 0.62, 0.63), rough=0.55, coat=0.0),
}
VIEWS = {"three_quarter": (-125, 12, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (55, 14, 1.0)}
DETAILS = {
    "detail_face": ((-0.72, -0.18, 0.30), (0.03, 0.0, 0.225), 34),     # ref_01: the 45 at an angle
}


def plate(k, lb, r, t, windows, x):
    z = r
    s = r / 0.225
    rim_in = r - 0.040 * s
    k.disc("ure", (x, 0, z), r, rim_in, t, axis="x", seg=96, soft=0.008 * s)                       # the rim
    if windows:
        r_c = 0.15 * s                                          # the centre's radius (the cross's body)
        tc = t - 0.008                                          # the centre stands a little in from the rim's faces
        k.disc("ure", (x, 0, z), r_c, R_INS + 0.02, tc, axis="x", seg=64, soft=0.003)
        for i in range(4):                                      # the spokes on the diagonals, the windows between
            th = math.radians(45 + 90 * i)
            half = math.radians(25)                         # the spoke's half-width at the rim: the windows narrow

            def spoke(cr, ct, cx, th=th):
                rr = (rim_in + 0.004) if cr > 0 else (r_c - 0.01)
                a = th + ct * (half if cr > 0 else math.radians(31))
                return (x + cx * tc / 2, rr * math.cos(a), z + rr * math.sin(a))
            k.block("ure", spoke, soft=0.003)
            gy, gz = math.cos(th) * (r - 0.02 * s), math.sin(th) * (r - 0.02 * s)
            for sf in (1, -1):                                  # the groove across the rim's face at the spoke
                k.box("groove", (x + sf * (t / 2 - 0.001), gy, z + gz), (0.003, 0.004, 0.040 * s), rx=th - math.pi / 2,
                      soft=0.0)
    else:
        k.disc("ure", (x, 0, z), rim_in + 0.002, R_INS + 0.02, t - 0.006, axis="x", seg=64, soft=0.003)
    k.disc("collar", (x, 0, z), R_INS + 0.02, R_INS, t + 0.002, axis="x", seg=48, soft=0.002)        # the insert's collar
    k.disc("steel", (x, 0, z), R_INS + 0.006, R_INS, t + 0.004, axis="x", seg=48, soft=0.001)         # the insert
    xt = x - (t - (0.008 if windows else 0.006)) / 2 - 0.0003
    rz = -math.pi / 2
    label = "2.5" if lb == 2.5 else str(lb)
    if windows:
        k.text("ink", "HAMMER", (xt, 0, z + 0.088 * s), 0.064 * s, rz=rz, depth=0.0008)
        k.text("ink", "STRENGTH", (xt, 0, z - 0.088 * s), 0.054 * s, rz=rz, depth=0.0008)
        for sy in (1, -1):
            k.text("ink", label, (xt, sy * 0.082 * s, z), 0.05 * s, rz=rz, depth=0.0008)
    else:                                               # on the face ring between the insert's collar and the rim
        rr = (R_INS + 0.02 + rim_in) / 2
        k.text("ink", label, (xt, 0, z + rr), (rim_in - R_INS - 0.02) * 0.7, rz=rz, depth=0.0006)
        k.text("ink", "LB", (xt, 0, z - rr), (rim_in - R_INS - 0.02) * 0.6, rz=rz, depth=0.0006)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = 0.0
    for lb, r, t, w in PLATES:
        plate(k, lb, r, t, w, x + t / 2)
        x += t + GAP

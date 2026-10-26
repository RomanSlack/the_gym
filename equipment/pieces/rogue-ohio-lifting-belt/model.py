"""Rogue Ohio Lifting Belt (refs/: ref_01 / ref_02 the belt closed standing on a bench: tan leather, 4 in, ROGUE
stamped across the back, the silver single-prong buckle, the keeper loop with ROGUE up it, the tail through it; ref_03
the holes and stitching; ref_04 the buckle end; ref_05 laid out flat). The linked page: 4 in wide, 10 mm (+/- 1 mm),
tan with a silver buckle and brown stitching, single prong, S 21-28 in to XXL 38-45 in, the logo stamped on the loop
and across the back. Fetched 2026-10-25. The M (26-33 in) shown closed on its middle hole. Built to the two gates and
README point 9.

DESIGN SPEC (gate 1)
1. Use. Braced squats, pulls and presses: worn round the waist, cinched, the abdomen braced into it.
2. Each mass named (ref_01 / ref_04): the strap, 4 in x 10 mm vegetable-tanned leather, brown stitching along its
   edges; the buckle, a chrome frame with a single prong, riveted on with its fold; the keeper loop; a row of holes in
   the tail; ROGUE stamped across the back and up the keeper.
3. Adjustments. The hole (the size within the range).
4. Load path. The abdomen and back against the leather, the prong in the hole.
5. Fit range. The sizes S-XXL cover 21-45 in waists: the M fits the 1.78 m user, S and L the others. No figure.
6. Size. Closed, about 0.30 x 0.22 x 0.10 m.
Axes: metres, floor z = 0; the belt standing on its edge, the buckle toward -y.
"""
import math

IN = 0.0254
W, T = 4 * IN, 0.010
RX, RY = 0.15, 0.11                   # the closed belt's half axes (about 30 in round)

LOOK = {
    "leather": dict(color=(0.30, 0.11, 0.025), rough=0.55, coat=0.1, bump=(1800, 0.05)),
    "stitch": dict(color=(0.08, 0.03, 0.008), rough=0.7, coat=0.0),
    "stamp": dict(color=(0.16, 0.05, 0.01), rough=0.6, coat=0.0),
    "chrome": dict(color=(0.82, 0.82, 0.83), rough=0.1, metal=1.0),
    "hole": dict(color=(0.03, 0.012, 0.005), rough=1.0),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_buckle": ((-0.25, -0.45, 0.20), (0.0, -0.10, 0.05), 30),   # the buckle, the keeper, the tail
}


def ell(a, r_off=0.0):
    return ((RX + r_off) * math.sin(a), -(RY + r_off) * math.cos(a))


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zc = W / 2
    # the strap: once round, its tail over the buckle end and out through the keeper
    pts = []
    for i in range(73):
        a = math.radians(20 + 330 * i / 72)            # from just past the buckle round to it again
        x, y = ell(a)
        pts.append((x, y, zc))
    for i in range(1, 13):                              # the tail over the outside, past the buckle and the keeper
        a = math.radians(-10 + 5 * i)
        x, y = ell(a, T + 0.001)
        pts.append((x, y, zc))
    k.sweep("leather", pts, k.rect(T, W, 0.002), up=(0, 0, 1), soft=0.0)
    for dz in (W / 2 - 0.006, -W / 2 + 0.006):          # the stitching along both edges
        k.sweep("stitch", [(p[0], p[1], zc + dz) for p in pts[2:70]], k.rect(T + 0.0016, 0.0016, 0.0003),
                up=(0, 0, 1), soft=0.0)
    # the buckle: a chrome frame on the strap's end at 20 deg, its prong through the tail
    a = math.radians(12)
    bx, by = ell(a, 1.5 * T + 0.0045)                   # over the tail's outside
    tx, ty = math.cos(a) * RX, math.sin(a) * RY         # along the belt there
    tn = math.hypot(tx, ty)
    tx, ty = tx / tn, ty / tn
    frame = [(bx + dx * tx, by + dx * ty, zc + dz) for dx, dz in
             ((-0.02, -W / 2 - 0.007), (0.02, -W / 2 - 0.007), (0.02, W / 2 + 0.007), (-0.02, W / 2 + 0.007),
              (-0.02, -W / 2 - 0.007))]
    k.sweep("chrome", frame, k.circle(0.0042, 10), bend=0.006, soft=0.0)
    k.tube("chrome", (bx - 0.02 * tx, by - 0.02 * ty, zc), (bx + 0.018 * tx, by + 0.018 * ty, zc), 0.0032, seg=10)  # prong
    ak = math.radians(32)                               # the keeper loop past the buckle, ROGUE up it
    kx, ky = ell(ak, T + 0.002)
    rk = math.atan2(math.cos(ak) * RY, math.sin(ak) * 0 + math.cos(ak) * RX) * 0 + ak * 0.9
    k.box("leather", (kx, ky, zc), (0.032, 2 * T + 0.008, W + 0.008), rz=rk, soft=0.003)
    ox, oy = ell(ak, 2 * T + 0.0065)
    k.text("stamp", "ROGUE", (ox, oy, zc), 0.012, rz=rk, spin=math.pi / 2, depth=0.0008)
    x, y = ell(math.pi, 0.0004)                         # ROGUE across the back, outside
    k.text("stamp", "ROGUE", (x, y + T / 2 + 0.0002, zc - 0.004), 0.040, rz=math.pi, depth=0.0008)
    for i in range(4):                                  # the holes in the tail, short of the buckle
        a = math.radians(-7 + 3.6 * i)
        hx, hy = ell(a, 1.5 * T + 0.001)
        k.cyl("hole", (hx, hy, zc), 0.004, 0.004, axis="y", seg=12, soft=0.0)

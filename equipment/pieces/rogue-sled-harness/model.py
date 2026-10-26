"""Rogue Sled Harness, with its pull strap (refs/: ref_01 / ref_03 / ref_04 worn: the two shoulder straps in a V to the
chest, a box-X tab where they meet, the belt round the ribs with the white ROGUE on its buckle plate, the O-ring under
it where the strap clips; ref_02 laid flat with the pull strap beside it, a snap hook at each end and a ROGUE tag;
ref_05 the back's anchor). The linked page: one size (adult S to 4XL), 3 in webbing shoulders, a 1.5 in belt with
padded rib guards, a lined back panel, steel belt fasteners and anchors front and back, a 9 ft nylon pull strap, two
2000 lb connectors. Fetched 2026-10-25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Sled drags and pulls: the vest on, the belt cinched round the ribs, the strap clipped to the front or back
   anchor and to the sled; the lifter walks or sprints away from the sled, or faces it and pulls hand over hand.
2. Each mass named (ref_02): the two 3 in shoulder straps in a V, a lined panel between them at the back, the box-X tab
   where they meet; the 1.5 in belt across, a padded rib guard each side, its tails hanging, the buckle plate with
   ROGUE in the middle; the O-ring under it (the front anchor); the 9 ft pull strap coiled beside, a snap hook each end
   and its ROGUE tag. Black.
3. Adjustments. The belt and the shoulder straps through their rings: one size, S to 4XL.
4. Load path. The sled, the strap, the anchor, the belt and shoulder straps, the ribs and shoulders.
5. Fit range. Adult S to 4XL by its straps: every user (1.55 / 1.78 / 1.95 m) wears it. Laid flat as ref_02, no figure.
6. Size. The vest about 0.64 x 0.80 m laid flat; the strap 2.74 m.
Axes: metres, floor z = 0; laid flat, the belt along x, the shoulders toward +y; the strap coiled at +x.
"""
import math

IN = 0.0254
T = 0.004                             # the webbing's thickness

LOOK = {
    "web": dict(color=(0.008, 0.008, 0.009), rough=0.95, coat=0.0, spec=0.15, bump=(3000, 0.12)),
    "pad": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, spec=0.2, bump=(1800, 0.08)),
    "lining": dict(color=(0.007, 0.007, 0.008), rough=0.8, coat=0.0, spec=0.2, bump=(2400, 0.05)),
    "steel": dict(color=(0.5, 0.5, 0.52), rough=0.3, metal=1.0),
    "white": dict(color=(0.85, 0.85, 0.86), rough=0.5),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 60, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_belt": ((0.0, -0.55, 0.45), (0.0, -0.05, 0.0), 35),        # the buckle plate, ROGUE, the O-ring
}


def strap(k, mat, pts, w, z=T / 2):
    k.sweep(mat, [(x, y, z) for x, y in pts], k.rect(w, T, 0.001), up=(0, 0, 1), soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    W = 3 * IN
    for s in (1, -1):                                   # the shoulder straps, a V from the shoulders to the chest
        strap(k, "web", [(s * 0.21, 0.52), (s * 0.18, 0.36), (s * 0.10, 0.0)], W, z=T * 1.5)
    k.block("lining", lambda cx, cy, cz: (cx * (0.20 if cy > 0 else 0.13), 0.30 if cy > 0 else 0.0, T if cz > 0 else 0.0),
            soft=0.0008)                                                                            # the back panel
    k.box("web", (0, 0.06, T * 1.5), (0.045, 0.09, T), soft=0.0008)                                 # the box-X tab
    for s in (1, -1):
        k.box("white", (0, 0.07, T * 2 + 0.0003), (0.003, 0.05, 0.0006), rz=s * 0.45, soft=0.0)    # its X stitching
    yb = -0.04
    strap(k, "web", [(-0.30, yb), (0.30, yb)], 1.5 * IN, z=T * 2.5)                                 # the belt
    for s in (1, -1):
        k.box("pad", (s * 0.22, yb, 0.012), (0.20, 0.12, 0.022), soft=0.007)                        # a rib guard
        k.cyl("steel", (s * 0.11, yb, T * 3), 0.016, 0.004, seg=24, soft=0.001)                     # a sleeve ring
    strap(k, "web", [(0.10, yb - 0.02), (0.13, -0.20), (0.16, -0.40)], 1.5 * IN)                    # a tail hanging
    strap(k, "web", [(-0.30, yb), (-0.36, yb - 0.01)], 1.5 * IN)
    k.box("web", (0, yb, T * 3.2), (0.13, 0.045, T * 1.2), soft=0.002)                              # the buckle plate
    k.text("white", "ROGUE", (0, yb, T * 3.9), 0.026, rx=0.0, depth=0.0005)
    ring = [(0.03 * math.cos(t), yb - 0.075 + 0.03 * math.sin(t), 0.005) for t in [2 * math.pi * i / 32 for i in range(33)]]
    k.sweep("steel", ring, k.circle(0.005, 10), soft=0.0)                                           # the O-ring
    strap(k, "web", [(0, yb - 0.02), (0, yb - 0.05)], 0.025)
    # the 9 ft pull strap coiled beside it, a snap hook each end
    xc, yc = 0.62, 0.22
    path = []
    for i in range(65):                                 # two turns, each laid a little inside and over the last
        t = math.pi / 2 + 4 * math.pi * i / 64
        f = 1.0 - 0.18 * i / 64
        path.append((xc + 0.11 * f * math.cos(t), yc + 0.22 * f * math.sin(t), T / 2 + 0.0045 * i / 64))
    h0 = (xc + 0.03, 0.50)
    k.sweep("web", [(h0[0], h0[1], T / 2)] + path[:1], k.rect(1.0 * IN, T, 0.001), up=(0, 0, 1), soft=0.0)
    k.sweep("web", path, k.rect(1.0 * IN, T, 0.001), up=(0, 0, 1), soft=0.0)
    h1 = (xc + 0.24, -0.30)
    k.sweep("web", [path[-1], (path[-1][0] + 0.02, path[-1][1] - 0.15, T / 2), (h1[0], h1[1], T / 2)],
            k.rect(1.0 * IN, T, 0.001), bend=0.06, up=(0, 0, 1), soft=0.0)
    k.box("web", (xc + 0.18, -0.22, T * 1.5), (0.036, 0.14, T), rz=0.65, soft=0.001)                 # its ROGUE tag
    k.text("white", "ROGUE", (xc + 0.18, -0.22, T * 2.1), 0.026, rx=0.0, rz=0.65 + math.pi / 2, depth=0.0004)
    for (x0, y0), ang in ((h0, math.pi / 2 - 0.3), (h1, -0.9)):        # the snap hooks
        c, sn = math.cos(ang), math.sin(ang)
        hook = [(x0 + c * (0.055 + 0.05 * math.cos(t)) - sn * 0.025 * math.sin(t),
                 y0 + sn * (0.055 + 0.05 * math.cos(t)) + c * 0.025 * math.sin(t), 0.005)
                for t in [2 * math.pi * i / 32 for i in range(33)]]
        k.sweep("steel", hook, k.circle(0.005, 10), soft=0.0)

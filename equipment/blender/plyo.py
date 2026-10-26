"""The Hammer Strength 3-in-1 plyo box, shared by the soft and the wood one: a box 50 x 76 x 60 cm standing on its
50 x 76 face (60 up), each face printed with the height it gives when it is the top: 60 cm / 24 in on the long sides,
76 / 30 on the ends, 50 / 20 on the top and bottom; a scale of ticks down one vertical edge of each side; HAMMER
STRENGTH low on the ends."""
import math

CM = 0.01
X, Y, Z = 50 * CM, 76 * CM, 60 * CM   # across, long, up


def ticks(k, mat, x0, y0, z0, z1, n, face):
    """A scale of ticks up a vertical edge. face = 'x' (on a face whose normal is -x) or 'y' (normal -y)."""
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        L = 0.045 if i % 5 == 0 else 0.028
        if face == "x":
            k.box(mat, (x0, y0 + L / 2, z), (0.0008, L, 0.004), soft=0.0)
        else:
            k.box(mat, (x0 - L / 2, y0, z), (L, 0.0008, 0.004), soft=0.0)


def box(k, body, print_, soft, inset=None, logo=None, holes=None):
    """The box at the origin, its ends facing +-y, its long sides +-x. body / print_ / inset / logo / holes: roles."""
    k.box(body, (0, 0, Z / 2), (X, Y, Z), soft=soft)
    e = 0.0004
    # the -x side (76 x 60): 60 / 24 at its top corner, the ticks down the edge
    k.text(print_, "60", (-X / 2 - e, -Y / 2 + 0.08, Z - 0.065), 0.075, rz=-math.pi / 2, depth=0.0006)
    k.text(print_, "24", (-X / 2 - e, -Y / 2 + 0.08, Z - 0.145), 0.075, rz=-math.pi / 2, depth=0.0006)
    ticks(k, print_, -X / 2 - e, -Y / 2 + 0.015, 0.04, Z - 0.20, 16, "x")
    # the -y end (50 x 60): 76 / 30, its ticks, HAMMER STRENGTH low
    k.text(print_, "76", (X / 2 - 0.08, -Y / 2 - e, Z - 0.065), 0.075, depth=0.0006)
    k.text(print_, "30", (X / 2 - 0.08, -Y / 2 - e, Z - 0.145), 0.075, depth=0.0006)
    ticks(k, print_, X / 2 - 0.015, -Y / 2 - e, 0.04, Z - 0.20, 16, "y")
    k.text(print_, "HAMMER", (-X / 2 + 0.10, -Y / 2 - e, 0.10), 0.042, depth=0.0006)
    k.text(print_, "STRENGTH", (-X / 2 + 0.115, -Y / 2 - e, 0.06), 0.042, depth=0.0006)
    # the top (50 x 76): 50 / 20 along its edge
    k.text(print_, "50  20", (X / 2 - 0.06, 0.0, Z + e), 0.06, rx=0.0, rz=math.pi / 2, depth=0.0006)
    if inset:                                           # the grip panels on each face (the soft box)
        k.box(inset, (-X / 2 - e / 2, 0.04, Z / 2 + 0.02), (0.0006, Y - 0.24, Z - 0.20), soft=0.0)   # clear of the print
        k.box(inset, (-0.04, -Y / 2 - e / 2, Z / 2 + 0.035), (X - 0.20, 0.0006, Z - 0.21), soft=0.0)
        k.box(inset, (0.0, 0.0, Z + e), (X - 0.12, Y - 0.16, 0.0012), soft=0.0)
        k.box(inset, (X / 2 + e, 0.0, Z / 2), (0.0012, Y - 0.20, Z - 0.16), soft=0.0)
        k.box(inset, (0.0, Y / 2 + e, Z / 2), (X - 0.14, 0.0012, Z - 0.16), soft=0.0)
    if logo:                                            # the yellow triangle
        c = (X / 2 - 0.05, -Y / 2 - e * 2, 0.12)
        k.block(logo, lambda cx, cy, cz: (c[0] + (cx * 0.016 if cz < 0 else 0.0), c[1] + cy * 0.0006,
                                          c[2] + (-0.012 if cz < 0 else 0.016)), soft=0.0)
    if holes:                                           # the hand holes through each face (the wood box)
        r = 0.018
        for c, ax in (((-X / 2 - e, 0.0, Z - 0.11), "x"), ((X / 2 + e, 0.0, Z - 0.11), "x"),
                      ((0.0, -Y / 2 - e, Z - 0.11), "y"), ((0.0, Y / 2 + e, Z - 0.11), "y")):
            for s in (1, -1):
                d = (0.0, s * 0.035, 0.0) if ax == "x" else (s * 0.035, 0.0, 0.0)
                k.cyl(holes, (c[0] + d[0], c[1] + d[1], c[2]), r, 0.0012, axis=ax, seg=20, soft=0.0)
            sz = (0.0012, 0.07, 2 * r) if ax == "x" else (0.07, 0.0012, 2 * r)
            k.box(holes, c, sz, soft=0.0)

"""Rogue Monster Mass Storage, 43 in wide, 100 in tall (refs/: ref_01 the 4-shelf unit loaded with blue and red bumpers
and medicine balls, the configurator's image; the numbers from the linked page: 100.5 in tall, 43 in shelves, 49 in
overall, 20 in front to back over the uprights, 31 in base, bumper / medball shelves of two 2 x 2 x 1/8 in rails 11 in
on centre between 3/8 in end plates, 3 x 3 in 11-gauge uprights, 1 in hardware, 3 x 3 in rubber feet, two bolt-on
ROGUE plates). Fetched 2026-10-24 / 25 off the linked page. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. A tall shelf unit for the heavy loose gear: bumpers on edge across each shelf's two rails, medicine balls in
   the same cradle, lifted on and off from the front.
2. Each mass named (ref_01): two end frames, each a front and a back 3 x 3 in upright on a 31 in base foot (its ends
   sloped, a rubber foot under each), tied by two crossmembers at the top and one low; four bumper / medball shelves
   between the end frames (ref_01's heights, read at 284 px/m: 0.39 / 0.93 / 1.49 / 2.00 m), each two 2 x 2 in rails
   11 in apart welded to 3/8 in end plates bolted to the uprights' inner faces; the two ROGUE plates up the front
   uprights. Loaded as ref_01: on each of the lower three shelves a medicine ball at the left, then blue 45 lb and red
   55 lb bumpers; three medicine balls on the top. Colour: Roman's for the Rogue storage (2026-10-25): the uprights
   red, the rest black (ref_01 is all black).
3. Adjustments. Each shelf by the hole (2 in steps).
4. Load path. A plate's rim across the two rails, the end plates, their bolts, the uprights, the base feet, the floor.
5. Fit range. The shelves at 0.39 / 0.93 / 1.49 / 2.00 m: a bumper's hub at 0.57 / 1.11 / 1.67 / -: from mid-shin to
   head height; the 1.55 m user lifts a bumper off the third shelf at the face, and reaches the top shelf's balls only
   on tiptoe (their tops 2.35 m): keep the light balls up there, as ref_01 does.
6. Size. 1.24 x 0.79 x 2.55 m (49 x 31 x 100.5 in).
Axes: metres, floor z = 0; the shelves along x, the front at -y.
"""
import math

IN = 0.0254
TB = 3 * IN
XU = (43 / 2 + 1.5) * IN              # the uprights' centres (x): 43 in between their inner faces
YU = (20 / 2 - 1.5) * IN              # and (y): 20 in over their outer faces
H = 100.5 * IN
Z_FOOT = 3 * IN                       # the base feet's top
SHELVES = (0.39, 0.93, 1.49, 2.00)    # the rails' tops (ref_01)
Y_RAIL = 5.5 * IN                     # 11 in on centre
RW = 2 * IN
PT = 0.375 * IN
R_BALL = 0.17                         # a medicine ball (14 in)
# a lower shelf's load, left to right: (look, label, radius, thickness, count)
LOAD = (("p_blue", "45", 0.225, 0.040, 8), ("p_red", "55", 0.225, 0.040, 9))

LOOK = {
    "frame": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),        # Rogue red (Roman)
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.25, coat=0.35, bump=(900, 0.05)),        # medium gloss black
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "stainless": dict(color=(0.75, 0.75, 0.76), rough=0.18, metal=1.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0),
    "p_blue": dict(color=(0.03, 0.10, 0.55), rough=0.5, coat=0.1),
    "p_red": dict(color=(0.50, 0.03, 0.03), rough=0.5, coat=0.1),
    "ball": dict(color=(0.02, 0.02, 0.022), rough=0.7, coat=0.0, bump=(1800, 0.1)),
    "ink": dict(color=(0.85, 0.85, 0.86), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (150, 16, 1.0),
         "ref_view": (-38, 8, 1.0)}                   # ref_01: from the front left
DETAILS = {
    "detail_shelf": ((-0.75, -0.95, 1.30), (-0.45, 0.0, 1.05), 40),     # a shelf's end plate, its rails, a medball
    "detail_foot": ((-0.95, -0.95, 0.45), (-0.62, 0.0, 0.10), 40),      # a base foot, a rubber foot, the low tie
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    frames(k)
    shelves(k)
    load(k)


def holes(k, x, y, z0, z1, face):
    ax, sg = face[1], (1 if face[0] == "+" else -1)
    z = z0
    while z <= z1:
        c = (x + sg * (TB / 2 + 0.0003), y, z) if ax == "x" else (x, y + sg * (TB / 2 + 0.0003), z)
        k.cyl("hole", c, 0.5 * IN, 0.0008, axis=ax, seg=14, soft=0.0)
        z += 2 * IN


def frames(k):
    """Each end: the base foot (31 in, its ends sloped), the two uprights on it, the crossmembers, the ROGUE plate."""
    L = 31 * IN / 2
    for sx in (1, -1):
        x = sx * XU

        for sy in (1, -1):                                         # the foot in two halves, each sloped at its end
            def half(cx, cy, cz, sy=sy, x=x):
                y = sy * (YU + TB / 2 + 0.03) if cy * sy < 0 else sy * L
                zt = Z_FOOT if cy * sy < 0 else Z_FOOT * 0.45
                return (x + cx * TB / 2, y, zt if cz > 0 else 0.012)
            k.block("black", half, soft=0.003)
            k.box("rubber", (x, sy * (L - 1.5 * IN), 0.006), (TB, TB, 0.012), soft=0.002)        # its rubber foot
        k.box("black", (x, 0.0, (Z_FOOT + 0.012) / 2), (TB, 2 * (YU + TB / 2 + 0.03), Z_FOOT - 0.012), soft=0.003)
        for sy in (1, -1):
            y = sy * YU
            k.bar("frame", (x, y, Z_FOOT), (x, y, H), TB, TB, r=0.004)
            for face in ("+x", "-x", "+y", "-y"):
                holes(k, x, y, Z_FOOT + 3 * IN, H - 3 * IN, face)
            k.bolt((x + sx * TB / 2, y, Z_FOOT + 1.5 * IN), "+x" if sx > 0 else "-x", size=0.025)
        for z in (H - 2.5 * IN, H - 9 * IN, Z_FOOT + 7 * IN):      # the end frame's ties
            k.bar("black", (x, -YU + TB / 2, z), (x, YU - TB / 2, z), TB, TB, r=0.004)
            for sy in (1, -1):
                k.bolt((x, sy * (YU + TB / 2), z), "+y" if sy > 0 else "-y", size=0.025)
        # the ROGUE plate up the front upright's front face, on its stainless backer
        y = -YU - TB / 2
        k.box("stainless", (x, y - 0.001, H - 0.36), (TB - 0.012, 0.002, 0.32), soft=0.0005)
        k.box("black", (x, y - 0.0035, H - 0.36), (TB - 0.02, 0.003, 0.30), soft=0.0005)
        k.text("stainless", "ROGUE", (x, y - 0.0053, H - 0.36), 0.045, depth=0.0006, spin=math.pi / 2)


def shelves(k):
    """Each shelf: an end plate on each end frame's inner faces, the two rails between them."""
    for z in SHELVES:
        zr = z - RW / 2
        for sx in (1, -1):
            xp = sx * (XU - TB / 2 - PT / 2)
            k.box("black", (xp, 0.0, zr - 0.01), (PT, 2 * YU + TB, 4 * IN), soft=0.002)
            for sy in (1, -1):
                k.bolt((sx * (XU + TB / 2), sy * YU, zr - 0.01), "+x" if sx > 0 else "-x", size=0.025)
        for sy in (1, -1):
            k.bar("black", (-(XU - TB / 2 - PT), sy * Y_RAIL, zr), (XU - TB / 2 - PT, sy * Y_RAIL, zr), RW, RW, r=0.003)


def _plate(k, look, lb, x, z, r, t):
    k.disc(look, (x, 0.0, z), r, 0.0255, t, axis="x", seg=72)
    k.disc("steel", (x, 0.0, z), 0.045, 0.0255, t + 0.002, axis="x", seg=32)


def _ball(k, x, z, r, kg):
    k.sphere("ball", (x, 0.0, z), r, seg=48)
    k.text("ink", "ROGUE", (x, -r - 0.0004, z + 0.03), 0.06, depth=0.0006)
    k.text("ink", str(kg), (x, -r * 0.94 - 0.0004, z - 0.06), 0.035, depth=0.0006)


def load(k):
    x_in = XU - TB / 2 - PT
    zb = lambda z, r: z + math.sqrt(r ** 2 - Y_RAIL ** 2) - 0.003        # a round thing's centre over the rails
    for z in SHELVES[:3]:
        x = -x_in + 0.005
        _ball(k, x + R_BALL, zb(z, R_BALL), R_BALL, 20)
        x += 2 * R_BALL + 0.01
        for look, lb, r, t, n in LOAD:
            for i in range(n):
                _plate(k, look, lb, x + t / 2, zb(z, r), r, t)
                x += t + 0.001
        k.text("ink", "ROGUE", (-x_in + 2 * R_BALL + 0.015 - 0.0004, 0.0, zb(z, 0.225) + 0.13), 0.06,
               rz=-math.pi / 2, depth=0.0006)
    for i, kg in enumerate((14, 20, 25)):                                  # the top shelf: three balls
        _ball(k, -x_in + 0.02 + R_BALL + i * (2 * R_BALL + 0.03), zb(SHELVES[3], R_BALL), R_BALL, kg)

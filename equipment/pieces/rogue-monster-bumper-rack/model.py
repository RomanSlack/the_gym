"""Rogue Monster Bumper Rack (refs/: ref_01 / ref_05 loaded with Rogue's colour training bumpers, kettlebells and mats
on the shelf; ref_03 the empty rack with Rogue's dimensions: 44 x 23.5 in, 24.375 in to the top rails, 31.625 in to the
dividers' tops; ref_02 the ROGUE cut into the front shelf rail; ref_04 a divider's legs in the rail's holes). Fetched
2026-10-24 off the linked page. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Bumper plates stand on edge in a row along the top, sorted into bays by the dividers, rolled on and lifted off
   from either side; the shelf below holds anything (kettlebells, mats: other pieces, not drawn).
2. Each mass named (ref_03): four short 3 x 3 in Monster uprights, holes up every face, each on a base plate reaching
   out front and back; an end crossmember across each end's top and low down; the top rails
   along the front and back, leg top to leg top; the two plate rails set in under the end crossmembers so a plate's
   rim rests across both and its lower half stands down behind the top rails (ref_01: the hub 0.20 m over them); five stainless
   U dividers across the depth, their legs down through the rails' holes (ref_04); the low front and back rails, the
   ROGUE cut through the front one (ref_02), the black steel shelf between them. Loaded as ref_01: Rogue's training
   bumpers, black with the colour band round each face and the colour lettering: green 25, yellow 35, blue 45, red
   55 lb. Colour: Roman's for the Rogue storage (2026-10-25): the uprights red, the rest black (ref_01 is all black).
3. Adjustments. The dividers by the hole along the rails.
4. Load path. The plates' rims on the plate rails, the end crossmembers, the uprights, the base plates.
5. Fit range. A plate's hub at 0.74 m: the 1.55 m user's hip, the 1.95 m user's knuckles; a plate rolls off the rails
   onto the floor or lifts off at the waist, no reach overhead. No figure: nothing on it is held or sat on.
6. Size. 1.12 x 0.60 x 0.80 m (44 x 23.5 x 31.625 in); loaded, the plates' tops at 0.96 m.
Axes: metres, floor z = 0; the length along x, the front (the ROGUE rail) at -y.
"""
import math

IN = 0.0254
TB = 3 * IN
XL = 22 * IN - TB / 2                 # the uprights' centres (x): 44 in over their outer faces
YL = 23.5 / 2 * IN - 2.5 * IN         # and (y): the base plates reach 2.5 in past them
Z_TOP = 24.375 * IN                   # the top rails' top
Z_DIV = 31.625 * IN                   # the dividers' tops
Y_RAIL = 0.11                         # the top rails' centres (y), set in from the legs
RW = 2 * IN                           # the rails: 2 x 2 in
X_DIV = tuple(-0.42 + 0.21 * i for i in range(5))
Z_LOW = 4 * IN                        # the low rails' centre
PL = 0.0048
# the plates in each bay (look, label, lb, radius, thickness, count), left to right (ref_01)
LOAD = (("c_green", "25", 0.225, 0.045, 3), ("c_yellow", "35", 0.225, 0.054, 3), ("c_blue", "45", 0.225, 0.062, 3),
        ("c_red", "55", 0.225, 0.075, 2))

LOOK = {
    "frame": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),        # Rogue red (Roman)
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "stainless": dict(color=(0.75, 0.75, 0.76), rough=0.18, metal=1.0, aniso=0.3),
    "rubber": dict(color=(0.015, 0.015, 0.016), rough=0.55, coat=0.1, spec=0.35),              # the bumpers' black
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0),
    "c_green": dict(color=(0.05, 0.45, 0.04), rough=0.5, coat=0.1),
    "c_yellow": dict(color=(0.75, 0.55, 0.03), rough=0.5, coat=0.1),
    "c_blue": dict(color=(0.03, 0.12, 0.6), rough=0.5, coat=0.1),
    "c_red": dict(color=(0.45, 0.04, 0.03), rough=0.5, coat=0.1),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0),
         "ref_view": (-30, 12, 1.0)}                  # ref_01 / ref_03: from the front left, a little high
DETAILS = {
    "detail_divider": ((-0.55, -0.75, 1.15), (-0.20, 0.0, 0.70), 40),   # a divider, the rails, a plate's band
    "detail_shelf": ((-0.35, -0.95, 0.40), (0.0, -0.20, 0.12), 40),     # the ROGUE rail, the shelf, a base plate
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    frame(k)
    plates(k)


def holes(k, x, y, z0, z1, face):
    ax, sg = face[1], (1 if face[0] == "+" else -1)
    z = z0
    while z <= z1:
        c = (x + sg * (TB / 2 + 0.0003), y, z) if ax == "x" else (x, y + sg * (TB / 2 + 0.0003), z)
        k.cyl("hole", c, 0.5 * IN, 0.0008, axis=ax, seg=14, soft=0.0)
        z += 2 * IN


def frame(k):
    bp = 0.0095
    zc = Z_TOP - TB / 2                                   # the top end crossmembers' centre
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * XL, sy * YL
            k.box("frame", (x, y + sy * 1.25 * IN, bp / 2), (4 * IN, 7.5 * IN, bp), soft=0.0015)   # the base plate
            for dy in (-1.5 * IN, 3.8 * IN):
                k.bolt((x, y + sy * dy, bp), "+z", size=0.014)
            k.bar("frame", (x, y, bp), (x, y, Z_TOP), TB, TB, r=0.004)
            for face in ("+x", "-x", "+y", "-y"):
                holes(k, x, y, 3 * IN, Z_TOP - 2 * IN, face)
        # the end crossmembers, top and low, between the front and back uprights, bolted through
        for z in (zc, Z_LOW):
            k.bar("black", (sx * XL, -YL + TB / 2, z), (sx * XL, YL - TB / 2, z), TB, TB, r=0.004)
            for sy in (1, -1):
                k.bolt((sx * XL, sy * (YL + TB / 2), z), "+y" if sy > 0 else "-y", size=0.022, nut=None)
    # the top rails along the front and back, leg top to leg top (ref_03), holes along their faces
    for sy in (1, -1):
        y = sy * YL
        k.bar("black", (-XL + TB / 2, y, zc), (XL - TB / 2, y, zc), TB, TB, r=0.004)
        for i in range(9):
            k.cyl("hole", (-0.40 + i * 0.10, y + sy * (TB / 2 + 0.0003), zc), 0.5 * IN, 0.0008, axis="y", seg=14, soft=0.0)
    # the plate rails, set in under the end crossmembers, holes along their tops (ref_04): the plates' rims rest
    # across them, their lower halves down behind the top rails (ref_01)
    zr = Z_TOP - TB - RW / 2
    for sy in (1, -1):
        y = sy * Y_RAIL
        k.bar("black", (-XL + TB / 2, y, zr), (XL - TB / 2, y, zr), RW, RW, r=0.003)
        for i in range(19):
            k.cyl("hole", (-0.45 + i * 0.05, y, zr + RW / 2 + 0.0003), 0.35 * IN, 0.0008, seg=14, soft=0.0)
    # the dividers: stainless U's across the depth, the legs down through the rails
    for x in X_DIV:
        r = 0.006
        zb = Z_TOP - TB - RW - 0.012
        pts = [(x, -Y_RAIL, zb), (x, -Y_RAIL, Z_DIV - 0.03), (x, -Y_RAIL + 0.03, Z_DIV), (x, Y_RAIL - 0.03, Z_DIV),
               (x, Y_RAIL, Z_DIV - 0.03), (x, Y_RAIL, zb)]
        k.sweep("stainless", pts, k.circle(r, 12), bend=0.025, soft=0.0)
    # the low rails along the length, the ROGUE cut through the front one, the shelf between
    for sy in (1, -1):
        y = sy * (YL - TB / 2 - 0.5 * IN)
        k.bar("black", (-XL + TB / 2, y, Z_LOW), (XL - TB / 2, y, Z_LOW), 1 * IN, TB, r=0.002)
    yf = -(YL - TB / 2 - 0.5 * IN) - 0.5 * IN
    k.text("hole", "ROGUE", (0.0, yf - 0.0003, Z_LOW), 1.6 * IN, depth=0.0006)
    k.box("black", (0.0, 0.0, Z_LOW + TB / 2 + 0.0015), (2 * XL - TB, 2 * YL - TB - 2 * IN, 0.003), soft=0.001)


def plates(k):
    """The bumpers on edge between the dividers, resting across the two top rails (ref_01)."""
    zc = Z_TOP - TB + math.sqrt(0.225 ** 2 - Y_RAIL ** 2) - 0.004  # the hub: the rim sits on the plate rails' tops
    for b, (look, lb, r, t, n) in enumerate(LOAD):
        x0 = X_DIV[b] + 0.01
        for i in range(n):
            x = x0 + t / 2 + i * (t + 0.003)
            k.disc("rubber", (x, 0.0, zc), r, 0.0255, t, axis="x", seg=72)
            k.disc(look, (x, 0.0, zc), r + 0.0006, r - 0.002, t * 0.35, axis="x", seg=72)          # the rim's band
            for s in (1, -1):                                       # the colour band round each face, the lettering
                xf = x + s * (t / 2 + 0.0004)
                k.disc(look, (xf, 0.0, zc), r - 0.008, r - 0.024, 0.0008, axis="x", seg=72)
                if s < 0 and i == 0 or s > 0 and i == n - 1:
                    rz = -math.pi / 2 if s < 0 else math.pi / 2
                    k.text(look, "ROGUE", (xf + s * 0.0003, 0.0, zc + 0.13), 0.055, rz=rz, depth=0.0006)
                    k.text(look, lb, (xf + s * 0.0003, 0.0, zc - 0.13), 0.05, rz=rz, depth=0.0006)
            k.disc("steel", (x, 0.0, zc), 0.045, 0.0255, t + 0.002, axis="x", seg=32)                 # the hub

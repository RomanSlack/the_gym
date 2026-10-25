"""Hammer Strength HD Air Bike, Charcoal (refs/: ref_01 / ref_02 the maker's three-quarters, ref_03 / ref_04 / ref_07 in
the gym (ref_07 tipped onto its wheels), ref_05 the seat post's knob and the fore-aft slider, ref_06 the crank and
pedal, ref_08 the annotated side three-quarter). Roman's pick. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Seated facing -y, the feet on the pedals, the hands on the moving arms' grips: the legs drive the cranks and
   the arms push and pull, both turning the fan; the air it moves is the resistance (the harder, the more). The knee is
   the working joint (145 deg inside at the bottom of the stroke); the elbows work the arms.
2. Moving parts, each mass named (ref_01 / ref_02 / ref_08):
   - The fan at the front: a drum in a wire cage (a grille on each face, a band round it), its blades on a hub on an
     axle across between two fork plates off the column; the AirGuard, a curved shield over its upper back (it turns to
     send the air elsewhere).
   - The column: a square tube up behind the fan from the base's front to the console; the arms' pivot across it just
     above the fan's hub.
   - The arms: each a long tube on the pivot, the multi-grip handle at its top (a curved grip curling back over), its
     foot below the pivot; a link rod from the foot back to its crank pin, so the arms swing with the pedals (a
     four-bar, solved, not posed).
   - The drive: the cranks on an axle in the round housing under the seat (a belt inside from the crank's pulley to the
     fan's hub, not drawn), the pedals (wide platforms, ref_06).
   - The frame: a square beam along the floor between the stabilizers (front: wheels; back: levelers), the seat tube
     leaning back off it, the column off its front.
   - The seat: the post in the tube (height scale, the pop-pin knob on the tube's front, ref_05), the fore-aft slider
     (scale, its knob), the wide saddle.
3. Adjustments. Seat height: the pop-pin knob, a hole every 25 mm (14 holes); seat fore-aft: the slider (+/-0.08). The
   default build sets the middle user; settings seat_low / seat_high set the short and the tall (each with its user).
4. Load path. The feet: the pedals, the cranks, the belt, the fan. The hands: the arms, the pivots, the links, the
   cranks (the same axle). The air: the fan's blades.
5. Fit range. 1.55 / 1.78 / 1.95 m: the seat hole for a 145 deg knee at the bottom; the hands on the grips with the
   arms at mid-swing, elbows soft. Both of the figure's feet on the bottom pedal's spot.
6. Size. Life Fitness: 105 x 62 x 138 cm (L x W x H) on the catalogue page (the same figure as their upright bike's:
   doubtful), 140 cm long with the seat at its highest and farthest back (their support page). Ours about 1.25 x 0.62 x
   1.36, built from the photos' proportions to the 62 cm width and the 138 cm height.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the crank axle.
"""
import math

LOOK = {
    "frame": dict(color=(0.075, 0.077, 0.08), rough=0.45, metal=0.4, coat=0.2),                      # Charcoal
    "arm": dict(color=(0.02, 0.02, 0.021), rough=0.4, metal=0.3, coat=0.2),                          # the arms: black
    "shroud": dict(color=(0.03, 0.03, 0.032), rough=0.5, coat=0.1),
    "cage": dict(color=(0.02, 0.02, 0.021), rough=0.4, metal=0.5, coat=0.0),
    "blade": dict(color=(0.04, 0.04, 0.042), rough=0.5, coat=0.0),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0, spec=0.3),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.72, coat=0.0, spec=0.3),
    "screen": dict(color=(0.33, 0.36, 0.33), rough=0.3, coat=0.3),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (50, 14, 1.1)}      # ref_01: from the front, on the rider's left
DETAILS = {
    "detail_fan": ((-0.95, -1.05, 0.85), (0.0, -0.45, 0.50), 40),         # the fan, the cage, the fork, the AirGuard
    "detail_arms": ((-0.80, 0.30, 1.30), (0.0, -0.25, 0.90), 40),          # the arms, the pivot, the console
    "detail_seat": ((0.65, 0.75, 1.00), (0.0, 0.32, 0.75), 45),            # the seat post, the knob, the slider
}
SETTINGS = ("seat_low", "seat_high")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

C = (0.06, 0.33)                     # the crank axle (y = 0 at the column's foot's back, nearly)
R_C = 0.17
FAN = (-0.565, 0.46)                 # the fan's hub: forward, the drive housing right behind it
R_FAN, W_FAN = 0.34, 0.20            # its cage: radius (0.68 across, ref_01: near the floor) and width
Y_FS, Y_RS = -0.74, 0.55             # the stabilizers (under the fan's front, behind the seat tube)
X_ST = 0.31                          # their half length (62 cm)
BEAM_Z = 0.11                        # the floor beam's centre (0.08 square, on the stabilizers' tops)
COL = ((-0.185, BEAM_Z + 0.04), (-0.12, 1.06))  # the column: up through the gap between the fan and the drive, leaning back
PIV_Z = 0.66                         # the arms' pivot height on the column
L_UP, L_DN = 0.42, 0.36              # each arm: up from the pivot to the handle's foot, down to the link's eye
X_ARM = 0.18                         # the arms at the pivot (x): outside the fan's fork plates
X_TOP = 0.25                         # the handles at the top (x): splayed out
ST0 = (0.31, BEAM_Z + 0.04)           # the seat tube's foot on the beam
ST_A = 14.0                          # it leans back (deg)
ST_L = 0.52                          # its length (the knob near its top)
HOLE, N_HOLES = 0.025, 14
PHI = -90.0                          # the left crank: straight down
SEAT_HOLE = None


def col_at(z):
    (y0, z0), (y1, z1) = COL
    return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


PIV = (col_at(PIV_Z) - 0.045, PIV_Z)  # on the column's front face


def sdir():
    a = math.radians(ST_A)
    return (math.sin(a), math.cos(a))


def tube_top():
    d = sdir()
    return (ST0[0] + d[0] * ST_L, ST0[1] + d[1] * ST_L)


def seat_top(hole):
    d = sdir()
    ty, tz = tube_top()
    e = 0.03 + hole * HOLE                              # the post out of the tube at the lowest hole + holes
    return (ty + d[0] * e + 0.0, tz + d[1] * e + 0.03 + 0.07)


def leg(H, hole):
    a_ = math.radians(-90.0)
    py, pz = C[0] + R_C * math.cos(a_), C[1] + R_C * math.sin(a_) + 0.025
    ay, az = py + 0.48 * 0.152 * H, pz + 0.039 * H
    sy, sz = seat_top(hole)
    hy, hz = sy + 0.03, sz + 0.075 * H / 1.78
    d = math.hypot(hy - ay, hz - az)
    a, b = 0.246 * H, 0.245 * H
    c = max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))
    return math.degrees(math.acos(c)), (ay, az), (hy, hz)


def best_hole(H):
    return min(range(N_HOLES), key=lambda h: abs(leg(H, h)[0] - 145.0))


SEAT_HOLE = best_hole(1.78)
SHOW = ("middle",)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))


def setting(name):
    global SEAT_HOLE, SHOW
    H = {"seat_low": 1.55, "seat_high": 1.95}[name]
    SEAT_HOLE, SHOW = best_hole(H), ({"seat_low": "short", "seat_high": "tall"}[name],)


def rot(p, about, deg):
    a = math.radians(deg)
    dy, dz = p[0] - about[0], p[1] - about[1]
    return (about[0] + dy * math.cos(a) - dz * math.sin(a), about[1] + dy * math.sin(a) + dz * math.cos(a))


EYE0 = (PIV[0], PIV[1] - L_DN)       # the arm's foot hanging straight
L_LINK = math.sqrt(math.dist(EYE0, C) ** 2 + R_C ** 2)   # the link: the arm upright at mid-swing; a crank-rocker
                                     # (crank 0.17 + ground 0.40 <= link 0.28 + rocker 0.36): the crank turns right round


def _solve(phi, lo, hi, step):
    a = math.radians(phi)
    P = (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))
    best = None
    psi = lo
    while psi <= hi:
        E = rot(EYE0, PIV, psi)
        err = abs(math.dist(E, P) - L_LINK)
        if best is None or err < best[0]:
            best = (err, psi, E, P)
        psi += step
    return best


_TABLE = {}


def arm_angle(phi):
    """The arm's swing (deg, + = its foot toward +y) for a crank angle, the link's length held; followed round the
    crank's turn from 0 deg so the linkage stays on one branch (as the real one does)."""
    if not _TABLE:
        b = _solve(0.0, -60.0, 60.0, 0.05)
        prev = b[1]
        for d in range(0, 360):
            b = _solve(float(d), prev - 4.0, prev + 4.0, 0.02)
            _TABLE[d] = b[1]
            prev = b[1]
    d = int(round(phi)) % 360
    b = _solve(phi % 360.0, _TABLE[d] - 1.0, _TABLE[d] + 1.0, 0.01)
    return b[1], b[2], b[3]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    fan(k)
    column(k)
    drive(k)
    for s in (1, -1):
        crank_and_arm(k, s)
    seat(k)


def base(k):
    k.bar("frame", (0, Y_RS, BEAM_Z), (0, Y_FS, BEAM_Z), 0.08, 0.08, up=(0, 0, 1), r=0.01)        # the floor beam
    for y in (Y_FS, Y_RS):
        k.bar("frame", (-X_ST, y, 0.045), (X_ST, y, 0.045), 0.10, 0.05, up=(0, 0, 1), r=0.01)
        for s in (1, -1):
            k.box("plastic", (s * (X_ST + 0.005), y, 0.045), (0.01, 0.10, 0.05), soft=0.003)
    for s in (1, -1):
        k.cyl("rubber", (s * (X_ST - 0.05), Y_RS, 0.01), 0.025, 0.02, seg=24, soft=0.003)              # levelers
        xw, yw = s * (X_ST - 0.07), Y_FS - 0.05 - 0.045
        for d in (1, -1):                               # the wheels on cheeks off the front bar
            k.box("frame", (xw + d * 0.0255, yw + 0.02, 0.05), (0.006, 0.07, 0.05), soft=0.002)
        k.disc("rubber", (xw, yw, 0.045), 0.045, 0.01, 0.045, axis="x", seg=32)
        k.tube("steel", (xw - 0.0295, yw, 0.045), (xw + 0.0295, yw, 0.045), 0.009, seg=12)


def fan(k):
    """The cage (a grille of rings and spokes on each face, a band round it), the blades on the hub, the axle across
    between the fork plates, the AirGuard over its upper back."""
    fy, fz = FAN
    for s in (1, -1):
        x = s * W_FAN / 2
        for r in [0.06 + 0.022 * i for i in range(13)]:
            k.disc("cage", (x, fy, fz), r + 0.002, r - 0.002, 0.005, axis="x", seg=72)
        k.disc("cage", (x, fy, fz), R_FAN + 0.004, R_FAN - 0.012, 0.014, axis="x", seg=96)            # its rolled rim
        for i in range(16):                             # the grille's spokes
            a = 2 * math.pi * i / 16
            p0 = (s * (W_FAN / 2 + 0.002), fy + 0.04 * math.cos(a), fz + 0.04 * math.sin(a))   # from the hub plate
            p1 = (x, fy + R_FAN * math.cos(a), fz + R_FAN * math.sin(a))
            k.tube("cage", p0, p1, 0.0025, seg=6)
        k.cyl("cage", (s * (W_FAN / 2 + 0.008), fy, fz), 0.045, 0.016, axis="x", seg=32)          # the face's hub, bolted
                                                        # to the fork plate (the cage stands still, the blades turn)
    for i in range(36):                                 # the band: wires across between the faces' outer rings
        a = 2 * math.pi * i / 36
        q = (fy + (R_FAN - 0.006) * math.cos(a), fz + (R_FAN - 0.006) * math.sin(a))
        k.tube("cage", (-W_FAN / 2, *q), (W_FAN / 2, *q), 0.0025, seg=6)
    k.cyl("plastic", (0, fy, fz), 0.06, W_FAN - 0.02, axis="x", seg=32, soft=0.004)               # the blades' hub
    for i in range(14):                                 # the blades
        a = 2 * math.pi * i / 14
        c = (0.0, fy + 0.18 * math.cos(a), fz + 0.18 * math.sin(a))
        k.box("blade", c, (W_FAN - 0.03, 0.006, 0.255), rx=a - math.pi / 2, rz=math.radians(30), soft=0.002)   # pitched
    k.tube("steel", (-(W_FAN / 2 + 0.035), fy, fz), (W_FAN / 2 + 0.035, fy, fz), 0.012, seg=16)    # the axle
    for s in (1, -1):                                   # the fork plates from the column to the axle
        x = s * (W_FAN / 2 + 0.022)
        k.bar("frame", (x, col_at(fz) - 0.03, fz), (x, fy, fz), 0.06, 0.012, up=(1, 0, 0), r=0.01)
        k.cyl("frame", (x, fy, fz), 0.03, 0.02, axis="x", seg=24, soft=0.002)
    k.box("frame", (0, col_at(fz) - 0.03 - 0.0125, fz), (2 * 0.128, 0.025, 0.06), soft=0.004)      # their cross plate
    # the AirGuard: a curved shield round the cage's upper back (40 to 120 deg off the back)
    rg = R_FAN + 0.0075
    pts = [(0, fy + rg * math.cos(math.radians(a)), fz + rg * math.sin(math.radians(a))) for a in range(45, 126, 8)]
    k.sweep("shroud", pts, k.rect(0.006, W_FAN + 0.04, 0.002), up=(1, 0, 0), soft=0.002)        # thin, the fan's width
    for s in (1, -1):                                   # its arms off the axle's ends (it turns on the axle)
        xa = s * (W_FAN / 2 + 0.017)
        k.cyl("shroud", (xa, fy, fz), 0.022, 0.006, axis="x", seg=24, soft=0.001)
        k.bar("shroud", (xa, fy, fz), (xa, fy + rg * math.cos(math.radians(85)), fz + rg * math.sin(math.radians(85))),
              0.03, 0.006, up=(1, 0, 0), r=0.004)


def column(k):
    """The column off the beam's front up behind the fan to the console; the pivot's boss across it; the console."""
    (y0, z0), (y1, z1) = COL
    k.bar("frame", (0, y0, z0 - 0.004), (0, y1, z1), 0.08, 0.06, up=(0, 1, 0), r=0.008)
    k.cyl("frame", (0, PIV[0] + 0.015, PIV[1]), 0.035, 2 * X_ARM - 0.04, axis="x", seg=32, soft=0.003)  # the boss
    k.text("label", "HAMMER STRENGTH", (0.0405, col_at(0.85), 0.85), 0.022, rz=math.pi / 2, spin=math.pi / 2, depth=0.0006)
    t = math.radians(20)
    cn = (y1 + 0.03, z1 + 0.08)
    k.box("shroud", (0, *cn), (0.16, 0.04, 0.20), rx=t, soft=0.008)                                  # the console
    k.box("screen", (0, cn[0] + 0.0205 * math.cos(t) - 0.02 * math.sin(t), cn[1] + 0.0205 * math.sin(t) + 0.02 * math.cos(t)),
          (0.11, 0.002, 0.08), rx=t, soft=0.0)
    k.bar("frame", (0, y1, z1 - 0.004), (0, cn[0], cn[1] - 0.06), 0.05, 0.04, up=(0, 1, 0), r=0.006)


def drive(k):
    """The round housing round the crank (the belt inside), a capsule forward to the column."""
    cov = [(C[0] + 0.24 * math.cos(math.radians(a)), C[1] + 0.24 * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    k.slab("shroud", cov, -0.10, 0.10, 0.03, seg=5)    # (ref_02: a drum as wide as the fan; the column rises out of its top)
    k.box("frame", (0, C[0], (BEAM_Z + 0.04 + C[1] - 0.24) / 2 + 0.002), (0.06, 0.10, C[1] - 0.24 - BEAM_Z - 0.04 + 0.008),
          soft=0.003)                                   # its bracket on the beam
    k.text("label", "HAMMER STRENGTH", (0.1003, C[0] - 0.05, C[1] + 0.12), 0.03, rz=math.pi / 2, depth=0.0006)


def crank_and_arm(k, s):
    phi = PHI if s > 0 else PHI + 180.0
    psi, E, P = arm_angle(phi)
    xa = s * 0.115
    k.cyl("frame", (xa, C[0], C[1]), 0.035, 0.03, axis="x", seg=32, soft=0.003)                     # the crank's hub
    k.bar("frame", (xa, C[0] + (P[0] - C[0]) / R_C * 0.03, C[1] + (P[1] - C[1]) / R_C * 0.03), (xa, P[0], P[1]), 0.045, 0.02,
          up=(1, 0, 0), r=0.006)
    k.cyl("frame", (xa, P[0], P[1]), 0.022, 0.02, axis="x", seg=24, soft=0.002)
    xp = s * 0.23
    k.cyl("steel", (s * 0.15, P[0], P[1]), 0.011, 0.05, axis="x", seg=16)                            # the pedal spindle
    k.box("plastic", (xp, P[0], P[1]), (0.11, 0.13, 0.03), soft=0.006)                               # the pedal (ref_06)
    k.box("rubber", (xp, P[0], P[1] + 0.0155), (0.10, 0.12, 0.002), soft=0.0)
    # the arm on the pivot: its foot (the eye) to the link, up past the pivot to the handle
    xl = s * X_ARM
    up_dir = rot((PIV[0], PIV[1] + 1.0), PIV, psi)
    ud = (up_dir[0] - PIV[0], up_dir[1] - PIV[1])
    top = (PIV[0] + ud[0] * L_UP, PIV[1] + ud[1] * L_UP)
    k.tube("arm", (xl, *E), (xl, *top), 0.022, seg=24)                                             # the arm's lower run
    k.cyl("arm", (xl, PIV[0], PIV[1]), 0.034, 0.04, axis="x", seg=32, soft=0.003)                  # its hub on the pivot
    # up and out to the handle: the arm bends out to X_TOP, the grip curls back over (multi-grip, ref_01)
    h0 = (xl, *top)
    h1 = (s * X_TOP, top[0] + ud[0] * 0.12, top[1] + ud[1] * 0.12)
    h2 = (s * X_TOP, h1[1] + ud[0] * 0.14, h1[2] + ud[1] * 0.14)
    h3 = (s * X_TOP, h2[1] + 0.10, h2[2] + 0.03)
    h4 = (s * X_TOP, h3[1] + 0.06, h3[2] - 0.07)
    k.sweep("arm", [h0, h1, h2], k.circle(0.019, 20), bend=0.05)
    k.sweep("foam", [h2, h3, h4], k.circle(0.021, 20), bend=0.04, soft=0.003)
    k.cyl("plastic", (h4[0], h4[1] + 0.006, h4[2] - 0.006), 0.022, 0.01, axis="z", seg=20, soft=0.002)
    # the link: from the arm's eye back to the crank pin, beside the crank
    xk = s * 0.145                                     # the link: on the pedal's spindle, between the crank and the pedal
    k.cyl("frame", (xk, *E), 0.022, 0.015, axis="x", seg=24, soft=0.002)
    k.cyl("frame", (xk, *P), 0.022, 0.015, axis="x", seg=24, soft=0.002)
    k.bar("frame", (xk, *E), (xk, *P), 0.03, 0.015, up=(1, 0, 0), r=0.005)
    k.cyl("frame", ((xl + xk) / 2, *E), 0.016, abs(xl - xk) + 0.002, axis="x", seg=16)                # the eye's pin


def seat(k):
    """The seat tube off the beam, the post in it (scale; the pop-pin knob on the tube's front, ref_05), the slider
    on the post's top (scale, knob), the wide saddle."""
    d = sdir()
    ty, tz = tube_top()
    k.bar("frame", (0, *ST0), (0, ty, tz), 0.07, 0.07, up=(0, 1, 0), r=0.008, cut0=((0, *ST0), (0, 0, 1)))
    e = 0.03 + SEAT_HOLE * HOLE
    pt = (ty + d[0] * e, tz + d[1] * e)
    k.bar("frame", (0, ty - d[0] * 0.004, tz - d[1] * 0.004), (0, *pt), 0.05, 0.05, up=(0, 1, 0), r=0.006)   # the post
    for i in range(1, int(e / 0.025)):
        q = (ty + d[0] * i * 0.025, tz + d[1] * i * 0.025)
        k.box("label", (0, q[0] + 0.0252, q[1]), (0.012, 0.0015, 0.0015), soft=0.0)
    kn = (ty - d[1] * 0.0355 - d[0] * 0.05, tz + d[0] * 0.0355 - d[1] * 0.05)                       # the knob, on the
    k.cyl("frame", (0, kn[0] - 0.015, kn[1]), 0.012, 0.03, axis="y", seg=16)                         # tube's front
    k.cyl("plastic", (0, kn[0] - 0.04, kn[1]), 0.03, 0.025, axis="y", seg=24, soft=0.005)
    zr = pt[1] + 0.02
    k.box("frame", (0, pt[0], zr), (0.045, 0.24, 0.04), soft=0.005)                                  # the slider
    for j in range(-8, 9, 2):
        k.box("label", (-0.0226, pt[0] + j * 0.01, zr), (0.0015, 0.0015, 0.012), soft=0.0)
    k.cyl("plastic", (0.04, pt[0] - 0.09, zr), 0.02, 0.016, axis="x", seg=20, soft=0.003)
    k.cyl("frame", (0.0275, pt[0] - 0.09, zr), 0.007, 0.012, axis="x", seg=12)
    ct = (pt[0], zr + 0.02 + 0.012)
    k.box("frame", (0, *ct), (0.07, 0.10, 0.024), soft=0.004)
    k.shaped_pad("pad", [(-0.15, 0.10), (-0.16, 0.0), (-0.10, -0.10), (-0.05, -0.15), (0.05, -0.15), (0.10, -0.10), (0.16, 0.0),
                         (0.15, 0.10)], (0, ct[0], ct[1] + 0.012 + 0.035), (0, 0, 1), (1, 0, 0), 0.07, r=0.05, cushion=0.012)


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        kn, (ay, az), (hy, hz) = leg(H, SEAT_HOLE)
        a, b = 0.246 * H, 0.245 * H
        vy, vz = hy - ay, hz - az
        dd = math.hypot(vy, vz)
        base_ = math.degrees(math.atan2(-vy, vz))
        al = math.degrees(math.acos((a * a + dd * dd - b * b) / (2 * a * dd)))
        be = math.degrees(math.acos((b * b + dd * dd - a * a) / (2 * b * dd)))
        shank, thigh = base_ + al, base_ - be
        ball = (0.0, ay - 0.48 * 0.152 * H, az - 0.039 * H)
        psi, _, _ = arm_angle(PHI)                      # the left arm's grip at this crank angle
        up_dir = rot((PIV[0], PIV[1] + 1.0), PIV, psi)
        ud = (up_dir[0] - PIV[0], up_dir[1] - PIV[1])
        top = (PIV[0] + ud[0] * L_UP, PIV[1] + ud[1] * L_UP)
        g = (X_TOP, top[0] + ud[0] * 0.17, top[1] + ud[1] * 0.17)   # the grip's upright, mid-height
        best = None
        for tr in range(0, 40):
            sh = (0.13 * H * 0.85, hy - math.sin(math.radians(tr)) * 0.288 * H, hz + math.cos(math.radians(tr)) * 0.288 * H)
            r = reach(H, sh, g)
            if best is None or abs(r[4] - 150) < abs(best[1][4] - 150):
                best = (tr, r)
        tr, (a1, l1, a2, l2, elbow) = best
        print(f"fit {label}: seat hole {SEAT_HOLE + 1} of {N_HOLES}, knee {kn:.0f} deg, trunk {tr} deg, elbow {elbow:.0f} deg",
              flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=shank, thigh=thigh, trunk=tr, neck=-8, stance=0.34,
                          arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def reach(H, sh, g):
    f, left = (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w0 = (0.5, 0.2, -0.85)
        dot = sum(w0[i] * vh[i] for i in range(3))
        w = tuple(w0[i] - vh[i] * dot for i in range(3))
        wl = math.sqrt(sum(c * c for c in w))
        w = tuple(c / wl for c in w)
        e = tuple(L1 * (math.cos(al) * vh[i] + math.sin(al) * w[i]) for i in range(3))
        elbow = math.degrees(math.acos((L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2)))
    fo = tuple(v[i] - e[i] for i in range(3))
    fl = math.sqrt(sum(c * c for c in fo))
    fo = tuple(c / fl for c in fo)
    eh = tuple(c / L1 for c in e)

    def angles(u):
        lat = math.degrees(math.asin(max(-1.0, min(1.0, sum(u[i] * left[i] for i in range(3))))))
        a = math.degrees(math.atan2(sum(u[i] * f[i] for i in range(3)), u[2]))
        return a, lat

    a1, l1 = angles(eh)
    a2, l2 = angles(fo)
    return a1, l1, a2, l2, elbow

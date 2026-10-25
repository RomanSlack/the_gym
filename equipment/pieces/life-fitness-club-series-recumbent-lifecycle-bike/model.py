"""Life Fitness Club Series+ Recumbent Lifecycle Bike, black, the 24 in SE4 console (refs/: ref_01 / ref_05-ref_07 the
maker's studio three-quarters, ref_03 a true side view with a rider (the geometry is read off it, 472 px per m from the
179 cm length), ref_02 / ref_04 in use). Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred). Built to
the two gates and README point 9 (name what every big shape is before shaping it).

DESIGN SPEC (gate 1)
1. Use. Sitting back on the seat against the backrest, facing -y, the feet on the pedals ahead at about hip height,
   the hands on the side grips under the seat (or the assist bar under the console). The knee is the working joint:
   with the pedal at its farthest it stays bent about 30 deg (150 inside); the seat's place on its rail sets that.
2. Moving parts, each mass named (ref_01 / ref_03):
   - The drive unit at the front: a tall moulded body (the flywheel and generator inside, not drawn), its back sloping
     down toward the rider, a raised side panel with the logos; the crank axle through it, a silver crank arm each side,
     the pedals with heel cups and straps. It stands on the front stabilizer and the main tube.
   - The frame: one bent main tube along the floor from under the drive unit back to the rear stabilizer, turning up
     there as the rear leg to the seat rail; a middle post, parallel, off the main tube to the rail's front (the
     step-through: nothing between the rail and the drive unit but the floor tube).
   - The seat rail: a long black pan falling 9 deg toward the front, a silver track along each side; the seat's
     carriage slides on it.
   - The seat: the carriage on the track, the cushion on it, the tall backrest leaning back 15 deg on its bracket,
     a grip each side under the hands; the red release loop under the carriage's front (ref_03).
   - The column off the drive unit's top, leaning back toward the rider, the console on it tilted 23 deg, the assist
     bar across under it.
3. Adjustments. The seat's place along the rail: 41 positions (Life Fitness), 11 mm apart (44 cm of travel); lifting the
   red loop draws the carriage's pin out of the rail's holes, the seat slides, the pin drops in. Pedal straps. The
   default build sets the seat for the middle user; settings seat_near / seat_far set it for the short and the tall.
4. Load path. The feet push the pedals round, the cranks turn the flywheel's generator (resistance from the console).
   The rider's weight and the push back off the pedals: the carriage, the rail, the two legs, the main tube.
5. Fit range. 1.55 / 1.78 / 1.95 m: each user's seat position chosen so the knee is 150 deg inside with the pedal at
   its farthest (the fit run prints it). Both of the figure's feet stand on that pedal's spot (it can't split them).
   The trunk lies back on the backrest; the hands on the side grips.
6. Size. Life Fitness: 179 x 66 x 131 cm (L x W x H, with its small SL console). Ours about 1.79 x 0.66 x 1.60: the
   24 in SE4 console stands higher (ref_03: its top at 1.59).
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the crank axle.
"""
import math

LOOK = {
    "frame": dict(color=(0.022, 0.022, 0.024), rough=0.4, metal=0.3, coat=0.2),
    "shroud": dict(color=(0.018, 0.018, 0.019), rough=0.42, coat=0.25),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "silver": dict(color=(0.62, 0.63, 0.65), rough=0.25, metal=1.0, coat=0.2),
    "track": dict(color=(0.55, 0.56, 0.58), rough=0.35, metal=0.9, aniso=0.5, coat=0.0),       # the rail's sides
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0, spec=0.3),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.72, coat=0.0, spec=0.3),
    "screen": dict(color=(0.01, 0.012, 0.016), rough=0.08, coat=1.0),
    "glow": dict(color=(0.20, 0.55, 0.30), rough=0.4, coat=0.0, emit=0.6),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "vent": dict(color=(0.07, 0.07, 0.075), rough=0.6, coat=0.0),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.1),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-130, 18, 1.15)}   # ref_01's angle: from behind the rider's left, a little above
DETAILS = {
    "detail_drive": ((0.80, -0.55, 0.85), (0.10, 0.0, 0.45), 45),         # the drive unit, its crank and a pedal
    "detail_seat": ((0.85, 1.35, 1.25), (0.0, 0.75, 0.70), 45),          # the seat, the carriage, the rail
    "detail_console": ((0.70, 0.75, 1.55), (0.0, 0.05, 1.20), 45),       # the console, the assist bar, the column
}
SETTINGS = ("seat_near", "seat_far")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

# ---- (y, z) from ref_03's px: y = (670 - x) / 472, z = (900 - y) / 472
Y_FS, Y_RS = -0.45, 1.08             # the front and rear stabilizers' centres (880 / 160 px)
X_ST = 0.33                          # their half length (66 cm)
ST = (0.09, 0.08)                    # their section: depth, height (their top 0.096)
C = (0.0, 0.455)                     # the crank axle (670, 685)
R_C = 0.17                           # the crank's length
HB = 0.12                            # the drive unit's half width
HF = HB + 0.005                      # its raised side panel's face
X_PED = HF + 0.088                   # the pedals' centres (x)
TUBE_R = 0.03                        # the frame's tube (6 cm)
Z_TUBE = 0.096 + TUBE_R              # the main tube's centre: on the stabilizers
REAR_LEG = ((1.02, Z_TUBE), (1.14, 0.53))      # the rear leg: the bend off the floor run (190, 840) up to the rail
MID_POST = ((0.49, Z_TUBE), (0.60, 0.43))      # the middle post (440, 840) up to the rail's front (380, 705)
RAIL = ((0.40, 0.49), (1.32, 0.63))  # the rail's centre line, front to back (465, 670) / (45, 605): falling 9 deg forward
RAIL_H, RAIL_W = 0.15, 0.17          # its pan's height and width (ref_03: 0.40-0.58 at the front)
N_POS, STEP = 41, 0.011              # the seat's positions along the rail
Q0 = 0.10                            # the carriage's middle at the nearest position, along the rail from its front
COL = ((-0.10, 0.79), (0.07, 1.10))  # the column: off the drive unit's top (720, 525) up and back to the console's foot
CN = (0.03, 1.37)                    # the console's centre (650, 265)
TILT = 23.0                          # tilted back (deg): its top (695, 150), its bottom (600, 370)
BAR = (0.14, 1.03)                   # the assist bar across (605, 415)
PHI = None                           # the left crank's angle (deg from +y toward +z): set to the far stroke below
SEAT_POS = None


def rail_dir():
    (y0, z0), (y1, z1) = RAIL
    L = math.hypot(y1 - y0, z1 - z0)
    return ((y1 - y0) / L, (z1 - z0) / L), L


def carriage(pos):
    """The carriage's middle on the rail's top (y, z) at a position (0 = the nearest the pedals)."""
    (dy, dz), _ = rail_dir()
    t = Q0 + pos * STEP
    (y0, z0) = RAIL[0]
    nz = (-dz, dy)                                      # square to the rail, up
    return (y0 + dy * t + nz[0] * RAIL_H / 2, z0 + dz * t + nz[1] * RAIL_H / 2)


def hip(pos, H):
    """The hip joint for a user of height H with the seat at pos: over the cushion, in front of the backrest."""
    qy, qz = carriage(pos)
    return (qy + 0.03, qz + 0.04 + 0.07 + 0.085 * H / 1.78)


def far_angle(pos, H=1.78):
    """The crank's angle with the pedal farthest from the hip."""
    hy, hz = hip(pos, H)
    return math.degrees(math.atan2(C[1] - hz, C[0] - hy))


def pedal_pt(phi):
    a = math.radians(phi)
    return (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))


def leg_ik(A, Hp, a, b):
    """Knee above the ankle-hip line: returns the knee (y, z) and the knee's inside angle."""
    dy, dz = Hp[0] - A[0], Hp[1] - A[1]
    d = math.hypot(dy, dz)
    d = min(d, a + b - 1e-6)
    al = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d))))
    base = math.atan2(dz, dy)
    for sgn in (1, -1):                                 # the knee above the line
        K = (A[0] + a * math.cos(base + sgn * al), A[1] + a * math.sin(base + sgn * al))
        if (K[0] - A[0]) * dz - (K[1] - A[1]) * dy < 0:
            break
    kn = math.degrees(math.acos(max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))))
    return K, kn


def foot(pos, H):
    """The ball on the far pedal, the sole square to the hip-pedal line; returns (ball, sole deg, ankle)."""
    phi = far_angle(pos, H)
    py, pz = pedal_pt(phi)
    hy, hz = hip(pos, H)
    sole = 90.0 - math.degrees(math.atan2(hz - pz, hy - py))     # toes up from level
    s = math.radians(sole)
    so, su = (-math.cos(s), math.sin(s)), (math.sin(s), math.cos(s))
    ball = (py + su[0] * 0.016, pz + su[1] * 0.016)
    Lf = 0.152 * H
    ank = (ball[0] - so[0] * 0.48 * Lf + su[0] * 0.039 * H, ball[1] - so[1] * 0.48 * Lf + su[1] * 0.039 * H)
    return ball, sole, ank


def knee_at(pos, H):
    ball, sole, ank = foot(pos, H)
    return leg_ik(ank, hip(pos, H), 0.246 * H, 0.245 * H)[1]


def best_pos(H, knee=150.0):
    return min(range(N_POS), key=lambda p: abs(knee_at(p, H) - knee))


USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ("middle",)
SEAT_POS = best_pos(1.78)
PHI = far_angle(SEAT_POS)


def setting(name):
    global SEAT_POS, SHOW, PHI
    if name == "seat_near":
        SEAT_POS, SHOW = best_pos(1.55), ("short",)
    elif name == "seat_far":
        SEAT_POS, SHOW = best_pos(1.95), ("tall",)
    PHI = far_angle(SEAT_POS)


def arc(c, r, a0, a1, n=8):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    drive(k)
    for s in (1, -1):
        crank(k, s)
    column(k)
    rail(k)
    seat(k)


def base(k):
    """The two stabilizers (capped bars, rubber feet; wheels on the front one), the main tube along the floor on them,
    bent up at the back as the rear leg, the middle post off it."""
    zc = ST[1] / 2 + 0.016
    for y in (Y_FS, Y_RS):
        k.bar("frame", (-X_ST, y, zc), (X_ST, y, zc), ST[0], ST[1], up=(0, 0, 1), r=0.028)
        for s in (1, -1):
            k.cyl("plastic", (s * (X_ST + 0.005), y, zc), 0.034, 0.01, axis="x", seg=32, soft=0.003)
            k.box("rubber", (s * (X_ST - 0.05), y, 0.008), (0.07, 0.07, 0.016), soft=0.003)
    for s in (1, -1):                                   # the front wheels on cheeks off the front bar's face
        xw, yw = s * (X_ST - 0.07), Y_FS - ST[0] / 2 - 0.045
        for d in (1, -1):
            k.box("frame", (xw + d * 0.0205, yw + 0.012, 0.06), (0.006, 0.07, 0.05), soft=0.002)
        k.disc("rubber", (xw, yw, 0.048), 0.036, 0.008, 0.035, axis="x", seg=32)
        k.tube("steel", (xw - 0.0245, yw, 0.048), (xw + 0.0245, yw, 0.048), 0.008, seg=12)
    (ry0, rz0), (ry1, rz1) = REAR_LEG
    rail_bottom = rail_z(ry1) - RAIL_H / 2
    k.sweep("frame", [(0, Y_FS, Z_TUBE), (0, ry0, Z_TUBE), (0, ry1, rail_bottom + 0.004)], k.circle(TUBE_R, 28), bend=0.12,
            cut1=((0, ry1, rail_bottom + 0.004), rail_normal()))   # the main tube and the rear leg
    (my0, mz0), (my1, mz1) = MID_POST
    mb = rail_z(my1) - RAIL_H / 2
    k.tube("frame", (0, my0, Z_TUBE), (0, my1, mb + 0.004), TUBE_R * 0.9, seg=28,
           cut0=((0, my0, Z_TUBE + 0.022), (0, 0, 1)), cut1=((0, my1, mb + 0.004), rail_normal()), weld=True)


def rail_z(y):
    (y0, z0), (y1, z1) = RAIL
    return z0 + (z1 - z0) * (y - y0) / (y1 - y0)


def rail_normal():
    (dy, dz), _ = rail_dir()
    return (0.0, -dz, dy)


def drive_outline():
    """The drive unit's side (y, z), from ref_03: its foot on the main tube, the back sloping up from the crank to the
    top, the top level, a round over the front, the front nearly upright."""
    import kit
    return kit._round_poly([(-0.505, Z_TUBE + TUBE_R), (0.13, Z_TUBE + TUBE_R), (0.15, 0.50), (-0.03, 0.78), (-0.36, 0.785),
                            (-0.515, 0.62)], 0.13, 10)


def drive(k):
    k.slab("shroud", drive_outline(), -HB, HB, 0.04, seg=6)
    import kit
    panel = kit._round_poly([(-0.47, 0.19), (0.09, 0.19), (0.11, 0.49), (-0.05, 0.72), (-0.34, 0.73), (-0.47, 0.60)], 0.10, 8)
    for s in (1, -1):
        k.slab("shroud", panel, *sorted((s * (HB - 0.001), s * HF)), 0.003, seg=2)             # the raised side panel
        k.text("label", "Life Fitness", (s * (HF + 0.0003), -0.17, 0.33), 0.045, rz=math.pi / 2 * s, depth=0.0006)
        k.text("label", "LF", (s * (HF + 0.0003), -0.40, 0.33), 0.05, rz=math.pi / 2 * s, depth=0.0006)
        k.box("vent", (s * (HF + 0.0005), -0.42, 0.55), (0.002, 0.018, 0.22), soft=0.0)        # a grip slot (ref_03)


def crank(k, s):
    """One side: the silver ring round the axle's end, the crank arm, the pedal with its heel cup and strap, turned to
    meet the sole."""
    phi = PHI if s > 0 else PHI + 180.0
    a = math.radians(phi)
    P = (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))
    k.disc("silver", (s * (HF + 0.004), C[0], C[1]), 0.05, 0.03, 0.008, axis="x", seg=48)       # the ring
    xa = s * (HF + 0.016)
    k.cyl("silver", (xa, C[0], C[1]), 0.038, 0.024, axis="x", seg=40, soft=0.003)
    k.cyl("plastic", (s * (HF + 0.0295), C[0], C[1]), 0.02, 0.003, axis="x", seg=24)
    k.bar("silver", (xa, C[0] + (P[0] - C[0]) / R_C * 0.03, C[1] + (P[1] - C[1]) / R_C * 0.03), (xa, P[0], P[1]), 0.045,
          0.022, up=(1, 0, 0), r=0.008)
    k.cyl("silver", (xa, P[0], P[1]), 0.022, 0.024, axis="x", seg=24, soft=0.002)
    k.cyl("steel", (s * (HF + 0.033), P[0], P[1]), 0.013, 0.014, axis="x", seg=20, soft=0.001)
    # the pedal turned so its face meets the sole: square to the hip-pedal line (the middle user's)
    hy, hz = hip(SEAT_POS, 1.78)
    sole = math.radians(90.0 - math.degrees(math.atan2(hz - P[1], hy - P[0])))
    rx = -sole
    nrm = (0.0, math.sin(sole), math.cos(sole))         # out of the pedal's face, toward the rider
    fwd = (0.0, -math.cos(sole), math.sin(sole))        # along it, to the toes
    xp = s * X_PED

    def at(u, v):
        return (xp, P[0] + fwd[1] * u + nrm[1] * v, P[1] + fwd[2] * u + nrm[2] * v)

    k.box("plastic", at(0.0, 0.0), (0.10, 0.15, 0.022), rx=rx, soft=0.006)
    k.box("rubber", at(0.0, 0.0115), (0.09, 0.13, 0.002), rx=rx, soft=0.0)
    k.box("plastic", at(-0.068, 0.03), (0.10, 0.014, 0.05), rx=rx, soft=0.005)                  # the heel cup
    loop = []                                           # the strap over the toes
    for ang in range(0, 181, 15):
        x = xp + 0.047 * math.cos(math.radians(ang))
        p = at(0.035, 0.011 + 0.045 * math.sin(math.radians(ang)))
        loop.append((x, p[1], p[2]))
    k.sweep("rubber", loop, k.rect(0.006, 0.045, 0.002), up=(0, *fwd[1:]), soft=0.002)


def column(k):
    """The column off the drive unit's top, leaning back to the console's foot; the assist bar across on a stem back
    out of it; the console tilted 23 deg, its mount box behind."""
    (y0, z0), (y1, z1) = COL
    k.bar("frame", (0, y0, z0 - 0.03), (0, y1, z1), 0.07, 0.10, up=(0, 1, 0), r=0.02, cut0=((0, 0, 0.778), (0, 0, 1)))
    t = math.radians(TILT)
    fn = (0.0, math.cos(t), math.sin(t))
    fu = (0.0, -math.sin(t), math.cos(t))
    cn = (0, CN[0], CN[1])
    mb = (0, cn[1] - fn[1] * 0.0465 - fu[1] * 0.08, cn[2] - fn[2] * 0.0465 - fu[2] * 0.08)
    k.box("shroud", cn, (0.62, 0.045, 0.42), rx=t, soft=0.02)
    k.box("screen", (0, cn[1] + fn[1] * 0.0228, cn[2] + fn[2] * 0.0228), (0.58, 0.003, 0.37), rx=t, soft=0.0)
    k.box("glow", (0.12, cn[1] + fn[1] * 0.0245 + fu[1] * 0.08, cn[2] + fn[2] * 0.0245 + fu[2] * 0.08), (0.10, 0.002, 0.05),
          rx=t, soft=0.0)
    k.box("shroud", mb, (0.24, 0.05, 0.20), rx=t, soft=0.012)                                    # the mount box
    k.text("label", "Life Fitness", (0, mb[1] - fn[1] * 0.0249 + fu[1] * 0.04, mb[2] - fn[2] * 0.0249 + fu[2] * 0.04),
           0.025, rx=math.pi / 2 + t, depth=0.0005)
    # the column's head: a block from the column's top into the mount box's foot
    mlow = (0, mb[1] - fu[1] * 0.096 - fn[1] * 0.012, mb[2] - fu[2] * 0.096 - fn[2] * 0.012)
    cd = ((y1 - y0) / math.hypot(y1 - y0, z1 - z0), (z1 - z0) / math.hypot(y1 - y0, z1 - z0))
    k.bar("shroud", (0, y1 - cd[0] * 0.03, z1 - cd[1] * 0.03), mlow, 0.10, 0.06, up=(0, 1, 0), r=0.02,
          cut0=((0, y1 - cd[0] * 0.004, z1 - cd[1] * 0.004), (0, *cd)))     # the head, off the column's top
    # the assist bar: a stem back off the column, the bar across, foam on its ends
    yb, zb = BAR
    yc = y0 + (y1 - y0) * (zb - z0) / (z1 - z0)
    k.bar("frame", (0, yc + 0.056, zb), (0, yb, zb), 0.04, 0.04, up=(0, 0, 1), r=0.01)
    k.tube("frame", (-0.20, yb + 0.017, zb), (0.20, yb + 0.017, zb), 0.021, seg=20)
    for s in (1, -1):
        k.tube("foam", (s * 0.06, yb + 0.017, zb), (s * 0.19, yb + 0.017, zb), 0.026, seg=20, soft=0.003)
        k.cyl("plastic", (s * 0.205, yb + 0.017, zb), 0.027, 0.01, axis="x", seg=20, soft=0.002)


def rail(k):
    """The seat rail: a black pan along the rail line, a silver track down each side, end caps."""
    (dy, dz), L = rail_dir()
    (y0, z0), (y1, z1) = RAIL
    tilt = math.atan2(dz, dy)
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    k.box("frame", (0, ym, zm), (RAIL_W, L, RAIL_H), rx=tilt, soft=0.012)
    nz = (-dz, dy)
    for s in (1, -1):
        k.box("track", (s * (RAIL_W / 2 + 0.002), ym + nz[0] * 0.035, zm + nz[1] * 0.035), (0.004, L - 0.08, 0.06), rx=tilt,
              soft=0.0)
    for (ye, ze), sg in ((RAIL[0], -1), (RAIL[1], 1)):
        k.box("plastic", (0, ye + dy * sg * 0.006, ze + dz * sg * 0.006), (RAIL_W + 0.01, 0.014, RAIL_H + 0.01), rx=tilt,
              soft=0.004)


def seat(k):
    """The carriage on the rail's top, the cushion on it, the backrest on its bracket leaning back 15 deg, a grip each
    side; the red release loop under the carriage's front."""
    (dy, dz), _ = rail_dir()
    tilt = math.atan2(dz, dy)
    qy, qz = carriage(SEAT_POS)
    nz = (-dz, dy)

    def at(u, v):                                        # along the rail (+ back) and square to it (+ up)
        return (qy + dy * u + nz[0] * v, qz + dz * u + nz[1] * v)

    k.box("frame", (0, *at(0.03, 0.02)), (RAIL_W + 0.03, 0.40, 0.04), rx=tilt, soft=0.006)       # the carriage
    k.box("shroud", (0, *at(0.0, 0.055)), (0.24, 0.22, 0.03), rx=tilt, soft=0.006)                # the seat's pan
    k.shaped_pad("pad", [(-0.20, 0.17), (-0.21, -0.05), (-0.16, -0.17), (0.16, -0.17), (0.21, -0.05), (0.20, 0.17)],
                 (0, *at(0.0, 0.07 + 0.0345)), (0, -dz, dy), (1, 0, 0), 0.07, r=0.05, cushion=0.012)  # the cushion
    # the backrest: a bracket up off the carriage's back, the pad leaning back 15 deg
    br = at(0.205, 0.04)
    lean = math.radians(15)
    up = (math.sin(lean), math.cos(lean))
    top = (br[0] + up[0] * 0.26, br[1] + up[1] * 0.26)
    k.bar("frame", (0, br[0] - 0.01, br[1]), (0, *top), 0.08, 0.05, up=(0, 1, 0), r=0.01)
    bc = (top[0] + up[0] * 0.11, top[1] + up[1] * 0.11)
    k.shaped_pad("pad", [(-0.19, -0.28), (0.19, -0.28), (0.20, 0.22), (0.16, 0.30), (-0.16, 0.30), (-0.20, 0.22)],
                 (0, bc[0] - up[1] * 0.06, bc[1] + up[0] * 0.06), (0, -up[1], up[0]), (1, 0, 0), 0.08, r=0.05, cushion=0.012)
    k.box("shroud", (0, bc[0] - up[1] * 0.012, bc[1] + up[0] * 0.012), (0.36, 0.024, 0.52), rx=-lean, soft=0.01)  # its shell
    # the grips: a bar out of each side of the pan, along the seat's edge, foam on the front
    for s in (1, -1):
        g0, g1 = at(0.06, 0.055), at(-0.30, 0.15)      # ref_01: long, reaching forward past the cushion's nose
        k.sweep("frame", [(s * 0.118, *g0), (s * 0.255, *g0), (s * 0.255, *g1)], k.circle(0.015, 20), bend=0.05)
        k.tube("foam", (s * 0.255, *at(-0.08, 0.089)), (s * 0.255, *at(-0.29, 0.147)), 0.02, seg=20, soft=0.003)
        k.tube("silver", (s * 0.255, *at(-0.29, 0.147)), (s * 0.255, *at(-0.31, 0.153)), 0.021, seg=20, soft=0.002)
    # the release loop: red, under the carriage's front
    lp = [(0.07 * math.cos(math.radians(a)), *at(-0.16 - 0.06 * math.sin(math.radians(a)), 0.0)) for a in range(0, 181, 15)]
    k.sweep("red", lp, k.circle(0.005, 10), soft=0.0)


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        ball, sole, ank = foot(SEAT_POS, H)
        hp = hip(SEAT_POS, H)
        K, kn = leg_ik(ank, hp, 0.246 * H, 0.245 * H)
        print(f"fit {label}: seat position {SEAT_POS + 1} of {N_POS}, knee {kn:.0f} deg at the far stroke", flush=True)

        def ang(p, q):
            return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))

        shank, thigh = ang(ank, K), ang(K, hp)
        trunk = -15.0
        sh = (0.13 * H * 0.85, hp[0] + math.sin(math.radians(15)) * 0.288 * H, hp[1] + math.cos(math.radians(15)) * 0.288 * H)
        qy, qz = carriage(SEAT_POS)
        (dy, dz), _ = rail_dir()
        g = (0.255, qy + dy * -0.07 + (-dz) * 0.11, qz + dz * -0.07 + dy * 0.11)   # just ahead of the cushion (ref_03)
        a1, l1, a2, l2, elbow = reach(H, sh, g)
        print(f"fit {label}: elbow {elbow:.0f} deg on the side grips", flush=True)
        out[label] = dict(H=H, ball=(0.0, *ball), face=(0, -1), sole=sole, shank=shank, thigh=thigh, trunk=trunk, neck=12,
                          stance=2 * X_PED, arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
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
        w0 = (0.4, 0.6, -0.5)                           # the elbow's way: out and back
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

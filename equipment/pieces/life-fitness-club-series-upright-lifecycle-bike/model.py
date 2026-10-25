"""Life Fitness Club Series+ Upright Lifecycle Bike, black, the 24 in SE4 console (refs/: ref_01 / ref_08-ref_10 the
maker's studio three-quarters, ref_02 a true side view with a rider (the geometry is read off it, 476 px per m from the
105 cm length), ref_03 the crank and pedal, ref_04 the seat and its lever, ref_05 / ref_06 in use, ref_07 the
handlebar). Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred). Built to the two gates and README
point 9 (name what every big shape is before shaping it).

DESIGN SPEC (gate 1)
1. Use. Seated on the saddle facing -y (the console), the feet in the pedals' straps turning the cranks, the hands on
   the handlebar (its rear loop, or the horns for standing climbs). The knee is the working joint: at the bottom of the
   stroke it stays bent about 25-35 deg (145 deg inside), the seat height sets that.
2. Moving parts, each mass named (ref_02 / ref_03 / ref_04):
   - The body: one moulded shroud over the drive (the flywheel and its generator inside, not drawn), a big round cover
     on each side round the crank, a rise at its back that holds the seat's sleeve, a collar at its front for the
     column. It is not a frame member you can see: it stands on the two stabilizers.
   - The crank: one axle across the body under the cover discs; a silver crank arm each side outside the cover, 180 deg
     apart, its hub capped (ref_03); a pedal with a toe strap on each arm's spindle.
   - The seat: a square post sliding in a square sleeve that leans back 17 deg out of the body's rise (ref_02), so
     raising the seat also moves it back, as the leg gets longer; the saddle on a clamp on the post's top.
   - The column: near upright from the collar to the cradle; the cradle carries the handlebar and the console's neck.
   - The handlebar (ref_07, from the rider): one stem back out of the cradle to a button hub nearest the rider (the
     resistance keys), two arms out of the hub sweeping out and forward, rising into horns beside the screen. Fixed.
3. Adjustments. The seat height: 42 positions (Life Fitness), a hole every 8 mm along the post (33 cm of travel); the
   red lever under the saddle's nose (ref_04) pulls the spring pin out of the post, the post slides, the pin drops into
   the next hole. Pedal straps. Resistance on the console (not drawn). The default build sets the seat for the middle
   user; settings seat_low / seat_high set it for the short and the tall user (each rendered with that user).
4. Load path. The feet push the pedals round; the cranks turn the axle and the flywheel's generator inside the body
   (an eddy brake, resistance from the console). The rider's weight: the saddle, the post, the sleeve, the body's rise,
   the rear stabilizer.
5. Fit range. 1.55 / 1.78 / 1.95 m: each user's seat hole chosen so the knee is 145 deg inside with the pedal at the
   bottom (the fit run prints the hole and the knee). The trunk leans to the loop grips, the elbows soft (about 150).
   The figure can't split its feet, so both stand on the bottom pedal's spot (the check is the bottom of the stroke).
6. Size. Life Fitness: 105 x 62 x 138 cm (L x W x H, with its small SL console). Ours about 1.05 x 0.62 x 1.56: the
   24 in SE4 console the photos show stands higher (ref_02: its top 1.55).
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the crank axle.
"""
import math

LOOK = {
    "frame": dict(color=(0.022, 0.022, 0.024), rough=0.4, metal=0.3, coat=0.2),                     # black frame
    "shroud": dict(color=(0.018, 0.018, 0.019), rough=0.42, coat=0.25),                            # the moulded body
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "silver": dict(color=(0.62, 0.63, 0.65), rough=0.25, metal=1.0, coat=0.2),                     # the crank arms
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0, spec=0.3),                         # the grips
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.72, coat=0.0, spec=0.3),                                 # the saddle
    "screen": dict(color=(0.01, 0.012, 0.016), rough=0.08, coat=1.0),
    "glow": dict(color=(0.20, 0.55, 0.30), rough=0.4, coat=0.0, emit=0.6),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "vent": dict(color=(0.07, 0.07, 0.075), rough=0.6, coat=0.0),
    "red": dict(color=(0.55, 0.02, 0.02), rough=0.4, coat=0.1),                                    # the seat lever
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-135, 18, 1.2)}   # ref_01's angle: from behind the rider's left, a little above
DETAILS = {
    "detail_crank": ((0.75, -0.45, 0.45), (0.15, 0.0, 0.25), 45),        # the crank, its cover, a pedal
    "detail_seat": ((0.65, 0.75, 1.05), (0.10, 0.30, 0.85), 45),         # the saddle, its lever, the post in the sleeve
    "detail_bar": ((0.75, 0.10, 1.55), (0.0, -0.40, 1.20), 45),          # the handlebar, the cradle, the console
}
SETTINGS = ("seat_low", "seat_high")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

# ---- the base (ref_02: a stabilizer under each end of the body, wheels on the front one)
Y_FS, Y_RS = -0.60, 0.20             # the front and rear stabilizers' centres (ref_02: x 305 / 712 px)
X_ST = 0.31                          # their half length (62 cm)
ST = (0.09, 0.085)                   # their section: depth, height (their top 0.10, the body's foot)
# ---- the body (ref_02, (y, z) from px: y = (x - 590) / 476, z = (900 - y) / 476)
HB = 0.11                            # its half width (ref_01: narrow, the cranks just outside the covers)
HF = HB + 0.005                      # the raised side panel's face (ref_01: the logos and the crank's cover on it)
C = (0.0, 0.28)                      # the crank axle (590, 765)
R_C = 0.17                           # the crank's length (170 mm)
R_COV = 0.14                         # the round cover round it (ref_01)
X_PED = HF + 0.10                    # the pedals' centres (x): the pedal's inner face 1 cm out of the arm
# ---- the column, the cradle, the console, the handlebar
COL = ((-0.45, 0.575), (-0.42, 1.033))   # the column's foot (on its collar) and top (into the cradle): (375, 640) / (395, 420)
CN = (-0.64, 1.35)                   # the console's centre: its face's top at (248, 160), bottom at (300, 395)
TILT = 13.0                          # the console tilted back (deg)
# ---- the seat (ref_02 / ref_04)
SL0 = (0.195, 0.664)                 # the sleeve's foot, on the tower's top (ref_01)
SL_A = 17.0                          # the sleeve leans back from upright (deg)
SL_L = 0.03                          # the sleeve's cap above the body's rise (ref_02: the numbered post shows from 600 px up)
HOLE = 0.008                         # one hole of the 42 along the post
N_HOLES = 42
E0 = 0.0                             # the post out of the sleeve at the lowest hole (to the clamp's foot)
PHI = -90.0                          # the left crank's angle (deg from +y toward +z): straight down, the right one up
SEAT_HOLE = None                     # set below for the middle user


def sdir():
    a = math.radians(SL_A)
    return (math.sin(a), math.cos(a))


def seat_top(hole):
    """The saddle's top middle (y, z) at a hole (0 = the lowest)."""
    d = sdir()
    e = SL_L + E0 + hole * HOLE + 0.04              # the sleeve's cap, the post, the clamp's top
    return (SL0[0] + d[0] * e + 0.01, SL0[1] + d[1] * e + 0.08)


def pedal_top(phi):
    a = math.radians(phi)
    return (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a) + 0.025)


def leg(H, hole, knee=145.0):
    """The knee angle (inside) for a user of height H at a seat hole, the pedal at the bottom; returns (knee, ankle, hip)."""
    py, pz = pedal_top(-90.0)
    ay, az = py + 0.48 * 0.152 * H, pz + 0.039 * H     # the ball on the pedal's middle, the heel behind (+y)
    sy, sz = seat_top(hole)
    hy, hz = sy + 0.02, sz + 0.075 * H / 1.78          # the hip joint over the sit bones
    d = math.hypot(hy - ay, hz - az)
    a, b = 0.246 * H, 0.245 * H
    c = max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))
    return math.degrees(math.acos(c)), (ay, az), (hy, hz)


def best_hole(H, knee=145.0):
    return min(range(N_HOLES), key=lambda h: abs(leg(H, h)[0] - knee))


USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ("middle",)


def setting(name):
    global SEAT_HOLE, SHOW
    if name == "seat_low":
        SEAT_HOLE, SHOW = best_hole(1.55), ("short",)
    elif name == "seat_high":
        SEAT_HOLE, SHOW = best_hole(1.95), ("tall",)


SEAT_HOLE = best_hole(1.78)


def arc(c, r, a0, a1, n=8):
    """Points on a circle (y, z) from angle a0 to a1 (deg, from +y toward +z)."""
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def body_outline():
    """The body's side (y, z), counter-clockwise from the front's foot (ref_02 / ref_01): flat on the stabilizers, a
    round over the back, the long flat top, a round over the front, the front leaning forward a little."""
    return ([(-0.59, 0.10), (0.23, 0.10)] + arc((0.23, 0.14), 0.04, -90, 0, 4) + arc((0.17, 0.435), 0.10, 0, 90, 8)
            + arc((-0.56, 0.435), 0.10, 90, 168, 8) + arc((-0.59, 0.14), 0.04, 175, 270, 4))


def tower_outline():
    """The seat's sleeve tower (ref_01): a narrower block standing on the body's back, its front sloping, its top
    level, its back flush with the body's."""
    import kit
    return kit._round_poly([(0.03, 0.529), (0.265, 0.529), (0.265, 0.665), (0.13, 0.67)], 0.03, 4)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    body(k)
    for s in (1, -1):
        crank(k, s)
    column(k)
    seat(k)


def base(k):
    """The two stabilizers (rounded bars across, their ends capped), rubber feet under their ends, two transport wheels
    on the front one's front face."""
    zc = ST[1] / 2 + 0.0155
    for y in (Y_FS, Y_RS):
        k.bar("frame", (-X_ST, y, zc), (X_ST, y, zc), ST[0], ST[1], up=(0, 0, 1), r=0.03)
        for s in (1, -1):
            k.cyl("plastic", (s * (X_ST + 0.005), y, zc), 0.035, 0.01, axis="x", seg=32, soft=0.003)
            k.box("rubber", (s * (X_ST - 0.05), y, 0.008), (0.07, 0.07, 0.016), soft=0.003)
    for s in (1, -1):                                   # the wheels: a bracket off the bar's face, the wheel on its axle
        xw = s * (X_ST - 0.07)
        yw = Y_FS - ST[0] / 2 - 0.045
        for d in (1, -1):                               # the cheeks either side of the wheel, off the bar's face
            k.box("frame", (xw + d * 0.0205, yw + 0.012, 0.06), (0.006, 0.07, 0.05), soft=0.002)
        k.disc("rubber", (xw, yw, 0.048), 0.036, 0.008, 0.035, axis="x", seg=32)
        k.tube("steel", (xw - 0.0245, yw, 0.048), (xw + 0.0245, yw, 0.048), 0.008, seg=12)       # its axle


def body(k):
    """The moulded body on the stabilizers (README point 9: a shroud, not a frame), its logos, a vent strip, the column's
    collar on its front top, the sleeve's collar on its rise."""
    k.slab("shroud", body_outline(), -HB, HB, 0.035, seg=6)
    k.slab("shroud", tower_outline(), -0.07, 0.07, 0.02, seg=4)                                   # the sleeve tower
    panel = k.rounded([(-0.55, 0.14), (0.20, 0.14), (0.22, 0.43), (0.12, 0.49), (-0.53, 0.49), (-0.57, 0.40)], 0.06, 6)
    for s in (1, -1):
        k.slab("shroud", panel, *sorted((s * (HB - 0.001), s * HF)), 0.003, seg=2)                 # the raised side panel
        k.text("label", "Life Fitness", (s * (HF + 0.0003), -0.22, 0.40), 0.045, rz=math.pi / 2 * s, depth=0.0006)
        k.text("label", "LF", (s * (HF + 0.0003), -0.47, 0.40), 0.05, rz=math.pi / 2 * s, depth=0.0006)
        k.box("vent", (s * (HF + 0.0005), -0.22, 0.465), (0.002, 0.30, 0.02), soft=0.0)          # its grip slot
        k.cyl("vent", (s * 0.0705, 0.20, 0.61), 0.006, 0.002, axis="x", seg=16)                   # the tower's pin hole
    k.slab("plastic", k.rounded([(-0.53, 0.53), (-0.37, 0.53), (-0.37, 0.575), (-0.53, 0.575)], 0.015, 3), -0.075, 0.075,
           0.012, seg=3)                                # the column's collar


def crank(k, s):
    """One side: the round cover on the body's wall, the crank arm off the axle's end (a silver hub, ref_03), the pedal on
    its spindle, the toe strap over it."""
    phi = PHI if s > 0 else PHI + 180.0
    a = math.radians(phi)
    P = (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))
    k.cyl("shroud", (s * (HF + 0.006), C[0], C[1]), R_COV, 0.012, axis="x", seg=96, soft=0.004)   # the cover
    k.disc("vent", (s * (HF + 0.0125), C[0], C[1]), R_COV - 0.012, R_COV - 0.016, 0.001, axis="x", seg=96)
    xa = s * (HF + 0.024)
    k.cyl("silver", (s * (HF + 0.025), C[0], C[1]), 0.045, 0.026, axis="x", seg=40, soft=0.003)    # the arm's hub, on the cover
    k.cyl("plastic", (s * (HF + 0.0395), C[0], C[1]), 0.022, 0.003, axis="x", seg=24)             # its cap
    k.bar("silver", (xa, C[0] + (P[0] - C[0]) / R_C * 0.03, C[1] + (P[1] - C[1]) / R_C * 0.03), (xa, P[0], P[1]), 0.045,
          0.022, up=(1, 0, 0), r=0.008)
    k.cyl("silver", (xa, P[0], P[1]), 0.022, 0.026, axis="x", seg=24, soft=0.002)               # the arm's eye
    xp = s * X_PED
    k.cyl("steel", (s * (HF + 0.0425), P[0], P[1]), 0.013, 0.014, axis="x", seg=20, soft=0.001)        # the spindle
    k.box("plastic", (xp, P[0], P[1]), (0.10, 0.13, 0.022), soft=0.006)                          # the pedal
    k.box("rubber", (xp, P[0], P[1] + 0.0115), (0.09, 0.12, 0.002), soft=0.0)                    # its tread
    for d in (1, -1):                                   # its side rims
        k.box("plastic", (xp + d * 0.047, P[0], P[1] + 0.014), (0.008, 0.13, 0.012), soft=0.003)
    # the toe strap (ref_03): a loop over the toes, its feet on the side rims
    loop = [(xp + 0.047 * math.cos(math.radians(a)), P[0] - 0.035, P[1] + 0.02 + 0.045 * math.sin(math.radians(a)))
            for a in range(0, 181, 15)]
    k.sweep("rubber", loop, k.rect(0.006, 0.05, 0.002), up=(0, 1, 0), soft=0.002)


def column(k):
    """The column off its collar up to the cradle; the cradle (a moulded bowl); the handlebar out of the cradle's sides;
    the console on its neck off the cradle's front, a mount box on its back."""
    (y0, z0), (y1, z1) = COL
    k.bar("frame", (0, y0, z0 - 0.003), (0, y1, z1), 0.08, 0.12, up=(0, 1, 0), r=0.025)
    cr = k.rounded([(-0.66, 1.05), (-0.58, 1.03), (-0.30, 1.03), (-0.27, 1.10), (-0.70, 1.11)], 0.025, 4)
    k.slab("shroud", cr, -0.12, 0.12, 0.025, seg=4)                                               # the cradle
    for s in (1, -1):                                   # its two cup bowls (ref_07), off its sides
        k.cyl("shroud", (s * 0.165, -0.44, 1.065), 0.05, 0.08, seg=40, soft=0.008)
        k.cyl("plastic", (s * 0.165, -0.44, 1.104), 0.04, 0.002, seg=40)
    # the handlebar (ref_07, seen from the rider): one stem back out of the cradle to the button hub nearest the rider;
    # from the hub two arms sweep out and forward, then rise into the horns beside the screen
    k.bar("frame", (0, -0.292, 1.075), (0, -0.196, 1.085), 0.05, 0.035, up=(0, 0, 1), r=0.012)     # the stem
    hub = k.rounded([(-0.20, 1.065), (-0.13, 1.065), (-0.12, 1.105), (-0.20, 1.11)], 0.015, 3)
    k.slab("shroud", hub, -0.06, 0.06, 0.012, seg=3)                                              # the button hub
    for s in (1, -1):
        k.box("label", (s * 0.022, -0.15, 1.1065), (0.018, 0.018, 0.002), soft=0.0)              # its + / - keys
        bar = [(s * 0.045, -0.165, 1.085), (s * 0.19, -0.19, 1.09), (s * 0.29, -0.27, 1.12), (s * 0.30, -0.37, 1.22),
               (s * 0.27, -0.45, 1.36)]
        k.sweep("frame", bar, k.circle(0.016, 20), bend=0.07, cut0=((s * 0.06, 0, 0), (s, 0, 0)))

        def on(i, t):                                   # a point on the bar's straight run i -> i + 1
            return tuple(bar[i][j] + (bar[i + 1][j] - bar[i][j]) * t for j in range(3))

        k.sweep("foam", [on(0, 0.45), bar[1], bar[2], bar[3], on(3, 0.93)], k.circle(0.021, 20), bend=0.07, soft=0.003)
        k.sweep("plastic", [on(3, 0.93), on(3, 1.0)], k.circle(0.022, 20), soft=0.002)             # its end cap
    t = math.radians(TILT)
    fn = (0.0, math.cos(t), math.sin(t))                # the console's face, toward the rider
    fu = (0.0, -math.sin(t), math.cos(t))
    cn = (0, CN[0], CN[1])
    k.box("shroud", cn, (0.64, 0.045, 0.42), rx=t, soft=0.02)                                     # 24 in, its housing
    k.box("screen", (0, cn[1] + fn[1] * 0.0228, cn[2] + fn[2] * 0.0228), (0.60, 0.003, 0.37), rx=t, soft=0.0)
    k.box("glow", (0.12, cn[1] + fn[1] * 0.0245 + fu[1] * 0.08, cn[2] + fn[2] * 0.0245 + fu[2] * 0.08), (0.10, 0.002, 0.05),
          rx=t, soft=0.0)
    mb = (0, cn[1] - fn[1] * 0.0465 - fu[1] * 0.07, cn[2] - fn[2] * 0.0465 - fu[2] * 0.07)
    k.box("shroud", mb, (0.24, 0.05, 0.20), rx=t, soft=0.012)                                    # the mount box
    k.text("label", "Life Fitness", (0, mb[1] - fn[1] * 0.0249 + fu[1] * 0.04, mb[2] - fn[2] * 0.0249 + fu[2] * 0.04), 0.025,
           rx=math.pi / 2 + t, depth=0.0005)
    mlow = (0, mb[1] - fu[1] * 0.099, mb[2] - fu[2] * 0.099)
    k.bar("shroud", (0, mlow[1], 1.105), mlow, 0.10, 0.07, up=(0, 1, 0), r=0.02)                  # the neck


def seat(k):
    """The sleeve out of the body's rise, the post in it (its holes marked), the clamp on the post's top, the saddle on
    it; the red lever under the saddle's nose (ref_04)."""
    d = sdir()
    up = (0.0, -d[1], d[0])                             # square to the sleeve, forward-up (its front face)

    def P(e, n=0.0):
        return (SL0[0] + d[0] * e + up[1] * n, SL0[1] + d[1] * e + up[2] * n)

    ax = (0.0, d[0], d[1])
    k.bar("shroud", (0, *P(-0.03)), (0, *P(SL_L)), 0.07, 0.075, up=(0, *up[1:]), r=0.012,
          cut0=((0, 0, SL0[1] - 0.004), (0, 0, 1)))           # the sleeve
    k.bar("plastic", (0, *P(SL_L - 0.004)), (0, *P(SL_L + 0.012)), 0.08, 0.085, up=(0, *up[1:]), r=0.012)   # its cap
    e1 = SL_L + E0 + SEAT_HOLE * HOLE                   # the post's top
    k.bar("frame", (0, *P(SL_L + 0.008)), (0, *P(e1)), 0.05, 0.055, up=(0, *up[1:]), r=0.008)      # the post (on in
                                                        # the sleeve, below its cap: not drawn)
    for i in range(0, N_HOLES, 6):                      # its hole marks, on its front face, every 6th
        e = e1 - 0.05 - i * HOLE                       # the holes count down from the post's top
        if SL_L + 0.014 < e < e1 - 0.01:
            k.box("label", (0, *P(e, -0.0277)), (0.012, 0.003, 0.0015), rx=math.radians(SL_A), soft=0.0)
    k.bar("frame", (0, *P(e1 - 0.004)), (0, *P(e1 + 0.04)), 0.07, 0.10, up=(0, *up[1:]), r=0.01)      # the clamp
    st = seat_top(SEAT_HOLE)
    ct = P(e1 + 0.04)
    y0, z0 = ct[0] - 0.01, ct[1] + 0.009               # the saddle (ref_04): thick and rounded at the back, its top
    side = ([(y0 - 0.16, z0 + 0.012), (y0 + 0.06, z0)] + arc((y0 + 0.06, z0 + 0.03), 0.03, -90, 0, 4)  # running smooth
            + arc((y0 + 0.05, z0 + 0.03), 0.04, 0, 90, 6) + [(y0 - 0.03, z0 + 0.062)]              # to the thinner nose
            + arc((y0 - 0.14, z0 + 0.034), 0.022, 90, 200, 5))

    def hw(y):                                          # wide at the back (0.27), the nose 0.12
        t = max(0.0, min(1.0, (y0 + 0.08 - y) / 0.24))
        return 0.135 - 0.075 * t * t

    k.slab("pad", side, -0.14, 0.14, 0.03, seg=6, halfw=hw)
    k.slab("plastic", [(y0 - 0.10, z0 - 0.013), (y0 + 0.07, z0 - 0.013), (y0 + 0.07, z0 + 0.001), (y0 - 0.10, z0 + 0.001)],
           -0.09, 0.09, 0.005, seg=2)                   # its shell's foot on the clamp                         # the saddle: wide at the back, its nose toward the console
    # the lever: a pivot block on the clamp's front, the red handle out under the nose
    pv = P(e1 + 0.02, 0.05 + 0.006)
    k.box("plastic", (0, pv[0], pv[1]), (0.03, 0.012, 0.03), soft=0.002)
    k.bar("red", (0, pv[0] - 0.006, pv[1]), (0.07, pv[0] - 0.09, pv[1] - 0.012), 0.016, 0.008, r=0.004)
    return st


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        kn, (ay, az), (hy, hz) = leg(H, SEAT_HOLE)
        print(f"fit {label}: seat hole {SEAT_HOLE + 1} of {N_HOLES}, knee {kn:.0f} deg at the bottom", flush=True)
        # the leg's angles (from up, + toward the face, -y): the knee forward of the ankle-hip line
        a, b = 0.246 * H, 0.245 * H
        vy, vz = hy - ay, hz - az
        dd = math.hypot(vy, vz)
        base_ = math.degrees(math.atan2(-vy, vz))
        al = math.degrees(math.acos((a * a + dd * dd - b * b) / (2 * a * dd)))
        be = math.degrees(math.acos((b * b + dd * dd - a * a) / (2 * b * dd)))
        shank, thigh = base_ + al, base_ - be
        ball = (0.0, ay - 0.48 * 0.152 * H, az - 0.039 * H)
        best = None
        for tr in range(0, 46):                         # lean to the loop grips, the elbow nearest 150
            sh = (0.13 * H * 0.85, hy - math.sin(math.radians(tr)) * 0.288 * H, hz + math.cos(math.radians(tr)) * 0.288 * H)
            r = reach(H, sh)
            if best is None or abs(r[4] - 150) < abs(best[1][4] - 150):
                best = (tr, r)
        tr, (a1, l1, a2, l2, elbow) = best
        print(f"fit {label}: trunk {tr} deg forward, elbow {elbow:.0f} deg", flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=shank, thigh=thigh, trunk=tr, neck=-10,
                          stance=2 * X_PED, arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def reach(H, sh):
    """The left arm to the left loop grip; returns body.figure's angles and the elbow's inside angle."""
    g = (0.17, -0.20, 1.11)                             # the arm just out of the hub (ref_02's rear hand)
    f, left = (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w0 = (0.5, 0.2, -0.85)                          # the elbow's way: out, down, a little back
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

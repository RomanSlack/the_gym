"""Hammer Strength Select Chest Press (HS-CP), Charcoal Frame / Black Upholstery. Claude's pick (Roman, 2026-10-23: a
free hand, Life Fitness preferred). Our mechanism (v005, Roman: "yeah looks fine"), rebuilt to the two gates
(equipment/README.md, 2026-10-24): v005 was 2.0 m tall (the maker's 1.63), had no start adjustment and one grip.

DESIGN SPEC (gate 1)
1. Use. Seated facing -y, the back on the pad, the hands beside the chest, pressed forward and a little up. Both arms
   turn together on one level shaft (along x) overhead, just above and behind the shoulders (y 0.10), so the grips
   sweep an arc forward from the chest (a level shaft: a straight press, not converging; noted, not hidden).
2. Moving parts.
   - The shaft: in a bearing block on each side upright's inner face.
   - Each arm: a hub on the shaft on a bushing (free until pinned), hanging forward and down to its foot by the chest.
   - The index plates: one keyed to the shaft beside each hub; each arm's spring pin goes into one of its holes.
   - The cam: keyed to the shaft's middle, over the user's head.
   - The stack: 20 x 15 lb (10-295 lb) on its rods, the open Select tower with its head pulley (stack_tower head=True).
3. Adjustments.
   - Start position: 5 holes per index plate, the arm 20, 27, 35, 42 or 50 deg forward of hanging straight down; the
     grips start from beside the chest (20, a deep stretch) to 0.28 m ahead of it (50, a short range or short arms).
     Life Fitness: "five positions".
   - Seat height: 7 holes (0.40-0.61 m to its top), the grips level with the lower chest.
   - Two grips per arm: a level grip in from the arm's foot (pronated) and a long vertical grip on a J below it
     (neutral, 0.18 m long, so one seat height serves short to tall users).
   - The rest stop: a lug on the back of each index plate against a rubber bumper over it (on a bracket off the cross
     bar's stub); with the stack down the shaft rests there, so the arms rest at the chosen start and can't swing back
     past it.
4. Load path. Hand, grip, arm, hub, pin, index plate, shaft, cam; the cable off the cam's underside, level straight back
   to the head pulley on the tower's deck, down through the deck to the top plate. Winding: pressing swings the arms'
   feet forward (-y), turning the shaft about -x; the cam's underside then moves forward too, away from the tower,
   winding the cable in. Nothing on the cable's run: it passes under the uprights' cross bar and over the pad's column.
5. Fit range. The shoulders sit under the shaft (the back on the pad puts them at y 0.09). At the drawn seat (0.46)
   the shoulders are at 0.98 (1.55 m user) to 1.11 (1.95 m); the neutral grips (x +/-0.42, wider than the shoulders as
   on a bench) hang from about 0.83 to 1.04 at the middle start, the hands a little under the shoulders for all three.
   The start hole sets the depth for the arm's length: the fit run picks each user's (the elbow nearest 75 deg, bent
   back and out): 27 deg for a 1.55 m user (77 deg), the middle 35 for 1.78 m (71), 50 for 1.95 m (77). Head room: the
   cam's underside is 1.47 m up, a 1.95 m user's head at most 1.40.
6. Size. Life Fitness: 104 x 145 x 163 cm (L x W x H). Ours about 0.95 long, 1.32 wide, 1.63 tall: a little narrower
   because the arms hang inside the uprights instead of splaying out on low front pivots.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; s = +1 / -1 the two sides.
"""
import math

import stack_tower

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal
    "lever": dict(color=(0.012, 0.012, 0.013), rough=0.48, metal=0.15, coat=0.0, bump=(1400, 0.07)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7, coat=0.0),
    "plate": dict(color=(0.04, 0.04, 0.042), rough=0.45, metal=0.3, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "cam": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.1),
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "warn": dict(color=(0.9, 0.7, 0.02), rough=0.4, coat=0.0),
    "redplastic": dict(color=(0.75, 0.08, 0.05), rough=0.4, coat=0.1),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.15), "front": (0, 5, 1.15), "side": (90, 3, 1.15), "back_three_quarter": (150, 16, 1.15)}
DETAILS = {
    "detail_shaft": ((0.85, -0.90, 2.05), (0.0, 0.15, 1.52), 50),        # the shaft, the cam, the cable, the cross bar
    "detail_index": ((0.95, -0.55, 1.75), (0.43, 0.10, 1.50), 40),       # the bearing block, index plate, pin, stop
    "detail_grip": ((0.95, -1.00, 1.20), (0.33, -0.12, 0.98), 45),       # an arm's foot, its two grips
    "detail_head": ((0.60, 1.20, 1.90), (0.0, 0.56, 1.42), 45),          # the head pulley, the cable down
}
SETTINGS = ("deep_start",)           # rendered as deep_start_<view>: the arms pinned at 10 deg, the grips by the chest
SETTING_VIEWS = ("three_quarter", "side")
FIT_VIEWS = ("side", "three_quarter")

# ---- heights, from the head room up (spec 4, 5)
Z_RUN = 1.47                         # the cable's level: over a 1.95 m user's head (1.40) when seated
CAM_R = 0.07                         # the cam's bed (its flanges 1 cm proud)
Z_S = Z_RUN + CAM_R + 0.0028         # the shaft
Y_S = 0.10
TOWER_H = Z_RUN - 0.04 - 0.008 - 0.86 * 0.04 - 0.0028   # the tower: its head pulley's groove top level with the run
TOWER = dict(style="open", W=0.56, D=0.30, H=TOWER_H, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="CHEST PRESS", brand="HAMMER STRENGTH", round=1, step=15, start=-5, head=True)
TC = (0.0, 0.56)                     # the tower: behind the pad's column
TY_F, TY_B = TC[1] - TOWER["D"] / 2, TC[1] + TOWER["D"] / 2
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
SQ = 0.076
X_UP = 0.62                          # the side uprights and their floor rails (the arms at +/-0.48: hands wider than the shoulders)
Y_RAIL0 = -0.06                      # the rails' front ends (beside the seat, out of the feet's way)
Y_REAR = TY_B + SQ / 2               # the rear cross bar, against the tower's back
Y_XF = -0.156                        # the seat's cross foot, under its front edge
X_XF = 0.26
# ---- the shaft's parts, out from the middle (spec 2)
X_BLOCK = X_UP - SQ / 2 - 0.025      # the bearing blocks (0.05 wide, on the uprights' inner faces)
X_PLATE = X_BLOCK - 0.025 - 0.002 - 0.005   # the index plates (10 mm, 2 mm off the blocks)
R_PLATE = 0.11
X_ARM = X_PLATE - 0.005 - 0.002 - 0.035     # the arms (their hubs 70 mm long, 2 mm off the plates)
L_ARM = 0.58                         # the shaft to the arm's foot (sized so each user's best hole is in the range)
HOLES = (20.0, 27.0, 35.0, 42.0, 50.0)   # the start positions: the arm's angle forward of hanging straight down
THETA = 35.0                         # this build's (the middle hole); setting() changes it
GRIP_IN = 0.32                       # the level grip's inner end (x)
NEUTRAL = (0.06, 0.18)               # the vertical grip: in from the arm by, and its length
UP_LEVEL, UP_J = 0.10, 0.03          # the level grip and the J leave the arm this far up from its foot
# ---- the seat and the pad (spec 3, 5)
SEAT = (0.0, -0.05, 0.46)            # the seat's top centre
SEAT_P = (0.42, 0.32, 0.08)
PAD = ((0.18, 0.56), (0.21, 1.36), 0.30, 0.08)   # its face (y, z) bottom and top (a slight recline), width, thickness
Y_COL = 0.358                        # the pad's column (its front face just behind the pad's plate)


def setting(name):
    global THETA
    if name == "deep_start":
        THETA = HOLES[0]


def arm_u(theta):
    """Down the arm (y, z) at theta deg forward of hanging straight down."""
    a = math.radians(theta)
    return -math.sin(a), -math.cos(a)


def foot(k, x, y, w=0.09, d=0.09):
    k.box("rubber", (x, y, FOOT_H / 2 + 0.001), (w, d, FOOT_H + 0.002), soft=0.003)


def bar_x(k, mat, y, z, x0, x1, w, h):
    k.bar(mat, (x0, y, z), (x1, y, z), w, h, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    # ---- the base: a floor rail under each upright back to the rear cross bar behind the tower; the spine from the
    # tower's front forward to the seat's cross foot (the floor ahead of the seat left clear for the feet)
    for s in (1, -1):
        x = s * X_UP
        k.bar("frame", (x, Y_RAIL0, RAIL_Z), (x, Y_REAR + SQ / 2, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        k.box("plastic", (x, Y_RAIL0 - 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
        foot(k, x, Y_RAIL0 + 0.04)
        foot(k, x, Y_REAR)
    bar_x(k, "frame", Y_REAR, RAIL_Z, -(X_UP - RAIL[0] / 2), X_UP - RAIL[0] / 2, SQ, RAIL[1])
    k.bar("frame", (-X_XF, Y_XF, RAIL_Z), (X_XF, Y_XF, RAIL_Z), SQ, RAIL[1], r=0.006)
    for s in (1, -1):
        k.box("plastic", (s * (X_XF + 0.004), Y_XF, RAIL_Z), (0.008, SQ + 0.004, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * (X_XF - 0.04), Y_XF)
    k.bar("frame", (0, Y_XF + SQ / 2, RAIL_Z), (0, TY_F + 0.01, RAIL_Z), 0.10, RAIL[1], r=0.008,
          cut0=((0, Y_XF + SQ / 2, 0), Y), cut1=((0, TY_F + 0.01, 0), Y), weld=True)
    k.box("warn", (0.12, Y_XF - SQ / 2 - 0.001, RAIL_Z), (0.045, 0.002, 0.03), soft=0.0)
    # ---- the uprights, their cross bar behind the shaft (over the cable), the bearing blocks, the shaft
    ztop = Z_S + 0.07
    for s in (1, -1):
        x = s * X_UP
        k.bar("frame", (x, Y_S, RAIL_TOP), (x, Y_S, ztop), SQ, SQ, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("plastic", (x, Y_S, ztop + 0.004), (SQ + 0.004, SQ + 0.004, 0.008), soft=0.002)
        k.box("frame", (s * X_BLOCK, Y_S, Z_S), (0.05, 0.10, 0.12), soft=0.005)                 # the bearing block
        for dz in (-0.04, 0.04):
            k.bolt((s * (X_UP + SQ / 2), Y_S, Z_S + dz), "+x" if s > 0 else "-x", size=0.014)
        k.text("label", "HAMMER STRENGTH", (s * (X_UP + SQ / 2 + 0.001), Y_S, 0.90), 0.03, rz=math.pi / 2 * s,
               spin=math.pi / 2, depth=0.0006)
    yx = Y_S + 0.18                                     # the cross bar: behind the plates and stops, over the cable, on two stubs
    k.bar("frame", (-(X_UP + SQ / 2), yx, Z_S), (X_UP + SQ / 2, yx, Z_S), SQ, 0.05)              # back off the uprights
    for s in (1, -1):
        k.box("plastic", (s * (X_UP + SQ / 2 + 0.004), yx, Z_S), (0.008, SQ + 0.004, 0.054), soft=0.002)
        k.bar("frame", (s * X_UP, Y_S + SQ / 2, Z_S), (s * X_UP, yx - SQ / 2, Z_S), SQ, 0.05,
              cut0=((0, Y_S + SQ / 2, 0), (0, 1, 0)), cut1=((0, yx - SQ / 2, 0), (0, 1, 0)), weld=True)
    xb = X_BLOCK + 0.025
    k.tube("steel", (-xb, Y_S, Z_S), (xb, Y_S, Z_S), 0.02, seg=24)                               # the shaft
    # ---- the cam on the shaft's middle, the cable off its underside level back to the head pulley
    k.cyl("cam", (0, Y_S, Z_S), CAM_R, 0.024, axis="x", seg=48, soft=0.002)
    for s in (1, -1):
        k.cyl("cam", (s * 0.015, Y_S, Z_S), CAM_R + 0.01, 0.006, axis="x", seg=48, soft=0.001)
        k.cyl("cam", (s * 0.025, Y_S, Z_S), 0.035, 0.014, axis="x", seg=32, soft=0.003)      # its keyed collars
    ox, oy, oz = tw["cable"]
    k.cable([(0, Y_S, Z_S - CAM_R - 0.0026), (ox, oy, oz)])
    for s in (1, -1):
        side(k, s)
    pad_and_seat(k)


def side(k, s):
    """One side: the index plate (keyed, 5 holes, the stop lug), the stop's bumper on the upright, the hub, the arm,
    the pin, the two grips."""
    xp = s * X_PLATE
    k.cyl("frame", (xp, Y_S, Z_S), R_PLATE, 0.01, axis="x", seg=56, soft=0.002)               # the index plate
    k.cyl("frame", (s * (X_PLATE + 0.006), Y_S, Z_S), 0.03, 0.006, axis="x", seg=24, soft=0.001)   # its keyed collar
    for h in HOLES:
        uy, uz = arm_u(h)
        k.cyl("hole", (xp - s * 0.0052, Y_S + uy * 0.09, Z_S + uz * 0.09), 0.006, 0.001, axis="x", seg=12)
    # the stop: a lug on the plate's back rim; at rest the stack turns the shaft so the lug rises onto the rubber
    # bumper over it, on a bracket off the cross bar's stub (all at the shaft's height, nothing above the uprights)
    yl = Y_S + R_PLATE + 0.009
    k.box("frame", (xp, yl, Z_S), (0.01, 0.018, 0.02), soft=0.001)
    zb = Z_S + 0.01 + 0.002 + 0.009
    k.box("rubber", (xp, yl, zb), (0.022, 0.022, 0.018), soft=0.002)
    k.bar("frame", (s * (X_PLATE + 0.011), yl, zb), (s * (X_UP - SQ / 2), yl, zb), 0.022, 0.018,
          cut1=((s * (X_UP - SQ / 2), 0, 0), (s, 0, 0)), weld=True)
    # the hub, the arm down and forward to its foot, the pin from the arm into the plate (its knob inside)
    xa = s * X_ARM
    k.cyl("lever", (xa, Y_S, Z_S), 0.055, 0.07, axis="x", seg=40, soft=0.004)
    uy, uz = arm_u(THETA)
    a0 = (xa, Y_S + uy * 0.05, Z_S + uz * 0.05)
    F = (xa, Y_S + uy * L_ARM, Z_S + uz * L_ARM)
    k.bar("lever", a0, F, 0.08, 0.05, up=(1, 0, 0))
    k.sweep("plastic", [F, (xa, F[1] + uy * 0.008, F[2] + uz * 0.008)], k.rect(0.084, 0.054, 0.003), up=(1, 0, 0),
            soft=0.002)
    pp = (Y_S + uy * 0.09, Z_S + uz * 0.09)
    k.tube("steel", (xa - s * 0.037, pp[0], pp[1]), (s * (X_PLATE - 0.004), pp[0], pp[1]), 0.006, seg=12)
    k.cyl("redplastic", (xa - s * (0.025 + 0.012), pp[0], pp[1]), 0.016, 0.024, axis="x", seg=20, soft=0.004)
    k.box("warn", (xa + s * 0.026, Y_S + uy * 0.25, Z_S + uz * 0.25), (0.002, 0.04, 0.04), soft=0.0)
    # the grips at the foot: level in from the inner face (pronated); a J in and down to the vertical grip (neutral)
    gl = (F[1] - uy * UP_LEVEL, F[2] - uz * UP_LEVEL)    # up the arm from its foot
    g0 = (xa - s * 0.021, gl[0], gl[1])
    g1 = (s * GRIP_IN, gl[0] + 0.03, gl[1])
    k.tube("lever", g0, g1, 0.016, seg=20)
    k.tube("rubber", (xa - s * 0.06, gl[0] + 0.004, gl[1]), g1, 0.021, soft=0.003)
    ug = tuple((g1[i] - g0[i]) / math.dist(g0, g1) for i in range(3))
    k.sweep("plastic", [g1, tuple(g1[i] + ug[i] * 0.01 for i in range(3))], k.circle(0.022, 20), soft=0.002)
    xn = xa - s * NEUTRAL[0]
    yj, zj = F[1] - uy * UP_J, F[2] - uz * UP_J
    j0 = (xa - s * 0.021, yj, zj)
    j1 = (xn, yj, zj)
    j2 = (xn, yj, zj - NEUTRAL[1] - 0.03)
    k.sweep("lever", [j0, j1, j2], k.circle(0.016, 20), bend=0.03)
    k.tube("rubber", (xn, yj, j2[2] + 0.005), (xn, yj, zj - 0.03), 0.021, soft=0.003)
    k.cyl("plastic", (xn, yj, j2[2] + 0.001), 0.019, 0.008, seg=20, soft=0.002)


def pad_and_seat(k):
    Z = (0, 0, 1)
    (y0, z0), (y1, z1), bw, bt = PAD
    L = math.hypot(y1 - y0, z1 - z0)
    up = (0.0, (y1 - y0) / L, (z1 - z0) / L)
    face = (0.0, -up[2], up[1])
    c = (0.0, (y0 + y1) / 2 - face[1] * bt / 2, (z0 + z1) / 2 - face[2] * bt / 2)
    k.shaped_pad("pad", [(-bw / 2, -L / 2), (bw / 2, -L / 2), (bw / 2, L / 2), (-bw / 2, L / 2)], c, face, (1, 0, 0), bt,
                 r=0.05, cushion=0.03)
    # its plate, two brackets level back into the column's front face; the column off the spine
    sp = tuple(c[i] - face[i] * (bt / 2 + 0.01) for i in range(3))
    s0 = tuple(sp[i] - up[i] * L * 0.40 for i in range(3))
    s1 = tuple(sp[i] + up[i] * L * 0.40 for i in range(3))
    k.bar("frame", s0, s1, 0.16, 0.02, up=face)
    yc = Y_COL - SQ / 2
    for f in (0.2, 0.8):
        q = tuple(s0[i] + (s1[i] - s0[i]) * f for i in range(3))
        back = tuple(q[i] - face[i] * 0.01 for i in range(3))
        k.bar("frame", (0, back[1] - 0.005, back[2]), (0, yc, back[2]), 0.08, 0.05, up=(0, 0, 1),
              cut0=(back, face), cut1=((0, yc, 0), (0, 1, 0)), weld=True)
    zc = s1[2] + 0.02
    k.bar("frame", (0, Y_COL, RAIL_TOP), (0, Y_COL, zc), SQ, SQ, up=(0, 1, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("plastic", (0, Y_COL, zc + 0.004), (SQ + 0.004, SQ + 0.004, 0.008), soft=0.002)
    # the seat on its post: the sleeve with 7 holes, the inner post, the pop pin's handle forward
    sx, sy, sz = SEAT
    bw_ = 0.076
    zt0 = 0.28
    wt = (bw_ - 0.058) / 2
    for qx, qy, w_, d_ in ((1, 0, wt, bw_), (-1, 0, wt, bw_), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (qx * (bw_ - wt) / 2, sy + qy * (bw_ - wt) / 2, (RAIL_TOP + zt0) / 2), (w_, d_, zt0 - RAIL_TOP),
              soft=0.002)
    for i in range(7):
        k.cyl("hole", (0, sy - bw_ / 2 - 0.0005, 0.08 + i * 0.026), 0.007, 0.001, axis="y", seg=14)
    zt = sz - SEAT_P[2] - 0.012
    k.bar("frame", (0, sy, zt0 - 0.08), (0, sy, zt), 0.058, 0.058, up=(0, 1, 0))
    k.box("frame", (0, sy, zt + 0.006), (0.28, 0.24, 0.012), soft=0.002)
    k.pad("pad", (0, sy, sz - SEAT_P[2] / 2), SEAT_P, r=0.035)
    pin_z = zt0 - 0.03
    k.tube("steel", (0, sy - 0.02, pin_z), (0, sy - bw_ / 2 - 0.03, pin_z), 0.007)
    k.sweep("frame", [(0, sy - bw_ / 2 - 0.03, pin_z), (0, sy - bw_ / 2 - 0.09, pin_z - 0.01),
                      (-0.12, sy - bw_ / 2 - 0.12, pin_z - 0.03)], k.circle(0.009, 14), bend=0.03)
    k.cyl("plastic", (0, sy - bw_ / 2 - 0.03, pin_z), 0.016, 0.02, axis="y", seg=20, soft=0.004)


# ---- the fit check (spec 5): three users on the neutral grips, each arm a two-link reach, the elbow printed
def fit():
    out = {}
    r = math.radians
    lean = math.degrees(math.atan2(PAD[1][0] - PAD[0][0], PAD[1][1] - PAD[0][1]))
    for label, H in (("short", 1.55), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        hip = (0.0, PAD[0][0] - 0.11 * sc, SEAT[2] + 0.045 * sc)
        ay, az = hip[1] - 0.36 * sc, 0.039 * H          # the ankle: the feet flat ahead of the knees (forward is -y)
        best = min(((math.hypot(ay - (math.sin(r(sh)) * 0.246 * H + math.sin(r(th)) * 0.245 * H) - hip[1],
                                az + math.cos(r(sh)) * 0.246 * H + math.cos(r(th)) * 0.245 * H - hip[2]), sh, th)
                    for sh in range(-30, 41) for th in range(-120, 0)))
        _, sh, th = best
        ball = (0.0, ay - 0.48 * 0.152 * H, 0.0)
        a1, l1, a2, l2, elbow = reach(H, hip, -lean)
        print(f"fit {label} ({THETA:.0f} deg start): elbow {elbow:.0f} deg", flush=True)
        if THETA == 35.0:                               # which hole suits this user best (the elbow nearest 75 deg)
            keep = THETA
            by = []
            for h in HOLES:
                globals()["THETA"] = h
                by.append((abs(reach(H, hip, -lean)[4] - 75.0), h, reach(H, hip, -lean)[4]))
            globals()["THETA"] = keep
            _, hb, eb = min(by)
            print(f"fit {label}: best start hole {hb:.0f} deg (elbow {eb:.0f})", flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=sh, thigh=th, trunk=-lean, neck=2,
                          arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def reach(H, hip, trunk):
    """The left arm to the left neutral grip, the hand a little under the shoulder; the elbow bent back and out (the
    press's start); returns body.figure's angles and the elbow's inside angle."""
    r = math.radians
    f, left = (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
    sh = (0.13 * H * 0.85, hip[1] - math.sin(r(trunk)) * 0.288 * H, hip[2] + math.cos(r(trunk)) * 0.288 * H)
    uy, uz = arm_u(THETA)
    Fy, Fz = Y_S + uy * (L_ARM - UP_J), Z_S + uz * (L_ARM - UP_J)   # the J's line
    zlo, zhi = Fz - NEUTRAL[1] - 0.025, Fz - 0.035
    g = (X_ARM - NEUTRAL[0], Fy, max(zlo, min(zhi, sh[2] - 0.08)))
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w0 = (0.55, 0.55, -0.62)                        # the elbow's way: out, back and down
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

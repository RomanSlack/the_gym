"""Life Fitness IC7 Indoor Cycle, powered by ICG (refs/: ref_01 a true side view from the drive side (the geometry is
read off it, 657 px per m from the 132 cm length), ref_02 the other side, ref_03 / ref_08 the handlebar, ref_04 the
bar's slider and the STOP knob, ref_05 the drive cover and crank, ref_06 the saddle's slider, ref_07 / ref_11 the seat
post and its lever, ref_09 / ref_10 / ref_12-ref_14 in use). Roman's pick. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Riding, facing -y: seated on the saddle or standing on the pedals, the hands on the bar (its rear corners
   seated, the horns standing or out of the saddle). The knee is the working joint: at the bottom of the stroke it
   stays bent about 30 deg (145 inside); the saddle's height sets that, its fore-aft and the bar set the reach.
2. Moving parts, each mass named (ref_01 / ref_02 / ref_05):
   - The flywheel at the back, under the seat, in a round shroud with a red rim (a rear-flywheel bike).
   - The drive: a belt from the crank's ring back to the flywheel's hub, under a long rounded cover on each side
     ("Life Fitness powered by ICG"); the crank's ring cover, the black cranks, the dual pedals (cage + clip).
   - The frame: one sculpted piece, an upside-down U (the seat tube at the back, the top tube forward over an open
     window, the head tube and the down tube to the crank), closed below by the lower body over the crank and round the
     flywheel's foot; it stands on the arched base (one curved beam, a foot bar across each end: levelers at the back,
     wheels at the front).
   - The seat: a post up out of the seat tube (its height scale on its back, ref_11), clamped by the red lever on the
     seat tube's back (ref_07); on its top the fore-aft slider (a scale +10 to -10, a red knob, ref_06), the saddle on
     its carriage.
   - The bar: a post up out of the head tube, clamped by its red lever; on its top the fore-aft slider (ref_04), the
     multi-position bar (ref_08: a loop round the rider's side, inner horns and outer horns), the console in the middle.
   - The STOP knob on the head tube's top (ref_04): the resistance, pushed down it stops the flywheel.
3. Adjustments (all stepless, a cam lever or a knob clamps each): saddle height (the post, 0-0.25 m out), saddle
   fore-aft (+/-0.10 on the slider), bar height (its post, 0-0.20 out), bar fore-aft (+/-0.06). Each user's setting is
   solved: the saddle's height for a 145 deg knee at the bottom, the bar level with the saddle's top.
4. Load path. The feet on the pedals, the cranks, the ring, the belt, the flywheel's hub; the magnetic brake (inside
   the shroud, not drawn) under the STOP knob's control. The rider's weight: the saddle, the post, the frame, the arch.
5. Fit range. 1.55 / 1.78 / 1.95 m: the saddle and the bar set per user (the fit run prints them); seated, the trunk
   leaning to the bar's rear corners, the elbows soft. Both of the figure's feet on the bottom pedal's spot.
6. Size. Life Fitness: 132 x 52 x 102 cm (L x W x H), Q-factor 155 mm. Ours to those.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the crank axle.
"""
import math

LOOK = {
    "frame": dict(color=(0.02, 0.02, 0.021), rough=0.5, metal=0.2, coat=0.15),                       # satin black
    "shroud": dict(color=(0.016, 0.016, 0.017), rough=0.45, coat=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "redrim": dict(color=(0.55, 0.02, 0.02), rough=0.35, coat=0.3),                                  # the flywheel's rim
    "red": dict(color=(0.6, 0.02, 0.02), rough=0.4, coat=0.1),                                       # the levers, knobs
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "alu": dict(color=(0.35, 0.35, 0.37), rough=0.35, metal=0.9, coat=0.0),                          # the crank's ring
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0, spec=0.3),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.72, coat=0.0, spec=0.3),
    "screen": dict(color=(0.01, 0.012, 0.016), rough=0.08, coat=1.0),
    "glow": dict(color=(0.55, 0.10, 0.08), rough=0.4, coat=0.0, emit=0.6),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-90, 2, 1.25)}      # ref_01: square on from the rider's left
DETAILS = {
    "detail_drive": ((-0.75, 0.10, 0.55), (0.0, 0.20, 0.38), 40),        # the cover, the crank, a pedal
    "detail_seat": ((-0.60, 0.65, 1.10), (0.0, 0.25, 0.82), 45),         # the post, the slider, the saddle
    "detail_bar": ((-0.55, 0.10, 1.25), (0.0, -0.45, 0.92), 45),         # the bar, its slider, the knob
}
SETTINGS = ("rider_short", "rider_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

# ---- (y, z) from ref_01's px: y = (515 - x) / 657, z = (820 - y) / 657
C = (0.0, 0.32)                      # the crank axle (515, 610)
R_C = 0.17                           # the crank (170 mm)
FW = (0.457, 0.449)                  # the flywheel's centre (215, 525)
R_FW = 0.215                         # its shroud's radius (to the red rim)
HW_FRAME = 0.045                     # the frame's half width
HW_LOW = 0.04                        # the lower body's half width at the crank (slim: the 155 mm Q-factor)
X_PED = HW_LOW + 0.092               # the pedals' centres (x): the cranks' outer faces 148 mm apart (Q-factor 155)
Y_RF, Y_FF = 0.63, -0.50             # the rear and front foot bars' centres (x 100 / 845 px)
X_FOOT = 0.26                        # the foot bars' half length (52 cm)
SP0 = (0.205, 0.745)                 # the seat tube's top (380, 335): the seat post comes out here
SP_A = 10.0                          # the post leans back (deg)
BP0 = (-0.30, 0.815)                 # the head tube's top (the bar's post comes out here, (712, 285))
BP_A = 14.0                          # the bar's post leans forward (deg)
SEAT_E, SEAT_F = 0.10, 0.0           # the seat post out of the tube, the slider's offset (+ back)
BAR_E, BAR_F = 0.06, 0.0             # the bar's post out of the head tube, its slider's offset (+ toward the rider)


def sdir(a, sign):
    r = math.radians(a)
    return (sign * math.sin(r), math.cos(r))


def saddle_top(e, f):
    """The saddle's top middle (y, z) for the post out e and the slider at f."""
    d = sdir(SP_A, 1)
    return (SP0[0] + d[0] * e + f - 0.01, SP0[1] + d[1] * e + 0.045 + 0.09)


def bar_top(e, f):
    """The middle of the bar's sides (y, z): where the seated hands go (ref_10)."""
    d = sdir(BP_A, -1)
    return (BP0[0] + d[0] * e + f - 0.06, BP0[1] + d[1] * e + 0.075)


def leg(H, e, f=0.0):
    a_ = math.radians(-90.0)
    py, pz = C[0] + R_C * math.cos(a_), C[1] + R_C * math.sin(a_) + 0.02
    ay, az = py + 0.48 * 0.152 * H, pz + 0.039 * H
    sy, sz = saddle_top(e, f)
    hy, hz = sy + 0.03, sz + 0.075 * H / 1.78
    d = math.hypot(hy - ay, hz - az)
    a, b = 0.246 * H, 0.245 * H
    c = max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))
    return math.degrees(math.acos(c)), (ay, az), (hy, hz)


def settings_for(H):
    """The saddle's height for a 145 deg knee at the bottom (stepless, 1 mm), the bar level with the saddle's top."""
    e = min((i / 1000 for i in range(0, 251)), key=lambda e: abs(leg(H, e)[0] - 145.0))
    st = saddle_top(e, 0.0)
    be = min((i / 1000 for i in range(0, 201)), key=lambda b: abs(bar_top(b, 0.0)[1] - 0.05 - st[1]))
    return e, be


USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ("middle",)
SEAT_E, BAR_E = settings_for(1.78)


def setting(name):
    global SEAT_E, BAR_E, SHOW
    H = {"rider_short": 1.55, "rider_tall": 1.95}[name]
    SEAT_E, BAR_E = settings_for(H)
    SHOW = ({"rider_short": "short", "rider_tall": "tall"}[name],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    frame(k)
    drive(k)
    for s in (1, -1):
        crank(k, s)
    seat(k)
    bar(k)


def base(k):
    """The arch: one curved beam from the rear foot bar up under the lower body and down to the front one (ref_01);
    levelers under the rear bar, wheels on the front bar's front."""
    pts = [(0, Y_RF - 0.03, 0.105), (0, Y_RF - 0.12, 0.11), (0, 0.18, 0.182), (0, -0.15, 0.182), (0, Y_FF + 0.10, 0.11),
           (0, Y_FF + 0.03, 0.105)]                     # its ends level on the foot bars' tops (0.07)
    k.sweep("frame", pts, k.rect(0.10, 0.07, 0.025), bend=0.18, up=(0, 0, 1))
    for y in (Y_RF, Y_FF):
        k.bar("frame", (-X_FOOT, y, 0.045), (X_FOOT, y, 0.045), 0.12, 0.05, up=(0, 0, 1), r=0.02)       # a foot bar
        for s in (1, -1):
            k.cyl("plastic", (s * (X_FOOT + 0.004), y, 0.045), 0.024, 0.008, axis="x", seg=24, soft=0.002)
            k.cyl("rubber", (s * (X_FOOT - 0.05), y, 0.011), 0.025, 0.022, seg=24, soft=0.003)        # levelers
    for s in (1, -1):                                   # the front wheels, on cheeks off the front bar
        xw, yw = s * (X_FOOT - 0.06), Y_FF - 0.06 - 0.035
        for d in (1, -1):
            k.box("frame", (xw + d * 0.0205, yw + 0.015, 0.05), (0.006, 0.06, 0.045), soft=0.002)
        k.disc("rubber", (xw, yw, 0.04), 0.032, 0.008, 0.035, axis="x", seg=32)
        k.tube("steel", (xw - 0.0245, yw, 0.04), (xw + 0.0245, yw, 0.04), 0.008, seg=12)


def frame(k):
    """The sculpted frame: the upper U (seat tube, top tube over the window, head tube, down tube) standing on the
    lower body (over the crank, round the flywheel's foot); the flywheel's shroud with its red rim."""
    import kit
    U = [(0.30, 0.42), (0.26, 0.735), (0.15, 0.745), (0.135, 0.70), (-0.12, 0.545), (-0.185, 0.64), (-0.20, 0.815),
         (-0.40, 0.815), (-0.31, 0.52), (-0.237, 0.42), (-0.10, 0.42), (-0.10, 0.47), (0.08, 0.585), (0.08, 0.42)]
    # (ref_01: the top tube leaves the seat tube near its top and runs down to the head tube's foot, the window under it)
    k.slab("frame", kit._round_poly(U, 0.03, 4), -HW_FRAME, HW_FRAME, 0.02, seg=4)
    L = [(0.30, 0.42), (-0.237, 0.42), (-0.17, 0.30), (-0.05, 0.215), (0.30, 0.215), (0.48, 0.24), (0.52, 0.34)]
    k.slab("frame", kit._round_poly(L, 0.04, 6), -HW_LOW, HW_LOW, 0.025, seg=4)
    k.cyl("shroud", (0, FW[0], FW[1]), R_FW - 0.012, 2 * HW_LOW, axis="x", seg=96, soft=0.008)     # the flywheel's shroud
    k.disc("redrim", (0, FW[0], FW[1]), R_FW, R_FW - 0.013, 2 * HW_LOW + 0.01, axis="x", seg=96)    # its red rim
    for s in (1, -1):
        k.text("label", "IC7", (s * (HW_FRAME + 0.0003), 0.215, 0.70), 0.03, rz=math.pi / 2 * s, depth=0.0006)


def drive(k):
    """The belt covers: a long rounded shape from the flywheel's hub to the crank on each side (ref_05), the logo on
    it; the crank's ring cover."""
    for s in (1, -1):
        x0 = s * HW_LOW
        cov = ([(FW[0] + 0.125 * math.cos(math.radians(a)), FW[1] + 0.125 * math.sin(math.radians(a))) for a in range(-90, 91, 15)]
               + [(C[0] + 0.095 * math.cos(math.radians(a)), C[1] + 0.095 * math.sin(math.radians(a))) for a in range(90, 271, 15)])
        k.slab("shroud", cov, *sorted((x0 - s * 0.002, x0 + s * 0.015)), 0.006, seg=3)
        k.text("label", "Life Fitness", (s * (HW_LOW + 0.0153), 0.24, 0.40), 0.045, rz=math.pi / 2 * s, depth=0.0006)


def crank(k, s):
    """The ring cover over the crank (on the right, the belt side), the crank arm, the dual pedal (cage on top)."""
    phi = -90.0 if s > 0 else 90.0
    a = math.radians(phi)
    P = (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))
    k.disc("alu", (s * (HW_LOW + 0.018), C[0], C[1]), 0.07, 0.03, 0.006, axis="x", seg=48)         # the ring's cover
    xa = s * (HW_LOW + 0.026)
    k.cyl("frame", (xa, C[0], C[1]), 0.03, 0.016, axis="x", seg=32, soft=0.002)
    k.bar("frame", (xa, C[0] + (P[0] - C[0]) / R_C * 0.02, C[1] + (P[1] - C[1]) / R_C * 0.02), (xa, P[0], P[1]), 0.04, 0.016,
          up=(1, 0, 0), r=0.006)
    k.cyl("frame", (xa, P[0], P[1]), 0.018, 0.016, axis="x", seg=24, soft=0.002)
    xp = s * X_PED
    k.cyl("steel", (s * (HW_LOW + 0.04), P[0], P[1]), 0.01, 0.014, axis="x", seg=16)
    k.box("plastic", (xp, P[0], P[1]), (0.09, 0.11, 0.025), soft=0.006)                           # the pedal's body
    k.box("alu", (xp, P[0], P[1] - 0.0135), (0.05, 0.05, 0.002), soft=0.0)                         # its clip side
    loop = [(xp + 0.042 * math.cos(math.radians(g)), P[0] - 0.03, P[1] + 0.012 + 0.04 * math.sin(math.radians(g)))
            for g in range(0, 181, 15)]
    k.sweep("plastic", loop, k.rect(0.006, 0.04, 0.002), up=(0, 1, 0), soft=0.002)                 # the toe cage


def seat(k):
    """The post up out of the seat tube (its scale on its back), the red lever on the tube's back, the slider on the
    post's top (scale, red knob), the saddle on its carriage."""
    d = sdir(SP_A, 1)
    top = (SP0[0] + d[0] * SEAT_E, SP0[1] + d[1] * SEAT_E)
    k.bar("frame", (0, SP0[0] - d[0] * 0.02, SP0[1] - d[1] * 0.02), (0, *top), 0.045, 0.045, up=(0, 1, 0), r=0.006,
          cut0=((0, 0, SP0[1] - 0.007), (0, 0, 1)))     # the post (its foot in the tube, not drawn)
    for i in range(0, int(SEAT_E * 100) - 1, 2):        # its scale, every 2 cm, on its back
        e = 0.01 + i / 100
        k.box("label", (0, SP0[0] + d[0] * e + 0.0228, SP0[1] + d[1] * e), (0.012, 0.0015, 0.0015), soft=0.0)
    k.box("plastic", (0, 0.278, 0.70), (0.03, 0.02, 0.03), soft=0.004)                    # the lever's pivot, on the
    k.box("red", (0, 0.289, 0.68), (0.02, 0.016, 0.06), rx=math.radians(-20), soft=0.004)   # tube's back; the lever
    # the slider: a rail along y on the post's top, its scale, the red knob; the carriage on it, the saddle
    zr = top[1] + 0.022
    k.box("frame", (0, top[0], zr), (0.045, 0.26, 0.04), soft=0.006)
    for j in range(-10, 11, 2):
        k.box("label", (-0.0226, top[0] + j * 0.01, zr), (0.0015, 0.0015, 0.012), soft=0.0)
    k.cyl("red", (0.045, top[0] + 0.10, zr), 0.022, 0.016, axis="x", seg=24, soft=0.003)           # the knob
    k.cyl("frame", (0.03, top[0] + 0.10, zr), 0.008, 0.016, axis="x", seg=12)
    ct = (top[0] + SEAT_F, zr + 0.02 + 0.0125)
    k.box("frame", (0, ct[0], ct[1]), (0.06, 0.10, 0.025), soft=0.004)                             # the carriage
    y0, z0 = ct[0] - 0.01, ct[1] + 0.0125
    side = ([(y0 - 0.16, z0 + 0.012), (y0 + 0.06, z0)] + arc((y0 + 0.06, z0 + 0.03), 0.03, -90, 0, 4)
            + arc((y0 + 0.05, z0 + 0.03), 0.04, 0, 90, 6) + [(y0 - 0.03, z0 + 0.058)] + arc((y0 - 0.14, z0 + 0.032), 0.02, 90, 200, 5))

    def hw(y):                                          # a sport saddle: 0.16 at the back, the nose 0.06
        t = max(0.0, min(1.0, (y0 + 0.08 - y) / 0.22))
        return 0.08 - 0.05 * t ** 1.5

    k.slab("pad", side, -0.08, 0.08, 0.02, seg=5, halfw=hw)


def arc(c, r, a0, a1, n=8):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def bar(k):
    """The bar's post up out of the head tube (forward 14 deg), its red lever; the slider on its top; the multi-position
    bar (ref_08) on it: the loop round the rider's side, the inner and outer horns; the console in the middle; the STOP
    knob on the head tube."""
    d = sdir(BP_A, -1)
    top = (BP0[0] + d[0] * BAR_E, BP0[1] + d[1] * BAR_E)
    k.bar("frame", (0, BP0[0] - d[0] * 0.02, BP0[1] - d[1] * 0.02), (0, *top), 0.05, 0.05, up=(0, 1, 0), r=0.006,
          cut0=((0, *BP0), (0, 0, 1)))
    k.box("plastic", (0, -0.398, 0.755), (0.03, 0.03, 0.03), soft=0.004)                  # its lever's pivot, on the
    k.box("red", (0, -0.418, 0.72), (0.02, 0.012, 0.06), rx=math.radians(-20), soft=0.004)   # head tube's front
    zr = top[1] + 0.02
    k.box("frame", (0, top[0], zr), (0.05, 0.20, 0.035), soft=0.006)                              # the slider
    mt = (top[0] + BAR_F, zr + 0.0175 + 0.015)
    k.box("frame", (0, mt[0], mt[1]), (0.08, 0.09, 0.03), soft=0.006)                              # the bar's mount
    zb = mt[1] + 0.015 + 0.016                          # the bar's centre line
    yb = mt[0]
    for s in (1, -1):
        loop = [(s * 0.035, yb, zb), (s * 0.08, yb + 0.10, zb), (s * 0.24, yb + 0.10, zb), (s * 0.255, yb - 0.12, zb),
                (s * 0.24, yb - 0.30, zb + 0.03), (s * 0.20, yb - 0.37, zb + 0.10)]
        k.sweep("frame", loop, k.circle(0.016, 20), bend=0.05, cut0=((s * 0.04, 0, 0), (s, 0, 0)))
        k.sweep("foam", loop[1:-1] + [(s * 0.205, yb - 0.363, zb + 0.09)], k.circle(0.0205, 20), bend=0.05, soft=0.003)
        k.sweep("plastic", [(s * 0.20, yb - 0.37, zb + 0.10), (s * 0.197, yb - 0.375, zb + 0.108)], k.circle(0.021, 20),
                soft=0.002)
        inner = [(s * 0.035, yb - 0.02, zb), (s * 0.09, yb - 0.06, zb), (s * 0.10, yb - 0.26, zb + 0.02),
                 (s * 0.10, yb - 0.31, zb + 0.08)]       # the inner horns (ref_08)
        k.sweep("frame", inner, k.circle(0.015, 20), bend=0.04, cut0=((s * 0.04, 0, 0), (s, 0, 0)))
        k.sweep("foam", inner[1:], k.circle(0.019, 20), bend=0.04, soft=0.003)
    k.box("frame", (0, yb, zb), (0.08, 0.06, 0.04), soft=0.006)                                    # the bar's clamp
    k.box("shroud", (0, yb - 0.06, zb + 0.08), (0.11, 0.025, 0.16), rx=math.radians(20), soft=0.008)   # the console
    k.box("glow", (0, yb - 0.048, zb + 0.084), (0.09, 0.002, 0.12), rx=math.radians(20), soft=0.0)
    k.bar("frame", (0, yb - 0.02, zb + 0.015), (0, yb - 0.055, zb + 0.008), 0.04, 0.03, up=(0, 0, 1), r=0.006)
    # the STOP knob on the head tube's top, behind the bar's post
    k.cyl("frame", (0, -0.235, 0.815 + 0.015), 0.015, 0.03, seg=20)
    k.cyl("red", (0, -0.235, 0.815 + 0.04), 0.03, 0.025, seg=32, soft=0.004)


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        kn, (ay, az), (hy, hz) = leg(H, SEAT_E)
        print(f"fit {label}: saddle post {SEAT_E * 100:.1f} cm out, bar post {BAR_E * 100:.1f} cm, knee {kn:.0f} deg", flush=True)
        a, b = 0.246 * H, 0.245 * H
        vy, vz = hy - ay, hz - az
        dd = math.hypot(vy, vz)
        base_ = math.degrees(math.atan2(-vy, vz))
        al = math.degrees(math.acos((a * a + dd * dd - b * b) / (2 * a * dd)))
        be = math.degrees(math.acos((b * b + dd * dd - a * a) / (2 * b * dd)))
        shank, thigh = base_ + al, base_ - be
        ball = (0.0, ay - 0.48 * 0.152 * H, az - 0.039 * H)
        gy, gz = bar_top(BAR_E, BAR_F)
        g = (0.25, gy, gz)
        best = None
        for tr in range(10, 70):
            sh = (0.13 * H * 0.85, hy - math.sin(math.radians(tr)) * 0.288 * H, hz + math.cos(math.radians(tr)) * 0.288 * H)
            r = reach(H, sh, g)
            if best is None or abs(r[4] - 150) < abs(best[1][4] - 150):
                best = (tr, r)
        tr, (a1, l1, a2, l2, elbow) = best
        print(f"fit {label}: trunk {tr} deg forward, elbow {elbow:.0f} deg", flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=shank, thigh=thigh, trunk=tr, neck=-25,
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

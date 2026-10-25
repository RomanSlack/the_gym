"""Life Fitness Row HX Trainer, a water rower, ash rails (refs/: ref_01 the maker's three-quarter, ref_06 a true side
view (the geometry is read off it: 451 px per m from the 213 cm length, the floor at 663 px), ref_02 / ref_05 tipped up
on its wheels for storage, ref_03 / ref_04 in use (the finish, the catch), ref_07 the console). Roman's pick. Built to
the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Seated on the sliding seat facing -y, the feet strapped to the foot plates on the inclined footboard, the
   hands on the handle. The stroke: from the catch (knees up, shins near upright, arms long, the trunk forward) the legs
   drive the seat back, the trunk swings back, the arms pull the handle to the lower ribs (the finish); the recovery
   reverses it. The knee and the hip do the work, the seat rolls with them.
2. Moving parts, each mass named (ref_01 / ref_06):
   - The rails: two ash beams on rubber feet, a black aluminium track on each top, a wooden cross block joining them
     at the back; at the front they run into the wooden base under the tank.
   - The seat: a wooden carriage on four rollers riding the tracks, the moulded seat on it (its top 29 cm up).
   - The tank: a clear barrel of water (a red band round its middle) on the base, the paddle inside on a vertical
     shaft; the shaft's top carries the drum the strap winds on (red collar on the lid).
   - The arch: one black steel frame over the tank from the base at the front, along the top, down the back into the
     footboard; it carries the shaft's top bearing, the strap's guide pulley, the handle's rest and the console.
   - The footboard: a black plate inclined 48 deg off the tracks to the arch, two foot plates on it with heel cups
     and red straps.
   - The handle: a bar across, the strap from its middle forward over the guide pulley to the drum (pulling unwinds
     the drum and spins the paddle; a bungee winds it back, inside the arch, not drawn).
   - Two wheels on the front end: tipped up, the rower stands on them and rolls (ref_02 / ref_05).
3. Adjustments. The foot plates slide along the footboard (heel cup height for the foot's size, five positions); the
   straps. The seat is free on its tracks (no adjustment: each user's legs set where it rolls to).
4. Load path. The handle, the strap, the guide pulley, the drum, the shaft, the paddle in the water. The rider's push:
   the feet into the foot plates, the footboard, the arch and the rails.
5. Fit range. 1.55 / 1.78 / 1.95 m: at the finish the knees near straight (170 deg) set where each user's seat rolls
   to, the trunk back 20 deg, the handle at the lower ribs; at the catch the knees 85 deg, the shins near upright,
   the trunk forward 25 deg, the arms long to the handle over the footboard's head. The default
   build shows the middle user at the catch; the finish settings show each user with the seat and handle where they go.
6. Size. Life Fitness: 213 x 52 x 56 cm (L x W x H), the seat 29 cm off the floor. Ours to those.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the tank's axis.
"""
import math

LOOK = {
    "ash": dict(color=(0.46, 0.17, 0.065), rough=0.45, coat=0.25,                                    # the rails (oiled ash)
                grain=dict(dark=(0.33, 0.11, 0.04), scale=18.0, distortion=2.0, along="Z")),   # along the beams
    "frame": dict(color=(0.02, 0.02, 0.021), rough=0.45, metal=0.3, coat=0.15),
    "track": dict(color=(0.03, 0.03, 0.032), rough=0.35, metal=0.6, coat=0.1),                    # black anodised
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "tank": dict(color=(0.92, 0.93, 0.94), rough=0.02, coat=0.0, trans=1.0),                      # clear barrel
    "water": dict(color=(0.10, 0.12, 0.13), rough=0.02, coat=0.0, trans=0.6),
    "red": dict(color=(0.6, 0.02, 0.02), rough=0.4, coat=0.1),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.02, 0.02, 0.021), rough=0.7, coat=0.0, spec=0.3),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.72, coat=0.0, spec=0.3),
    "strap": dict(color=(0.05, 0.05, 0.055), rough=0.6, coat=0.0),
    "screen": dict(color=(0.35, 0.38, 0.34), rough=0.3, coat=0.3),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "labeld": dict(color=(0.03, 0.03, 0.03), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-140, 24, 1.15)}  # ref_01: from behind the rider's left, above
DETAILS = {
    "detail_tank": ((0.85, -0.60, 0.85), (0.0, 0.0, 0.32), 40),          # the tank, the arch, the drum, the console
    "detail_seat": ((0.70, 1.55, 0.65), (0.0, 1.05, 0.22), 45),          # the seat on its carriage, the tracks
    "detail_feet": ((0.70, 0.95, 0.80), (0.0, 0.38, 0.30), 45),          # the footboard, the plates, the straps
}
SETTINGS = ("finish", "finish_short", "finish_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

# ---- (y, z) from ref_06's px: y = (822 - x) / 451, z = (663 - y) / 451
Y_BACK, Y_FRONT = 1.73, -0.395       # the rails' back end (41 px) and the base's front (1000 px)
X_RAIL, RAIL_W = 0.165, 0.07         # the rails' centres and width (ref_01: just wider than the seat)
RAIL_Z = (0.027, 0.10)               # the ash beam's foot and top (651 / 618 px)
TRACK_H = 0.035                      # the black track on top (616-600 px): its top 0.135
Y_BASE = 0.40                        # the base under the tank starts here (the rails' front ends, 640 px)
BASE_Z = (0.027, 0.13)               # its foot and top (651 / 604 px)
TANK_R, TANK_Z = 0.235, (0.13, 0.39)  # the barrel: radius (52 cm wide), its foot and top (604 / 485 px)
ARCH = [(0.0, -0.31, 0.13), (0.0, -0.31, 0.47), (0.0, -0.26, 0.53), (0.0, 0.12, 0.53), (0.0, 0.24, 0.43)]   # front leg,
                                     # the top (423-445 px at 850-905 px), down the back to the footboard's head
FOOT0, FOOT1 = (0.46, 0.135), (0.25, 0.40)   # the footboard: its foot on the tracks (620 px) and its head (720 px)
SEAT_TOP = 0.29                      # the seat's top (Life Fitness)
CATCH_Y = 0.78                       # the seat at the catch (the middle user)
SEAT_Y = CATCH_Y
HANDLE = None                        # (y, z) of the handle's middle; None = at rest on its hooks
SHOW = ("middle",)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
POSE = "catch"


def fdir():
    dy, dz = FOOT1[0] - FOOT0[0], FOOT1[1] - FOOT0[1]
    L = math.hypot(dy, dz)
    return (dy / L, dz / L), L


def plate_pt():
    """The foot plates' middle on the footboard (40 % up), the ball's point (y, z) and the sole's angle."""
    (dy, dz), L = fdir()
    t = 0.42 * L
    n = (dz, -dy)                                       # out of the board toward the rider (+y, up)
    p = (FOOT0[0] + dy * t + n[0] * 0.045, FOOT0[1] + dz * t + n[1] * 0.045)
    return p, math.degrees(math.atan2(dz, -dy))


def ankle_of(H):
    (by, bz), sole = plate_pt()
    s = math.radians(sole)
    so, su = (-math.cos(s), math.sin(s)), (math.sin(s), math.cos(s))
    Lf = 0.152 * H
    return (by - so[0] * 0.48 * Lf + su[0] * 0.039 * H, bz - so[1] * 0.48 * Lf + su[1] * 0.039 * H), (by, bz), sole


def rest_handle():
    """The handle at rest on its hooks (their tops, out of the footboard's face, ref_01)."""
    (dy, dz), _ = fdir()
    n = (dz, -dy)
    return (FOOT1[0] - dy * 0.03 + n[0] * (0.054 + 0.03 + 0.0135), FOOT1[1] - dz * 0.03 + n[1] * (0.054 + 0.03 + 0.0135))


def hip_z(H):
    return SEAT_TOP + 0.075 * H / 1.78


def seat_for(H, knee):
    """Where the seat rolls to (its middle, y) for a knee angle: the hip on the seat at that distance from the ankle."""
    (ay, az), _, _ = ankle_of(H)
    a, b = 0.246 * H, 0.245 * H
    d = math.sqrt(a * a + b * b - 2 * a * b * math.cos(math.radians(knee)))
    hz = hip_z(H)
    return ay + math.sqrt(max(0.0, d * d - (hz - az) ** 2)) - 0.03


def setting(name):
    global SEAT_Y, HANDLE, SHOW, POSE
    H = {"finish": 1.78, "finish_short": 1.55, "finish_tall": 1.95}[name]
    SHOW = ({"finish": "middle", "finish_short": "short", "finish_tall": "tall"}[name],)
    SEAT_Y = seat_for(H, 170.0)
    POSE = "finish"
    hy = SEAT_Y + 0.03
    HANDLE = (hy - 0.06 - math.sin(math.radians(20)) * 0.0, hip_z(H) + 0.20 * H / 1.78)   # at the lower ribs


SEAT_Y = seat_for(1.78, 85.0)                           # the catch: the knees up, the shins near upright, arms long


def catch_handle(H):
    """At the catch the handle is just over the footboard's head, out past the shins (ref_04)."""
    ry, rz = rest_handle()
    return (ry - 0.02, rz + 0.08)


HANDLE = catch_handle(1.78)


def arc(c, r, a0, a1, n=8):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    rails(k)
    tank(k)
    arch(k)
    footboard(k)
    seat(k)
    handle(k)


def rails(k):
    """The two ash beams on rubber feet, the black track on each, the cross block at the back, the base at the front,
    the wheels on its front end."""
    z0, z1 = RAIL_Z
    for s in (1, -1):
        k.box("ash", (s * X_RAIL, (Y_BACK + Y_BASE) / 2, (z0 + z1) / 2), (RAIL_W, Y_BACK - Y_BASE + 0.004, z1 - z0), soft=0.004)
        k.box("track", (s * X_RAIL, (Y_BACK - 0.02 + FOOT0[0] - 0.02) / 2, z1 + TRACK_H / 2),
              (0.05, Y_BACK - 0.02 - FOOT0[0] + 0.02, TRACK_H), soft=0.003)
        for y in (Y_BACK - 0.08, 1.0):
            k.box("rubber", (s * X_RAIL, y, z0 / 2), (0.06, 0.08, z0), soft=0.002)
        k.text("labeld", "Life Fitness", (s * (X_RAIL + RAIL_W / 2 + 0.0003), 1.35, 0.064), 0.04, rz=math.pi / 2 * s,
               depth=0.0006)
        for y in (1.62, 0.55):                          # the bolts' heads at the cross members
            k.cyl("plastic", (s * (X_RAIL + RAIL_W / 2 + 0.001), y, 0.06), 0.008, 0.003, axis="x", seg=16)
    k.box("ash", (0, Y_BACK - 0.05, (z0 + z1) / 2), (2 * X_RAIL - RAIL_W + 0.004, 0.10, z1 - z0), soft=0.004)   # back block
    b0, b1 = BASE_Z                                     # the rails run on to the front, deeper under the tank (ref_06)
    for s in (1, -1):
        k.box("ash", (s * X_RAIL, (Y_BASE + Y_FRONT) / 2, (b0 + b1) / 2), (RAIL_W, Y_BASE - Y_FRONT, b1 - b0), soft=0.004)
    for y in (0.0, -0.32):                              # the cross members the tank and the arch stand on
        k.box("ash", (0, y, b1 - 0.03), (2 * X_RAIL - RAIL_W + 0.004, 0.10 if y == 0.0 else 0.08, 0.06), soft=0.004)
    for s in (1, -1):
        k.box("rubber", (s * X_RAIL, Y_FRONT + 0.25, b0 / 2), (0.06, 0.08, b0), soft=0.002)
        k.disc("rubber", (s * (X_RAIL + RAIL_W / 2 + 0.018), Y_FRONT + 0.035, 0.063), 0.034, 0.008, 0.03, axis="x", seg=32)
        k.tube("steel", (s * (X_RAIL + RAIL_W / 2 - 0.002), Y_FRONT + 0.035, 0.063), (s * (X_RAIL + RAIL_W / 2 + 0.035),
               Y_FRONT + 0.035, 0.063), 0.008, seg=12)


def tank(k):
    """The clear barrel on the base (its wall, its floor, the lid ring), the water in it to the MAX line, the red band,
    the shaft up out of the water through the lid, the red collar, the drum the strap winds on."""
    z0, z1 = TANK_Z
    k.cyl("tank", (0, 0, z0 + 0.004), TANK_R, 0.008, seg=96, soft=0.004)                              # its floor
    k.disc("tank", (0, 0, (z0 + z1) / 2 + 0.004), TANK_R, TANK_R - 0.006, z1 - z0 - 0.008, axis="z", seg=96, soft=0.002)
    k.disc("tank", (0, 0, z1 - 0.004), TANK_R, 0.016, 0.008, axis="z", seg=96, soft=0.002)             # the lid ring
    wz = z0 + 0.16                                      # the water (the paddle in it, too dark to see: not drawn)
    k.cyl("water", (0, 0, (z0 + 0.008 + wz) / 2), TANK_R - 0.0065, wz - z0 - 0.008, seg=96, soft=0.0)
    k.disc("red", (0, 0, z0 + 0.14), TANK_R + 0.004, TANK_R - 0.0005, 0.012, axis="z", seg=96)         # the band
    k.tube("steel", (0, 0, wz), (0, 0, z1 + 0.078), 0.012, seg=16)                                    # the shaft
    k.disc("plastic", (0, 0, z1 + 0.006), 0.12, 0.013, 0.012, axis="z", seg=48)                       # the lid's cap
    k.disc("red", (0, 0, z1 + 0.025), 0.04, 0.013, 0.026, axis="z", seg=32)                           # the red collar
    k.disc("frame", (0, 0, z1 + 0.06), 0.035, 0.013, 0.04, axis="z", seg=32)                          # the drum


def arch(k):
    """The black arch: up from the base in front of the tank, along over it (the shaft's top bearing, the guide
    pulley), down the back into the footboard's head; the console on an arm off its back."""
    for s in (1, -1):                                   # two plates, the strap runs between them
        k.sweep("frame", [(s * 0.035, y, z) for _, y, z in ARCH], k.rect(0.035, 0.06, 0.01), bend=0.07, up=(0, 1, 0))
    zt = ARCH[2][2]
    k.box("frame", (0, 0, zt - 0.04), (0.10, 0.10, 0.04), soft=0.006)                                # the bearing block
    k.box("frame", (0, -0.31, ARCH[0][2] + 0.02), (0.085, 0.04, 0.04), soft=0.004)                   # the legs' foot
    gp = (0, 0.12, zt - 0.045)                          # the guide pulley under the top, behind the drum
    k.disc("plastic", (0, gp[1], gp[2]), 0.035, 0.008, 0.02, axis="x", seg=32)
    for c in (1, -1):                                   # its cheeks off the plates' inner faces
        k.box("frame", (c * 0.0145, gp[1], gp[2] + 0.005), (0.004, 0.05, 0.05), soft=0.001)
    # the console (ref_07): on a short arm off the arch's back corner, facing the rider
    t = math.radians(15)
    fn, fu = (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))      # its face toward the rider, tilted up
    cc = (0.10, zt + 0.10)                              # its middle
    k.box("frame", (0, 0.10, zt + 0.023), (0.085, 0.05, 0.008), soft=0.002)                          # a bridge plate
    k.bar("frame", (0, 0.10, zt + 0.025), (0, cc[0] - fn[0] * 0.012, cc[1] - 0.06), 0.03, 0.02, up=(0, 1, 0), r=0.005)
    k.box("plastic", (0, *cc), (0.11, 0.025, 0.15), rx=t, soft=0.008)

    def on(u, v=0.0125):
        return (cc[0] + fn[0] * v + fu[0] * u, cc[1] + fn[1] * v + fu[1] * u)

    k.box("screen", (0, *on(0.015, 0.0128)), (0.08, 0.002, 0.06), rx=t, soft=0.0)
    k.text("label", "Life Fitness", (0, *on(0.058, 0.0127)), 0.012, rz=math.pi, rx=math.radians(75), depth=0.0004)


def footboard(k):
    """The inclined black plate from the tracks to the arch's back, the two foot plates on it (heel cups, red
    straps), the LF badge above them, the handle's hooks at its head."""
    (dy, dz), L = fdir()
    tilt = math.atan2(dz, dy)
    n = (dz, -dy)
    mid = ((FOOT0[0] + FOOT1[0]) / 2 + n[0] * 0.012, (FOOT0[1] + FOOT1[1]) / 2 + n[1] * 0.012)
    k.box("frame", (0, *mid), (0.30, L + 0.02, 0.024), rx=tilt, soft=0.006)
    for s in (1, -1):                                   # the side rails it hangs on (into the tracks' ends)
        k.box("frame", (s * X_RAIL, FOOT0[0] + 0.02, RAIL_Z[1] + TRACK_H / 2), (0.05, 0.05, TRACK_H), soft=0.003)
    (py, pz), sole = plate_pt()
    for s in (1, -1):
        xc = s * 0.075
        c = (py - n[0] * 0.013, pz - n[1] * 0.013)
        k.box("plastic", (xc, *c), (0.12, 0.30, 0.016), rx=tilt, soft=0.004)                         # the foot plate
        heel = (c[0] - dy * 0.15 + n[0] * 0.035, c[1] - dz * 0.15 + n[1] * 0.035)
        k.box("plastic", (xc, *heel), (0.12, 0.016, 0.07), rx=tilt, soft=0.004)                      # its heel cup
        sp = (c[0] + dy * 0.03 + n[0] * 0.05, c[1] + dz * 0.03 + n[1] * 0.05)
        k.box("red", (xc, *sp), (0.125, 0.05, 0.006), rx=tilt, soft=0.002)                           # the strap
        for d in (1, -1):
            k.box("red", (xc + d * 0.062, sp[0] - n[0] * 0.025, sp[1] - n[1] * 0.025), (0.004, 0.05, 0.05), rx=tilt, soft=0.001)
    badge = (FOOT1[0] - dy * 0.06 + n[0] * 0.0245, FOOT1[1] - dz * 0.06 + n[1] * 0.0245)
    k.cyl("label", (0, *badge), 0.03, 0.002, axis="y", seg=32)
    for s in (1, -1):                                   # the handle's hooks either side at the head, on its face
        hk = (FOOT1[0] - dy * 0.03 + n[0] * 0.054, FOOT1[1] - dz * 0.03 + n[1] * 0.054)
        k.box("frame", (s * 0.13, *hk), (0.02, 0.03, 0.06), rx=tilt, soft=0.004)


def seat(k):
    """The wooden carriage on four rollers on the tracks, the moulded seat on two posts."""
    zt = RAIL_Z[1] + TRACK_H
    rz_ = zt + 0.022                                    # the rollers' axles: on the tracks
    cz = zt + 0.05                                      # the carriage's foot
    k.box("ash", (0, SEAT_Y, cz + 0.03), (2 * X_RAIL + 0.08, 0.20, 0.06), soft=0.006)                  # the carriage
    for s in (1, -1):
        for d in (1, -1):
            yr = SEAT_Y + d * 0.065
            k.disc("rubber", (s * X_RAIL, yr, rz_), 0.022, 0.006, 0.02, axis="x", seg=24)
            for c in (1, -1):                           # the cheeks down off the carriage either side of the roller
                k.box("frame", (s * X_RAIL + c * 0.0135, yr, (rz_ + cz) / 2), (0.004, 0.03, cz - rz_ + 0.012), soft=0.001)
            k.tube("steel", (s * X_RAIL - 0.016, yr, rz_), (s * X_RAIL + 0.016, yr, rz_), 0.006, seg=10)
        k.tube("frame", (s * 0.06, SEAT_Y, cz + 0.06), (s * 0.06, SEAT_Y, SEAT_TOP - 0.05), 0.012, seg=16)
    k.shaped_pad("pad", [(-0.17, -0.14), (0.17, -0.14), (0.18, 0.10), (0.15, 0.15), (-0.15, 0.15), (-0.18, 0.10)],
                 (0, SEAT_Y, SEAT_TOP - 0.025), (0, 0, 1), (1, 0, 0), 0.05, r=0.04, cushion=0.008)


def handle(k):
    """The handle: a bar across with foam grips; the strap from its middle forward to the guide pulley, then to the
    drum. At rest it sits on the hooks at the footboard's head."""
    zt = ARCH[2][2]
    gp = (0.12, zt - 0.045 - 0.035)                     # the guide pulley's foot
    hy, hz = HANDLE if HANDLE else rest_handle()
    k.tube("frame", (-0.28, hy, hz), (0.28, hy, hz), 0.014, seg=20)
    for s in (1, -1):
        k.tube("foam", (s * 0.06, hy, hz), (s * 0.27, hy, hz), 0.019, seg=20, soft=0.003)
        k.cyl("plastic", (s * 0.28, hy, hz), 0.02, 0.012, axis="x", seg=20, soft=0.002)
    k.box("frame", (0, hy - 0.02, hz), (0.03, 0.03, 0.03), soft=0.004)                                 # the strap's clip
    k.sweep("strap", [(0, hy - 0.035, hz), (0, gp[0], gp[1])], k.rect(0.025, 0.0025, 0.0), up=(1, 0, 0), soft=0.0)
    k.sweep("strap", [(0, gp[0] - 0.035, gp[1] + 0.035), (0, 0.035, TANK_Z[1] + 0.07)], k.rect(0.025, 0.0025, 0.0),
            up=(1, 0, 0), soft=0.0)


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        (ay, az), ball, sole = ankle_of(H)
        hy, hz = SEAT_Y + 0.03, hip_z(H)
        a, b = 0.246 * H, 0.245 * H
        d = math.hypot(hy - ay, hz - az)
        d = min(d, a + b - 1e-6)
        al = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d))))
        base = math.atan2(hz - az, hy - ay)
        K = (ay + a * math.cos(base + al), az + a * math.sin(base + al))            # the knee up
        if K[1] < az + a * math.sin(base - al):
            K = (ay + a * math.cos(base - al), az + a * math.sin(base - al))
        kn = math.degrees(math.acos(max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))))

        def ang(p, q):
            return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))

        shank, thigh = ang((ay, az), K), ang(K, (hy, hz))
        trunk = -20.0 if POSE == "finish" else 25.0
        sh = (0.13 * H * 0.85, hy - math.sin(math.radians(trunk)) * 0.288 * H, hz + math.cos(math.radians(trunk)) * 0.288 * H)
        g = (0.20, *(HANDLE if HANDLE else rest_handle()))
        a1, l1, a2, l2, elbow = reach(H, sh, g, POSE)
        print(f"fit {label} ({POSE}): seat at y {SEAT_Y:.2f}, knee {kn:.0f} deg, elbow {elbow:.0f} deg", flush=True)
        out[label] = dict(H=H, ball=(0.0, *ball), face=(0, -1), sole=sole, shank=shank, thigh=thigh, trunk=trunk, neck=-trunk * 0.5,
                          stance=0.15, arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def reach(H, sh, g, pose):
    f, left = (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w0 = (0.5, 0.8, -0.2) if pose == "finish" else (0.6, 0.2, -0.75)   # at the finish the elbows go back, out
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

"""Hammer Strength Select Chest Press (HS-CP) as we design it, Charcoal Frame / Black Upholstery, the arms at their start.
Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Roman, 2026-10-24, on the version copied off the maker's renders: "it sucks and doesn't even physically make sense ...
where the wire is running ... design your own, something that actually ergonomically and mechanically makes sense". So
the mechanism is ours, the look Hammer Strength's (refs/ ref_01-ref_03, Charcoal, the open Select tower):
  - one shaft across overhead, above and just behind the user's shoulders, in bearing blocks on two side uprights (a
    cross beam over their tops);
  - both press arms keyed to it, hanging forward and down to the grips beside the chest: pressing swings the grips
    forward and a little up, the converging arc of a plate-loaded press;
  - one cam on the shaft's middle, over the user's head: pressing turns the shaft and the cam's underside winds the
    cable in; the cable runs level straight back to the head pulley on the stack tower's deck and drops straight down
    to the top plate (stack_tower "head" option). One straight run, nothing in its way, nothing at the user;
  - the tower centred behind the back pad; the seat on its adjustable post; a rubber stop on each upright the arms
    rest against at the start (the stack's weight holds them there).
Held to the catalogue's 145 cm width and 295 lb stack (20 x 15 lb, numbered 10 to 295); the overhead shaft makes it
taller than the maker's 163 cm (about 2.0 m) and longer (about 1.36 m).
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left.
"""
import math

import stack_tower

IN = 0.0254
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
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.2), "front": (0, 5, 1.2), "side": (90, 3, 1.2), "back_three_quarter": (150, 16, 1.2)}
DETAILS = {
    "detail_shaft": ((0.95, -1.00, 2.30), (0.0, 0.15, 1.78), 50),         # the shaft, the cam, the hubs, the cable
    "detail_head": ((0.70, 1.30, 2.10), (0.0, 0.48, 1.68), 45),           # the head pulley on the deck, the cable down
    "detail_grip": ((0.95, -1.00, 1.30), (0.38, -0.12, 1.02), 45),        # an arm's foot, its grip, the stop above
}

TOWER = dict(style="open", W=0.56, D=0.30, H=64 * IN, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="CHEST PRESS", brand="HAMMER STRENGTH", round=1, step=15, start=-5, head=True)
TC = (0.0, 0.48)                     # the tower: centred behind the back pad
TY_F, TY_B = TC[1] - TOWER["D"] / 2, TC[1] + TOWER["D"] / 2
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
SQ = 0.076
X_UP = 0.62                          # the side uprights and rails (x): Life Fitness's 145 cm width over the rails' caps
Y0, Y1 = -0.66, TY_B + 0.076         # the side rails' ends
Y_FRONT = -0.62                      # the front cross bar
CAM_R = 0.08                         # the cam's groove (the cable's bed); its flanges stand 1 cm proud
# the shaft: its cam's underside level with the head pulley's top, so the cable runs dead level between them
Z_RUN = TOWER["H"] + 0.04 + 0.008 + 0.04
SHAFT = (0.10, Z_RUN + CAM_R + 0.0028)   # (y, z): above and just behind the shoulders
Z_BEAM = SHAFT[1] + CAM_R + 0.08     # the cross beam over the uprights, clear of the cam
X_ARM = 0.45
FOOT = (-0.14, 1.00)                 # each arm's foot (y, z): the grip there, beside the chest at the start
GRIP = 0.27                          # the grips' inner ends (x)
SEAT = (0.0, -0.04, 0.50)            # the seat's top centre
SEAT_P = (0.42, 0.32, 0.08)
BACK_BOT, BACK_TOP = (0.10, 0.60), (0.15, 1.36)   # the back pad's face (y, z)
BACK = (0.30, 0.08)


def foot(k, x, y, w=0.09, d=0.09):
    k.box("rubber", (x, y, FOOT_H / 2 + 0.001), (w, d, FOOT_H + 0.002), soft=0.003)


def bar_x(k, y, z, x0, x1, w=SQ, h=RAIL[1]):
    k.bar("frame", (x0, y, z), (x1, y, z), w, h, cut0=((x0, 0, 0), (1, 0, 0)), cut1=((x1, 0, 0), (1, 0, 0)), weld=True)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    # ---- the base: side rails, the front cross bar, the rear one against the tower's back, the spine to its front
    for s in (1, -1):
        x = s * X_UP
        k.bar("frame", (x, Y0, RAIL_Z), (x, Y1, RAIL_Z), RAIL[0], RAIL[1], r=0.006)
        for ye, d in ((Y0, -1), (Y1, 1)):
            k.box("plastic", (x, ye + d * 0.004, RAIL_Z), (RAIL[0] + 0.004, 0.008, RAIL[1] + 0.004), soft=0.002)
            foot(k, x, ye - d * 0.05)
    xi = X_UP - RAIL[0] / 2
    bar_x(k, Y_FRONT, RAIL_Z, -xi, xi)
    bar_x(k, TY_B + SQ / 2, RAIL_Z, -xi, xi)
    k.bar("frame", (0, Y_FRONT + SQ / 2, RAIL_Z), (0, TY_F + 0.01, RAIL_Z), 0.10, RAIL[1], r=0.008,
          cut0=((0, Y_FRONT + SQ / 2, 0), Y), cut1=((0, TY_F + 0.01, 0), Y), weld=True)
    k.box("warn", (0.25, Y_FRONT - SQ / 2 - 0.001, RAIL_Z), (0.045, 0.002, 0.03), soft=0.0)
    # ---- the uprights off the side rails, the cross beam over them, the bearing blocks, the shaft
    ys, zs = SHAFT
    for s in (1, -1):
        x = s * X_UP
        k.bar("frame", (x, ys, RAIL_TOP), (x, ys, Z_BEAM - SQ / 2), SQ, SQ, cut0=((0, 0, RAIL_TOP), Z), weld=True)
        k.box("frame", (s * (X_UP - SQ / 2 - 0.03), ys, zs), (0.06, 0.11, 0.13), soft=0.006)     # the bearing block
        for dz in (-0.045, 0.045):
            k.bolt((s * (X_UP + SQ / 2), ys, zs + dz), "+x" if s > 0 else "-x", size=0.014)
        k.text("label", "HAMMER STRENGTH", (s * (X_UP + SQ / 2 + 0.001), ys, 1.05), 0.03, rz=math.pi / 2 * s,
               spin=math.pi / 2, depth=0.0006)
    k.bar("frame", (-(X_UP + SQ / 2), ys, Z_BEAM), (X_UP + SQ / 2, ys, Z_BEAM), SQ, SQ)
    for s in (1, -1):
        k.box("plastic", (s * (X_UP + SQ / 2 + 0.004), ys, Z_BEAM), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)
    xb = X_UP - SQ / 2 - 0.06
    k.tube("steel", (-xb, ys, zs), (xb, ys, zs), 0.02, seg=24)                                   # the shaft
    # ---- the cam on the shaft's middle, the cable off its underside level back to the head pulley
    k.cyl("cam", (0, ys, zs), CAM_R, 0.024, axis="x", seg=48, soft=0.002)                       # the cable's bed
    for s in (1, -1):
        k.cyl("cam", (s * 0.015, ys, zs), CAM_R + 0.01, 0.006, axis="x", seg=48, soft=0.001)    # its flanges
    for s in (1, -1):
        k.cyl("cam", (s * 0.025, ys, zs), 0.035, 0.014, axis="x", seg=32, soft=0.003)            # its keyed collars
    ox, oy, oz = tw["cable"]
    k.cable([(0, ys, zs - CAM_R - 0.0028), (ox, oy, oz)])
    # ---- the arms: keyed hubs on the shaft, down and forward to the feet, the grips in toward the user
    py, pz = SHAFT
    fy, fz = FOOT
    L = math.hypot(fy - py, fz - pz)
    u = (0.0, (fy - py) / L, (fz - pz) / L)             # down the arm
    nb = (0.0, -u[2], u[1])                             # the arm's back face's normal (toward +y)
    nb = nb if nb[1] > 0 else tuple(-c for c in nb)
    for s in (1, -1):
        x = s * X_ARM
        k.tube("lever", (x - 0.045, py, pz), (x + 0.045, py, pz), 0.05, seg=32)                  # the hub
        k.bolt((x + s * 0.045, py, pz + 0.03), "+x" if s > 0 else "-x", size=0.012)              # its key bolt
        top = (x, py + u[1] * 0.048, pz + u[2] * 0.048)
        E = (x, fy, fz)
        k.sweep("lever", [top, E], k.rect(0.09, 0.05, 0.008), up=(1, 0, 0), soft=0.003)
        k.sweep("plastic", [E, (x, fy + u[1] * 0.01, fz + u[2] * 0.01)], k.rect(0.094, 0.054, 0.003), up=(1, 0, 0),
                soft=0.002)
        gb = (x, fy - u[1] * 0.05, fz - u[2] * 0.05)
        g0 = (x - s * 0.021, gb[1], gb[2])
        g1 = (s * GRIP, gb[1] + 0.04, gb[2] - 0.01)
        k.tube("lever", g0, g1, 0.016, seg=20)
        k.tube("rubber", tuple(g0[i] + (g1[i] - g0[i]) * 0.3 for i in range(3)), g1, 0.021, soft=0.003)
        ug = tuple((g1[i] - g0[i]) / math.dist(g0, g1) for i in range(3))
        k.sweep("chrome", [g1, tuple(g1[i] + ug[i] * 0.012 for i in range(3))], k.circle(0.021, 20), soft=0.002)
        k.box("warn", (x + s * 0.026, (py + fy) / 2, (pz + fz) / 2), (0.002, 0.04, 0.04), soft=0.0)
        # the start stop: a stub in off the upright behind the arm, its rubber pad against the arm's back face
        q = (py + (fy - py) * 0.55, pz + (fz - pz) * 0.55)
        dpad, dstub = 0.045 + 0.006, 0.045 + 0.012 + 0.016           # the pad's and the stub's offsets off the arm
        st = (q[0] + nb[1] * dstub, q[1] + nb[2] * dstub)
        k.tube("frame", (s * (X_UP - SQ / 2), st[0], st[1]), (s * (X_ARM - 0.02), st[0], st[1]), 0.016, seg=20)
        rx = math.atan2(-nb[1], nb[2])
        k.box("rubber", (s * X_ARM, q[0] + nb[1] * dpad, q[1] + nb[2] * dpad), (0.04, 0.05, 0.012), rx=rx, soft=0.002)
    # ---- the seat on its post (sleeve, holes, the pop pin's handle reaching forward)
    sx, sy, sz = SEAT
    bw = 0.076
    zt0 = 0.30
    wt = (bw - 0.058) / 2
    for qx, qy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (qx * (bw - wt) / 2, sy + qy * (bw - wt) / 2, (RAIL_TOP + zt0) / 2), (w_, d_, zt0 - RAIL_TOP),
              soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, sy - bw / 2 - 0.0005, 0.12 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = sz - SEAT_P[2] - 0.012
    k.bar("frame", (0, sy, zt0 - 0.06), (0, sy, zt), 0.058, 0.058, up=(0, 1, 0))
    k.box("frame", (0, sy, zt + 0.006), (0.28, 0.22, 0.012), soft=0.002)
    k.pad("pad", (0, sy, sz - SEAT_P[2] / 2), SEAT_P, r=0.035)
    pin_z = zt0 - 0.03
    k.tube("steel", (0, sy - 0.02, pin_z), (0, sy - bw / 2 - 0.03, pin_z), 0.007)
    k.sweep("frame", [(0, sy - bw / 2 - 0.03, pin_z), (0, sy - bw / 2 - 0.09, pin_z - 0.01),
                      (-0.12, sy - bw / 2 - 0.12, pin_z - 0.03)], k.circle(0.009, 14), bend=0.03)
    k.cyl("plastic", (0, sy - bw / 2 - 0.03, pin_z), 0.016, 0.02, axis="y", seg=20, soft=0.004)
    # ---- the back pad on its column off the spine
    (y0, z0), (y1, z1) = BACK_BOT, BACK_TOP
    Lb = math.hypot(y1 - y0, z1 - z0)
    up = (0.0, (y1 - y0) / Lb, (z1 - z0) / Lb)
    face = (0.0, -up[2], up[1])
    c = (0.0, (y0 + y1) / 2 - face[1] * BACK[1] / 2, (z0 + z1) / 2 - face[2] * BACK[1] / 2)
    k.shaped_pad("pad", [(-BACK[0] / 2, -Lb / 2), (BACK[0] / 2, -Lb / 2), (BACK[0] / 2, Lb / 2), (-BACK[0] / 2, Lb / 2)],
                 c, face, (1, 0, 0), BACK[1], r=0.05, cushion=0.03)
    sp = tuple(c[i] - face[i] * (BACK[1] / 2 + 0.02) for i in range(3))
    s0 = tuple(sp[i] - up[i] * Lb * 0.40 for i in range(3))
    s1 = tuple(sp[i] + up[i] * Lb * 0.40 for i in range(3))
    k.bar("frame", s0, s1, 0.16, 0.04, up=face)                                                  # the pad's plate
    q = tuple(s0[i] + (s1[i] - s0[i]) * 0.30 for i in range(3))
    back = tuple(q[i] - face[i] * 0.02 for i in range(3))   # on the plate's back face
    yc = back[1] + 0.02 + SQ / 2                        # the column: straight up off the spine behind the plate
    zc = q[2] + 0.04
    k.bar("frame", (0, yc, RAIL_TOP), (0, yc, zc), SQ, SQ, up=(0, 1, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("plastic", (0, yc, zc + 0.004), (SQ + 0.004, SQ + 0.004, 0.008), soft=0.002)
    k.bar("frame", (0, yc, q[2]), (0, back[1] - 0.01, q[2]), 0.10, 0.05, up=(0, 0, 1),     # the bracket into the plate
          cut0=((0, yc - SQ / 2, 0), (0, -1, 0)), cut1=(back, face), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """On the seat facing -y, the back on the pad, the hands on the grips beside the chest (the start of the press),
    the feet flat in front; for a short, a middle and a tall user (the seat adjusts; shown at one height)."""
    out = {}
    r = math.radians
    lean = math.degrees(math.atan2(BACK_TOP[0] - BACK_BOT[0], BACK_TOP[1] - BACK_BOT[1]))
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        hip = (0.0, BACK_BOT[0] - 0.12 * sc, SEAT[2] + 0.045 * sc)
        ay, az = -0.38, 0.039 * H                       # the ankle: the feet flat in front of the seat
        best = min(((math.hypot(ay - math.sin(r(sh)) * 0.246 * H - math.sin(r(th)) * 0.245 * H - hip[1],
                                az + math.cos(r(sh)) * 0.246 * H + math.cos(r(th)) * 0.245 * H - hip[2]), sh, th)
                    for sh in range(-30, 41) for th in range(-120, 0)))
        _, sh, th = best
        ball = (0.0, ay - 0.48 * 0.152 * H, 0.0)
        arm, forearm, arm_out = reach(H, hip, -lean)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=sh, thigh=th, trunk=-lean, neck=4,
                          arm=arm, forearm=forearm, arm_out=arm_out)
    return out


def reach(H, hip, trunk):
    """The arm angles that put the left hand on the left grip's rubber, the elbow back and out."""
    r = math.radians
    sy = hip[1] - math.sin(r(trunk)) * 0.288 * H
    sz = hip[2] + math.cos(r(trunk)) * 0.288 * H
    sx = 0.13 * H * 0.85
    py, pz = SHAFT
    fy, fz = FOOT
    L = math.hypot(fy - py, fz - pz)
    gy, gz = fy - (fy - py) / L * 0.05, fz - (fz - pz) / L * 0.05
    tx, ty, tz = (X_ARM + GRIP) / 2 - 0.03, gy + 0.02, gz - 0.005

    def miss(arm, fore, out):
        ax, ay, az = math.sin(r(out)), -math.sin(r(arm)), math.cos(r(arm))
        m = math.sqrt(ax * ax + ay * ay + az * az)
        ex, ey, ez = sx + ax / m * 0.186 * H, sy + ay / m * 0.186 * H, sz + az / m * 0.186 * H
        g = 0.191 * H
        hx, hy, hz = ex, ey - math.sin(r(fore)) * g, ez + math.cos(r(fore)) * g
        return math.dist((hx, hy, hz), (tx, ty, tz)) + (0.05 if ey < sy - 0.02 else 0.0)

    best = min(((miss(a, f, o), a, f, o) for a in range(90, 271, 5) for f in range(-60, 181, 5) for o in range(0, 81, 5)))
    _, a0, f0, o0 = best
    best = min(((miss(a0 + da, f0 + df, o0 + do), a0 + da, f0 + df, o0 + do)
                for da in range(-5, 6) for df in range(-5, 6) for do in range(-5, 6)))
    assert best[0] < 0.03, f"the grips are out of reach ({best[0]:.3f} m short)"
    return best[1], best[2], best[3]

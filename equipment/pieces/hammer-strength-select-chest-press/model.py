"""Hammer Strength Select Chest Press (HS-CP), Charcoal Frame / Black Upholstery, the arms at their start. Claude's pick
(Roman, 2026-10-23: a free hand, Life Fitness preferred).

Built by eye from refs/: the maker's renders, ref_01 the front three-quarter, ref_02 from the tower's side, ref_03 from
the other front corner; held to Life Fitness's 41 x 57 x 64 in (104 x 145 x 163 cm, L x W x H), a 295 lb stack (20
plates of 15 lb, the top one 10 lb, numbered 10 to 295 as on the Select Leg Extension).
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left; the tower behind the user's right shoulder.
Structure: the stack tower (shared builder: equipment/blender/stack_tower.py, "open" style) behind and to the right; a
spine from the tower forward to the front beam; the press arms pivoting low at the beam's ends in boxed brackets (a
shaft across between them), rising past the seat to the handles beside the chest; a cam on the right arm's pivot, the
cable back along the floor and up the tower's face to the stack; the seat on its adjustable post (the pop pin's
handle), the tall back pad on a curved column off the spine.
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
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_pivot": ((-1.20, -1.10, 0.60), (-0.50, -0.45, 0.15), 45),     # a bracket, the hub, the cam, the shaft
    "detail_handles": ((0.95, -1.10, 1.35), (0.38, -0.15, 1.00), 45),     # the arm's top and its grip
    "detail_seat": ((0.80, -1.20, 0.80), (0.0, 0.0, 0.45), 45),           # the seat's post, the pop pin's handle
}

TOWER = dict(style="open", W=0.56, D=0.30, H=64 * IN, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="CHEST PRESS", brand="HAMMER STRENGTH", round=1, step=15, start=-5)
TC = (-0.45, 0.36)                   # the tower's footprint centre: behind the user's right shoulder (ref_01)
TY_FRONT = TC[1] - TOWER["D"] / 2    # its front face (y)
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
Y_BEAM = -0.45                       # the front beam (the arms' pivots on its ends)
X_BR = 0.58                          # the pivot brackets (x)
PIV_Z = 0.14
X_ARM = 0.45                         # the arms' plane
ARM = [(-0.45, PIV_Z), (-0.33, 0.58), (-0.12, 1.02)]   # each arm (y, z): up and back from the pivot (ref_03), the grip beside the chest
GRIP = 0.30                          # the grips' inner ends (x)
SEAT = (0.0, -0.01, 0.55)            # the seat's top centre (ref_01)
SEAT_P = (0.42, 0.30, 0.08)
BACK_BOT, BACK_TOP = (0.12, 0.62), (0.20, 1.40)   # the back pad's face (y, z): tall, reclined a little
BACK = (0.30, 0.08)


def foot(k, x, y, w=0.09, d=0.09):
    k.box("rubber", (x, y, FOOT_H / 2 + 0.001), (w, d, FOOT_H + 0.002), soft=0.003)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    # ---- the base: the front beam across, the spine back to the tower's face, a foot under each beam end
    xe = X_BR + 0.04                                    # the beam's ends: under the brackets' outer faces
    k.bar("frame", (-xe, Y_BEAM, RAIL_Z), (xe, Y_BEAM, RAIL_Z), 0.10, RAIL[1], r=0.008)
    for s in (1, -1):
        k.box("plastic", (s * (xe + 0.004), Y_BEAM, RAIL_Z), (0.008, 0.104, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * X_BR, Y_BEAM, 0.12, 0.14)
    yr = TY_FRONT + 0.025                               # the rear cross bar: into the tower's front post (its left one)
    xt = TC[0] + TOWER["W"] / 2                         # the tower's left side
    k.bar("frame", (0.14, yr, RAIL_Z), (xt, yr, RAIL_Z), 0.076, RAIL[1], r=0.006, cut1=((xt, 0, 0), (1, 0, 0)), weld=True)
    k.box("plastic", (0.144, yr, RAIL_Z), (0.008, 0.08, RAIL[1] + 0.004), soft=0.002)
    foot(k, 0.10, yr)
    ys = Y_BEAM + 0.05
    k.bar("frame", (0, ys, RAIL_Z), (0, yr - 0.038, RAIL_Z), 0.10, RAIL[1], r=0.008, cut0=((0, ys, 0), Y),
          cut1=((0, yr - 0.038, 0), Y), weld=True)
    k.box("warn", (0.25, Y_BEAM - 0.051, RAIL_Z), (0.045, 0.002, 0.03), soft=0.0)
    # ---- the pivot brackets on the beam's ends, the shaft across, the arms' hubs on it, the cam on the right
    for s in (1, -1):
        x = s * X_BR
        k.box("frame", (x, Y_BEAM, (RAIL_TOP + PIV_Z + 0.07) / 2), (0.08, 0.12, PIV_Z + 0.07 - RAIL_TOP), soft=0.006)
        k.bolt((x + s * 0.04, Y_BEAM, PIV_Z), "+x" if s > 0 else "-x", size=0.026)
    k.tube("lever", (-(X_BR - 0.04), Y_BEAM, PIV_Z), (X_BR - 0.04, Y_BEAM, PIV_Z), 0.02, seg=24)           # the shaft
    xc = -(X_BR + 0.08)                                 # the cam outside the right bracket, clear of the beam's end
    k.tube("steel", (-(X_BR + 0.04), Y_BEAM, PIV_Z), (xc - 0.02, Y_BEAM, PIV_Z), 0.02, seg=20)
    k.cyl("cam", (xc, Y_BEAM, PIV_Z), 0.095, 0.03, axis="x", seg=48, soft=0.003)
    k.disc("steel", (xc, Y_BEAM, PIV_Z), 0.112, 0.095, 0.026, axis="x", seg=48)          # its grooved rim
    k.bolt((xc - 0.015, Y_BEAM, PIV_Z), "-x", size=0.022)
    # the cable: off the cam's top up and back past the tower's right front post to a pulley beside the tower (on an
    # arm off that post's back face), over it and straight in between the posts to the stack's top pulley
    ox, oy, oz = tw["cable"]
    xr = TC[0] - TOWER["W"] / 2                         # the tower's right side (x)
    yb = TC[1] - TOWER["D"] / 2 + 0.05                  # the right front post's back face (y)
    xp, zp = xr - 0.05, oz - 0.045                      # the pulley (axis y), its top level with the run in
    k.pulley((xp, oy, zp), 0.045, axis="y")
    k.box("frame", (xr - 0.02, (yb + oy - 0.013) / 2, zp), (0.10, oy - 0.013 - yb, 0.05), soft=0.002)   # its arm
    # the low pulley at the tower's foot (on its own floor bracket): the cable from the cam's bottom back along the
    # floor to it, round it and straight up to the top pulley's outer side (ref_01: the cable up the tower's corner)
    xl, yl, zl = xp - 0.045, oy - 0.045, 0.10
    k.pulley((xl, yl, zl), 0.045, axis="x")
    k.box("frame", (xl + 0.033, yl, (zl + 0.025) / 2), (0.04, 0.05, zl + 0.025), soft=0.002)
    k.box("rubber", (xl + 0.033, yl, 0.004), (0.06, 0.08, 0.008), soft=0.002)
    zc = PIV_Z - 0.112                                  # off the cam's bottom, level until clear of its rim
    k.cable([(xc, Y_BEAM + 0.01, zc), (xc, Y_BEAM + 0.15, zc), (xl, yl - 0.10, zl - 0.045), (xl, yl, zl - 0.045)])
    k.cable([(xl, yl + 0.043, zl), (xl + 0.002, oy, zp)])
    k.cable([(xp, oy, zp + 0.045), (ox, oy, oz)])
    # ---- the arms: the hub round the shaft, up and back to the top, the grip in toward the user
    for s in (1, -1):
        x = s * X_ARM
        k.tube("lever", (x - 0.045, Y_BEAM, PIV_Z), (x + 0.045, Y_BEAM, PIV_Z), 0.05, seg=32)
        pts = [(x, y, z) for y, z in ARM]
        u = (0.0, ARM[1][0] - ARM[0][0], ARM[1][1] - ARM[0][1])
        ul = math.hypot(u[1], u[2])
        pts[0] = (x, Y_BEAM + u[1] / ul * 0.048, PIV_Z + u[2] / ul * 0.048)
        k.sweep("lever", pts, k.rect(0.08, 0.06, 0.008), bend=0.12, up=(1, 0, 0), soft=0.003)
        top = pts[-1]
        ut = (0.0, ARM[2][0] - ARM[1][0], ARM[2][1] - ARM[1][1])
        utl = math.hypot(ut[1], ut[2])
        k.sweep("plastic", [top, (x, top[1] + ut[1] / utl * 0.01, top[2] + ut[2] / utl * 0.01)],
                k.rect(0.084, 0.064, 0.003), up=(1, 0, 0), soft=0.002)
        g0 = (x - s * 0.03, top[1] - 0.02, top[2] - 0.03)
        g1 = (s * GRIP, top[1] + 0.16, top[2] - 0.05)
        k.tube("lever", g0, g1, 0.016, seg=20)
        k.tube("rubber", tuple(g0[i] + (g1[i] - g0[i]) * 0.3 for i in range(3)), g1, 0.021, soft=0.003)
        ug = tuple((g1[i] - g0[i]) / math.dist(g0, g1) for i in range(3))
        k.sweep("chrome", [g1, tuple(g1[i] + ug[i] * 0.012 for i in range(3))], k.circle(0.021, 20), soft=0.002)
        k.box("warn", (x + s * 0.031, -0.43, 0.40), (0.002, 0.04, 0.04), soft=0.0)
    # ---- the seat on its post (sleeve, holes, the pop pin's handle reaching forward)
    sx, sy, sz = SEAT
    bw = 0.076
    zs = 0.32
    wt = (bw - 0.058) / 2
    for qx, qy, w_, d_ in ((1, 0, wt, bw), (-1, 0, wt, bw), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (qx * (bw - wt) / 2, sy + qy * (bw - wt) / 2, (RAIL_TOP + zs) / 2), (w_, d_, zs - RAIL_TOP),
              soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, sy - bw / 2 - 0.0005, 0.14 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = sz - SEAT_P[2] - 0.012
    k.bar("frame", (0, sy, zs - 0.06), (0, sy, zt), 0.058, 0.058, up=(0, 1, 0))
    k.box("frame", (0, sy, zt + 0.006), (0.28, 0.22, 0.012), soft=0.002)
    k.pad("pad", (0, sy, sz - SEAT_P[2] / 2), SEAT_P, r=0.035)
    pin = (0, sy - bw / 2, zs - 0.03)
    k.tube("steel", (0, sy - 0.02, pin[2]), (0, sy - bw / 2 - 0.03, pin[2]), 0.007)
    k.sweep("frame", [(0, sy - bw / 2 - 0.03, pin[2]), (0, sy - bw / 2 - 0.09, pin[2] - 0.01),
                      (-0.12, sy - bw / 2 - 0.12, pin[2] - 0.03)], k.circle(0.009, 14), bend=0.03)   # its handle
    k.cyl("plastic", (0, sy - bw / 2 - 0.03, pin[2]), 0.016, 0.02, axis="y", seg=20, soft=0.004)
    # ---- the back pad on its curved column off the spine
    (y0, z0), (y1, z1) = BACK_BOT, BACK_TOP
    L = math.hypot(y1 - y0, z1 - z0)
    up = (0.0, (y1 - y0) / L, (z1 - z0) / L)
    face = (0.0, -up[2], up[1])
    c = (0.0, (y0 + y1) / 2 - face[1] * BACK[1] / 2, (z0 + z1) / 2 - face[2] * BACK[1] / 2)
    k.shaped_pad("pad", [(-BACK[0] / 2, -L / 2), (BACK[0] / 2, -L / 2), (BACK[0] / 2, L / 2), (-BACK[0] / 2, L / 2)],
                 c, face, (1, 0, 0), BACK[1], r=0.05, cushion=0.03)
    sp = tuple(c[i] - face[i] * (BACK[1] / 2 + 0.02) for i in range(3))
    s0 = tuple(sp[i] - up[i] * L * 0.40 for i in range(3))
    s1 = tuple(sp[i] + up[i] * L * 0.40 for i in range(3))
    k.bar("frame", s0, s1, 0.16, 0.04, up=face)                                                  # the pad's plate
    yr = TY_FRONT + 0.025                               # the column: up off the rear cross bar, curving into the plate
    q = tuple(s0[i] + (s1[i] - s0[i]) * 0.25 + face[i] * 0.01 for i in range(3))
    col = [(0, yr, RAIL_TOP), (0, yr + 0.03, 0.40), q]
    k.sweep("frame", col, k.rect(0.076, 0.076, 0.008), bend=0.12, up=(1, 0, 0),
            cut0=((0, 0, RAIL_TOP), Z), cut1=(tuple(sp[i] - face[i] * 0.02 for i in range(3)), face), weld=True)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """On the seat facing -y, the back on the pad, the hands on the grips beside the chest (the start of the press),
    the feet flat on the floor; for a short, a middle and a tall user (the seat adjusts; shown at one height)."""
    out = {}
    lean = math.degrees(math.atan2(BACK_TOP[0] - BACK_BOT[0], BACK_TOP[1] - BACK_BOT[1]))
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        hip = (0.0, BACK_BOT[0] - 0.12 * sc, SEAT[2] + 0.045 * sc)
        # the feet flat behind the arms' shaft (the ankle at y -0.30): the shank and thigh solved from the ankle up to
        # the hip (a two-link reach in the side plane, the knee forward)
        ay, az = -0.30, 0.039 * H
        best = min(((math.hypot(ay - math.sin(math.radians(sh)) * 0.246 * H - math.sin(math.radians(th)) * 0.245 * H
                                - hip[1], az + math.cos(math.radians(sh)) * 0.246 * H
                                + math.cos(math.radians(th)) * 0.245 * H - hip[2]), sh, th)
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
    ty_, tz_ = ARM[-1]
    tx, ty, tz = (X_ARM + GRIP) / 2 - 0.03, ty_ + 0.10, tz_ - 0.07

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

"""Hammer Strength Select Pectoral Fly / Rear Deltoid (HS-PFRD) as we design it, Charcoal Frame / Black Upholstery, set
for the fly, the arms at their start. Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred).

Designed mechanism first (Roman, 2026-10-24: "design your own, something that actually ergonomically and mechanically
makes sense"), the look Hammer Strength's (refs/ref_01, the maker's render: the open Select tower, the pad on a post,
the arms hung overhead):
  - each arm turns on its own vertical shaft directly above a shoulder (the fly's and the rear delt's axis: the
    shoulder joint), in a bearing housing hung under the overhead beam; the arm runs out from its hub, then drops to a
    vertical grip at shoulder height. The fly swings the grips forward round the shoulders to meet in front of the
    chest; for the rear delt the user sits facing the pad and the hub's pop pin re-sets the arm to start in front;
  - each shaft carries a level cam on top of the beam; each cam winds its own cable, which runs level straight back to
    its own head pulley on the tower's deck, down through the deck to the floating pulley on the stack's top plate (one
    cable, looped under it: stack_tower head="twin"), so either arm alone or both lift the stack;
  - the beam on an arm off the main column (behind the back pad, up off the spine, tied to the tower), the tower
    centred behind; the seat on its adjustable post in front of the pad.
About 1.9 m tall, 1.5 m across the grips at the start, 1.3 m long; a 235 lb stack (20 x 12 lb, numbered 5 to 235).
Axes: metres, floor z = 0, the user sits facing -y (the fly), x+ = the user's left.
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
VIEWS = {"three_quarter": (-35, 14, 1.2), "front": (0, 6, 1.2), "side": (90, 3, 1.2), "back_three_quarter": (150, 18, 1.2)}
DETAILS = {
    "detail_top": ((0.90, -0.90, 2.40), (0.0, 0.05, 1.80), 50),           # the beam, the cams, the housings, the hubs
    "detail_head": ((0.70, 1.30, 2.20), (0.0, 0.50, 1.85), 45),           # the twin head pulleys, the cables down
    "detail_grip": ((1.25, -0.60, 1.40), (0.68, 0.10, 1.25), 45),         # an arm's drop and its grip
}

TOWER = dict(style="open", W=0.56, D=0.30, H=1.77, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="PEC FLY / REAR DELT", brand="HAMMER STRENGTH", round=-1, step=12, start=-7, head="twin", twin=0.07)
TC = (0.0, 0.52)
TY_F, TY_B = TC[1] - TOWER["D"] / 2, TC[1] + TOWER["D"] / 2
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
SQ = 0.076
Y_FRONT = -0.58                      # the front cross bar
X_FB = 0.40                          # its half length (feet at its ends)
Y_COL = 0.32                         # the main column (behind the back pad's plate and brackets)
# the overhead: the cams' cable bed level with the head pulleys' tops, so each run is dead level
Z_RUN = TOWER["H"] + 0.04 + 0.008 + 0.86 * 0.04 + 0.0028   # the head pulleys' groove tops
CAM_R = 0.07
Z_BEAM = Z_RUN - 0.028 - SQ / 2      # the beam under the cams (1 cm running clearance under them)
Y_BEAM = 0.02                        # the beam (y): over the shoulders
X_PIV = 0.20                         # each arm's vertical shaft: over its shoulder
Z_HUB = Z_BEAM - SQ / 2 - 0.08 - 0.05   # the hub's centre (under the housing and the index plate)
REACH, Z_DROP = 0.70, 1.24          # the drop's distance from the shaft, its foot's height
Z_GRIP = (Z_DROP - 0.21, Z_DROP + 0.01)   # the fly grip's bottom and top (ref_01: a J off the drop's foot, hanging)
J_OUT = 0.075                        # the fly grip's offset ahead of the drop (the way the arm swings)
START = 15.0                         # the fly's start: each arm out to the side and this far back (deg)
SEAT = (0.0, -0.06, 0.50)
SEAT_P = (0.42, 0.32, 0.08)
BACK = ((0.12, 0.62), (0.12, 1.38), 0.28, 0.08)   # the back pad's face bottom and top (y, z), width, thickness


def foot(k, x, y, w=0.09, d=0.09):
    k.box("rubber", (x, y, FOOT_H / 2 + 0.001), (w, d, FOOT_H + 0.002), soft=0.003)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    # ---- the base: the front cross bar (feet at its ends), the spine back to the tower, a rear cross bar behind it
    k.bar("frame", (-X_FB, Y_FRONT, RAIL_Z), (X_FB, Y_FRONT, RAIL_Z), SQ, RAIL[1], r=0.006)
    for s in (1, -1):
        k.box("plastic", (s * (X_FB + 0.004), Y_FRONT, RAIL_Z), (0.008, SQ + 0.004, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * (X_FB - 0.05), Y_FRONT)
    k.bar("frame", (0, Y_FRONT + SQ / 2, RAIL_Z), (0, TY_F + 0.01, RAIL_Z), 0.10, RAIL[1], r=0.008,
          cut0=((0, Y_FRONT + SQ / 2, 0), Y), cut1=((0, TY_F + 0.01, 0), Y), weld=True)
    yr = TY_B + SQ / 2
    k.bar("frame", (-0.40, yr, RAIL_Z), (0.40, yr, RAIL_Z), SQ, RAIL[1], r=0.006)
    for s in (1, -1):
        k.box("plastic", (s * 0.404, yr, RAIL_Z), (0.008, SQ + 0.004, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * 0.35, yr)
    k.box("warn", (0.20, Y_FRONT - SQ / 2 - 0.001, RAIL_Z), (0.045, 0.002, 0.03), soft=0.0)
    # ---- the main column off the spine up behind the pad, a tie back to the tower, the arm forward to the beam
    zc = Z_BEAM + SQ / 2
    k.bar("frame", (0, Y_COL, RAIL_TOP), (0, Y_COL, zc), SQ, SQ, up=(0, 1, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("plastic", (0, Y_COL, zc + 0.004), (SQ + 0.004, SQ + 0.004, 0.008), soft=0.002)
    k.bar("frame", (0, Y_COL + SQ / 2, 1.30), (0, TY_F, 1.30), 0.06, 0.06, cut0=((0, Y_COL + SQ / 2, 0), Y),
          cut1=((0, TY_F, 0), Y), weld=True)                                                    # the tie to the tower
    k.bar("frame", (0, Y_COL - SQ / 2, Z_BEAM), (0, Y_BEAM + SQ / 2, Z_BEAM), SQ, SQ,
          cut0=((0, Y_COL - SQ / 2, 0), Y), cut1=((0, Y_BEAM + SQ / 2, 0), Y), weld=True)       # the arm forward
    xe = X_PIV + 0.10
    k.bar("frame", (-xe, Y_BEAM, Z_BEAM), (xe, Y_BEAM, Z_BEAM), SQ, SQ)                          # the beam
    for s in (1, -1):
        k.box("plastic", (s * (xe + 0.004), Y_BEAM, Z_BEAM), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)
    k.text("label", "HAMMER STRENGTH", (0, Y_BEAM - SQ / 2 - 0.001, Z_BEAM), 0.03, depth=0.0006)
    # ---- each side: the housing under the beam, the shaft, the cam on top, the hub, the arm, the grip
    rad = math.radians(START)
    for s in (1, -1):
        x = s * X_PIV
        zb = Z_BEAM - SQ / 2
        k.cyl("frame", (x, Y_BEAM, zb - 0.04), 0.045, 0.08, seg=36, soft=0.003)                 # the bearing housing
        zt = Z_BEAM + SQ / 2
        k.tube("steel", (x, Y_BEAM, Z_HUB - 0.04), (x, Y_BEAM, Z_RUN + 0.03), 0.02, seg=20)     # the shaft
        k.cyl("cam", (x, Y_BEAM, zt + 0.009), 0.035, 0.018, seg=32, soft=0.002)                 # its thrust washer
        k.cyl("cam", (x, Y_BEAM, Z_RUN), CAM_R, 0.024, seg=48, soft=0.002)                       # the cam's bed
        for dz in (-0.015, 0.015):
            k.cyl("cam", (x, Y_BEAM, Z_RUN + dz), CAM_R + 0.01, 0.006, seg=48, soft=0.001)      # its flanges
        # the cable: off the cam's outer side level straight back to its head pulley
        ox, oy, oz = tw["cables"][0 if s < 0 else 1]
        dx, dy = ox - x, oy - Y_BEAM
        dl = math.hypot(dx, dy)
        nx, ny = dy / dl, -dx / dl                      # level, across the run
        if nx * s < 0:                                  # the tangent on the cam's outer side: the fly turns the left
            nx, ny = -nx, -ny                           # cam clockwise from above, its outer side moving forward, so
                                                        # the cable winds in (the inner side would pay it out)
        p0 = (x + nx * (CAM_R + 0.0026), Y_BEAM + ny * (CAM_R + 0.0026), Z_RUN)
        k.cable([p0, (ox, oy, oz)])
        # under the housing: the index plate (its ring of holes), the hub; the arm off the hub
        zhb = zb - 0.08                                 # the housing's underside
        k.cyl("frame", (x, Y_BEAM, zhb - 0.005), 0.10, 0.01, seg=48, soft=0.002)                # the index plate
        for a in range(0, 360, 20):
            k.cyl("hole", (x + 0.085 * math.cos(math.radians(a)), Y_BEAM + 0.085 * math.sin(math.radians(a)),
                           zhb - 0.0102), 0.005, 0.001, seg=10)
        k.cyl("lever", (x, Y_BEAM, Z_HUB), 0.055, 0.08, seg=40, soft=0.004)                      # the hub
        ux, uy = s * math.cos(rad), math.sin(rad)
        side_ = (-uy, ux, 0.0)                          # level, across the arm: the section's narrow way
        a0 = (x + ux * 0.05, Y_BEAM + uy * 0.05, Z_HUB)
        a1 = (x + ux * REACH, Y_BEAM + uy * REACH, Z_HUB)
        zd = Z_DROP                                     # the drop's foot
        k.sweep("lever", [a0, a1, (a1[0], a1[1], zd)], k.rect(0.08, 0.05, 0.008), bend=0.08, up=side_, soft=0.003)
        k.sweep("plastic", [(a1[0], a1[1], zd), (a1[0], a1[1], zd - 0.01)], k.rect(0.084, 0.054, 0.003), up=side_,
                soft=0.002)
        # the pop pin: up through the arm into the index plate's holes, its knob under the arm (the start position)
        pp = (x + ux * 0.085, Y_BEAM + uy * 0.085)
        k.tube("steel", (pp[0], pp[1], Z_HUB - 0.05), (pp[0], pp[1], zhb - 0.01), 0.006, seg=12)
        k.cyl("redplastic", (pp[0], pp[1], Z_HUB - 0.04 - 0.012), 0.016, 0.024, seg=20, soft=0.004)
        k.box("warn", (x + ux * 0.40, Y_BEAM + uy * 0.40, Z_HUB + 0.041), (0.04, 0.04, 0.002), rz=rad * s, soft=0.0)
        # the handles (ref_01): the fly grip a J off the drop's front face (the way the arm swings: forward), turned
        # down into a vertical rubber grip; the rear-delt grip level, in from the drop's inner face toward the user
        fx, fy = s * uy, -s * ux                        # ahead of the arm: the fly's swing
        j0 = (a1[0] + fx * 0.02, a1[1] + fy * 0.02, zd + 0.035)
        j1 = (a1[0] + fx * J_OUT, a1[1] + fy * J_OUT, zd + 0.035)
        j2 = (a1[0] + fx * J_OUT, a1[1] + fy * J_OUT, Z_GRIP[0])
        k.sweep("lever", [j0, j1, j2], k.circle(0.016, 20), bend=0.03)
        k.tube("rubber", (j2[0], j2[1], Z_GRIP[0] + 0.005), (j2[0], j2[1], Z_GRIP[1] - 0.02), 0.021, soft=0.003)
        k.cyl("plastic", (j2[0], j2[1], Z_GRIP[0] + 0.001), 0.019, 0.008, seg=20, soft=0.002)
        r0 = (a1[0] - ux * 0.035, a1[1] - uy * 0.035, zd + 0.035)
        r1 = (a1[0] - ux * 0.17, a1[1] - uy * 0.17, zd + 0.035)
        k.tube("lever", r0, r1, 0.016, seg=20)
        k.tube("rubber", (a1[0] - ux * 0.07, a1[1] - uy * 0.07, zd + 0.035), r1, 0.021, soft=0.003)
        k.sweep("plastic", [r1, (r1[0] - ux * 0.008, r1[1] - uy * 0.008, r1[2])], k.circle(0.022, 20), soft=0.002)
    # ---- the back pad on the column
    (y0, z0), (y1, z1), bw, bt = BACK
    c = (0.0, y0 + bt / 2, (z0 + z1) / 2)
    k.shaped_pad("pad", [(-bw / 2, -(z1 - z0) / 2), (bw / 2, -(z1 - z0) / 2), (bw / 2, (z1 - z0) / 2),
                         (-bw / 2, (z1 - z0) / 2)], c, (0, -1, 0), (1, 0, 0), bt, r=0.05, cushion=0.03)
    yp = y0 + bt + 0.02
    k.box("frame", (0, yp, (z0 + z1) / 2), (0.16, 0.04, (z1 - z0) * 0.8), soft=0.002)            # its plate
    for zz in (z0 + 0.15, z1 - 0.15):
        k.bar("frame", (0, yp + 0.02, zz), (0, Y_COL - SQ / 2, zz), 0.08, 0.05, up=(0, 0, 1),
              cut1=((0, Y_COL - SQ / 2, 0), (0, 1, 0)), weld=True)
    # ---- the seat on its post (sleeve, holes, the pop pin's handle forward)
    sx, sy, sz = SEAT
    bw_ = 0.076
    zt0 = 0.30
    wt = (bw_ - 0.058) / 2
    for qx, qy, w_, d_ in ((1, 0, wt, bw_), (-1, 0, wt, bw_), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (qx * (bw_ - wt) / 2, sy + qy * (bw_ - wt) / 2, (RAIL_TOP + zt0) / 2), (w_, d_, zt0 - RAIL_TOP),
              soft=0.002)
    for i in range(5):
        k.cyl("hole", (0, sy - bw_ / 2 - 0.0005, 0.12 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = sz - SEAT_P[2] - 0.012
    k.bar("frame", (0, sy, zt0 - 0.06), (0, sy, zt), 0.058, 0.058, up=(0, 1, 0))
    k.box("frame", (0, sy, zt + 0.006), (0.28, 0.22, 0.012), soft=0.002)
    k.pad("pad", (0, sy, sz - SEAT_P[2] / 2), SEAT_P, r=0.035)
    pin_z = zt0 - 0.03
    k.tube("steel", (0, sy - 0.02, pin_z), (0, sy - bw_ / 2 - 0.03, pin_z), 0.007)
    k.sweep("frame", [(0, sy - bw_ / 2 - 0.03, pin_z), (0, sy - bw_ / 2 - 0.09, pin_z - 0.01),
                      (-0.12, sy - bw_ / 2 - 0.12, pin_z - 0.03)], k.circle(0.009, 14), bend=0.03)
    k.cyl("plastic", (0, sy - bw_ / 2 - 0.03, pin_z), 0.016, 0.02, axis="y", seg=20, soft=0.004)


FIT_VIEWS = ("front", "three_quarter", "side")


def fit():
    """On the seat facing -y, the back on the pad, the arms out to the sides on the grips (the fly's start), the feet
    flat in front; for a short, a middle and a tall user (the seat adjusts; shown at one height)."""
    out = {}
    r = math.radians
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        hip = (0.0, BACK[0][0] - 0.11 * sc, SEAT[2] + 0.045 * sc)
        ay, az = -0.40, 0.039 * H
        best = min(((math.hypot(ay - math.sin(r(sh)) * 0.246 * H - math.sin(r(th)) * 0.245 * H - hip[1],
                                az + math.cos(r(sh)) * 0.246 * H + math.cos(r(th)) * 0.245 * H - hip[2]), sh, th)
                    for sh in range(-30, 41) for th in range(-120, 0)))
        _, sh, th = best
        ball = (0.0, ay - 0.48 * 0.152 * H, 0.0)
        arm, arm_lat, forearm, fore_lat = reach(H, hip)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=sh, thigh=th, trunk=0.0, neck=0,
                          arm=arm, forearm=forearm, arm_lat=arm_lat, fore_lat=fore_lat)
    return out


def reach(H, hip):
    """The left arm to the left grip's middle as a two-link reach (the elbow a little below the shoulder-grip line,
    soft): each segment's direction returned as body.figure's (angle in the side plane, true raise to the side)."""
    sx, sy, sz = 0.13 * H * 0.85, hip[1], hip[2] + 0.288 * H
    rad = math.radians(START)
    ux, uy = math.cos(rad), math.sin(rad)
    gx, gy = X_PIV + ux * REACH + uy * J_OUT, Y_BEAM + uy * REACH - ux * J_OUT   # the fly grip (ahead of the drop)
    gz = (Z_GRIP[0] + Z_GRIP[1]) / 2
    L1, L2 = 0.186 * H, 0.191 * H
    v = (gx - sx, gy - sy, gz - sz)
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2:                                    # out of reach: the arm straight toward the grip
        e = tuple(c * L1 for c in vh)
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w = (0.0, 0.0, -1.0)                            # the elbow's bend: down, off the line
        w = tuple(w[i] - vh[i] * sum(w[j] * vh[j] for j in range(3)) for i in range(3))
        wl = math.sqrt(sum(c * c for c in w))
        w = tuple(c / wl for c in w)
        e = tuple(L1 * (math.cos(al) * vh[i] + math.sin(al) * w[i]) for i in range(3))
    f = tuple(v[i] - e[i] for i in range(3))
    fl = math.sqrt(sum(c * c for c in f))
    f = tuple(c / fl for c in f)
    eh = tuple(c / L1 for c in e)

    def angles(u):                                      # facing -y, the figure's left +x
        lat = math.degrees(math.asin(max(-1.0, min(1.0, u[0]))))
        a = math.degrees(math.atan2(-u[1], u[2]))
        return a, lat

    a1, l1 = angles(eh)
    a2, l2 = angles(f)
    return a1, l1, a2, l2

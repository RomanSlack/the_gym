"""Hammer Strength Select Pectoral Fly / Rear Deltoid (HS-PFRD), Charcoal Frame / Black Upholstery. Claude's pick
(Roman, 2026-10-23: a free hand, Life Fitness preferred). Built to the two gates (equipment/README.md, Roman
2026-10-24): v001-v003 were 1.7 m wide for one wingspan, with rigid arms and a decorative start adjuster.

DESIGN SPEC (gate 1)
1. Use. Fly: seated facing -y, back on the pad, the arms out to the sides with the elbows bent, swept forward round the
   shoulders until the hands meet in front. Rear delt: seated facing +y, chest on the same pad, the arms in front, swept
   back out to the sides. Both turn about the shoulder joint's vertical axis, so each arm turns on a vertical shaft
   directly over a shoulder (x +/-0.20, y 0.01); the red disc under each hub marks the axis to line the shoulder up
   with (Life Fitness: "the axis of rotation marked with a red indicator").
2. Moving parts.
   - Each shaft: vertical, in a bearing housing hung under the overhead beam; turns with its arm.
   - Each arm: a hub on its shaft (on a bushing: free on it until pinned), out level to the drop's pivot.
   - Each drop: hung from a pivot at the arm's end, its axle level and across the arm (ref_01's round boss), so it
     swings in and out a little and the grip settles where the user's hand is: one geometry for short and long arms.
   - Each cam: keyed to the top of its shaft above the beam, winding its own cable.
   - The floating pulley on the stack's top plate (the two cables are one, looped under it).
   - The stack: 20 x 15 lb on its rods (the open Select tower).
3. Adjustments.
   - Start position (both exercises): an index plate keyed to each shaft under its housing with 5 holes; a spring pin in
     the arm's hub, its knob under the arm, goes up into one of them, so the arm turns the shaft from that angle.
     Holes at -20, -5, +10 deg (the fly: the arm that far forward of straight out to the side; minus is behind it, the
     stretch) and -55, -70 deg (the rear delt: the arms swung round behind the side, i.e. in front of a user facing +y,
     -90 being straight at the tower). Life Fitness: "five positions".
   - Two handles per arm (ref_01; Life Fitness: no re-adjusting between the two exercises): the long vertical grip, a
     J hung outward of the drop, for the fly and for a neutral-grip rear delt; a level grip in from the drop's inner
     face, for a pronated rear delt with the elbows more bent.
   - Seat height: a pop pin in the seat's sleeve, 7 holes 35 mm apart (0.40-0.61 m to its top), set so the hands meet
     the grips where the shoulders are level with them; the grips are long (0.21 m) so one setting serves a range.
   - The rest stop: a lug on each index plate rests on a rubber bumper hung from the housing, so with the stack down
     the arms sit at the chosen start and can't swing back past it.
4. Load path. Hand, grip, drop, pivot, arm, hub, pin, index plate, shaft, cam; the cable off the cam's outer side, level
   straight back to its head pulley on the tower's deck, down through the deck, under the floating pulley on the top
   plate. Winding: the fly turns the left arm (x+) clockwise from above (from the side toward the front); the rear delt
   (the user turned round, the arm on their right, pulled from the front out to the side) turns it clockwise too. So
   one cam per shaft winds the cable in for both exercises; from above, its outer tangent point moves forward (away
   from the tower) as it turns: it winds in. The right arm mirrors it.
5. Fit range. Seated at the drawn seat height (0.46), the shoulder joint sits at the shaft's x for every user to a few
   cm (+/-0.18 to +/-0.22). The vertical grip is 0.53 m out from the shaft; a 1.55-1.95 m user's arm is 0.58-0.73 m, so
   the elbows bend about 150 deg (short) to about 90 deg (tall) at the start, about 100-140 for the rear delt on the
   same grip: a bent-arm fly, the pec deck's natural range, the drop's swing easing it either way. The grips span
   0.90-1.09 m high: the shoulders of all three users at the drawn seat (0.95-1.07 m) meet them. The fit run prints
   each elbow.
6. Size. Life Fitness: 124 x 142 x 180 cm (L x W x H), live area 261 x 173. Ours: about 148 wide at the fly's drawn
   start (+10 deg, the grips at +/-0.72), about 1.88 m tall (the cams on the beam, level with the head pulleys), about
   1.17 m long (the tower's front at 0.59, clear of the rear-delt arms, which swing to y 0.51). The floor where the
   user's feet go is clear: the seat's cross foot sits under its front edge, the tower stands on its own base (ref_01).
Axes: metres, floor z = 0, the fly's user facing -y, x+ = the fly user's left; s = +1 / -1 the two sides.
"""
import math
import os

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
VIEWS = {"three_quarter": (-35, 14, 1.2), "front": (0, 6, 1.2), "side": (90, 3, 1.2), "back_three_quarter": (150, 18, 1.2),
         "top": (0, 80, 1.2)}
DETAILS = {
    "detail_top": ((0.90, -0.90, 2.40), (0.0, 0.05, 1.80), 50),           # the beam, the cams, the cables, the housings
    "detail_hub": ((0.75, -0.55, 1.35), (0.22, 0.0, 1.60), 45),           # the index plate, the pin, the stop, the hub
    "detail_drop": ((1.15, -0.55, 1.45), (0.69, -0.05, 1.35), 45),        # the drop's pivot, the grips
    "detail_head": ((0.70, 1.40, 2.20), (0.0, 0.70, 1.85), 45),           # the twin head pulleys, the cables down
}
SETTINGS = ("rear_delt",)            # rendered as rear_delt_<view> (studio.py), the arms at their rear-delt start
SETTING_VIEWS = ("three_quarter", "side", "top")
FIT_VIEWS = ("front", "three_quarter", "top")

# heights from the references (ref_01, and Roman's straight-on shot 2026-10-24: "needs to be taller"): the arms right
# up under the top at about 1.60, the drops and grips hanging about 0.6 m to about 0.90, the seat's top about 0.46;
# everything overhead stacks up compactly from the arms
Z_HUB = 1.60                         # the hubs' (and the arms') centres
Z_PLATE = Z_HUB + 0.04 + 0.002 + 0.005   # the index plates (10 mm thick, keyed to the shafts), 2 mm over the hubs
Z_HOUS = Z_PLATE + 0.035             # the housings' undersides (room between for the stop)
H_HOUS = 0.06                        # the housings' height
SQ = 0.076
Z_BEAM = Z_HOUS + H_HOUS + SQ / 2    # the beam over the housings
Z_RUN = Z_BEAM + SQ / 2 + 0.028      # the cables' level (1 cm running clearance under the cams)
TOWER_H = Z_RUN - 0.04 - 0.008 - 0.86 * 0.04 - 0.0028   # the tower: its head pulleys' groove tops level with the cams
TOWER = dict(style="open", W=0.56, D=0.30, H=TOWER_H, n=20, plate=(0.26, 0.125, 0.0254), rods=0.40,
             title="PEC FLY / REAR DELT", brand="HAMMER STRENGTH", round=-1, step=15, start=-5, head="twin", twin=0.07)
TC = (0.0, 0.74)                     # the tower: its front at 0.59, clear of the rear-delt arms (spec 6)
TY_F, TY_B = TC[1] - TOWER["D"] / 2, TC[1] + TOWER["D"] / 2
FOOT_H = 0.015
RAIL = (0.076, 0.05)
RAIL_Z = FOOT_H + RAIL[1] / 2
RAIL_TOP = FOOT_H + RAIL[1]
Y_FRONT = -0.156                     # the cross foot against the seat's sleeve, under its front edge (clear of the heels)
X_FB = 0.26
Y_COL = 0.32                         # the main column, behind the pad
# ---- the overhead (spec 1, 4)
X_AX, Y_AX = 0.20, 0.01              # each shaft: over its shoulder
CAM_R = 0.07
ARM_H = 0.06                         # the arm's section: tall x wide
R_ARM = 0.47                         # the shaft to the drop's pivot (spec 5)
Z_DROP = 1.08                        # the drop's foot (the drop about 0.45 m, the grip on below it)
Z_GRIP = (0.90, Z_DROP + 0.01)       # the vertical grip's bottom and top (ref_01: about 0.90-1.10)
J_OUT = 0.06                         # the vertical grip outward of the drop (ref_01)
REAR_IN = (0.035, 0.17)              # the rear-delt grip: in from the drop's axis (toward the shaft)
HOLES = (-20.0, -5.0, 10.0, -55.0, -70.0)   # the index holes (spec 3): the arm's angle forward of the side
FLY_AT, REAR_AT = 10.0, -70.0        # the fly's drawn start and the rear delt's (the arms in front of a user facing +y)
PHI = FLY_AT                         # this build's start (setting() changes it)
MODE = "fly"
# ---- the seat and the pad (spec 3, 5)
SEAT = (0.0, -0.08, 0.46)            # its top centre (ref_01: about 0.45): deep enough for the fly and the rear delt
SEAT_P = (0.42, 0.38, 0.08)
SEAT_RANGE = (0.40, 0.61)
PAD = ((0.12, 0.70), (0.12, 1.30), 0.26, 0.08)   # its face (y, z) bottom and top, width, thickness: above a rear-delt
                                                 # user's thighs, narrower than the shoulders (the arms pass it)


def setting(name):
    """The rear delt: the arms pinned at their rear-delt start, the fit users turned round."""
    global PHI, MODE
    if name == "rear_delt":
        PHI, MODE = REAR_AT, "rear_delt"


def arm_dir(s, phi):
    """The arm's level direction for side s at angle phi (deg forward of straight out to the side; forward is -y)."""
    a = math.radians(phi)
    return s * math.cos(a), -math.sin(a)


def foot(k, x, y, w=0.09, d=0.09):
    k.box("rubber", (x, y, FOOT_H / 2 + 0.001), (w, d, FOOT_H + 0.002), soft=0.003)


def build(k):
    Z, Y = (0, 0, 1), (0, 1, 0)
    tw = stack_tower.tower(k, TOWER, TC, 0.0)
    # ---- the base, kept out of the user's way (ref_01, Roman 2026-10-24: "the leg support things are different, so as
    # not to interfere with the person using the machine"): the spine from the tower's front forward to a short cross
    # foot just under the seat's front edge, nothing on the floor where the feet go; the tower stands on its own base
    # (Roman: the long diagonal braces behind it, v007, are not necessary)
    k.bar("frame", (-X_FB, Y_FRONT, RAIL_Z), (X_FB, Y_FRONT, RAIL_Z), SQ, RAIL[1], r=0.006)
    for s in (1, -1):
        k.box("plastic", (s * (X_FB + 0.004), Y_FRONT, RAIL_Z), (0.008, SQ + 0.004, RAIL[1] + 0.004), soft=0.002)
        foot(k, s * (X_FB - 0.04), Y_FRONT)
    k.bar("frame", (0, Y_FRONT + SQ / 2, RAIL_Z), (0, TY_F + 0.01, RAIL_Z), 0.10, RAIL[1], r=0.008,
          cut0=((0, Y_FRONT + SQ / 2, 0), Y), cut1=((0, TY_F + 0.01, 0), Y), weld=True)
    k.box("warn", (0.12, Y_FRONT - SQ / 2 - 0.001, RAIL_Z), (0.045, 0.002, 0.03), soft=0.0)
    # ---- the column off the spine, its tie to the tower, the arm forward to the beam, the beam
    zc = Z_BEAM + SQ / 2
    k.bar("frame", (0, Y_COL, RAIL_TOP), (0, Y_COL, zc), SQ, SQ, up=(0, 1, 0), cut0=((0, 0, RAIL_TOP), Z), weld=True)
    k.box("plastic", (0, Y_COL, zc + 0.004), (SQ + 0.004, SQ + 0.004, 0.008), soft=0.002)
    k.bar("frame", (0, Y_COL + SQ / 2, 1.30), (0, TY_F, 1.30), 0.06, 0.06, cut0=((0, Y_COL + SQ / 2, 0), Y),
          cut1=((0, TY_F, 0), Y), weld=True)
    k.bar("frame", (0, Y_COL - SQ / 2, Z_BEAM), (0, Y_AX + SQ / 2, Z_BEAM), SQ, SQ,
          cut0=((0, Y_COL - SQ / 2, 0), Y), cut1=((0, Y_AX + SQ / 2, 0), Y), weld=True)
    xe = X_AX + 0.10
    k.bar("frame", (-xe, Y_AX, Z_BEAM), (xe, Y_AX, Z_BEAM), SQ, SQ)
    for s in (1, -1):
        k.box("plastic", (s * (xe + 0.004), Y_AX, Z_BEAM), (0.008, SQ + 0.004, SQ + 0.004), soft=0.002)
    k.text("label", "HAMMER STRENGTH", (0, Y_AX - SQ / 2 - 0.001, Z_BEAM), 0.03, depth=0.0006)
    for s in (1, -1):
        side(k, s, tw)
    pad_and_seat(k)


def side(k, s, tw):
    """One side: housing, shaft, cam and its cable; index plate, stop; hub and its pin; arm, fork, drop, grips."""
    x, y = s * X_AX, Y_AX
    zb = Z_BEAM - SQ / 2
    zt = Z_BEAM + SQ / 2
    k.cyl("frame", (x, y, zb - H_HOUS / 2), 0.045, H_HOUS, seg=36, soft=0.003)                # the bearing housing
    k.tube("steel", (x, y, Z_HUB - 0.05), (x, y, Z_RUN + 0.03), 0.02, seg=20)                 # the shaft
    # the cam: a thrust washer on the beam, the bed, two flanges; the cable off its outer tangent (spec 4)
    k.cyl("cam", (x, y, zt + 0.009), 0.035, 0.018, seg=32, soft=0.002)
    k.cyl("cam", (x, y, Z_RUN), CAM_R, 0.024, seg=48, soft=0.002)
    for dz in (-0.015, 0.015):
        k.cyl("cam", (x, y, Z_RUN + dz), CAM_R + 0.01, 0.006, seg=48, soft=0.001)
    ox, oy, oz = tw["cables"][0 if s < 0 else 1]
    dx, dy = ox - x, oy - y
    dl = math.hypot(dx, dy)
    nx, ny = dy / dl, -dx / dl
    if nx * s < 0:
        nx, ny = -nx, -ny
    k.cable([(x + nx * (CAM_R + 0.0026), y + ny * (CAM_R + 0.0026), Z_RUN), (ox, oy, oz)])
    # the index plate keyed to the shaft under the housing, its five holes; the stop lug on it and the rubber bumper
    # hung from the housing on a bracket (spec 3)
    k.cyl("frame", (x, y, Z_PLATE), 0.12, 0.01, seg=56, soft=0.002)
    k.cyl("frame", (x, y, (Z_PLATE + 0.005 + Z_HOUS) / 2), 0.03, Z_HOUS - Z_PLATE - 0.005, seg=24, soft=0.001)   # its keyed collar
    for h in HOLES:
        ux, uy = arm_dir(s, h)
        k.cyl("hole", (x + ux * 0.095, y + uy * 0.095, Z_PLATE - 0.0052), 0.006, 0.001, seg=12)
    ua, ub = arm_dir(s, FLY_AT + 180.0)                  # the lug: opposite the fly's start hole (clear of the arm)
    rot = math.radians(PHI - FLY_AT) * s                 # the plate turns with the pinned arm's setting
    la = (ua * math.cos(rot) + ub * math.sin(rot), -ua * math.sin(rot) + ub * math.cos(rot))
    lug = (x + la[0] * 0.105, y + la[1] * 0.105)
    zl0 = Z_PLATE + 0.005                               # the plate's top
    k.box("frame", (lug[0], lug[1], zl0 + 0.01), (0.02, 0.02, 0.02), rz=math.atan2(la[1], la[0]), soft=0.002)
    # the bumper: against the lug's side the stack turns it toward (the fly's opposite: counter-clockwise for s = +1)
    tg = (-la[1] * s, la[0] * s)                          # the tangent the rest pull moves the lug along
    bp = (lug[0] + tg[0] * 0.021, lug[1] + tg[1] * 0.021)
    k.box("rubber", (bp[0], bp[1], zl0 + 0.002 + 0.009), (0.022, 0.022, 0.018), rz=math.atan2(la[1], la[0]), soft=0.002)
    rb = math.hypot(bp[0] - x, bp[1] - y)
    ub_ = ((bp[0] - x) / rb, (bp[1] - y) / rb)
    hb0 = (x + ub_[0] * 0.045, y + ub_[1] * 0.045)        # the bracket: out from the housing's side, down to the bumper
    k.bar("frame", (hb0[0], hb0[1], Z_HOUS + 0.02), (bp[0] + ub_[0] * 0.011, bp[1] + ub_[1] * 0.011, Z_HOUS + 0.02),
          0.022, 0.03, up=(0, 0, 1))
    zr = zl0 + 0.02                                     # the bumper's top: its hanger up to the bracket
    k.box("frame", (bp[0], bp[1], (Z_HOUS + 0.005 + zr) / 2), (0.022, 0.022, Z_HOUS + 0.005 - zr), rz=math.atan2(la[1], la[0]),
          soft=0.001)
    # the hub on the shaft (a bushing: free until pinned), the red axis disc under it, the arm, the pin
    ux, uy = arm_dir(s, PHI)
    k.cyl("lever", (x, y, Z_HUB), 0.055, 0.08, seg=40, soft=0.004)
    k.cyl("redplastic", (x, y, Z_HUB - 0.04 - 0.003), 0.03, 0.006, seg=32, soft=0.001)        # the axis marker
    tg_ = (-uy * s, ux * s)                              # level, across the arm, toward the fly's swing
    a0 = (x + ux * 0.053, y + uy * 0.053, Z_HUB)
    a1 = (x + ux * R_ARM, y + uy * R_ARM, Z_HUB)
    k.bar("lever", a0, (a1[0] + ux * 0.03, a1[1] + uy * 0.03, Z_HUB), 0.05, ARM_H, up=(0, 0, 1))
    k.box("plastic", (a1[0] + ux * 0.034, a1[1] + uy * 0.034, Z_HUB), (0.008, 0.054, ARM_H + 0.004),
          rz=math.atan2(uy, ux), soft=0.002)
    pp = (x + ux * 0.095, y + uy * 0.095)
    k.tube("steel", (pp[0], pp[1], Z_HUB - ARM_H / 2 - 0.012), (pp[0], pp[1], Z_PLATE - 0.002), 0.006, seg=12)
    k.cyl("redplastic", (pp[0], pp[1], Z_HUB - ARM_H / 2 - 0.024), 0.016, 0.024, seg=20, soft=0.004)   # its knob
    k.box("warn", (x + ux * 0.30, y + uy * 0.30, Z_HUB + ARM_H / 2 + 0.001), (0.04, 0.04, 0.002), rz=math.atan2(uy, ux),
          soft=0.0)
    # the fork under the arm's end, the axle across the arm, the drop's knuckle on it, the drop down to its foot
    za = Z_HUB - ARM_H / 2 - 0.045                       # the axle
    for d in (-1, 1):
        c = (a1[0] + tg_[0] * d * 0.021, a1[1] + tg_[1] * d * 0.021)
        k.box("lever", (c[0], c[1], (Z_HUB - ARM_H / 2 + za - 0.03) / 2), (0.06, 0.008, Z_HUB - ARM_H / 2 - za + 0.03),
              rz=math.atan2(uy, ux), soft=0.001)
    ax0 = (a1[0] - tg_[0] * 0.028, a1[1] - tg_[1] * 0.028, za)
    ax1 = (a1[0] + tg_[0] * 0.028, a1[1] + tg_[1] * 0.028, za)
    k.tube("steel", ax0, ax1, 0.011, seg=16)
    for p_, d in ((ax0, -1), (ax1, 1)):                  # the axle's nuts
        k.sweep("bolt", [p_, (p_[0] + tg_[0] * d * 0.005, p_[1] + tg_[1] * d * 0.005, za)], k.circle(0.016, 6))
    k.sweep("lever", [(a1[0] - tg_[0] * 0.016, a1[1] - tg_[1] * 0.016, za), (a1[0] + tg_[0] * 0.016, a1[1] + tg_[1] * 0.016, za)],
            k.circle(0.028, 28), soft=0.002)                                                 # the knuckle
    k.bar("lever", (a1[0], a1[1], za - 0.028), (a1[0], a1[1], Z_DROP), 0.05, 0.03, up=(tg_[0], tg_[1], 0))   # 30 mm: in the fork
    k.box("plastic", (a1[0], a1[1], Z_DROP - 0.004), (0.054, 0.034, 0.008), rz=math.atan2(uy, ux), soft=0.002)
    # the vertical grip: a J off the drop's outer face, down into the long rubber grip; the rear-delt grip level, in
    j0 = (a1[0] + ux * 0.02, a1[1] + uy * 0.02, Z_DROP + 0.035)
    j1 = (a1[0] + ux * J_OUT, a1[1] + uy * J_OUT, Z_DROP + 0.035)
    j2 = (j1[0], j1[1], Z_GRIP[0])
    k.sweep("lever", [j0, j1, j2], k.circle(0.016, 20), bend=0.03)
    k.tube("rubber", (j2[0], j2[1], Z_GRIP[0] + 0.005), (j2[0], j2[1], Z_GRIP[1] - 0.02), 0.021, soft=0.003)
    k.cyl("plastic", (j2[0], j2[1], Z_GRIP[0] + 0.001), 0.019, 0.008, seg=20, soft=0.002)
    r0 = (a1[0] - ux * REAR_IN[0], a1[1] - uy * REAR_IN[0], Z_DROP + 0.035)
    r1 = (a1[0] - ux * REAR_IN[1], a1[1] - uy * REAR_IN[1], Z_DROP + 0.035)
    k.tube("lever", (a1[0] - ux * 0.02, a1[1] - uy * 0.02, r0[2]), r1, 0.016, seg=20)
    k.tube("rubber", (a1[0] - ux * 0.07, a1[1] - uy * 0.07, r0[2]), r1, 0.021, soft=0.003)
    k.sweep("plastic", [r1, (r1[0] - ux * 0.008, r1[1] - uy * 0.008, r1[2])], k.circle(0.022, 20), soft=0.002)


def pad_and_seat(k):
    Z = (0, 0, 1)
    (y0, z0), (y1, z1), bw, bt = PAD
    c = (0.0, y0 + bt / 2, (z0 + z1) / 2)
    k.shaped_pad("pad", [(-bw / 2, -(z1 - z0) / 2), (bw / 2, -(z1 - z0) / 2), (bw / 2, (z1 - z0) / 2),
                         (-bw / 2, (z1 - z0) / 2)], c, (0, -1, 0), (1, 0, 0), bt, r=0.05, cushion=0.03)
    yp = y0 + bt + 0.02
    k.box("frame", (0, yp, (z0 + z1) / 2), (0.16, 0.04, (z1 - z0) * 0.8), soft=0.002)
    for zz in (z0 + 0.12, z1 - 0.15):
        k.bar("frame", (0, yp + 0.02, zz), (0, Y_COL - SQ / 2, zz), 0.08, 0.05, up=(0, 0, 1),
              cut1=((0, Y_COL - SQ / 2, 0), (0, 1, 0)), weld=True)
    # the seat on its post: the sleeve with 7 holes, the inner post, the pop pin's handle forward
    sx, sy, sz = SEAT
    bw_ = 0.076
    zt0 = 0.30
    wt = (bw_ - 0.058) / 2
    for qx, qy, w_, d_ in ((1, 0, wt, bw_), (-1, 0, wt, bw_), (0, 1, 0.058, wt), (0, -1, 0.058, wt)):
        k.box("frame", (qx * (bw_ - wt) / 2, sy + qy * (bw_ - wt) / 2, (RAIL_TOP + zt0) / 2), (w_, d_, zt0 - RAIL_TOP),
              soft=0.002)
    for i in range(7):
        k.cyl("hole", (0, sy - bw_ / 2 - 0.0005, 0.08 + i * 0.035), 0.007, 0.001, axis="y", seg=14)
    zt = sz - SEAT_P[2] - 0.012
    k.bar("frame", (0, sy, zt0 - 0.08), (0, sy, zt), 0.058, 0.058, up=(0, 1, 0))
    k.box("frame", (0, sy, zt + 0.006), (0.28, 0.26, 0.012), soft=0.002)
    k.pad("pad", (0, sy, sz - SEAT_P[2] / 2), SEAT_P, r=0.035)
    pin_z = zt0 - 0.03
    k.tube("steel", (0, sy - 0.02, pin_z), (0, sy - bw_ / 2 - 0.03, pin_z), 0.007)
    k.sweep("frame", [(0, sy - bw_ / 2 - 0.03, pin_z), (0, sy - bw_ / 2 - 0.09, pin_z - 0.01),
                      (-0.12, sy - bw_ / 2 - 0.12, pin_z - 0.03)], k.circle(0.009, 14), bend=0.03)
    k.cyl("plastic", (0, sy - bw_ / 2 - 0.03, pin_z), 0.016, 0.02, axis="y", seg=20, soft=0.004)


# ---- the fit check (spec 5): three users, each arm a two-link reach, the elbow's angle printed
def fit():
    out = {}
    r = math.radians
    rear = MODE == "rear_delt"
    face = (0, 1) if rear else (0, -1)
    for label, H in (("short", 1.55), ("middle", 1.78), ("tall", 1.95)):
        sc = H / 1.78
        # the hips: the fly's back on the pad, the rear delt's chest on it; the shoulders then over the shafts
        hip = (0.0, PAD[0][0] - (0.13 if rear else 0.11) * sc, SEAT[2] + 0.045 * sc)
        fy = 1 if rear else -1                           # forward, for this user
        ay, az = hip[1] + fy * (0.30 if rear else 0.40) * sc, 0.039 * H   # the ankle: the feet flat (the rear delt's
                                                         # tucked back: the tower is ahead of them)
        best = min(((math.hypot(ay + fy * (math.sin(r(sh)) * 0.246 * H + math.sin(r(th)) * 0.245 * H) - hip[1],
                                az + math.cos(r(sh)) * 0.246 * H + math.cos(r(th)) * 0.245 * H - hip[2]), sh, th)
                    for sh in range(-30, 41) for th in range(-120, 0)))
        _, sh, th = best
        ball = (0.0, ay + fy * 0.48 * 0.152 * H, 0.0)
        a1, l1, a2, l2, elbow = reach(H, hip, face)
        print(f"fit {MODE} {label}: elbow {elbow:.0f} deg", flush=True)
        out[label] = dict(H=H, ball=ball, face=face, sole=0, shank=sh, thigh=th, trunk=0.0, neck=0,
                          arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def reach(H, hip, face):
    """The figure's left arm to its vertical grip (the fly, and the neutral-grip rear delt), a two-link reach, the elbow bent
    down off the line; returns body.figure's angles and the elbow's inside angle."""
    f = (face[0], face[1], 0.0)
    left = (-f[1], f[0], 0.0)                            # up x face
    sh = (left[0] * 0.13 * H * 0.85, hip[1] + left[1] * 0.13 * H * 0.85, hip[2] + 0.288 * H)
    s = 1 if left[0] > 0 else -1                         # the machine side of the figure's left arm
    ux, uy = arm_dir(s, PHI)
    ax, ay = s * X_AX + ux * R_ARM, Y_AX + uy * R_ARM
    gz = max(Z_GRIP[0] + 0.05, min(Z_GRIP[1] - 0.05, sh[2] - 0.03))   # the hand level with the shoulder, a bit under
    g = (ax + ux * J_OUT, ay + uy * J_OUT, gz)          # the vertical grip, for both exercises (spec 3)
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w = (vh[0] * vh[2], vh[1] * vh[2], vh[2] * vh[2] - 1.0)   # down, square to the shoulder-grip line
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

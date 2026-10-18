"""Precor Resolute Series Leg Extension (RSL0605).

Built from orthographic reference views we generated from the real photos (refs/gen/: side, front, rear, top; the side
view is the main source for lengths + heights, the top view for widths), held to Precor's spec (155 x 127 x 148 cm, the
RSL0605 sell sheet) and checked against two real photos through the camera match (match.json, tools/camsolve.py).
Materials: Black Pearl powder coat, Tungsten shroud, All Spice vinyl (65 mm), orange adjusters, silver caps.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left. The stack tower stands on the user's right with
its flat face (slot, placards, logo) towards the seat; the knee mechanism sits in front of it.
"""
import json
import math
import os
from pathlib import Path

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.3, metal=0.35, coat=0.5, bump=(900, 0.05)),   # Black Pearl
    "shroud": dict(color=(0.035, 0.036, 0.04), rough=0.42, metal=0.2, coat=0.3),                     # Tungsten
    "pad": dict(color=(0.25, 0.075, 0.028), rough=0.48, sheen=0.3, bump=(1600, 0.12)),                  # All Spice vinyl
    "seam": dict(color=(0.17, 0.05, 0.02), rough=0.55),
    "accent": dict(color=(0.95, 0.42, 0.02), rough=0.35),                                            # orange adjusters
    "label": dict(color=(0.92, 0.92, 0.92), rough=0.4),
    "panel": dict(color=(0.03, 0.035, 0.045), rough=0.25, coat=0.6),
    "alu": dict(color=(0.8, 0.8, 0.81), rough=0.22, metal=1.0, aniso=0.3),                            # silver caps
}
ORTHO = {"ortho_side": 90, "ortho_front": 0, "ortho_rear": 180, "ortho_top": "top"}
VIEWS = {"three_quarter": (60, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (200, 16, 1.0)}

# ---- the stack tower (D plan: flat face along x = TX1 its whole length, a half-elliptical back)
TX1, TD = -0.50, 0.25            # face plane, depth of the back behind it
TY0, TY1 = -0.47, 0.07           # front + rear ends of the face
TZ0, H = 0.10, 1.48              # bottom of the shroud (on its base), top
TYAW = 0.0
YS, SLOT, SLOT_TOP = -0.20, 0.05, 1.31     # the slot through the shroud (centre y, width, top z)
PLATE_TOP, PLATE_BOT = 1.41, 1.21          # the face plate: header band + placards
STACK_Z = (0.27, 0.64)                     # the plates seen in the slot
# ---- the knee mechanism
PIV = (-0.27, -0.49, 0.74)       # the lever's pivot hub (axle along x)
DIAL = (-0.33, -0.45, 0.815)     # the numbered start-position dial on the cam housing
CAM = (-0.40, -0.43, 0.78)       # centre of the cam housing
LE = (-0.27, -0.733, 0.514)      # the lever's lower end block (the drop arm to the roller hangs from it)
UE = (-0.27, -0.235, 0.996)      # its upper end (foam sleeve)
RA = (-0.653, 0.325)             # roller axle (y, z)
ROLLER, ROLLER_R = (-0.215, 0.294), 0.074
GRIP_A, GRIP_B = (-0.33, -0.567, 0.977), (-0.30, -0.636, 0.833)   # tops of the two silver-capped hand grips
POST = (-0.30, -0.58)            # the round post foot under the mechanism
SPINE0 = (-0.30, -0.567, 0.571)  # the spine's front end (big silver cap), bolted to the mechanism
# ---- the frame
XS = 0.30                        # the user's-left side frame
FOOT_F, FOOT_R = -0.056, 0.715   # its feet (y)
FLEG_TOP = (0.27, 0.057, 0.50)   # the front leg meets the seat frame
ARCH_TOP = (0.22, 0.62, 0.44)    # the user's-left rear leg's arch top (under the seat's edge)
XR = -0.40                       # the other rear leg, beside the tower (top drawing)
# ---- seat + back pad
SEAT = (0.02, -0.12, 0.62, 0.44, 0.45, 0.075)    # x, y (centre), top z at the front, width at the front, depth, thickness
# (the photos: the seat's front edge ~11 cm behind the knee hub, so the knee lines up with the pivot; the side drawing had
# it 29 cm back. Set by eye on the overlays: the soft pad corners as anchors pulled the solve apart)
SEAT_BACKW, SEAT_TILT = 0.36, 5.0               # width at the back; the front raised (deg)
BACK = (0.0, 0.243, 0.68, 0.684, 0.33, 0.065)   # x, bottom front edge y + z, length, width at the bottom, thickness
BACK_LEAN, BACK_TOPW = 22.0, 0.30               # lean from vertical (deg), width at the top
ORANGE = (0.19, 0.449, 0.80)     # the orange back-pad release paddle, on its rod from the seat carriage
SPEC = (1.55, 1.27, 1.48)        # Precor's overall L (y) x W (x) x H

# solved with the cameras of the real photos (equipment/tools/camsolve.py), each held to its value above by sigma (m / deg)
# solved with the cameras of the real photos (equipment/tools/camsolve.py), each held to its value above by sigma (m / deg)
FIT = {"TX1": 0.05, "TD": 0.05, "TY0": 0.05, "TY1": 0.05, "PIV": 0.04, "DIAL": 0.05, "CAM": 0.06, "LE": 0.05, "UE": 0.05,
       "RA": 0.04, "ROLLER": 0.04, "GRIP_A": 0.05, "GRIP_B": 0.05, "POST": 0.05, "XS": 0.04, "FOOT_F": 0.05, "FOOT_R": 0.05,
       "FLEG_TOP": 0.05, "ARCH_TOP": 0.05,  "BACK": 0.04,
       "BACK_LEAN": 4.0, "BACK_TOPW": 0.04, "ORANGE": 0.05, "PLATE_TOP": 0.03, "PLATE_BOT": 0.03, "SLOT_TOP": 0.04, "YS": 0.04}
_ff = Path(__file__).with_name("fit.json")
if _ff.exists() and not os.environ.get("EQ_NOFIT"):
    globals().update({k_: (tuple(v_) if isinstance(v_, list) else v_) for k_, v_ in json.loads(_ff.read_text()).items()})


def _bp():
    a = math.radians(90 - BACK_LEAN)
    return a, (0.0, math.cos(a), math.sin(a)), (0.0, -math.sin(a), math.cos(a))   # angle, along the pad (up), its face normal


def _seat_top(front, sx):
    x, y, zt, wf, d, th = SEAT
    w = wf if front else SEAT_BACKW
    yy = y - d / 2 if front else y + d / 2
    z = zt if front else zt - d * math.sin(math.radians(SEAT_TILT))
    return (x + sx * w / 2, yy, z)


def anchors():
    a, up, nrm = _bp()
    bx, by0, bz0, bh, bw, bt = BACK
    top = (by0 + up[1] * bh, bz0 + up[2] * bh)
    return {
        "tower_top_rear_face": (TX1, TY1, H),
        "plate_top_rear": (TX1, TY1 - 0.04, PLATE_TOP),
        "plate_top_front": (TX1, TY0 + 0.04, PLATE_TOP),
        "plate_bot_front": (TX1, TY0 + 0.04, PLATE_BOT),
        "tower_face_rear_bottom": (TX1, TY1, TZ0),
        "logo": (TX1, YS, (H + PLATE_TOP) / 2),
        "slot_top": (TX1, YS, SLOT_TOP),
        "dial": DIAL,
        "drum": CAM,
        "lever_hub": (PIV[0] + 0.035, PIV[1], PIV[2]),
        "lever_top": (PIV[0] + 0.035, UE[1], UE[2]),
        "lever_low": (PIV[0] + 0.035, LE[1], LE[2]),
        "grip_a": (GRIP_A[0], GRIP_A[1], GRIP_A[2] + 0.017),
        "grip_b": (GRIP_B[0], GRIP_B[1], GRIP_B[2] + 0.017),
        "roller_cap": (ROLLER[1] + 0.012, RA[0], RA[1]),
        "roller_far_end": (PIV[0] + 0.08, RA[0], RA[1]),
        "post_foot": (POST[0], POST[1], 0.0),
        "foot_front": (XS, FOOT_F, 0.03),
        "foot_rear": (ARCH_TOP[0], FOOT_R, 0.03),
        "front_leg_top": FLEG_TOP,
        "arch_top": ARCH_TOP,
        "seat_front_left": _seat_top(True, 1),
        "seat_rear_left": _seat_top(False, 1),
        "backpad_bot_left": (bx + bw / 2, by0, bz0),
        "backpad_bot_right": (bx - bw / 2, by0, bz0),
        "backpad_top_left": (bx + BACK_TOPW / 2, top[0], top[1]),
        "backpad_top_right": (bx - BACK_TOPW / 2, top[0], top[1]),
        "orange": ORANGE,
    }


ANCHORS = anchors()


def extents():
    xs = [TX1 - TD, ROLLER[1] + 0.01, XS + 0.06, SEAT[0] + SEAT[3] / 2, XR - 0.06]
    a, up, nrm = _bp()
    ys = [RA[0] - ROLLER_R, POST[1] - 0.05, TY0, LE[1] - 0.04, FOOT_F - 0.12, FOOT_R + 0.10, TY1, BACK[1] + up[1] * BACK[3] + 0.07]
    return (max(ys) - min(ys), max(xs) - min(xs), H)


def lerp(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))


def _shell(k, y0, y1, z0, z1, mat, grow=0.0, soft=0.005):
    """The part of the tower's D plan between y0 and y1 (the slot splits the shroud in two), swept from z0 to z1:
    the flat face along x = TX1, the back a half-ellipse (depth TD, the face's length), grown by `grow` all round."""
    yc, lh, td = (TY0 + TY1) / 2, (TY1 - TY0) / 2 + grow, TD + grow
    x1 = TX1 + grow
    t0 = math.acos(max(-1.0, min(1.0, (yc - y0) / lh)))
    t1 = math.acos(max(-1.0, min(1.0, (yc - y1) / lh)))
    n = max(4, int(40 * (t1 - t0) / math.pi))
    sp = lambda c_: math.copysign(abs(c_) ** (2 / 2.5), c_)   # a superellipse: flat back, rounded corners (top drawing + lid)
    back = [(x1 - td * sp(math.sin(t0 + (t1 - t0) * i / n)), yc - lh * sp(math.cos(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]
    pts = [(x1, back[-1][1]), (x1, back[0][1])] + back
    k.sweep(mat, [(0, 0, z0), (0, 0, z1)], [(-x, y) for x, y in pts], soft=soft)  # a vertical sweep maps (u, v) to (-u, v)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    tower(k)
    mechanism(k)
    frame(k)
    seat_and_back(k)


def tower(k):
    g = SLOT / 2
    LID = 0.085
    _shell(k, TY0, YS - g, TZ0, H - LID, "shroud")
    _shell(k, YS + g, TY1, TZ0, H - LID, "shroud")
    # the lid: a D-shaped cap a little proud of the shroud all round, its top edge well rounded, a shallow tray in its top
    _shell(k, TY0, TY1, H - LID, H, "frame", grow=0.008, soft=0.016)
    _shell(k, TY0, TY1, H - 0.006, H + 0.0008, "rubber", grow=-0.022, soft=0.004)
    _shell(k, TY0, TY1, 0.0, TZ0, "frame", grow=-0.02)                          # the base under the shroud
    for fy in (TY0 + 0.08, TY1 - 0.08):
        k.cyl("rubber", (TX1 - TD * 0.5, fy, 0.004), 0.045, 0.012)
    # the face (from the top): the PRECOR logo under the lid, then a raised black bezel: the header bar across its top, the
    # two placards either side of the slot below it (the official photo: logo 1.37 m, header 1.29, placards 1.06-1.23)
    fx, f0, f1 = TX1 + 0.006, TY0 + 0.035, TY1 - 0.035
    k.text("label", "PRECOR", (TX1 + 0.002, (TY0 + TY1) / 2, H - 0.118), 0.04, rz=math.pi / 2)
    hz0, hz1, pz0 = H - 0.235, H - 0.16, H - 0.44
    k.box("frame", (fx, (f0 + f1) / 2, (hz0 + hz1) / 2), (0.012, f1 - f0, hz1 - hz0), soft=0.005)
    for a_, b_ in ((f0, YS - g - 0.008), (YS + g + 0.008, f1)):
        k.box("frame", (fx, (a_ + b_) / 2, (pz0 + hz0) / 2 + 0.003), (0.012, b_ - a_, hz0 - pz0 + 0.006), soft=0.005)
    k.box("panel", (fx + 0.0065, (f0 + f1) / 2, hz1 - 0.035), (0.002, f1 - f0 - 0.05, 0.032), soft=0.0)
    k.text("label", "LEG EXTENSION", (fx + 0.008, (f0 + f1) / 2, hz1 - 0.035), 0.0125, rz=math.pi / 2)
    art = Path(__file__).with_name("art")
    pz, ph = pz0 + 0.02, hz0 - pz0 - 0.035
    for (y0_, y1_), img in zip(((f0 + 0.022, YS - g - 0.026), (YS + g + 0.026, f1 - 0.022)), ("placard_left.png", "placard_right.png")):
        k.decal(art / img, (fx + 0.0065, (y0_ + y1_) / 2, pz + ph / 2), y1_ - y0_, ph, "+x")
    sx = TX1 - TD / 2
    for s in (-1, 1):  # the slot's dark side walls
        k.box("plastic", (sx, YS + s * (g + 0.002), (TZ0 + SLOT_TOP) / 2), (TD * 0.85, 0.004, SLOT_TOP - TZ0), soft=0.0)
    k.tube("chrome", (sx, YS, STACK_Z[1]), (sx, YS, SLOT_TOP), 0.009)          # the lifting rod above the stack
    n = 20
    t = (STACK_Z[1] - STACK_Z[0]) / n
    for i in range(n):  # the plates, numbered on their fronts
        z = STACK_Z[0] + (i + 0.5) * t
        k.box("plate", (sx, YS, z), (0.10, 0.26, t - 0.0012), soft=0.002)
        k.box("label", (TX1 - 0.004, YS + g + 0.015, z), (0.002, 0.018, t * 0.45), soft=0.0)
    for s in (-1, 1):
        k.tube("chrome", (sx, YS + s * 0.10, TZ0), (sx, YS + s * 0.10, H - 0.06), 0.012)
    # the orange selector pin + keeper on the face, at the top of the stack
    k.cyl("accent", (TX1 + 0.018, YS - g - 0.02, STACK_Z[1] + 0.02), 0.011, 0.04, axis="x")
    k.box("accent", (TX1 + 0.012, YS - g - 0.025, STACK_Z[1] + 0.07), (0.018, 0.045, 0.022), soft=0.006)


def mechanism(k):
    # the knee unit stands on the post in front of the tower (photos), not on the tower: a side plate carries the round
    # cam housing (axis along y, its open front a dark recess with the cam's silver hub), the start dial and the pivot;
    # a silver drum runs back from the housing to the dial
    cx, cy, cz = CAM
    px_ = PIV[0] - 0.085
    k.shaped_pad("frame", [(-0.13, -0.15), (0.06, -0.13), (0.15, -0.07), (0.14, 0.05), (0.06, 0.11), (-0.10, 0.08)],
                 (px_, (cy + PIV[1]) / 2, (cz + DIAL[2]) / 2), (1, 0, 0), (0, 1, 0), 0.03, r=0.035, seam=False, board=False)
    # a deep rounded-square shell, its open front a dark cavity: the cam (a lobe, not a wheel) and the cable inside
    k.sweep("frame", [(cx, cy - 0.06, cz), (cx, cy + 0.07, cz)], k.rect(0.25, 0.27, 0.07, 8), up=(0, 0, 1), soft=0.012)
    k.sweep("plastic", [(cx, cy - 0.0615, cz), (cx, cy - 0.058, cz)], k.rect(0.215, 0.235, 0.052, 8), up=(0, 0, 1), soft=0.0)   # the cavity
    k.sweep("frame", [(cx, cy - 0.075, cz), (cx, cy - 0.06, cz)], [(0.06 * math.cos(t) + 0.025 * math.cos(t) ** 3, 0.075 * math.sin(t))
                                                                for t in [2 * math.pi * i / 32 for i in range(32)]], up=(0, 0, 1), soft=0.004)
    k.cyl("chrome", (cx, cy - 0.078, cz), 0.012, 0.01, axis="y")
    k.tube("frame", (cx + 0.03, cy + 0.06, cz + 0.02), (PIV[0] - 0.06, PIV[1] - 0.02, PIV[2] + 0.01), 0.036, seg=32)
    # the start-position plate: a fan round the pivot (towards the dial anchor), a ring of pin holes, numbered
    py_, pz_ = PIV[1], PIV[2]
    f0_ = math.atan2(DIAL[2] - pz_, DIAL[1] - py_)
    arc = [f0_ - 0.9 + 1.8 * i / 12 for i in range(13)]
    k.shaped_pad("frame", [(0.0, 0.0)] + [(0.145 * math.cos(t), 0.145 * math.sin(t)) for t in arc], (PIV[0] - 0.012, py_, pz_),
                 (1, 0, 0), (0, 1, 0), 0.012, r=0.012, seam=False, board=False)
    for i, t in enumerate(arc[1:-1:2]):
        k.cyl("plastic", (PIV[0] - 0.004, py_ + 0.122 * math.cos(t), pz_ + 0.122 * math.sin(t)), 0.0085, 0.004, axis="x", seg=16)
        k.text("label", str(i + 1), (PIV[0] - 0.004, py_ + 0.097 * math.cos(t), pz_ + 0.097 * math.sin(t)), 0.011, rz=math.pi / 2)
    k.tube("chrome", (px_, PIV[1], PIV[2]), (PIV[0] + 0.03, PIV[1], PIV[2]), 0.02)       # the axle from the side plate
    # the lever: a straight round tube through its hub (all in one plane, x = LX), the foam sleeve at the top, the block +
    # silver cap below
    LX = PIV[0] + 0.035
    le, ue = (LX, LE[1], LE[2]), (LX, UE[1], UE[2])
    k.tube("frame", le, ue, 0.031, seg=32)
    k.tube("rubber", lerp(ue, le, 0.02), lerp(ue, le, 0.30), 0.037, seg=32)
    k.cyl("frame", ue, 0.036, 0.012, axis="x")
    k.cyl("frame", (LX, PIV[1], PIV[2]), 0.045, 0.07, axis="x", seg=32, soft=0.004)
    k.cyl("alu", (LX + 0.037, PIV[1], PIV[2]), 0.03, 0.008, axis="x")
    k.cyl("frame", le, 0.042, 0.07, axis="x", seg=32, soft=0.006)                          # the lever's rounded lower end
    k.cyl("alu", (LX + 0.038, le[1], le[2]), 0.024, 0.008, axis="x")
    # the drop arm from the block down to the roller axle, the roller across under the shins
    ry, rz = RA
    k.sweep("frame", [(LX - 0.005, le[1], le[2]), (LX - 0.005, ry, rz)], k.stadium(0.075, 0.035), up=(1, 0, 0))   # the flat roller arm
    k.box("frame", (LX - 0.005, ry, rz), (0.06, 0.08, 0.09), soft=0.008)                  # the roller's adjust block
    k.tube("chrome", (LX, ry, rz), (ROLLER[1], ry, rz), 0.016)
    k.cyl("frame", (LX + 0.03, ry, rz), 0.03, 0.03, axis="x", soft=0.004)                # the roller's collar on the arm
    k.sweep("pad", [(LX + 0.05, ry, rz), (ROLLER[1] - 0.012, ry, rz)], k.circle(ROLLER_R, 48), soft=0.014)
    k.sweep("plastic", [(ROLLER[1] - 0.013, ry, rz), (ROLLER[1] + 0.006, ry, rz)], k.circle(ROLLER_R - 0.003, 48), soft=0.008)
    # the two hand grips: black stubs with silver caps, on a bent tube down into the spine's front
    base = (PIV[0] - 0.03, PIV[1] - 0.03, PIV[2] - 0.11)                                    # into the hub plate under the pivot
    for top in (GRIP_A, GRIP_B):
        bot = (top[0], top[1] + 0.035, top[2] - 0.11)
        k.tube("rubber", bot, top, 0.018)
        k.cyl("alu", top, 0.019, 0.016)
        k.sweep("frame", [bot, (top[0], bot[1] + 0.01, bot[2] - 0.08), base], k.circle(0.016), bend=0.05)
    # the post foot under the mechanism, into the housing
    k.tube("frame", (POST[0], POST[1], 0.05), (POST[0], POST[1], CAM[2] - 0.10), 0.036, seg=32)
    k.cyl("frame", (POST[0], POST[1], 0.05), 0.04, 0.012)                                  # its end plate
    k.cyl("chrome", (POST[0], POST[1], 0.035), 0.011, 0.025, seg=12)                       # the levelling foot's thread
    k.cyl("rubber", (POST[0], POST[1], 0.012), 0.04, 0.024, seg=40)


def frame(k):
    # the spine: a curved oval beam from the mechanism (big silver cap) under the seat to the carriage
    x, y, zt, wf, d, th = SEAT
    k.sweep("frame", [SPINE0, (-0.08, -0.42, 0.53), (x, -0.18, 0.465), (x, 0.08, 0.45), (x, y + d / 2 + 0.08, 0.45)], k.stadium(0.12, 0.075), bend=0.15, up=(0, 0, 1))
    k.cyl("frame", (SPINE0[0] + 0.04, SPINE0[1], SPINE0[2]), 0.04, 0.05, axis="x", soft=0.004)      # the cross shaft's boss
    k.cyl("alu", (SPINE0[0] + 0.075, SPINE0[1], SPINE0[2]), 0.04, 0.024, axis="x", seg=48)         # its big silver knob
    # the user's-left side: the front leg (slanting back as it rises), a rail low along it, the rear arch, feet
    L = k.rect(0.075, 0.05, 0.01)
    k.bar("frame", (XS, FOOT_F, 0.03), FLEG_TOP, 0.05, 0.10, up=(0, 1, 0))                 # broad front to back
    k.bar("frame", (x + 0.05, FLEG_TOP[1] - 0.02, FLEG_TOP[2] - 0.02), FLEG_TOP, 0.06, 0.05)          # into the spine
    xa = ARCH_TOP[0]
    fl = lerp((XS, FOOT_F, 0.03), FLEG_TOP, 0.26)
    k.bar("frame", fl, (xa, FOOT_R - 0.04, 0.09), 0.06, 0.05)                                  # the floor rail, leg to leg
    # the rear (top drawing): two legs, one under the seat's left edge, one beside the tower, each running back from a cross
    # tube under the seat carriage and bending down to its foot
    yc_, zc_ = y + d / 2 + 0.04, 0.40
    for xr in (xa, XR):
        k.sweep("frame", [(xr, yc_, zc_), (xr, ARCH_TOP[1], zc_ - 0.01), (xr, FOOT_R + 0.01, 0.04)], k.circle(0.036, 28), bend=0.14)
    k.tube("frame", (XR - 0.036, yc_, zc_), (xa + 0.036, yc_, zc_), 0.036, seg=28)
    k.bar("frame", (XR, FOOT_R - 0.06, 0.05), (POST[0] - 0.01, FOOT_F + 0.03, 0.14), 0.06, 0.05)   # the floor rail along the tower
    for fx_, fy_ in ((xa, FOOT_R + 0.01), (XR, FOOT_R + 0.01), (XS, FOOT_F)):   # the feet: thick rounded pads
        k.sweep("rubber", [(fx_, fy_, 0.0), (fx_, fy_, 0.042)], k.stadium(0.22, 0.11), soft=0.012)
    # the base: the post foot's rail curving back under the tower to the front leg, the tower's own base rail
    k.sweep("frame", [(POST[0], POST[1] + 0.02, 0.36), (POST[0], POST[1] + 0.02, 0.15), (POST[0], TY0 + 0.06, 0.15), (POST[0], FOOT_F, 0.15),
                      (XS, FOOT_F + 0.04, 0.15)], k.circle(0.032, 28), bend=0.10)                     # the J


def seat_and_back(k):
    x, y, zt, wf, d, th = SEAT
    tl = math.radians(SEAT_TILT)
    c = (x, y, zt - d / 2 * math.sin(tl) - th / 2)
    k.shaped_pad("pad", [(-wf / 2, -d / 2), (wf / 2, -d / 2), (SEAT_BACKW / 2, d / 2), (-SEAT_BACKW / 2, d / 2)],
                 c, (0, math.sin(tl), math.cos(tl)), (1, 0, 0), th, r=0.045)
    k.box("frame", (x, y + 0.02, c[2] - th / 2 - 0.02), (0.22, d * 0.7, 0.03), rx=-tl, soft=0.004)   # the seat pan on the spine
    # the adjust handles under the seat's rear corners: a black grip with a silver end cap pointing out, an elbow down, the
    # rod forward under the seat with a white collar
    zb = c[2] - th / 2 - 0.03
    for sx in (-1, 1):
        xo = x + sx * (SEAT_BACKW / 2 + 0.035)
        xi = x + sx * (SEAT_BACKW / 2 - 0.035)
        hy = y + d / 2 - 0.03
        k.tube("rubber", (xo, hy, zb), (xi, hy, zb), 0.019)
        k.cyl("alu", (xo + sx * 0.008, hy, zb), 0.021, 0.014, axis="x")
        k.sweep("frame", [(xi, hy, zb), (xi - sx * 0.03, hy, zb), (xi - sx * 0.03, hy, zb - 0.09), (xi - sx * 0.06, hy - 0.22, zb - 0.10)],
                k.circle(0.012), bend=0.03)
        k.cyl("label", (xi - sx * 0.03, hy, zb - 0.07), 0.015, 0.012)
    # the carriage behind the seat (the back pad's post goes into it) and its bolted bracket plate, all below the seat
    k.box("frame", (x, y + d / 2 + 0.05, 0.46), (0.12, 0.12, 0.10), soft=0.006)
    k.shaped_pad("frame", [(-0.10, -0.08), (0.11, -0.08), (0.11, 0.05), (0.06, 0.09), (-0.10, 0.09)], (x + 0.105, y + d / 2 + 0.01, 0.39),
                 (1, 0, 0), (0, 1, 0), 0.008, r=0.012, seam=False, board=False)
    for by, bz in ((-0.05, 0.45), (0.05, 0.44), (0.0, 0.36), (0.04, 0.33), (-0.07, 0.34)):
        k.cyl("alu", (x + 0.111, y + d / 2 + 0.01 + by, bz), 0.0065, 0.006, axis="x", seg=12)
    rod0 = (ORANGE[0] - 0.02, ORANGE[1] - 0.09, 0.52)
    k.tube("frame", rod0, ORANGE, 0.007)
    k.box("accent", ORANGE, (0.025, 0.035, 0.09), rx=math.atan2(ORANGE[1] - rod0[1], ORANGE[2] - rod0[2]), soft=0.008)
    # the back pad on its round post and a bracket plate behind its foot
    a, up, nrm = _bp()
    bx, by0, bz0, bh, bw, bt = BACK
    foot = (bx, by0 - nrm[1] * (bt + 0.03), bz0 - nrm[2] * (bt + 0.03))
    k.tube("frame", (bx, foot[1] + 0.04, 0.47), (bx, foot[1] + 0.02, foot[2] + 0.06), 0.035, seg=32)
    k.box("frame", (bx, foot[1] + up[1] * 0.12, foot[2] + up[2] * 0.12), (0.12, 0.03, 0.26), rx=a - math.pi / 2, soft=0.004)
    pc = (bx, by0 + up[1] * bh / 2 - nrm[1] * bt / 2, bz0 + up[2] * bh / 2 - nrm[2] * bt / 2)
    k.shaped_pad("pad", [(-bw / 2, -bh / 2), (bw / 2, -bh / 2), (BACK_TOPW / 2, bh / 2), (-BACK_TOPW / 2, bh / 2)], pc, nrm, (1, 0, 0), bt, r=0.04)

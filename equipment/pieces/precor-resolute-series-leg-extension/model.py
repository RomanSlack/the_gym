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
    "pad": dict(color=(0.36, 0.13, 0.05), rough=0.48, sheen=0.3, bump=(1600, 0.12)),                  # All Spice vinyl
    "seam": dict(color=(0.27, 0.095, 0.035), rough=0.55),
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
ROLLER, ROLLER_R = (-0.215, 0.294), 0.065
GRIP_A, GRIP_B = (-0.33, -0.567, 0.977), (-0.30, -0.636, 0.833)   # tops of the two silver-capped hand grips
POST = (-0.30, -0.58)            # the round post foot under the mechanism
SPINE0 = (-0.30, -0.567, 0.571)  # the spine's front end (big silver cap), bolted to the mechanism
# ---- the frame
XS = 0.30                        # the user's-left side frame
FOOT_F, FOOT_R = -0.056, 0.715   # its feet (y)
FLEG_TOP = (0.27, 0.057, 0.50)   # the front leg meets the seat frame
ARCH_TOP = (0.29, 0.62, 0.44)    # the rear leg's arch top
XR = -0.39                       # the rear frame's other side (x)
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
        "lever_top": UE,
        "lever_low": LE,
        "grip_a": (GRIP_A[0], GRIP_A[1], GRIP_A[2] + 0.017),
        "grip_b": (GRIP_B[0], GRIP_B[1], GRIP_B[2] + 0.017),
        "roller_cap": (ROLLER[1] + 0.012, RA[0], RA[1]),
        "roller_far_end": (ROLLER[0], RA[0], RA[1]),
        "post_foot": (POST[0], POST[1], 0.0),
        "foot_front": (XS, FOOT_F, 0.03),
        "foot_rear": (XS, FOOT_R, 0.03),
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


def _shell(k, y0, y1, z0, z1, mat, grow=0.0):
    """The part of the tower's D plan between y0 and y1 (the slot splits the shroud in two), swept from z0 to z1:
    the flat face along x = TX1, the back a half-ellipse (depth TD, the face's length), grown by `grow` all round."""
    yc, lh, td = (TY0 + TY1) / 2, (TY1 - TY0) / 2 + grow, TD + grow
    x1 = TX1 + grow
    t0 = math.acos(max(-1.0, min(1.0, (yc - y0) / lh)))
    t1 = math.acos(max(-1.0, min(1.0, (yc - y1) / lh)))
    n = max(4, int(40 * (t1 - t0) / math.pi))
    back = [(x1 - td * math.sin(t0 + (t1 - t0) * i / n), yc - lh * math.cos(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]
    pts = [(x1, back[-1][1]), (x1, back[0][1])] + back
    k.sweep(mat, [(0, 0, z0), (0, 0, z1)], [(-x, y) for x, y in pts], soft=0.005)  # a vertical sweep maps (u, v) to (-u, v)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    tower(k)
    mechanism(k)
    frame(k)
    seat_and_back(k)


def tower(k):
    g = SLOT / 2
    _shell(k, TY0, YS - g, TZ0, H - 0.06, "shroud")
    _shell(k, YS + g, TY1, TZ0, H - 0.06, "shroud")
    _shell(k, TY0, TY1, H - 0.06, H, "frame", grow=0.004)                      # the lid band
    _shell(k, TY0 + 0.03, TY1 - 0.03, H - 0.01, H + 0.001, "plastic", grow=-0.03)  # the recessed tray on top
    _shell(k, TY0, TY1, 0.0, TZ0, "frame", grow=-0.02)                          # the base under the shroud
    for fy in (TY0 + 0.08, TY1 - 0.08):
        k.cyl("rubber", (TX1 - TD * 0.5, fy, 0.004), 0.045, 0.012)
    # the face: the plate (header band over both placards), the logo on the lid band, the slot with the lifting rod
    fx, f0, f1 = TX1 + 0.005, TY0 + 0.04, TY1 - 0.04
    k.box("frame", (fx, (f0 + f1) / 2, (PLATE_TOP + PLATE_BOT) / 2), (0.01, f1 - f0, PLATE_TOP - PLATE_BOT), soft=0.004)
    k.box("panel", (fx + 0.006, (f0 + f1) / 2, PLATE_TOP - 0.02), (0.003, f1 - f0 - 0.03, 0.025), soft=0.0)
    k.text("label", "LEG EXTENSION", (fx + 0.009, (f0 + f1) / 2, PLATE_TOP - 0.02), 0.012, rz=math.pi / 2)
    ph = PLATE_TOP - PLATE_BOT - 0.065
    art = Path(__file__).with_name("art")
    for (y0_, y1_), img in zip(((f0 + 0.03, YS - g - 0.02), (YS + g + 0.02, f1 - 0.03)), ("placard_left.png", "placard_right.png")):
        k.decal(art / img, (fx + 0.0085, (y0_ + y1_) / 2, PLATE_BOT + 0.015 + ph / 2), y1_ - y0_, ph, "+x")
    k.text("label", "PRECOR", (TX1 + 0.002, YS, (H + PLATE_TOP) / 2 - 0.005), 0.042, rz=math.pi / 2)
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
    k.shaped_pad("frame", [(-0.13, -0.15), (0.06, -0.13), (0.15, -0.07), (0.15, 0.08), (0.06, 0.17), (-0.10, 0.13)],
                 (px_, (cy + PIV[1]) / 2, (cz + DIAL[2]) / 2), (1, 0, 0), (0, 1, 0), 0.03, r=0.035, seam=False, board=False)
    k.sweep("frame", [(cx, cy - 0.05, cz), (cx, cy + 0.06, cz)], k.circle(0.12, 64), soft=0.012)
    k.disc("frame", (cx, cy - 0.055, cz), 0.122, 0.092, 0.014, axis="y", seg=64)       # the rim, proud of the face
    k.cyl("plastic", (cx, cy - 0.05, cz), 0.093, 0.004, axis="y", seg=64)              # the recess
    k.cyl("alu", (cx, cy - 0.055, cz), 0.032, 0.012, axis="y")
    for t in range(0, 360, 60):
        k.cyl("alu", (cx + 0.06 * math.cos(math.radians(t)), cy - 0.054, cz + 0.06 * math.sin(math.radians(t))), 0.006, 0.006, axis="y", seg=12)
    k.tube("alu", (cx + 0.03, cy + 0.06, cz + 0.02), (DIAL[0] - 0.02, DIAL[1] + 0.03, DIAL[2] - 0.02), 0.038, seg=32)
    # the start dial with its numbered holes
    dx, dy, dz = DIAL
    k.disc("frame", DIAL, 0.06, 0.012, 0.014, axis="x")
    for i in range(8):
        a = math.radians(-40 + i * 22)
        k.text("label", str(i + 1), (dx + 0.009, dy + 0.045 * math.cos(a), dz + 0.045 * math.sin(a)), 0.012, rz=math.pi / 2)
    k.tube("chrome", (px_, PIV[1], PIV[2]), (PIV[0] + 0.03, PIV[1], PIV[2]), 0.02)       # the axle from the side plate
    # the lever: a straight round tube through its hub, the foam sleeve at the top, the block + silver cap below
    k.tube("frame", LE, UE, 0.025, seg=28)
    k.tube("rubber", lerp(UE, LE, 0.02), lerp(UE, LE, 0.30), 0.036, seg=28)
    k.cyl("frame", UE, 0.036, 0.012, axis="x")
    k.cyl("frame", PIV, 0.045, 0.06, axis="x", seg=32, soft=0.004)
    k.cyl("alu", (PIV[0] + 0.035, PIV[1], PIV[2]), 0.03, 0.012, axis="x")
    k.box("frame", LE, (0.06, 0.10, 0.07), soft=0.008)
    k.cyl("alu", (LE[0] + 0.035, LE[1] + 0.02, LE[2]), 0.022, 0.01, axis="x")
    # the drop arm from the block down to the roller axle, the roller across under the shins
    ry, rz = RA
    k.sweep("frame", [(LE[0], LE[1] + 0.01, LE[2] - 0.02), (LE[0], ry - 0.01, rz + 0.05), (LE[0], ry, rz)], k.stadium(0.07, 0.045), bend=0.04, up=(1, 0, 0))
    k.tube("chrome", (LE[0], ry, rz), (ROLLER[1], ry, rz), 0.016)
    k.sweep("pad", [(ROLLER[0] + 0.01, ry, rz), (ROLLER[1] - 0.012, ry, rz)], k.circle(ROLLER_R, 48), soft=0.014)
    k.sweep("plastic", [(ROLLER[1] - 0.013, ry, rz), (ROLLER[1] + 0.006, ry, rz)], k.circle(ROLLER_R - 0.003, 48), soft=0.008)
    # the two hand grips: black stubs with silver caps, on a bent tube down into the spine's front
    base = (SPINE0[0] + 0.02, SPINE0[1] + 0.03, SPINE0[2] + 0.05)
    for top in (GRIP_A, GRIP_B):
        bot = (top[0], top[1] + 0.035, top[2] - 0.11)
        k.tube("rubber", bot, top, 0.018)
        k.cyl("alu", top, 0.019, 0.016)
        k.sweep("frame", [bot, (top[0], bot[1] + 0.01, bot[2] - 0.08), base], k.circle(0.014), bend=0.04)
    # the post foot under the mechanism, into the housing
    k.bar("frame", (POST[0], POST[1], 0.03), (POST[0], POST[1], CAM[2] - 0.10), 0.085, 0.065, up=(0, 1, 0))
    k.cyl("rubber", (POST[0], POST[1], 0.012), 0.045, 0.024)


def frame(k):
    # the spine: a curved oval beam from the mechanism (big silver cap) under the seat to the carriage
    x, y, zt, wf, d, th = SEAT
    k.sweep("frame", [SPINE0, (-0.08, -0.42, 0.53), (x, -0.18, 0.465), (x, 0.08, 0.45), (x, y + d / 2 + 0.08, 0.45)], k.stadium(0.12, 0.075), bend=0.15, up=(0, 0, 1))
    k.cyl("alu", (SPINE0[0] - 0.01, SPINE0[1], SPINE0[2]), 0.034, 0.03, axis="x")
    # the user's-left side: the front leg (slanting back as it rises), a rail low along it, the rear arch, feet
    L = k.rect(0.075, 0.05, 0.01)
    k.bar("frame", (XS, FOOT_F, 0.03), FLEG_TOP, 0.08, 0.06, up=(0, 1, 0))
    k.bar("frame", (x + 0.05, FLEG_TOP[1] - 0.02, FLEG_TOP[2] - 0.02), FLEG_TOP, 0.06, 0.05)          # into the spine
    k.bar("frame", (XS, FOOT_F + 0.04, 0.15), (XS, FOOT_R - 0.06, 0.06), 0.07, 0.045)                 # the rail
    for xr in (XS, XR):  # rear arches both sides, joined at the top by a cross tube
        k.sweep("frame", [(xr, FOOT_R, 0.03), (xr, FOOT_R - 0.02, ARCH_TOP[2] - 0.05), (xr, ARCH_TOP[1] - 0.06, ARCH_TOP[2])],
                k.circle(0.032), bend=0.08)
        k.sweep("rubber", [(xr, FOOT_R, 0.0), (xr, FOOT_R, 0.03)], k.circle(0.07, 32), soft=0.006)
    k.tube("frame", (XR, ARCH_TOP[1] - 0.06, ARCH_TOP[2]), (XS, ARCH_TOP[1] - 0.06, ARCH_TOP[2]), 0.032)
    k.sweep("rubber", [(XS, FOOT_F, 0.0), (XS, FOOT_F, 0.03)], k.stadium(0.22, 0.11), soft=0.006)
    # the base: the post foot's rail curving back under the tower to the front leg, the tower's own base rail
    k.sweep("frame", [(POST[0], POST[1] + 0.02, 0.36), (POST[0], POST[1] + 0.02, 0.15), (POST[0], TY0 + 0.06, 0.15), (POST[0], FOOT_F, 0.15),
                      (XS, FOOT_F + 0.04, 0.15)], k.rect(0.075, 0.06, 0.012), bend=0.09, up=(1, 0, 0))   # the J
    k.tube("frame", (XR, ARCH_TOP[1] - 0.06, ARCH_TOP[2]), (XR, TY1 - 0.05, 0.06), 0.03)            # the far side back to the tower
    k.bar("frame", (TX1 - TD * 0.5, TY1 - 0.05, 0.05), (XR, TY1 - 0.05, 0.05), 0.06, 0.05)


def seat_and_back(k):
    x, y, zt, wf, d, th = SEAT
    tl = math.radians(SEAT_TILT)
    c = (x, y, zt - d / 2 * math.sin(tl) - th / 2)
    k.shaped_pad("pad", [(-wf / 2, -d / 2), (wf / 2, -d / 2), (SEAT_BACKW / 2, d / 2), (-SEAT_BACKW / 2, d / 2)],
                 c, (0, math.sin(tl), math.cos(tl)), (1, 0, 0), th, r=0.045)
    k.box("frame", (x, y + 0.02, c[2] - th / 2 - 0.02), (0.22, d * 0.7, 0.03), rx=-tl, soft=0.004)   # the seat pan on the spine
    # the carriage under the seat's rear: a box, the bolted bracket plate, the release lever's rod with the orange paddle
    k.box("frame", (x, y + d / 2 + 0.07, 0.47), (0.12, 0.14, 0.12), soft=0.006)
    k.box("frame", (x + 0.11, y + d / 2 + 0.17, 0.42), (0.008, 0.15, 0.25), soft=0.002)
    for by, bz in ((0.10, 0.50), (0.14, 0.45), (0.12, 0.36), (0.20, 0.33)):
        k.cyl("alu", (x + 0.115, y + d / 2 + by, bz), 0.007, 0.006, axis="x", seg=12)
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

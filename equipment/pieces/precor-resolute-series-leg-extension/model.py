"""Precor Resolute Series Leg Extension (RSL0605), matched to Precor's official render (refs/precor_official.png).

Spec (precor.com + the RSL0605 sell sheet): 155 x 127 x 148 cm (L x W x H), stack tower 148 cm, 109 kg stack, 280 kg;
upholstery 65 mm (19 mm plywood + 2 x 19 mm foam + vinyl), colour All Spice; frame Black Pearl powder coat; shroud
Tungsten. Start position, roller pad and the gas-assisted back pad adjust from the seat.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left. The stack tower stands on the user's right with
its flat face (slot, placards, logo) turned to the seat; its front end is round.
The numbers below are fitted to the photo through equipment/tools/camsolve.py (anchors at the bottom of the constants).
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
    "placard": dict(color=(0.62, 0.63, 0.65), rough=0.25, coat=0.6),
    "panel": dict(color=(0.03, 0.035, 0.045), rough=0.25, coat=0.6),                                 # the dark placard frame
    "alu": dict(color=(0.8, 0.8, 0.81), rough=0.22, metal=1.0, aniso=0.3),                            # the silver caps
}
VIEWS = {"three_quarter": (40, 16, 1.0)}

# ---- the tower (D plan: the flat face at x = TX1 its whole length, the back one half-ellipse)
TX1, TD = -0.30, 0.32            # face plane, depth of the ellipse behind it (towards -x)
TY0, TY1 = -0.40, 0.20           # the face's front and rear ends
H, LID = 1.48, 0.13              # top, the lid band (seam on the round end; on the face the plate covers it)
PLATE_TOP, PLATE_BOT, HEADER = 1.405, 0.98, 0.085   # the raised face plate (header band + placards), z
YS, SLOT = -0.06, 0.045          # the slot through the shroud (centre y, width)
TYAW = 0.0                       # the tower turned about z (deg, + = face turned towards the front), about (TX1, YS)
STACK_N, STACK_T = 20, 0.0254
# ---- the mechanism
PIV = (-0.26, -0.36, 0.62)       # the cam axle + start dial (along x) on the housing
LEV_T = 0.45                     # where along the lever (LE -> UE) its hub is, bolted to the cam arm
LE = (-0.20, -0.66, 0.20)        # the lever's lower end
UE = (-0.20, -0.05, 1.02)        # its upper end (foam sleeve)
RA = (-0.60, 0.17)               # roller axle (y, z)
ROLLER = (-0.18, 0.265)          # x from, x to
ROLLER_R = 0.062                 # its radius
ROLL_TIP = (0.0, 0.0)            # the roller's +x end moved (dy, dz) from level: the pad's own angle in the photo
POST = (-0.47, -0.60)            # the round post foot under the mechanism
DRUM = (-0.45, -0.55, 0.50)      # centre of the open cam cover (axis along x)
DRUM_R = 0.14
GRIP_A, GRIP_B = (-0.17, -0.37, 0.74), (-0.17, -0.18, 0.70)   # tops of the two silver-capped grips by the knee
# ---- the frame + seat
XS = 0.30                        # the user's-left side frame
FOOT_F, FOOT_R = -0.20, 0.62     # its feet (y)
SEAT = (0.03, -0.02, 0.52, 0.46, 0.50, 0.075)   # x, y, top z, width x, depth y, thickness
BACK = (0.02, 0.26, 0.56, 0.78, 0.42, 0.07)   # x, bottom front edge y + z, height, bottom width, thickness
BACK_LEAN, BACK_TOPW = 18.0, 0.36             # lean from vertical (deg), width at the top (the pad tapers)
SEAT_TILT = 0.0                  # the seat's front raised (deg)
ORANGE = (0.25, 0.40, 0.80)      # the orange back-pad release paddle, on its rod up from the seat carriage
FLEG_TOP = (0.28, -0.12, 0.42)   # the user's-left front leg meets the seat frame here
ARCH_TOP = (0.27, 0.50, 0.40)    # the rear leg's arch, where it turns forward under the seat


# solved with the camera of the official photo (equipment/tools/camsolve.py), each held to its value above by sigma (m)
FIT = {"TX1": 0.06, "TD": 0.06, "TY0": 0.08, "TY1": 0.08, "YS": 0.05, "PIV": 0.06, "LE": 0.08, "UE": 0.08, "RA": 0.06,
       "POST": 0.08, "XS": 0.06, "FOOT_F": 0.08, "FOOT_R": 0.08, "SEAT": 0.05, "BACK": 0.06, "BACK_LEAN": 6.0, "BACK_TOPW": 0.06, "DRUM": 0.10, "ROLLER": 0.10, "LEV_T": 0.15, "DRUM_R": 0.04, "GRIP_A": 0.08, "GRIP_B": 0.08, "FLEG_TOP": 0.08, "SEAT_TILT": 4.0, "ORANGE": 0.08,  "ARCH_TOP": 0.08, "PLATE_TOP": 0.04, "PLATE_BOT": 0.06, "HEADER": 0.03}
_ff = Path(__file__).with_name("fit.json")
if _ff.exists() and not os.environ.get("EQ_NOFIT"):
    globals().update({k_: (tuple(v_) if isinstance(v_, list) else v_) for k_, v_ in json.loads(_ff.read_text()).items()})


def _bp():
    a = math.radians(90 - BACK_LEAN)
    up = (0.0, math.cos(a), math.sin(a))                  # along the pad, bottom to top
    nrm = (0.0, -math.sin(a), math.cos(a))                # its face normal (towards the user)
    return a, up, nrm


def _back_top(sx):
    a, up, nrm = _bp()
    return (BACK[0] + sx * BACK_TOPW / 2, BACK[1] + up[1] * BACK[3], BACK[2] + up[2] * BACK[3])


def tw(p):
    """A point of the tower (designed square to the seat) turned by TYAW about the slot line."""
    a = math.radians(TYAW)
    dx, dy = p[0] - TX1, p[1] - YS
    return (TX1 + dx * math.cos(a) - dy * math.sin(a), YS + dx * math.sin(a) + dy * math.cos(a), p[2])


def anchors():
    x, y, zt, w, d, th = SEAT
    return {k_: (tw(v_) if k_.startswith(("tower", "plate", "logo", "slot")) else v_) for k_, v_ in {
        "tower_top_rear_face": (TX1, TY1, H),
        "plate_top_rear": (TX1, TY1 - 0.01, PLATE_TOP),
        "plate_top_front": (TX1, TY0 + 0.01, PLATE_TOP),
        "plate_bot_front": (TX1, TY0 + 0.01, PLATE_BOT),
        "tower_face_rear_bottom": (TX1, TY1, 0.06),
        "logo": (TX1, YS, (H + PLATE_TOP) / 2),
        "slot_top": (TX1, YS, PLATE_TOP - HEADER),
        "dial": (PIV[0] + 0.03, PIV[1], PIV[2]),
        "lever_hub": tuple(LE[i] + (UE[i] - LE[i]) * LEV_T + (0.035 if i == 0 else 0) for i in range(3)),
        "lever_top": UE,
        "lever_low": LE,
        "drum": DRUM,
        "grip_a": (GRIP_A[0], GRIP_A[1], GRIP_A[2] + 0.017),
        "grip_b": (GRIP_B[0], GRIP_B[1], GRIP_B[2] + 0.017),
        "front_leg_top": FLEG_TOP,
        "arch_top": ARCH_TOP,
        "roller_cap": (ROLLER[1] + 0.012, RA[0] + ROLL_TIP[0], RA[1] + ROLL_TIP[1]),
        "roller_far_end": (ROLLER[0], RA[0], RA[1]),
        "post_foot": (POST[0], POST[1], 0.0),
        "foot_front": (XS, FOOT_F, 0.03),
        "foot_rear": (XS, FOOT_R, 0.03),
        "seat_front_left": (x + w / 2, y - d / 2, zt - 0.01 + d / 2 * math.sin(math.radians(SEAT_TILT))),
        "seat_rear_left": (x + w / 2, y + d / 2, zt - 0.01 - d / 2 * math.sin(math.radians(SEAT_TILT))),
        "orange": ORANGE,
        "backpad_bot_left": (BACK[0] + BACK[4] / 2, BACK[1], BACK[2]),
        "backpad_bot_right": (BACK[0] - BACK[4] / 2, BACK[1], BACK[2]),
        "backpad_top_left": _back_top(1),
        "backpad_top_right": _back_top(-1),
    }.items()}


ANCHORS = anchors()
SPEC = (1.55, 1.27, 1.48)   # Precor's overall L (y) x W (x) x H


def extents():
    """Overall L, W, H of the machine from the current numbers (for the solver to hold to SPEC)."""
    x, y, zt, w, d, th = SEAT
    xs = [TX1 - TD, ROLLER[1] + 0.01, XS + 0.06, x + w / 2, BACK[0] + BACK[4] / 2]
    a, up, nrm = _bp()
    ys = [RA[0] - ROLLER_R, POST[1] - 0.05, TY0, FOOT_F - 0.12, FOOT_R + 0.12, TY1, BACK[1] + up[1] * BACK[3] + 0.07]
    return (max(ys) - min(ys), max(xs) - min(xs), H)


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
    # ================= the tower (built square to the seat, then turned by TYAW about the slot line)
    kk, k = k, k.sub("tower", (TX1, YS, 0.0), TYAW)
    g = SLOT / 2
    _shell(k, TY0, YS - g, 0.06, H - LID, "shroud")
    _shell(k, YS + g, TY1, 0.06, H - LID, "shroud")
    # the lid over the whole plan, a touch proud, a recessed tray on top; the black plinth under it all
    _shell(k, TY0, TY1, H - LID, H, "frame", grow=0.005)
    _shell(k, TY0 + 0.03, TY1 - 0.03, H - 0.012, H + 0.001, "plastic", grow=-0.03)
    _shell(k, TY0, TY1, 0.0, 0.06, "frame", grow=0.01)
    # the face: the raised plate (header band across the slot, two placards below it), the logo on the lid band above
    fx, f0, f1 = TX1 + 0.005, TY0 + 0.01, TY1 - 0.01
    k.box("frame", (fx, (f0 + f1) / 2, PLATE_TOP - HEADER / 2), (0.01, f1 - f0, HEADER), soft=0.004)
    for y0_, y1_ in ((f0, YS - g), (YS + g, f1)):
        k.box("frame", (fx, (y0_ + y1_) / 2, (PLATE_BOT + PLATE_TOP - HEADER) / 2), (0.01, y1_ - y0_, PLATE_TOP - HEADER - PLATE_BOT), soft=0.004)
    k.box("panel", (fx + 0.006, (f0 + f1) / 2, PLATE_TOP - HEADER / 2 - 0.005), (0.003, f1 - f0 - 0.06, HEADER * 0.55), soft=0.0)
    k.text("label", "LEG EXTENSION", (fx + 0.009, YS, PLATE_TOP - HEADER / 2 - 0.005), 0.016, rz=math.pi / 2)
    ph = PLATE_TOP - HEADER - PLATE_BOT - 0.016
    for y0_, y1_ in ((f0 + 0.03, YS - g - 0.02), (YS + g + 0.02, f1 - 0.03)):
        k.box("panel", (fx + 0.006, (y0_ + y1_) / 2, PLATE_BOT + 0.006 + ph / 2), (0.003, y1_ - y0_ + 0.012, ph + 0.012), soft=0.0)
    art = Path(__file__).with_name("art")
    for (y0_, y1_), img in zip(((f0 + 0.03, YS - g - 0.02), (YS + g + 0.02, f1 - 0.03)), ("placard_left.png", "placard_right.png")):
        k.decal(art / img, (fx + 0.0085, (y0_ + y1_) / 2, PLATE_BOT + 0.006 + ph / 2), y1_ - y0_, ph, "+x")
    k.text("label", "PRECOR", (TX1 + 0.002, YS + 0.005, (H + PLATE_TOP) / 2), 0.045, rz=math.pi / 2)
    # the slot: dark sides, the chrome lifting rod up its middle, the stack at its foot with numbers on the plate fronts
    sx = TX1 - TD / 2
    for s in (-1, 1):
        k.box("plastic", (sx, YS + s * (g + 0.002), 0.66), (TD - 0.02, 0.004, 1.14), soft=0.0)
    k.tube("chrome", (sx, YS, 0.1), (sx, YS, H - LID - 0.02), 0.0095)
    ztop = 0.07
    for i in range(STACK_N):
        z = 0.07 + i * STACK_T + STACK_T / 2
        k.box("plate", (sx, YS, z), (0.12, 0.27, STACK_T - 0.0012), soft=0.003)
        k.box("label", (TX1 - 0.005, YS + g + 0.012, z), (0.002, 0.014, 0.009), soft=0.0)
        ztop = z + STACK_T / 2
    k.box("plate", (sx, YS, ztop + 0.03), (0.12, 0.27, 0.06), soft=0.006)
    for s in (-1, 1):
        k.tube("chrome", (sx, YS + s * 0.11, 0.06), (sx, YS + s * 0.11, H - LID), 0.0127)
    # the orange selector pin + its keeper, left of the slot at the top of the stack
    k.cyl("accent", (TX1 + 0.02, YS - g - 0.02, ztop + 0.02), 0.012, 0.05, axis="x")
    k.box("accent", (TX1 + 0.012, YS - g - 0.025, ztop + 0.09), (0.02, 0.05, 0.022), soft=0.006)
    k = kk

    # ================= the knee mechanism at the tower's round front end
    px, py, pz = PIV
    _drum(k, DRUM, DRUM_R, 0.13)                 # the open cam cover
    k.tube("chrome", (sx, py, pz), (px + 0.03, py, pz), 0.022)               # axle
    k.cyl("frame", (TX1 + 0.04, py, pz), 0.06, 0.08, axis="x", seg=40, soft=0.006)
    k.disc("frame", (px + 0.005, py, pz), 0.085, 0.024, 0.014, axis="x")     # the start dial
    for i in range(5):
        a = math.radians(100 + i * 22)
        k.text("label", str(i + 1), (px + 0.014, py + 0.07 * math.cos(a), pz + 0.07 * math.sin(a)), 0.016, rz=math.pi / 2)
    # the lever: a straight round tube from low in front up past the knee, a foam sleeve on top, a silver bolt cap
    k.tube("frame", LE, UE, 0.026, seg=28)
    lerp = lambda a_, b_, f: tuple(a_[i] + (b_[i] - a_[i]) * f for i in range(3))
    k.tube("rubber", lerp(UE, LE, 0.02), lerp(UE, LE, 0.33), 0.036, seg=28)
    hub = lerp(LE, UE, LEV_T)
    k.cyl("frame", hub, 0.04, 0.05, axis="x", seg=32, soft=0.004)
    k.cyl("alu", (hub[0] + 0.03, hub[1], hub[2]), 0.03, 0.02, axis="x")
    k.sweep("frame", [(hub[0] - 0.03, hub[1], hub[2]), (px - 0.02, py, pz)], k.rect(0.02, 0.07, 0.008), up=(0, 0, 1))  # the cam arm plate
    lc = lerp(LE, UE, 0.12)
    k.cyl("alu", (lc[0] + 0.03, lc[1], lc[2]), 0.028, 0.02, axis="x")
    # the J arm under to the roller, the roller across under the shins
    ry, rz = RA
    k.sweep("frame", [LE, (LE[0], LE[1] - 0.05, LE[2] - 0.10), (LE[0], ry - 0.02, rz - 0.13), (LE[0], ry + 0.06, rz - 0.06), (LE[0], ry, rz)],
            k.stadium(0.075, 0.045), bend=0.06, up=(1, 0, 0))
    tip = (ROLLER[1], ry + ROLL_TIP[0], rz + ROLL_TIP[1])
    k.tube("chrome", (LE[0], ry, rz), tip, 0.016)
    lr = math.dist((ROLLER[0], ry, rz), tip)
    f0, f1 = 0.02 / lr, 1 - 0.012 / lr
    a_ = tuple(ROLLER[0 if i == 0 else 0] if False else (ROLLER[0], ry, rz)[i] + (tip[i] - (ROLLER[0], ry, rz)[i]) * f0 for i in range(3))
    b_ = tuple((ROLLER[0], ry, rz)[i] + (tip[i] - (ROLLER[0], ry, rz)[i]) * f1 for i in range(3))
    k.sweep("pad", [a_, b_], k.circle(ROLLER_R, 48), soft=0.014)
    c_ = tuple((ROLLER[0], ry, rz)[i] + (tip[i] - (ROLLER[0], ry, rz)[i]) * (1 + 0.008 / lr) for i in range(3))
    k.sweep("plastic", [b_, c_], k.circle(ROLLER_R - 0.003, 48), soft=0.008)
    # the hand grips by the knee: a bent U tube with two short silver-capped stubs pointing up
    ga, gb = GRIP_A, GRIP_B
    base = (ga[0] - 0.02, (ga[1] + gb[1]) / 2, 0.47)   # the U's bottom, bolted onto the spine
    k.sweep("frame", [(ga[0], ga[1], ga[2] - 0.09), (ga[0], ga[1] - 0.02, ga[2] - 0.2), base], k.circle(0.016), bend=0.05)
    k.sweep("frame", [base, (gb[0], gb[1] + 0.03, gb[2] - 0.2), (gb[0], gb[1], gb[2] - 0.09)], k.circle(0.016), bend=0.05)
    for top in (ga, gb):
        k.tube("rubber", (top[0], top[1], top[2] - 0.10), (top[0], top[1], top[2]), 0.019)
        k.cyl("alu", (top[0], top[1], top[2] + 0.008), 0.02, 0.018)
        k.cyl("alu", (top[0], top[1], top[2] - 0.103), 0.0205, 0.008)
    # the post foot under the mechanism
    k.tube("frame", (POST[0], POST[1], 0.03), (POST[0], POST[1], DRUM[2] - DRUM_R * 0.5), 0.034)   # up into the cam cover
    k.cyl("rubber", (POST[0], POST[1], 0.0), 0.046, 0.03)

    # ================= the frame
    # the curved oval spine from the mechanism under the seat, a silver cap where it bolts on
    k.sweep("frame", [(TX1 + 0.02, -0.40, 0.47), (-0.10, -0.30, 0.45), (0.0, -0.05, 0.42), (0.02, 0.30, 0.41)], k.stadium(0.11, 0.06), bend=0.2, up=(0, 0, 1))
    k.cyl("alu", (TX1 + 0.06, -0.41, 0.47), 0.038, 0.03, axis="x")
    # the user's-left side: front leg, floor rail, arched rear leg, oval foot pads
    k.bar("frame", (XS, FOOT_F, 0.03), FLEG_TOP, 0.085, 0.06, up=(0, 1, 0))
    k.bar("frame", (XS, FOOT_F, 0.045), (XS, FOOT_R, 0.045), 0.075, 0.055)
    k.sweep("frame", [(XS, FOOT_R, 0.03), (ARCH_TOP[0], FOOT_R + 0.02, ARCH_TOP[2] - 0.02), ARCH_TOP, (ARCH_TOP[0] - 0.06, SEAT[1] + SEAT[4] / 2 - 0.05, SEAT[2] - SEAT[5] - 0.04)],
            k.stadium(0.09, 0.07), bend=0.10, up=(1, 0, 0))
    for fy in (FOOT_F, FOOT_R):
        k.sweep("rubber", [(XS, fy, 0.0), (XS, fy, 0.03)], k.stadium(0.24, 0.12), soft=0.006)
    # cross rails from the tower base to the side frame
    k.bar("frame", (TX1 - 0.02, FOOT_F + 0.02, 0.05), (XS, FOOT_F + 0.02, 0.05), 0.07, 0.05)
    k.bar("frame", (TX1 - 0.02, 0.10, 0.06), (XS, 0.10, 0.06), 0.07, 0.05)
    k.bar("frame", (0.02, 0.10, 0.06), (0.02, 0.28, 0.40), 0.07, 0.05)

    # ================= the seat, its carriage, the back pad
    x, y, zt, w, d, th = SEAT
    k.box("frame", (x, y, zt - th - 0.015), (w - 0.14, d - 0.10, 0.03), soft=0.004)
    tl = math.radians(SEAT_TILT)
    k.shaped_pad("pad", [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)],
                 (x, y, zt - th / 2), (0, math.sin(tl), math.cos(tl)), (1, 0, 0), th, r=0.04)
    # the carriage at the seat's rear left: a box with a knob, the back-pad release handle, a bolted bracket plate
    k.box("frame", (0.22, 0.25, 0.42), (0.09, 0.12, 0.13), soft=0.006)
    k.cyl("plastic", (0.22, 0.25, 0.495), 0.012, 0.02)
    k.sweep("frame", [(0.24, 0.22, 0.44), (0.30, 0.22, 0.44), (0.32, 0.22, 0.40), (0.32, 0.12, 0.36), (0.24, 0.08, 0.35)], k.circle(0.013), bend=0.03)
    k.cyl("alu", (0.25, 0.22, 0.44), 0.016, 0.03, axis="x")
    k.box("frame", (0.20, 0.13, 0.32), (0.006, 0.20, 0.11), soft=0.002)
    for by, bz in ((0.12, 0.35), (0.12, 0.33), (0.17, 0.30)):
        k.cyl("alu", (0.204, by, bz), 0.006, 0.006, axis="x", seg=12)
    # the back post, the pad on it, the gas spring, the orange handle on the pad's left edge
    a, up, nrm = _bp()
    bx, by0, bz0, bh, bw, bt = BACK
    pb = (bx, by0 + up[1] * 0.12 - nrm[1] * (bt + 0.02), bz0 + up[2] * 0.12 - nrm[2] * (bt + 0.02))   # behind the pad, near its foot
    k.tube("frame", (bx, pb[1] - 0.03, SEAT[2] - SEAT[5] - 0.05), pb, 0.04, seg=32)                    # the round back post
    c = (bx, by0 + up[1] * bh / 2 - nrm[1] * bt / 2, bz0 + up[2] * bh / 2 - nrm[2] * bt / 2)
    k.shaped_pad("pad", [(-bw / 2, -bh / 2), (bw / 2, -bh / 2), (BACK_TOPW / 2, bh / 2), (-BACK_TOPW / 2, bh / 2)],
                 c, nrm, (1, 0, 0), bt, r=0.04)
    rod0 = (0.20, SEAT[1] + SEAT[4] / 2 - 0.02, SEAT[2] - SEAT[5] - 0.06)               # from the seat carriage
    k.tube("frame", rod0, ORANGE, 0.007)
    k.box("accent", ORANGE, (0.022, 0.07, 0.085), rx=math.atan2(ORANGE[1] - rod0[1], ORANGE[2] - rod0[2]), soft=0.008)


def _drum(k, c, r, w):
    """The cam cover: a smooth open shell of a drum on the x axis (from below the front round over the top), rims at both sides."""
    cx, cy, cz = c
    arc = [math.radians(t) for t in range(215, 506, 6)]   # all round except the front (open towards the user)
    outer = [(-(r * math.cos(t)), r * math.sin(t)) for t in arc]               # profile (u, v): world y = -u, z = v
    inner = [(-((r - 0.008) * math.cos(t)), (r - 0.008) * math.sin(t)) for t in reversed(arc)]
    k.sweep("frame", [(cx - w / 2, cy, cz), (cx + w / 2, cy, cz)], outer + inner, up=(0, 0, 1), soft=0.003)
    rim_o = [(-((r + 0.006) * math.cos(t)), (r + 0.006) * math.sin(t)) for t in arc]
    rim_i = [(-((r - 0.03) * math.cos(t)), (r - 0.03) * math.sin(t)) for t in reversed(arc)]
    for s_ in (-1, 1):
        k.sweep("frame", [(cx + s_ * w / 2 - 0.006, cy, cz), (cx + s_ * w / 2 + 0.006, cy, cz)], rim_o + rim_i, up=(0, 0, 1), soft=0.003)
    k.cyl("frame", (cx, cy, cz), r * 0.62, w * 0.45, axis="x", seg=64, soft=0.006)       # the cam inside
    for t in range(0, 360, 45):                                                           # its bolt circle
        k.cyl("alu", (cx + w * 0.23, cy + r * 0.42 * math.cos(math.radians(t)), cz + r * 0.42 * math.sin(math.radians(t))), 0.007, 0.006, axis="x", seg=12)

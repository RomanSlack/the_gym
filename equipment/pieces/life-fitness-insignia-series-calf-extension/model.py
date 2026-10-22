"""Life Fitness Insignia Series Calf Extension (rotary, seated), Charcoal frame / Black upholstery, the foot bar at its
start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit (titanium
frame) photographed all round at Fitness Equipment Empire (ref_02 / ref_03 / ref_04 / ref_10 three-quarters, ref_05
the placard, ref_06 the stack's numbers and the seat, ref_07 / ref_08 / ref_09 the back), held to Life Fitness's height
of 58.1 in (148 cm) and about 70 x 41 in.
The same family frame as the Insignia Leg Extension (its model.py: the base's low and rear beams, the seat, the back
pad's carriage are imported from it), the back pad nearly upright; this one's own parts: the tower a little further
forward (ref_03: the seat's front behind its front edge, the foot bar about 0.29 m beyond it); the front frame on
the tower side (the foot, the leg up to the housing, the strut back down to the low beam); the axle through the
housing with the cam on its tower side and the start-position disc and pin on the other; the long foot bar on the
axle's end, cantilevered across both feet (the balls of the feet on its back face, the heels dropping, the bar turning
forward on the axle); the seat's front post and the cross beam to it; the cable from the cam to the tower's foot.
Axes as the leg extension: metres, floor z = 0, the user sits facing -y, x+ = the user's left, the tower on the right.
"""
import importlib.util
import math
from pathlib import Path

import stack_tower

_spec = importlib.util.spec_from_file_location(
    "insignia_leg_extension", Path(__file__).resolve().parent.parent / "life-fitness-insignia-series-leg-extension" / "model.py")
le = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(le)

LOOK = le.LOOK
VIEWS = le.VIEWS
DETAILS = {
    "detail_bar": ((0.70, -1.65, 1.0), (-0.10, -0.90, 0.52), 45),      # the foot bar, its hub, the cam, the pin
    "detail_back": le.DETAILS["detail_back"],
}

TOWER = dict(le.TOWER, title="CALF EXTENSION")
T, FOOT_H, Z, X, Y = le.T, le.FOOT_H, le.Z, le.X, le.Y
TC = (le.TC[0], -0.20)               # the tower: the seat's front behind its front edge, the foot bar about 0.29 m beyond it (ref_03)
X_FACE = le.X_FACE
PX = le.PIV[0]                       # the housing (x), on the tower side
AXLE = (-0.92, 0.49)                 # the foot bar's axle (y, z): under the balls of the feet, legs out from the seat
BAR = (-0.24, 0.50)                  # the foot bar's ends (x): past the seat's open side (ref_01 / ref_03)
LEAN = math.radians(12)              # the back pad: nearly upright (ref_01)
SEAT_DZ = -0.08                      # the seat lower than the leg extension's, its top at 0.48 (ref_01)
SEAT_FRONT = -0.42                   # and longer, its front near the foot bar
BACK_TALL = 0.16                     # the back pad taller (ref_01)
H0, H1 = 0.32 + BACK_TALL / 2, 0.30 + BACK_TALL / 2
BACK_OUTLINE = [(-0.20, -H0), (0.20, -H0), (0.20, -0.02), (0.15, 0.08), (0.15, H1), (-0.15, H1), (-0.15, 0.08), (-0.20, -0.02)]
                                     # wide at the lumbar, stepping in to the narrower upper back (ref_01 / ref_10)


def build(k):
    tw = stack_tower.tower(k, TOWER, TC, 90.0)
    ay, az = AXLE
    # ---- the front frame: the foot, the leg up to the housing, the strut back down to the low beam's front
    y_low = ay + 0.24
    le.foot(k, PX, ay - 0.14, 0.12)
    k.sweep("frame", [(PX, ay - 0.14, FOOT_H), (PX, ay - 0.10, 0.20), (PX, ay, az - 0.07)], k.rect(T, T, 0.008),
            bend=0.06, up=(1, 0, 0), cut0=((0, 0, FOOT_H), Z), soft=0.002)
    k.bar("frame", (PX, ay + 0.02, az - 0.10), (PX, y_low, le.RZ0 + 0.02), 0.06, 0.06)
    le.base(k, y_low, on_tower=False)
    # ---- the seat's curved front post and the cross beam to its foot from the low beam; the seat; the back pad
    sy = SEAT_FRONT + 0.08
    sz = le.SPINE_Z + SEAT_DZ
    yf = sy + 0.16                                   # the post's foot, behind the seat's front: it curves forward up
    le.foot(k, 0.0, yf, 0.11)
    k.sweep("frame", [(0, yf, FOOT_H), (0, yf, 0.16), (0, sy + 0.02, sz - 0.08), (0, sy, sz - 0.01)], k.circle(0.036, 24),
            bend=0.12, cut0=((0, 0, FOOT_H), Z), soft=0.002)                       # (ref_01)
    k.bar("frame", (PX + T / 2, yf, le.RZ0), (-0.036, yf, le.RZ0), T, 0.05,
          cut0=((PX + T / 2, 0, 0), X), cut1=((-0.036, 0, 0), X), weld=True)
    le.seat(k, SEAT_DZ, SEAT_FRONT)
    le.back(k, LEAN, SEAT_DZ, BACK_TALL, BACK_OUTLINE)
    # ---- the housing, the axle through it, the cam on the tower side, the start-position disc and its pin on the
    # other with the chrome pull (ref_01)
    k.box("frame", (PX, ay, az), (0.10, 0.14, 0.14), soft=0.008)
    x0, x1 = BAR
    k.tube("steel", (PX - 0.075, ay, az), (x0 + 0.02, ay, az), 0.022, seg=20)
    cx_ = PX - 0.062
    k.cyl("cam", (cx_, ay, az), 0.12, 0.022, axis="x", seg=48, soft=0.003)
    k.disc("steel", (cx_, ay, az), 0.122, 0.10, 0.018, axis="x", seg=48)
    k.bolt((PX - 0.075, ay, az), "-x", size=0.026)
    k.disc("cam", (PX + 0.056, ay, az), 0.10, 0.03, 0.012, axis="x", seg=40)
    for i in range(8):
        a = math.radians(-60 + 18 * i)
        k.cyl("hole", (PX + 0.0625, ay + 0.08 * math.cos(a), az + 0.08 * math.sin(a)), 0.006, 0.001, axis="x", seg=12, soft=0.0)
    pz = az + 0.10
    k.box("frame", (PX + 0.03, ay + 0.02, pz), (0.04, 0.04, 0.06), soft=0.002)                     # the pin's housing
    k.tube("chrome", (PX + 0.05, ay + 0.02, pz), (PX + 0.12, ay + 0.02, pz + 0.03), 0.008, seg=14)
    k.cyl("yellow", (PX + 0.13, ay + 0.02, pz + 0.035), 0.017, 0.022, axis="x", seg=20, soft=0.004)
    # ---- the foot bar: its hub on the axle's end, the bar across both feet, a grip strip on its back face (the
    # balls of the feet), three bolt heads on its front (ref_01)
    k.tube("lever", (x0 - 0.04, ay, az), (x0 + 0.03, ay, az), 0.05, seg=32)
    bz = az + 0.06
    k.box("lever", (x0 + 0.02, ay, (az + bz) / 2), (0.05, 0.06, bz - az + 0.04), soft=0.004)
    k.box("lever", ((x0 + x1) / 2 + 0.02, ay, bz), (x1 - x0 + 0.04, 0.10, 0.13), soft=0.02)
    k.box("rubber", ((x0 + x1) / 2 + 0.03, ay + 0.051, bz + 0.01), (x1 - x0 - 0.04, 0.003, 0.09), soft=0.001)
    for i in range(3):
        k.cyl("lever", (x0 + 0.15 + i * 0.20, ay - 0.051, bz), 0.016, 0.004, axis="y", seg=20, soft=0.001)
    # ---- the cable: off the cam's bottom, back and down to the pulley at the tower's foot, in through its face
    yq = TC[1] - TOWER["W"] / 2 + 0.16
    k.box("frame", (X_FACE + 0.03, yq, 0.12), (0.06, 0.06, 0.12), soft=0.004)
    k.pulley((X_FACE + 0.035, yq, 0.12), 0.04, axis="x")
    k.cable([(cx_, ay + 0.02, az - 0.12), (cx_ + 0.005, ay + 0.08, 0.25), (X_FACE + 0.035, yq - 0.04, 0.13)])
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)
    k.cable([(X_FACE - 0.02, yq, 0.12), (out[0] - 0.02, yq, 0.12), (out[0] - 0.02, out[1], oz - 0.06), out])

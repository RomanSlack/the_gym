"""Life Fitness Insignia Series Seated Leg Curl, Charcoal frame / Black upholstery, the lever and the thigh pad at their
start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit in black
photographed all round at Fitness Equipment Empire (ref_02 / ref_03 / ref_08 three-quarters, ref_04 square on from the
user's front, ref_05 / ref_07 the sides, ref_06 the back), held to Life Fitness's 61 x 39.7 x 58.1 in
(155 x 101 x 148 cm, L x W x H).
The same frame as the Insignia Leg Extension (its model.py: the tower, the base's rear, the seat, the back pad's
carriage, the cam and the start-position handle are imported from it); this one's own parts:
the front frame on the tower side, a post from its foot splitting into a branch up to the lever's housing and an
upright on to the thigh arm's hinge above the knee (ref_01); the thigh arm back from the hinge over the knees, the
cross beam on its end carrying the long thigh pad across both thighs and the two grips, its angle set by the
telescoping strut from the housing with a yellow pop pin; the seat's straight front post and the low cross beam to
it; the lever forward to the calf roller (the legs out straight at the start, the roller under the ankles).
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
    "detail_lever": ((0.75, -1.25, 1.05), (-0.20, -0.40, 0.70), 45),   # the front frame, the thigh arm and pad, the roller
    "detail_back": le.DETAILS["detail_back"],
}

TOWER = dict(le.TOWER, title="SEATED LEG CURL")
T, FOOT_H, Z, X, Y = le.T, le.FOOT_H, le.Z, le.X, le.Y
PIV, LX = le.PIV, le.LX
Y_FOOT = -0.55                       # the front frame's foot (y)
HINGE = (-0.64, 1.04)                # the thigh arm's hinge (y, z): the front frame's top, well ahead of the knee (ref_01)
PAD_Y = -0.17                        # the thigh pad over the thighs just behind the knee
PAD_TOP = 0.79                       # its underside on the thighs: the seat's top at 0.56 + a thigh about 0.15
DROP = math.radians(16)              # the lever at its start: out level with the legs, the roller under the ankles
ARM = 0.44


def build(k):
    tw = stack_tower.tower(k, TOWER, le.TC, 90.0)
    px, py, pz = PIV
    # ---- the front frame: its foot, the post up to a knot, a branch back to the lever's housing, the upright on to
    # the thigh arm's hinge
    le.foot(k, px, Y_FOOT, 0.12)
    knot = (px, Y_FOOT + 0.08, 0.42)
    k.sweep("frame", [(px, Y_FOOT, FOOT_H), (px, Y_FOOT + 0.02, 0.25), knot], k.rect(T, T, 0.008), bend=0.08,
            up=(1, 0, 0), cut0=((0, 0, FOOT_H), Z), soft=0.002)
    k.sweep("frame", [knot, (px, py - 0.02, pz - 0.18), (px, py, pz - 0.06)], k.rect(0.07, 0.07, 0.008), bend=0.06,
            up=(1, 0, 0), soft=0.002)
    hy, hz = HINGE
    k.sweep("frame", [knot, (px, hy + 0.06, 0.70), (px, hy, hz - 0.05)], k.rect(T, T, 0.008), bend=0.08,
            up=(1, 0, 0), soft=0.002)
    le.base(k, Y_FOOT)
    # ---- the seat's straight front post on its foot, the low cross beam to it from the base's side beam
    sy = le.SEAT[1] + 0.08
    le.foot(k, 0.0, sy, 0.11)
    k.bar("frame", (0, sy, FOOT_H), (0, sy, le.SPINE_Z - T / 2), T, T, cut0=((0, 0, FOOT_H), Z), weld=True)
    k.bar("frame", (px + T / 2, sy, le.RZ0), (-T / 2, sy, le.RZ0), T, 0.05,
          cut0=((px + T / 2, 0, 0), X), cut1=((-T / 2, 0, 0), X), weld=True)
    le.seat(k)
    le.back(k)
    le.cam(k, tw)
    # ---- the thigh arm: its hub on the hinge pin, level back over the knees, then down to the cross beam; the
    # cross beam across the thighs, the board and the long pad under it, the two grips up off it
    k.box("frame", (px, hy, hz - 0.03), (0.10, 0.10, 0.06), soft=0.004)
    k.tube("steel", (px - 0.06, hy, hz), (px + 0.06, hy, hz), 0.014, seg=16)
    k.tube("lever", (px - 0.045, hy, hz), (px + 0.045, hy, hz), 0.04, seg=28)
    zb = PAD_TOP + 0.02 + 0.03 - 0.002                       # the cross beam's centre, on the board
    k.sweep("lever", [(px, hy + 0.03, hz), (px, PAD_Y - 0.06, hz - 0.01), (px, PAD_Y, zb + 0.03)], k.rect(0.06, 0.07, 0.008),
            bend=0.06, up=(1, 0, 0), soft=0.002)
    k.bar("lever", (px - 0.03, PAD_Y, zb), (0.22, PAD_Y, zb), 0.06, 0.06)
    k.box("plastic", (0.225, PAD_Y, zb), (0.01, 0.062, 0.062), soft=0.003)
    k.box("frame", (-0.02, PAD_Y, PAD_TOP + 0.01), (0.40, 0.08, 0.02), soft=0.002)
    k.pad("pad", (-0.02, PAD_Y, PAD_TOP - 0.04), (0.46, 0.15, 0.08), r=0.035)
    for x in (-0.14, 0.15):
        g0 = (x, PAD_Y, zb + 0.03)
        g1 = (x, PAD_Y + 0.04, zb + 0.14)
        g2 = (x, PAD_Y + 0.07, zb + 0.24)
        k.tube("chrome", (x, PAD_Y, zb), g1, 0.012, seg=16)
        k.tube("rubber", g1, g2, 0.02, seg=20)
        k.cyl("plastic", g2, 0.022, 0.01, axis="z", seg=20, soft=0.003)
    # the strut setting its angle: the outer tube on a bracket on the housing's top, the chrome inner tube up into a
    # bracket under the arm, the yellow pop pin on the outer tube's collar
    ys = py + 0.03
    za = hz - 0.005 * (ys - hy) / (PAD_Y - 0.06 - hy) - 0.035      # the arm's underside over the strut
    k.box("frame", (px, ys, pz + 0.08), (0.05, 0.05, 0.02), soft=0.002)
    k.tube("lever", (px, ys, pz + 0.09), (px, ys, 0.82), 0.022, seg=20)
    k.tube("chrome", (px, ys, 0.80), (px, ys, za), 0.015, seg=18)
    k.box("frame", (px, ys, za + 0.005), (0.05, 0.05, 0.02), soft=0.002)
    k.cyl("lever", (px, ys, 0.80), 0.028, 0.03, axis="z", seg=24, soft=0.003)                     # the collar
    k.cyl("lever", (px, ys - 0.032, 0.80), 0.012, 0.012, axis="y", seg=16, soft=0.002)           # its boss
    k.cyl("yellow", (px, ys - 0.048, 0.80), 0.017, 0.022, axis="y", seg=20, soft=0.004)
    # ---- the lever: forward from the hub, level with the legs, to the calf roller; the lower tube sliding in the
    # upper (the roller's reach) with its yellow pop pin
    fw = (-math.cos(DROP), -math.sin(DROP))
    ry, rz_ = py + ARM * fw[0], pz + ARM * fw[1]
    k.bar("lever", (LX, py, pz), (LX, py + 0.26 * fw[0], pz + 0.26 * fw[1]), 0.06, 0.06, up=(1, 0, 0))
    k.bar("steel", (LX, py + 0.18 * fw[0], pz + 0.18 * fw[1]), (LX, ry, rz_), 0.045, 0.045, up=(1, 0, 0), r=0.004)
    pp = (LX, py + 0.23 * fw[0], pz + 0.23 * fw[1])
    k.cyl("lever", (LX - 0.036, pp[1], pp[2]), 0.016, 0.012, axis="x", seg=20, soft=0.002)
    k.cyl("yellow", (LX - 0.053, pp[1], pp[2]), 0.017, 0.022, axis="x", seg=20, soft=0.004)
    for i in range(4):
        q = 0.29 + 0.035 * i
        k.cyl("hole", (LX + 0.0228, py + q * fw[0], pz + q * fw[1]), 0.005, 0.001, axis="x", seg=12, soft=0.0)
    k.tube("steel", (LX - 0.02, ry, rz_), (0.24, ry, rz_), 0.02, seg=20)
    k.tube("pad", (LX + 0.03, ry, rz_), (0.235, ry, rz_), 0.065, seg=36, soft=0.012)
    k.cyl("plastic", (0.24, ry, rz_), 0.066, 0.01, axis="x", seg=36, soft=0.003)

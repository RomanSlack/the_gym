"""Rogue Adjustable Bench 3.0 (AB-3, USA textured foam pad), set at an incline as in Rogue's photo.

Built by eye from Rogue's gallery (refs/: ref_01 the three-quarter, ref_02-05 the textured pad and its cross section),
held to Rogue's spec: base 56.5 in long, rear foot 24.75 in wide, pads 52 in overall with a 1 in gap, 11 in wide,
17.5 in high when flat, 3 x 3 in 11-gauge steel.
Axes: metres, floor z = 0, the bench runs along x: the seat and front leg at -x, the ladder, rear foot and handle at +x.
Structure (ref_01): one spine from the rear foot rising forwards into the front leg, which stands on the front foot
and carries the seat on two side plates; the back pad on its own frame, hinged on two plates on the spine behind the
seat; a pair of straps under it ending in a rod that sits in the notches of the laser-cut ladder plates either side of
the spine; a handle post at the rear.
"""
import math
from pathlib import Path

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.016, 0.016, 0.017), rough=0.45, metal=0.1, coat=0.05, bump=(1400, 0.06)),   # black satin powder coat
    "pad": dict(color=(0.030, 0.030, 0.032), rough=0.8, sheen=0.05, bump=(2600, 0.35)),              # textured grey foam
    "emboss": dict(color=(0.024, 0.024, 0.025), rough=0.55, bump=(2600, 0.1)),
    "plastic": dict(color=(0.012, 0.012, 0.013), rough=0.7),                                         # the pads' boards, matte
    "cap": dict(color=(0.010, 0.010, 0.011), rough=0.22, coat=0.3),                                  # gloss end caps
    "laser": dict(color=(0.62, 0.62, 0.63), rough=0.3, metal=1.0, aniso=0.3),                         # bare laser-cut steel
    "etch": dict(color=(0.05, 0.05, 0.05), rough=0.6),
    "bolt": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-30, 14, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_ladder": ((0.45, -0.75, 0.55), (0.30, 0.0, 0.27), 45),      # the rod in the ladder's notch
    "detail_seat": ((-0.95, -0.6, 0.5), (-0.52, 0.0, 0.3), 45),         # the seat on its plates, the front leg + foot
    "detail_hinge": ((-0.05, -0.7, 0.55), (-0.30, 0.0, 0.33), 45),      # the back pad's hinge on the spine
}

BACK_DEG = 40.0                 # the back pad's incline (Rogue's photo; 0 = flat)
T = 3 * IN                      # 3 x 3 in tube
PAD_T, PAD_W = 0.06, 11 * IN
SEAT = (-0.70, -0.32)           # the seat pad (x from / to)
BACK_L = 0.915                  # the back pad (the 52 in overall, less the seat and the 1 in gap)
H = (-0.30, 0.36)               # the back's hinge (x, z): the back pad's top is level with the seat's when flat
REAR_X, FRONT_X = 0.72, -0.66   # the feet's centres (x): 56.5 in from the rear foot's back face to the front foot's front
REAR_W, FRONT_W = 24.75 * IN, 0.32
LEG_TOP = (-0.50, 0.33)         # the front leg's top (x, z), the seat plates on it
ARM_AT = 0.45                   # the straps hang from the back frame this far up from the hinge
ROD_X = 0.30                    # the notch the rod sits in (x)
CAP_L, CAP_T = 0.024, 0.002


def spine_z(x):
    """The spine's centreline height at x: from the rear foot's top (its bottom face on the foot) up to the front leg."""
    return (0.078 + T / 2) + (REAR_X - x) * SLOPE


SLOPE = 0.1264                  # rise of the spine per metre forwards (it meets the front leg at about z 0.27)


def foot(k, x, w, sec):
    """A foot across y: the tube between gloss end caps, the caps a touch bigger, standing on the floor."""
    a, h = sec
    body = w / 2 - CAP_T
    k.bar("frame", (x, -body, CAP_T + h / 2), (x, body, CAP_T + h / 2), a, h, up=(0, 0, 1))
    for d in (1, -1):
        k.box("cap", (x, d * (w / 2 - CAP_L / 2), CAP_T + h / 2), (a + 2 * CAP_T, CAP_L, h + 2 * CAP_T), soft=0.004)
    return CAP_T + h


def build(k):
    a = math.atan(SLOPE)
    np_ = (math.sin(a), 0.0, math.cos(a))                              # the spine's up
    Y = (0, 1, 0)
    # the feet
    foot(k, REAR_X, REAR_W, (T, T))
    ftop = foot(k, FRONT_X, FRONT_W, (T, 2 * IN))
    # the front leg: welded on the front foot, leaning back to its top under the seat
    lx0, (lx1, lz1) = FRONT_X, LEG_TOP
    k.bar("frame", (lx0, 0, ftop), (lx1, 0, lz1), T, T, up=Y, cut0=((0, 0, ftop), (0, 0, 1)), cut1=((0, 0, lz1), (0, 0, 1)), weld=True)
    ld = (lx1 - lx0, 0, lz1 - ftop); n = math.hypot(ld[0], ld[2]); ld = (ld[0] / n, 0, ld[2] / n)
    rear_face_n = (ld[2], 0, -ld[0])                                   # the leg's face towards the rear
    # the spine: sits on the rear foot (capped past it), runs forwards and up into the leg's rear face, welded
    xs = lx0 + (0.27 - ftop) / ld[2] * ld[0]                           # where the leg's centreline is at z 0.27
    lp = (xs + rear_face_n[0] * T / 2, 0, 0.27 + rear_face_n[2] * T / 2)
    xe = REAR_X + 0.05
    k.bar("frame", (xe, 0, spine_z(xe)), (xs, 0, spine_z(xs)), T, T, up=Y, cut1=(lp, rear_face_n), weld=True)
    k.box("cap", (xe + 0.004, 0, spine_z(xe)), (0.008, T + 0.004, T + 0.004), ry=a, soft=0.003)
    # the seat: two side plates welded to the leg's top, a mount plate across them, the pad bolted on
    sx0, sx1 = SEAT
    for s in (1, -1):
        k.box("frame", (lx1 - 0.01, s * (T / 2 + 0.005), 0.335), (0.20, 0.01, 0.08), soft=0.002)
        k.bolt((lx1 + 0.05, s * (T / 2 + 0.01), 0.32), "+y" if s > 0 else "-y", size=0.014)
    k.box("frame", (lx1 - 0.01, 0, 0.38), (0.22, T + 0.02, 0.01), soft=0.002)
    k.box("laser", (lx1 - 0.06, -(T / 2 + 0.0105), 0.335), (0.045, 0.001, 0.045), soft=0.0)             # the R badge
    k.text("etch", "R", (lx1 - 0.06, -(T / 2 + 0.0112), 0.335), 0.032, depth=0.0006)
    pad(k, ((sx0 + sx1) / 2, 0, 0.385 + PAD_T / 2), (1, 0, 0), (0, 0, 1), sx1 - sx0)
    # the back: hinge plates on the spine, the back frame on a hub between them, the pad on the frame
    A = math.radians(BACK_DEG)
    u = (math.cos(A), 0, math.sin(A)); nrm = (-math.sin(A), 0, math.cos(A))
    hx, hz = H
    ztop = spine_z(hx) + T / 2 / math.cos(a)
    for s in (1, -1):
        k.box("frame", (hx, s * (T / 2 + 0.005), (ztop - 0.01 + hz + 0.04) / 2), (0.09, 0.01, hz + 0.05 - ztop), soft=0.002)
    k.tube("frame", (hx, -T / 2, hz), (hx, T / 2, hz), 0.026, seg=28)
    k.tube("steel", (hx, -(T / 2 + 0.016), hz), (hx, T / 2 + 0.016, hz), 0.01)
    for s in (1, -1):
        k.bolt((hx, s * (T / 2 + 0.01), hz), "+y" if s > 0 else "-y", size=0.018)
    fh = 2 * IN                                                       # the back frame: 2 x 3 in under the pad
    f0 = (hx + u[0] * 0.01, 0, hz + u[2] * 0.01)
    f1 = (hx + u[0] * 0.80, 0, hz + u[2] * 0.80)
    k.bar("frame", f0, f1, fh, T, up=Y)
    k.box("cap", (f1[0] + u[0] * 0.004, 0, f1[2] + u[2] * 0.004), (0.008, T + 0.004, fh + 0.004), ry=-A, soft=0.003)
    pc = tuple((hx, 0.0, hz)[i] + u[i] * (0.012 + BACK_L / 2) + nrm[i] * (fh / 2 + PAD_T / 2) for i in range(3))
    pad(k, pc, u, nrm, BACK_L)
    top = tuple((hx, 0.0, hz)[i] + u[i] * (0.012 + BACK_L - 0.07) + nrm[i] * (fh / 2 + PAD_T - 0.0002) for i in range(3))
    k.text("emboss", "ROGUE", top, 0.04, rz=-math.pi / 2, rx=A, depth=0.0016)
    # the straps: a hub under the back frame, two flat straps down to the rod in the ladder's notch
    q = tuple((hx, 0.0, hz)[i] + u[i] * ARM_AT - nrm[i] * (fh / 2 + 0.024) for i in range(3))
    k.tube("frame", (q[0], -0.064, q[2]), (q[0], 0.064, q[2]), 0.024, seg=24)
    k.box("frame", tuple((hx, 0.0, hz)[i] + u[i] * ARM_AT - nrm[i] * (fh / 2 + 0.006) for i in range(3)), (0.05, 0.05, 0.012), ry=-A, soft=0.002)
    lt = 0.073                                                        # the ladder's top edge above the spine's centre
    r = (ROD_X + np_[0] * (lt + 0.0205), 0, spine_z(ROD_X) + np_[2] * (lt + 0.0205))
    for s in (1, -1):
        k.bar("frame", (q[0], s * 0.055, q[2]), (r[0], s * 0.055, r[2]), 0.04, 0.008, up=Y)
    k.tube("frame", (r[0], -0.064, r[2]), (r[0], 0.064, r[2]), 0.0205, seg=24)
    for s in (1, -1):
        k.cyl("cap", (r[0], s * 0.067, r[2]), 0.024, 0.006, axis="y", seg=24)
    # the ladder: a laser-cut plate bolted each side of the spine, teeth along its top edge, the angles etched
    xm, L = 0.28, 0.52
    for s in (1, -1):
        yp = s * (T / 2 + 0.003)
        c = (xm + np_[0] * 0.0215, yp, spine_z(xm) + np_[2] * 0.0215)
        k.box("laser", c, (L, 0.006, 0.103), ry=a, soft=0.001)
        for bx in (xm - 0.2, xm + 0.2):
            k.bolt((bx, s * (T / 2 + 0.006), spine_z(bx)), "+y" if s > 0 else "-y", size=0.012)
        i = 0
        for tx in [xm - L / 2 + 0.025 + j * 0.068 for j in range(8)]:
            if abs(tx - ROD_X) < 0.03:
                continue
            tc = (tx + np_[0] * (lt + 0.012), yp, spine_z(tx) + np_[2] * (lt + 0.012))
            k.box("laser", tc, (0.032, 0.006, 0.024), ry=a, soft=0.002)
            if s < 0:
                deg = ("85", "75", "60", "45", "30", "15", "0", "")[i] if i < 8 else ""
                if deg:
                    k.text("etch", deg, (tx, yp - 0.0032, spine_z(tx) + np_[2] * 0.05), 0.018, depth=0.0006)
            i += 1
    # the handle post at the rear: welded on the spine's top, a round cap, a handle across it
    px = REAR_X - 0.06
    pz0 = spine_z(px) + T / 2 / math.cos(a)
    k.bar("frame", (px, 0, pz0 - 0.01), (px, 0, 0.42), 2 * IN, 2 * IN, up=Y,
          cut0=((px, 0, spine_z(px) + T / 2 / math.cos(a)), np_), weld=True)
    k.cyl("cap", (px, 0, 0.427), 0.034, 0.014, seg=32, soft=0.004)
    k.tube("frame", (px, -0.17, 0.37), (px, 0.17, 0.37), 0.014)
    for s in (1, -1):
        k.tube("cap", (px, s * 0.08, 0.37), (px, s * 0.175, 0.37), 0.019, seg=24)


def pad(k, c, along, up, L):
    """A moulded textured foam pad on its plywood board (ref_03): no stitching, rounded edges."""
    side = (along[1] * up[2] - along[2] * up[1], along[2] * up[0] - along[0] * up[2], along[0] * up[1] - along[1] * up[0])
    k.shaped_pad("pad", [(-PAD_W / 2, -L / 2), (PAD_W / 2, -L / 2), (PAD_W / 2, L / 2), (-PAD_W / 2, L / 2)],
                 c, up, side, PAD_T, r=0.012, seam=False)

"""Life Fitness Insignia Series Leg Extension, Charcoal frame / Black upholstery, the lever at its start.

Built by eye from refs/: ref_01 the maker's studio three-quarter in the picked colourway, and a used unit (silver frame)
photographed all round at Fitness Equipment Empire (ref_02 / ref_05 / ref_10 from the open side, ref_10 nearly square
on to the tower's face; ref_03 / ref_04 the lever end; ref_06 the placard; ref_07 the stack's numbers; ref_08 the back;
ref_09 from behind the back pad, the tower in profile), held to Life Fitness's height of 58.1 in (148 cm). Their
65.4 x 41.5 in footprint is the width (105 cm) we hold to; the photos read the length nearer 1.35 m with the roller
at its start.
Axes: metres, floor z = 0, the user sits facing -y, x+ = the user's left; the tower on the user's right (-x), its
face turned across the seat (+x); the lever and its cam at the seat's front on the tower side, the shin roller
reaching across to the open side.
Structure: the closed stack tower (shared builder, "shroud" style); the base: the lever's post and foot at the front,
a low beam from it back beside the tower's face to the rear cross beam, the rear post on the open side; the seat on a
spine from the curved front leg to a rear leg slanting down to the rear beam; the back pad on a carriage hung from the rear post on two parallel
links (it swings fore and aft), the lock plate of holes and its pull knob (ref_01 / ref_10); handles each side of the
seat; the lever: the housing on its post, the cam inside it with the guard outside, the hub, the start-position
handle and its pin in a ring of holes, the arm down with its telescoping lower tube and pop pin, the shin roller; the
cable from the cam to a pulley at the tower's foot and into the tower.
"""
import math

import stack_tower

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.05, 0.052, 0.056), rough=0.38, metal=0.45, coat=0.15, bump=(1400, 0.05)),  # Charcoal: a
                                     # metallic grey, a shade lighter than the black panels (ref_01's tower edges)
    "lever": dict(color=(0.02, 0.02, 0.021), rough=0.42, metal=0.3, coat=0.1, bump=(1400, 0.06)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "seam": dict(color=(0.30, 0.30, 0.30), rough=0.7, coat=0.0),                                        # the grey stitching
    "plate": dict(color=(0.04, 0.04, 0.042), rough=0.45, metal=0.3, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "cam": dict(color=(0.05, 0.05, 0.052), rough=0.35, metal=0.4, coat=0.1),
    "shroud": dict(color=(0.012, 0.012, 0.013), rough=0.22, coat=0.7),                                 # the gloss cap and pan
    "shroud2": dict(color=(0.03, 0.033, 0.04), rough=0.38, metal=0.15, coat=0.25),                     # the satin slate panels
    "cable": dict(color=(0.03, 0.03, 0.03), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "yellow": dict(color=(0.95, 0.55, 0.02), rough=0.4, coat=0.1),                                      # the pop-pin knobs
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
}
VIEWS = {"three_quarter": (48, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (-125, 16, 1.0)}
DETAILS = {
    "detail_lever": ((0.75, -1.05, 0.95), (-0.25, -0.30, 0.45), 45),   # the cam, its guard, the handle, the roller
    "detail_back": ((0.95, 1.05, 0.95), (0.15, 0.55, 0.50), 45),       # the back pad's links, the lock plate
    "detail_tower": ((0.75, -0.25, 1.45), (-0.42, 0.42, 1.05), 40),    # the tower's face: panels, channel, placards, cap
}

TOWER = dict(style="insignia", W=0.74, D=0.30, H=58.1 * IN, n=20, plate=(0.34, 0.14, 0.0254), rods=0.24,
             title="LEG EXTENSION", brand="LifeFitness", step=15, start=-5)   # half as wide as tall (the glute's ref_04,
                                     # square on to the face: 0.72 m against its 73 in length; the close-up back photos
                                     # read wider)
TC = (-0.56, 0.42)                   # the tower: beside the user on the right, its face (+x) across the seat (ref_10)
X_FACE = TC[0] + TOWER["D"] / 2      # its face (x)
FOOT_H = 0.015
T = 0.076
SPINE_Z = 0.41                       # the seat's spine (centre)
SEAT = (0.0, -0.26, 0.22)            # the seat pad (x, front y, back y), its top at 0.56
PIV = (-0.32, -0.31, 0.62)           # the lever's axle (x of the housing, y, z): at the knee, just ahead of the seat
LX = -0.245                          # the lever's plane (just outside the right knee)
DROP = math.radians(30)              # the lever at its start: the roller well ahead of the seat (ref_01 / ref_10)
ARM = 0.40                           # knee to the roller's axis (the ankle)
Y_REAR = 0.50                        # the rear cross beam and the rear post
X_REAR = 0.20
LEAN = math.radians(32)              # the back pad's recline (ref_10)


def foot(k, x, y, s=0.10):
    k.box("rubber", (x, y, FOOT_H / 2), (s, s, FOOT_H), soft=0.003)


Z, X, Y = (0, 0, 1), (1, 0, 0), (0, 1, 0)
RZ0 = FOOT_H + 0.05 / 2              # the base beams' centre height


def build(k):
    tw = stack_tower.tower(k, TOWER, TC, 90.0)
    px, py, pz = PIV
    # ---- the lever's post on its foot (the base's low beam starts from it)
    foot(k, px, py, 0.12)
    k.bar("frame", (px, py, FOOT_H), (px, py, pz - 0.07), T, T, cut0=((0, 0, FOOT_H), Z), weld=True)
    base(k, py)
    # the curved front leg up into the seat's spine (ref_10)
    foot(k, 0.12, -0.30, 0.11)
    k.sweep("frame", [(0.12, -0.30, FOOT_H), (0.12, -0.30, 0.22), (0.05, -0.26, SPINE_Z - 0.03), (0.0, SEAT[1] + 0.08, SPINE_Z)],
            k.circle(0.036, 24), bend=0.14, cut0=((0, 0, FOOT_H), Z), soft=0.002)
    seat(k)
    back(k)
    cam(k, tw)
    lever(k)


def base(k, y0, on_tower=True):
    """The low beam from the front (y0, beside the lever's post) back beside the tower's face, the rear cross beam from
    the tower's face to the open side, the rear post."""
    px = PIV[0]
    rz0 = RZ0
    k.bar("frame", (px, y0 + T / 2, rz0), (px, Y_REAR - T / 2, rz0), T, 0.05,
          cut0=((0, y0 + T / 2, 0), Y), cut1=((0, Y_REAR - T / 2, 0), Y), weld=True)
    k.bar("frame", (X_FACE, Y_REAR, rz0), (X_REAR + T / 2, Y_REAR, rz0), T, 0.05,
          cut0=((X_FACE, 0, 0), X), weld=True)
    if on_tower:                                       # (a piece whose tower stands further forward leaves it off)
        k.box("frame", (X_FACE + 0.004, Y_REAR, rz0 + 0.02), (0.008, 0.12, 0.11), soft=0.001)    # its plate on the tower
    foot(k, X_REAR, Y_REAR + 0.02, 0.12)
    post_top = 0.50
    k.bar("frame", (X_REAR, Y_REAR, FOOT_H), (X_REAR, Y_REAR, post_top), T, T, cut0=((0, 0, FOOT_H), Z), weld=True)
    k.box("plastic", (X_REAR, Y_REAR, post_top + 0.004), (T + 0.004, T + 0.004, 0.008), soft=0.002)


def seat(k, dz=0.0, front=None):
    """The seat: the spine from its front leg (the piece's own) back to the rear leg slanting down to the rear beam,
    the board, the pad; the handles each side. dz lowers or raises it, front moves its front edge (y)."""
    rz0 = RZ0
    sx, sy0, sy1 = SEAT
    sy0 = sy0 if front is None else front
    SPINE_Z = globals()["SPINE_Z"] + dz
    fy = sy0 + 0.04
    ye = sy1 + 0.06
    k.bar("frame", (0, fy, SPINE_Z), (0, ye, SPINE_Z), T, T)
    k.bar("frame", (0, ye - 0.03, SPINE_Z - 0.02), (0, Y_REAR - T / 2, rz0), 0.06, 0.06,
          cut1=((0, Y_REAR - T / 2, 0), Y), weld=True)                                    # the rear leg down to the beam
    k.box("frame", (0, (sy0 + sy1) / 2, SPINE_Z + T / 2 + 0.01), (0.30, sy1 - sy0 - 0.04, 0.02), soft=0.003)
    k.pad("pad", (0, (sy0 + sy1) / 2, SPINE_Z + T / 2 + 0.02 + 0.045), (0.38, sy1 - sy0, 0.09), r=0.04)
    # the handles each side of the seat: from under the board out, along the seat's side, the grip's end down and back
    for s in (1, -1):
        g0 = (s * 0.12, sy1 - 0.08, SPINE_Z + T / 2)
        g1 = (s * 0.24, sy1 - 0.02, SPINE_Z + 0.02)
        g2 = (s * 0.25, sy1 + 0.16, SPINE_Z - 0.06)
        k.sweep("frame", [g0, g1, g2], k.circle(0.016, 18), bend=0.05, soft=0.0015)
        k.tube("rubber", (s * 0.245, sy1 + 0.05, SPINE_Z - 0.01), g2, 0.021, seg=22)
        k.cyl("plastic", g2, 0.023, 0.012, axis="y", seg=20, soft=0.003)


def back(k, lean=LEAN, dz=0.0, tall=0.0, outline=None):
    """The back pad's carriage: two parallel links from the rear post's inner face up and forward to the carriage
    plate (the pad swings fore and aft on them), the lock plate of holes on the post, the pull knob (ref_01 / ref_10).
    dz moves it with the seat, tall makes the pad taller, outline (across, up from its centre) shapes it."""
    # ---- the back pad's carriage: two parallel links from the rear post's inner face up and forward to the carriage
    # plate (the pad swings fore and aft on them), the lock plate of holes on the post, the pull knob (ref_01 / ref_10)
    lk = math.radians(35)
    L = 0.20
    xl = X_REAR - T / 2 - 0.012
    lows = [(Y_REAR, 0.29 + dz), (Y_REAR, 0.41 + dz)]
    ups = [(y - L * math.cos(lk), z + L * math.sin(lk)) for y, z in lows]
    for (y0, z0), (y1, z1) in zip(lows, ups):
        k.bar("frame", (xl, y0, z0), (xl, y1, z1), 0.012, 0.05, up=(1, 0, 0))
        for y_, z_ in ((y0, z0), (y1, z1)):
            k.tube("steel", (xl - 0.012, y_, z_), (X_REAR - T / 2 + 0.001, y_, z_), 0.011, seg=16)
            k.bolt((xl - 0.008, y_, z_), "-x", size=0.018)
    cy_ = ups[0][0]
    k.box("frame", (xl - 0.018, cy_, (ups[0][1] + ups[1][1]) / 2), (0.012, 0.09, ups[1][1] - ups[0][1] + 0.08), soft=0.002)
    for y_, z_ in ups:
        k.tube("steel", (xl - 0.024, y_, z_), (xl - 0.006, y_, z_), 0.011, seg=16)
    # the lock: a plate of holes on the post's inner face, the pin through the lower link, its yellow knob outside
    for i in range(5):
        a = math.radians(15 + 10 * i)
        k.cyl("hole", (X_REAR - T / 2 - 0.0005, lows[0][0] - 0.12 * math.cos(a), lows[0][1] + 0.12 * math.sin(a)),
              0.006, 0.001, axis="x", seg=12, soft=0.0)
    k.box("frame", (X_REAR - T / 2 - 0.003, Y_REAR - 0.07, 0.35 + dz), (0.006, 0.14, 0.16), soft=0.001)
    kp = (X_REAR + T / 2, Y_REAR - 0.03, 0.35 + dz)
    k.tube("steel", (X_REAR - T / 2 - 0.006, kp[1], kp[2]), (kp[0] + 0.03, kp[1], kp[2]), 0.006, seg=12)
    k.cyl("frame", (kp[0] + 0.006, kp[1], kp[2]), 0.017, 0.012, axis="x", seg=20, soft=0.002)        # its boss
    k.cyl("yellow", (kp[0] + 0.024, kp[1], kp[2]), 0.018, 0.024, axis="x", seg=20, soft=0.004)
    # the carriage's cross bar from the plate in under the back pad, the stem up behind it, the pad
    zc = ups[1][1]
    xs = xl - 0.024
    k.bar("frame", (xs, cy_, zc), (-0.04, cy_, zc), 0.05, 0.05, cut0=((xs, 0, 0), X), weld=True)
    up = (0.0, math.sin(lean), math.cos(lean))
    nrm = (0.0, -math.cos(lean), math.sin(lean))
    base = (0.0, cy_, zc)
    top = tuple(base[i] + up[i] * (0.66 + tall) for i in range(3))
    k.bar("frame", (0.0, cy_, zc - 0.025), top, 0.06, 0.04, up=(0, 1, 0))
    pc = tuple(base[i] + up[i] * (0.36 + tall / 2) + nrm[i] * 0.075 for i in range(3))
    k.shaped_pad("pad", outline or [(-0.20, -0.32 - tall / 2), (0.20, -0.32 - tall / 2), (0.20, 0.30 + tall / 2), (-0.20, 0.30 + tall / 2)], pc, nrm, (1, 0, 0), 0.09,
                 r=0.05, cushion=0.03)
    k.box("frame", tuple(base[i] + up[i] * (0.36 + tall / 2) + nrm[i] * 0.024 for i in range(3)), (0.30, 0.016, 0.56 + tall), rx=-lean, soft=0.002)


def cam(k, tw):
    """The lever's housing (on the piece's own post), the axle, the cam with its guard, the cable into the tower; the
    lever's hub, the ring of start-position holes and the handle."""
    px, py, pz = PIV
    # ---- the lever's housing on its post, the axle, the cam inside it (between the housing and the tower) with its
    # guard outside; a yellow warning tag
    k.box("frame", (px, py, pz), (0.10, 0.14, 0.14), soft=0.008)
    k.tube("steel", (LX - 0.03, py, pz), (px - 0.12, py, pz), 0.022, seg=20)
    cx_ = px - 0.075
    k.cyl("cam", (cx_, py, pz), 0.14, 0.03, axis="x", seg=48, soft=0.003)
    k.disc("steel", (cx_, py, pz), 0.142, 0.12, 0.026, axis="x", seg=48)
    k.bolt((px - 0.12, py, pz), "-x", size=0.026)
    gx = px - 0.075 - 0.035
    k.cyl("plastic", (gx, py + 0.03, pz - 0.03), 0.18, 0.012, axis="x", seg=48, soft=0.004)          # the cam's guard
    k.bar("frame", (gx + 0.006, py + 0.03, pz - 0.15), (px - 0.05, py + 0.03, pz - 0.15), 0.03, 0.03)
    k.box("yellow", (px + 0.051, py - 0.03, pz - 0.03), (0.002, 0.04, 0.05), soft=0.0)
    # the cable: off the cam's bottom, back and down to the pulley at the tower's foot, in through its face (inside,
    # up to the stack's top pulley, hidden by the shroud)
    yq = TC[1] - TOWER["W"] / 2 + 0.10
    k.box("frame", (X_FACE + 0.03, yq, 0.12), (0.06, 0.06, 0.12), soft=0.004)
    k.pulley((X_FACE + 0.035, yq, 0.12), 0.04, axis="x")
    k.cable([(cx_, py + 0.02, pz - 0.14), (cx_ + 0.01, py + 0.14, 0.30), (X_FACE + 0.035, yq - 0.04, 0.13)])
    ox, oy, oz = tw["cable"]
    out = (TC[0] - (oy - TC[1]), TC[1] + (ox - TC[0]), oz)
    k.cable([(X_FACE - 0.02, yq, 0.12), (out[0] - 0.02, yq, 0.12), (out[0] - 0.02, out[1], oz - 0.06), out])
    # ---- the lever's hub on the axle inside the housing, the ring of start-position holes, the handle with its pin
    # knob and the black ball on top (ref_04 / ref_10)
    k.tube("lever", (LX - 0.03, py, pz), (px + 0.05, py, pz), 0.05, seg=32)
    k.disc("cam", (LX + 0.034, py, pz), 0.10, 0.05, 0.012, axis="x", seg=40)
    for i in range(8):
        a = math.radians(200 + 18 * i)
        k.cyl("hole", (LX + 0.0405, py + 0.08 * math.cos(a), pz + 0.08 * math.sin(a)), 0.006, 0.001, axis="x", seg=12, soft=0.0)
    hd = (math.sin(math.radians(-20)), math.cos(math.radians(-20)))               # the handle: up, leaning forward
    h1 = (LX, py + 0.26 * hd[0], pz + 0.26 * hd[1])
    k.bar("lever", (LX, py, pz), h1, 0.05, 0.05, up=(1, 0, 0))
    k.cyl("plastic", (LX, h1[1] + 0.03 * hd[0], h1[2] + 0.03 * hd[1]), 0.045, 0.06, axis="x", seg=32, soft=0.01)
    k.tube("chrome", (LX + 0.025, py - 0.10, pz + 0.12), (LX + 0.025, py - 0.15, pz + 0.30), 0.009, seg=14)  # the pin's pull
    k.tube("rubber", (LX + 0.025, py - 0.14, pz + 0.27), (LX + 0.025, py - 0.165, pz + 0.35), 0.016, seg=18)
    k.tube("steel", (LX + 0.025, py - 0.07, pz + 0.07), (LX + 0.025, py - 0.10, pz + 0.12), 0.006, seg=12)


def lever(k):
    """The arm down to the roller: the upper square tube, the lower tube sliding in it (the roller's length) with its
    yellow pop pin; the shin roller."""
    px, py, pz = PIV
    dn = (-math.sin(DROP), -math.cos(DROP))                                       # the arm: down, the foot forward
    ry, rz_ = py + ARM * dn[0], pz + ARM * dn[1]
    a1 = (LX, py + 0.22 * dn[0], pz + 0.22 * dn[1])
    k.bar("lever", (LX, py, pz), a1, 0.06, 0.06, up=(1, 0, 0))
    k.bar("steel", (LX, py + 0.15 * dn[0], pz + 0.15 * dn[1]), (LX, ry, rz_), 0.045, 0.045, up=(1, 0, 0), r=0.004)
    pp = (LX, py + 0.20 * dn[0], pz + 0.20 * dn[1])
    k.cyl("lever", (LX - 0.036, pp[1], pp[2]), 0.016, 0.012, axis="x", seg=20, soft=0.002)         # its boss
    k.cyl("yellow", (LX - 0.053, pp[1], pp[2]), 0.017, 0.022, axis="x", seg=20, soft=0.004)
    for i in range(4):
        q = 0.25 + 0.035 * i
        k.cyl("hole", (LX + 0.0228, py + q * dn[0], pz + q * dn[1]), 0.005, 0.001, axis="x", seg=12, soft=0.0)
    k.tube("steel", (LX - 0.02, ry, rz_), (0.24, ry, rz_), 0.02, seg=20)
    k.tube("pad", (LX + 0.03, ry, rz_), (0.235, ry, rz_), 0.065, seg=36, soft=0.012)
    k.cyl("plastic", (0.24, ry, rz_), 0.066, 0.01, axis="x", seg=36, soft=0.003)

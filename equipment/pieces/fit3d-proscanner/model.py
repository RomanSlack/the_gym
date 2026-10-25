"""Fit3D ProScanner, black (refs/: ref_01 a product render from the user's front, a little high (ShapeScale's review
page), ref_02 a photo of one in use at Bournemouth University's ORI (from the front: the tablet on the tower), ref_03 the
newer white unit with a user on it (the stance, the hands on the handles' tops). Fit3D's own pages carry no photo of the
hardware any more. Fetched 2026-10-25, one request per page, 6-7 s apart. Claude's pick. Built to the two gates and
README point 9.

DESIGN SPEC (gate 1)
1. Use. The user steps onto the turntable, stands on the two footprints facing away from the tower, arms a little out
   from the sides, a hand on each handle; the turntable turns them once round (about 40 s) while the tower's three
   depth sensors look at them; the integrated scale weighs them. They step off; the operator reads the tablet.
2. Moving parts, each mass named (ref_01 / ref_02):
   - The base: a round fixed disc on the floor (0.97 m across), the motor and the 4-point scale inside, not drawn.
   - The turntable: a slightly smaller platter on the base, its edge a dark seam above the base's; on it a grey mat with
     two light footprints, the toes away from the tower.
   - The handles: two upright poles fixed to the platter's rim at the user's sides (they turn with the user), a silver
     knob on each top; the user holds them anywhere along their upper part.
   - The tongue: a tapered floor plate from the base to the tower's foot (the FIT3D mark on it), fixing the tower's
     distance and keeping both square to each other.
   - The tower: a tall narrow black column, orange bands at its top and foot, a dark glass strip down its face over the
     three depth sensors (at the knees, the waist, the head), the operator's tablet on a bracket on its face (ref_02).
3. Adjustments. None on the hardware: the user stands on the footprints and holds the poles wherever their hands fall.
4. Load path. The user's weight on the platter, its bearing, the base's load cells, the floor. The tower stands on the
   tongue's end; the tongue keeps it 0.55 m from the turntable's edge.
5. Fit range. 1.55 / 1.78 / 1.95 m standing on the footprints (the ankles over the turntable's centre), arms straight
   and out to the side to the poles: the hands meet the poles 0.73 / 0.81 / 0.88 m up, all under the knobs (0.92), so
   the tallest user still reaches without shrugging (v001: the poles 0.84 tall above the platter).
6. Size. Fit3D: 97 x 166 cm footprint (the turntable's edge to the tower's back), 182 cm tall (71.5 in), the turntable
   3 in high. Ours 0.97 x 1.64 x 1.82: the tongue read off ref_02's perspective (0.55 m, edge to tower).
Axes: metres, floor z = 0, the user faces -y (toward the camera at azimuth 0), x+ = the user's left; the turntable's
centre at x = y = 0, the tower at +y.
"""
import math

LOOK = {
    "frame": dict(color=(0.018, 0.018, 0.019), rough=0.4, metal=0.2, coat=0.2),
    "plastic": dict(color=(0.025, 0.025, 0.027), rough=0.45, coat=0.1),
    "mat": dict(color=(0.06, 0.06, 0.062), rough=0.9, coat=0.0, spec=0.2),
    "print": dict(color=(0.45, 0.45, 0.46), rough=0.8, coat=0.0),
    "orange": dict(color=(0.85, 0.32, 0.06), rough=0.4, coat=0.1),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, coat=0.0),
    "glass": dict(color=(0.01, 0.01, 0.012), rough=0.08, coat=0.6),
    "screen": dict(color=(0.30, 0.34, 0.36), rough=0.3, coat=0.3),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "case": dict(color=(0.62, 0.62, 0.63), rough=0.35, coat=0.2),                                    # the tablet's
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (0, 15, 1.1),        # ref_01 / ref_02: from the user's front, a little high
         "user_three_quarter": (-35, 8, 1.1)}   # ref_03
DETAILS = {
    "detail_turntable": ((0.0, -1.10, 0.75), (0.0, 0.0, 0.10), 40),       # the platter, the mat, the poles' feet
    "detail_tower": ((-0.70, -0.30, 1.50), (0.0, 1.10, 1.20), 40),        # the tower's face, the tablet, the strip
}
SETTINGS = ("scan_short", "scan_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")

R_BASE, Z_BASE = 0.485, 0.028        # the base: its radius (97 cm across) and top
R_PLAT, Z_PLAT = 0.478, (0.036, 0.076)   # the turntable: its radius, its underside and top (3 in)
X_POLE, Z_POLE = 0.43, 0.92          # the handles: their x, their knobs' tops
GAP = 0.55                           # the turntable's edge to the tower's face (ref_02)
TOWER = (0.13, 0.12, 1.82)           # its width, depth, height
Y_TOWER = R_BASE + GAP + TOWER[1] / 2
Z_TONGUE = 0.022                     # the tongue's top
Z_TABLET = 1.32                      # the tablet's centre (ref_02)
Z_SENSORS = (0.50, 1.00, 1.62)       # the three depth sensors behind the strip
SHOW = ("middle",)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))


def setting(name):
    global SHOW
    SHOW = ({"scan_short": "short", "scan_tall": "tall"}[name],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    turntable(k)
    handles(k)
    tower(k)


def turntable(k):
    """The fixed base on the floor, the platter on its bearing, the mat and the footprints, the tongue to the tower."""
    k.cyl("frame", (0, 0, Z_BASE / 2), R_BASE, Z_BASE, seg=128, soft=0.004)
    k.cyl("plastic", (0, 0, (Z_BASE + Z_PLAT[0]) / 2), 0.30, Z_PLAT[0] - Z_BASE + 0.002, seg=64)       # its bearing ring
    z0, z1 = Z_PLAT
    k.cyl("frame", (0, 0, (z0 + z1) / 2), R_PLAT, z1 - z0, seg=128, soft=0.005)
    k.box("mat", (0, -0.02, z1 + 0.0015), (0.52, 0.36, 0.003), soft=0.001)                           # the mat (ref_02)
    for s in (1, -1):                                   # the footprints: heel toward the tower, toes to -y
        x = s * 0.115
        k.cyl("print", (x, 0.045, z1 + 0.0035), 0.034, 0.001, seg=32, soft=0.0)                         # the heel
        k.box("print", (x, -0.005, z1 + 0.0035), (0.056, 0.10, 0.001), soft=0.0)                       # the arch
        k.cyl("print", (x, -0.07, z1 + 0.0035), 0.046, 0.001, seg=32, soft=0.0)                        # the ball
    # the tongue: narrow at the tower, wide where it runs under the base's edge
    y0, y1 = R_BASE - 0.06, Y_TOWER + TOWER[1] / 2 + 0.03

    def corner(sx, sy, sz):
        far = sy > 0
        return (sx * (0.12 if far else 0.26), y1 if far else y0, Z_TONGUE if sz > 0 else 0.0)
    k.block("frame", corner, soft=0.004)
    k.text("label", "FIT3D", (0, R_BASE + 0.16, Z_TONGUE + 0.0003), 0.07, rx=0.0, depth=0.0006)


def handles(k):
    """A pole each side on the platter's rim, a foot block, a silver knob on top."""
    z1 = Z_PLAT[1]
    for s in (1, -1):
        x = s * X_POLE
        k.box("plastic", (x, 0, z1 + 0.015), (0.06, 0.06, 0.03), soft=0.006)                            # its foot
        k.cyl("frame", (x, 0, (z1 + 0.03 + Z_POLE - 0.025) / 2), 0.017, Z_POLE - 0.025 - z1 - 0.03, seg=24, r2=0.013)
        k.cyl("steel", (x, 0, Z_POLE - 0.0125), 0.016, 0.025, seg=24, soft=0.006)                        # the knob


def tower(k):
    """The column on the tongue's end: orange bands, the glass strip over the sensors, the tablet on its bracket."""
    w, d, h = TOWER
    y = Y_TOWER
    yf = y - d / 2                                      # its face, toward the turntable
    k.box("frame", (0, y, (Z_TONGUE + h - 0.02) / 2), (w, d, h - 0.02 - Z_TONGUE), soft=0.006)
    k.box("orange", (0, y, h - 0.01), (w - 0.004, d - 0.004, 0.02), soft=0.005)                      # the top band
    k.box("orange", (0, y, Z_TONGUE + 0.06), (w + 0.004, d + 0.004, 0.012), soft=0.002)             # the foot band
    k.box("glass", (0, yf - 0.001, 1.05), (0.036, 0.004, 1.40), soft=0.0015)                        # the strip
    for z in Z_SENSORS:                                 # the depth sensors behind it
        k.box("steel", (0, yf - 0.0035, z), (0.026, 0.002, 0.05), soft=0.0005)
    k.text("label", "FIT3D", (0, yf - 0.0003, 0.20), 0.035, depth=0.0006, spin=math.pi / 2)
    # the tablet (ref_02): a bracket off the face, the tablet tilted down 8 deg
    t = math.radians(8)
    k.box("plastic", (0, yf - 0.03, Z_TABLET), (0.05, 0.06, 0.08), soft=0.004)
    c = (0, yf - 0.07, Z_TABLET)
    k.box("case", c, (0.25, 0.02, 0.17), rx=-t, soft=0.006)                                   # light (ref_02)
    k.box("screen", (0, c[1] - 0.0105 * math.cos(t), c[2] - 0.0105 * math.sin(t)), (0.22, 0.002, 0.14), rx=-t, soft=0.0)


# ---- the fit check (spec 5)
def pose(H):
    """Arms straight and out to the side to the poles: (the raise from the side, deg; the hands' height)."""
    L = 0.186 * H + 0.146 * H + 0.05 * H               # the shoulder to the middle of the palm
    a = math.asin((X_POLE - 0.13 * H * 0.85) / L)
    return math.degrees(a), 0.818 * H - L * math.cos(a)


def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        a, zh = pose(H)
        print(f"fit {label}: the arms {a:.0f} deg out from the sides, the hands {zh:.2f} m up (the knobs {Z_POLE:.2f})",
              flush=True)
        ball = -0.48 * 0.152 * H                        # the ankles over the turntable's centre
        out[label] = dict(H=H, ball=(0.0, ball, Z_PLAT[1] + 0.004), face=(0, -1), stance=0.23, arm=180, forearm=180,
                          arm_lat=a, fore_lat=a)
    return out

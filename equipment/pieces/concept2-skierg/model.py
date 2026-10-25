"""Concept2 SkiErg on its floor stand, black (refs/: ref_11 the true side view on the floor stand (the geometry is read off
it: 416 px per m from the 216 cm height), ref_12 the stand's three-quarter, ref_02 / ref_03 the SkiErg alone (the V
from the front), ref_04 / ref_05 the stand alone, ref_06 / ref_07 the flywheel, ref_08 / ref_09 the handle's holder
and the PM5, ref_10 in use on the wide stand). Fetched from Concept2's product page (one cached request, the images 5-10 s
apart, 2026-10-25). Claude's pick. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Standing on the stand's board facing -y (the machine), a handle in each hand: from the arms long overhead
   (the start) the hips hinge and the arms pull the handles down past the hips, the knees soften; the cords pay out
   from the pulleys at the top and wind back on the recovery. The shoulders, the trunk and the hips do the work.
2. Moving parts, each mass named (ref_11 / ref_03 / ref_06):
   - The column: a black box beam, its user-side face upright, 0.21 deep below the joint at 1.09 m, opening above it
     into a V of two arms to the top bar (0.52 wide); a pulley in a housing at each end of the top bar.
   - The flywheel at the column's foot on its user side: a fan in a round housing (0.48 across), the C2 badge, the
     damper lever on its rim (resistance).
   - The cords: from each handle up to its pulley at the top, over it, along inside the arm and the column down to
     the flywheel's drive (a bungee winds them back), not drawn inside.
   - The handles: yellow T handles; at rest each hangs in its holder on the column's side (ref_08).
   - The PM5 monitor on its arm off the column's front at about chest height.
   - The floor stand: a board (black tread, a plywood edge), the column's foot bolted to its front end, a U of tube
     whose bar clamps the column's back at 0.83 m and whose legs run down to the board's back end either side of where
     the user stands; two wheels on the front end.
3. Adjustments. The damper lever (1-10) on the flywheel housing; the PM5's tilt. No body adjustment: the user stands
   where their reach puts them.
4. Load path. The hands, the handles, the cords, the pulleys, the flywheel's drive. The machine's pull on the stand:
   the column's foot bolted to the board, its back held by the U's bar, the legs to the board under the user's feet
   (the user's weight holds it down).
5. Fit range. 1.55 / 1.78 / 1.95 m at the start of the stroke: standing upright, the arms long and forward of the
   head, the hands 12 cm over the head (no higher than 0.15 below the pulleys), each user standing where that puts
   the hands over the column's front face. The default build has the handles in their holders; start_short /
   start_middle / start_tall show each user with the handles in its hands.
6. Size. Concept2: 61 x 132 x 216 cm (W x L x H) on the floor stand; the SkiErg 52 cm wide at the top, 48 at the
   bottom, 41 deep. Ours to those.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; y = 0 at the column's front face.
"""
import math

LOOK = {
    "frame": dict(color=(0.018, 0.018, 0.019), rough=0.45, metal=0.3, coat=0.15),
    "shroud": dict(color=(0.02, 0.02, 0.021), rough=0.45, coat=0.15),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "yellow": dict(color=(0.55, 0.75, 0.02), rough=0.45, coat=0.1),                                  # Concept2's lime
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "cord": dict(color=(0.8, 0.8, 0.78), rough=0.6, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "tread": dict(color=(0.03, 0.03, 0.03), rough=0.9, coat=0.0, spec=0.2),
    "ply": dict(color=(0.55, 0.38, 0.22), rough=0.6, coat=0.0, grain=dict(dark=(0.42, 0.28, 0.15), scale=40.0,
                distortion=1.0, along="Z")),
    "screen": dict(color=(0.30, 0.34, 0.32), rough=0.3, coat=0.3),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "logo": dict(color=(0.55, 0.75, 0.02), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-90, 2, 1.1),       # ref_11: square on from the rider's left
         "user_three_quarter": (-145, 10, 1.1)}   # ref_12: from the user's side, left
DETAILS = {
    "detail_flywheel": ((-0.70, 0.75, 0.70), (0.0, 0.08, 0.36), 40),      # the flywheel, the stand's foot
    "detail_monitor": ((-0.55, 0.70, 1.25), (0.0, 0.05, 0.95), 45),        # the PM5, the holders
    "detail_top": ((-0.60, 0.80, 2.30), (0.0, -0.05, 2.05), 40),           # the V, the top bar, the pulleys
}
SETTINGS = ("start_short", "start_middle", "start_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")

# ---- (y, z) from ref_11's px: y = (455 - x) / 416, z = (950 - y) / 416
BOARD = (0.98, -0.34, 0.012, 0.045)  # the board: its back and front (y), foot and top (z): 132 cm long
X_BOARD = 0.305                      # its half width (61 cm)
COL_D = 0.216                        # the column's depth below the joint (455-545 px)
COL_W = 0.10                         # its width (ref_03)
Z_JOINT = 1.09                       # the joint (495 px): the V opens above it
Z_TOP = 2.16                         # the top (216 cm)
TOP_D = 0.168                        # the depth at the top (455-525 px)
X_TOPBAR = 0.26                      # the top bar's half length (52 cm)
FW = (0.084, 0.36)                   # the flywheel: its centre (420, 800 px)
R_FW, D_FW = 0.24, 0.168             # its radius (48 cm across) and depth
U_BAR = (-0.24, 0.83)                # the stand's U: its bar behind the column (545-555, 600 px)
U_FOOT = 0.68                        # its legs' feet on the board (160-185 px)
X_U = 0.27                           # its legs (x)
Z_PM5 = 0.95                         # the monitor (515-580 px)
HANDLES = None                       # ((x, y, z) of each handle's grip) or None: at rest in the holders
SHOW = ()                            # the default build: the handles at rest, no user
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))


def pulley(s):
    return (s * (X_TOPBAR - 0.03), 0.035, Z_TOP - 0.07)


def start_pose(H):
    """The start of the stroke: (ball's y, the arm's angle from up toward the face, the hands' (y, z))."""
    L = 0.377 * H
    zsh = 0.818 * H
    zh = min(H + 0.12, pulley(1)[2] - 0.15)            # over the head, under the pulleys
    a = math.degrees(math.acos(max(-1.0, min(1.0, (zh - zsh) / L))))
    yh = 0.12                                           # the hands just in front of the column's face
    ysh = yh + L * math.sin(math.radians(a))
    ball = ysh - 0.48 * 0.152 * H
    return ball, a, (yh, zh)


def _handles_for(H):
    _, _, (yh, zh) = start_pose(H)
    return tuple((s * 0.20, yh, zh) for s in (1, -1))


def setting(name):
    global HANDLES, SHOW
    H = {"start_short": 1.55, "start_middle": 1.78, "start_tall": 1.95}[name]
    SHOW = ({"start_short": "short", "start_middle": "middle", "start_tall": "tall"}[name],)
    HANDLES = _handles_for(H)




def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    stand(k)
    column(k)
    flywheel(k)
    monitor(k)
    handles(k)


def stand(k):
    """The board (black tread on plywood), the wheels at its front, the U of tube: its legs from the board's back up
    either side to the bar clamped behind the column."""
    yb, yf, z0, z1 = BOARD
    k.box("ply", (0, (yb + yf) / 2, (z0 + z1 - 0.004) / 2), (2 * X_BOARD, yb - yf, z1 - z0 - 0.004), soft=0.004)
    k.box("tread", (0, (yb + yf) / 2, z1 - 0.002), (2 * X_BOARD - 0.006, yb - yf - 0.006, 0.004), soft=0.001)
    for s in (1, -1):
        for y in (yb - 0.05, 0.40):
            k.box("rubber", (s * (X_BOARD - 0.05), y, z0 / 2), (0.05, 0.05, z0), soft=0.001)
        k.disc("rubber", (s * (X_BOARD - 0.02), yf - 0.025, 0.03), 0.03, 0.008, 0.025, axis="x", seg=24)
        k.box("frame", (s * (X_BOARD - 0.045), yf - 0.01, 0.04), (0.006, 0.05, 0.04), soft=0.001)
        k.tube("steel", (s * (X_BOARD - 0.045), yf - 0.025, 0.03), (s * (X_BOARD - 0.01), yf - 0.025, 0.03), 0.007, seg=10)
    # the U: up from a foot plate each side at the back to the bar behind the column
    yu, zu = U_BAR
    for s in (1, -1):
        k.box("frame", (s * X_U, U_FOOT, z1 + 0.003), (0.05, 0.08, 0.006), soft=0.002)             # its foot plate
    pts = [(X_U, U_FOOT + 0.01, z1 + 0.02), (X_U, yu + 0.06, zu - 0.03), (X_U, yu, zu), (-X_U, yu, zu),
           (-X_U, yu + 0.06, zu - 0.03), (-X_U, U_FOOT + 0.01, z1 + 0.02)]
    k.sweep("frame", pts, k.circle(0.016, 20), bend=0.06, cut0=((0, 0, z1 + 0.006), (0, 0, 1)),
            cut1=((0, 0, z1 + 0.006), (0, 0, 1)))
    k.box("frame", (0, yu + 0.02, zu), (COL_W + 0.03, 0.04, 0.06), soft=0.004)                     # its clamp


def column(k):
    """The column: the box beam up to the joint, the V of two arms above it to the top bar, the pulley housings."""
    z1 = BOARD[3]
    k.box("frame", (0, -COL_D / 2, (z1 + Z_JOINT) / 2), (COL_W, COL_D, Z_JOINT - z1), soft=0.004)
    k.box("plastic", (0, -COL_D / 2, Z_JOINT + 0.03), (COL_W + 0.01, COL_D + 0.006, 0.06), soft=0.006)   # the joint
    for s in (1, -1):                                   # the V's arms, their depth tapering to the top
        a0 = (s * 0.03, 0.0, Z_JOINT + 0.055)
        a1 = (s * (X_TOPBAR - 0.05), 0.0, Z_TOP - 0.05)
        k.sweep("frame", [(a0[0], -COL_D / 2, a0[2]), (a1[0], -TOP_D / 2, a1[2])], k.rect(0.05, COL_D * 0.9, 0.006),
                up=(0, 1, 0))
    k.box("frame", (0, -TOP_D / 2, Z_TOP - 0.025), (2 * X_TOPBAR - 0.04, TOP_D, 0.05), soft=0.005)    # the top bar
    for s in (1, -1):
        p = pulley(s)
        k.box("plastic", (p[0], p[1] + 0.001, p[2] + 0.01), (0.05, 0.07, 0.08), soft=0.008)         # its housing, on the
                                                        # top bar's front
        k.disc("steel", p, 0.022, 0.008, 0.012, axis="x", seg=24)
    k.text("logo", "concept 2", (COL_W / 2 + 0.0003, -COL_D / 2, 0.80), 0.06, rz=math.pi / 2, spin=-math.pi / 2, depth=0.0006)
    for s in (1, -1):                                   # the handles' holders on the column's sides (ref_08)
        k.box("plastic", (s * (COL_W / 2 + 0.012), 0.02, Z_PM5 + 0.06), (0.024, 0.04, 0.05), soft=0.004)


def flywheel(k):
    fy, fz = FW
    k.cyl("shroud", (0, fy, fz), R_FW, 0.12, axis="y", seg=96, soft=0.012)                          # its housing
    k.cyl("plastic", (0, fy + 0.0605, fz), R_FW - 0.04, 0.002, axis="y", seg=96)                    # the face's grille
    for r in (0.08, 0.12, 0.16):
        k.disc("frame", (0, fy + 0.062, fz), r + 0.004, r, 0.002, axis="y", seg=72)
    k.cyl("logo", (0, fy + 0.0625, fz), 0.03, 0.002, axis="y", seg=32)                              # the C2 badge
    k.box("frame", (0, (fy - 0.06 - 0.006) / 2, fz), (COL_W - 0.02, fy - 0.06 + 0.010, 0.10), soft=0.003)   # its mount
    a = math.radians(135)                               # the damper lever on the housing's rim (upper left)
    k.box("plastic", (R_FW * math.cos(a) - 0.012, fy, fz + R_FW * math.sin(a) + 0.012), (0.03, 0.03, 0.05),
          ry=math.radians(45), soft=0.004)


def monitor(k):
    """The PM5 on its arm off the column's front (ref_08)."""
    t = math.radians(20)                                # tilted up toward the user
    c = (0, 0.12, Z_PM5 + 0.05)
    n, u = (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))
    back = (c[1] - n[0] * 0.016 - u[0] * 0.05, c[2] - n[1] * 0.016 - u[1] * 0.05)    # into its back, low
    k.bar("frame", (0, -0.004, back[1] - 0.01), (0, *back), 0.03, 0.03, up=(0, 0, 1), r=0.006)
    k.box("plastic", c, (0.14, 0.04, 0.17), rx=t, soft=0.01)
    k.box("screen", (0, c[1] + n[0] * 0.0205 + u[0] * 0.02, c[2] + n[1] * 0.0205 + u[1] * 0.02), (0.09, 0.002, 0.08), rx=t, soft=0.0)


def handles(k):
    """Each handle: in its holder at rest, or in the user's hand with the cord drawn from its pulley."""
    for i, s in enumerate((1, -1)):
        if HANDLES:
            g = HANDLES[i]
        else:
            g = (s * (COL_W / 2 + 0.012), 0.04, Z_PM5 - 0.02)
        p = pulley(s)
        top = (g[0], g[1], g[2] + 0.07)                  # the handle hangs off its cord: the top end
        k.box("yellow", (g[0], g[1], g[2] + 0.02), (0.035, 0.035, 0.12), soft=0.012)                 # the grip
        k.box("yellow", (g[0], g[1], g[2] - 0.045), (0.05, 0.10, 0.03), soft=0.012)                  # its foot
        k.sweep("cord", [p, top], k.circle(0.003, 8), soft=0.0)


# ---- the fit check (spec 5)
def fit():
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        ball, a, (yh, zh) = start_pose(H)
        print(f"fit {label}: standing at y {ball:.2f}, the arms {a:.0f} deg off upright, the hands at {zh:.2f} m", flush=True)
        out[label] = dict(H=H, ball=(0.0, ball, BOARD[3]), face=(0, -1), sole=0, shank=3, thigh=-3, trunk=0, neck=-5,
                          stance=0.30, arm=a, forearm=a)
    return out

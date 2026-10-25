"""Life Fitness Club Series+ Elliptical Cross-Trainer, black with the grey frame (refs/: ref_01 / ref_11-ref_13 the maker's
studio three-quarters, ref_14 Fitshop's side three-quarter, ref_15 the drive close-up, ref_02 / ref_04 in use, ref_06 /
ref_07 the pedals, ref_08 the moving handle's grip, ref_10 the pivot hub). Claude's pick (Roman, 2026-10-23: a free
hand, Life Fitness preferred). Built to the two gates; v004 rebuilt to the photos' build and bulk (Roman on v001-v003:
"your elliptical looks like shit": a tall open box, thin bars and stick feet).

DESIGN SPEC (gate 1)
1. Use. Standing on the two pedals facing -y (the console), the hands on the moving handles (or the fixed ones), the
   feet tracing ellipses, the arms pushing and pulling against them. Rear drive.
2. Moving parts (a real four-bar linkage per side, solved, not posed):
   - The crank: one axle across the narrow flywheel housing at the back, the flywheel inside it, a crank each side
     outside it, 180 deg apart (ref_14 / ref_15: the cranks outside the housing, under the pedal arms' pods).
   - Each pedal arm: its back end a big shrouded pod riding its crank's pin ("Life Fitness" on it), a beam forward to
     the rimmed pedal near the front, on to a pin at its swing arm's lower end.
   - Each swing arm: on the hub's axle at the column's top; below it carries the pedal arm's front end, above it is the
     moving handle. Its angle comes from the crank's: the pedal arm's length fixed between the crank pin and the link.
3. Adjustments. None on the machine (a fixed 51 cm stride, Life Fitness); the range is the user's: the moving handles
   are long curved grips (any height along them), the fixed handlebars round the console, 25 resistance levels on the
   console. The render shows the cranks level (the photos' pose); feet_level turns them a quarter on, where the fit
   users stand.
4. Load path. The feet on the pedals: the pedal arms turn the cranks; the axle turns the flywheel in its housing (its
   eddy brake inside, not drawn). The hands: the swing arms, the same linkage. The stride: the swing arm's lower end
   sweeps about the crank's diameter (0.50 m); the pedals near the front ride mostly the swing: 51 cm.
5. Fit range. The pedals' tops about 0.36-0.47 up (the step-up), 0.18 apart inside. Standing on them a 1.55-1.95 m
   user's hands reach the moving grips (1.20-1.64 m, curving back toward the user), the elbows bent in front; the fit
   run prints each elbow. The head clears the console (its top at 1.63, 0.35 m ahead).
6. Size. Life Fitness: 218 x 73 x 163 cm (L x W x H), stride 51 cm, 38 cm pedals. Ours about 2.20 x 0.76 x 1.75: the
   24 in SE4 console (the photos') stands over the hub; Life Fitness's 163 cm fits its smaller SL console.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; s = +1 left, -1 right.
"""
import math

LOOK = {
    "frame": dict(color=(0.025, 0.025, 0.027), rough=0.4, metal=0.3, coat=0.2),                       # the black frame
    "shroud": dict(color=(0.018, 0.018, 0.019), rough=0.42, coat=0.25),                              # the black shrouds
    "lever": dict(color=(0.02, 0.02, 0.021), rough=0.45, metal=0.2, coat=0.1),                       # the black arms
    "silver": dict(color=(0.55, 0.56, 0.58), rough=0.3, metal=0.9, coat=0.2),                        # the housing's discs
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "tread": dict(color=(0.06, 0.06, 0.062), rough=0.9, coat=0.0),                                  # the pedals' rubber
    "screen": dict(color=(0.01, 0.012, 0.016), rough=0.08, coat=1.0),
    "glow": dict(color=(0.20, 0.55, 0.30), rough=0.4, coat=0.0, emit=0.6),
    "label": dict(color=(0.75, 0.75, 0.76), rough=0.4, coat=0.0),
    "vent": dict(color=(0.08, 0.08, 0.085), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1),
         "ref_view": (-118, 10, 1.15)}  # ref_14's angle: from behind the user's left
DETAILS = {
    "detail_hub": ((0.90, -1.35, 1.75), (0.0, -0.72, 1.30), 45),          # the hub, the swing arms, the console
    "detail_pedal": ((0.80, -0.95, 0.95), (0.17, -0.35, 0.45), 45),        # a pedal, its arm, the link to the swing arm
    "detail_drive": ((0.95, 0.35, 0.95), (0.20, 0.78, 0.45), 50),          # the housing, a crank, a pod
}
SETTINGS = ("feet_level",)          # the cranks upright, the pedals level: the fit users stand here (a split stance
                                     # can't be posed with our figure)
SETTING_VIEWS = ("side", "three_quarter")
FIT_VIEWS = ("side", "three_quarter")

# ---- the base (ref_14: a flat grey rail on a rear stabilizer with wheels, a sculpted foot block under the column)
Y_FRONT, Y_REAR = -0.96, 1.05        # the front foot block's and the rear stabilizer's centres
X_STAB = 0.30                        # the rear stabilizer's half length (the wheels outside it: 73 cm)
SPINE_Z = 0.10                       # the spine's centre (a 120 x 100 box beam, under the pedals' lowest)
Y_COL = -0.72                        # the front column
# ---- the linkage (y, z), per side; spec 2
C = (0.80, 0.36)                     # the crank axle, in the body: as low as the flywheel allows (the body low)
R_C = 0.25                           # the crank's radius: its diameter sets the stride (51 cm, spec 4)
S = (-0.72, 1.24)                    # the swing arms' pivot on the hub
L_S = 0.84                           # the pivot to the swing arm's lower link
L_P = math.hypot(C[0] - S[0], C[1] - (S[1] - L_S))   # the pedal arm: pin to link (the swing hanging straight at 90 deg)
X_PA = 0.21                          # the pedal arms (x): on the cranks, inside the body's walls
X_SW = 0.34                          # the swing arms (x), outside the hub's ends
D_PED = 0.33                         # the pedal's centre back from the pedal arm's front link
PEDAL = (0.38, 0.17)                 # length, width (38 cm, Life Fitness)
X_PED = 0.15                         # the pedals' centres (x): in from the arms (ref_06: the pedal over the arm's inside)
PHI = 0.0                            # the left crank's angle (deg, from +y toward +z); the right one 180 deg on: level,
                                     # the pedal arms parallel, as the photos show it
HOUS = (0.40, 1.22, 0.10, 0.72, 0.30)   # the body: front and back (y), bottom and top (z), half width (a low skirt)
POD = (0.60, 0.24, 0.14, -0.38)      # each pod: length, height, width; where it starts ahead of the crank pin (the
                                     # cover on the arm that slides into the housing's open front)


def setting(name):
    global PHI
    if name == "feet_level":
        PHI = 90.0


def solve(phi):
    """The crank pin and the swing arm's angle (deg from straight down, + toward +y) for a crank angle: the pedal arm's
    length held between them."""
    a = math.radians(phi)
    P = (C[0] + R_C * math.cos(a), C[1] + R_C * math.sin(a))
    best = None
    for i in range(-600, 601):
        psi = i * 0.05
        L = (S[0] + L_S * math.sin(math.radians(psi)), S[1] - L_S * math.cos(math.radians(psi)))
        err = abs(math.dist(L, P) - L_P)
        if best is None or err < best[0]:
            best = (err, psi, L)
    return P, best[1], best[2]


def beam(phi):
    """The pedal arm at a crank angle: its pin and link points, its run (rear to front), its up, the pedal's centre and
    the pedal's tilt (box rx)."""
    P, psi, L = solve(phi)
    u = ((L[0] - P[0]) / L_P, (L[1] - P[1]) / L_P)
    nrm = (u[1], -u[0])                                 # square to the run, up (the run points mostly -y)
    pc = (L[0] - u[0] * D_PED + nrm[0] * 0.07, L[1] - u[1] * D_PED + nrm[1] * 0.07)
    return P, psi, L, u, nrm, pc, math.atan2(-u[1], -u[0])


def rot(p, about, deg):
    """Turn a (y, z) point about another by deg (from -z toward +y, the swing's sense)."""
    a = math.radians(deg)
    dy, dz = p[0] - about[0], p[1] - about[1]
    return (about[0] + dy * math.cos(a) - dz * math.sin(a), about[1] + dy * math.sin(a) + dz * math.cos(a))


# the moving handle in the swing arm's own frame (psi = 0): up from the pivot, curving back to the user (y, z)
HANDLE = [(S[0] + 0.0, S[1] + 0.058), (S[0] - 0.02, S[1] + 0.26), (S[0] + 0.10, S[1] + 0.38), (S[0] + 0.24, S[1] + 0.40)]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    column(k)
    housing(k)
    for s in (1, -1):
        linkage(k, s)


def base(k):
    """The rear stabilizer under the housing (its wheels at the ends), the spine (a black box beam) from the housing's
    front low down to the front stabilizer (a bar across, its feet at the ends), the column's foot on their joint."""
    k.box("frame", (0, Y_REAR, 0.045), (2 * X_STAB, 0.12, 0.07), soft=0.02)                     # the rear stabilizer
    for s in (1, -1):
        k.cyl("plastic", (s * (X_STAB + 0.022), Y_REAR + 0.02, 0.045), 0.045, 0.04, axis="x", seg=36, soft=0.004)
        k.tube("steel", (s * (X_STAB - 0.01), Y_REAR + 0.02, 0.045), (s * (X_STAB + 0.046), Y_REAR + 0.02, 0.045), 0.012, seg=16)
        k.box("rubber", (s * (X_STAB - 0.06), Y_REAR - 0.03, 0.006), (0.08, 0.05, 0.012), soft=0.003)
    k.tube("frame", (-0.36, Y_FRONT, 0.05), (0.36, Y_FRONT, 0.05), 0.038, seg=32)               # the front stabilizer
    for s in (1, -1):
        k.cyl("plastic", (s * 0.366, Y_FRONT, 0.05), 0.04, 0.012, axis="x", seg=32, soft=0.003)
        k.box("rubber", (s * 0.30, Y_FRONT, 0.006), (0.08, 0.07, 0.012), soft=0.003)
    zs = SPINE_Z
    k.bar("frame", (0, HOUS[0] + 0.06, zs), (0, Y_FRONT, zs), 0.12, 0.10, up=(0, 0, 1), r=0.02,
          cut1=((0, Y_FRONT + 0.038, 0), (0, -1, 0)), weld=True)                                  # the spine


def column(k):
    """The column up off the foot block to the hub, leaning back a little; the hub across (the swing arms' axle through
    it); the console on its neck off the hub, the fixed handlebars round its sides."""
    zh = S[1]
    c0 = (0, Y_FRONT + 0.10, SPINE_Z + 0.05)             # on the spine's top, behind the stabilizer
    c1 = (0, S[0], zh - 0.09 + 0.004)                   # its top into the hub's underside
    k.bar("frame", c0, c1, 0.13, 0.10, up=(0, 1, 0), r=0.035, cut0=((0, 0, SPINE_Z + 0.05), (0, 0, 1)))
    k.cyl("shroud", (0, S[0], zh), 0.09, 2 * X_SW - 0.09, axis="x", seg=48, soft=0.012)         # the hub
    k.cyl("label", (0, S[0] - 0.091, zh), 0.03, 0.002, axis="y", seg=32)                         # its LF badge
    k.tube("steel", (-(X_SW + 0.04), S[0], zh), (X_SW + 0.04, S[0], zh), 0.02, seg=20)          # the axle
    # the console: tilted back, its face up toward the user's eyes, on a neck straight up off the hub
    tl = math.radians(25)
    cn = (0, -0.74, 1.56)                               # its lower edge over the hub, its neck on the hub
    fn = (0.0, math.cos(tl), math.sin(tl))
    fu = (0.0, -math.sin(tl), math.cos(tl))
    bk = (0, cn[1] - fn[1] * 0.045, cn[2] - fn[2] * 0.045)
    yst = bk[1]
    zs0 = zh + math.sqrt(0.09 ** 2 - (yst - S[0]) ** 2)
    tn = (0.0, (yst - S[0]) / 0.09, (zs0 - zh) / 0.09)
    k.bar("shroud", (0, yst, zs0 - 0.02), (0, yst, bk[2] + 0.08), 0.12, 0.07, up=(0, 1, 0), r=0.02,
          cut0=((0, yst, zs0 - 0.001), tn), cut1=(bk, fn), weld=False)
    k.box("shroud", cn, (0.58, 0.09, 0.34), rx=tl, soft=0.03)                                     # 24 in, its housing
    k.box("screen", (0, cn[1] + fn[1] * 0.0455, cn[2] + fn[2] * 0.0455), (0.53, 0.003, 0.29), rx=tl, soft=0.0)
    k.box("glow", (0.12, cn[1] + fn[1] * 0.0475 + fu[1] * 0.08, cn[2] + fn[2] * 0.0475 + fu[2] * 0.08), (0.10, 0.002, 0.05),
          rx=tl, soft=0.0)
    # the fixed handlebars: off the console's lower corners, down and back toward the user (ref_11)
    for s in (1, -1):                                   # the fixed handlebars: out of the neck's sides, round toward the user
        a0 = (s * 0.058, yst, 1.365)
        a1, a2 = (s * 0.21, yst + 0.04, 1.365), (s * 0.23, -0.56, 1.345)   # between the hub and the console
        k.sweep("frame", [a0, a1, a2], k.circle(0.018, 20), bend=0.05)
        k.tube("rubber", tuple(a1[i] + (a2[i] - a1[i]) * 0.15 for i in range(3)), a2, 0.023, soft=0.003)
        ue = tuple((a2[i] - a1[i]) / math.dist(a1, a2) for i in range(3))
        k.sweep("plastic", [a2, tuple(a2[i] + ue[i] * 0.01 for i in range(3))], k.circle(0.024, 20), soft=0.002)


def body_curve(n=30):
    """The body's outer edge (y, z) from its front top over the crank and down its back: high enough over the arms'
    sweep and the pods (they slide in at the front), rounded at the back (ref_01)."""
    yf, yb, zb, zt, hw = HOUS
    pts = []
    p0, c1, p1 = (yf, zt - 0.05), (yf + 0.18, zt + 0.01), (yf + 0.45, zt)
    for i in range(n // 2):
        t = i / (n // 2)
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c1[0] + t * t * p1[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c1[1] + t * t * p1[1]))
    r = 0.22
    cy, cz = yb - r, zt - r
    for i in range(n // 2 + 1):
        a = math.radians(90 - 90 * i / (n // 2))
        pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    pts.append((yb, zb + 0.02))
    return pts


def housing(k):
    """The body: two sculpted side walls to the outline (a big round inset each, a vent strip at the back), a curved
    shell over the top and down the back between them; open at the front for the pedal arms and their pods, open below.
    On a cross plate over the spine's end and two posts on the rear stabilizer. Inside: the crank axle in bearings in
    the walls, the flywheel on it."""
    yf, yb, zb, zt, hw = HOUS
    top = body_curve()
    outline = top + [(yb, zb)] + [(yf + 0.12 - 0.12 * math.sin(math.radians(a)), zb + 0.12 - 0.12 * math.cos(math.radians(a)))
                                   for a in range(0, 91, 10)]   # the nose: rounded at the bottom front
    cy_, cz_ = (yf + yb) / 2, (zb + zt) / 2             # the profile's origin (the sweep maps u -> -y, v -> z)
    prof = [(-(y - cy_), z - cz_) for y, z in outline]
    for s in (1, -1):
        k.sweep("shroud", [(s * (hw - 0.014), cy_, cz_), (s * hw, cy_, cz_)], prof, up=(0, 0, 1), soft=0.005)
        k.cyl("plastic", (s * (hw + 0.002), C[0], C[1]), 0.24, 0.004, axis="x", seg=72)       # the round inset
        k.box("vent", (s * (hw + 0.001), yb - 0.10, (zb + zt) / 2), (0.002, 0.03, 0.30), soft=0.0)
    inner = []
    for i, (y, z) in enumerate(top):
        a = top[max(0, i - 1)]
        b_ = top[min(len(top) - 1, i + 1)]
        ty, tz = b_[0] - a[0], b_[1] - a[1]
        tl = math.hypot(ty, tz)
        inner.append((y + tz / tl * 0.02, z - ty / tl * 0.02))   # 2 cm in (the curve runs front to back, clockwise)
    band = [(-(y - cy_), z - cz_) for y, z in top + inner[::-1]]
    k.sweep("shroud", [(-(hw - 0.014), cy_, cz_), (hw - 0.014, cy_, cz_)], band, up=(0, 0, 1), soft=0.004)
    # the front: closed but for a slot each side the pedal arm's pod slides in through (ref_01)
    zft = body_curve()[0][1]                            # the front's top
    sx0, sx1 = X_PA - 0.076, X_PA + 0.076               # the slots: across the pods, the front's full height
    zp = SPINE_Z + 0.05                                 # the middle panel: down onto the spine's top
    k.box("shroud", (0, yf + 0.01, (zp + zft) / 2), (2 * sx0, 0.02, zft - zp), soft=0.004)

    for s in (1, -1):
        k.box("frame", (s * (hw - 0.03), Y_REAR, (0.08 + zb) / 2), (0.06, 0.06, zb - 0.08 + 0.004), soft=0.004)
    k.tube("steel", (-(hw - 0.014), C[0], C[1]), (hw - 0.014, C[0], C[1]), 0.02, seg=24)         # the crank axle
    k.disc("silver", (0, C[0], C[1]), 0.20, 0.05, 0.05, axis="x", seg=64)                         # the flywheel
    k.cyl("lever", (0, C[0], C[1]), 0.05, 0.07, axis="x", seg=40, soft=0.003)


def linkage(k, s):
    """One side: the crank outside the housing, the pedal arm (its pod over the crank, the beam, the rimmed pedal), the
    link to the swing arm, the swing arm and its moving handle, all at this build's crank angle."""
    phi = PHI if s > 0 else PHI + 180.0
    P, psi, L, u, nrm, pc, tilt = beam(phi)
    xc = s * (X_PA - 0.045)                             # the crank: a plate on the axle inside the body, by the arm
    k.cyl("lever", (xc, C[0], C[1]), 0.045, 0.024, axis="x", seg=32, soft=0.003)
    k.bar("lever", (xc, C[0] + (P[0] - C[0]) / R_C * 0.04, C[1] + (P[1] - C[1]) / R_C * 0.04), (xc, P[0], P[1]), 0.07, 0.024,
          up=(1, 0, 0))
    xa = s * X_PA
    k.tube("steel", (xc, P[0], P[1]), (xa, P[0], P[1]), 0.014, seg=16)                         # the crank pin
    k.cyl("lever", (xa, P[0], P[1]), 0.045, 0.06, axis="x", seg=32, soft=0.004)                # the arm's eye
    # the beam from the eye to the link; the pod round it ahead of the pin ("Life Fitness" on it), the pedal on it
    pl, ph, pw, pa = POD
    p0 = (P[0] - u[0] * pa, P[1] - u[1] * pa)           # the pod's back end
    p1 = (p0[0] + u[0] * pl, p0[1] + u[1] * pl)         # its front end
    k.bar("lever", (xa, P[0] + u[0] * 0.044, P[1] + u[1] * 0.044), (xa, p0[0] + u[0] * 0.006, p0[1] + u[1] * 0.006), 0.08,
          0.06, up=(1, 0, 0), r=0.012)                  # the beam: the eye into the pod, the pod out to the link
    k.bar("lever", (xa, p1[0] - u[0] * 0.006, p1[1] - u[1] * 0.006), (xa, L[0] - u[0] * 0.035, L[1] - u[1] * 0.035), 0.08,
          0.06, up=(1, 0, 0), r=0.012)
    pm = (p0[0] + u[0] * pl / 2, p0[1] + u[1] * pl / 2)
    k.box("shroud", (xa, pm[0], pm[1]), (pw, pl, ph), rx=tilt, soft=0.06)
    k.text("label", "Life Fitness", (xa + s * (pw / 2 + 0.001), pm[0], pm[1]), 0.045, rz=math.pi / 2 * s, spin=tilt,
           depth=0.0006)
    xp = s * X_PED
    k.box("lever", (s * (X_PED + X_PA) / 2, pc[0] - nrm[0] * 0.0225, pc[1] - nrm[1] * 0.0225), (X_PA - X_PED + 0.06, 0.14, 0.015),
          rx=tilt, soft=0.004)                                                                    # the pedal's bracket
    k.box("shroud", (xp, pc[0], pc[1]), (PEDAL[1], PEDAL[0], 0.03), rx=tilt, soft=0.01)        # the pedal: its tray
    k.box("tread", (xp, pc[0] + nrm[0] * 0.0155, pc[1] + nrm[1] * 0.0155), (PEDAL[1] - 0.03, PEDAL[0] - 0.05, 0.002),
          rx=tilt, soft=0.0)
    for d in (1, -1):                                   # its rim: the side walls and the raised toe
        k.box("shroud", (xp + d * (PEDAL[1] / 2 - 0.006), pc[0] + nrm[0] * 0.03, pc[1] + nrm[1] * 0.03),
              (0.012, PEDAL[0] - 0.07, 0.03), rx=tilt, soft=0.004)
    toe = (pc[0] + u[0] * (PEDAL[0] / 2 - 0.01), pc[1] + u[1] * (PEDAL[0] / 2 - 0.01))
    k.box("shroud", (xp, toe[0] + nrm[0] * 0.04, toe[1] + nrm[1] * 0.04), (PEDAL[1], 0.025, 0.05), rx=tilt, soft=0.008)
    # the link: the beam's front eye, a cross pin out to the swing arm's lower end
    k.cyl("lever", (xa, L[0], L[1]), 0.04, 0.08, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xa, L[0], L[1]), (s * (X_SW + 0.03), L[0], L[1]), 0.014, seg=16)
    # the swing arm: from the hub down to the link (its lower housing), up as the moving handle
    xs = s * X_SW
    k.cyl("lever", (xs, S[0], S[1]), 0.06, 0.07, axis="x", seg=40, soft=0.005)                 # its hub
    dn = ((L[0] - S[0]) / L_S, (L[1] - S[1]) / L_S)
    k.bar("lever", (xs, S[0] + dn[0] * 0.058, S[1] + dn[1] * 0.058), (xs, L[0] - dn[0] * 0.11, L[1] - dn[1] * 0.11),
          0.07, 0.05, up=(1, 0, 0), r=0.012)
    k.box("shroud", (xs, L[0] - dn[0] * 0.04, L[1] - dn[1] * 0.04), (0.08, 0.09, 0.14), rx=math.radians(psi),
          soft=0.02)                                                                              # the lower housing
    hp = [rot(p, S, psi) for p in HANDLE]
    k.sweep("lever", [(xs, y, z) for y, z in hp], k.circle(0.021, 24), bend=0.06)
    g = [(xs, y, z) for y, z in hp[1:]]
    k.sweep("rubber", g, k.circle(0.026, 24), bend=0.06, soft=0.003)
    e = g[-1]
    k.cyl("plastic", (xs, e[1] + 0.006, e[2]), 0.027, 0.012, axis="y", seg=24, soft=0.003)


# ---- the fit check (spec 5)
def fit():
    if PHI != 90.0:
        return {}
    out = {}
    r = math.radians
    pl = [ped_top(s) for s in (1, -1)]
    by = (pl[0][0] + pl[1][0]) / 2
    bz = (pl[0][1] + pl[1][1]) / 2
    for label, H in (("short", 1.55), ("middle", 1.78), ("tall", 1.95)):
        ball = (0.0, by - 0.06, bz)
        hip, sh = stand(H, ball, 8.0, -4.0, 6.0)
        a1, l1, a2, l2, elbow = reach(H, sh)
        print(f"fit {label}: elbow {elbow:.0f} deg", flush=True)
        out[label] = dict(H=H, ball=ball, face=(0, -1), sole=0, shank=8.0, thigh=-4.0, trunk=6.0, neck=0,
                          stance=0.20, arm=a1, forearm=a2, arm_lat=l1, fore_lat=l2)
    return out


def ped_top(s):
    """The pedal's top (y, z) for side s at this build's crank angle."""
    pc = beam(PHI if s > 0 else PHI + 180.0)[5]
    return pc[0], pc[1] + 0.017


def stand(H, ball, shank, thigh, trunk):
    r = math.radians
    ay, az = ball[1] + 0.48 * 0.152 * H, ball[2] + 0.039 * H
    ky, kz = ay - math.sin(r(shank)) * 0.246 * H, az + math.cos(r(shank)) * 0.246 * H
    hy, hz = ky - math.sin(r(thigh)) * 0.245 * H, kz + math.cos(r(thigh)) * 0.245 * H
    sy, sz = hy - math.sin(r(trunk)) * 0.288 * H, hz + math.cos(r(trunk)) * 0.288 * H
    return (0.0, hy, hz), (0.13 * H * 0.85, sy, sz)


def reach(H, sh):
    """The left arm to the left moving handle's grip at about the elbow's natural height; returns body.figure's angles
    and the elbow's inside angle."""
    _, psi, _ = solve(PHI)
    hp = [rot(p, S, psi) for p in HANDLE]
    best = None
    for (y0, z0), (y1, z1) in zip(hp[1:], hp[2:]):
        for i in range(11):
            t = i / 10
            q = (X_SW, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t)
            d = abs(q[2] - (sh[2] - 0.22))
            if best is None or d < best[0]:
                best = (d, q)
    g = best[1]
    f, left = (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
    L1, L2 = 0.186 * H, 0.191 * H
    v = tuple(g[i] - sh[i] for i in range(3))
    d = math.sqrt(sum(c * c for c in v))
    vh = tuple(c / d for c in v)
    if d >= L1 + L2 - 1e-6:
        e, elbow = tuple(c * L1 for c in vh), 180.0
    else:
        al = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        w0 = (0.3, 0.3, -0.9)                           # the elbow's way: down, a little out and back
        dot = sum(w0[i] * vh[i] for i in range(3))
        w = tuple(w0[i] - vh[i] * dot for i in range(3))
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

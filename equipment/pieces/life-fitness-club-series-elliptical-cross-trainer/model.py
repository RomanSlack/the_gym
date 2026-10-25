"""Life Fitness Club Series+ Elliptical Cross-Trainer, black with the grey frame (refs/: ref_01 / ref_11-ref_13 the maker's
studio three-quarters, ref_02 / ref_04 in use, ref_07 / ref_06 the pedals, ref_08 the moving handle's grip, ref_10 the
pivot hub). Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred). Built to the two gates.

DESIGN SPEC (gate 1)
1. Use. Standing on the two pedals facing -y (the console), the hands on the moving handles (or the fixed ones), the
   feet tracing ellipses, the arms pushing and pulling against them. Rear drive: the crank and the flywheel in the
   housing behind the user, the swing arms pivoting on the hub at the top of the front column.
2. Moving parts (a real four-bar linkage per side, solved, not posed):
   - The crank: one axle across the rear housing, the flywheel on it, a crank each side 180 deg apart.
   - Each pedal arm: its back end on its crank's pin, its front end pinned to its swing arm's lower end; the pedal on
     top of it near the front, the shrouded middle ("Life Fitness" on it) the arm's main section.
   - Each swing arm: on the hub's axle; below the hub it carries the pedal arm's front end, above it it is the moving
     handle. Its angle comes from the crank's: the pedal arm's length fixed between the crank pin and the link.
3. Adjustments. None on the machine (a fixed 51 cm stride, Life Fitness); the range is the user's: the moving handles
   are long curved grips (any height along them), the fixed handlebars below the console, the 25 resistance levels on
   the console. The render shows the cranks level (the photos' pose); the feet_level setting turns them a quarter on,
   the pedals level, where the fit users stand.
4. Load path. The feet on the pedals: the pedal arms turn the cranks; the axle turns the flywheel, braked by its eddy
   magnet (inside the housing, not drawn). The hands: the swing arms, the same linkage. The stride: the swing arm's
   lower end sweeps about the crank's diameter (0.50 m); the pedals near the front ride mostly the swing: 51 cm.
5. Fit range. The pedals' tops about 0.36-0.47 up (the step-up), 0.10 apart inside (a narrow Q). Standing on them a
   1.55-1.95 m user's hands reach the moving grips (they run from 1.20 to 1.55 m, curving back toward the user), the
   elbows bent in front; the fit run prints each elbow. The head clears the console (its top at 1.63, 0.35 m ahead).
6. Size. Life Fitness: 218 x 73 x 163 cm (L x W x H), stride 51 cm, 38 cm pedals. Ours to that box.
Axes: metres, floor z = 0, the user faces -y, x+ = the user's left; s = +1 left, -1 right.
"""
import math

LOOK = {
    "frame": dict(color=(0.20, 0.205, 0.21), rough=0.38, metal=0.6, coat=0.2),                        # the grey frame
    "shroud": dict(color=(0.018, 0.018, 0.019), rough=0.42, coat=0.25),                              # the black shrouds
    "lever": dict(color=(0.02, 0.02, 0.021), rough=0.45, metal=0.2, coat=0.1),                       # the black arms
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.06, metal=1.0, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "tread": dict(color=(0.06, 0.06, 0.062), rough=0.9, coat=0.0),                                  # the pedals' rubber
    "screen": dict(color=(0.01, 0.012, 0.016), rough=0.08, coat=1.0),
    "glow": dict(color=(0.20, 0.55, 0.30), rough=0.4, coat=0.0, emit=0.6),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
    "fly": dict(color=(0.35, 0.35, 0.36), rough=0.3, metal=0.8, coat=0.0),
}
VIEWS = {"three_quarter": (-40, 12, 1.1), "front": (0, 5, 1.1), "side": (90, 3, 1.1), "back_three_quarter": (140, 16, 1.1)}
DETAILS = {
    "detail_hub": ((0.90, -1.35, 1.75), (0.0, -0.72, 1.30), 45),          # the hub, the swing arms, the console's stem
    "detail_pedal": ((0.80, -0.95, 0.95), (0.13, -0.35, 0.45), 45),        # a pedal, its arm, the link to the swing arm
    "detail_crank": ((0.95, 0.20, 0.75), (0.15, 0.72, 0.40), 50),          # the housing's opening, the cranks
}
SETTINGS = ("feet_level",)          # the cranks upright, the pedals level: the fit users stand here (a split stance
                                     # can't be posed with our figure)
SETTING_VIEWS = ("side", "three_quarter")
FIT_VIEWS = ("side", "three_quarter")

# ---- the frame
Y_FRONT, Y_REAR = -0.98, 0.98        # the stabilizers (Life Fitness's 218 cm over their caps and the housing)
X_STAB = 0.33                        # their half length (73 cm wide with the wheels)
R_SPINE = 0.045
Z_SPINE = 0.07 + R_SPINE             # the spine's centre (on the stabilizers)
Y_COL = -0.72                        # the front column
# ---- the linkage (y, z), per side; spec 2
C = (0.72, 0.44)                     # the crank axle, in the housing
R_C = 0.25                           # the crank's radius: its diameter sets the stride (51 cm, spec 4)
S = (-0.72, 1.24)                    # the swing arms' pivot on the hub
L_S = 0.84                           # the pivot to the swing arm's lower link
L_P = math.hypot(C[0] - S[0], C[1] - (S[1] - L_S))   # the pedal arm: pin to link (the swing hanging straight at 90 deg)
X_PA = 0.13                          # the pedal arms (x)
X_SW = 0.27                          # the swing arms (x), outside the hub's ends
D_PED = 0.33                         # the pedal's centre back from the pedal arm's front link
PEDAL = (0.38, 0.16)                 # length, width (38 cm, Life Fitness)
PHI = 0.0                            # the left crank's angle (deg, from +y toward +z); the right one 180 deg on: level,
                                     # the pedal arms parallel, as the photos show it
# ---- the housing (spec 1)
HOUS = (0.40, 1.02, 0.10, 0.83, 0.27)   # its front and back (y), bottom and top (z), half width (the curve: hood_curve)


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
    pc = (L[0] - u[0] * D_PED + nrm[0] * 0.05, L[1] - u[1] * D_PED + nrm[1] * 0.05)
    return P, psi, L, u, nrm, pc, math.atan2(-u[1], -u[0])


def rot(p, about, deg):
    """Turn a (y, z) point about another by deg (from -z toward +y, the swing's sense)."""
    a = math.radians(deg)
    dy, dz = p[0] - about[0], p[1] - about[1]
    return (about[0] + dy * math.cos(a) - dz * math.sin(a), about[1] + dy * math.sin(a) + dz * math.cos(a))


# the moving handle in the swing arm's own frame (psi = 0): up from the pivot, curving back to the user (y, z)
HANDLE = [(S[0] + 0.0, S[1] + 0.048), (S[0] - 0.02, S[1] + 0.26), (S[0] + 0.10, S[1] + 0.38), (S[0] + 0.24, S[1] + 0.40)]


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    base(k)
    column(k)
    housing(k)
    for s in (1, -1):
        linkage(k, s)


def base(k):
    """The stabilizers (feet at their ends, the rear one with its transport wheels), the spine between them."""
    for y, wheels in ((Y_FRONT, False), (Y_REAR, True)):
        k.tube("frame", (-X_STAB, y, 0.05), (X_STAB, y, 0.05), 0.035, seg=28)
        for s in (1, -1):
            k.cyl("plastic", (s * (X_STAB + 0.006), y, 0.05), 0.037, 0.012, axis="x", seg=28, soft=0.003)
            k.box("rubber", (s * (X_STAB - 0.06), y, 0.0075), (0.08, 0.07, 0.015), soft=0.003)
            if wheels:
                k.cyl("plastic", (s * (X_STAB + 0.03), y + 0.05, 0.045), 0.04, 0.03, axis="x", seg=32, soft=0.004)
                k.box("plastic", (s * (X_STAB + 0.012), y + 0.02, 0.05), (0.012, 0.07, 0.04), soft=0.002)
    k.tube("frame", (0, Y_FRONT + 0.03, Z_SPINE), (0, Y_REAR - 0.03, Z_SPINE), R_SPINE, seg=32)
    for y in (Y_FRONT, Y_REAR):                         # the spine's saddles on the stabilizers
        k.box("frame", (0, y, (0.085 + Z_SPINE - 0.02) / 2), (0.10, 0.07, Z_SPINE - 0.02 - 0.085 + 0.01), soft=0.004)


def column(k):
    """The column up off the spine to the hub; the hub across (the swing arms' axle through it); the fixed handlebars
    and the console on a stem off the hub."""
    zh = S[1]
    zfoot = Z_SPINE + R_SPINE - 0.005                   # its saddle on the spine's top
    k.box("frame", (0, Y_COL, zfoot + 0.02), (0.12, 0.12, 0.04), soft=0.006)
    k.bar("frame", (0, Y_COL, zfoot + 0.04), (0, Y_COL, zh - 0.075), 0.10, 0.08, up=(0, 1, 0), r=0.02,
          cut0=((0, 0, zfoot + 0.04), (0, 0, 1)), weld=True)
    k.cyl("shroud", (0, S[0], zh), 0.08, 2 * X_SW - 0.08, axis="x", seg=48, soft=0.01)          # the hub
    k.cyl("label", (0, S[0] - 0.081, zh + 0.0), 0.028, 0.002, axis="y", seg=32)                  # its LF badge
    k.tube("steel", (-(X_SW + 0.04), S[0], zh), (X_SW + 0.04, S[0], zh), 0.02, seg=20)          # the axle
    # the console: a stem up and forward off the hub, the tablet tilted toward the user
    tl = math.radians(20)                               # tilted back, its face up toward the user's eyes
    cn = (0, -0.74, 1.53)
    fn = (0.0, math.cos(tl), math.sin(tl))              # the face's normal (toward the user, a little up)
    bk = (0, cn[1] - fn[1] * 0.02, cn[2] - fn[2] * 0.02)   # the console's back face
    yst = bk[1]                                         # the stem: straight up off the hub's top to the back face
    zs0 = zh + math.sqrt(0.08 ** 2 - (yst - S[0]) ** 2)   # its foot on the hub's curve, cut to the tangent there
    tn = (0.0, (yst - S[0]) / 0.08, (zs0 - zh) / 0.08)
    st0, st1 = (0, yst, zs0 - 0.02), (0, yst, bk[2] + 0.06)
    k.bar("shroud", st0, st1, 0.08, 0.06, up=(0, 1, 0), cut0=((0, yst, zs0 - 0.001), tn), cut1=(bk, fn), weld=False)
    k.box("shroud", cn, (0.44, 0.04, 0.30), rx=tl, soft=0.012)
    k.box("screen", (0, cn[1] + fn[1] * 0.0215, cn[2] + fn[2] * 0.0215), (0.40, 0.003, 0.26), rx=tl, soft=0.0)
    fu = (0.0, -math.sin(tl), math.cos(tl))             # the face's up (away from the user as it rises)
    k.box("glow", (0.08, cn[1] + fn[1] * 0.0235 + fu[1] * 0.06, cn[2] + fn[2] * 0.0235 + fu[2] * 0.06), (0.06, 0.002, 0.03),
          rx=tl, soft=0.0)
    # the fixed handlebars: a U under the console, its grips back toward the user
    zf = zh + 0.11                                      # under the console's lower edge, over the hub
    yb = yst + 0.03 + 0.02 + 0.016                      # the cross bar, clamped to the stem's face on the user's side
    path = [(-0.17, -0.56, zf + 0.02), (-0.15, yb, zf), (0.15, yb, zf), (0.17, -0.56, zf + 0.02)]
    k.sweep("frame", path, k.circle(0.016, 20), bend=0.05)
    k.box("frame", (0, yst + 0.04, zf), (0.08, 0.02, 0.04), soft=0.003)                           # its clamp block
    for s in (1, -1):
        k.tube("rubber", (s * 0.158, yb + 0.06, zf + 0.008), (s * 0.17, -0.56, zf + 0.02), 0.021, soft=0.003)


def hood_curve(n=28):
    """The hood's outer edge (y, z) from its front top over the crank and down its back (the side photo's long, low
    loaf): a curve up from the front, an arc round the back, straight down to the stabilizer."""
    pts = []
    p0, c1, p1 = (0.40, 0.70), (0.55, 0.83), (0.80, 0.82)
    for i in range(n // 2):
        t = i / (n // 2)
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c1[0] + t * t * p1[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c1[1] + t * t * p1[1]))
    cy, cz, r = 0.80, 0.62, 0.20
    for i in range(n // 2 + 1):
        a = math.radians(90 - 90 * i / (n // 2))
        pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    pts.append((cy + r, 0.14))
    return pts


def housing(k):
    """The rear hood: two side panels to the side photo's outline, a curved shell over the top and down the back
    between them (open at the front for the pedal arms, open below); posts down onto the rear stabilizer. Inside: the
    crank axle in bearings on the panels, the flywheel on it, a crank each side."""
    yf, _, zb, _, hw = HOUS
    top = hood_curve()
    outline = top + [(top[-1][0], zb), (yf, zb)]        # the side panel: the curve, the back, the bottom, the front
    cy_, cz_ = 0.70, 0.45                               # the profile's origin (the sweep maps u -> -y, v -> z)
    prof = [(-(y - cy_), z - cz_) for y, z in outline]
    for s in (1, -1):
        k.sweep("shroud", [(s * (hw - 0.012), cy_, cz_), (s * hw, cy_, cz_)], prof, up=(0, 0, 1), soft=0.004)
        k.cyl("plastic", (s * (hw + 0.002), C[0], C[1]), 0.20, 0.004, axis="x", seg=64)       # the round inset
    # the shell: the curve and its inside (2 cm in), swept across between the panels
    inner = []
    for i, (y, z) in enumerate(top):
        a = top[max(0, i - 1)]
        b_ = top[min(len(top) - 1, i + 1)]
        ty, tz = b_[0] - a[0], b_[1] - a[1]
        tl = math.hypot(ty, tz)
        inner.append((y + tz / tl * 0.02, z - ty / tl * 0.02))   # 2 cm in (the curve runs front to back, clockwise)
    band = [(-(y - cy_), z - cz_) for y, z in top + inner[::-1]]
    k.sweep("shroud", [(-(hw - 0.012), cy_, cz_), (hw - 0.012, cy_, cz_)], band, up=(0, 0, 1), soft=0.004)
    for x in (0.16, -0.16):                             # the posts onto the rear stabilizer, under the shell's back
        k.box("frame", (x, Y_REAR - 0.03, (0.085 + 0.20) / 2), (0.06, 0.06, 0.20 - 0.085 + 0.004), soft=0.004)   # against its inside
    k.text("label", "Life Fitness", (hw + 0.001, 0.62, 0.66), 0.05, rz=math.pi / 2, spin=0.0, depth=0.0006)
    k.text("label", "Life Fitness", (-(hw + 0.001), 0.62, 0.66), 0.05, rz=-math.pi / 2, spin=0.0, depth=0.0006)
    k.tube("steel", (-(hw - 0.012), C[0], C[1]), (hw - 0.012, C[0], C[1]), 0.02, seg=24)         # the crank axle
    k.disc("fly", (0, C[0], C[1]), 0.20, 0.05, 0.05, axis="x", seg=64)                            # the flywheel's rim
    k.cyl("lever", (0, C[0], C[1]), 0.05, 0.07, axis="x", seg=40, soft=0.003)                     # its keyed hub


def linkage(k, s):
    """One side: the crank, the pedal arm (its shroud, the pedal), the link to the swing arm, the swing arm and its
    moving handle, all at this build's crank angle."""
    phi = PHI if s > 0 else PHI + 180.0
    P, psi, L, u, nrm, pc, tilt = beam(phi)
    xc = s * (X_PA + 0.035)                             # the crank plate, outside the pedal arm
    k.bar("lever", (xc, C[0] + (P[0] - C[0]) / R_C * 0.04, C[1] + (P[1] - C[1]) / R_C * 0.04), (xc, P[0], P[1]), 0.06, 0.012,
          up=(1, 0, 0))
    k.cyl("lever", (xc, C[0], C[1]), 0.04, 0.02, axis="x", seg=32, soft=0.003)
    k.tube("steel", (xc, P[0], P[1]), (s * (X_PA - 0.028), P[0], P[1]), 0.012, seg=16)          # the crank pin
    # the pedal arm: pin to link, a 50 x 70 beam; its shroud over the back part; the pedal on top near the front
    xa = s * X_PA
    sh0 = (P[0] + u[0] * 0.30, P[1] + u[1] * 0.30)      # the shroud: the arm's middle, the beam's two ends into it
    sh1 = (L[0] - u[0] * (D_PED + PEDAL[0] / 2 + 0.03), L[1] - u[1] * (D_PED + PEDAL[0] / 2 + 0.03))
    k.bar("lever", (xa, P[0] + u[0] * 0.036, P[1] + u[1] * 0.036), (xa, sh0[0] + u[0] * 0.006, sh0[1] + u[1] * 0.006),
          0.07, 0.05, up=(1, 0, 0))
    k.bar("lever", (xa, sh1[0] - u[0] * 0.006, sh1[1] - u[1] * 0.006), (xa, L[0] - u[0] * 0.031, L[1] - u[1] * 0.031),
          0.07, 0.05, up=(1, 0, 0))
    k.cyl("lever", (xa, P[0], P[1]), 0.04, 0.06, axis="x", seg=32, soft=0.004)                 # its bearing eye
    k.sweep("shroud", [(xa, sh0[0], sh0[1]), (xa, sh1[0], sh1[1])], k.rect(0.12, 0.10, 0.03), up=(1, 0, 0), soft=0.008)
    mid = ((sh0[0] + sh1[0]) / 2, (sh0[1] + sh1[1]) / 2)
    k.text("label", "Life Fitness", (xa + s * 0.0505, mid[0], mid[1]), 0.035, rz=math.pi / 2 * s,
           spin=math.atan2(-u[1], -u[0]), depth=0.0005)
    xp = s * (X_PA - 0.005)
    k.box("shroud", (xp, pc[0], pc[1]), (PEDAL[1], PEDAL[0], 0.03), rx=tilt, soft=0.008)
    k.box("tread", (xp, pc[0] + nrm[0] * 0.0155, pc[1] + nrm[1] * 0.0155), (PEDAL[1] - 0.02, PEDAL[0] - 0.03, 0.002),
          rx=tilt, soft=0.0)
    toe = (pc[0] + u[0] * (PEDAL[0] / 2 + 0.015), pc[1] + u[1] * (PEDAL[0] / 2 + 0.015))
    k.box("shroud", (xp, toe[0] + nrm[0] * 0.035, toe[1] + nrm[1] * 0.035), (PEDAL[1], 0.03, 0.07), rx=tilt,
          soft=0.01)                                                                              # the toe's lip
    # the link: the pedal arm's front eye, a cross pin out to the swing arm's lower end
    k.cyl("lever", (xa, L[0], L[1]), 0.035, 0.06, axis="x", seg=32, soft=0.004)
    k.tube("steel", (xa, L[0], L[1]), (s * (X_SW + 0.03), L[0], L[1]), 0.013, seg=16)
    # the swing arm: from the hub's axle down to the link (a boxy lower housing, ref_02), up as the moving handle
    xs = s * X_SW
    k.cyl("lever", (xs, S[0], S[1]), 0.05, 0.06, axis="x", seg=40, soft=0.004)                 # its hub
    dn = ((L[0] - S[0]) / L_S, (L[1] - S[1]) / L_S)
    k.bar("lever", (xs, S[0] + dn[0] * 0.048, S[1] + dn[1] * 0.048), (xs, L[0] - dn[0] * 0.10, L[1] - dn[1] * 0.10),
          0.045, 0.04, up=(1, 0, 0))
    k.box("lever", (xs, L[0] - dn[0] * 0.03, L[1] - dn[1] * 0.03), (0.07, 0.07, 0.14), rx=math.radians(psi),
          soft=0.01)                                                                              # the lower housing
    hp = [rot(p, S, psi) for p in HANDLE]
    k.sweep("lever", [(xs, y, z) for y, z in hp], k.circle(0.019, 24), bend=0.06)
    g = [(xs, y, z) for y, z in hp[1:]]
    k.sweep("rubber", g, k.circle(0.024, 24), bend=0.06, soft=0.003)                           # the grip's rubber
    e = g[-1]
    k.cyl("plastic", (xs, e[1] + 0.006, e[2]), 0.025, 0.012, axis="y", seg=24, soft=0.003)


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

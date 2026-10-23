"""StairMaster 8Gx StepMill with the LED console, Matte Black.

Built by eye from the maker's renders (refs/: ref_04 / ref_06 the true sides, ref_10 the true front, ref_05 the back,
ref_01 the three-quarter, ref_02 / ref_07 / ref_09 the LED console square on, ref_08 its back, ref_03 the handrails' tops
from the front), held to StairMaster's 58 x 34 x 79 in (147 x 86 x 200 cm), steps 22 in wide x 10 in deep on an 8 in
rise, a 9 in step-up. Side-view numbers off ref_04 at 1.96 mm/px (the 79 in height), as (y, z): y = (px - 600) * 0.00196,
z = (1112 - py) * 0.00196; widths off ref_10 at the same scale (centre px 615).
Axes: metres, floor z = 0; the user climbs facing +y toward the console, the stair's foot at -y; +x is the side ref_04
shows (the user's right).
Structure: a low steel base on levelling feet in front and transport wheels at the back; two polypropylene side
housings, each wrapping the lower and the upper drum (the grey rings on their outer faces), joined across by the top cap
over the stair's head and the back wall; the staircase between them (treads with grip ribs, risers, the grille under the
lowest), a red-lipped rest platform at each housing's foot; each side's handrail (the post off the housing's top edge,
the C-loop back toward the entry, the upper rail with its heart-rate grip rising to a bend, the grip horn up from it, the
diagonal in to the mast); the mast with the cup holders and the tilted LED console.
"""
import math

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.55, metal=0.2, coat=0.0, bump=(1400, 0.06)),    # Matte Black
    "shroud": dict(color=(0.016, 0.016, 0.017), rough=0.42, metal=0.0, coat=0.15, bump=(900, 0.03)),   # polypropylene
    "ring": dict(color=(0.07, 0.07, 0.075), rough=0.3, metal=0.4, coat=0.2),
    "trim": dict(color=(0.16, 0.16, 0.17), rough=0.3, metal=0.5, coat=0.0),
    "rail": dict(color=(0.02, 0.02, 0.021), rough=0.6, coat=0.0, bump=(2000, 0.08)),               # soft-touch
    "tread": dict(color=(0.02, 0.02, 0.021), rough=0.8, coat=0.0, spec=0.2),
    "red": dict(color=(0.55, 0.03, 0.02), rough=0.45, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.08, metal=1.0, coat=0.0),
    "steel": dict(color=(0.7, 0.7, 0.71), rough=0.22, metal=1.0, aniso=0.4),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "hole": dict(color=(0.003, 0.003, 0.003), rough=0.9),
    "glass": dict(color=(0.004, 0.004, 0.005), rough=0.55, coat=0.0, spec=0.25),   # a matte anti-glare screen
    "led": dict(color=(0.75, 0.8, 0.85), rough=0.4, emit=0.9),
    "ledred": dict(color=(0.8, 0.06, 0.04), rough=0.4, emit=0.9),
    "ledgreen": dict(color=(0.15, 0.6, 0.2), rough=0.4, emit=0.8),
    "label": dict(color=(0.35, 0.35, 0.37), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (35, 12, 1.0), "front": (0, 4, 1.0), "side": (90, 2, 1.0), "back": (180, 4, 1.0)}
DETAILS = {
    "detail_console": ((0.0, -0.45, 2.05), (0.0, 0.55, 1.75), 45),        # the console, the mast, rails, cup holders
    "detail_stair": ((0.45, -1.35, 1.05), (0.0, -0.25, 0.55), 40),        # the treads, the grille, a rest platform
}

S = 0.00196
XI, XO = 0.297, 0.425               # the side housings' inner and outer faces (ref_10: the 22 in stair between them)
ZB = 0.063                          # the housings' and the stair's underside, on the base
CL = (-0.333, 0.337, 0.21)          # the lower drum: centre (y, z), the housing's radius round it (ref_04: 430, 940 px)
CU = (0.47, 1.023, 0.27)            # the upper drum (ref_04: 840, 590 px), its top the housing's 1.29
YR0, YR1 = 0.62, 0.70               # the back wall (ref_04: px 955)
STEP = (-0.48, 0.25, 0.254, 0.203)  # the lowest nosing (y, z), the tread depth, the rise (10 in, 8 in)
NST = 5
XR = 0.37                           # the handrails' plane (ref_10: px 405-445)
POST = [(-0.03, 0.97), (-0.176, 1.55)]                                  # the post (ref_04: 585, 610 -> 510, 320 px)
LOOP = [(-0.176, 1.55), (-0.33, 1.51), (-0.447, 1.36), (-0.33, 1.22), (-0.11, 1.27)]   # the C-loop (ref_04: 372 px)
BEND = (0.284, 1.75)                # the upper rail's top bend (ref_04: 745, 220 px)
HORN = (0.30, 0.392, 1.93)          # the grip horn's tip (x, y, z) (ref_04: 800, 128 px; ref_10: px 470, 150)
MAST = (0.53, 1.30, 1.55)           # the mast: y, its foot on the cap, the knuckle (ref_04: 860, 330 px)
CON = (0.61, 1.885, 0.35, 0.27, math.radians(41))   # the console: centre y, z, width, height, tilt back from vertical


def _hull(pts):
    pts = sorted(set(pts))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _circle(c, r, n=36, a0=0, a1=360):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def slab(k, mat, prof, x0, x1, soft):
    """Extrude a (y, z) outline across x from x0 to x1 (x0 < x1)."""
    k.sweep(mat, [(x0, 0, 0), (x1, 0, 0)], [(-y, z) for y, z in prof], up=(0, 0, 1), soft=soft)


def foot(k, x, y):
    k.cyl("steel", (x, y, 0.035), 0.009, 0.05, seg=12)
    k.cyl("rubber", (x, y, 0.006), 0.035, 0.012, seg=28, soft=0.003)
    k.cyl("frame", (x, y, 0.016), 0.016, 0.008, seg=6)


def build(k):
    Z = (0, 0, 1)
    # ---- the base: a low steel frame under the housings, levelling feet in front, the wheels on brackets at the back
    for s in (1, -1):
        k.bar("frame", (s * (XO - 0.05), -0.46, 0.042), (s * (XO - 0.05), 0.68, 0.042), 0.07, 0.042, up=Z)
        foot(k, s * (XO - 0.05), -0.42)
        k.box("frame", (s * (XO - 0.05), 0.70, 0.07), (0.05, 0.06, 0.06), soft=0.004)
        k.cyl("rubber", (s * (XO - 0.02), 0.735, 0.062), 0.06, 0.035, axis="x", seg=36, soft=0.006)
        k.cyl("chrome", (s * (XO + 0.0), 0.735, 0.062), 0.02, 0.006, axis="x", seg=24)
    for y in (-0.42, 0.10, 0.62):
        k.bar("frame", (-(XO - 0.05) + 0.035, y, 0.042), ((XO - 0.05) - 0.035, y, 0.042), 0.05, 0.042, up=Z,
              cut0=((-(XO - 0.05) + 0.035, 0, 0), (1, 0, 0)), cut1=(((XO - 0.05) - 0.035, 0, 0), (1, 0, 0)), weld=True)
    # ---- the side housings: the hull of both drums and the back's foot, extruded; the drums' rings, the logo
    side = _hull(_circle(CL[:2], CL[2]) + _circle(CU[:2], CU[2]) + [(YR1, 0.85), (YR1, ZB + 0.03), (YR1 - 0.03, ZB),
                                                                   (-0.47, ZB), (-0.53, ZB + 0.05)])
    band = _hull(_circle(CL[:2], CL[2]) + _circle(CU[:2], CU[2]))
    xb = XO - 0.018                                     # the recessed triangle's face; the band stands proud of it
    for s in (1, -1):
        slab(k, "shroud", side, XI if s > 0 else -xb, xb if s > 0 else -XI, 0.02)
        slab(k, "shroud", band, xb - 0.01 if s > 0 else -XO, XO if s > 0 else -(xb - 0.01), 0.012)
        # the grey trim line along the band's lower edge, from the lower drum up to the upper (ref_04)
        (ly_, lz_, lr_), (uy_, uz_, ur_) = CL, CU
        ang = math.atan2(uz_ - lz_, uy_ - ly_) - math.pi / 2
        p0 = (ly_ + lr_ * math.cos(ang), lz_ + lr_ * math.sin(ang)); p1 = (uy_ + ur_ * math.cos(ang), uz_ + ur_ * math.sin(ang))
        k.bar("trim", (s * (XO - 0.004), p0[0] + 0.05, p0[1] + 0.05 * math.tan(ang + math.pi / 2)),
              (s * (XO - 0.004), p1[0] - 0.05, p1[1] - 0.05 * math.tan(ang + math.pi / 2)), 0.012, 0.012, up=(1, 0, 0))
        for (cy, cz, _), ro, ri in ((CL, 0.20, 0.15), (CU, 0.253, 0.155)):
            k.disc("ring", (s * (XO + 0.004), cy, cz), ro, ri, 0.008, axis="x", seg=64)
            k.cyl("shroud", (s * (XO + 0.002), cy, cz), ri, 0.004, axis="x", seg=48)
        for i, (dy, dz) in enumerate(((0.0, 0.0), (0.03, 0.03), (0.03, -0.03), (0.06, 0.0), (0.06, 0.06), (0.06, -0.06))):
            k.cyl("trim", (s * (XO + 0.0045), CL[0] + 0.02 + dy, CL[1] + dz), 0.008 - 0.0008 * i, 0.002, axis="x", seg=16)
        k.text("label", "StairMaster", (s * (xb + 0.0012), 0.235, 0.27), 0.05, rz=s * math.pi / 2, depth=0.0006)
        # the rest platform at the housing's foot, its red lip (ref_04: px 240-310, py 950-975)
        yp, zp = -0.70, 0.29                                # its front edge, its top
        k.box("tread", (s * (XI + XO) / 2, (yp - 0.47) / 2, zp - 0.015), ((XO - XI) - 0.01, -0.47 - yp, 0.03), soft=0.005)
        k.box("red", (s * (XI + XO) / 2, yp - 0.004, zp - 0.015), ((XO - XI) - 0.01, 0.008, 0.026), soft=0.002)
        for j in range(5):
            k.box("rubber", (s * (XI + XO) / 2, yp + 0.03 + j * 0.03, zp + 0.0005), ((XO - XI) - 0.03, 0.008, 0.002), soft=0.0)
    # ---- the top cap over the stair's head and the back wall, the full width
    cap = [(0.22, 1.13), (0.22, 1.215)] + [p for p in _circle(CU[:2], CU[2], 24, 120, 0)] + \
          [(YR1, 0.90), (YR1, ZB + 0.03), (YR1 - 0.03, ZB), (YR0, ZB), (YR0, 1.10)]
    slab(k, "shroud", cap, -XO + 0.02, XO - 0.02, 0.02)
    k.box("trim", (0.0, 0.222, 1.17), (2 * XI, 0.004, 0.012), soft=0.0)
    # ---- the staircase between the housings: the body's front is the steps (treads and risers), the grille under the
    # lowest; ribbed grip treads on each
    y0, z0, d, r = STEP
    st = [(y0, ZB), (y0, z0)]
    for i in range(NST):
        st += [(y0 + d * i, z0 + r * i), (y0 + d * (i + 1), z0 + r * i)]
        if i < NST - 1:
            st.append((y0 + d * (i + 1), z0 + r * (i + 1)))
    st += [(YR0 + 0.01, z0 + r * (NST - 1)), (YR0 + 0.01, ZB)]
    slab(k, "frame", st, -XI, XI, 0.003)
    for i in range(NST):
        yt, zt = y0 + d * i, z0 + r * i
        k.box("tread", (0.0, yt + d / 2, zt + 0.004), (2 * XI - 0.01, d - 0.01, 0.008), soft=0.002)
        for j in range(9):
            k.box("rubber", (0.0, yt + 0.02 + j * (d - 0.04) / 8, zt + 0.0095), (2 * XI - 0.03, 0.008, 0.003), soft=0.0)
        k.box("trim", (0.0, yt + 0.006, zt - 0.006), (2 * XI - 0.01, 0.012, 0.012), soft=0.002)        # the nosing
    for i in range(14):
        for j in range(3):
            k.box("hole", (-XI + 0.04 + i * (2 * XI - 0.08) / 13, y0 - 0.0005, ZB + 0.04 + j * 0.05), (0.025, 0.001, 0.03),
                  soft=0.0)
    # ---- the handrails, each side: the post off the housing's top, the C-loop, the upper rail to the bend, the grip
    # horn, the diagonal in to the mast; the heart-rate grips, the horns' end grips
    my, mz0, mz1 = MAST
    for s in (1, -1):
        x = s * XR
        k.sweep("rail", [(x, y, z) for y, z in POST], k.circle(0.02, 20), soft=0.0)
        k.cyl("plastic", (x, POST[0][0], POST[0][1] + 0.01), 0.032, 0.03, seg=24, soft=0.004)        # the boot
        k.sweep("rail", [(x, y, z) for y, z in LOOP], k.circle(0.019, 20), bend=0.07, soft=0.0)
        up = [(x, POST[1][0], POST[1][1]), (x, BEND[0], BEND[1])]
        k.sweep("rail", up, k.circle(0.02, 20), soft=0.0)
        k.tube("chrome", (x, -0.06, 1.583), (x, 0.03, 1.615), 0.0215, seg=24)                         # HR grip
        hx, hy, hz = HORN
        k.sweep("rail", [(x, BEND[0], BEND[1]), (s * 0.355, 0.33, 1.84), (s * hx, hy, hz)], k.circle(0.019, 20),
                bend=0.06, soft=0.0)
        k.cyl("rail", (s * hx, hy, hz + 0.01), 0.028, 0.05, seg=24, soft=0.008)
        k.sweep("rail", [(x, BEND[0], BEND[1]), (s * 0.20, 0.44, 1.64), (s * 0.06, my - 0.02, mz1)], k.circle(0.018, 20),
                bend=0.05, soft=0.0)
    # ---- the mast from the cap up to the knuckle, the cross arm with the cup holders, the console's neck and the
    # console tilted to the user
    k.bar("frame", (0.0, my, CU[1] + CU[2] - 0.03), (0.0, my - 0.02, mz1), 0.09, 0.07, up=(0, 1, 0))
    k.cyl("frame", (0.0, my - 0.02, mz1), 0.065, 0.12, axis="x", seg=32, soft=0.006)
    for s in (1, -1):                                   # the cup holders hung off the mast's sides (ref_10)
        k.box("frame", (s * 0.07, my - 0.02, 1.43), (0.05, 0.04, 0.03), soft=0.004)
        k.box("plastic", (s * 0.145, my - 0.04, 1.42), (0.10, 0.10, 0.11), soft=0.01)
        k.box("hole", (s * 0.145, my - 0.04, 1.4755), (0.08, 0.08, 0.002), soft=0.0)
    cy, cz, cw, chh, tilt = CON
    nb = (cy - 0.055, cz - 0.095)                       # into the console's back, near its lower edge
    k.bar("frame", (0.0, my - 0.02, mz1 + 0.05), (0.0, nb[0], nb[1]), 0.07, 0.06, up=(0, 1, 0))
    k.box("frame", (0.0, cy + 0.025 * math.cos(tilt), cz - 0.025 * math.sin(tilt)), (cw, 0.05, chh), rx=-tilt, soft=0.012)
    nrm = (0.0, -math.cos(tilt), math.sin(tilt))                    # the console face's normal, to the user
    def on_face(u, v, off=0.002):
        """A point on the console's face: u across, v up its face."""
        return (u, cy + nrm[1] * off + v * math.sin(tilt), cz + nrm[2] * off + v * math.cos(tilt))
    k.box("glass", on_face(0.0, 0.01, 0.0015), (cw - 0.02, 0.003, chh - 0.04), rx=-tilt, soft=0.0)
    for u, txt in ((-0.12, "15:00"), (-0.035, "55"), (0.04, "126"), (0.12, "150")):
        k.text("led", txt, on_face(u, 0.09, 0.0035), 0.026, rx=math.pi / 2 - tilt, rz=0.0, depth=0.0005)
    for i in range(8):
        k.box("led", on_face(-0.145, 0.04 - i * 0.017, 0.0035), (0.008, 0.001, 0.006), rx=-tilt, soft=0.0)
        k.box("led", on_face(0.145, 0.04 - i * 0.017, 0.0035), (0.008, 0.001, 0.006), rx=-tilt, soft=0.0)
    k.box("ledgreen", on_face(0.0, -0.04, 0.0035), (0.05, 0.001, 0.022), rx=-tilt, soft=0.0)
    k.box("ledred", on_face(0.0, -0.068, 0.0035), (0.05, 0.001, 0.022), rx=-tilt, soft=0.0)
    k.box("plastic", on_face(0.0, -0.125, 0.008), (0.12, 0.016, 0.02), rx=-tilt, soft=0.004)            # the key strip


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Climbing, mid-stride: standing on the second tread, the body upright with a slight lean to the console, the
    hands lightly on the posts' heart-rate grips; a short, a middle and a tall user."""
    y0, z0, d, r = STEP
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        ball = (0.0, y0 + d + 0.17, z0 + r + 0.012)
        out[label] = dict(H=H, ball=ball, face=(0, 1), sole=0, shank=8, thigh=4, trunk=8, neck=5, arm=168, forearm=118,
                          arm_out=24)
    return out

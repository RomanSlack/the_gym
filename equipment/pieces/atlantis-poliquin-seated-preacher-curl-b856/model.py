"""Atlantis Poliquin Seated Preacher Curl (B856), Pro Series, charcoal frame, red upholstery.

Built by eye from the one camera angle that exists of it (refs/: ref_01 the maker's render, ref_02 the same render
larger from the dealer: a three-quarter from the front right and above, the pad at its lowest), held to Atlantis's
115.1 x 122.7 x 98.7 cm (L x W x H). The page: seat height and pad height adjustable, used from either side (an angled
or a vertical curling surface), the seat removable for standing preacher curls, a support for dumbbells, storage horns.
Axes: metres, floor z = 0; the seated user sits at +y facing -y, straddling the spine, the arms over the pad's 45 deg
face; x+ = the user's left. Reading ref_02: the frame is a square of four posts seen corner on (the nearest post is
the user's front left); the pad's ridge runs across the user (along x), its big 45 deg face sloping down to -y toward
the camera, its near-vertical face behind it to +y; the saddle seat sits behind the pad (+y) with its nose to the pad;
the stepped tread plates (the dumbbell support) across the front under the 45 deg face; two horns out of the
front posts to -y, one out of the left side to +x (that is why W is 7 cm more than L).

DESIGN SPEC (gate 1)
1. Use. A preacher curl, dumbbells or an EZ bar. Seated (or standing, the seat pulled out) at +y facing -y: the chest on
   the back (near-vertical) face, the armpits over the cushioned ridge, the upper arms down the 45 deg face, the
   curl turning about the elbows near the face's lower edge, the weight going down and up in front of the face (-y).
   The other side (-y, facing +y): the chest on the 45 deg face, the arms down the near-vertical face (Poliquin's
   "vertical curling surface"), standing. The elbow is the joint; the pad holds the upper arm so only the elbow turns.
2. Moving parts. The pad post (inner tube) sliding in its sleeve, a pop pin (red knob, front face) through both, a
   star lock knob under it (takes the rattle out), a chrome barrel on the +x face; the seat post sliding in its
   sleeve, a red pop pin; the seat lifts out of its sleeve. No pivots: the user's elbow is the pivot.
3. Adjustments. Pad height: 9 holes 50 mm apart, the ridge 0.987 m (lowest, the maker's H) to 1.387 m. Seat height:
   6 holes 40 mm apart, top 0.48 to 0.68 m. Seat out: standing. (The maker gives no ranges: these are ours, sized
   for the fit below.)
4. Load path. The weight in the hands, the forearms about the elbows, the upper arms on the pad, the pad's A core,
   the inner post, the pop pin, the sleeve, the spine (two 2 x 3 in rails, top and bottom, through both sleeves),
   the side frames and the four posts on their round rubber feet. Bar at rest: on the two caps on the user's far
   side (P1 / P2 at -y for the seated user, P4 / P3 at +y for the vertical side); dumbbells at rest on the treads.
5. Fit range (fit(), the SETTINGS): the shoulder joint 3 cm behind and about 10 cm over the ridge, the upper arm
   along the 45 deg face (its centre ~4.5 cm off the cushion), the elbow at 90 deg mid curl.
   Seated (straddling the spine, the knees either side of the pad post): 1.55 m seat 0.60, pad hole 0, on the balls
   of the feet, thighs down 25 deg, trunk 30 deg; 1.78 m seat 0.56, hole 0, feet flat, thighs down 18 deg; 1.95 m
   seat 0.52, hole 1, feet flat. The pad's A bottom clears the thighs (2 cm for the middle user, the tightest).
   Standing (seat out, feet either side of the seat sleeve, the toes under the open +y side): 1.55 m hole 2 trunk
   35 deg; 1.78 m hole 5 trunk 40 deg; 1.95 m hole 8 trunk 35 deg.
6. Size. Ours 1.17 x 1.15 x 0.99 m (W x L x H) against 1.227 x 1.151 x 0.987: W 6 cm short (the +x horn length is a
   guess), the rest within 1 cm.
Structure: four 76 mm posts on round rubber feet, a urethane bar cradle on each top (long along y, a lip at each end so a
bar lying along x can't roll); 2 x 3 in rails: the two side frames (top and bottom rail along y) and the front (-y)
top and bottom rails between the front posts; the +y side open (the standing user's feet); the spine, top and bottom,
from the front rails through the pad sleeve to the seat sleeve; the pad: an A core (charcoal ends) with the 45 deg
cushion, the near-vertical cushion and a cushioned roll on the ridge, on its inner post; the saddle seat on its post;
the dumbbell support: three tread plates across the front stepping down toward the front left post, on stands off the
front top rail, where the dumbbells come down at the bottom of the curl; three chrome storage horns on bolted plates.
"""
import math

IN = 0.0254
LOOK = {
    "frame": dict(color=(0.07, 0.072, 0.077), rough=0.45, metal=0.3, coat=0.1, bump=(1400, 0.05)),    # charcoal
    "pad": dict(color=(0.50, 0.03, 0.035), rough=0.5, sheen=0.3, bump=(1500, 0.1)),                  # red vinyl
    "seam": dict(color=(0.33, 0.015, 0.02), rough=0.6, coat=0.0),
    "urethane": dict(color=(0.10, 0.10, 0.105), rough=0.55, coat=0.0),                               # cradles, caps
    "tread": dict(color=(0.05, 0.05, 0.052), rough=0.8, coat=0.0, bump=(90, 0.5)),
    "rubber": dict(color=(0.03, 0.03, 0.03), rough=0.85, coat=0.0, spec=0.2),
    "chrome": dict(color=(0.85, 0.85, 0.86), rough=0.08, metal=1.0, coat=0.0),
    "steel": dict(color=(0.55, 0.55, 0.57), rough=0.3, metal=1.0, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9, coat=0.0),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "redplastic": dict(color=(0.6, 0.03, 0.03), rough=0.35, coat=0.2),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "warn": dict(color=(0.7, 0.04, 0.03), rough=0.4, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
}
# the reference camera stands off the user's front left (+x, -y), high: azimuth 45
VIEWS = {"three_quarter": (45, 24, 1.0), "front": (0, 6, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (-140, 18, 1.0)}
DETAILS = {
    "detail_post": ((-0.40, -0.80, 0.80), (0.0, -0.12, 0.46), 40),       # the pad post: its pop pin and lock knob, the collar
    "detail_shelf": ((-0.80, -1.15, 1.00), (-0.15, -0.33, 0.40), 40),     # the dumbbell treads, a front horn, a cradle
}
FIT_VIEWS = ("side", "three_quarter")
SETTING_VIEWS = ("side",)

# ---- the frame
FOOT_H = 0.02                       # the rubber disc (12 mm) and the post's steel foot plate (8 mm)
PX, PY = 0.40, 0.375                # the posts' centres (ref_02: a square seen corner on)
POST = 0.076                        # 3 in square posts
POST_TOP = 0.515                    # the cradle on top: its trough 0.55, the lips 0.585 (a bar at rest under the pad's
                                    # lower edge, in reach of the seated user's straight arms)
RW, RH = 0.05, 0.076                # the rails, 2 x 3 in (w across, h tall)
ZL, ZU = 0.13, 0.30                 # the bottom and top rails' centres (ref_02: low under the horns, mid under the cradles)
# ---- the pad: an A on a post. C = the ridge roll's centre (y, z); the 45 deg face down to -y, the 80 deg face to +y
R0 = 0.987                          # the ridge's top at the lowest hole (the maker's H)
PAD_STEP, PAD_N = 0.05, 9
ROLL = 0.055                        # the ridge roll's radius (the armpits go over it)
PAD_TH = 0.07                       # cushion thickness
PAD_LEN = 0.68                      # along x (ref_02: about 0.85 x the post spacing)
L45, LV = 0.32, 0.26                # the two cushions' slant lengths below the roll
A45, AV = math.radians(45), math.radians(80)
S0 = 0.045                          # the cushions' top ends tuck under the roll
POST_Y = -0.10                      # the pad post under the A's middle
SLEEVE = 0.08                       # the pad sleeve (the inner post 0.064)
SLEEVE_Z = (0.055, 0.55)              # its top 11 cm under the pad at the lowest hole (ref_02: the knobs show)
PIN_Z = 0.51                        # the pad's pop pin on the sleeve, 4 cm under its top
# ---- the seat
SEAT_Y = 0.25                       # the seat sleeve: the hips 22 cm behind the shoulders (trunk 23-30 deg)
SEAT0, SEAT_STEP, SEAT_N = 0.48, 0.04, 6
SEAT_SLEEVE = 0.07
SEAT_SLEEVE_Z = (0.05, 0.35)
SEAT_PIN_Z = 0.31
SEAT_TH = 0.075
# ---- the dumbbell support: three treads across the front, stepping down toward the front left post (ref_02); their
# back edge at y -0.28, 1 cm in front of the tall seated user's shins, 5 cm under his knees (the photo's reach further
# back, over where the seated user's shins go: ours stop short of them)
TREADS = [(-0.356, -0.20, 0.50), (-0.27, -0.07, 0.45), (-0.12, 0.08, 0.40)]    # x0, x1, tread top
TREAD_Y = (-0.43, -0.28)

# the setting: pad hole, seat hole (None = the seat lifted out), the user fitted (None = the photo's state, no user)
SET = dict(pad=0, seat=0, user=None)
USERS = {"short": 1.55, "middle": 1.78, "tall": 1.95}
SETS = {
    "seated_short": dict(pad=0, seat=3, user=("short", "seated")),
    "seated_middle": dict(pad=0, seat=2, user=("middle", "seated")),
    "seated_tall": dict(pad=1, seat=1, user=("tall", "seated")),
    "standing_short": dict(pad=2, seat=None, user=("short", "standing")),
    "standing_middle": dict(pad=5, seat=None, user=("middle", "standing")),
    "standing_tall": dict(pad=8, seat=None, user=("tall", "standing")),
}
SETTINGS = tuple(SETS)
LEAN = {"seated": None, "standing": {"short": 35, "middle": 40, "tall": 35}}


def setting(name):
    SET.clear()
    SET.update(SETS[name])


def n45():
    return (-math.sin(A45), math.cos(A45))          # out of the 45 deg face (y, z): to -y and up


def t45():
    return (-math.cos(A45), -math.sin(A45))         # down the 45 deg face


def nv():
    return (math.sin(AV), math.cos(AV))             # out of the near-vertical face: to +y, a little up


def tv():
    return (math.cos(AV), -math.sin(AV))            # down it (its foot 4.5 cm further +y than its top: an A)


def ridge(j):
    return R0 + PAD_STEP * j


def core(R):
    """The A core's outline (y, z) under the cushions, and its bottom z: apex (where the two boards' planes meet),
    down the 45 deg board, across the flat bottom, up the near-vertical board."""
    C = (0.0, R - ROLL)
    off = ROLL - PAD_TH                             # the boards' planes: the cushions' inner faces
    a, b = n45(), nv()
    p1 = (C[0] + off * a[0], C[1] + off * a[1])
    p2 = (C[0] + off * b[0], C[1] + off * b[1])
    # the apex: p1 + s t45 = p2 + u tv
    t1, t2 = t45(), tv()
    det = t1[0] * (-t2[1]) - t1[1] * (-t2[0])
    s = ((p2[0] - p1[0]) * (-t2[1]) - (p2[1] - p1[1]) * (-t2[0])) / det
    apex = (p1[0] + s * t1[0], p1[1] + s * t1[1])
    B1 = (p1[0] + L45 * t1[0], p1[1] + L45 * t1[1])
    B2 = (p2[0] + LV * t2[0], p2[1] + LV * t2[1])
    zb = min(B1[1], B2[1]) - 0.012
    return C, [apex, B1, (B1[0], zb), (B2[0], zb), B2], zb


def foot(k, x, y):
    k.cyl("rubber", (x, y, 0.006), 0.07, 0.012, seg=36, soft=0.002)
    k.cyl("frame", (x, y, 0.016), 0.062, 0.008, seg=36, soft=0.001)
    for a in (45, 135, 225, 315):                   # the anchor holes round it (ref_02)
        r = 0.048
        k.cyl("hole", (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)), 0.0202), 0.006, 0.0006, seg=12, soft=0.0)


def cradle(k, x, y, holes=False):
    """The urethane bar cradle on a post top: long along y, a lip at each end, rubber pads in the trough (ref_02)."""
    z0 = POST_TOP
    k.box("urethane", (x, y, z0 + 0.0175), (0.095, 0.21, 0.035), soft=0.008)
    for s in (1, -1):
        k.box("urethane", (x, y + s * 0.085, z0 + 0.05), (0.095, 0.04, 0.04), soft=0.012)
    for s in (1, -1):
        k.box("rubber", (x, y + s * 0.03, z0 + 0.037), (0.075, 0.05, 0.004), soft=0.001)
    if holes:                                       # the far cradle has two holes in its trough (ref_02)
        for s in (1, -1):
            k.cyl("hole", (x, y + s * 0.03, z0 + 0.0396), 0.013, 0.0008, seg=20, soft=0.0)


def collar(k, y, z, w, wi):
    """The black plastic bushing on a sleeve's top (outer w): a square ring the inner post (wi) slides through."""
    a, b = wi / 2 + 0.0005, w / 2 + 0.004       # the ring's inner and outer half widths
    for s in (1, -1):
        k.box("plastic", (s * (a + b) / 2, y, z + 0.006), (b - a, 2 * b, 0.012), soft=0.002)
        k.box("plastic", (0, y + s * (a + b) / 2, z + 0.006), (2 * a, b - a, 0.012), soft=0.002)


def horn(k, at, d, z, mount):
    """A chrome storage horn welded to a plate bolted on a face: `at` the face point (x, y), d the way out (+-x / +-y)."""
    ax = "x" if d[0] else "y"
    px, py = at
    k.box("frame", (px + d[0] * 0.004, py + d[1] * 0.004, mount[0]),
          (0.008, 0.08, mount[1]) if ax == "x" else (0.08, 0.008, mount[1]), soft=0.001)
    for dz in mount[2]:
        k.bolt((px + d[0] * 0.008, py + d[1] * 0.008, dz), ("+" if d[0] + d[1] > 0 else "-") + ax, size=0.014)
    o = (px + d[0] * 0.008, py + d[1] * 0.008)
    k.disc("frame", (o[0] + d[0] * 0.006, o[1] + d[1] * 0.006, z), 0.05, 0.026, 0.012, axis=ax, seg=40)       # the collar
    e = (o[0] + d[0] * 0.25, o[1] + d[1] * 0.25)
    k.tube("chrome", (o[0], o[1], z), (e[0], e[1], z), 0.025, seg=32)
    k.cyl("plastic", (e[0] + d[0] * 0.005, e[1] + d[1] * 0.005, z), 0.026, 0.01, axis=ax, seg=32, soft=0.003)


def build(k):
    Z, X, Y = (0, 0, 1), (1, 0, 0), (0, 1, 0)
    h = POST / 2
    # ---- the four posts on their feet, a cradle on each
    posts = [(-PX, -PY), (PX, -PY), (PX, PY), (-PX, PY)]          # P1 front right, P2 front left, P3, P4 (the user's view)
    for i, (x, y) in enumerate(posts):
        foot(k, x, y)
        k.bar("frame", (x, y, FOOT_H), (x, y, POST_TOP), POST, POST, r=0.006, cut0=((0, 0, FOOT_H), Z), weld=True)
        cradle(k, x, y, holes=(i == 2))
    # ---- the side frames: a bottom and a top rail along y between each side's posts
    for s in (1, -1):
        x = s * PX
        for z in (ZL, ZU):
            k.bar("frame", (x, -PY + h, z), (x, PY - h, z), RW, RH, r=0.004,
                  cut0=((0, -PY + h, 0), Y), cut1=((0, PY - h, 0), Y), weld=True)
    # ---- the front (-y) rails between the front posts; the +y side is open (the standing user's feet)
    for z in (ZL, ZU):
        k.bar("frame", (-PX + h, -PY, z), (PX - h, -PY, z), RW, RH, r=0.004, up=Z,
              cut0=((-PX + h, 0, 0), X), cut1=((PX - h, 0, 0), X), weld=True)
    # ---- the two sleeves and the spine through them (top and bottom rails), from the front rails
    sy0, sy1 = SLEEVE_Z
    k.bar("frame", (0, POST_Y, sy0), (0, POST_Y, sy1), SLEEVE, SLEEVE, r=0.006)
    k.box("plastic", (0, POST_Y, sy0 - 0.004), (SLEEVE - 0.004, SLEEVE - 0.004, 0.008), soft=0.002)            # its end cap
    collar(k, POST_Y, sy1, SLEEVE, 0.064)
    q0, q1 = SEAT_SLEEVE_Z
    k.bar("frame", (0, SEAT_Y, q0), (0, SEAT_Y, q1), SEAT_SLEEVE, SEAT_SLEEVE, r=0.006)
    k.box("plastic", (0, SEAT_Y, q0 - 0.004), (SEAT_SLEEVE - 0.004, SEAT_SLEEVE - 0.004, 0.008), soft=0.002)
    collar(k, SEAT_Y, q1, SEAT_SLEEVE, 0.058)
    for z in (ZL, ZU):
        ya, yb = -PY + RW / 2, POST_Y - SLEEVE / 2
        k.bar("frame", (0, ya, z), (0, yb, z), RW, RH, r=0.004, cut0=((0, ya, 0), Y), cut1=((0, yb, 0), Y), weld=True)
        ya, yb = POST_Y + SLEEVE / 2, SEAT_Y - SEAT_SLEEVE / 2
        k.bar("frame", (0, ya, z), (0, yb, z), RW, RH, r=0.004, cut0=((0, ya, 0), Y), cut1=((0, yb, 0), Y), weld=True)
    # the pad's pop pin on the sleeve's front (-y) face, the star lock knob under it (both as in ref_02, between the seated
    # user's knees); the pin's short chrome barrel on the +x face (2.5 cm proud: clear of the left thigh)
    ys = POST_Y - SLEEVE / 2
    k.tube("steel", (0, POST_Y - 0.031, PIN_Z), (0, ys - 0.03, PIN_Z), 0.008, seg=16)                    # the pin
    k.cyl("steel", (0, ys - 0.015, PIN_Z), 0.012, 0.03, axis="y", seg=20, soft=0.001)
    k.cyl("redplastic", (0, ys - 0.04, PIN_Z), 0.019, 0.022, axis="y", seg=28, soft=0.005)
    k.cyl("steel", (0, ys - 0.01, PIN_Z - 0.045), 0.008, 0.02, axis="y", seg=16, soft=0.001)
    k.cyl("plastic", (0, ys - 0.032, PIN_Z - 0.045), 0.026, 0.024, axis="y", seg=10, soft=0.004)        # star knob
    xs = SLEEVE / 2
    k.cyl("chrome", (xs + 0.009, 0 + POST_Y, PIN_Z), 0.012, 0.018, axis="x", seg=24, soft=0.002)
    k.cyl("chrome", (xs + 0.021, POST_Y, PIN_Z), 0.014, 0.008, axis="x", seg=24, soft=0.003)
    # ---- the pad on its inner post, at its hole
    j = SET["pad"]
    R = ridge(j)
    C, outline, zb = core(R)
    k.slab("frame", outline, -PAD_LEN / 2 + 0.01, PAD_LEN / 2 - 0.01, 0.004, seg=3)
    ip = 0.064
    k.bar("steel", (0, POST_Y, zb - 0.60), (0, POST_Y, zb), ip, ip, r=0.004, cut1=((0, 0, zb), Z), weld=True)
    for i in range(PAD_N):                          # its holes: hole i at the pin when the post is at hole i
        zh = PIN_Z - PAD_STEP * i + PAD_STEP * j
        if zh > sy1 + 0.02 and zh < zb - 0.02:
            for s in (1, -1):
                k.cyl("hole", (0, POST_Y + s * (ip / 2 + 0.0003), zh), 0.006, 0.0008, axis="y", seg=14, soft=0.0)
    a, t = n45(), t45()
    l45 = L45 - S0                                  # each cushion starts S0 down from the roll's line, under the roll
    c45 = (0.0, C[0] + (ROLL - PAD_TH / 2) * a[0] + (S0 + l45 / 2) * t[0], C[1] + (ROLL - PAD_TH / 2) * a[1] + (S0 + l45 / 2) * t[1])
    k.shaped_pad("pad", [(-PAD_LEN / 2, -l45 / 2), (PAD_LEN / 2, -l45 / 2), (PAD_LEN / 2, l45 / 2), (-PAD_LEN / 2, l45 / 2)],
                 c45, (0, a[0], a[1]), (1, 0, 0), PAD_TH, r=0.03, cushion=0.025)
    b, u = nv(), tv()
    lv = LV - S0
    cv = (0.0, C[0] + (ROLL - PAD_TH / 2) * b[0] + (S0 + lv / 2) * u[0], C[1] + (ROLL - PAD_TH / 2) * b[1] + (S0 + lv / 2) * u[1])
    k.shaped_pad("pad", [(-PAD_LEN / 2, -lv / 2), (PAD_LEN / 2, -lv / 2), (PAD_LEN / 2, lv / 2), (-PAD_LEN / 2, lv / 2)],
                 cv, (0, b[0], b[1]), (1, 0, 0), PAD_TH, r=0.03, cushion=0.025)
    k.tube("pad", (-PAD_LEN / 2 + 0.012, C[0], C[1]), (PAD_LEN / 2 - 0.012, C[0], C[1]), ROLL, seg=40, soft=0.004)   # the roll
    for s in (1, -1):
        k.sweep("seam", [(s * (PAD_LEN / 2 - 0.012), C[0] + ROLL * math.cos(q), C[1] + ROLL * math.sin(q))
                         for q in [math.radians(d) for d in range(-10, 200, 15)]], k.circle(0.0016, 6), caps=False, soft=0)
    # ---- the seat: the saddle on its plate and post, at its hole (or lifted out: standing)
    if SET["seat"] is not None:
        st = SEAT0 + SEAT_STEP * SET["seat"]
        zp = st - SEAT_TH - 0.012                      # the seat plate's underside
        sp = 0.058
        k.bar("steel", (0, SEAT_Y, zp - 0.03 - 0.30), (0, SEAT_Y, zp - 0.03), sp, sp, r=0.004)
        k.box("frame", (0, SEAT_Y, zp - 0.015), (0.07, 0.07, 0.03), soft=0.002)        # the mounting block, welded
        k.box("frame", (0, SEAT_Y - 0.01, zp + 0.006), (0.16, 0.22, 0.012), soft=0.002)  # the seat plate
        for i in range(SEAT_N):
            zh = SEAT_PIN_Z - SEAT_STEP * i + SEAT_STEP * SET["seat"]
            if zh > q1 + 0.02 and zh < zp - 0.05:
                k.cyl("hole", (0, SEAT_Y + (sp / 2 + 0.0003), zh), 0.005, 0.0008, axis="y", seg=14, soft=0.0)
        # the saddle: wide at the back (+y), narrowing to its nose at the pad (ref_02)
        sad = [(-0.17, 0.12), (0.17, 0.12), (0.16, 0.04), (0.06, -0.06), (0.045, -0.13), (-0.045, -0.13), (-0.06, -0.06), (-0.16, 0.04)]
        k.shaped_pad("pad", sad, (0, SEAT_Y, st - SEAT_TH / 2), (0, 0, 1), (1, 0, 0), SEAT_TH,
                     r=0.04, cushion=0.02)
    else:
        k.box("plastic", (0, SEAT_Y, q1 + 0.0135), (SEAT_SLEEVE - 0.01, SEAT_SLEEVE - 0.01, 0.003), soft=0.001)   # empty
    yq = SEAT_Y + SEAT_SLEEVE / 2                   # the seat's pop pin on the sleeve's back face (the spine meets its front)
    if SET["seat"] is not None:
        k.tube("steel", (0, SEAT_Y + 0.028, SEAT_PIN_Z), (0, yq + 0.02, SEAT_PIN_Z), 0.007, seg=16)
    k.cyl("steel", (0, yq + 0.012, SEAT_PIN_Z), 0.01, 0.024, axis="y", seg=18, soft=0.001)
    k.cyl("redplastic", (0, yq + 0.034, SEAT_PIN_Z), 0.017, 0.02, axis="y", seg=28, soft=0.005)
    # ---- the dumbbell support: a stand off the front top rail up to each tread's rib, the tray and its rubber tread
    yc, dy = sum(TREAD_Y) / 2, TREAD_Y[1] - TREAD_Y[0]
    for i, (x0, x1, top) in enumerate(TREADS):
        xs_ = (-0.33, -0.17, -0.02)[i]                 # each stand clear of the tread above and of P1
        zb_ = ZU + RH / 2 - 0.004
        zt = top - 0.008 - 0.006 - 0.03                # under the rib
        k.bar("frame", (xs_, -PY, zb_), (xs_, -PY, zt), 0.04, 0.04, r=0.003, cut0=((0, 0, zb_), Z), weld=True)
        k.box("frame", (xs_, yc, zt + 0.015), (0.008, dy - 0.01, 0.03), soft=0.001)                  # the rib
        xm = (x0 + x1) / 2
        k.box("frame", (xm, yc, top - 0.011), (x1 - x0, dy, 0.006), soft=0.002)                          # the tray
        k.box("tread", (xm, yc, top - 0.004), (x1 - x0 - 0.006, dy - 0.006, 0.008), soft=0.003)
        for r_ in (-1, 1):                          # the tread's blocks, the name moulded between them
            k.box("rubber", (xm, yc + r_ * (dy / 2 - 0.025), top + 0.0005), (x1 - x0 - 0.03, 0.014, 0.002), soft=0.0)
        k.text("rubber", "ATLANTIS", (xm, yc, top + 0.001), 0.026, rx=0.0, depth=0.0015)
    # ---- the storage horns: one out of each front post to -y, one out of the left side frame to +x
    for x in (-PX, PX):
        horn(k, (x, -PY - h), (0, -1), 0.20, (0.20, 0.17, (0.135, 0.265)))
    horn(k, (PX + RW / 2, 0.10), (1, 0), 0.215, ((ZL + ZU) / 2, ZU - ZL + RH, (ZL, ZU)))
    # ---- the warning placard on P3's outer face (ref_02), the badge on the front top rail
    k.box("placard", (PX + h + 0.001, PY, 0.36), (0.002, 0.05, 0.22), soft=0.0)
    k.box("warn", (PX + h + 0.0022, PY, 0.46), (0.0005, 0.05, 0.02), soft=0.0)
    k.text("label", "ATLANTIS", (0.0, -PY - RW / 2 - 0.0005, ZU), 0.03, depth=0.0005)


# ---- the fit check (spec 5)
def _hip(pose):
    """The hip joint (y, z) for a pose (body.py's chain)."""
    H = pose["H"]
    f = -1.0                                        # facing -y
    so = (f * math.cos(math.radians(pose["sole"])), math.sin(math.radians(pose["sole"])))
    su = (-f * math.sin(math.radians(pose["sole"])), math.cos(math.radians(pose["sole"])))
    d = lambda a: (f * math.sin(math.radians(a)), math.cos(math.radians(a)))
    b = pose["ball"]
    ank = (b[1] - so[0] * 0.48 * 0.152 * H + su[0] * 0.039 * H, b[2] - so[1] * 0.48 * 0.152 * H + su[1] * 0.039 * H)
    kn = (ank[0] + d(pose["shank"])[0] * 0.246 * H, ank[1] + d(pose["shank"])[1] * 0.246 * H)
    hp = (kn[0] + d(pose["thigh"])[0] * 0.245 * H, kn[1] + d(pose["thigh"])[1] * 0.245 * H)
    return hp, kn


def fit():
    if not SET.get("user"):
        return {}
    label, mode = SET["user"]
    H = USERS[label]
    s = H / 1.78
    R = ridge(SET["pad"])
    C = (0.0, R - ROLL)
    sh_y = C[0] + 0.03                               # the shoulder joint 3 cm behind the ridge
    if mode == "seated":
        st = SEAT0 + SEAT_STEP * SET["seat"]
        hip = (SEAT_Y, st + 0.085 * s)
        sole = -25.0 if label == "short" else 0.0     # the short user on the balls of the feet
        pose = dict(H=H, ball=(0, 0, 0), face=(0, -1), sole=sole, shank=0.0, thigh=-90.0, stance=0.26)
        _, kn = _hip(pose)
        th = -math.degrees(math.acos(max(-1.0, min(1.0, (hip[1] - kn[1]) / (0.245 * H)))))
        pose["thigh"] = th
        hp, _ = _hip(pose)
        pose["ball"] = (0.0, hip[0] - hp[0], hip[1] - hp[1])
        trunk = math.degrees(math.asin((hip[0] - sh_y) / (0.288 * H)))
    else:
        trunk = LEAN["standing"][label]
        pose = dict(H=H, ball=(0, 0, 0), face=(0, -1), sole=0.0, shank=8.0, thigh=-4.0)
        hp, _ = _hip(pose)
        hip_y = sh_y + 0.288 * H * math.sin(math.radians(trunk))
        pose["ball"] = (0.0, hip_y - hp[0], 0.0)
        hip = (hip_y, hp[1])
    pose["trunk"] = trunk
    pose["neck"] = trunk - 25
    S = (hip[0] - 0.288 * H * math.sin(math.radians(trunk)), hip[1] + 0.288 * H * math.cos(math.radians(trunk)))
    # the upper arm along the 45 deg face: its centre ra off the cushion's face, the elbow at 90 deg mid curl
    a, t = n45(), t45()
    P0 = (C[0] + ROLL * a[0], C[1] + ROLL * a[1])     # on the cushion's outer face (tangent to the roll)
    dS = a[0] * (S[0] - P0[0]) + a[1] * (S[1] - P0[1])
    L = 0.186 * H
    ra = 0.042 * s
    # elbow = S + L (-sin q, cos q) in (y, z); its distance off the face = dS + L(-sin q a_y + cos q a_z)
    # with a = (-sin45, cos45): dS + L sin45 (sin q + cos q) = ra, sin q + cos q = sqrt2 sin(q + 45): the branch down the face
    k2 = (ra - dS) / (L * math.sin(A45))
    q = 135.0 - math.degrees(math.asin(max(-1.0, min(1.0, k2 / math.sqrt(2)))))
    E = (S[0] - L * math.sin(math.radians(q)), S[1] + L * math.cos(math.radians(q)))
    down = (E[0] - C[0]) * t[0] + (E[1] - C[1]) * t[1]
    print(f"fit {mode} {label} ({H} m): pad hole {SET['pad']} (ridge {R:.3f})"
          + (f", seat {SEAT0 + SEAT_STEP * SET['seat']:.2f}" if mode == "seated" else ", seat out")
          + f"; shoulder ({S[0]:.3f}, {S[1]:.3f}) {S[1] - R:+.3f} over the ridge, {dS:.3f} off the 45 deg face;"
          f" trunk {trunk:.0f} deg, thigh {pose['thigh']:.0f}; upper arm {q:.0f} deg (45 deg face = 135),"
          f" elbow {down:.2f} m down the face (its cushion {L45:.2f})", flush=True)
    pose.update(arm=q, forearm=q - 90.0, arm_out=6)
    return {label: pose}

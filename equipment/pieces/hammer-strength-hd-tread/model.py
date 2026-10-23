"""Hammer Strength HD Tread (PT-ST-01), the self-powered curved treadmill, High Wear Charcoal Grey.

Built by eye from the maker's renders (refs/: ref_02 the true side, ref_01 / ref_03 the three-quarters, ref_04 the
bridge and console square on, ref_05 / ref_06 the deck from behind, ref_08 the console, ref_09 the slats close, ref_10
the support arm, ref_11 the annotated sheet), held to Life Fitness's 66.6 x 34.7 x 63.7 in (169 x 88 x 161 cm), an 18 in
running surface and a 14 in step-up. Side-view numbers off ref_02 at 2.02 mm/px (the 161 cm height), as (y, z):
y = (px - 500) * 0.00202, z = (867 - py) * 0.00202.
Axes: metres, floor z = 0; the user runs facing +y toward the console; +x is the side ref_02 shows.
Structure: the two side frames following the deck's curve (rounded ends, the red pinstripe, the HAMMER STRENGTH mark)
on levellers at the back and the transport wheels under the front housing; the slatted belt between them in its curve
(rubber-topped slats over the drums at each end), the transport handle at the back; the front frame: a post each side
leaning forward, bolted to the side frame, arched over into the bridge with the console cradle and the LCD console;
the heavy-duty support arm each side, bolted to its post, with the curved brace under it.
"""
import math

LOOK = {
    "frame": dict(color=(0.045, 0.046, 0.05), rough=0.45, metal=0.35, coat=0.0, bump=(1200, 0.06)),   # Charcoal Grey
    "panel": dict(color=(0.04, 0.041, 0.044), rough=0.4, metal=0.3, coat=0.1, bump=(900, 0.04)),
    "slat": dict(color=(0.018, 0.018, 0.019), rough=0.8, coat=0.0, spec=0.25, bump=(2500, 0.15)),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "plastic": dict(color=(0.025, 0.025, 0.027), rough=0.45, coat=0.0),
    "red": dict(color=(0.45, 0.03, 0.02), rough=0.45, coat=0.0),
    "label": dict(color=(0.55, 0.55, 0.57), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "steel": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0),
    "lcd": dict(color=(0.42, 0.45, 0.38), rough=0.4, emit=0.35),
    "ink": dict(color=(0.02, 0.02, 0.02), rough=0.5),
}
VIEWS = {"three_quarter": (-40, 14, 1.0), "front": (180, 6, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (140, 16, 1.0)}
DETAILS = {
    "detail_deck": ((0.75, -1.25, 0.95), (0.0, -0.20, 0.36), 40),        # the slats, the side frame, the curve
    "detail_bridge": ((-0.70, -0.20, 1.75), (0.0, 0.70, 1.35), 45),      # the console, the bridge, an arm's bolts
}

S = 0.00202
XS0, XS1 = 0.245, 0.33              # the side frames' inner and outer faces (an 18 in belt between, ref_03)
DECK = [(-0.70, 0.40), (-0.61, 0.39), (-0.40, 0.362), (-0.20, 0.352), (0.0, 0.358), (0.17, 0.38), (0.39, 0.41),
        (0.61, 0.46), (0.70, 0.47)]   # the slats' top along the run (ref_02), its lowest the 14 in step-up
XP = XS1 + 0.035                    # the front posts (x), on the side frames' outer faces
POST = [(0.37, 0.07), (0.70, 1.33)] # a post from its foot up to where it arches over (ref_02: 667, 833 -> 833, 210 px)
ZBR, YBR = 1.455, 0.735             # the bridge across the top (ref_02: py 146)
XA = 0.42                           # the support arms (x), outside the posts: 88 cm overall
ARM = ((-0.15, 1.20), (0.66, 1.20)) # an arm's two ends (y, z) (ref_02: 425 -> 825 px, py 250-296)


def zs(y):
    """The slats' top at y (piecewise linear through DECK, smoothed by the many points)."""
    pts = DECK
    if y <= pts[0][0]:
        return pts[0][1]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return z0 + (z1 - z0) * t
    return pts[-1][1]


def build(k):
    Z = (0, 0, 1)
    UPX = (1, 0, 0)
    # ---- the side frames: the top edge riding just above the slats, the rounded ends, the flat foot; the red
    # pinstripes along the curve, the HAMMER STRENGTH mark (ref_02)
    top = [(y / 100, zs(y / 100) + 0.035) for y in range(-60, 71, 5)]
    prof = [(-0.60, 0.04), (-0.70, 0.09), (-0.78, 0.19), (-0.80, 0.29), (-0.77, 0.37), (-0.70, 0.43)] + top + \
           [(0.78, 0.50), (0.84, 0.47), (0.87, 0.41), (0.86, 0.34), (0.80, 0.29), (0.70, 0.26), (0.68, 0.04)]
    for s in (1, -1):
        k.sweep("panel", [(XS0 if s > 0 else -XS1, 0, 0), (XS1 if s > 0 else -XS0, 0, 0)], [(-y, z) for y, z in prof],
                up=Z, soft=0.012)
        for dz in (-0.045, -0.20):
            line = [(s * (XS1 + 0.0008), y / 100, zs(y / 100) + dz) for y in range(-62, 72, 4)]
            k.sweep("red", line, k.rect(0.0012, 0.0025, 0.0), up=UPX, soft=0.0)
        k.text("label", "HAMMER STRENGTH", (s * (XS1 + 0.0012), -0.02, 0.255), 0.045, rz=s * math.pi / 2, depth=0.0006)
        for y, z in ((-0.68, 0.33), (-0.69, 0.21), (0.76, 0.42), (0.77, 0.33)):
            k.bolt((s * XS1, y, z), "+x" if s > 0 else "-x", size=0.014)
    # the underbody between the frames, below the belt; the drums at the ends; the transport handle at the back
    under = [(-0.66, 0.06)] + [(y / 100, zs(y / 100) - 0.0235) for y in range(-66, 71, 2)] + [(0.70, 0.06)]   # the slats ride on it
    k.sweep("plastic", [(-XS0, 0, 0), (XS0, 0, 0)], [(-y, z) for y, z in under], up=Z, soft=0.004)
    for yd, r in ((-0.69, 0.09), (0.73, 0.085)):
        zd = zs(yd) - 0.012 - r
        k.tube("rubber", (-XS0, yd, zd), (XS0, yd, zd), r, seg=40, soft=0.004)
    k.tube("frame", (-XS0, -0.79, 0.22), (XS0, -0.79, 0.22), 0.016, seg=20)
    for s in (1, -1):
        k.box("frame", (s * (XS0 - 0.02), -0.77, 0.22), (0.04, 0.05, 0.05), soft=0.004)
    # ---- the slats: across the belt along its curve, each turned to the curve, with its grooved rubber top (ref_09)
    y = -0.66
    while y < 0.70:
        z = zs(y); dzdy = (zs(y + 0.01) - zs(y - 0.01)) / 0.02
        a = math.atan(dzdy)
        k.box("slat", (0.0, y, z - 0.012), (2 * XS0 - 0.006, 0.054, 0.024), rx=a, soft=0.003)
        for dy in (-0.012, 0.0, 0.012):                 # the fine grooves across the slat's top (ref_09)
            k.box("ink", (0.0, y + dy * math.cos(a), z + dy * math.sin(a) - 0.0001), (2 * XS0 - 0.03, 0.0025, 0.0004),
                  rx=a, soft=0.0)
        y += 0.0575
    # ---- the feet: levellers at the back, the transport wheels at the front housing
    for s in (1, -1):
        x = s * (XS0 + XS1) / 2
        k.cyl("steel", (x, -0.57, 0.03), 0.009, 0.03, seg=12)
        k.cyl("rubber", (x, -0.57, 0.007), 0.032, 0.014, seg=28, soft=0.003)
        k.cyl("rubber", (s * (XS1 + 0.022), 0.65, 0.04), 0.04, 0.03, axis="x", seg=32, soft=0.005)
        k.cyl("steel", (s * (XS1 + 0.004), 0.65, 0.04), 0.012, 0.008, axis="x", seg=16)
    # ---- the front frame: each post up from its foot beside the side frame, arching over into the bridge (one bent
    # tube, ref_04); the posts bolted to the frames' outer faces
    (y0, z0), (y1, z1) = POST
    path = [(-XP, y0, z0), (-XP, y1, z1), (-XP + 0.05, YBR, ZBR), (XP - 0.05, YBR, ZBR), (XP, y1, z1), (XP, y0, z0)]
    k.sweep("frame", path, k.rect(0.07, 0.07, 0.008), bend=0.13, up=(0, -0.2, 1))
    for s in (1, -1):
        k.box("plastic", (s * XP, y0 - 0.003, z0 - 0.036), (0.074, 0.076, 0.008), soft=0.002)
        for z in (0.30, 0.37):                          # two pairs through the post into the side frame (ref_02)
            yp = y0 + (z - z0) * (y1 - y0) / (z1 - z0)
            for dy in (-0.017, 0.017):
                k.bolt((s * (XP + 0.035), yp + dy, z), "+x" if s > 0 else "-x", size=0.016, nut=0.11)
    # the console cradle on the bridge (the phone holder), the LCD console tilted back to the runner (ref_04, ref_08)
    k.box("frame", (0.0, YBR - 0.02, ZBR + 0.04), (0.22, 0.09, 0.04), soft=0.006)
    tilt = math.radians(28)
    cc = (0.0, YBR + 0.0, ZBR + 0.14)
    k.box("plastic", cc, (0.13, 0.03, 0.21), rx=-tilt, soft=0.008)
    n = (0.0, -math.cos(tilt), math.sin(tilt)); u = (0.0, math.sin(tilt), math.cos(tilt))
    def on(a, v, off):
        return (a, cc[1] + n[1] * (0.015 + off) + u[1] * v, cc[2] + n[2] * (0.015 + off) + u[2] * v)
    k.box("lcd", on(0.0, 0.02, 0.001), (0.10, 0.002, 0.13), rx=-tilt, soft=0.0)
    for v, txt in ((0.06, "00:29"), (0.015, "2.94"), (-0.03, "54")):
        k.text("ink", txt, on(0.0, v, 0.0022), 0.022, rx=math.pi / 2 - tilt, depth=0.0003)
    for i in range(5):
        k.box("ink", on(-0.04 + i * 0.02, -0.075, 0.001), (0.012, 0.002, 0.012), rx=-tilt, soft=0.001)
    k.text("label", "HAMMER", on(0.0, 0.092, 0.001), 0.012, rx=math.pi / 2 - tilt, depth=0.0003)
    # ---- the support arms: a heavy box arm each side, bolted to its post, the curved brace under it into the post
    # (ref_02 / ref_10), the end caps and the mark
    (ya, za), (yb, zb) = ARM
    for s in (1, -1):
        x = s * XA
        k.bar("frame", (x, ya, za), (x, yb + 0.02, zb), 0.045, 0.09, up=Z)
        k.box("plastic", (x, ya - 0.004, za), (0.049, 0.008, 0.094), soft=0.002)
        k.sweep("frame", [(x, 0.12, za - 0.045), (x, 0.24, 1.07), (x, 0.36, 1.055), (x, 0.645, 1.055)],
                k.rect(0.04, 0.045, 0.005), bend=0.08, up=UPX)
        for y, z in ((0.60, 1.21), (0.66, 1.21), (0.605, 1.055), (0.635, 1.055)):
            k.bolt((s * (XA + 0.0225), y, z), "+x" if s > 0 else "-x", size=0.016)
        k.text("label", "HAMMER STRENGTH", (s * (XA + 0.0235), 0.40, za), 0.03, rz=s * math.pi / 2, depth=0.0005)


FIT_VIEWS = ("side", "three_quarter")


def fit():
    """Running in the curve's low middle, mid-stance, upright with the slight forward lean, the arms bent; a short, a
    middle and a tall user."""
    out = {}
    for label, H in (("short", 1.60), ("middle", 1.78), ("tall", 1.95)):
        out[label] = dict(H=H, ball=(0.0, -0.10, zs(-0.10) + 0.006), face=(0, 1), sole=0, shank=10, thigh=-6, trunk=8,
                          neck=4, arm=195, forearm=100, arm_out=8)
    return out

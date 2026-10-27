"""VersaClimber TS-Magnetic (TS-M), Black hood, Floor Mount (bolted to the ground): the variant Roman linked.

Built by eye from the maker's photos (refs/: ref_08 the floor-mount unit from its side, the pedals and the side rails
toward the camera; ref_14 the mast's face close up, the red VERSACLIMBER, a grip carriage; ref_01 / ref_02 / ref_03 the
free-standing unit (the pedals, the rails, the hood from the front three-quarter); ref_05-ref_07 the wall-mount from the
front, the tablet), held to the maker's 7 ft 10 in height. Side-view numbers off ref_08 at 3.27 mm/px (the 2.39 m height),
as (y, z): y = (460 - px) * 0.00327, z = (745 - py) * 0.00327.
DESIGN SPEC (gate 1, written 2026-10-25 for v004: the piece predates the gates)
1. Use. The user stands on the two pedals facing the mast, a grip in each hand, and climbs: each hand moves with the
   opposite foot (contralateral), the strokes as long or short as they choose, against the magnetic resistance.
2. Moving parts, each mass named: the mast, a box beam leaning back 15 deg, the chain track up its face; the pedal
   carriages riding the face, a tread out each side (heel cup, toe strap); the grip carriages riding the mast's SIDES
   (ref_14; v003 had them on the face, where the tablet's bracket would stop them), a straight grip out from each with
   its quick-release; the resistance unit under the hood at the top; the hip rails, one padded U clamped to the mast's
   back; the tablet on the face under the hood; the floor mount (flange, foot block, floor bar, brace).
3. Adjustments. The grips' height on their carriages (the quick-release), the stroke length (free), the resistance.
4. Load path. The feet and hands into the carriages, the chain, the resistance unit; the mast into the foot block and
   the brace, the flange bolted down, the floor bar's leveller behind.
5. Fit range. 1.55 / 1.78 / 1.95 m at mid-stroke (the pedals level at 0.44, where they pass), heels in the cups, the
   body leaning in parallel to the mast; the grips set 15 cm over the shoulders (no higher than 2.10, under the hood):
   1.83 / 2.02 / 2.10 m, elbows 86 / 72 / 59 deg, solved (reach.py). The default build is ref_08's stroke;
   climb_short / climb_middle / climb_tall each set the machine for its user.
6. Size. 2.39 m tall (7 ft 10 in), as above.
Axes: metres, floor z = 0; the user stands at -y facing +y, climbing up the mast's front face; the mast leans back
15 deg, away from the user.
Structure: the foot block bolted to the floor on its flange, the floor bar back from it to a leveller, the brace up to
the mast; the mast (a box beam) with the chain track up its front face, the red lettering on its stripe; the two pedal
carriages (each pedal out to its side, a tread with a heel cup and toe strap) and the two grip carriages on the mast's sides (each
straight grip out from it, quick-release, rubber-gripped); the padded side rails, one U bent round behind the mast and clamped
to its back; the tablet console on its bracket at the top of the face; the hood over the magnetic resistance unit at the
top's back.
"""
import math

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.06)),    # black
    "hood": dict(color=(0.014, 0.014, 0.015), rough=0.35, metal=0.0, coat=0.25),
    "steel": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0, aniso=0.3),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.08, metal=1.0, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "foam": dict(color=(0.016, 0.016, 0.017), rough=0.7, coat=0.0, bump=(2400, 0.12)),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "grey": dict(color=(0.12, 0.12, 0.13), rough=0.45, coat=0.0),
    "red": dict(color=(0.6, 0.03, 0.03), rough=0.4, coat=0.0),
    "label": dict(color=(0.8, 0.8, 0.8), rough=0.4, coat=0.0),
    "glass": dict(color=(0.004, 0.004, 0.005), rough=0.5, coat=0.0, spec=0.25),
    "screen": dict(color=(0.25, 0.55, 0.9), rough=0.4, emit=0.8),
    "screenw": dict(color=(0.75, 0.8, 0.85), rough=0.4, emit=0.7),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
}
VIEWS = {"three_quarter": (-35, 12, 1.0), "front": (0, 4, 1.0), "side": (90, 3, 1.0), "back_three_quarter": (145, 16, 1.0)}
DETAILS = {
    "detail_top": ((-0.75, -1.05, 2.30), (0.0, 0.42, 1.85), 45),          # the tablet, the grips, the hood
    "detail_pedals": ((0.85, -1.05, 0.75), (0.0, -0.02, 0.40), 45),       # the pedals, the carriages, the floor mount
}

S = 0.00327
LEAN = math.radians(15)             # the mast's lean back from vertical (ref_08: 180 px over 670)
MB = (0.016, 0.147)                 # the mast's axis at the top of the foot block (ref_08: 455, 700 px)
MTOP = 2.30                         # where the mast's axis ends inside the hood
MW, MD = 0.10, 0.085                # the mast: across, front to back
YBAR = 0.78                         # the floor bar's end (ref_08: px 220), the leveller near it
PEDALS = ((-1, 0.33), (1, 0.55))    # (side, tread height): contralateral, the right foot high (ref_08)
GRIPS = ((-1, 1.83), (1, 1.58))     # (side, height): the left hand high
ZR = 1.29                           # the side rails' bend behind the mast (ref_08: py 350)
ZT = 1.95                           # the tablet's centre (ref_08: py 150)


def ax(z):
    """The mast's axis (y) at height z."""
    return MB[0] + (z - MB[1]) * math.tan(LEAN)


def face(z, off=0.0):
    """A point on the mast's front face (y, z), `off` further out toward the user."""
    n = (-math.cos(LEAN), math.sin(LEAN))
    y = ax(z)
    return (y + n[0] * (MD / 2 + off), z + n[1] * (MD / 2 + off))


def build(k):
    Z = (0, 0, 1)
    up = (0, math.sin(LEAN), math.cos(LEAN))           # along the mast
    nrm = (0, -math.cos(LEAN), math.sin(LEAN))          # out of its front face
    tilt = LEAN
    # ---- the floor mount: the flange bolted down, the foot block the mast stands in, the floor bar back to the
    # leveller, the brace up to the mast (ref_08)
    k.box("frame", (0.0, -0.02, 0.006), (0.30, 0.26, 0.012), soft=0.003)
    for x in (-0.12, 0.12):
        for y in (-0.12, 0.08):
            k.bolt((x, y, 0.012), "+z", size=0.014)
    k.box("frame", (0.0, -0.02, 0.012 + (MB[1] - 0.012) / 2), (0.14, 0.16, MB[1] - 0.012), soft=0.006)
    k.bar("frame", (0.0, 0.06, 0.045), (0.0, YBAR, 0.045), 0.06, 0.06, up=Z, cut0=((0, 0.06, 0), (0, 1, 0)), weld=True)
    k.box("plastic", (0.0, YBAR + 0.004, 0.045), (0.064, 0.008, 0.064), soft=0.002)
    k.cyl("steel", (0.0, YBAR - 0.05, 0.012), 0.008, 0.024, seg=12)
    k.cyl("rubber", (0.0, YBAR - 0.05, 0.004), 0.025, 0.008, seg=24, soft=0.002)
    zb = 0.44
    k.bar("frame", (0.0, 0.36, 0.075), (0.0, ax(zb) + MD / 2 * math.cos(LEAN), zb), 0.035, 0.035, up=(1, 0, 0),
          cut0=((0, 0, 0.075), Z), weld=True)
    # ---- the mast: the box beam from the foot block up into the hood; the chain track up the front face, its
    # stripe and the red lettering (ref_14), the TS-M badge
    p0 = (0.0, ax(MB[1]), MB[1]); p1 = (0.0, ax(MTOP), MTOP)
    k.bar("frame", p0, p1, MW, MD, up=nrm)
    k.box("plastic", (0.0, *face(1.05, 0.0012)), (0.045, 0.0024, 1.55), rx=-tilt, soft=0.0)            # the stripe
    # (v005: a second stripe centred at 0.27 ran 0.47 m down through the floor; found placing it in the gym)
    for side in (-1, 1):
        k.box("steel", (side * 0.035, *face(1.05, 0.003)), (0.012, 0.006, 1.75), rx=-tilt, soft=0.0)    # the chains
        for i in range(70):
            k.box("frame", (side * 0.035, *face(0.22 + i * 0.025, 0.0065)), (0.010, 0.002, 0.008), rx=-tilt, soft=0.0)
    zl = 1.35
    for i, ch in enumerate("VERSACLIMBER"):
        k.text("red", ch, (0.0, *face(zl - i * 0.056, 0.0026)), 0.046, rx=math.pi / 2 - tilt, depth=0.0006)   # upright, stacked
    k.text("label", "TS-M", (0.0, *face(zl + 0.06, 0.0026)), 0.026, rx=math.pi / 2 - tilt, depth=0.0006)
    # ---- the pedal carriages: a block riding the face, a pedal arm out to its side, the tread (rubber), the heel cup
    # and the toe strap (ref_01)
    for side, zp in PEDALS:
        cy, cz = face(zp + 0.02, 0.03)
        k.box("frame", (side * 0.03, cy, cz), (0.05, 0.06, 0.16), rx=-tilt, soft=0.004)
        x0, x1 = side * 0.055, side * 0.16
        k.bar("frame", (x0, cy - 0.01, zp - 0.02), (x1, cy - 0.01, zp - 0.02), 0.04, 0.03, up=Z)
        ty = cy - 0.13
        k.box("grey", ((x0 + x1) / 2 + side * 0.01, ty, zp - 0.005), (0.12, 0.26, 0.02), soft=0.004)
        for j in range(8):
            k.box("rubber", ((x0 + x1) / 2 + side * 0.01, ty - 0.11 + j * 0.03, zp + 0.0065), (0.11, 0.01, 0.003), soft=0.0)
        k.box("grey", ((x0 + x1) / 2 + side * 0.01, ty - 0.13, zp + 0.035), (0.12, 0.012, 0.07), soft=0.003)
        k.box("frame", ((x0 + x1) / 2 + side * 0.01, cy - 0.04, zp + 0.045), (0.125, 0.03, 0.01), soft=0.003)
        for xs in (-1, 1):
            k.box("frame", ((x0 + x1) / 2 + side * 0.01 + xs * 0.061, cy - 0.04, zp + 0.022), (0.004, 0.03, 0.045), soft=0.0)
    # ---- the grip carriages, each riding its side of the mast (ref_14: the grips' shafts come out of the sides, clear
    # of the face and the tablet): a block on the side, the straight grip out from it, the rubber grip, the
    # quick-release knob on the block's front
    for side, zg in GRIPS:
        cy, cz = ax(zg), zg
        xs = side * (MW / 2 + 0.02)
        k.box("frame", (xs, cy, cz), (0.04, MD + 0.01, 0.14), rx=-tilt, soft=0.004)
        k.tube("chrome", (side * (MW / 2 + 0.04), cy, cz), (side * 0.30, cy, cz), 0.0125, seg=20)
        k.tube("rubber", (side * 0.17, cy, cz), (side * 0.295, cy, cz), 0.018, seg=24, soft=0.003)
        k.cyl("plastic", (side * 0.302, cy, cz), 0.022, 0.012, axis="x", seg=24, soft=0.003)
        k.cyl("plastic", (xs, cy - (MD + 0.01) / 2 * math.cos(tilt) - 0.01, cz + (MD + 0.01) / 2 * math.sin(tilt)), 0.012,
              0.02, axis="y", seg=20, soft=0.003)
    # ---- the padded side rails: one U bent round behind the mast, clamped to its back, both arms forward and down
    # to the user's side (ref_08), foam over the arms
    yb = ax(ZR) + MD / 2 / math.cos(LEAN)
    rail = [(-0.20, -0.14, 1.07), (-0.22, 0.10, 1.17), (-0.17, yb + 0.04, 1.27), (0.0, yb + 0.07, ZR),
            (0.17, yb + 0.04, 1.27), (0.22, 0.10, 1.17), (0.20, -0.14, 1.07)]
    k.sweep("frame", rail, k.circle(0.019, 20), bend=0.08, soft=0.0)
    k.box("frame", (0.0, yb + 0.035, ZR - 0.005), (0.08, 0.075, 0.06), soft=0.004)        # the clamp to the mast's back
    for s in (1, -1):
        k.sweep("foam", [(s * 0.214, 0.06, 1.155), (s * 0.20, -0.13, 1.073)], k.circle(0.027, 24), soft=0.006)
        k.cyl("plastic", (s * 0.20, -0.143, 1.067), 0.027, 0.012, axis="y", seg=24, soft=0.003)
    # ---- the tablet console on its bracket at the top of the face: the bezel, the screen with the climb graph
    yt, zt = face(ZT, 0.05)
    k.box("frame", (0.0, *face(ZT, 0.025)), (0.06, 0.05, 0.06), rx=-tilt, soft=0.004)
    k.box("frame", (0.0, yt, zt), (0.27, 0.025, 0.19), rx=-tilt - math.radians(10), soft=0.008)
    t2 = tilt + math.radians(10)
    fn = (0.0, -math.cos(t2), math.sin(t2)); fu = (0.0, math.sin(t2), math.cos(t2))
    def on(u, v, off):
        return (u, yt + fn[1] * (0.0125 + off) + fu[1] * v, zt + fn[2] * (0.0125 + off) + fu[2] * v)
    k.box("glass", on(0.0, 0.0, 0.0012), (0.25, 0.0024, 0.165), rx=-t2, soft=0.0)
    for i, h in enumerate((0.03, 0.05, 0.04, 0.07, 0.06, 0.09, 0.08, 0.1)):
        k.box("screen", on(-0.09 + i * 0.022, -0.06 + h / 2, 0.0029), (0.014, 0.001, h), rx=-t2, soft=0.0)
    for u, txt in ((0.05, "412"), (0.11, "86")):
        k.text("screenw", txt, on(u, 0.045, 0.003), 0.024, rx=math.pi / 2 - t2, depth=0.0004)
    # ---- the hood over the magnetic resistance unit at the top's back (ref_08: a rounded D, the mast's top in it)
    hood = [(ax(MTOP) - 0.06, 1.98), (ax(MTOP) - 0.035, 2.33), (ax(MTOP) + 0.02, 2.39), (ax(MTOP) + 0.13, 2.385),
            (ax(MTOP) + 0.20, 2.33), (ax(MTOP) + 0.22, 2.15), (ax(MTOP) + 0.17, 2.0), (ax(MTOP) + 0.06, 1.95)]
    k.sweep("hood", [(-0.105, 0, 0), (0.105, 0, 0)], [(-y, z) for y, z in hood], up=Z, soft=0.025)


FIT_VIEWS = ("side", "three_quarter")
SETTINGS = ("climb_short", "climb_middle", "climb_tall")
SETTING_VIEWS = ("side",)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()                           # the default build: the stroke as ref_08, no user
Z_MID = sum(z for _, z in PEDALS) / 2    # mid-stroke, where the pedals pass each other (ref_08's stroke: 0.44)
Z_GRIP_MAX = 2.10                         # the grips' carriages run up the mast's sides to under the hood


def _climb(H):
    """Mid-stroke (spec 5): (the pose, the arms, the grips' height). The feet on the level pedals, heels in the cups,
    the body leaning in parallel to the mast; the grips (their quick-release sets them on the carriage) where the hands
    meet them 15 cm over the shoulders, the elbows bent, the hands about the face (at the stroke's top the arms reach
    near straight)."""
    import reach
    cy, _ = face(Z_MID + 0.02, 0.03)
    ball = (0.0, cy - 0.26 + 0.73 * 0.152 * H + 0.01, Z_MID + 0.008)   # the heel against its cup
    pose = dict(H=H, ball=ball, face=(0, 1), sole=0, shank=14, thigh=11, trunk=14, neck=8, stance=0.23)
    zg = min(reach.shoulder(pose)[2] + 0.15, Z_GRIP_MAX)
    return pose, reach.reach(pose, (0.23, ax(zg), zg), elbow=110), zg


def setting(name):
    global PEDALS, GRIPS, SHOW
    label = name.split("_")[1]
    SHOW = (label,)
    _, _, zg = _climb(dict(USERS)[label])
    PEDALS = ((-1, Z_MID), (1, Z_MID))
    GRIPS = ((-1, zg), (1, zg))


def fit():
    """Climbing at mid-stroke, each user on their setting."""
    import reach
    out = {}
    for label, H in USERS:
        if label not in SHOW:
            continue
        pose, a, zg = _climb(H)
        sh = reach.shoulder(pose)
        print(f"fit {label}: the hands on the grips at {zg:.2f} m ({zg - sh[2]:+.2f} from the "
              f"shoulders), elbows {a['elbow']:.0f} deg (miss {a['err'] * 100:.1f} cm); the shoulders {face(sh[2])[0] - sh[1]:.2f} m off the mast's face",
              flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

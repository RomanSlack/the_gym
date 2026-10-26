"""Life Fitness Flexibility Trainer (refs/: ref_01 black, ref_02 silver: a base with a foot at each end (wheels on the
front one), a post up from the front foot curving back over the seat, a beam from the rear foot up under the seat
into the post's foot; on the beam the seat, low,
and behind it a backrest pad on a short post with foot pegs either side below it; on the tall post a pair of pegs at
seat height, a handle loop at the top with its ends curled toward the user, two stretch straps hanging, and the placard
of six stretches on top, facing the seat). The shop page refuses requests (HTTP 429): every size is an estimate off
the refs (about 1.30 m long, 0.70 m wide, 1.55 m to the placard). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Guided stretching: sitting on the seat facing the post, the placard's six stretches (hamstrings and calves with
   the feet on the post's pegs, the back and shoulders pulling on the loop, quads and hips against the backrest with a
   foot on its pegs), holding each.
2. Each mass named (ref_01): the base, a foot across at each end, wheels on the front one; the post, oval tube, up from the front
   foot and curving back over the seat; the beam, up from the rear foot, under the seat, into the post's foot; the seat on its support; the backrest pad on its post, foot pegs below it either side; the
   post's pegs (black grips); the handlebar across the post's top (bent tube, its ends swept back and curled down, foam on them); the straps
   on a bracket with their handles; the placard on a stalk and bracket, leaning back, its face up to the seat. Black.
3. Adjustments. None: the user moves (how far forward on the seat, which peg, which grip).
4. Load path. The body on the seat and against the pegs or pad, the hands on the loop; the beam and post, the feet.
5. Fit range. 1.55 / 1.78 / 1.95 m (sit_short / sit_middle / sit_tall): sitting on the seat facing the post, the hands on
   the loop's curls (reach.py; the elbows printed), the feet on the floor or hanging just clear for the short user.
6. Size. 0.70 x 1.30 x 1.55 m.
Axes: metres, floor z = 0; the post toward -y, the user on the seat facing -y.
"""
import math

Y_POST = -0.62                        # the front foot and the post's foot
Y_REAR = 0.62                         # the rear foot
Z_SEAT = 0.48
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()
GRIP = (0.28, -0.22, 1.10)            # the handlebar's foam ends (where the hands go)
TILT = math.radians(18)
TOP = (0.0, -0.42, 1.10)               # the post's top (the handlebar's middle)               # the placard leans back, its face up toward the seat

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.4, coat=0.2, bump=(900, 0.05)),
    "pad": dict(color=(0.02, 0.02, 0.022), rough=0.6, coat=0.0, spec=0.35, bump=(1500, 0.03)),
    "grip": dict(color=(0.015, 0.015, 0.016), rough=0.8, coat=0.0, bump=(2500, 0.2)),
    "wheel": dict(color=(0.03, 0.03, 0.032), rough=0.6, coat=0.0),
    "placard": dict(color=(0.05, 0.05, 0.055), rough=0.5, coat=0.0),
    "art": dict(color=(0.22, 0.22, 0.23), rough=0.5, coat=0.0),
    "strap": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, bump=(3000, 0.1)),
}
VIEWS = {"three_quarter": (-145, 22, 1.0), "front": (180, 8, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (-35, 18, 1.0)}
DETAILS = {
    "detail_top": ((-0.45, 0.45, 1.60), (0.0, -0.30, 1.20), 40),         # the loop, the placard, the straps
}
SETTINGS = ("sit_short", "sit_middle", "sit_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    oval = k.oval(0.085, 0.058, 20)                       # the main tube: oval, its long axis vertical in the frame's plane
    # the feet: a cross tube at each end, the front one on wheels
    for y in (Y_POST - 0.02, Y_REAR):
        k.bar("frame", (-0.32, y, 0.03), (0.32, y, 0.03), 0.06, 0.05, r=0.006)
        for sx in (1, -1):
            k.box("pad", (sx * 0.325, y, 0.03), (0.012, 0.062, 0.052), soft=0.004)                  # end caps
            if y == Y_REAR:
                k.box("pad", (sx * 0.27, y, 0.004), (0.07, 0.06, 0.008), soft=0.002)                  # rubber pads
            else:
                k.box("frame", (sx * 0.27, y - 0.035, 0.035), (0.03, 0.02, 0.04), soft=0.003)          # wheel bracket
                k.cyl("wheel", (sx * 0.27, y - 0.055, 0.035), 0.035, 0.028, axis="x", seg=28, soft=0.005)
    # the post: up from the front foot, then curving back over the seat's front (ref_01)
    post = [(0, Y_POST, 0.03), (0, Y_POST, 0.42), (0, Y_POST + 0.10, 0.82), (0, TOP[1], TOP[2])]
    k.sweep("frame", post, oval, bend=0.30, up=(0, 1, 0), soft=0.0)
    # the beam: up from the rear foot, along under the seat, into the post's foot
    beam = [(0, Y_REAR, 0.03), (0, 0.24, 0.27), (0, -0.22, 0.30), (0, Y_POST + 0.02, 0.36)]
    k.sweep("frame", beam, oval, bend=0.14, up=(0, 0, 1), soft=0.0)
    # the seat on its bracket
    k.box("frame", (0, 0.02, 0.37), (0.10, 0.14, 0.14), soft=0.004)
    k.box("frame", (0, 0.02, Z_SEAT - 0.072), (0.26, 0.26, 0.008), soft=0.002)
    k.box("pad", (0, 0.02, Z_SEAT - 0.035), (0.42, 0.38, 0.07), soft=0.03)
    # the back pad on its post, behind the seat
    k.sweep("frame", [(0, 0.36, 0.24), (0, 0.30, 0.62)], k.oval(0.05, 0.04, 16), up=(0, 1, 0), soft=0.0)
    k.box("frame", (0, 0.30, 0.625), (0.14, 0.06, 0.01), soft=0.002)
    k.box("pad", (0, 0.30, 0.665), (0.44, 0.14, 0.075), soft=0.032)
    # foot pegs: a bar through the beam behind the seat, and through the post at seat height
    for y, z in ((0.44, 0.19), (Y_POST, 0.50)):
        k.tube("frame", (-0.10, y, z), (0.10, y, z), 0.019, seg=16)
        for sx in (1, -1):
            k.tube("grip", (sx * 0.09, y, z), (sx * 0.25, y, z), 0.026, seg=20)
            k.cyl("pad", (sx * 0.255, y, z), 0.027, 0.012, axis="x", seg=20, soft=0.003)
    # the handlebar: across the post's top, each end swept back toward the seat and curled down, foam on the ends
    gx, gy, gz = GRIP
    tx, ty, tz = TOP
    for sx in (1, -1):
        bar = [(0, ty, tz), (sx * 0.20, ty - 0.02, tz + 0.02), (sx * gx, ty + 0.06, tz + 0.06), (sx * gx, gy, gz + 0.06),
               (sx * gx, gy + 0.05, gz - 0.04)]
        k.sweep("frame", bar, k.circle(0.0175, 16), bend=0.05, soft=0.0)
        k.tube("grip", (sx * gx, ty + 0.10, tz + 0.06), (sx * gx, gy - 0.005, gz + 0.06), 0.023, seg=20)
    # the straps: from a bracket under the post's top, hanging, a handle on each
    yb, zb = TOP[1] - 0.06, 0.98                        # on the post's curve, its seat side
    k.box("frame", (0, yb + 0.03, zb), (0.10, 0.05, 0.04), soft=0.003)
    for sx in (1, -1):
        x = sx * 0.035
        k.sweep("strap", [(x, yb + 0.05, zb - 0.01), (x, yb + 0.06, 0.66)], k.rect(0.02, 0.003, 0.001), up=(0, 1, 0), soft=0.0)
        k.sweep("strap", [(x, yb + 0.06, 0.67), (x - 0.035, yb + 0.06, 0.62), (x - 0.03, yb + 0.06, 0.56),
                          (x + 0.03, yb + 0.06, 0.56), (x + 0.035, yb + 0.06, 0.62), (x, yb + 0.06, 0.67)],
                k.circle(0.008, 10), bend=0.015, soft=0.0)
    # the placard: on a stalk above the handlebar, leaning back, its face (six stretches) up toward the seat
    pc = (0, TOP[1] - 0.04, 1.38)
    nb, vb = (math.cos(TILT), math.sin(TILT)), (-math.sin(TILT), math.cos(TILT))     # the plate's normal, up its face
    bc = (0, pc[1] - nb[0] * 0.012 - vb[0] * 0.03, pc[2] - nb[1] * 0.012 - vb[1] * 0.03)  # a bracket on the plate's back
    k.box("frame", bc, (0.07, 0.016, 0.10), rx=TILT, soft=0.003)
    bk = (0, bc[1] - nb[0] * 0.006, bc[2] - nb[1] * 0.006)
    k.tube("frame", (0, TOP[1], TOP[2] - 0.02), bk, 0.02, seg=16)                                   # the stalk up to it
    k.box("placard", pc, (0.40, 0.012, 0.27), rx=TILT, soft=0.008)       # top back, face up to the seat
    n = (0.0, math.cos(TILT), math.sin(TILT))          # its face's normal (toward the seat, tipped up)
    v = (0.0, -math.sin(TILT), math.cos(TILT))         # up its face
    for i in range(6):
        u, w = -0.13 + 0.13 * (i % 3), 0.045 - 0.10 * (i // 3)
        c = (u, pc[1] + v[1] * w + n[1] * 0.0065, pc[2] + v[2] * w + n[2] * 0.0065)
        k.box("art", c, (0.11, 0.004, 0.085), rx=TILT, soft=0.0)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        hip = (0.0, 0.06, Z_SEAT + 0.035 * Hu)         # the pelvis down on the seat           # sitting back on the seat
        zb = max(0.0, hip[2] - 0.285 * Hu)
        sole = 0 if zb == 0 else -25
        pose = dict(H=Hu, ball=(0.0, hip[1] - 0.245 * Hu - 0.07 * Hu, zb), face=(0, -1), sole=sole, shank=0, thigh=-90,
                    trunk=4, neck=-6, stance=0.22)    # sat up, reaching to the loop
        sh = reach.shoulder(pose)
        a = reach.reach(pose, (GRIP[0], GRIP[1] - 0.02, GRIP[2] + 0.06), elbow=150, low=3.0)
        print(f"fit {label}: seated, the hands on the loop's curls at {GRIP[2]:.2f} m, elbows {a['elbow']:.0f} deg "
              f"(miss {a['err'] * 100:.1f} cm); the feet {'on the floor' if zb == 0 else f'{zb:.2f} m off it'}",
              flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

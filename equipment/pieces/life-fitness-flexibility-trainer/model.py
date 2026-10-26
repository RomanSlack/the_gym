"""Life Fitness Flexibility Trainer (refs/: ref_01 black, ref_02 silver: a base with a foot at each end (wheels on the
front one), a beam from the rear foot running low forward and curving up into a tall post; on the beam the seat, low,
and behind it a backrest pad on a short post with foot pegs either side below it; on the tall post a pair of pegs at
seat height, a handle loop at the top with its ends curled toward the user, two stretch straps hanging, and the placard
of six stretches on top, facing the seat). The shop page refuses requests (HTTP 429): every size is an estimate off
the refs (about 1.45 m long, 0.70 m wide, 1.55 m to the placard). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Guided stretching: sitting on the seat facing the post, the placard's six stretches (hamstrings and calves with
   the feet on the post's pegs, the back and shoulders pulling on the loop, quads and hips against the backrest with a
   foot on its pegs), holding each.
2. Each mass named (ref_01): the base, a foot across at each end, wheels on the front one; the beam, oval tube, low then
   curving up into the post; the seat on its support; the backrest pad on its post, foot pegs below it either side; the
   post's pegs (black grips); the handle loop (bent tube, foam on its curls); the straps with their handles; the
   placard. Black.
3. Adjustments. None: the user moves (how far forward on the seat, which peg, which grip).
4. Load path. The body on the seat and against the pegs or pad, the hands on the loop; the beam and post, the feet.
5. Fit range. 1.55 / 1.78 / 1.95 m (sit_short / sit_middle / sit_tall): sitting on the seat facing the post, the hands on
   the loop's curls (reach.py; the elbows printed), the feet on the floor or hanging just clear for the short user.
6. Size. 0.70 x 1.45 x 1.55 m.
Axes: metres, floor z = 0; the post toward -y, the user on the seat facing -y.
"""
import math

Y_POST = -0.60
Z_SEAT = 0.48
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()
GRIP = (0.24, Y_POST + 0.15, 1.15)    # the loop's curled ends

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.4, coat=0.2, bump=(900, 0.05)),
    "pad": dict(color=(0.02, 0.02, 0.022), rough=0.6, coat=0.0, spec=0.35, bump=(1500, 0.03)),
    "grip": dict(color=(0.015, 0.015, 0.016), rough=0.8, coat=0.0, bump=(2500, 0.2)),
    "wheel": dict(color=(0.03, 0.03, 0.032), rough=0.6, coat=0.0),
    "placard": dict(color=(0.05, 0.05, 0.055), rough=0.5, coat=0.0),
    "art": dict(color=(0.45, 0.45, 0.46), rough=0.5, coat=0.0),
    "strap": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, bump=(3000, 0.1)),
}
VIEWS = {"three_quarter": (150, 18, 1.0), "front": (180, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (-35, 18, 1.0)}
DETAILS = {
    "detail_top": ((0.55, 0.45, 1.65), (0.0, Y_POST, 1.20), 40),         # the loop, the placard, the straps
}
SETTINGS = ("sit_short", "sit_middle", "sit_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    prof = k.oval(0.06, 0.05, 20)
    for y, wheels in ((0.72, False), (-0.68, True)):    # the feet
        k.bar("frame", (-0.33, y, 0.03), (0.33, y, 0.03), 0.05, 0.06, r=0.004)
        for sx in (1, -1):
            if wheels:
                k.cyl("wheel", (sx * 0.30, y - 0.05, 0.035), 0.035, 0.03, axis="x", seg=24, soft=0.004)
            k.box("pad", (sx * 0.31, y, 0.004), (0.06, 0.07, 0.008), soft=0.002)
    beam = [(0, 0.72, 0.06), (0, 0.40, 0.10), (0, -0.10, 0.18), (0, Y_POST + 0.02, 0.40), (0, Y_POST, 0.70),
            (0, Y_POST, 1.12)]
    k.sweep("frame", beam, prof, bend=0.18, soft=0.0)                                                # beam into post
    k.bar("frame", (0, Y_POST + 0.03, 0.03), (0, Y_POST + 0.03, 0.30), 0.05, 0.05, r=0.004)          # the post's foot
    k.bar("frame", (0, -0.68, 0.06), (0, Y_POST + 0.03, 0.06), 0.05, 0.05, r=0.004)
    # the seat
    k.bar("frame", (0, 0.10, 0.12), (0, 0.10, Z_SEAT - 0.07), 0.05, 0.05, r=0.004)
    k.box("frame", (0, 0.10, Z_SEAT - 0.07), (0.20, 0.20, 0.01), soft=0.002)
    k.box("pad", (0, 0.10, Z_SEAT - 0.035), (0.42, 0.40, 0.07), soft=0.03)
    # the backrest on its post, the foot pegs below it
    k.sweep("frame", [(0, 0.46, 0.08), (0, 0.42, 0.40), (0, 0.39, 0.56)], prof, bend=0.1, soft=0.0)
    k.box("pad", (0, 0.38, 0.60), (0.40, 0.12, 0.07), rx=math.radians(-15), soft=0.03)
    for sx in (1, -1):
        k.tube("frame", (0, 0.45, 0.20), (sx * 0.12, 0.45, 0.20), 0.022, seg=16)
        k.tube("grip", (sx * 0.12, 0.45, 0.20), (sx * 0.24, 0.45, 0.20), 0.026, seg=20)
        k.tube("frame", (0, Y_POST + 0.02, 0.48), (sx * 0.10, Y_POST + 0.02, 0.48), 0.022, seg=16)   # the post's pegs
        k.tube("grip", (sx * 0.10, Y_POST + 0.02, 0.48), (sx * 0.22, Y_POST + 0.02, 0.48), 0.026, seg=20)
    # the handle loop: up from the post, out, round toward the user, the curls foam
    gx, gy, gz = GRIP
    for sx in (1, -1):
        loop = [(0, Y_POST, 1.10), (sx * 0.20, Y_POST - 0.02, 1.16), (sx * gx, Y_POST + 0.02, 1.24),
                (sx * gx, gy, gz + 0.06), (sx * (gx - 0.03), gy + 0.04, gz)]
        k.sweep("frame", loop, k.circle(0.016, 16), bend=0.06, soft=0.0)
        k.tube("grip", (sx * gx, gy - 0.03, gz + 0.07), (sx * (gx - 0.03), gy + 0.04, gz - 0.005), 0.021, seg=20)
    # the straps hanging from the post's top, a handle on each
    for sx in (1, -1):
        x = sx * 0.035
        k.sweep("strap", [(x, Y_POST + 0.015, 1.08), (x, Y_POST + 0.06, 0.70)], k.rect(0.02, 0.003, 0.001), up=(0, 1, 0),
                soft=0.0)
        k.sweep("strap", [(x - 0.03, Y_POST + 0.06, 0.70), (x, Y_POST + 0.06, 0.62), (x + 0.03, Y_POST + 0.06, 0.70),
                          (x - 0.03, Y_POST + 0.06, 0.70)], k.rect(0.02, 0.004, 0.001), up=(0, 1, 0), bend=0.02,
                soft=0.0)
    # the placard on top, tilted to face the seat
    k.tube("frame", (0, Y_POST, 1.12), (0, Y_POST - 0.02, 1.41), 0.018, seg=16)      # into the placard
    a = math.radians(30)
    k.box("placard", (0, Y_POST - 0.02, 1.42), (0.36, 0.008, 0.24), rx=-a, soft=0.004)
    for i in range(6):                                  # its six stretches
        cx, cz = -0.11 + 0.11 * (i % 3), 1.47 - 0.10 * (i // 3)
        dz = cz - 1.42                                  # on the placard's face (its normal: +y tilted up by a)
        k.box("art", (cx, Y_POST - 0.02 + dz * math.sin(a) + 0.0045 * math.cos(a), 1.42 + dz * math.cos(a)
                      + 0.0045 * math.sin(a)), (0.08, 0.006, 0.07), rx=-a, soft=0.0)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        hip = (0.0, 0.16, Z_SEAT + 0.05 * Hu)           # sitting back on the seat
        zb = max(0.0, hip[2] - 0.285 * Hu)
        sole = 0 if zb == 0 else -25
        pose = dict(H=Hu, ball=(0.0, hip[1] - 0.245 * Hu - 0.07 * Hu, zb), face=(0, -1), sole=sole, shank=0, thigh=-90,
                    trunk=20, neck=-10, stance=0.22)   # leaning in to the loop
        sh = reach.shoulder(pose)
        a = reach.reach(pose, GRIP, elbow=150)
        print(f"fit {label}: seated, the hands on the loop's curls at {GRIP[2]:.2f} m, elbows {a['elbow']:.0f} deg "
              f"(miss {a['err'] * 100:.1f} cm); the feet {'on the floor' if zb == 0 else f'{zb:.2f} m off it'}",
              flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

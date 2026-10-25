"""Rogue Monster Landmine 2.0 (refs/: ref_01 / ref_05 on a Monster upright, low, the sleeve's mouth on the floor; ref_02
with a bar in it; ref_03 / ref_04 in use: a lifter holding the bar's far end, loaded, at the chest; ref_06 the unit
alone: the pin with its end cap and knurled collar and knob, the body, the clevis and its bolt, the sleeve). Fetched
2026-10-24 off the linked page. Built to the two gates and README point 9. Shown on one Monster upright on its base
plate (the rig's, not part of the piece).

DESIGN SPEC (gate 1)
1. Use. A barbell's end goes in the sleeve; the lifter works the far end (presses, rows, rotations, squats) while the
   near end pivots at the upright, up and down and side to side.
2. Each mass named (ref_06 / ref_05): the pin, through a low hole in the upright, its knurled collar against the near
   face and the knurled knob clamping it on the far face, the end cap; the body (machined, ROGUE on its side) turning
   on the pin on bronze bushings: the up-and-down pivot; the clevis on the body's end with its vertical bolt: the
   side-to-side pivot; the sleeve, a 2 in bore tube welded to the clevis, its mouth open.
3. Adjustments. The pin's hole (any hole up the upright; the lowest for presses, ref_01).
4. Load path. The bar's end in the sleeve, the clevis bolt, the body, the pin, the upright (the collar and the knob
   clamp it), the rig.
5. Fit range. 1.55 / 1.78 / 1.95 m at the start of a landmine press (press_short / press_middle / press_tall): a 2.2 m
   bar in the sleeve, a 10 kg green bumper on its far sleeve, both hands round the far sleeve's end beyond the plate
   (ref_03), at the front of the shoulders (0.78 H), elbows folded under it; the bar's angle per user (fit()).
6. Size. The unit 0.21 x 0.42 x 0.10 m at rest (the pin's length, the arm to the sleeve's mouth).
Axes: metres, floor z = 0; the upright at the origin, the sleeve toward +y (the lifter stands out at +y facing -y), the
pin along x, the body on the upright's +x side (ref_05).
"""
import math

IN = 0.0254
TB = 3 * IN
H_UP = 36 * IN                        # a section of the rig's upright, for display (capped; not part of the piece)
Z_PIN = 6.5 * IN + 0.0095             # the pin's hole over the base plate (ref_05: low)
X_BODY = TB / 2 + 0.035 + 0.03        # the body's mid-plane (x): past the collar, on the +x side (ref_05)
L_BODY, L_SLEEVE = 0.14, 0.28         # the pin to the clevis bolt, the sleeve's length
R_SL, R_BORE = 0.031, 0.026
REST = -math.asin((Z_PIN - R_SL) / (L_BODY + L_SLEEVE))    # at rest the sleeve's mouth on the floor
S_GRIP = 0.14 + 0.03 + 2.2 - 0.06      # the hands on the bar's far end, the plate just inside them (ref_03)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()
ANGLE = None                          # the arm's angle from level, None: at rest

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # the rig's upright
    "black": dict(color=(0.015, 0.015, 0.017), rough=0.3, metal=0.3, coat=0.2),                 # the landmine
    "machined": dict(color=(0.02, 0.02, 0.022), rough=0.25, metal=0.5, coat=0.3),
    "silver": dict(color=(0.06, 0.06, 0.065), rough=0.3, metal=0.7, coat=0.2),                  # the clevis (ref_05)
    "knurl": dict(color=(0.03, 0.03, 0.033), rough=0.5, metal=0.6, bump=(3000, 0.2)),
    "bronze": dict(color=(0.55, 0.32, 0.12), rough=0.3, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "steel": dict(color=(0.72, 0.72, 0.73), rough=0.2, metal=1.0),
    "p_green": dict(color=(0.02, 0.32, 0.05), rough=0.6, coat=0.0, spec=0.3),
}
VIEWS = {"three_quarter": (-145, 12, 0.8), "front": (180, 6, 1.0), "side": (-90, 4, 0.75), "back_three_quarter": (35, 16, 1.0),
         }
DETAILS = {
    "detail_pivot": ((0.40, 0.45, 0.35), (0.08, 0.10, 0.15), 40),       # the body, the clevis, the pin's collar
    "detail_ref": ((0.62, 0.62, 0.22), (0.06, 0.16, 0.13), 38),         # ref_05: low, the sleeve toward the camera
    "detail_knob": ((-0.35, 0.30, 0.30), (-0.05, 0.0, 0.17), 40),       # the far knob on the upright's other face
}
SETTINGS = ("press_short", "press_middle", "press_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW, ANGLE
    label = name.split("_")[1]
    SHOW = (label,)
    ANGLE = press_angle(dict(USERS)[label])


def press_angle(Hu):
    return math.asin((0.78 * Hu - Z_PIN) / S_GRIP)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    upright(k)
    landmine(k)
    if SHOW:
        bar(k)


def upright(k):
    bp = 0.0095
    k.box("frame", (0, 0, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)
    k.bar("frame", (0, 0, bp), (0, 0, H_UP), TB, TB, r=0.004)
    k.box("frame", (0, 0, H_UP + 0.0015), (TB - 0.001, TB - 0.001, 0.003), soft=0.001)
    for ax, sg in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
        z = 4 * IN
        while z < H_UP - 2 * IN:
            if not (ax == "x" and abs(z - Z_PIN) < 0.01):          # the pin's hole is filled by the pin
                c = (sg * (TB / 2 + 0.0003), 0, z) if ax == "x" else (0, sg * (TB / 2 + 0.0003), z)
                k.cyl("hole", c, 0.5 * IN, 0.0008, axis=ax, seg=14, soft=0.0)
            z += 2 * IN


def arm_dir():
    a = REST if ANGLE is None else ANGLE
    return (0.0, math.cos(a), math.sin(a)), a


def landmine(k):
    """The pin through the upright, the body on it, the clevis, the sleeve."""
    z = Z_PIN
    # the pin: the end cap, through the body, the bronze bushings, the collar, the upright, the far knob
    x0, x1 = X_BODY + 0.04, -TB / 2 - 0.035
    k.tube("steel", (x1 - 0.03, 0, z), (x0, 0, z), 0.0125, seg=24)
    k.cyl("black", (x0 + 0.008, 0, z), 0.022, 0.016, axis="x", seg=32, soft=0.003)               # the end cap
    for xb in (X_BODY - 0.031, X_BODY + 0.031):
        k.cyl("bronze", (xb, 0, z), 0.021, 0.003, axis="x", seg=32, soft=0.0005)
    k.cyl("knurl", (TB / 2 + 0.0175, 0, z), 0.026, 0.035, axis="x", seg=40, soft=0.002)           # the collar
    k.cyl("knurl", (-TB / 2 - 0.0175, 0, z), 0.026, 0.035, axis="x", seg=40, soft=0.002)          # the knob
    k.cyl("knurl", (-TB / 2 - 0.035 - 0.03, 0, z), 0.024, 0.02, axis="x", seg=40, soft=0.002)     # its handle end
    u, a = arm_dir()
    p = lambda s: (X_BODY, u[1] * s, z + u[2] * s)
    # the body: a machined block from round the pin out to the clevis, ROGUE on its outer side
    k.bar("machined", p(-0.025), p(L_BODY - 0.02), 0.059, 0.059, up=(1, 0, 0), r=0.006)
    k.text("label", "ROGUE", (X_BODY + 0.0298, *p(0.055)[1:]), 0.018, rz=math.pi / 2, spin=a, depth=0.0005)
    # the clevis: a plate each side of the body's end, its vertical bolt (the side-to-side pivot)
    for s in (1, -1):
        c = p(L_BODY - 0.01)
        k.box("silver", (X_BODY + s * 0.0335, c[1], c[2]), (0.008, 0.05, 0.062), rx=a, soft=0.002)
    nb = (0.0, -u[2], u[1])                              # the body's 'up', square to the arm
    c = p(L_BODY - 0.012)
    k.tube("bolt", (X_BODY, c[1] + nb[1] * 0.0285, c[2] + nb[2] * 0.0285), (X_BODY, c[1] + nb[1] * 0.0355,
           c[2] + nb[2] * 0.0355), 0.009, seg=20)
    # the sleeve: welded to the clevis, out to its open mouth
    k.tube("black", p(L_BODY), p(L_BODY + L_SLEEVE), R_SL, seg=40)
    k.tube("hole", p(L_BODY + L_SLEEVE - 0.04), p(L_BODY + L_SLEEVE + 0.0004), R_BORE, seg=32)


def bar(k):
    """The fit's barbell (not part of the piece): its near sleeve in the landmine's sleeve, the 10 kg green bumper on
    its far sleeve."""
    u, a = arm_dir()
    z = Z_PIN
    p = lambda s: (X_BODY, u[1] * s, z + u[2] * s)
    s0 = L_BODY + 0.03
    k.tube("steel", p(s0), p(s0 + 0.415), 0.0245, seg=28)                 # the near sleeve
    k.tube("steel", p(s0 + 0.415), p(s0 + 0.445), 0.026, seg=28)          # its collar
    k.tube("steel", p(s0 + 0.445), p(s0 + 1.755), 0.014, seg=24)          # the shaft
    k.tube("steel", p(s0 + 1.755), p(s0 + 1.785), 0.026, seg=28)
    k.tube("steel", p(s0 + 1.785), p(s0 + 2.2), 0.0245, seg=28)           # the far sleeve
    k.tube("p_green", p(s0 + 1.80), p(s0 + 1.83), 0.225, seg=72)          # the plate, square to the bar


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        a = press_angle(Hu)
        g = (X_BODY, S_GRIP * math.cos(a), Z_PIN + S_GRIP * math.sin(a))
        pose = dict(H=Hu, ball=(X_BODY, 0.0, 0.0), face=(0, -1), shank=4, thigh=0, trunk=-6, neck=0, stance=0.30)
        sh = reach.shoulder(pose)
        pose["ball"] = (X_BODY, g[1] + 0.17 - (sh[1] - 0.0) + 0.0, 0.0)        # the shoulders 17 cm behind the hands
        sh = reach.shoulder(pose)
        arms = reach.reach(pose, (X_BODY + 0.045, g[1], g[2]), elbow=45)
        print(f"fit {label}: the bar up {math.degrees(a):.0f} deg, the hands at {g[2]:.2f} m, {g[1]:.2f} m out; "
              f"elbows {arms['elbow']:.0f} deg (miss {arms['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=arms["arm"], forearm=arms["forearm"], arm_lat=arms["arm_lat"],
                          fore_lat=arms["fore_lat"])
    return out

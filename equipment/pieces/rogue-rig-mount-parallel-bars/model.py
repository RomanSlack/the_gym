"""Rogue Rig Mount Parallel Bars, a pair (refs/: ref_01 / ref_02 / ref_03 in a rig, an athlete dipping and in an L-sit;
ref_04 the bars and brackets from below; ref_05 a bracket on an upright: ROGUE cut through it, the two bolts). The linked
page: 69.5 in usable, 76.5 overall, 1.9 in schedule 40 pipe, 18.5 / 20 / 23 / 27.5 in centre to centre (the bottom bolt
in an arc of holes), four 5/16 in formed brackets, 5/8 in hardware, socket cap screws to the bars, textured black,
85 lb, for a 70 in rig depth. Fetched 2026-10-24 / 25. Built to the two gates and README point 9. Shown in a 43 in bay
of four 72 in sections of red Monster uprights (display only).

DESIGN SPEC (gate 1)
1. Use. Dips, L-sits, leg raises, walks along: the user supports their weight on straight arms between the two bars.
2. Each mass named (ref_04 / ref_05): the two bars, 1.9 in pipe, running the rig's depth from a front upright to a
   back one; at each end a bracket: a formed 5/16 in plate bolted to the upright's face toward the bar, tall at the
   upright and tapering in to the bar's end, a flange bent along its top, ROGUE cut through it; the bar's end held to
   the bracket's tip by socket cap screws through an end plate.
3. Adjustments. The height (the brackets' bolts by the hole, 2 in steps); the spacing: each bracket pivots on its top
   bolt, the bottom bolt in the arc's holes, 18.5 / 20 / 23 / 27.5 in centre to centre.
4. Load path. The hands on the bars, the end plates and screws, the brackets, their two bolts in shear, the uprights.
5. Fit range. 1.55 / 1.78 / 1.95 m in the top of a dip, arms straight, body upright, legs long (dip_short /
   dip_middle / dip_tall): the spacing the arc's nearest to the shoulders' width plus 7 cm, the height so the toes stay
   0.30 m clear for the descent (fit() prints both).
6. Size. 1.94 m long (76.5 in) over the brackets, 0.47-0.70 m wide by the setting.
Axes: metres, floor z = 0; the bars along y (the rig's depth), centred on x = 0.
"""
import math

IN = 0.0254
TB = 3 * IN
XU = (43 + 3) / 2 * IN                # the uprights' centres (x): a 43 in bay
YU = (70 + 3) / 2 * IN                # and (y): the rig's 70 in depth between faces
H_UP = 72 * IN
HOLE0, PITCH = 4 * IN, 2 * IN
SPACINGS = (18.5, 20, 23, 27.5)       # centre to centre (in)
R_BAR = 0.95 * IN
PB = 0.3125 * IN
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "frame": dict(color=(0.014, 0.014, 0.015), rough=0.55, coat=0.1, bump=(1600, 0.12)),        # textured black
    "upright": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),       # the rig's red
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 4, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_bracket": ((0.15, -0.35, 1.35), (-0.40, -0.85, 1.05), 40),  # ref_05: a bracket, its bolts, ROGUE
}
SETTINGS = ("dip_short", "dip_middle", "dip_tall")
SETTING_VIEWS = ("front",)
FIT_VIEWS = ("front", "three_quarter")


def hole_z(n):
    return HOLE0 + (n - 1) * PITCH


def setup(Hu):
    """(spacing in, hole): the spacing nearest the shoulders + 7 cm; the bars' hole for 0.30 m under the toes."""
    want = (0.259 * Hu + 0.07) / IN
    sp = min(SPACINGS, key=lambda s: abs(s - want))
    zb = 0.446 * Hu + 0.13 + 0.30                         # the toes 0.30 m clear at the top of the dip (toes pointed)
    n = max(1, round((zb - HOLE0) / PITCH) + 1)
    return sp, n


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    uprights(k)
    sp, n = setup(dict(USERS)[SHOW[0] if SHOW else "middle"])
    bars(k, sp * IN / 2, hole_z(n))


def uprights(k):
    bp = 0.0095
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * XU, sy * YU
            k.box("upright", (x, y, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)
            k.bar("upright", (x, y, bp), (x, y, H_UP), TB, TB, r=0.004)
            k.box("upright", (x, y, H_UP + 0.0015), (TB - 0.001, TB - 0.001, 0.003), soft=0.001)
            for ax, sg in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
                z = HOLE0
                while z < H_UP - 2 * IN:
                    c = (x + sg * (TB / 2 + 0.0003), y, z) if ax == "x" else (x, y + sg * (TB / 2 + 0.0003), z)
                    k.cyl("hole", c, 0.5 * IN, 0.0008, axis=ax, seg=14, soft=0.0)
                    z += PITCH


def bars(k, xb, zb):
    """Each bar at x = +-xb, its top zb: a bracket at each end on the upright's face toward it."""
    for sx in (1, -1):
        for sy in (1, -1):
            yp = sy * (YU - TB / 2 - PB / 2)               # the bracket's plane, on the upright's face
            xi = sx * (XU - TB / 2)                         # the upright's inner edge
            xt = sx * (xb - R_BAR - 0.01)                   # the bracket's tip, past the bar

            def plate(cx, cy, cz, xi=xi, xt=xt, yp=yp):
                at_up = (cx * sx > 0)
                x = sx * (XU + TB / 2 - 0.005) if at_up else xt
                z = (zb - 0.17 if cz < 0 else zb + 0.08) if at_up else (zb - 2 * R_BAR - 0.035 if cz < 0 else zb + 0.005)
                return (x, yp + cy * PB / 2, z)
            k.block("frame", plate, soft=0.0015)
            # the flange bent along its top edge, toward the bay
            k.block("frame", lambda cx, cy, cz, xi=xi, xt=xt, yp=yp: (
                sx * (XU - TB / 2) if cx * sx > 0 else xt, yp - sy * (PB / 2 + (0.03 if cy * sy < 0 else 0.0)),
                (zb + 0.08 - 0.004 + 0.004 * (cz > 0) if cx * sx > 0 else zb + 0.001 + 0.004 * (cz > 0))), soft=0.001)
            for zz in (zb + 0.04, zb - 0.09):              # its two bolts through the upright
                k.bolt((sx * XU, yp - sy * PB / 2, zz), "-y" if sy > 0 else "+y", size=0.016, nut=TB + PB)
            k.text("hole", "ROGUE", ((xi + xt) / 2 + sx * 0.02, yp - sy * (PB / 2 + 0.0003), zb - 0.03), 0.028,
                   rz=0.0 if sy > 0 else math.pi, depth=0.0006)
        # the bar between its brackets, its end plates and screws
        y0, y1 = -(YU - TB / 2 - PB), YU - TB / 2 - PB
        zc = zb - R_BAR
        k.tube("frame", (sx * xb, y0 + 0.008, zc), (sx * xb, y1 - 0.008, zc), R_BAR, seg=32)
        for y, sy in ((y0, -1), (y1, 1)):
            k.box("frame", (sx * xb, y - sy * 0.004, zc), (0.06, 0.008, 0.06), soft=0.002)
            for dx in (-0.018, 0.018):
                k.cyl("bolt", (sx * xb + dx, y - sy * 0.0085, zc), 0.005, 0.003, axis="y", seg=12, soft=0.001)


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    for label, Hu in USERS:
        sp, n = setup(Hu)
        zb = hole_z(n)
        print(f"fit {label}: the bars {sp} in apart on hole {n} (their tops {zb:.2f} m)", flush=True)
        if label not in SHOW:
            continue
        xb = sp * IN / 2
        pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, 1), sole=-50, shank=0, thigh=0, trunk=0, neck=0, stance=0.16)
        sh = reach.shoulder(pose)
        L = 0.372 * Hu
        lat = math.degrees(math.asin(max(-1, min(1, (xb - 0.1105 * Hu) / L))))
        pose["ball"] = (0.0, -sh[1], zb - (sh[2] - L * math.cos(math.radians(lat))))
        toes = pose["ball"][2] - 0.27 * 0.152 * Hu * math.sin(math.radians(50))
        print(f"fit {label}: supported at the top, the toes {toes:.2f} m clear", flush=True)
        a = reach.reach(pose, (xb, 0.0, zb), elbow=178)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

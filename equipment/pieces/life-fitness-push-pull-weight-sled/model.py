"""Life Fitness Push-Pull Weight Sled (refs/: ref_01 the sled in black: two skis turned up at both ends, a frame bolted
along them with two crossmembers and a spine, the chrome plate post at the middle, two black uprights in sockets at the
back, each with a loop handle outboard and two pegs inboard, short sockets at the front for the uprights the other way
round; ref_02 the same, the uprights picked out). The linked page gives no sizes (shop.lifefitness.com rate-limited
us, its cached record has the title, the price and the photos only): every size here is read off ref_01 against the
plate post (a 50 mm sleeve) and marked an estimate. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Sled pushes (hands on the loops, the body leaning in, driving with the legs) and pulls (a strap or harness on
   the front; the uprights can go in the front sockets).
2. Each mass named (ref_01): two skis, steel plate on edge, turned up at both ends (estimate 1.10 m long, 75 mm deep);
   a 50 mm square tube bolted along each; two crossmembers and a spine between them; the plate post, chrome, 50 mm, at
   the middle (estimate 0.42 m up); a socket at each tube's front end; two uprights, round black tube, standing in
   sockets at the back (estimate 1.00 m up), holes up their tops; on each a loop handle outboard (the high push grip,
   0.50-0.86 m up) and two pegs inboard (the low grips and band pegs). Black, the post chrome.
3. Adjustments. The uprights front or back; the load.
4. Load path. The hands on the loops, the uprights, the frame, the skis on the turf.
5. Fit range. 1.55 / 1.78 / 1.95 m (push_short / push_middle / push_tall): leaning in at about 45 degrees, the hands
   on the loops' outer bars at a height for each, the arms near straight (reach.py; the hands' height and the elbows
   printed).
6. Size. About 1.10 x 0.72 x 1.00 m (estimates).
Axes: metres, floor z = 0; the skis along y, the uprights at +y (the back), the pusher behind them facing -y.
"""
import math

SKI_L, SKI_H, SKI_T = 1.10, 0.075, 0.008
XS = 0.24                             # the skis' centres (x)
TUBE = 0.05
ZT = SKI_H + TUBE / 2                 # the frame tubes' centres
Y_UP = 0.42                           # the uprights' sockets (y)
R_UP = 0.024
H_UP = 1.00
R_POST = 0.025
H_POST = 0.42
LOOP = (0.50, 0.86, 0.12)             # the loop: bottom, top, out
PEGS = (0.60, 0.80)
USERS = (("short", 1.55), ("middle", 1.78), ("tall", 1.95))
SHOW = ()

LOOK = {
    "frame": dict(color=(0.010, 0.010, 0.011), rough=0.6, coat=0.0, bump=(900, 0.05)),
    "chrome": dict(color=(0.6, 0.6, 0.62), rough=0.15, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_frame": ((0.9, -0.9, 0.7), (0.0, 0.0, 0.12), 35),           # the skis, the frame, the post
    "detail_handle": ((0.9, 1.3, 1.1), (0.25, 0.38, 0.70), 35),        # an upright, its loop and pegs
}
SETTINGS = ("push_short", "push_middle", "push_tall")
SETTING_VIEWS = ("side",)
FIT_VIEWS = ("side", "three_quarter")


def setting(name):
    global SHOW
    SHOW = (name.split("_")[1],)


def ski(k, x):
    """A ski: a steel blade on edge along y, its running edge flat and turned up round a radius at both ends (ref_01)."""
    R, A = 0.16, math.radians(80)
    yf = SKI_L / 2 - R * math.sin(A)                    # where the turn-ups start
    low, high = [], []
    for s in (-1, 1):
        rng = range(13) if s > 0 else range(12, -1, -1)
        for i in rng:
            a = A * i / 12
            for rr, out in ((R, low), (R - SKI_H, high)):   # a strip SKI_H wide, both its edges round one centre
                out.append((s * (yf + rr * math.sin(a)), R - rr * math.cos(a)))
    outline = low + high[::-1]
    k.slab("frame", outline, x - SKI_T / 2, x + SKI_T / 2, 0.0015, seg=2)


def upright(k, x, y, s):
    """An upright in its socket, s = +1 / -1 for its side (the loop outboard)."""
    k.tube("frame", (x, y, ZT + TUBE / 2), (x, y, ZT + TUBE / 2 + 0.08), R_UP + 0.007, seg=24)     # the socket
    k.tube("frame", (x, y, ZT), (x, y, H_UP), R_UP, seg=24)
    for z in (H_UP - 0.06, H_UP - 0.11, H_UP - 0.16):   # its holes
        k.cyl("hole", (x, y - R_UP - 0.0003, z), 0.006, 0.0008, axis="y", seg=12, soft=0.0)
    lo, hi, out = LOOP
    k.sweep("frame", [(x + s * R_UP * 0.5, y, lo), (x + s * out, y, lo), (x + s * out, y, hi), (x + s * R_UP * 0.5, y, hi)],
            k.circle(0.016, 16), bend=0.04, soft=0.0)
    for z in PEGS:                                      # the pegs inboard
        k.tube("frame", (x - s * R_UP * 0.5, y, z), (x - s * 0.13, y, z), 0.016, seg=16)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for s in (1, -1):
        x = s * XS
        ski(k, x)
        k.bar("frame", (x, -0.45, ZT), (x, 0.45, ZT), TUBE, TUBE, r=0.003)                         # the frame tube
        for yb in (-0.30, -0.10, 0.10, 0.30):           # its bolts
            k.cyl("frame", (x + s * (TUBE / 2 + 0.002), yb, ZT), 0.007, 0.004, axis="x", seg=12, soft=0.001)
        k.tube("frame", (x, -Y_UP, ZT + TUBE / 2), (x, -Y_UP, ZT + TUBE / 2 + 0.06), R_UP + 0.007, seg=24)  # a front socket
        upright(k, x, Y_UP, s)
    for yc in (-0.14, 0.14):                            # the crossmembers
        k.bar("frame", (-XS, yc, ZT), (XS, yc, ZT), TUBE, TUBE, r=0.003)
    k.bar("frame", (0, -0.14, ZT), (0, 0.14, ZT), TUBE * 1.6, TUBE * 0.6, r=0.003)                 # the spine
    k.tube("chrome", (0, 0, ZT), (0, 0, H_POST), R_POST, seg=32)                                   # the plate post


# ---- the fit check (spec 5)
def fit():
    import reach
    out = {}
    lo, hi, o = LOOP
    for label, Hu in USERS:
        if label not in SHOW:
            continue
        zh = lo + (hi - lo) * (Hu - 1.40) / 0.70        # the hands higher up the loop for the taller
        lean = 45
        pose = dict(H=Hu, ball=(0.0, 0.0, 0.0), face=(0, -1), sole=-30, shank=lean + 10, thigh=lean - 20, trunk=lean + 5,
                    neck=-20, stance=0.30)
        sh = reach.shoulder(pose)
        xh = XS + o
        best = None
        for i in range(60):                             # stand back until the arms reach, near straight
            pose["ball"] = (0.0, Y_UP + 0.30 + i * 0.015 - sh[1], 0.0)
            a = reach.reach(pose, (xh, Y_UP, zh), elbow=165)
            c = a["err"] * 100 + abs(a["elbow"] - 165) / 30
            if best is None or c < best[0]:
                best = (c, pose["ball"], a)
        _, pose["ball"], a = best
        print(f"fit {label}: the hands on the loops at {zh:.2f} m, elbows {a['elbow']:.0f} deg "
              f"(miss {a['err'] * 100:.1f} cm)", flush=True)
        out[label] = dict(pose, arm=a["arm"], forearm=a["forearm"], arm_lat=a["arm_lat"], fore_lat=a["fore_lat"])
    return out

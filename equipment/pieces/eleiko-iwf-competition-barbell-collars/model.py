"""Eleiko IWF Competition Barbell Collars, a pair (refs/: ref_01 Eleiko's render of the pair, one lying on its plate
side, one standing: the cast spanner ring with its two swept wings, ELEIKO on a wing; the chrome body and its smooth
plate-side flange with the IWF badge; the locking lever with its black ball). Eleiko (search result text; the linked
page no longer renders): IWF certified and calibrated, a precision-cast body, 40 mm wide, the lever locking system that
holds the spanner when tightened. 2.5 kg each (a retailer's listing, Fringe Sport). Fetched 2026-10-25 (the one image,
by its article code). Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Slid onto a 50 mm sleeve against the plates, the spanner's wings turned by hand to clamp, the lever dropped to
   lock it; lifted off by the lever then the wings.
2. Each mass named (ref_01): the body, a chrome steel sleeve 50.5 mm inside; the flange on its plate side, a smooth
   chrome disc with the IWF badge; the spanner ring on its outer side, cast, textured, two wings swept back from it at
   opposite sides (ELEIKO cast on one: too small to draw); the lever on the body's side, a short chrome arm with a black ball, pivoting to lock
   the spanner.
3. Adjustments. The clamp (the spanner's turn); the lock.
4. Load path. The plates' push on the flange, the body, the clamp's friction on the sleeve.
5. Fit range. Turned by the hand's fingers on the wings (0.20 m tip to tip); nothing else to fit.
6. Size. 40 mm wide, the flange 100 mm across, the wings 0.21 m tip to tip.
Axes: metres, floor z = 0; one collar standing (its axis along x, the spanner toward -x), one lying plate side up,
as ref_01.
"""
import math

R_BORE = 0.02525
W = 0.040                             # the collar's width
R_FL, T_FL = 0.050, 0.012             # the plate-side flange
R_BODY = 0.042
R_SP, T_SP = 0.050, 0.014             # the spanner ring (as wide as the flange, ref_01)
R_WING = 0.100                        # the wings' tips

LOOK = {
    "chrome": dict(color=(0.82, 0.82, 0.83), rough=0.1, metal=1.0),
    "cast": dict(color=(0.62, 0.62, 0.63), rough=0.35, metal=1.0, bump=(2600, 0.12)),        # the textured casting
    "ball": dict(color=(0.012, 0.012, 0.013), rough=0.2, coat=0.6),
    "hole": dict(color=(0.03, 0.03, 0.03), rough=0.5),
    "badge": dict(color=(0.85, 0.85, 0.88), rough=0.4),
    "blue": dict(color=(0.02, 0.03, 0.25), rough=0.4),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (145, 22, 1.0)}
DETAILS = {
    "detail_ref": ((-0.24, -0.30, 0.17), (-0.03, 0.05, 0.045), 30),      # ref_01's angle
}


def collar(k, frame):
    """One collar in a frame: o (the plate side's centre), a (the axis out of the plate side), u, v (square to it)."""
    o, a, u, v = frame
    P = lambda s, du=0.0, dv=0.0: tuple(o[i] + a[i] * s + u[i] * du + v[i] * dv for i in range(3))
    ax = "x" if abs(a[0]) > 0.5 else ("y" if abs(a[1]) > 0.5 else "z")
    k.disc("chrome", P(T_FL / 2), R_FL, R_BORE, T_FL, axis=ax, seg=64, soft=0.002)                 # the flange
    k.disc("chrome", P(T_FL + (W - T_FL - T_SP) / 2), R_BODY, R_BORE, W - T_FL - T_SP + 0.001, axis=ax, seg=48, soft=0.001)
    k.disc("cast", P(W - T_SP / 2), R_SP, R_BORE + 0.004, T_SP, axis=ax, seg=48, soft=0.002)        # the spanner ring
    k.disc("chrome", P(W - 0.002), R_BORE + 0.006, R_BORE, 0.004, axis=ax, seg=40, soft=0.0005)     # its bore's lip
    # the wings: a broad tapered cast arm each side, swept out away from the plates at the tip (ref_01)
    for sg in (1, -1):
        def wing(cr, ct, ca, sg=sg):
            tip = cr > 0
            rr = R_WING if tip else R_SP - 0.006
            half_w = (0.009 if tip else 0.016) * ct
            th = 0.010 if tip else T_SP
            ac = (W - T_SP / 2 + 0.010) if tip else (W - T_SP / 2)
            return P(ac + ca * th / 2, sg * rr, half_w)
        k.block("cast", wing, soft=0.002)
    # the IWF badge on the flange's plate face
    k.disc("badge", P(-0.0004, 0.0, 0.036), 0.007, 0.0, 0.0008, axis=ax, seg=24, soft=0.0)
    k.disc("blue", P(-0.0009, 0.0, 0.036), 0.004, 0.0, 0.0006, axis=ax, seg=20, soft=0.0)
    # the lever: a pivot boss on the body's side, the arm, the black ball
    b = P(T_FL + 0.008, 0.0, R_BODY)
    k.sweep("chrome", [P(T_FL + 0.008, 0.0, R_BODY - 0.004), P(T_FL + 0.008, 0.0, R_BODY + 0.012),
                       P(T_FL + 0.008, 0.035, R_BODY + 0.030)], k.circle(0.0045, 12), bend=0.006, soft=0.0)
    k.sphere("ball", P(T_FL + 0.008, 0.041, R_BODY + 0.035), 0.0125, seg=32)
    k.cyl("chrome", b, 0.007, 0.012, axis=ax, seg=20, soft=0.001)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    # standing (ref_01, right): the spanner face toward -x and the camera, the wings steep, the lower wing's tip and the
    # flange's rim near the floor
    t = math.radians(35)
    zc = R_WING * math.sin(t) + 0.010 * math.cos(t) * 0.0
    collar(k, ((0.06, 0.0, zc), (-1, 0, 0), (0, math.cos(t), math.sin(t)), (0, -math.sin(t), math.cos(t))))
    # lying (ref_01, left): the plate side up (the IWF badge on top), on its wing tips
    collar(k, ((-0.13, 0.12, W + 0.008), (0, 0, -1), (1, 0, 0), (0, -1, 0)))

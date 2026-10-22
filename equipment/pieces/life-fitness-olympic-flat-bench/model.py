"""Life Fitness Signature Series Olympic Flat Bench (no storage), Charcoal frame / Black upholstery.

Built by eye from the listing's three-quarter photos (refs/: ref_01 charcoal, ref_03 the same in platinum, ref_02 the
storage version from behind), held to Life Fitness's 49 x 51 x 51 in (L x W x H).
Axes: metres, floor z = 0, the bench runs along x, the lifter's head at +x under the bar; y across.
Structure (ref_01): two uprights at the head end, rounded rectangular tube on rubber feet, joined low by a straight
cross tube and higher by a bent U tube whose bottom carries the bench beam (bolted between two plates welded on it);
the beam runs back under the pads to one tail leg on a rubber foot. The bar catches are on the uprights' faces towards
the lifter: a moulded urethane strip down each face, two hooks lined in urethane (the rack and a lower position).
No bar or plates: they're not part of the bench.
"""
LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),             # black vinyl
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "urethane": dict(color=(0.012, 0.012, 0.013), rough=0.62),                                        # moulded racking
    "plastic": dict(color=(0.02, 0.02, 0.021), rough=0.5),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_hooks": ((0.05, -0.85, 1.15), (0.46, -0.6, 0.95), 45),        # the bar catches on the near upright
    "detail_beam": ((0.2, -0.75, 0.45), (0.52, 0.0, 0.25), 40),           # the beam on the U tube's plates
    "detail_tail": ((-1.15, -0.55, 0.45), (-0.62, 0.0, 0.2), 45),         # the tail leg and its foot
}

UX, UY = 0.52, 0.60              # the uprights' centres (x, +-y)
UP = (0.10, 0.075)               # upright section: along x, across y (rounded rectangle)
U_TOP = 1.295                    # 51 in, the caps' tops
FOOT_T = 0.025                   # rubber feet
PAD_TOP, PAD_T, PAD_W = 0.445, 0.075, 0.30
MAIN = (-0.70, 0.185)            # the long pad (x from / to)
HEAD = (0.212, 0.47)              # the head pad
BEAM = (0.065, 0.10)             # beam: across (y) x tall
BEAM_TOP = PAD_TOP - PAD_T - 0.015   # under the pads' mounting plates
BEAM_X = (-0.73, UX)
TAIL_X = -0.60                   # the tail leg
TAIL = (0.06, 0.09)              # tail leg section: along x, across y
U_R = 0.034                      # the U tube (round)
U_FROM = 0.80                    # where it leaves the uprights (z)
LOW_Z = 0.15                     # the low cross tube
HOOKS = (1.08, 0.84)             # the hooks' cradle heights


def build(k):
    zb = BEAM_TOP - BEAM[1] / 2
    beam_bot = BEAM_TOP - BEAM[1]
    ux_face = UX - UP[0] / 2                                       # the uprights' faces towards the lifter
    for s in (1, -1):
        y = s * UY
        k.box("rubber", (UX, y, FOOT_T / 2), (0.15, 0.11, FOOT_T), soft=0.006)
        k.bar("frame", (UX, y, FOOT_T), (UX, y, U_TOP - 0.012), UP[0], UP[1], r=0.024, up=(0, 1, 0))
        k.box("plastic", (UX, y, U_TOP - 0.006), (UP[0] + 0.004, UP[1] + 0.004, 0.012), soft=0.004)
        catches(k, s, ux_face)
    yi = UY - UP[1] / 2                                            # the uprights' inner faces
    Y = (0, 1, 0)
    # the low cross tube, and the U tube, both welded into the uprights' inner faces
    k.bar("frame", (UX, -yi, LOW_Z), (UX, yi, LOW_Z), 0.05, 0.07, cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    uz = beam_bot - 0.008 - U_R                                    # the U's bottom: the beam sits on its plates
    k.sweep("frame", [(UX, -yi, U_FROM), (UX, -0.34, uz), (UX, 0.34, uz), (UX, yi, U_FROM)], k.circle(U_R, 24), bend=0.16,
            cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    # the beam's seat: a saddle plate on the U, two side plates up the beam's sides, two through-bolts
    k.box("frame", (UX, 0, beam_bot - 0.004), (0.12, BEAM[0] + 0.024, 0.008), soft=0.002)
    for s in (1, -1):
        k.box("frame", (UX - 0.01, s * (BEAM[0] / 2 + 0.005), beam_bot + 0.035), (0.13, 0.01, 0.085), soft=0.002)
    for bx in (UX - 0.05, UX + 0.03):
        k.bolt((bx, -(BEAM[0] / 2 + 0.01), zb - 0.01), "-y", size=0.012, nut=BEAM[0] + 0.02)
    # the beam, capped at the tail
    k.bar("frame", (BEAM_X[0], 0, zb), (BEAM_X[1], 0, zb), BEAM[1], BEAM[0], r=0.012, up=Y)
    k.box("plastic", (BEAM_X[0] - 0.004, 0, zb), (0.008, BEAM[0] + 0.004, BEAM[1] + 0.004), soft=0.003)
    # the tail leg welded under the beam, on its rubber foot; the LF badge on its tail face
    k.box("rubber", (TAIL_X, 0, FOOT_T / 2), (0.12, 0.15, FOOT_T), soft=0.006)
    k.bar("frame", (TAIL_X, 0, FOOT_T), (TAIL_X, 0, beam_bot), TAIL[0], TAIL[1], r=0.02, up=Y,
          cut1=((0, 0, beam_bot), (0, 0, 1)), weld=True)
    bx = TAIL_X - TAIL[0] / 2
    k.disc("label", (bx - 0.001, 0, 0.17), 0.026, 0.022, 0.002, axis="x")
    k.text("label", "LF", (bx - 0.0015, 0, 0.17), 0.026, rz=-1.5708, depth=0.001)
    # the pads on their mounting plates, bolted to the beam
    for x0, x1 in (MAIN, HEAD):
        L = x1 - x0; xc = (x0 + x1) / 2
        k.box("frame", (xc, 0, BEAM_TOP + 0.0075), (min(0.5, L - 0.08), 0.16, 0.015), soft=0.002)
        k.shaped_pad("pad", [(-L / 2, -PAD_W / 2), (L / 2, -PAD_W / 2), (L / 2, PAD_W / 2), (-L / 2, PAD_W / 2)],
                     (xc, 0, PAD_TOP - PAD_T / 2), (0, 0, 1), (1, 0, 0), PAD_T, r=0.04, cushion=0.03)


def catches(k, s, xf):
    """The bar catches on one upright's face towards the lifter: the urethane strip bolted down it, two hooks (a steel
    arm through the strip into the upright, a lip at its tip, all sleeved in urethane)."""
    y = s * UY
    st = 0.012
    k.box("urethane", (xf - st / 2, y, 0.96), (st, UP[1] - 0.012, 0.52), soft=0.004)
    for zz in (0.73, 1.18):
        k.bolt((xf - st, y, zz), "-x", size=0.01)
    for hz in HOOKS:
        arm = 0.085
        k.box("urethane", (xf - st - arm / 2, y, hz - 0.03), (arm, 0.055, 0.05), soft=0.008)              # the arm
        k.box("urethane", (xf - st - arm + 0.012, y, hz - 0.005 + 0.012), (0.024, 0.055, 0.045), soft=0.008)  # its lip
        k.box("urethane", (xf - st - 0.02, y, hz - 0.075), (0.04, 0.05, 0.05), rx=0, ry=0.785, soft=0.006)  # the gusset under it
        k.bolt((xf - st - 0.03, y - s * 0.0275, hz - 0.03), "-y" if s > 0 else "+y", size=0.01)

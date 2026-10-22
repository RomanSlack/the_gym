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
import kit

LOOK = {
    "frame": dict(color=(0.028, 0.029, 0.031), rough=0.5, metal=0.25, coat=0.0, bump=(1400, 0.07)),   # Charcoal powder coat
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),             # black vinyl
    "seam": dict(color=(0.006, 0.006, 0.006), rough=0.7),
    "urethane": dict(color=(0.008, 0.008, 0.009), rough=0.78, bump=(900, 0.05), coat=0.0),                                        # moulded racking
    "plastic": dict(color=(0.02, 0.02, 0.021), rough=0.5),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (-90, 4, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (140, 18, 1.0)}
DETAILS = {
    "detail_hooks": ((0.05, -0.85, 1.15), (0.46, -0.6, 0.95), 45),        # the bar catches on the near upright
    "detail_beam": ((0.0, -0.8, 0.5), (0.26, 0.0, 0.25), 38),            # the beam on the U, the low bracket
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
BEAM_X = (-0.73, UX - 0.19)       # it ends just past the U
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
    # the U tube (ref_01): out of each upright's inner face, swooping down and forwards (towards the tail) into a level
    # bottom under the head pad, which carries the beam's head end; welded into both uprights
    ux_u = UX - 0.24                                               # the U's bottom (x)
    uz = beam_bot - 0.008 - U_R                                    # its top meets the beam's saddle
    k.sweep("frame", [(UX, -yi, U_FROM), (ux_u, -0.30, uz), (ux_u, 0.30, uz), (UX, yi, U_FROM)], k.circle(U_R, 24), bend=0.16,
            cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    # the beam's seat on it: a saddle plate on the U, a plate up each side of the beam, two through-bolts
    k.box("frame", (ux_u, 0, beam_bot - 0.004), (0.10, BEAM[0] + 0.024, 0.008), soft=0.002)
    for s in (1, -1):
        k.box("frame", (ux_u, s * (BEAM[0] / 2 + 0.005), beam_bot + 0.035), (0.10, 0.01, 0.085), soft=0.002)
    for bx in (ux_u - 0.03, ux_u + 0.03):
        k.bolt((bx, -(BEAM[0] / 2 + 0.01), zb - 0.01), "-y", size=0.012, nut=BEAM[0] + 0.02)
    # low down: a tube from each upright in to a bracket under the bench, and a brace from the beam down to it (the
    # triangle under the pads in ref_01), the bracket's side plates through-bolted
    hx, hz, hw = UX - 0.30, LOW_Z + 0.02, 0.07                     # the bracket: a box tube across, its centre
    k.box("frame", (hx, 0, hz), (0.08, hw * 2, 0.09), soft=0.004)
    for s in (1, -1):
        k.bar("frame", (UX, s * yi, LOW_Z), (hx, s * hw, hz), 0.05, 0.06, up=(0, 0, 1),
              cut0=((0, s * yi, 0), Y), cut1=((0, s * hw, 0), Y), weld=True)
        k.box("frame", (hx, s * (hw + 0.005), hz), (0.10, 0.01, 0.11), soft=0.002)
        for bz in (hz - 0.03, hz + 0.03):
            k.bolt((hx + 0.025, s * (hw + 0.01), bz), "+y" if s > 0 else "-y", size=0.01)
    k.bar("frame", (hx - 0.04, 0, hz + 0.02), (-0.06, 0, beam_bot), 0.05, 0.05, up=Y,
          cut0=((hx - 0.04, 0, 0), (1, 0, 0)), cut1=((0, 0, beam_bot), (0, 0, 1)), weld=True)
    # the beam, capped at the tail
    k.bar("frame", (BEAM_X[0], 0, zb), (BEAM_X[1], 0, zb), BEAM[1], BEAM[0], r=0.012, up=Y)
    for bx, d in ((BEAM_X[0], -1), (BEAM_X[1], 1)):
        k.box("plastic", (bx + d * 0.004, 0, zb), (0.008, BEAM[0] + 0.004, BEAM[1] + 0.004), soft=0.003)
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
    k.box("urethane", (xf - st / 2, y, 0.96), (st, UP[1] - 0.026, 0.52), soft=0.004)
    for zz in (0.73, 1.18):
        k.bolt((xf - st, y, zz), "-x", size=0.01)
    for hz in HOOKS:
        # the hook: one moulded urethane J (side profile swept across the strip): a long underside rising from the strip
        # out to the lip, the lip, the round cradle the bar sits in, the back sloping up to the strip again
        prof = [(0.0, -0.10), (-0.080, -0.022), (-0.080, 0.028), (-0.058, 0.028), (-0.052, 0.006), (-0.040, -0.004),
                (-0.024, -0.004), (-0.012, 0.010), (0.0, 0.045)]
        prof = kit._round_poly(prof, 0.006, 3)
        x0 = xf - st
        k.sweep("urethane", [(x0, y - 0.028, hz), (x0, y + 0.028, hz)], prof, up=(0, 0, 1), soft=0.003)
        k.bolt((x0 - 0.03, y - s * 0.028, hz - 0.045), "-y" if s > 0 else "+y", size=0.01, nut=0.056)

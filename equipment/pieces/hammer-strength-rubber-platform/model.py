"""Hammer Strength Rubber Platform, 6 x 8 ft (the half rack insert variant), lying on the floor.

Built by eye from Hammer Strength's photos (refs/: ref_01 from above, the three pieces; ref_02 the fine ribbed top;
ref_03 a corner, its bevel; ref_04 the waffle underside), held to the spec: 3/4 in recycled rubber, 92 in along the bar,
72 in deep (the 4 x 8's 92 in, at the 6 ft depth).
Axes: metres, floor z = 0, the bar along x, the lifter faces -y.
Three pieces side by side along x (a quarter, a half, a quarter), locked by jigsaw tabs along the two seams, the outer
edges bevelled down to the floor. The insert's cut-outs for the rack's uprights are not in the photos: left out.
"""
import kit

IN = 0.0254
LOOK = {
    "rubber": dict(color=(0.026, 0.028, 0.030), rough=0.85, coat=0.0, spec=0.15, bump=(2400, 0.10)),   # dark slate, fine rib
}
VIEWS = {"three_quarter": (-35, 32, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "top": (0, 89, 1.0)}
DETAILS = {"detail_seam": ((-0.20, -1.25, 0.40), (-0.58, -0.80, 0.0), 45)}   # a seam's tabs reaching the bevelled edge

LX, LY = 92 * IN, 72 * IN
T = 0.75 * IN
BEV = 1.0 * IN                 # the bevel's run at the outer edges
SEAMS = (-LX / 4, LX / 4)      # quarter, half, quarter
TAB, NECK, PITCH = 0.022, 0.014, 0.060   # the jigsaw: tab depth, its neck's half width, tab spacing
CUT = 0.0008                   # each side of a seam stands back this far: the cut shows as a dark line


@kit._part
def slab(k, mat, base, top, z0, z1):
    """A prism from a floor outline to a top outline (same vertex count): one rubber piece."""
    b = k.bm(mat, 0.0008)
    lo = [b.verts.new((x, y, z0)) for x, y in base]
    hi = [b.verts.new((x, y, z1)) for x, y in top]
    n = len(base)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((lo[i], lo[j], hi[j], hi[i]))
    b.faces.new(lo[::-1]); b.faces.new(hi)


def seam(x0, back=0.0):
    """The jigsaw line at x0 from the front edge to the back, as (x, y) points."""
    pts, run = [], LY - 4 * BEV          # clear of the bevels at both ends
    n = int(run / PITCH)
    step = run / n
    for i in range(n):
        yc = -run / 2 + (i + 0.5) * step
        d = TAB * (1 if i % 2 else -1)                   # alternate: a tab one way, then the other
        x0b = x0 + back
        pts += [(x0b, yc - NECK * 0.7), (x0b + d * 0.55, yc - NECK * 0.6), (x0b + d, yc - NECK * 1.1),
                (x0b + d, yc + NECK * 1.1), (x0b + d * 0.55, yc + NECK * 0.6), (x0b, yc + NECK * 0.7)]
    return pts


def build(k):
    edges = [-LX / 2] + list(SEAMS) + [LX / 2]
    for i in range(3):
        xl, xr = edges[i], edges[i + 1]
        # the outline anticlockwise: front edge, the right side (seam or outer), the back, the left side
        right = seam(xr, -CUT) if i < 2 else []
        left = list(reversed(seam(xl, CUT))) if i > 0 else []
        xl_, xr_ = xl + (CUT if i > 0 else 0.0), xr - (CUT if i < 2 else 0.0)
        base = [(xl_, -LY / 2), (xr_, -LY / 2)] + right + [(xr_, LY / 2), (xl_, LY / 2)] + left
        top = []
        for x, y in base:   # the top: the outer edges pulled in by the bevel, the seams straight down
            if abs(abs(x) - LX / 2) < 1e-6:
                x -= BEV if x > 0 else -BEV
            if abs(abs(y) - LY / 2) < 1e-6:
                y -= BEV if y > 0 else -BEV
            top.append((x, y))
        slab(k, "rubber", base, top, 0.0, T)

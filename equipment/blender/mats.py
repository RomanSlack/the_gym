"""Exercise mats: a mat lying flat or hanging by its grommets, and one rolled up standing on end. A mat is L long,
W wide, T thick, its corners rounded; two grommets at one end (the hanging end)."""
import math
import kit as _kit


def outline(L, W, rc, n=8):
    """The mat's plan, corners rounded by rc, centred (u along L, v along W)."""
    pts = []
    for cu, cv, a0 in ((L / 2 - rc, W / 2 - rc, 0), (-L / 2 + rc, W / 2 - rc, 90), (-L / 2 + rc, -W / 2 + rc, 180),
                       (L / 2 - rc, -W / 2 + rc, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cu + rc * math.cos(a), cv + rc * math.sin(a)))
    return pts


def grommets(L, W):
    """The two grommets' (u, v): 45 mm in from the hanging end (+u), 50 mm in from the sides."""
    return [(L / 2 - 0.045, s * (W / 2 - 0.05)) for s in (1, -1)]


def flat(k, body, ring, c, L, W, T, rz=0.0, rc=0.03, under=None):
    """A mat lying flat at c (its middle on the floor), along x turned by rz; under: a role for a thin layer of another
    colour under it (the core mats' grey)."""
    ca, sa = math.cos(rz), math.sin(rz)

    def xy(u, v):
        return (c[0] + u * ca - v * sa, c[1] + u * sa + v * ca)
    pts = [xy(u, v) for u, v in outline(L, W, rc)]
    if under:
        _plate(k, under, pts, c[2], c[2] + T * 0.3)
        _plate(k, body, pts, c[2] + T * 0.3 - 0.0005, c[2] + T)
    else:
        _plate(k, body, pts, c[2], c[2] + T)
    for u, v in grommets(L, W):
        p = xy(u, v)
        k.disc(ring, (p[0], p[1], c[2] + T / 2), 0.011, 0.006, T + 0.002, axis="z", seg=24, soft=0.0)


@_kit._part
def _plate(k, role, pts, z0, z1):
    """A flat plate from a plan outline (convex enough) between z0 and z1 (one part for the floating check)."""
    b = k.bm(role, 0.0)
    lo = [b.verts.new((x, y, z0)) for x, y in pts]
    hi = [b.verts.new((x, y, z1)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        b.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    b.faces.new(lo[::-1])
    b.faces.new(hi)


def hanging(k, body, ring, x0, y_wall, z_top, L, W, T, rc=0.03):
    """A mat hanging flat against a wall (its back at y_wall, facing -y), its grommet end up at z_top, centred on x0."""
    _hang(k, body, x0, y_wall, z_top, L, W, T, rc)
    for u, v in grommets(L, W):
        k.disc(ring, (x0 + v, y_wall - T / 2, z_top - L / 2 + u), 0.011, 0.006, T + 0.002, axis="y", seg=24, soft=0.0)


@_kit._part
def _hang(k, body, x0, y_wall, z_top, L, W, T, rc):
    b = k.bm(body, 0.0)
    pts = [(x0 + v, z_top - L / 2 + u) for u, v in outline(L, W, rc)]
    front = [b.verts.new((x, y_wall - T, z)) for x, z in pts]
    back = [b.verts.new((x, y_wall, z)) for x, z in pts]
    n = len(pts)
    for i in range(n):
        b.faces.new((back[i], back[(i + 1) % n], front[(i + 1) % n], front[i]))
    b.faces.new(back[::-1])
    b.faces.new(front)


def rolled(k, body, edge, c, W, R, layers=5):
    """A mat rolled up and standing on end at c: a cylinder W high of radius R, its spiral shown as rings on top."""
    k.cyl(body, (c[0], c[1], c[2] + W / 2), R, W, seg=48, soft=0.003)
    for i in range(1, layers + 1):
        r = R * i / (layers + 1)
        k.disc(edge, (c[0], c[1], c[2] + W + 0.0003), r + 0.0012, r, 0.0008, axis="z", seg=48, soft=0.0)

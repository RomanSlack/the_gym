"""Balls: a sphere resting on the floor, and lettering / patches laid onto it (placed flat on the tangent plane, then
wrapped round the sphere keeping their height off it)."""
import math
from mathutils import Vector


def normal(lat, lon):
    """The outward direction at latitude lat, longitude lon (lon 0 faces -y, positive toward +x)."""
    return Vector((math.sin(lon) * math.cos(lat), -math.cos(lon) * math.cos(lat), math.sin(lat)))


def wrap(k, mat, soft, c, r, n, fn):
    """Run fn() (which adds geometry to k.bm(mat, soft) on the tangent plane at c + n r) and wrap what it added."""
    g = k.bm(mat, soft)
    before = set(g.verts)
    fn()
    c = Vector(c)
    p0 = c + n * r
    for v in g.verts:
        if v in before:
            continue
        h = (v.co - p0).dot(n)
        q = v.co - n * h
        d = (q - c).normalized()
        v.co = c + d * (r + h)


def label(k, mat, text, c, r, size, lat=0.0, lon=0.0, depth=0.0008, spin=0.0):
    """Lettering on the ball at (lat, lon), upright along the meridian."""
    n = normal(lat, lon)
    p = Vector(c) + n * (r + 0.0002)
    wrap(k, mat, 0, c, r, n, lambda: k.text(mat, text, tuple(p), size, rx=math.pi / 2 - lat, rz=lon, depth=depth, spin=spin))


def band(k, mat, c, r, lat, width, h=0.0008, seg=96, soft=0.0):
    """A band round the ball at latitude lat (a ring of the given width, h proud)."""
    z = math.sin(lat) * r
    rr = math.cos(lat) * (r + h / 2)
    pts = [(c[0] + rr * math.cos(2 * math.pi * i / seg), c[1] + rr * math.sin(2 * math.pi * i / seg), c[2] + z)
           for i in range(seg + 1)]
    k.sweep(mat, pts, k.rect(h, width, h / 3), up=(0, 0, 1), soft=soft)


def seam(k, mat, c, r, axis_lon, w=0.0015, h=0.0006, seg=96):
    """A seam: a great circle through the poles at longitude axis_lon."""
    pts = []
    for i in range(seg + 1):
        t = 2 * math.pi * i / seg
        n = Vector((math.sin(axis_lon) * math.sin(t), -math.cos(axis_lon) * math.sin(t), math.cos(t)))
        pts.append(tuple(Vector(c) + n * (r + h / 2)))
    k.sweep(mat, pts, k.rect(w, h, h / 3), up=(0, 0, 1), soft=0.0)          # flat on the ball, w across

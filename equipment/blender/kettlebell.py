"""One kettlebell builder for the kettlebell pieces (Life Fitness cast iron, Hammer Strength competition):

    bell(k, c, R, handle_r, hw, hh, body, handle, band, lines)

c the centre of the base on the floor; R the body's radius (a ball flattened at the base, standing on it); the handle a
round loop of radius handle_r whose horns stand hw either side of the middle on the body's shoulders and whose top is
hh over the body's top, its corners rounded; a colour band round each horn above the shoulder (band None: none);
lines [(text, size, height over the ball's centre as a fraction of R)] raised on the body's front (-y);
face: the radius of a flat round face cut in the front (the lines go on it).
"""
import math

from mathutils import Vector


def bell(k, c, R, handle_r, hw, hh, body, handle, band, lines, flat=0.80, arch=None, face=None):
    cx, cy, cz = c
    zc = cz + flat * R                                   # the ball's centre over the floor
    before = set(k.bm(body, 0.002).verts)
    k.sphere(body, (cx, cy, zc), R, seg=64, soft=0.002)
    yf = cy - math.sqrt(max(R * R - face ** 2, 0.0)) if face else None   # the flat face's plane (face: its radius)
    for v in k.bm(body, 0.002).verts:                    # flatten the base it stands on, and the face
        if v not in before:
            if v.co.z < cz:
                v.co.z = cz
            if yf is not None and v.co.y < yf:
                v.co.y = yf
    # the horns rise from the shoulders, the loop over the top
    z_sh = zc + math.sqrt(max(R * R - hw * hw, 0.0)) - handle_r * 1.2
    z_top = zc + R + hh
    a = arch if arch is not None else min(0.035, hw * 0.4)   # the loop's corner radius (a big one: a round arch)
    hb = hw * 1.38                                       # the horns splay out to the shoulders (ref_01)
    z_sh = zc + math.sqrt(max(R * R - hb * hb, 0.0)) - handle_r * 1.2
    pts = [(cx - hb, cy, z_sh), (cx - hw, cy, z_top - a), (cx - hw, cy, z_top), (cx + hw, cy, z_top),
           (cx + hw, cy, z_top - a), (cx + hb, cy, z_sh)]
    k.sweep(handle, [Vector(p) for p in pts], k.circle(handle_r, 24), bend=a * 0.98, soft=0.0)
    for s in (1, -1):                                    # the horns' roots flare into the body
        if band:                                         # the band round the horn, along its slope
            p0, p1 = (hb, z_sh), (hw, z_top - a)
            at = lambda t: (cx + s * (p0[0] + (p1[0] - p0[0]) * t), cy, p0[1] + (p1[1] - p0[1]) * t)
            k.tube(band, at(0.30), at(0.42), handle_r + 0.0012, seg=28)
    for text, size, h in lines:
        z = zc + h * R
        if face:                                         # on the flat face, upright
            y = yf - 0.0003
            tilt = 0.0
        else:
            y = cy - math.sqrt(max(R * R - (z - zc) ** 2, 0.0)) - 0.0002
            tilt = math.asin(max(-1.0, min(1.0, (z - zc) / R)))
        k.text("ink" if body != "ink" else "label", text, (cx, y, z), size, rx=math.pi / 2 - tilt, depth=0.0012)
    return zc + R + hh                                    # the handle's top

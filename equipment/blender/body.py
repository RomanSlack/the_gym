"""A stand-in user for the fit check: a capsule figure scaled to any height, posed in the machine, rendered on its own
("fit_<label>" views, see studio.py), never part of the piece, its .glb or its joint check.

Segment lengths are the standard fractions of standing height H (Drillis & Contini): ankle 0.039 H above the sole,
knee 0.285 H, hip 0.530 H, shoulder 0.818 H, foot 0.152 H long, upper arm 0.186 H, forearm 0.146 H, hand 0.108 H,
shoulders 0.259 H across, hips 0.191 H.

Posed in the body's own side plane: `face` is the way the chest points (x, y); each segment's angle is measured from
straight up, positive toward `face` (a body leaning 28 deg into a pad: shank, thigh and trunk all 28). The chain starts
at the ball of the foot (`ball`, the middle between the feet); `sole` is the sole's angle from level, toes up positive.
"""
import math

import bmesh
from mathutils import Vector

LOOK = {"body": dict(color=(0.50, 0.58, 0.70), rough=0.6, coat=0.0)}


def figure(k, H, ball, face, sole=0.0, shank=0.0, thigh=0.0, trunk=0.0, neck=0.0, arm=180.0, forearm=180.0,
           stance=None, arm_out=0.0):
    """Build the figure into kit k; returns its key points (dict of Vectors, the right side's for limbs)."""
    s = H / 1.78
    f = Vector((face[0], face[1], 0.0)).normalized()
    up = Vector((0, 0, 1))
    left = up.cross(f)                                  # the figure's left
    d = lambda a: up * math.cos(math.radians(a)) + f * math.sin(math.radians(a))
    so = f * math.cos(math.radians(sole)) + up * math.sin(math.radians(sole))      # along the sole, to the toes
    su = up * math.cos(math.radians(sole)) - f * math.sin(math.radians(sole))      # out of the sole
    Lf = 0.152 * H
    st = 0.11 * H if stance is None else stance
    pts = {}
    b = Vector(ball)
    for side in (1, -1):
        o = left * side * st / 2
        bl = b + o
        heel, toe = bl - so * 0.73 * Lf, bl + so * 0.27 * Lf
        ankle = bl - so * 0.48 * Lf + su * 0.039 * H
        knee = ankle + d(shank) * 0.246 * H
        hip = knee + d(thigh) * 0.245 * H
        _cap(k, heel + su * 0.02 * s, toe + su * 0.018 * s, 0.03 * s, 0.022 * s)          # the foot
        _cap(k, ankle, knee, 0.042 * s, 0.05 * s)
        _cap(k, knee, hip, 0.055 * s, 0.075 * s)
        if side == 1:
            pts.update(heel=heel, toe=toe, ankle=ankle, knee=knee, hip=hip)
    hipc = pts["hip"] - left * st / 2
    sh = hipc + d(trunk) * 0.288 * H                    # between the shoulders
    pts["shoulders"] = sh
    _cap(k, hipc - left * 0.07 * s, hipc + left * 0.07 * s, 0.10 * s, 0.10 * s)          # the pelvis
    for t in (0.25, 0.55, 0.85):                        # the trunk: three slices, chest deeper than waist
        c = hipc + d(trunk) * 0.288 * H * t
        w = (0.13 if t < 0.5 else 0.15) * s
        _cap(k, c - left * w * 0.6, c + left * w * 0.6, (0.10 if t > 0.4 else 0.09) * s, (0.10 if t > 0.4 else 0.09) * s)
    head = sh + d(neck) * 0.12 * H
    _cap(k, sh, sh + d(neck) * 0.06 * H, 0.05 * s, 0.05 * s)
    _ball(k, head, 0.10 * s)
    pts["head"] = head
    for side in (1, -1):
        shp = sh + left * side * 0.13 * H * 0.85
        a = d(arm) + left * side * math.sin(math.radians(arm_out))
        el = shp + a.normalized() * 0.186 * H
        wr = el + d(forearm) * 0.146 * H
        hd = wr + d(forearm) * 0.08 * H
        _cap(k, shp, el, 0.045 * s, 0.04 * s)
        _cap(k, el, wr, 0.035 * s, 0.03 * s)
        _cap(k, wr, hd, 0.03 * s, 0.025 * s)
        if side == 1:
            pts.update(shoulder=shp, elbow=el, wrist=wr, hand=hd)
    return pts


def _cap(k, a, b, ra, rb):
    """A tapered capsule from a (radius ra) to b (radius rb)."""
    k.tube("body", tuple(a), tuple(b), (ra + rb) / 2, seg=20, soft=0.0)
    _ball(k, a, ra)
    _ball(k, b, rb)


def _ball(k, c, r):
    bm = k.bm("body", 0)
    g = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)["verts"]
    bmesh.ops.translate(bm, verts=g, vec=Vector(c))

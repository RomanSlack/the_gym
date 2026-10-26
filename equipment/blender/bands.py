"""Rubber loop bands lying flattened: a loop pressed flat into two layers, its ends rounded open, the top layer
settling onto the bottom one between them, as on a table."""
import math


def flat_loop(k, role, c, length, width, t, rz=0.0, fold=0.010, seg=10, n=24):
    """A band of the given flat length (half its circumference), width and thickness lying at c, along x turned by rz;
    fold: the open ends' radius."""
    rr = fold
    xe = length / 2 - rr
    pts = [(-xe + 2 * xe * i / n, t / 2) for i in range(n + 1)]               # the bottom layer, -x to +x
    for i in range(1, seg):                                                    # round the +x end
        a = math.radians(-90 + 180 * i / seg)
        pts.append((xe + rr * math.cos(a), rr + rr * math.sin(a)))
    for i in range(n + 1):                                                     # the top layer back, settling
        x = xe - 2 * xe * i / n
        f = (abs(x) / xe) ** 4
        pts.append((x, t * 1.5 + (2 * rr - t * 1.5) * f))
    for i in range(1, seg):                                                    # round the -x end
        a = math.radians(90 + 180 * i / seg)
        pts.append((-xe + rr * math.cos(a), rr + rr * math.sin(a)))
    pts.append(pts[0])
    ca, sa = math.cos(rz), math.sin(rz)
    path = [(c[0] + x * ca, c[1] + x * sa, c[2] + z) for x, z in pts]
    k.sweep(role, path, k.rect(t, width, t / 3), up=(-sa, ca, 0.0), soft=0.0)

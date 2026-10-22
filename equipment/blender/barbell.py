"""One barbell builder for the bar pieces (Eleiko, Hammer Strength, GIANT, Gymleco, Strencor): each piece's model.py
holds its numbers in a spec S and calls build(k, S). The bar lies on the floor on its collars, along x, centred on x = 0.

S keys (metres):
    L          overall length              G        between the collars' inner faces
    shaft      shaft diameter              sleeve   sleeve diameter
    collar     the collar's lathe profile from its inner face outwards: [(dx, r), ...], straight runs between points
    knurl      the knurled runs on each half [(x0, x1), ...] (distances from the centre), the rest of the shaft smooth
    centre     the centre knurl's length (0: none)
    marks      the smooth rings cut in the knurl (their centres, from the centre), 5 mm wide
    badge      dict(text=[lines], size, r): the sleeve end's printed cap (roles "badge" + "print"; big: the index of a line set larger)
    ring       optional dict(text, size, r_in, r_out, full): lettering (full: spread right round) round the collar's inner face (Eleiko; roles "ring" + "ink")
Roles: "shaft" (smooth), "knurl" (from knurl_look), "sleeve", "collar", "gap" (the bushing's dark seam), "badge" + "print"
(the end cap and its lettering), "ring" + "ink" (the collar face's ring and its lettering).
"""
import math

MARK = 0.005


def knurl_look(S, base, pitch=0.0016, strength=0.6):
    """The knurl role: the shaft's look, rougher, with the diamond knurl turned round the bar's own axis."""
    d = dict(base)
    d.update(rough=max(base.get("rough", 0.3), 0.42), aniso=0.0,
             knurl=dict(c=(0.0, z_axis(S)), r=S["shaft"] / 2, pitch=pitch, strength=strength))
    return d


def z_axis(S):
    return max(r for _, r in S["collar"])


def runs(S):
    """The shaft's half (x >= 0) cut into (x0, x1, knurled?) runs: knurl minus the marks, smooth between."""
    cuts = []
    for a, b in S["knurl"]:
        x = a
        for m in sorted(S.get("marks", ())):
            if a < m < b:
                cuts.append((x, m - MARK / 2, True)); x = m + MARK / 2
        cuts.append((x, b, True))
    out, x = [], S.get("centre", 0.0) / 2
    if x > 0:
        out.append((0.0, x, True))
    for a, b, kn in cuts:
        if a > x + 1e-6:
            out.append((x, a, False))
        out.append((a, b, kn)); x = b
    if x < S["G"] / 2 - 1e-6:
        out.append((x, S["G"] / 2, False))
    return out


def build(k, S):
    zc = z_axis(S)
    rs = S["shaft"] / 2
    # the shaft, run by run, mirrored (one run across the middle when there is a centre knurl)
    for s in (1, -1):
        for a, b, kn in runs(S):
            if a == 0.0 and S.get("centre") and s < 0:
                continue
            x0 = -b if (a == 0.0 and S.get("centre")) else s * a
            k.tube("knurl" if kn else "shaft", (x0, 0, zc), (s * b, 0, zc), rs, seg=40)
    for s in (1, -1):
        xi = s * S["G"] / 2
        # the collar: a lathe profile of cones from its inner face outwards
        prof = S["collar"]
        for (d0, r0), (d1, r1) in zip(prof, prof[1:]):
            if d1 > d0:
                k.cyl("collar", (xi + s * (d0 + d1) / 2, 0, zc), r0 if s > 0 else r1, d1 - d0, axis="x", seg=64,
                      r2=r1 if s > 0 else r0, soft=0.0004)
        k.disc("gap", (xi - s * 0.0003, 0, zc), rs + 0.0035, rs + 0.0002, 0.0006, axis="x", seg=48)
        # the sleeve to the end, its printed cap in a bright rim
        xo = xi + s * prof[-1][0]
        xe = s * S["L"] / 2
        rv = S["sleeve"] / 2
        k.tube("sleeve", (xo, 0, zc), (xe, 0, zc), rv, seg=64)
        bd = S["badge"]
        k.disc("sleeve", (xe + s * 0.0006, 0, zc), rv - 0.0002, bd["r"], 0.0012, axis="x", seg=64)
        k.cyl("badge", (xe + s * 0.0003, 0, zc), bd["r"], 0.0006, axis="x", seg=48)
        n = len(bd["text"])
        for i, line in enumerate(bd["text"]):
            sz = bd["size"] * (1.4 if i == bd.get("big", -1) else 1.0)
            k.text("print", line, (xe + s * 0.0007, 0, zc + (n - 1 - 2 * i) * bd["size"] * 0.75), sz, rz=s * math.pi / 2, depth=0.0003)
        ring = S.get("ring")
        if ring:
            # the coloured ring on the collar's inner face with its lettering running round it (as Eleiko prints it)
            k.disc("ring", (xi - s * 0.00025, 0, zc), ring["r_out"], ring["r_in"], 0.0005, axis="x", seg=64)
            R = (ring["r_in"] + ring["r_out"]) / 2 - ring["size"] * 0.35
            step = 2 * math.pi / len(ring["text"]) if ring.get("full") else ring["size"] * 0.82 / R
            a = math.pi / 2 + step * (len(ring["text"]) - 1) / 2
            for ch in ring["text"]:
                if ch != " ":
                    u, v = R * math.cos(a), R * math.sin(a)       # in the face's own plane, u reading across it
                    k.text("ink", ch, (xi - s * 0.0006, -s * u, zc + v), ring["size"], rz=-s * math.pi / 2, depth=0.0003,
                           spin=a - math.pi / 2)
                a -= step

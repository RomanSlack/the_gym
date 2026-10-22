"""One half-rack builder for the Rogue Monster racks (Monster Collegiate Half Rack, Monster Lite Half Rack): each piece's
model.py holds its numbers in a spec S and calls build(k, S). Four 3 x 3 in uprights, the front pair at -y (the lifter's
side, the J-cups and the feet), the back pair at +y (the plate posts and the nameplate); the bar along x.

S keys (metres):
    W        across the uprights' outside faces        D        inside depth (between the front and back uprights)
    TB       the upright / crossmember tube            H_front, H_back   the uprights' heights (Monster: 100 / 90 in)
    hole     (radius, pitch) of the holes up every face of the uprights; numbered up the front faces
    low      the bottom side crossmembers' centre height (the feet carry on from it)
    foot     dict(flat, slope, tab): the angled front foot's level run, its run down to the floor, the floor tab
    side_top the top side crossmembers' centre below the back uprights' top (Monster: angled up to the front uprights)
    angled   True: the top side crossmembers run up to the taller front uprights (the Monster Collegiate), meeting them
             front_drop below the height they meet the back ones at
    plate    dict(h_end, h_mid, text, size, slots, chamfer, ink): the nameplate under the back top crossmember, arched
             along its bottom edge, or with its lower corners cut by `chamfer` (slots: a hand slot near each end; ink: the
             lettering's role, "cut" by default)
    pullup   dict(r, below): the pull-up bar between the front uprights, its centre below their top
    posts    dict(z=[...], len, r): the plate storage posts on the last uprights' outer faces (len: one, or one per post)
    jcup     the J-cups' seat height
    ext      optional: a rear pair of uprights this far behind the back ones (the storage extension), the side
             crossmembers carried on to them, the posts on them
    straps   optional dict(z, sag): strap safeties between the front and back uprights
    foot     optional (no foot: the uprights stand on their base plates)
Roles: "frame" (the steel), "hole", "label" (the numbers), "bolt" (zinc hardware), "nameplate", "cut" (its lettering),
"plastic" (the post sleeves, caps), "peg" (the band pegs), "strap" (the strap safeties).
"""
import math

import kit

IN = 0.0254
PL = 0.0048                      # 3/16 in plate


@kit._part
def holes(k, x, y, z0, z1, face, S, numbers=False):
    """A column of holes up one face of an upright at (x, y); face: "+x", "-x", "+y", "-y". One part (hardware)."""
    r, pitch = S["hole"]
    ax = face[1]
    sgn = 1 if face[0] == "+" else -1
    off = S["TB"] / 2 + 0.0003
    n, z = 1, z0
    while z <= z1:
        dx = S["TB"] * 0.14 if numbers else 0.0          # numbered faces: the holes to one side, the numbers beside them
        c = (x + sgn * off, y, z) if ax == "x" else (x + dx, y + sgn * off, z)
        k.cyl("hole", c, r, 0.0008, axis=ax, seg=14, soft=0.0)
        if numbers and ax == "y":
            k.text("label", str(n), (x + dx - r - S["TB"] * 0.17, y + sgn * (off + 0.0002), z), S["TB"] * 0.2,
                   rz=0.0 if sgn < 0 else math.pi, depth=0.0003)
        n += 1; z += pitch


def through(k, x, y, z, axis, grip, size=0.0254):
    """A 1 in bolt: its head and washer on the face at (x, y, z), pointing along axis, through `grip` to a nut."""
    k.bolt((x, y, z), axis, size=size, nut=grip, mat="bolt")


def build(k, S):
    TB, W, D = S["TB"], S["W"], S["D"]
    xu = W / 2 - TB / 2
    yf, yb = -(D / 2 + TB / 2), D / 2 + TB / 2
    Hf, Hb = S["H_front"], S["H_back"]
    bp = 0.0095                                   # the base plates
    rows = [(yf, Hf), (yb, Hb)]
    if S.get("ext"):                              # a rear pair behind the back uprights (the storage extension)
        rows.append((yb + S["ext"] + TB, Hb))
    ys = [y for y, _ in rows]
    ylast = ys[-1]
    # the uprights on their base plates, capped, holes up every face
    for y, H in rows:
        for s in (1, -1):
            x = s * xu
            k.box("frame", (x, y, bp / 2), (7 * IN, 7 * IN, bp), soft=0.0015)
            k.bar("frame", (x, y, bp), (x, y, H - 0.003), TB, TB, r=0.004)
            k.box("plastic", (x, y, H - 0.0015), (TB - 0.001, TB - 0.001, 0.003), soft=0.001)
            for face in ("+x", "-x", "+y", "-y"):
                holes(k, x, y, 4 * IN, H - 2.5 * IN, face, S, numbers=(face == "-y"))
    zl = S["low"]
    for s in (1, -1):
        x = s * xu
        # the bottom side crossmembers between each pair of uprights, bolted through the last one
        for y0, y1 in zip(ys, ys[1:]):
            k.bar("frame", (x, y0 + TB / 2, zl), (x, y1 - TB / 2, zl), TB, TB, r=0.004)
        through(k, x, ylast + TB / 2, zl, "+y", TB)
        if S.get("foot"):
            foot(k, S, x, s, yf, zl)
        top_side(k, S, x, ys, yf, yb, Hf, Hb)
    nameplate(k, S, xu, yb, Hb)
    extras(k, S, xu, yf, yb, ylast, Hf)


def foot(k, S, x, s, yf, zl):
    """The angled front foot: a plate bolted to the front upright, the tube level, then down to a floor tab."""
    TB, f = S["TB"], S["foot"]
    y0 = yf - TB / 2
    k.box("frame", (x, y0 - PL / 2, zl), (TB + 1.5 * IN, PL, TB + 2.5 * IN), soft=0.001)
    for dz in (1, -1):
        through(k, x, y0 - PL, zl + dz * (TB / 2 + 0.6 * IN), "-y", TB + PL, size=0.019)
    ye = y0 - PL - f["flat"] - f["slope"]
    k.sweep("frame", [(x, y0 - PL, zl), (x, y0 - PL - f["flat"], zl), (x, ye, TB / 2 + 0.002)],
            k.rect(TB, TB, 0.004), soft=0.0015)
    k.box("frame", (x, ye - f["tab"] / 2 + TB / 2, 0.003), (TB, f["tab"] + TB, 0.006), soft=0.001)
    k.cyl("hole", (x, ye - f["tab"] / 2, 0.0062), 0.007, 0.0006, seg=16, soft=0.0)
    for i in range(8):                       # the foot's eight numbered holes, through both side faces
        yy = y0 - PL - 1.5 * IN - i * 2 * IN
        for face in (1, -1):
            k.cyl("hole", (x + face * (TB / 2 + 0.0003), yy, zl), 0.5 * IN, 0.0008, axis="x", seg=16, soft=0.0)
    # the band pegs: zinc pins through the foot, reaching in
    for yy in (y0 - PL - 5.5 * IN, y0 - PL - 11.5 * IN):
        k.tube("peg", (x + s * TB / 2, yy, zl), (x - s * (TB / 2 + 5 * IN), yy, zl), 0.5 * IN, seg=20)


def top_side(k, S, x, ys, yf, yb, Hf, Hb):
    """The top side crossmembers (level, or up to the taller front uprights), bolted at the first and last uprights."""
    TB = S["TB"]
    zb = Hb - S["side_top"]
    zf = (Hf - S["side_top"] - S.get("front_drop", 0.0)) if S.get("angled") else zb
    for i, (y0, y1) in enumerate(zip(ys, ys[1:])):
        p0, p1 = (x, y0 + TB / 2, zf if i == 0 else zb), (x, y1 - TB / 2, zb)
        k.sweep("frame", [p0, p1], k.rect(TB, TB, 0.004), cut0=(p0, (0, 1, 0)), cut1=(p1, (0, 1, 0)), soft=0.0015)
    through(k, x, yf - TB / 2, zf, "-y", TB)
    through(k, x, ys[-1] + TB / 2, zb, "+y", TB)


def nameplate(k, S, xu, yb, Hb):
    """The back top crossmember, the nameplate hung under it: arched (Rogue) or with its lower corners cut (REP)."""
    TB = S["TB"]
    zt = Hb - TB / 2
    k.bar("frame", (-xu + TB / 2, yb, zt), (xu - TB / 2, yb, zt), TB, TB, r=0.004)
    for s in (1, -1):
        for dz in (0.8 * IN, -0.8 * IN):
            through(k, s * (xu + TB / 2), yb, zt + dz, "+x" if s > 0 else "-x", TB, size=0.019)
    pl = S["plate"]
    hw = xu - TB / 2
    top = zt - TB / 2
    if pl.get("chamfer"):
        c = pl["chamfer"]
        lower = [(hw, top - pl["h_end"]), (hw - c, top - pl["h_mid"]), (-hw + c, top - pl["h_mid"]), (-hw, top - pl["h_end"])]
    else:
        lower = [(hw - 2 * hw * i / 24, top - pl["h_mid"] - (pl["h_end"] - pl["h_mid"]) * ((hw - 2 * hw * i / 24) / hw) ** 2)
                 for i in range(25)]
    outline = [(-hw, top), (hw, top)] + lower
    k.sweep("nameplate", [(0, yb - PL / 2, 0), (0, yb + PL / 2, 0)], outline, soft=0.0008)
    zc = top - pl["h_mid"] * 0.5
    for sx in ((1, -1) if pl.get("slots") else ()):   # the hand slots cut through near each end
        k.box("cut", (sx * hw * 0.80, yb, top - pl["h_end"] * 0.35), (hw * 0.14, PL + 0.0008, pl["h_end"] * 0.30), soft=0.0)
    for sy in (1, -1):
        k.text(pl.get("ink", "cut"), pl["text"], (0, yb + sy * (PL / 2 + 0.0002), zc), pl["size"], rz=0.0 if sy < 0 else math.pi, depth=0.0004)


def extras(k, S, xu, yf, yb, ylast, Hf):
    TB = S["TB"]
    # the pull-up bar on endplates bolted inside the front uprights
    pu = S["pullup"]
    zp = Hf - pu["below"]
    xi = xu - TB / 2
    for s in (1, -1):
        k.box("frame", (s * (xi - PL / 2), yf, zp), (PL, TB, 9 * IN), soft=0.001)
        for dz in (3 * IN, -3 * IN):
            through(k, s * (xu + TB / 2), yf, zp + dz, "+x" if s > 0 else "-x", TB + PL, size=0.019)
    k.tube("frame", (-(xi - PL), yf, zp), (xi - PL, yf, zp), pu["r"], seg=28)
    # the plate storage posts on the last uprights' outer faces: a bolted plate, the post in its plastic sleeve
    po = S["posts"]
    yp = ylast
    lens = po["len"] if isinstance(po["len"], (list, tuple)) else [po["len"]] * len(po["z"])
    for s in (1, -1):
        xo = s * (xu + TB / 2)
        for z, ln in zip(po["z"], lens):
            k.box("frame", (xo + s * PL / 2, yp, z), (PL, TB, 8 * IN), soft=0.001)
            for dz in (2.8 * IN, -2.8 * IN):
                through(k, xo + s * PL, yp, z + dz, "+x" if s > 0 else "-x", TB + PL, size=0.019)
            x1 = xo + s * (PL + ln)
            k.tube("frame", (xo + s * PL, yp, z), (xo + s * (PL + 0.6 * IN), yp, z), po["r"] + 0.004, seg=28)
            k.tube("plastic", (xo + s * (PL + 0.6 * IN), yp, z), (x1, yp, z), po["r"], seg=28)
            k.cyl("plastic", (x1 + s * 0.002, yp, z), po["r"] + 0.001, 0.004, axis="x", seg=28, soft=0.0015)
    # strap safeties between the front and back uprights: a bracket inside each, the strap sagging between
    st = S.get("straps")
    for s in ((1, -1) if st else ()):
        xi = s * (xu - TB / 2)
        xs = xi - s * 1.6 * IN
        for y in (yf, yb):
            k.box("frame", (xi - s * PL / 2, y, st["z"]), (PL, TB, 4 * IN), soft=0.001)
            k.box("frame", (xi - s * 1.6 * IN, y, st["z"] + 1.0 * IN), (3.2 * IN, TB, 0.5 * IN), soft=0.001)
            through(k, s * (xu + TB / 2), y, st["z"], "+x" if s > 0 else "-x", TB + PL, size=0.019)
        y0, y1 = yf + TB / 2 - 0.004, yb - TB / 2 + 0.004
        zt = st["z"] + 1.0 * IN + 0.25 * IN + 0.0015
        pts = [(xs, y0, zt)] + [(xs, y0 + (y1 - y0) * t, zt - st["sag"] * math.sin(math.pi * t) ** 1.5) for t in
                                (0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92)] + [(xs, y1, zt)]
        k.sweep("strap", pts, k.rect(2 * IN, 0.12 * IN, 0.001), bend=0.03, soft=0.0008)
    # the J-cups on the front uprights: a sleeve round the upright, the hook out in front, lined
    zj = S["jcup"]
    for s in (1, -1):
        x = s * xu
        yfa = yf - TB / 2
        k.box("frame", (x, yfa - PL / 2, zj), (TB + 2 * PL, PL, 6 * IN), soft=0.001)                 # front plate
        for sx in (1, -1):
            k.box("frame", (x + sx * (TB / 2 + PL / 2), yf, zj), (PL, TB + PL, 6 * IN), soft=0.001)   # wings
        prof = k.rect(2.5 * IN, 0.25 * IN, 0.002)
        hy = yfa - PL
        k.sweep("frame", [(x, hy, zj - 1.6 * IN), (x, hy - 2.2 * IN, zj - 1.6 * IN), (x, hy - 2.6 * IN, zj - 0.2 * IN)],
                prof, bend=0.012, soft=0.001)
        k.box("plastic", (x, hy - 1.1 * IN, zj - 1.6 * IN + 0.25 * IN / 2 + 0.002), (2.4 * IN, 2.0 * IN, 0.004), soft=0.001)

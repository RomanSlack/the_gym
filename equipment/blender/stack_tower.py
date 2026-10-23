"""One weight-stack tower builder for the selectorized machines: each piece's model.py calls tower(k, T, c, rz) with its
numbers in a spec T and builds its own frame, lever and pads around the tower; the cable leaves the tower at the
returned point and the piece routes it on to its lever.

Two styles (read off the makers' photos, 2026-10-22):
  "open"    Hammer Strength Select: a steel frame front and back (the post on one side straight, the other bending round
            into the top beam), the front open (the stack, rods and top plate in view, the weights printed on the
            plates), the exercise placard across the top front and back, a frosted acrylic panel the full height of
            the back with HAMMER STRENGTH low on it.
  "shroud"  a closed tower (side panels, a dark front panel, a rounded top cap), the placard on the front's top, a
            narrow window up the front showing the weight numbers and the selector pin (the Precor Resolute).
  "insignia" Life Fitness Insignia, read off the straight-on photos of three used units (2026-10-22): two charcoal
            side uprights the full height (about 0.08 across, set back behind the front panels), a gloss rounded
            cap overhanging them with a thin silver line under its front; the front two satin panels with a channel
            between them showing the selector rod, the orange pin and the plates' printed numbers, the LF badge block
            on the channel's top, a placard on each panel's top (placard.insignia), a small hook on the left panel;
            the back one bowed inset panel with the LifeFitness script up it; a base pan. About 0.56 as wide as tall.
  "axiom"   Life Fitness Axiom, read off the maker's studio shot in two colourways (2026-10-22): frame-coloured side
            panels the full depth (bolt heads on them), two black front panels with a narrow slot between them down
            to the stack (the selector rod, the plates' numbers, the yellow pin and the add-on weight in it), the
            placard band across the top (black: the LifeFitness script, the muscle, the QR, the how-to pictures) on a
            grey strip with the exercise's name, a thin black cap, a frame-coloured base pan.
  "atlantis" Atlantis Precision, read off the maker's four renders of the M318 (2026-10-22): four square corner posts
            on low side rails and rubber feet, gloss black side panels between them with the big red A and ATLANTIS,
            the front open on the stack (each plate printed "20 lb / 9 kg"), a kick plate with its label at the foot,
            the placard band across the top (the small logo, the muscle, the figure), the cap rounded over at its
            front with a tray in its top.
Local frame (before the tower is turned by rz about its footprint's centre c): the tower's front faces -y.

T keys (metres): style, W (across), D (deep), H (tall), n (plates), plate (w, d, t), rods (centres apart), title
(the placard's exercise name), brand ("HAMMER STRENGTH" / "LifeFitness"), round (+1 / -1: which top corner of the open
frame is bent round), units ("lb"/"kg") and step (the weight per plate) for the printed numbers.
Roles: "frame" (the machine's frame colour), "shroud" + "shroud2" (the closed tower's panels), "plate", "chrome",
"acrylic", "placard" + "ink" (the placard and its lettering), "label" (printed numbers), "rubber", "plastic",
"cable".
"""
import math

import kit

FOOT_H = 0.012
LOOK = {   # defaults, a piece's LOOK overrides any of them
    "acrylic": dict(color=(0.92, 0.94, 0.95), rough=0.03, coat=0.0, trans=1.0),
    "placard": dict(color=(0.015, 0.015, 0.016), rough=0.35, coat=0.3),
    "ink": dict(color=(0.9, 0.9, 0.9), rough=0.4, coat=0.0),
    "ink2": dict(color=(0.30, 0.32, 0.36), rough=0.4, coat=0.0),
    "shroud": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.15),
    "shroud2": dict(color=(0.07, 0.072, 0.075), rough=0.4, coat=0.2),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
    "frosted": dict(color=(0.85, 0.87, 0.88), rough=0.35, coat=0.0, trans=0.85),                   # the frosted back
    "warn": dict(color=(0.95, 0.55, 0.02), rough=0.4, coat=0.0),                                     # the placard's orange
    "picture": dict(color=(0.035, 0.035, 0.038), rough=0.3, coat=0.3),                               # its dark pictures
    "yellow": dict(color=(0.95, 0.55, 0.02), rough=0.4, coat=0.1),                                   # the add-on weight
    "logo": dict(color=(0.62, 0.04, 0.05), rough=0.35, coat=0.2),                                    # Atlantis red
    "blue": dict(color=(0.10, 0.45, 0.85), rough=0.4, coat=0.0),                                     # the placard's figure
}


def _arc(cx, cz, r, a0, a1, y, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y, cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def tower(k, T, c, rz=0.0, name="tower"):
    """Build the tower in a sub-kit at c = (x, y), turned rz degrees; returns dict(cable=(x, y, z) where the cable
    leaves the tower's top pulley, local, before rz: the piece turns its own points the same way via `world`)."""
    for role, v in LOOK.items():
        if role not in k.looks:
            k.look(**{role: v})
    t = k.sub(name, pivot=(c[0], c[1], 0.0), rz=rz)
    cx, cy = c
    W, D, H = T["W"], T["D"], T["H"]
    pw, pd, pt = T["plate"]
    n = T["n"]
    # the stack, on the floor plate between its rubber bumpers, the rods to just under the rod plate
    rod_top = H - (0.30 if T["style"] == "open" else 0.18)
    k_floor = (cx, cy, FOOT_H + 0.006)
    t.box("frame", (cx, cy, FOOT_H / 2 + 0.003), (W - 0.02, D - 0.02, FOOT_H + 0.006), soft=0.002)        # the floor plate
    for sx in (1, -1):
        for sy in (1, -1):
            t.box("rubber", (cx + sx * (W / 2 - 0.04), cy + sy * (D / 2 - 0.04), FOOT_H / 2), (0.06, 0.06, FOOT_H), soft=0.002)
    ztop = t.stack(k_floor, n=n, w=pw, d=pd, t=pt, rods=T["rods"], top=rod_top - k_floor[2], pin_at=T.get("pin_at", 5))
    # the rod plate across the top of the rods (both styles), the top pulley under the deck, the cable up to it
    rp = {"open": (T["rods"] + 0.08, D - 0.10), "insignia": (W - 0.18, D - 0.08), "axiom": (W - 0.08, D - 0.08), "atlantis": (W - 0.14, D - 0.06)}.get(T["style"], (W - 0.024, D - 0.024))
    t.box("frame", (cx, cy, rod_top + 0.01), (rp[0], rp[1], 0.02), soft=0.002)
    zp = rod_top + 0.10
    t.box("frame", (cx, cy, (rod_top + 0.02 + zp - 0.04) / 2), (0.05, 0.06, zp - 0.04 - rod_top - 0.02), soft=0.002)
    t.pulley((cx, cy, zp), 0.045, axis="x")
    t.cable([(cx, cy, ztop - 0.01), (cx, cy, ztop + 0.10), (cx, cy - 0.045, zp - 0.02), (cx, cy - 0.045, zp)])
    out = (cx, cy - 0.046, zp)
    if T["style"] == "open":
        _open(t, T, cx, cy, W, D, H, n, pt, ztop)
    elif T["style"] == "insignia":
        _insignia(t, T, cx, cy, W, D, H, n, pt, ztop)
    elif T["style"] == "axiom":
        _axiom(t, T, cx, cy, W, D, H, n, pt, ztop)
    elif T["style"] == "atlantis":
        _atlantis(t, T, cx, cy, W, D, H, n, pt, ztop)
    else:
        _shroud(t, T, cx, cy, W, D, H, n, pt)
    return dict(cable=out, sub=t)


def _placard(t, T, cx, y, z, w, h, facing=-1, rz=0.0):
    """The exercise placard: a black panel, the brand top left, three diagram squares, the exercise's name (facing
    -y, or +y with rz = pi: then left and right swap)."""
    t.box("placard", (cx, y, z), (w, 0.006, h), soft=0.001)
    yf = y + facing * 0.0032
    sg = -facing
    t.text("ink", T["brand"], (cx - sg * (w / 2 - 0.11), yf, z + h / 2 - 0.025), 0.022, rz=rz, depth=0.0003)
    q = min(0.07, (w - 0.04) / 3.4)                  # the diagram squares, smaller on a narrow placard
    for i in range(3):
        t.box("ink2", (cx - sg * (w / 2 - 0.02 - q / 2 - i * q * 1.2), yf, z - 0.01), (q, 0.0006, q), soft=0.0)
    t.text("ink", T["title"], (cx + sg * (w / 2 - 0.13), yf, z - h / 2 + 0.03), 0.022, rz=rz, depth=0.0003)


def _insignia(t, T, cx, cy, W, D, H, n, pt, ztop):
    zb = FOOT_H + 0.006
    hc = 0.10                                      # the cap
    hb = H - hc
    yf, yb = cy - D / 2, cy + D / 2
    # the base pan, a little proud of the body all round
    t.box("shroud", (cx, cy, 0.025), (W + 0.02, D + 0.02, 0.05 - FOOT_H), soft=0.012)
    # the side uprights: the full height to the cap and the full depth, flanking the front and back panels (ref_10:
    # in view at both edges from the front, ref_08: from the back)
    uw = 0.075
    for sx in (1, -1):
        t.box("frame", (cx + sx * (W / 2 - uw / 2), cy, (0.05 + hb) / 2), (uw, D, hb - 0.05 + 0.002), soft=0.012)
    # the front: two satin panels between the uprights, a little back from their fronts, the channel between them
    # (ch wide), a fine steel lip on each panel's inner edge
    ch = 0.06                                  # (narrow: the studio shots' chrome strip)
    pw = (W - 2 * uw - ch) / 2 + 0.003
    pt_ = 0.026
    zp0, zp1 = 0.055, hb - 0.004
    for sx in (1, -1):
        xc = cx + sx * (ch / 2 + pw / 2)
        t.box("shroud2", (xc, yf + pt_ / 2 + 0.008, (zp0 + zp1) / 2), (pw, pt_, zp1 - zp0), soft=0.004)
        t.box("steel", (cx + sx * (ch / 2 + 0.003), yf + 0.014, (zp0 + zp1) / 2 - 0.08), (0.004, 0.012, zp1 - zp0 - 0.30), soft=0.001)
    # inside the channel: the dark back wall above the stack, the chrome lifting rod up from the top plate, the plates'
    # printed numbers each side of the pin holes, the orange pin knob
    t.box("shroud", (cx, cy + 0.07, (ztop + hb) / 2), (ch + 0.02, 0.01, hb - ztop), soft=0.002)
    t.tube("chrome", (cx, cy - 0.02, ztop - 0.01), (cx, cy - 0.02, hb - 0.20), 0.011, seg=18)
    t.box("frame", (cx, yf + 0.045, ztop + 0.02), (ch + 0.02, 0.04, 0.012), soft=0.002)                # the strip's foot
    t.tube("chrome", (cx, yf + 0.03, ztop + 0.02), (cx, yf + 0.03, hb - 0.185), 0.012, seg=20)      # the polished strip
    pw_, pd_, _ = T["plate"]
    z0 = FOOT_H + 0.006 + 0.05
    for i in range(n):
        z = z0 + (i + 0.5) * pt
        val = str((i + 1) * T.get("step", 15) + T.get("start", 0))
        for dx in (-0.032, 0.032):
            t.text("label", val, (cx + dx, cy - pd_ / 2 - 0.0005, z), pt * 0.42, depth=0.0002)
    zpin = z0 + (T.get("pin_at", 5) + 0.5) * pt
    t.cyl("warn", (cx, cy - pd_ / 2 - 0.058, zpin), 0.019, 0.026, axis="y", seg=24, soft=0.004)
    # the LF badge block on the channel's top
    zbg = hb - 0.11
    t.box("placard", (cx, yf + 0.018, zbg), (ch + 0.004, 0.024, 0.15), soft=0.004)
    t.cyl("ink2", (cx, yf + 0.006 - 0.0005, zbg + 0.035), 0.024, 0.002, axis="y", seg=32, soft=0.0005)
    t.cyl("placard", (cx, yf + 0.006 - 0.0015, zbg + 0.035), 0.019, 0.002, axis="y", seg=32, soft=0.0)
    t.text("ink", "LF", (cx, yf + 0.006 - 0.0026, zbg + 0.031), 0.016, depth=0.0003)
    for dz in (-0.015, -0.045):
        t.box("ink2", (cx, yf + 0.006 - 0.0005, zbg + dz), (0.05, 0.001, 0.018), soft=0.0)
    # the placards on the panels' tops, the hook on the left panel
    _placard_insignia(t, T, cx, yf + 0.005, hb - 0.10, ch, pw)
    xh = cx - ch / 2 - pw * 0.62
    t.box("plastic", (xh, yf - 0.003, hb - 0.27), (0.03, 0.022, 0.09), soft=0.004)
    t.box("plastic", (xh + 0.015, yf - 0.018, hb - 0.305), (0.05, 0.018, 0.022), rz=-0.4, soft=0.004)
    # the cap: gloss, flush with the uprights; seen from the front its top corners curve down on a big radius and the
    # top between them is gently domed (the studio shots), its front and back edges rounded over; a crisp band at its
    # foot; the silver line under its front between the uprights
    t.box("shroud", (cx, cy, hb + 0.0125), (W + 0.012, D + 0.012, 0.025), soft=0.003)                 # its crisp band
    a, rc, dome = (W + 0.012) / 2, 0.08, 0.012
    zs = hc - dome - rc                                            # where the sides start to curve over
    prof = [(-a, 0.0), (a, 0.0)]
    prof += [(a - rc + rc * math.cos(math.pi / 2 * i / 10), zs + rc * math.sin(math.pi / 2 * i / 10)) for i in range(11)]
    xt = a - rc
    prof += [(xt * (1 - 2 * i / 16), hc - dome + dome * (1 - (1 - 2 * i / 16) ** 2)) for i in range(1, 16)]
    prof += [(-a + rc - rc * math.cos(math.pi / 2 * i / 10), zs + rc * math.sin(math.pi / 2 * i / 10)) for i in range(10, -1, -1)]
    t.sweep("shroud", [(cx, yf - 0.006, hb + 0.004), (cx, yb + 0.006, hb + 0.004)], [(-u, v) for u, v in prof],
            up=(0, 0, 1), soft=0.028)                                                                    # its crown
    t.box("chrome", (cx, yf + 0.006, hb - 0.002), (W - 2 * uw + 0.004, 0.004, 0.006), soft=0.001)
    # the back: the bowed inset panel between the uprights with the script up it
    bw = W - 2 * uw - 0.03                     # a dark gap each side to the uprights (ref_08)
    yb2 = yb - 0.03                            # recessed behind their backs
    for sx in (1, -1):
        for zt in (0.25, 0.75, 1.15):
            t.box("frame", (cx + sx * (W / 2 - uw - 0.012), yb2 - 0.004, zt), (0.03, 0.012, 0.05), soft=0.001)   # its tabs
    t.sweep("shroud2", [(cx, yb2, 0.07), (cx, yb2, hb - 0.02)],
            [(-bw / 2 + bw * i / 12, 0.012 * math.sin(math.pi * i / 12)) for i in range(13)] +
            [(bw / 2 - bw * i / 12, 0.012 * math.sin(math.pi * (12 - i) / 12) - 0.016) for i in range(13)],
            up=(0, 1, 0), soft=0.006)
    t.text("ink2", T["brand"], (cx, yb2 + 0.0125, (0.07 + hb) / 2), 0.075, rz=math.pi, spin=math.pi / 2, depth=0.0006)


def _placard_insignia(t, T, cx, y, z, ch, pw):
    """Life Fitness Insignia's two placards (ref_05 of the calf extension, ref_06 of the leg extension), one across the
    top of each front panel either side of the badge block: on the left the QR square, the muscle picture (a pale leg,
    the worked muscle orange) and the exercise's name under it; on the right the two how-to pictures and the brand."""
    w, h = pw - 0.03, 0.15
    yf = y - 0.0032
    for sx in (-1, 1):
        xc = cx + sx * (ch / 2 + pw / 2)
        t.box("placard", (xc, y, z), (w, 0.006, h), soft=0.002)
        t.box("picture", (xc + sx * 0.012, yf, z + 0.012), (w - 0.05, 0.0006, h - 0.055), soft=0.0)     # the picture
    xl = cx - ch / 2 - pw / 2
    t.box("ink", (xl - w / 2 + 0.028, yf - 0.0004, z + 0.035), (0.03, 0.0006, 0.03), soft=0.0)          # the QR square
    t.box("ink2", (xl + 0.01, yf - 0.0004, z + 0.02), (0.022, 0.0006, 0.09), ry=0.5, soft=0.0)             # the leg
    t.box("warn", (xl + 0.045, yf - 0.0006, z + 0.0), (0.06, 0.0006, 0.024), ry=-0.3, soft=0.0)          # its muscle
    t.text("ink", T["title"], (xl + 0.01, yf - 0.0004, z - h / 2 + 0.017), 0.015, depth=0.0003)
    xr = cx + ch / 2 + pw / 2
    for i in range(2):
        xx = xr - w * 0.18 + i * w * 0.36
        t.box("ink2", (xx, yf - 0.0004, z + 0.02), (0.035, 0.0006, 0.05), soft=0.0)                       # the figures
        t.box("acrylic" if i else "warn", (xx + 0.015, yf - 0.0006, z - 0.005), (0.04, 0.0006, 0.01), soft=0.0)
    t.text("ink", T["brand"], (xr + w * 0.22, yf - 0.0004, z - h / 2 + 0.017), 0.015, depth=0.0003)


def _open(t, T, cx, cy, W, D, H, n, pt, ztop):
    xs = W / 2 - 0.038
    zb = FOOT_H + 0.006
    R = 0.16
    rs = T.get("round", 1)
    for y in (cy - D / 2 + 0.025, cy + D / 2 - 0.025):
        # the frame: straight post one side, the other bent round into the top beam (radius R)
        a = (cx - rs * xs, y, zb)
        b = (cx - rs * xs, y, H - 0.038)
        arc = _arc(cx + rs * (xs - R), H - 0.038 - R, R, 90 if rs > 0 else 90, 0 if rs > 0 else 180, y)
        path = [a, b] + arc + [(cx + rs * xs, y, zb)]
        t.sweep("frame", path, kit.rect(0.076, 0.05, 0.006), up=(0, 1, 0), soft=0.002)
    t.box("frame", (cx, cy, H - 0.012), (W - 0.2, D - 0.10, 0.024), soft=0.002)                       # the top deck
    # the front is open (ref photos of a used unit, 2026-10-22): the placard across its top; the weights printed on
    # the plates' fronts, a number each side of the pin hole
    yf = cy - D / 2 + 0.001
    ph = 0.22
    _placard(t, T, cx, yf - 0.003, H - 0.08 - ph / 2, 2 * xs, ph)
    pw, pd, _ = T["plate"]
    z0 = FOOT_H + 0.006 + 0.05
    for i in range(n):
        z = z0 + (i + 0.5) * pt
        val = str((i + 1) * T.get("step", 10) + T.get("start", 0))
        for dx in (-0.055, 0.055):
            t.box("label", (cx + dx, cy - pd / 2 - 0.0004, z), (0.05, 0.0008, pt * 0.62), soft=0.0)
            t.text("seam", val, (cx + dx, cy - pd / 2 - 0.0009, z), pt * 0.5, depth=0.0002)
    # the back: a frosted acrylic panel the full height between the frames, HAMMER STRENGTH low on it, the placard on top
    yb = cy + D / 2 + 0.002
    t.box("frosted", (cx, yb, (FOOT_H + H - 0.08 - ph) / 2 + 0.01), (2 * xs, 0.004, H - 0.08 - ph - FOOT_H), soft=0.0006)
    for i, line in enumerate(T["brand"].split(" ", 1) if T["brand"].isupper() else [T["brand"]]):
        t.text("ink2", line, (cx, yb + 0.0025, 0.45 - i * 0.075), 0.065, rz=math.pi, depth=0.0004)
    _placard(t, T, cx, yb + 0.003, H - 0.08 - ph / 2, 2 * xs, ph, facing=1, rz=math.pi)


def _corners(pts, radii, seg=8):
    """A closed outline (x, y) with each corner rounded by its own radius."""
    out = []
    n = len(pts)
    for i in range(n):
        (ax, ay), (bx, by), (qx, qy) = pts[i - 1], pts[i], pts[(i + 1) % n]
        r = radii[i]
        if r <= 0:
            out.append((bx, by))
            continue
        ux, uy = ax - bx, ay - by; lu = math.hypot(ux, uy); ux, uy = ux / lu, uy / lu
        vx, vy = qx - bx, qy - by; lv = math.hypot(vx, vy); vx, vy = vx / lv, vy / lv
        p0, p1 = (bx + ux * r, by + uy * r), (bx + vx * r, by + vy * r)     # (square corners: the arc's ends)
        ccx, ccy = p0[0] + vx * r, p0[1] + vy * r
        a0, a1 = math.atan2(p0[1] - ccy, p0[0] - ccx), math.atan2(p1[1] - ccy, p1[0] - ccx)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        out += [(ccx + r * math.cos(a0 + da * j / seg), ccy + r * math.sin(a0 + da * j / seg)) for j in range(seg + 1)]
    return out


def _axiom(t, T, cx, cy, W, D, H, n, pt, ztop):
    hc = 0.05                                      # the cap at its crown
    hb = H - hc
    yf, yb = cy - D / 2, cy + D / 2
    # the side uprights: frame colour, the full depth, from the floor plate to the cap, their outer corners rounded on
    # a big radius (the studio shots' highlight down the corner), standing proud of the front between them; two bolt
    # heads up each
    uw, ro = 0.06, 0.04
    for sx in (1, -1):
        xo, xi = cx + sx * W / 2, cx + sx * (W / 2 - uw)
        plan = [(xi, yf), (xo, yf), (xo, yb), (xi, yb)]
        out = _corners(plan, [0.004, ro, ro, 0.004])
        t.sweep("frame", [(0, 0, 0.012), (0, 0, hb)], [(-x, y) for x, y in out], up=(0, 1, 0), soft=0.004)
        for z in (0.78, 0.93):
            t.bolt((xo, yf + 0.09, z), "+x" if sx > 0 else "-x", size=0.014)
    yf = yf + 0.018                                # the front between them, set back
    zp = 0.07                                      # the base pan between the uprights, its top
    t.box("frame", (cx, (yf + yb) / 2, zp / 2 + 0.006), (W - 2 * uw + 0.004, yb - yf - 0.01, zp - 0.012), soft=0.004)
    st = uw
    # the front: two black panels between the sides, the slot between them; the placard band over them on its grey
    # strip, the band's top under the cap
    wi = W - 2 * st
    sl = 0.045
    pw = (wi - sl) / 2
    zs = hb - 0.20                                 # the grey strip's foot (the panels' top)
    hs = 0.035                                     # the strip's height
    for sx in (1, -1):
        t.box("shroud2", (cx + sx * (sl / 2 + pw / 2), yf + 0.016, (zp + zs) / 2), (pw, 0.02, zs - zp), soft=0.003)
    t.box("ink2", (cx, yf + 0.016, zs + hs / 2), (wi + 0.002, 0.024, hs), soft=0.002)
    t.box("placard", (cx, yf + 0.016, (zs + hs + hb) / 2), (wi + 0.002, 0.024, hb - zs - hs), soft=0.002)
    yp = yf + 0.004 - 0.0004                       # the band's face
    t.text("ink", T["title"], (cx - wi * 0.30, yp - 0.0002, zs + hs / 2), 0.014, depth=0.0003)
    t.box("placard", (cx, yp, zs + hs / 2), (0.004, 0.001, hs), soft=0.0)              # the strip's split at the slot
    for i in range(16):                                                                   # its dot pattern
        for j in range(2):
            t.box("hole", (cx + 0.03 + i * 0.008, yp, zs + 0.013 + j * 0.009), (0.004, 0.0008, 0.004), soft=0.0)
    zt = hb - 0.005
    t.text("ink", T["brand"], (cx - 0.01, yp, zt - 0.025), 0.024, depth=0.0003)
    xm = cx - wi / 2 + 0.065
    t.box("picture", (xm, yp, zt - 0.09), (0.10, 0.001, 0.11), soft=0.0)                  # the muscle picture: the
    for (x, z, w, h, r) in ((-0.012, 0.022, 0.012, 0.06, 0.55), (0.012, -0.02, 0.01, 0.05, -0.35)):   # leg, the
        t.box("warn", (xm + x, yp - 0.0006, zt - 0.09 + z), (w, 0.001, h), ry=r, soft=0.0)          # hamstring orange
    t.box("ink2", (xm + 0.02, yp - 0.0006, zt - 0.075), (0.006, 0.001, 0.07), ry=-0.2, soft=0.0)
    t.box("ink", (cx - 0.03, yp, zt - 0.08), (0.024, 0.001, 0.024), soft=0.0)           # the QR
    t.box("warn", (cx - 0.03, yp, zt - 0.104), (0.008, 0.001, 0.01), soft=0.0)
    pq = min(0.085, (wi / 2 - 0.04) / 2)                                                # the how-to pictures
    for i in range(2):
        x = cx + 0.025 + pq / 2 + i * (pq + 0.01)
        t.box("ink2", (x, yp, zt - 0.085), (pq, 0.001, 0.062), soft=0.0)
        t.box("picture", (x, yp - 0.0006, zt - 0.085), (pq - 0.006, 0.001, 0.056), soft=0.0)
        t.box("ink2", (x, yp - 0.0012, zt - 0.09), (pq * 0.6, 0.001, 0.01), ry=0.2, soft=0.0)
    # in the slot: the dark wall behind, the selector rod, the plates' numbers, the yellow pin, the add-on weight
    t.box("shroud", (cx, cy + 0.08, (ztop + zs) / 2), (sl + 0.02, 0.01, zs - ztop), soft=0.002)
    t.tube("chrome", (cx, cy - 0.02, ztop - 0.01), (cx, cy - 0.02, zs - 0.01), 0.009, seg=16)
    pw_, pd_, _ = T["plate"]
    z0 = FOOT_H + 0.006 + 0.05
    for i in range(n):
        val = str((i + 1) * T.get("step", 15) + T.get("start", 0))
        t.text("label", val, (cx - 0.008, cy - pd_ / 2 - 0.0005, z0 + (i + 0.5) * pt), pt * 0.32, depth=0.0002)
        t.box("hole", (cx + 0.012, cy - pd_ / 2 - 0.0005, z0 + (i + 0.5) * pt), (0.008, 0.001, 0.008), soft=0.0)
    zpin = z0 + (T.get("pin_at", 5) + 0.5) * pt
    t.cyl("warn", (cx + 0.012, yf - 0.008, zpin), 0.014, 0.03, axis="y", seg=20, soft=0.004)
    t.tube("chrome", (cx + 0.012, yf + 0.006, zpin), (cx + 0.012, cy - pd_ / 2 + 0.01, zpin), 0.005, seg=10)
    t.box("yellow", (cx, yf + 0.004, ztop + 0.05), (0.04, 0.012, 0.02), soft=0.003)                 # the add-on weight
    t.text("ink", "+7.5", (cx, yf - 0.0022, ztop + 0.05), 0.009, depth=0.0006)
    t.box("frame", (cx, (yf + 0.01 + cy + 0.076) / 2, ztop + 0.05), (0.03, cy + 0.076 - yf - 0.01, 0.012), soft=0.001)   # its arm
    # the cap, a hair over the body all round, its edges rounded; the back panel with the script
    # the cap: arched across (low over the uprights, high in the middle), its ends rounded down onto them, its front
    # and back edges rounded over
    a = W / 2 + 0.003
    prof = [(-a, 0.0), (a, 0.0), (a, 0.012)] + [(a - 0.014 + 0.014 * math.cos(math.pi / 2 * j / 6), 0.012 + 0.014 * math.sin(math.pi / 2 * j / 6)) for j in range(1, 7)]
    prof += [(x, 0.026 + (hc - 0.026) * (1 - (x / (a - 0.014)) ** 2)) for x in [(a - 0.014) * (1 - 2 * j / 20) for j in range(1, 20)]]
    prof += [(-a + 0.014 - 0.014 * math.cos(math.pi / 2 * j / 6), 0.012 + 0.014 * math.sin(math.pi / 2 * j / 6)) for j in range(6, 0, -1)] + [(-a, 0.012)]
    t.sweep("shroud", [(cx, cy - D / 2 - 0.003, hb), (cx, yb + 0.003, hb)], [(-x, z) for x, z in prof], up=(0, 0, 1), soft=0.01)
    t.box("shroud2", (cx, yb - 0.01, (zp + hb) / 2), (wi + 0.002, 0.02, hb - zp), soft=0.003)
    t.text("ink2", T["brand"], (cx, yb + 0.0005, hb - 0.12), 0.05, rz=math.pi, depth=0.0004)


def _seg(t, mat, o, rz, a, b, w, d=0.0012):
    """A flat stroke from a to b ((u, v): u the viewer's right, v up) in the vertical face through o whose front
    faces -y turned by rz; w wide, d deep (centred on o's plane)."""
    (u0, v0), (u1, v1) = a, b
    um, vm = (u0 + u1) / 2, (v0 + v1) / 2
    c = (o[0] + math.cos(rz) * um, o[1] + math.sin(rz) * um, o[2] + vm)
    t.box(mat, c, (math.hypot(u1 - u0, v1 - v0) + w, d, w), ry=-math.atan2(v1 - v0, u1 - u0), rz=rz, soft=0.0)


def _logo(t, o, rz, s, word=True):
    """Atlantis's mark centred on o (its foot's middle) in a face (see _seg): the red trapezoid A, the spear in it,
    ATLANTIS under it; s the trapezoid's foot width."""
    w = 0.075 * s
    q = [(-0.5 * s, 0.0), (0.5 * s, 0.0), (0.25 * s, 1.24 * s), (-0.25 * s, 1.24 * s)]
    for i in range(4):
        _seg(t, "logo", o, rz, q[i], q[(i + 1) % 4], w if i != 2 else 1.4 * w)
    _seg(t, "logo", o, rz, (0, 0.02 * s), (0, 0.45 * s), 0.035 * s)                    # the spear's shaft
    _seg(t, "logo", o, rz, (0, 0.42 * s), (0, 0.86 * s), 0.12 * s)                     # its blade
    t.box("logo", (o[0], o[1], o[2] + 0.88 * s), (0.085 * s, 0.0012, 0.085 * s), ry=math.pi / 4, rz=rz, soft=0.0)
    if word:
        t.text("ink", "ATLANTIS", (o[0], o[1], o[2] - 0.24 * s), 0.24 * s, rz=rz, depth=0.0008)


def _atlantis(t, T, cx, cy, W, D, H, n, pt, ztop):
    hc = 0.09                                      # the cap
    hb = H - hc
    yf, yb = cy - D / 2, cy + D / 2
    po = 0.07                                      # the corner posts
    zp = 0.10                                      # the panels' foot, over the low side rails
    for sx in (1, -1):
        x = cx + sx * (W / 2 - po / 2)
        for y in (yf + po / 2, yb - po / 2):
            t.box("frame", (x, y, (FOOT_H + hb) / 2), (po, po, hb - FOOT_H), soft=0.004)
        t.box("frame", (x, cy, 0.06), (po - 0.01, D - 2 * po + 0.004, 0.05), soft=0.003)          # the low side rail
        # the side panel, gloss, between the posts a hair inside their face; the big logo on it (ref_03 / ref_04)
        xs = cx + sx * (W / 2 - 0.012)
        t.box("shroud", (xs, cy, (zp + hb) / 2), (0.02, D - 2 * po + 0.004, hb - zp), soft=0.003)
        _logo(t, (xs + sx * 0.0101, cy, 1.24), sx * math.pi / 2, 0.16)
    # the back panel between the back posts
    t.box("shroud", (cx, yb - 0.012, (zp + hb) / 2), (W - 2 * po + 0.004, 0.02, hb - zp), soft=0.003)
    # the front, open on the stack: the kick plate at its foot with the label, the placard band across the top
    wi = W - 2 * po
    t.box("frame", (cx, yf + 0.012, 0.115), (wi + 0.004, 0.02, 0.07), soft=0.002)
    t.box("label", (cx - wi / 2 + 0.06, yf + 0.0018, 0.115), (0.07, 0.001, 0.03), soft=0.0)
    hp = 0.17
    zc = hb - hp / 2
    t.box("placard", (cx, yf + 0.012, zc), (wi + 0.004, 0.02, hp), soft=0.002)
    o = (cx, yf + 0.0021, zc)                      # the band's face
    _logo(t, (cx - wi / 2 + 0.035, o[1], hb - 0.045), 0.0, 0.026, word=False)
    t.text("ink", "ATLANTIS", (cx - wi / 2 + 0.105, o[1], hb - 0.03), 0.019, depth=0.0008)
    xm = cx - 0.02                                 # the muscle picture: the leg, its calf in red
    t.box("picture", (xm, o[1], zc - 0.005), (0.12, 0.0012, 0.14), soft=0.0)
    _seg(t, "ink2", (xm, o[1] - 0.0004, zc), 0.0, (-0.02, 0.05), (0.0, -0.01), 0.026)
    _seg(t, "ink2", (xm, o[1] - 0.0004, zc), 0.0, (0.0, -0.01), (0.01, -0.06), 0.02)
    _seg(t, "logo", (xm, o[1] - 0.0008, zc), 0.0, (0.004, -0.015), (0.012, -0.045), 0.014)
    _seg(t, "ink2", (cx + 0.055, o[1], zc), 0.0, (0, -0.07), (0, 0.07), 0.003)          # the divider
    xf = cx + 0.11                                 # the figure on the machine, in blue on white lines
    _seg(t, "ink", (xf, o[1], zc), 0.0, (-0.03, -0.06), (-0.03, 0.05), 0.004)
    _seg(t, "ink", (xf, o[1], zc), 0.0, (-0.03, 0.05), (0.02, -0.06), 0.004)
    _seg(t, "blue", (xf, o[1] - 0.0004, zc), 0.0, (-0.005, 0.03), (0.012, -0.03), 0.012)
    _seg(t, "logo", (xf, o[1], zc), 0.0, (0.03, 0.05), (0.04, 0.06), 0.004)
    # in the stack: each plate printed "20 lb / 9 kg" left of the pin
    pw_, pd_, _ = T["plate"]
    z0 = FOOT_H + 0.006 + 0.05
    for i in range(n):
        lb = (i + 1) * T.get("step", 20) + T.get("start", 0)
        t.text("label", f"{lb} lb / {round(lb * 0.4536)} kg", (cx - pw_ * 0.22, cy - pd_ / 2 - 0.0005, z0 + (i + 0.5) * pt),
               pt * 0.26, depth=0.0006)
    # the cap: the full width a hair over the posts, rounded over at its front top (ref_03 / ref_04), the tray in its top
    a0, a1, rf, rb = -D / 2 - 0.006, D / 2 + 0.006, 0.07, 0.012
    prof = [(a0, 0.0), (a1, 0.0), (a1, hc - rb)]
    prof += [(a1 - rb + rb * math.cos(math.pi / 2 * j / 4), hc - rb + rb * math.sin(math.pi / 2 * j / 4)) for j in range(1, 5)]
    prof += [(a0 + rf + rf * math.cos(math.pi / 2 + math.pi / 2 * j / 10), hc - rf + rf * math.sin(math.pi / 2 + math.pi / 2 * j / 10)) for j in range(11)]
    t.sweep("shroud", [(cx - W / 2 - 0.006, cy, hb), (cx + W / 2 + 0.006, cy, hb)], [(-y, z) for y, z in prof], up=(0, 0, 1), soft=0.006)
    t.box("picture", (cx, cy + 0.025, H - 0.0002), (W - 0.08, D - 0.13, 0.002), soft=0.004)


def _shroud(t, T, cx, cy, W, D, H, n, pt):
    zb = FOOT_H + 0.006
    hc = 0.10                                      # the rounded top cap
    hb = H - hc
    for sx in (1, -1):                             # the side panels
        t.box("shroud", (cx + sx * (W / 2 - 0.006), cy, (zb + hb) / 2), (0.012, D, hb - zb), soft=0.003)
    t.box("shroud", (cx, cy + D / 2 - 0.006, (zb + hb) / 2), (W - 0.024, 0.012, hb - zb), soft=0.003)        # the back
    # the front panel, its window up the right of centre (the numbers and the pin), the placard on its top
    yf = cy - D / 2 + 0.006
    t.box("shroud2", (cx, yf, (zb + hb) / 2), (W - 0.024, 0.012, hb - zb), soft=0.004)
    wx = cx + 0.05
    z0w, z1w = zb + 0.10, hb - 0.32
    t.box("acrylic", (wx, yf - 0.0065, (z0w + z1w) / 2), (0.05, 0.002, z1w - z0w), soft=0.0005)
    t.box("chrome", (wx, yf - 0.002, (z0w + z1w) / 2), (0.012, 0.004, z1w - z0w), soft=0.0)
    for i in range(0, n, 2):
        z = z0w + 0.03 + (i + 0.5) * pt * ((z1w - z0w - 0.06) / (n * pt))
        val = (i + 1) * T.get("step", 5) + T.get("start", 0)
        t.text("label", str(val), (wx - 0.05, yf - 0.0062, z), 0.012, depth=0.0003)
    t.cyl("plastic", (wx, yf - 0.03, z0w + 0.4 * (z1w - z0w)), 0.012, 0.05, axis="y", seg=16, soft=0.003)     # the pin
    _placard(t, T, cx, yf - 0.0065, hb - 0.16, W - 0.10, 0.20)
    # the rounded top cap: a half round along x over the panels
    half = [(-D / 2 * math.cos(math.pi * i / 16), hc * math.sin(math.pi * i / 16)) for i in range(17)]
    t.sweep("shroud", [(cx - W / 2, cy, hb), (cx + W / 2, cy, hb)], [(-dy, dz) for dy, dz in half], up=(0, 0, 1), soft=0.004)

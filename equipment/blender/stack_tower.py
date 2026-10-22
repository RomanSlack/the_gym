"""One weight-stack tower builder for the selectorized machines: each piece's model.py calls tower(k, T, c, rz) with its
numbers in a spec T and builds its own frame, lever and pads around the tower; the cable leaves the tower at the
returned point and the piece routes it on to its lever.

Two styles (read off the makers' photos, 2026-10-22):
  "open"    Hammer Strength Select: a steel frame front and back (the post on one side straight, the other bending round
            into the top beam), the front open (the stack, rods and top plate in view, the weights printed on the
            plates), the exercise placard across the top front and back, a frosted acrylic panel the full height of
            the back with HAMMER STRENGTH low on it.
  "shroud"  Life Fitness Insignia: a closed tower (side panels, a dark front panel, a rounded top cap), the placard on
            the front's top, a narrow window up the front showing the weight numbers and the selector pin.
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
    rp = (T["rods"] + 0.08, D - 0.10) if T["style"] == "open" else (W - 0.024, D - 0.024)   # to the frames / the panels
    t.box("frame", (cx, cy, rod_top + 0.01), (rp[0], rp[1], 0.02), soft=0.002)
    zp = rod_top + 0.10
    t.box("frame", (cx, cy, (rod_top + 0.02 + zp - 0.04) / 2), (0.05, 0.06, zp - 0.04 - rod_top - 0.02), soft=0.002)
    t.pulley((cx, cy, zp), 0.045, axis="x")
    t.cable([(cx, cy, ztop - 0.01), (cx, cy, ztop + 0.10), (cx, cy - 0.045, zp - 0.02), (cx, cy - 0.045, zp)])
    out = (cx, cy - 0.046, zp)
    if T["style"] == "open":
        _open(t, T, cx, cy, W, D, H, n, pt, ztop)
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

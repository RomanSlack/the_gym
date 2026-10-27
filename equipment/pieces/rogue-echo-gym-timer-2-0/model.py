"""Rogue Echo Gym Timer 2.0 (refs/: ref_01 on a box showing 10:37:57: a black case, six red LED digits with colons,
the unlit segments faint, ROGUE in white bottom left, the remote; ref_02 / ref_04 on its floor stand; ref_03 the phone
remote; ref_05 / ref_06 on a wall and a rig). The linked page: 24.5 x 8 x 2.5 in, 5 in LED digits, black with the
Rogue logo bottom left, keyholes 16 in apart and VESA 100, a remote. Fetched 2026-10-25. Built to the two gates and
README point 9. On a display wall section (not the piece), high enough to read over a room.

DESIGN SPEC (gate 1)
1. Use. The clock and the interval timer for the floor: read from across the room; set from the remote.
2. Each mass named (ref_01): the case, black, its face dark; six digits of red LED segments, 5 in high, with two
   colons; ROGUE in white bottom left.
3. Adjustments. None (its modes from the remote).
4. Load path. The case on two keyhole screws.
5. Fit range. Hung at 2.40 m (its middle): read by every user (1.55 / 1.78 / 1.95 m) from anywhere on the floor, above
   heads and racks. No figure.
6. Size. 0.62 x 0.06 x 0.20 m.
Axes: metres, floor z = 0; the wall's face at y = 0, the timer on it facing -y.
"""
IN = 0.0254
L, H, D = 24.5 * IN, 8 * IN, 2.5 * IN
ZC = 2.40
DIG = 5 * IN
SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
        "8": "abcdefg", "9": "abcdfg"}

LOOK = {
    "case": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15),
    "face": dict(color=(0.006, 0.006, 0.007), rough=0.5, coat=0.0),
    "led": dict(color=(1.0, 0.02, 0.02), rough=0.4, coat=0.0, emit=1.2),
    "dim": dict(color=(0.010, 0.003, 0.003), rough=0.6, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
    "wall": dict(color=(0.72, 0.72, 0.72), rough=0.9, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 5, 1.0), "front": (0, 2, 1.0), "side": (90, 2, 1.0), "back_three_quarter": (-70, 15, 1.0)}
DETAILS = {
    "detail_face": ((0.0, -0.95, 2.42), (0.0, -0.05, 2.40), 30),     # the digits, ROGUE (ref_01)
}


def digit(k, ch, x, y, z):
    """A seven-segment digit centred at (x, z) on the face plane y; lit segments red, the rest faint."""
    w, h, t = DIG * 0.42, DIG, DIG * 0.085
    seg = {"a": (0, h / 2, w, t), "g": (0, 0, w, t), "d": (0, -h / 2, w, t), "f": (-w / 2, h / 4, t, h / 2),
           "b": (w / 2, h / 4, t, h / 2), "e": (-w / 2, -h / 4, t, h / 2), "c": (w / 2, -h / 4, t, h / 2)}
    for s, (dx, dz, sw, sh) in seg.items():
        lit = s in SEGS[ch]
        k.box("led" if lit else "dim", (x + dx, y, z + dz), (sw * 0.9 if sw > sh else sw, 0.0012, sh * 0.85 if sh > sw else sh),
              soft=0.0)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    if getattr(k, "display", True):                                  # the display wall (not the piece: off when it hangs on a real wall)
        k.box("wall", (0, 0.05, 1.6), (1.2, 0.10, 3.2), soft=0.0)                                      # display wall
    k.box("case", (0, -D / 2, ZC), (L, D, H), soft=0.006)                                           # the case
    yf = -D - 0.0003
    k.box("face", (0, yf + 0.0004, ZC + 0.008), (L - 0.02, 0.0012, H - 0.03), soft=0.0)
    y = yf - 0.0006
    xs = (-0.215, -0.14, -0.04, 0.035, 0.135, 0.21)  # two digits, a colon, two, a colon, two (ref_01)
    for ch, x in zip("103757", xs):
        digit(k, ch, x, y, ZC + 0.012)
    for xc in (-0.09, 0.085):                           # the colons
        for dz in (0.025, -0.02):
            k.box("led", (xc, y, ZC + 0.012 + dz), (0.009, 0.0012, 0.009), soft=0.0)
    k.text("white", "ROGUE", (-L / 2 + 0.07, y, ZC - H / 2 + 0.022), 0.022, depth=0.0006)

"""Rogue Monster Band Pegs 2.0, a 4-pack, matte black (refs/: ref_01 four pegs and a Monster foot; ref_02 / ref_04 a
peg through a rack's foot, a band from it to the bar; ref_03 the cap against the tube; ref_05 the machined cap). The
linked page: 11 in long with the cap, 7-3/8 in standing out of a 3 in tube, 1 in diameter, carbon steel, the machined
version's chamfered low cap, 9 lb the four, Monster racks / rigs / wall mounts only. Fetched 2026-10-24 / 25. Built to
the two gates and README point 9. Shown through a 36 in section of a Monster foot (3 x 3 in, numbered holes) on the
floor (display only).

DESIGN SPEC (gate 1)
1. Use. A peg goes through a hole low on the rack (a foot, an upright's lowest holes), a band loops over its standing
   end and up to the bar: band resistance for squats, presses, pulls.
2. Each mass named (ref_01 / ref_05): the peg, a 1 in carbon steel pin, its machined cap on the near end (chamfered,
   1.6 in across, low), slid through the tube's two walls until the cap meets the face, 7-3/8 in standing out of the far
   face. Nothing else: gravity and the band's pull keep it seated.
3. Adjustments. Which hole.
4. Load path. The band's pull on the standing end, the pin in bending over the far wall, the near wall, the rack.
5. Fit range. None held or stood on; the band peg's job is the band's line: through the foot's holes the band rises
   from 0.04 m to the bar's height at any user's (1.55 / 1.78 / 1.95 m) rack position, the standing end long enough
   for two bands (7-3/8 in).
6. Size. Each peg 0.28 m long, 1 in.
Axes: metres, floor z = 0; the foot along x, the pegs out toward -y.
"""

IN = 0.0254
TB = 3 * IN
L_FOOT = 36 * IN
HOLES_AT = (5, 8, 11, 14)             # the pegs' holes (numbered along the foot, 2 in pitch)

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # the foot (display)
    "peg": dict(color=(0.02, 0.02, 0.022), rough=0.35, metal=0.6, coat=0.1),                    # matte black
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.6, 0.6, 0.62), rough=0.4, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 10, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0)}
DETAILS = {
    "detail_cap": ((0.45, 0.45, 0.30), (0.05, 0.0, 0.05), 35),          # ref_03: the caps against the back face
    "detail_peg": ((-0.35, -0.55, 0.30), (0.0, -0.12, 0.05), 35),       # the standing ends, the numbers
}


def hx(n):
    return -L_FOOT / 2 + 2 * IN + (n - 1) * 2 * IN


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zc = TB / 2 + 0.006
    k.bar("frame", (-L_FOOT / 2, 0, zc), (L_FOOT / 2, 0, zc), TB, TB, r=0.004)
    for x in (-L_FOOT / 2 + 0.05, L_FOOT / 2 - 0.05):
        k.box("rubber", (x, 0, 0.003), (0.06, TB, 0.006), soft=0.001)                            # its pads
    for n in range(1, 17):                              # the holes through it, numbered on the front face
        x = hx(n)
        if x > L_FOOT / 2 - 1.5 * IN:
            break
        for s in (1, -1):
            if n not in HOLES_AT:
                k.cyl("hole", (x, s * (TB / 2 + 0.0003), zc), 0.5 * IN, 0.0008, axis="y", seg=16, soft=0.0)
        k.cyl("hole", (x, 0, zc + TB / 2 + 0.0003), 0.5 * IN, 0.0008, seg=16, soft=0.0)
        k.text("label", str(n), (x + 0.6 * IN, -TB / 2 - 0.0003, zc - 0.9 * IN), 0.012, depth=0.0003)
    for n in HOLES_AT:                                  # the pegs: the cap on the back face, out of the front
        x = hx(n)
        y_cap = TB / 2
        k.tube("peg", (x, y_cap, zc), (x, -TB / 2 - 7.375 * IN, zc), 0.5 * IN, seg=24)
        k.cyl("peg", (x, y_cap + 0.005, zc), 0.8 * IN, 0.010, axis="y", seg=32, soft=0.003)    # the cap
        k.cyl("peg", (x, -TB / 2 - 7.375 * IN, zc), 0.5 * IN, 0.002, axis="y", seg=24, soft=0.001)  # chamfered end

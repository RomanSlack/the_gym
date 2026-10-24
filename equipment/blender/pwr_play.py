"""Life Fitness PWR Play: the modular cable system, one builder for every configuration (the 5 Stations piece now, the
gym's maze of towers later).

Read off the PWR Play assembly instructions (Life Fitness, 2025: the station drawings, the top mounts, the crossbar
connectors' 73.5 / 85.5 / 97.5 / 100.5 in spacings, the oval feet) and Life Fitness's figures for the same frame as the
Multi-Jungle (the Core 83 x 83 x 239 cm; a lat pulldown or row station 68 x 95 x 234; an adjustable pulley tower 37 x 47
x 234), the look off the dealer's photos (Charcoal frame, black upholstery, chrome guide rods and carriage tracks).
The Core: four corner legs, each a bent tube up and curving in over the top to the round hub with its cap (an X in plan),
cross-members between the legs at the top and the bottom (the stations bolt to them), the base X to the bottom hub, oval
feet. A station sits on one face: its stack inside the Core behind that face, its top mount (a boom with pulleys) out
under the top cross-member, its seat, bench, rope or carriage outside.
Coordinates: a station is built in its face's frame (u along the face, the user's right as they face the Core; v out
from the Core's centre; z up) and turned into the world by quarter turns, so boxes and stacks stay square.
"""
import math

LOOK = {
    "frame": dict(color=(0.042, 0.043, 0.047), rough=0.42, metal=0.35, coat=0.0, bump=(1400, 0.06)),   # Charcoal
    "boom": dict(color=(0.026, 0.027, 0.03), rough=0.45, metal=0.35, coat=0.0, bump=(1400, 0.06)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "plate": dict(color=(0.03, 0.031, 0.034), rough=0.42, metal=0.45, coat=0.0, bump=(2200, 0.06)),   # textured charcoal
    "grip": dict(color=(0.11, 0.11, 0.12), rough=0.7, coat=0.0, bump=(2500, 0.12)),
    "red": dict(color=(0.42, 0.03, 0.025), rough=0.4, coat=0.0),
    "white": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "stainless": dict(color=(0.78, 0.78, 0.79), rough=0.26, metal=1.0, aniso=0.5),           # brushed stainless (ref_02 / ref_03)
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.08, metal=1.0, coat=0.0),
    "steel": dict(color=(0.62, 0.62, 0.64), rough=0.25, metal=1.0, aniso=0.3),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "cable": dict(color=(0.05, 0.05, 0.055), rough=0.4, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "blue": dict(color=(0.08, 0.35, 0.7), rough=0.4, coat=0.0),
    "label": dict(color=(0.75, 0.75, 0.77), rough=0.4, coat=0.0),
    "rope": dict(color=(0.02, 0.02, 0.022), rough=0.8, coat=0.0, bump=(900, 0.3)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
}

FOOT_H = 0.021                      # the oval feet (13/16 in, the manual's Foot Dimensions)
A = 0.36                            # the Core's legs' centres from its centre (x and y): 83 cm over the feet
LEG = 0.076                         # the leg tube: flat-faced, rounded corners (ref_07 / ref_08; ref_03 / ref_06 close up)
ZARM = 2.29                         # the legs' arms over the top, into the hub
HUB = (0.12, 2.255, 2.38)           # the top hub, a small black cap where the legs meet (ref_07 / ref_08): radius, bottom, top;
                                    # the crossbar and the booms butt against its side
ZTC, ZBC = 2.03, 0.13               # the top and bottom cross-members (centres)
CM = (0.05, 0.076)                  # a cross-member: across (v), tall
VS = A - 0.085                      # a station's stack (v): right behind its face (ref_08: the plates behind the pads)
RTR = 0.022                         # the top rail across each face: a round tube (ref_08), under the legs' bends
RP = 0.085                          # a station's one big top pulley (ref_08): its radius; the cable runs at 0.86 of it
ZTP = 2.17                          # its centre: up inside the bends, over the stack's cable


class Face:
    """One face of a Core (or a tower) at centre c = (x, y), facing `out` ((0, -1), (1, 0), ...): maps (u, v, z) to
    the world and wraps the kit's calls."""

    def __init__(self, k, c, out):
        self.k, self.c = k, c
        self.o = out
        self.u = (-out[1], out[0])

    def p(self, u, v, z):
        return (self.c[0] + u * self.u[0] + v * self.o[0], self.c[1] + u * self.u[1] + v * self.o[1], z)

    def d(self, du, dv, dz):
        return (du * self.u[0] + dv * self.o[0], du * self.u[1] + dv * self.o[1], dz)

    def _size(self, su, sv, sz):
        return (su, sv, sz) if abs(self.u[0]) > 0.5 else (sv, su, sz)

    def _ax(self, a):
        if a == "z":
            return "z"
        vec = self.u if a == "u" else self.o
        return "x" if abs(vec[0]) > 0.5 else "y"

    def _sax(self, a):
        """A signed face axis ('+u', '-v', '+z') -> the world's ('+x', ...)."""
        if a[1] == "z":
            return a
        vec = self.u if a[1] == "u" else self.o
        s = (1 if a[0] == "+" else -1) * (vec[0] + vec[1])
        return ("+" if s > 0 else "-") + ("x" if abs(vec[0]) > 0.5 else "y")

    def box(self, mat, c, size, soft=0.0015):
        self.k.box(mat, self.p(*c), self._size(*size), soft=soft)

    def bar(self, mat, a, b, w, h=None, up="z", **kw):
        upv = (0, 0, 1) if up == "z" else self.d(*{"u": (1, 0, 0), "v": (0, 1, 0)}[up])
        for key in ("cut0", "cut1"):
            if key in kw and kw[key]:
                q, n = kw[key]
                kw[key] = (self.p(*q), self.d(*n))
        self.k.bar(mat, self.p(*a), self.p(*b), w, h, up=upv, **kw)

    def tube(self, mat, a, b, r, **kw):
        self.k.tube(mat, self.p(*a), self.p(*b), r, **kw)

    def sweep(self, mat, pts, prof, up="z", **kw):
        upv = (0, 0, 1) if up == "z" else self.d(*{"u": (1, 0, 0), "v": (0, 1, 0)}[up])
        for key in ("cut0", "cut1"):                    # cut planes are given in the face's frame too
            if key in kw and kw[key]:
                q, n = kw[key]
                kw[key] = (self.p(*q), self.d(*n))
        self.k.sweep(mat, [self.p(*q) for q in pts], prof, up=upv, **kw)

    def cyl(self, mat, c, r, h, axis="z", **kw):
        self.k.cyl(mat, self.p(*c), r, h, axis=self._ax(axis), **kw)

    def disc(self, mat, c, ro, ri, h, axis="u", **kw):
        self.k.disc(mat, self.p(*c), ro, ri, h, axis=self._ax(axis), **kw)

    def bolt(self, c, axis, **kw):
        self.k.bolt(self.p(*c), self._sax(axis), **kw)

    def pulley(self, c, r, axis="u", w=0.025):
        self.k.pulley(self.p(*c), r, axis=self._ax(axis), w=w)

    def cable(self, pts, r=0.0028):
        self.k.cable([self.p(*q) for q in pts], r=r)

    def text(self, mat, body, c, size, depth=0.0006, spin=0.0):
        """Lettering on a plane facing out (+v)."""
        rz = math.atan2(self.o[1], self.o[0]) + math.pi / 2
        self.k.text(mat, body, self.p(*c), size, rz=rz, depth=depth, spin=spin)

    def stack(self, v, vcm, n=16, rods=0.22, pin_at=5, hang=True, step=7.5):
        """A selectorized stack at (0, v), its frame's cross-members at vcm, as Life Fitness's look in the photos
        (ref_05 / ref_06): the base plate on the bottom cross-member, a round rubber cushion round each guide rod, n
        charcoal plates 0.30 (u) x 0.16 (v), each with rounded edges and a fine seam to the next, the pin's hole in the
        middle of each plate's front (no slot showing), the white numbers either side of it (ref_05: 5 on the top
        plate, then `step` more per plate down the stack), the pin with its black knob; the thick top plate with the cable's boss, the
        bushings and red collars on the rods; the chrome rods up to the rod plate (hung on two straps below a top
        mount's pulley, or right under the top rail). Returns the top of the cable's boss."""
        z0 = ZBC + CM[1] / 2
        lo, hi = min(v - 0.09, vcm - CM[0] / 2), max(v + 0.09, vcm + CM[0] / 2)
        self.box("frame", (0.0, (lo + hi) / 2, z0 + 0.005), (0.42, hi - lo, 0.010), soft=0.002)
        z0 += 0.010
        W, Dp, t = 0.30, 0.16, 0.0254
        for su in (-1, 1):                              # the cushions the stack rests on, round the rods
            self.cyl("rubber", (su * rods / 2, v, z0 + 0.03), 0.032, 0.06, seg=28, soft=0.006)
        zb = z0 + 0.06
        for i in range(n):
            zc = zb + i * t + t / 2
            self.box("plate", (0.0, v, zc), (W, Dp, t - 0.0025), soft=0.005)
            for su in (-1, 1):                          # the total lifted with the pin here: 5 on the top plate, +step each
                self.text("white", f"{5 + (n - i) * step:g}", (su * 0.036, v + Dp / 2 + 0.0004, zc), 0.0135, depth=0.0004)
            self.cyl("hole", (0.0, v + Dp / 2 + 0.0002, zc), 0.0065, 0.001, axis="v", seg=16)   # the pin's hole
        self.tube("chrome", (0.0, v, zb), (0.0, v, zb + n * t + 0.01), 0.0095, seg=14)            # the stem in it
        zp = zb + pin_at * t + t / 2
        self.tube("chrome", (0.0, v + Dp / 2 - 0.02, zp), (0.0, v + Dp / 2 + 0.035, zp), 0.0055, seg=14)
        self.cyl("plastic", (0.0, v + Dp / 2 + 0.05, zp), 0.019, 0.032, axis="v", seg=24, soft=0.006)  # its knob
        ztop = zb + n * t
        self.box("plate", (0.0, v, ztop + 0.0225), (W, Dp, 0.045), soft=0.01)                     # the top plate
        self.text("white", "5", (-0.036, v + Dp / 2 + 0.0004, ztop + 0.0225), 0.0135, depth=0.0004)
        self.cyl("hole", (0.0, v + Dp / 2 + 0.0002, ztop + 0.0225), 0.0065, 0.001, axis="v", seg=16)
        self.cyl("plate", (0.0, v, ztop + 0.06), 0.032, 0.03, seg=28, soft=0.006)                  # the cable's boss
        self.cyl("chrome", (0.0, v, ztop + 0.08), 0.012, 0.012, seg=16)
        for su in (-1, 1):                              # the bushings and the red collars where the rods run through
            self.cyl("chrome", (su * rods / 2, v, ztop + 0.05), 0.02, 0.012, seg=24)
            self.cyl("red", (su * rods / 2, v, ztop + 0.0595), 0.0165, 0.007, seg=24)
        zr = 1.80 if hang else ZTC - RTR - 0.012
        hi2 = vcm - CM[0] / 2 - 0.004 if hang else vcm
        self.box("frame", (0.0, (lo + hi2) / 2, zr + 0.006), (0.42, hi2 - lo, 0.012), soft=0.002)
        if hang:
            for su in (-1, 1):
                self.box("frame", (su * 0.21, vcm - CM[0] / 2 - 0.009, (zr + ZTC - CM[1] / 2) / 2), (0.03, 0.01, ZTC - CM[1] / 2 - zr),
                         soft=0.001)
        for su in (-1, 1):
            self.tube("chrome", (su * rods / 2, v, z0), (su * rods / 2, v, zr), 0.0135, seg=24)
        return ztop + 0.086

def looks(k):
    for role, v in LOOK.items():
        if role not in k.looks:
            k.look(**{role: v})


def foot(k, x, y, rz):
    """The oval foot plate under a leg (the manual's Foot Dimensions), long along rz (radians)."""
    k.box("rubber", (x, y, 0.004), (0.19, 0.11, 0.008), rz=rz, soft=0.004)
    k.box("frame", (x, y, 0.008 + (FOOT_H - 0.008) / 2), (0.17, 0.10, FOOT_H - 0.008), rz=rz, soft=0.012)
    for s in (-1, 1):
        k.cyl("hole", (x + s * 0.065 * math.cos(rz), y + s * 0.065 * math.sin(rz), FOOT_H + 0.0004), 0.007, 0.001, seg=14)


def core(k, c):
    """The Core at c = (x, y): the four bent legs into the top hub, the cap, the cross-members top and bottom, the base X
    to the bottom hub, the feet, the logo up each leg's outer corner, the station holes."""
    looks(k)
    cx, cy = c
    ha = HUB[0] + 0.01
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = cx + sx * A, cy + sy * A
            hx, hy = cx + sx * ha / math.sqrt(2), cy + sy * ha / math.sqrt(2)
            k.sweep("frame", [(x, y, FOOT_H), (x, y, ZARM), (hx, hy, ZARM)], k.rect(LEG, LEG, 0.022), bend=0.15,
                    up=(1, 0, 0), cut0=((0, 0, FOOT_H), (0, 0, 1)), weld=True)       # faces square to the Core's faces
            foot(k, x, y, math.atan2(sy, sx))
            k.bar("frame", (x - sx * 0.027, y - sy * 0.027, 0.07), (cx + sx * 0.05, cy + sy * 0.05, 0.07), 0.05, 0.012,
                  up=(0, 0, 1))                         # the base X, from the leg's inner face to the bottom hub
            for i in range(6):
                k.cyl("hole", (x + sx * (LEG / 2 + 0.0002), y, 0.55 + i * 0.20), 0.006, 0.001, axis="x", seg=12)
    k.cyl("frame", (cx, cy, (HUB[1] + HUB[2]) / 2), HUB[0], HUB[2] - HUB[1], seg=48, soft=0.006)
    k.cyl("plastic", (cx, cy, HUB[2] + 0.0175), HUB[0] + 0.01, 0.035, seg=48, soft=0.012)
    k.cyl("plastic", (cx, cy, 0.07), 0.07, 0.03, seg=36, soft=0.004)                                # bottom hub
    for o in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        f = Face(k, c, o)
        f.bar("frame", (-A + LEG / 2, A, ZBC), (A - LEG / 2, A, ZBC), CM[0], CM[1], up="z",
              cut0=((-A + LEG / 2, 0, 0), (1, 0, 0)), cut1=((A - LEG / 2, 0, 0), (1, 0, 0)), weld=True)
        f.tube("frame", (-A + LEG / 2 - 0.004, A, ZTC), (A - LEG / 2 + 0.004, A, ZTC), RTR, seg=24)   # the round top rail
    # the Life Fitness script up two legs' outer corners
    for sx, sy in ((1, -1), (-1, 1)):
        x, y = cx + sx * (A + LEG / 2 + 0.001), cy + sy * A
        k.text("label", "Life Fitness", (x, y, 1.45), 0.05, rz=math.pi / 2 * (1 if sx > 0 else -1), depth=0.0006,
               spin=math.pi / 2)


def top_mount(f, length, zt):
    """A station's top pulley (ref_08: one big black pulley up inside the legs' bends at the face): its housing's two
    cheeks standing on the round top rail, bolted through it, the pulley on its axle, the hubs; the cable up from the
    stack's top plate (zt) over the pulley's top and down just in front of the face. `length` is kept for the stations'
    calls (the cable now always drops at the face). Returns (v, z) where the cable leaves the pulley's outer side."""
    g = 0.86 * RP - 0.003                               # the groove, a hair inside it
    vp = VS + g                                         # the cable rises off the stack's centre on the pulley's near side
    lo, hi = vp - g + 0.012, vp + 0.10                 # the saddle on the rail: clear of the cable rising at vp - g
    zs0 = ZTC + RTR
    f.box("boom", (0.0, (lo + hi) / 2, zs0 + 0.005), (0.08, hi - lo, 0.010), soft=0.003)
    for su in (-1, 1):                                  # the cheeks up from it round the pulley, their tops under the cable
        f.box("boom", (su * 0.036, (lo + hi) / 2, (zs0 + ZTP + 0.04) / 2), (0.008, hi - lo, ZTP + 0.04 - zs0), soft=0.02)
    f.bolt((0.0, A, zs0 + 0.010), "+z", size=0.014)
    f.pulley((0.0, vp, ZTP), RP, axis="u")
    f.tube("chrome", (-0.04, vp, ZTP), (0.04, vp, ZTP), 0.009, seg=12)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.02, vp, ZTP), 0.026, 0.006, axis="u", seg=24)
    f.cable([(0.0, vp - g, zt), (0.0, vp - g, ZTP)])
    return (vp + g, ZTP)


ZBM = 2.31                          # a pulldown / pushdown boom's centre: level with the cap, the very top (ref_08)
RPB = 0.07                          # the pulleys under a boom


def boom_mount(f, reach, zt, end=True):
    """The big boom a pulldown (or a pushdown) hangs from (ref_08 / ref_07; the manual's LPP-PD and LPP-TP drawings):
    a heavy rounded tube straight out from the Core's top cap, at the very top, `reach` past the face, its end capped; a
    pulley hung under it over the stack and one at its end, each between two cheek plates; the cable up from the stack's
    top plate (zt), over the inner pulley, out along under the boom, over the end pulley and down. Returns (v, z) where
    the cable drops off the end pulley."""
    g = 0.86 * RPB - 0.003
    bw, bh = 0.10, 0.09
    v1 = A + reach
    zp = ZBM - bh / 2 - 0.012 - RPB
    vi, vo = VS + g, v1 - 0.09
    f.bar("boom", (0.0, HUB[0] - 0.003, ZBM), (0.0, v1, ZBM), bw, bh, r=0.035, up="z")
    f.box("plastic", (0.0, v1 + 0.005, ZBM), (bw - 0.01, 0.012, bh - 0.01), soft=0.02)            # its end cap
    for vp in ((vi, vo) if end else (vi,)):
        for su in (-1, 1):
            ztop = ZBM - bh / 2 + 0.006                 # up into the boom's rounded underside
            f.box("boom", (su * 0.036, vp, (ztop + zp - 0.04) / 2), (0.008, 0.13, ztop - zp + 0.04), soft=0.02)
            f.bolt((su * 0.04, vp, zp), "+u" if su > 0 else "-u", size=0.016)
        f.pulley((0.0, vp, zp), RPB, axis="u")
        f.tube("chrome", (-0.04, vp, zp), (0.04, vp, zp), 0.009, seg=12)
    f.cable([(0.0, vi - g, zt), (0.0, vi - g, zp)])
    if not end:                                         # the cable goes on along under the boom to whatever hangs there
        return (vi, zp + g)
    f.cable([(0.0, vi, zp + g), (0.0, vo, zp + g)])
    return (vo + g, zp)


def placard(f, u, z):
    f.box("placard", (u, A + LEG / 2 + 0.001, z), (0.07, 0.002, 0.30), soft=0.0)
    for i in range(3):
        f.box("blue", (u, A + LEG / 2 + 0.0024, z + 0.09 - i * 0.075), (0.05, 0.0008, 0.06), soft=0.0)


def guard(f, z=0.88, bow=0.10):
    """The curved black bar across a station's face just above its stack, bowing out between the face's two legs
    (ref_07 / ref_08)."""
    e, w = A - LEG / 2, A - LEG / 2 - 0.03
    f.sweep("frame", [(-w, A, z), (-0.22, A + bow, z), (0.22, A + bow, z), (w, A, z)], f.k.circle(0.024, 20), bend=0.12,
            soft=0.0, cut0=((-e, 0, 0), (1, 0, 0)), cut1=((e, 0, 0), (1, 0, 0)), weld=True)    # cut flush to the legs' faces


def pulldown(k, c, out):
    """Pulldown (LPP-PD), as the render has it (ref_08 / ref_07; the manual's LPP-PD drawing): the stack right behind
    the face; the big boom straight out from the Core's top cap at the very top, the lat bar hung from its end out over
    the seat; the station's upright on the floor beam back to the Core, the seat out from it under the bar, the knee pads
    on their pivoting arm with the pop pin and sector plate (adjustable); laid out for a seated 1.78 m user (hips under the
    bar, thighs under the pads, hands up to the bar)."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, n=17, hang=False, step=15)          # the heavy stack: 5 to 260
    vo, zo = boom_mount(f, 0.52, zt)                    # the boom out over the user (ref_08)
    zb = 1.95                                           # the bar at rest, hung from the boom's end over the hips
    f.cable([(0.0, vo, zo), (0.0, vo, zb + 0.06)])
    f.box("steel", (0.0, vo, zb + 0.035), (0.03, 0.02, 0.05), soft=0.002)
    bar = [(-0.60, vo + 0.03, zb - 0.09), (-0.46, vo, zb), (0.46, vo, zb), (0.60, vo + 0.03, zb - 0.09)]
    f.sweep("frame", bar, f.k.circle(0.0145, 18), bend=0.08, soft=0.0)
    for e, n_ in ((bar[0], bar[1]), (bar[-1], bar[-2])):
        d = [e[i] - n_[i] for i in range(3)]; ln = math.sqrt(sum(x * x for x in d)); d = [x / ln for x in d]
        f.tube("chrome", e, tuple(e[i] + d[i] * 0.012 for i in range(3)), 0.0155, seg=18)
    for s in (-1, 1):                                   # the grey grips most of its length (ref_04 / ref_05)
        f.tube("grip", (s * 0.06, vo, zb), (s * 0.45, vo, zb), 0.019, soft=0.003)
    guard(f)
    # the station's upright (the manual's LPP-PD drawing; ref_05): on the floor beam out from the bottom cross-member,
    # leaning in toward the Core as it rises; the seat cantilevered out from its foot on an arm; the knee pads on an
    # axle carried by two arm plates pivoting on a pin through the upright, held at their height by a pop pin in one of
    # the holes round a sector plate on the upright's side (Roman: the knee pads adjustable)
    vs, zs = vo + 0.02, 0.45                            # the seat: the hips right under the bar
    zb0 = ZBC + 0.038                                   # the floor beam's top
    vb, vt, zut = vs - 0.26, vs - 0.42, 1.00            # the upright: its foot, its top
    def vu(z):
        return vb + (vt - vb) * (z - zb0) / (zut - zb0)
    f.bar("frame", (0.0, A + CM[0] / 2, ZBC), (0.0, vb + 0.04, ZBC), 0.076, 0.076, up="z", cut0=((0, A + CM[0] / 2, 0), (0, 1, 0)),
          weld=True)
    f.box("frame", (0.0, vb, (FOOT_H + ZBC - 0.038) / 2), (0.08, 0.08, ZBC - 0.038 - FOOT_H), soft=0.004)
    f.box("rubber", (0.0, vb, FOOT_H / 2), (0.20, 0.14, FOOT_H), soft=0.006)
    f.bar("frame", (0.0, vb, zb0), (0.0, vt, zut), 0.07, 0.07, r=0.014, up="u", cut0=((0, 0, zb0), (0, 0, 1)), weld=True)
    f.box("plastic", (0.0, vt, zut + 0.004), (0.074, 0.074, 0.012), soft=0.004)                    # its cap
    zsa = 0.30                                          # the seat's arm out from the upright, its post up to the seat
    zsp = zs - 0.045                                    # the seat plate's centre, the pad on it
    nl = math.hypot(vt - vb, zut - zb0); nv, nz = (zut - zb0) / nl, -(vt - vb) / nl    # the upright's +v face's normal
    f.bar("frame", (0.0, vu(zsa), zsa), (0.0, vs - 0.0325, zsa), 0.065, 0.065, r=0.01, up="z",
          cut0=((0.0, vu(zsa) + 0.035 / nv, zsa), (0.0, nv, nz)), weld=True)
    f.bar("frame", (0.0, vs, zsa - 0.0325), (0.0, vs, zsp - 0.006), 0.065, 0.065, r=0.01, up="v")
    f.box("frame", (0.0, vs, zsp), (0.24, 0.24, 0.012), soft=0.003)
    f.box("pad", (0.0, vs + 0.02, zsp + 0.006 + 0.045), (0.38, 0.34, 0.09), soft=0.035)
    zpv = 0.84                                          # the knee pads' pivot, through the upright
    P = (vu(zpv), zpv)
    vk, zk = vs - 0.30, 0.66                            # the pads' axle at the middle setting: over the thighs
    L = math.hypot(vk - P[0], zk - P[1]); th = math.atan2(zk - P[1], vk - P[0])
    ext = (P[0] + (vk - P[0]) * (L + 0.03) / L, P[1] + (zk - P[1]) * (L + 0.03) / L)
    pre = (P[0] - (vk - P[0]) * 0.035 / L, P[1] - (zk - P[1]) * 0.035 / L)
    for uc in (-0.0465, 0.0395):                        # the two arm plates (the -u one outside the sector plate)
        f.bar("frame", (uc, pre[0], pre[1]), (uc, ext[0], ext[1]), 0.05, 0.008, r=0.003, up="u")
    rs = 0.115                                          # the sector plate: an arc of holes round the pivot
    sect = [((0.085 if i < 0 else 0.145) * math.cos(th + math.radians(a)), (0.085 if i < 0 else 0.145) * math.sin(th + math.radians(a)))
            for i, a in [(-1, a) for a in range(-45, 46, 5)] + [(1, a) for a in range(45, -46, -5)]]
    f.sweep("frame", [(-0.0415, P[0], P[1]), (-0.0355, P[0], P[1])], sect, up="z", soft=0.0015)
    f.box("frame", (-0.038, P[0], P[1]), (0.006, 0.07, 0.07), soft=0.002)                            # welded on the upright
    for a in range(-40, 41, 10):
        f.cyl("hole", (-0.0418, P[0] + rs * math.cos(th + math.radians(a)), P[1] + rs * math.sin(th + math.radians(a))),
              0.0065, 0.001, axis="u", seg=14)
    pin = (P[0] + rs * math.cos(th), P[1] + rs * math.sin(th))     # the pop pin through the outer arm plate
    f.tube("chrome", (-0.04, pin[0], pin[1]), (-0.062, pin[0], pin[1]), 0.006, seg=14)
    f.cyl("plastic", (-0.074, pin[0], pin[1]), 0.017, 0.026, axis="u", seg=24, soft=0.005)
    f.tube("chrome", (-0.055, P[0], P[1]), (0.048, P[0], P[1]), 0.008, seg=14)                       # the pivot pin
    for ue in (-0.053, 0.046):
        f.cyl("bolt", (ue, P[0], P[1]), 0.014, 0.006, axis="u", seg=6)
    f.tube("steel", (-0.31, vk, zk), (0.31, vk, zk), 0.018, seg=18)
    for s in (-1, 1):
        f.tube("pad", (s * 0.065, vk, zk), (s * 0.30, vk, zk), 0.066, seg=40, soft=0.012)
        f.cyl("plastic", (s * 0.305, vk, zk), 0.05, 0.012, axis="u", seg=28, soft=0.003)
    placard(f, A, 1.25)
    return dict(seat=(vs, zs), knee=(vk, zk), bar=(vo, zb))


def row(k, c, out):
    """Row (LPP-RW), as the render has it (ref_08 / ref_07): the stack right behind the face, the cable from a short top
    mount down at a slant to the low pulley on top of the row arm; the arm rising from the bench beam with the big
    perforated foot plate on its face; the V handle resting at the pulley; the long bench pad on its beam, the small
    angled foot stop at its near end, the single far leg."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, n=17, hang=False, step=15)          # the heavy stack: 5 to 260
    vo, zo = top_mount(f, 0.06, zt)
    guard(f)
    # the bench beam from the bottom cross-member out to the far leg
    vb1, zp = A + 1.70, 0.45
    f.bar("frame", (0.0, A + CM[0] / 2, ZBC), (0.0, vb1, ZBC), 0.076, 0.076, up="z", cut0=((0, A + CM[0] / 2, 0), (0, 1, 0)),
          weld=True)
    f.bar("frame", (0.0, vb1 - 0.04, FOOT_H), (0.0, vb1 - 0.04, zp - 0.05), 0.07, 0.07, up="v", cut0=((0, 0, FOOT_H), (0, 0, 1)),
          weld=True)
    f.box("rubber", (0.0, vb1 - 0.04, FOOT_H / 2), (0.20, 0.12, FOOT_H), soft=0.006)
    f.bar("frame", (0.0, A + 0.85, ZBC + 0.038), (0.0, A + 0.85, zp - 0.05), 0.06, 0.06, up="v",
          cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    f.box("frame", (0.0, A + 1.20, zp - 0.04), (0.24, 0.84, 0.024), soft=0.002)
    f.box("pad", (0.0, A + 1.20, zp + 0.008), (0.30, 0.92, 0.075), soft=0.03)
    stop = [(0.0, A + 0.70, ZBC + 0.038), (0.0, A + 0.72, 0.40)]                  # the angled foot stop at the bench's near end
    f.sweep("frame", stop, f.k.rect(0.05, 0.05, 0.008), up="u", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    _plate(f, (0.0, A + 0.70, 0.44), 0.20, 0.13, math.radians(40))
    # the row arm: up from the beam, leaning back to the Core, the pulley's cheeks on its top, the pulley, its axle
    va, za = A + 0.34, 0.60
    lean = math.atan2(0.10, 0.282)                      # the arm's lower run and the foot plate on it lean back together
    arm = [(0.0, A + 0.50, ZBC + 0.038), (0.0, A + 0.40, 0.45), (0.0, va, za - 0.07)]
    f.sweep("frame", arm, f.k.rect(0.07, 0.07, 0.012), bend=0.10, up="u", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    for su in (-1, 1):
        f.box("frame", (su * 0.034, va, za - 0.02), (0.008, 0.10, 0.12), soft=0.002)
    f.pulley((0.0, va, za), 0.065, axis="u")
    f.tube("chrome", (-0.036, va, za), (0.036, va, za), 0.008, seg=12)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.015, va, za), 0.022, 0.006, axis="u", seg=24)
    f.cable([(0.0, vo, zo), (0.0, va - 0.054, za + 0.01)])
    # the big perforated foot plate on the arm's face, leaning back to the rower (ref_08)
    zc = 0.36
    vc = A + 0.50 - 0.10 * (zc - ZBC - 0.038) / (0.45 - ZBC - 0.038)
    _plate(f, (0.0, vc + 0.042 * math.cos(lean), zc + 0.042 * math.sin(lean)), 0.42, 0.40, lean, dots=True)
    # the V handle resting at the pulley
    zl = za - 0.04
    f.cable([(0.0, va + 0.054, za), (0.0, va + 0.12, zl)])
    f.box("steel", (0.0, va + 0.122, zl), (0.03, 0.016, 0.02), soft=0.002)
    f.sweep("steel", [(-0.08, va + 0.22, zl - 0.02), (-0.02, va + 0.14, zl), (0.02, va + 0.14, zl), (0.08, va + 0.22, zl - 0.02)],
            f.k.circle(0.012, 16), bend=0.03, soft=0.0)
    for s in (-1, 1):
        f.tube("grip", (s * 0.08, va + 0.22, zl - 0.02), (s * 0.08, va + 0.32, zl - 0.04), 0.017, soft=0.003)
    placard(f, -A, 1.25)
    return dict(seat=(A + 1.00, zp), foot=(A + 0.47, 0.36), handle=(va + 0.27, zl))


def _plate(f, c, w, h, lean, dots=False):
    """A plate w (u) by h, centred at c, its face to +v, leaning back from vertical by `lean` (a foot plate), with the
    rubber tread on its face."""
    u, v, z = c
    sn, cs = math.sin(lean), math.cos(lean)
    n = f.d(0, cs, sn)                                  # its face's normal, in the world
    for mat, off, ww, hh, th in (("frame", 0.0, w, h, 0.014), ("rubber", 0.0085, w - 0.03, h - 0.03, 0.003)):
        cv, cz = v + off * cs, z + off * sn
        f.k.bar(mat, f.p(-ww / 2, cv, cz), f.p(ww / 2, cv, cz), hh, th, up=n, soft=0.003)
    if dots:                                            # the grip dots over the tread (ref_08)
        for i in range(7):
            for j in range(9):
                du, dh = -w / 2 + 0.04 + i * (w - 0.08) / 6, -h / 2 + 0.035 + j * (h - 0.07) / 8
                q = f.p(du, v + 0.0095 * cs - dh * sn, z + 0.0095 * sn + dh * cs)
                f.k.tube("hole", q, (q[0] + n[0] * 0.0016, q[1] + n[1] * 0.0016, q[2] + n[2] * 0.0016), 0.0055, seg=10)


def triceps(k, c, out):
    """Triceps Pushdown (LPP-TP): the stack, a shorter boom off the top cap out past the face, the rope hung from it."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, hang=False)
    vo, zo = boom_mount(f, 0.36, zt)
    zr = 1.62
    f.cable([(0.0, vo, zo), (0.0, vo, zr + 0.07)])
    f.box("steel", (0.0, vo, zr + 0.05), (0.025, 0.02, 0.04), soft=0.002)
    for s in (-1, 1):
        f.sweep("rope", [(0.0, vo, zr + 0.035), (s * 0.03, vo, zr - 0.02), (s * 0.05, vo, zr - 0.34)], f.k.circle(0.013, 14),
                bend=0.05, soft=0.0)
        f.cyl("rubber", (s * 0.05, vo, zr - 0.36), 0.024, 0.045, soft=0.006)
    placard(f, A, 1.25)


def _corners(w, h, r, seg=6):
    """A w x h outline (centred) with its own radius per corner: r = (+w+h, -w+h, -w-h, +w-h)."""
    pts = []
    for (sx, sy), rr, a0 in zip(((1, 1), (-1, 1), (-1, -1), (1, -1)), r, (0, 90, 180, 270)):
        cx, cy = sx * (w / 2 - rr), sy * (h / 2 - rr)
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def carriage_body(f, v, zc, track_w=0.055, track_d=0.035):
    """An adjustable carriage riding a track at (0, v) of face/frame f (ref_02 / ref_03 close up): the rounded black
    body round the track, the pop pin's round knob on its front (-u) over the warning label, the T release lever on
    its -v side; on its +v side the swivel's knuckle and arm to the pulley housing: two D-shaped black plates (round
    away from the track, squarer at the track) with the pulley's rim between them and the axle's bolts through (no
    yellow: Roman, 2026-10-23); the cable out of the housing's foot to the snap hook and the strap D handle.
    Returns (v, z) of the housing's top, where the cable comes in."""
    bu, bv = track_w + 0.03, track_d + 0.04
    f.box("frame", (0.0, v, zc), (bu, bv, 0.15), soft=0.012)
    f.cyl("chrome", (-(bu / 2 + 0.002), v, zc + 0.025), 0.02, 0.004, axis="u", seg=24)
    f.cyl("plastic", (-(bu / 2 + 0.015), v, zc + 0.025), 0.017, 0.024, axis="u", seg=24, soft=0.005)  # the pop pin's knob
    f.box("white", (-(bu / 2 + 0.0006), v, zc - 0.04), (0.0012, bv - 0.014, 0.036), soft=0.0)        # the warning label
    f.box("red", (-(bu / 2 + 0.0008), v, zc - 0.0255), (0.0012, bv - 0.014, 0.007), soft=0.0)
    lv = v - bv / 2                                     # the T release lever, toward the Core
    f.tube("plastic", (0.0, lv + 0.004, zc + 0.03), (0.0, lv - 0.032, zc + 0.03), 0.008, seg=14)
    f.tube("plastic", (0.0, lv - 0.032, zc + 0.002), (0.0, lv - 0.032, zc + 0.058), 0.0095, seg=16, soft=0.003)
    kv = v + bv / 2 + 0.013                             # the swivel: its knuckle on a vertical pin, the arm out
    f.cyl("frame", (0.0, kv, zc), 0.016, 0.10, seg=24, soft=0.004)
    for z in (zc - 0.053, zc + 0.053):
        f.cyl("chrome", (0.0, kv, z), 0.009, 0.006, seg=16)
    hv, hz, w, h = kv + 0.085, zc - 0.005, 0.15, 0.155
    f.box("frame", (0.0, kv + 0.02, zc), (0.026, 0.03, 0.07), soft=0.005)
    prof = _corners(w, h, (0.068, 0.022, 0.03, 0.068))   # (v, z): round on +v, square-ish at the track
    for su in (-1, 1):                                  # the two plates, the pulley's rim between them
        f.sweep("plastic", [(su * 0.0225 - 0.006, hv, hz), (su * 0.0225 + 0.006, hv, hz)],
                [(dv, dz) for dv, dz in prof], up="z", soft=0.003)
        for dv, dz in ((0.0, 0.0), (0.012, -0.05)):
            f.cyl("chrome", (su * 0.0295, hv + dv, hz + dz), 0.008 if dz == 0 else 0.0065, 0.004, axis="u", seg=16)
    f.cyl("rubber", (0.0, hv, hz), 0.064, 0.034, axis="u", seg=40, soft=0.002)
    f.box("frame", (0.0, hv - w / 2 + 0.012, hz), (0.034, 0.024, h - 0.05), soft=0.003)        # the spacer at the track
    zh = hz - h / 2 - 0.20
    cv = hv + 0.03
    f.cable([(0.0, cv, hz - 0.062), (0.0, cv, zh + 0.07)])
    f.cyl("rubber", (0.0, cv, hz - h / 2 - 0.009), 0.02, 0.022, seg=20, soft=0.004)             # the stop ball
    f.disc("chrome", (0.0, cv, zh + 0.06), 0.016, 0.011, 0.005, axis="u", seg=20)            # the snap hook
    f.sweep("rubber", [(0.0, cv, zh + 0.05), (-0.065, cv, zh - 0.005), (0.065, cv, zh - 0.005),
                       (0.0, cv, zh + 0.05)], f.k.rect(0.003, 0.022, 0.001), bend=0.015, up="v", soft=0.0)
    f.tube("rubber", (-0.06, cv, zh - 0.01), (0.06, cv, zh - 0.01), 0.016, soft=0.003)
    return hv - w / 2 + 0.03, hz + h / 2 - 0.004


HANG = (0.11, 0.055)                # a carriage post's hanger pulley: its centre below the bar's underside, its radius


def carriage_post(k, base, toward, z_top, zc=1.30, link=None, boom=None):
    """The crossover's stand-alone carriage post (ref_02 / ref_04): a stainless channel from its black floor bracket up
    to the crossbar, its row of holes facing `toward`, clamped to the crossbar at z_top (the bar's underside) with the
    pulley the cable comes over; the carriage on it at zc; `link` = (v, z) of a floor bar back to the Core (in the
    post's frame, v negative toward the Core); `boom` = (half width, half height) when it hangs from a boom's box
    instead of the round crossbar."""
    looks(k)
    f = Face(k, base, toward)
    tw, td = 0.055, 0.035
    zb = 0.075
    f.box("frame", (0.0, 0.0, 0.006), (0.20, 0.16, 0.012), soft=0.002)
    f.box("frame", (0.0, 0.0, 0.012 + (zb - 0.012) / 2), (0.10, 0.08, zb - 0.012), soft=0.004)
    for su in (-1, 1):
        f.bolt((su * 0.075, 0.0, 0.012), "+z", size=0.014)
    zpt = z_top - HANG[0] - HANG[1] - 0.02             # the post's top, under the hanger pulley
    f.box("stainless", (0.0, 0.0, (zb + zpt) / 2), (tw, td, zpt - zb), soft=0.002)
    for i in range(int((zpt - 0.30) / 0.05)):
        for su in (-1, 1):
            f.cyl("hole", (su * (tw / 2 + 0.0003), 0.0, 0.20 + i * 0.05), 0.0065, 0.001, axis="u", seg=14)
    if link:                                            # the black floor plate back to the Core, its tab up to the
        lv = link                                       # bottom cross-member (ref_08)
        f.box("frame", (0.0, (lv - 0.08) / 2, 0.006), (0.14, abs(lv) + 0.08, 0.012), soft=0.003)
        f.box("frame", (0.0, lv + 0.006, (0.012 + ZBC - CM[1] / 2) / 2), (0.12, 0.012, ZBC - CM[1] / 2 - 0.012), soft=0.002)
    if boom:                                            # the saddle's section: over the boom's box, or arched over the
        hw, hh = boom                                   # round crossbar, its legs down the sides to a foot under it
        zb_ = z_top + hh
        sad = [(hw + 0.006, -hh - 0.035), (hw + 0.006, hh + 0.006), (-hw - 0.006, hh + 0.006), (-hw - 0.006, -hh - 0.035),
               (-hw - 0.0005, -hh - 0.035), (-hw - 0.0005, hh + 0.0005), (hw + 0.0005, hh + 0.0005), (hw + 0.0005, -hh - 0.035)]
    else:
        hw = hh = 0.04
        zb_ = z_top + hh
        ro, ri = hh + 0.006, hh + 0.0005
        sad = [(ro * math.cos(math.radians(a)), ro * math.sin(math.radians(a))) for a in range(0, 181, 10)]
        sad += [(-ro, -hh - 0.035), (-ri, -hh - 0.035)]
        sad += [(ri * math.cos(math.radians(a)), ri * math.sin(math.radians(a))) for a in range(180, -1, -10)]
        sad += [(ri, -hh - 0.035), (ro, -hh - 0.035)]
    f.sweep("frame", [(0.0, -0.05, zb_), (0.0, 0.05, zb_)], sad, up="z", soft=0.003)   # the saddle (ref_03)
    for sv in (-1, 1):
        for su in (-1, 1):
            f.bolt((su * (hw + 0.006), sv * 0.032, z_top - 0.006), ("+u" if su > 0 else "-u"), size=0.012)
    f.box("frame", (0.0, 0.0, z_top - 0.035), (2 * hw + 0.012, 0.10, 0.014), soft=0.003)                # its foot
    pv, pz = 0.0, z_top - HANG[0]
    tongue = [(0.05, 0.0), (-0.05, 0.0), (-0.024, -0.075), (-0.024, -(z_top - 0.042 - zpt + 0.05)),
              (0.024, -(z_top - 0.042 - zpt + 0.05)), (0.024, -0.075)]
    for su in (-1, 1):                                  # the tongue, tapering down round the pulley onto the post's top
        f.sweep("frame", [(su * (tw / 2 + 0.0005), 0.0, z_top - 0.042), (su * (tw / 2 + 0.0085), 0.0, z_top - 0.042)],
                tongue, up="z", soft=0.002)
        f.bolt((su * (tw / 2 + 0.0085), 0.0, zpt - 0.025), ("+u" if su > 0 else "-u"), size=0.012)
    f.pulley((0.0, pv, pz), HANG[1], axis="u")
    f.tube("chrome", (-0.036, pv, pz), (0.036, pv, pz), 0.008, seg=12)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.015, pv, pz), 0.022, 0.006, axis="u", seg=24)
    cv, cz = carriage_body(f, 0.0, zc, tw, td)
    f.cable([(0.0, pv + 0.86 * HANG[1] - 0.003, pz), (0.0, cv, cz)])                                 # down to the housing's top
    return f


def face_carriage(f, v_face, zc):
    """An adjustable carriage on a track bolted to a face (the attached crossover's tower)."""
    vt = v_face + 0.02
    z0, z1 = 0.18, 1.98
    f.box("stainless", (0.0, vt, (z0 + z1) / 2), (0.055, 0.035, z1 - z0), soft=0.002)
    for i in range(34):
        f.cyl("hole", (0.0, vt + 0.0178, z0 + 0.05 + i * 0.05), 0.0065, 0.001, axis="v", seg=14)
    for z in (z0, z1):
        f.box("frame", (0.0, v_face + 0.005, z), (0.08, 0.012, 0.05), soft=0.003)
    carriage_body(f, vt, zc)


def crossover_station(k, c, out, post_v, z_bar):
    """The Core's side of the cable crossover (LPP-CX, your render): the stack inside the face, a short top mount, the
    stand-alone carriage post at post_v under the crossbar (its pulley facing away from the Core), the floor bar back to
    the Core, the cable from the top mount up to the post's pulley."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, hang=False)
    vo, zo = top_mount(f, 0.12, zt)
    pz = z_bar - 0.07
    f.cable([(0.0, vo - 0.86 * RP + 0.003, zo + 0.86 * RP - 0.003), (0.0, post_v, z_bar - HANG[0] + 0.86 * HANG[1] - 0.003)])
    base = f.p(0.0, post_v, 0.0)[:2]
    carriage_post(k, base, out, z_bar, link=-(post_v - A - CM[0] / 2))
    placard(f, A, 1.25)


def adjustable_station(k, c, out, post_v=None, zc=1.30):
    """Adjustable Pulley 2:1 (LPP-AC) on an outer face (Roman: the carriage that slides up and down, on the outside
    edge): the stack behind the face, a short boom off the top cap out over the post, the carriage post right in front
    of the face on its floor plate back to the Core, clamped under the boom's end, the cable from the boom down to the
    post's hanger pulley, the carriage on it."""
    f = Face(k, c, out)
    post_v = A + 0.16 if post_v is None else post_v
    zt = f.stack(VS, A, hang=False)
    vo, zo = boom_mount(f, post_v - A + 0.10, zt, end=False)
    z_top = ZBM - 0.045
    carriage_post(k, f.p(0.0, post_v, 0.0)[:2], out, z_top, zc=zc, link=-(post_v - A - CM[0] / 2), boom=(0.05, 0.045))
    f.cable([(0.0, vo, zo), (0.0, post_v, z_top - HANG[0] + 0.86 * HANG[1] - 0.003)])
    placard(f, A, 1.25)


def beam(k, a, b, z, handles="flat", caps=True):
    """The crossbar between two Cores' tops (or a Core and a tower): a round tube (ref_02 / ref_03), its rows of holes,
    the end sleeves; the pull-up handles at its middle angled down and out along it, rubber grips (your render)."""
    looks(k)
    R = 0.04
    k.tube("frame", (a[0], a[1], z), (b[0], b[1], z), R, seg=32)
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    for e in ((a, b) if caps else ()):                  # the end caps (not where the bar ends against a hub)
        k.cyl("plastic", (e[0] - ux * 0.006 * (1 if e is a else -1), e[1] - uy * 0.006 * (1 if e is a else -1), z), R + 0.003, 0.012,
              axis="x" if abs(ux) > 0.5 else "y", seg=32, soft=0.003)
    for side in (1, -1):
        for i in range(16):
            t = 0.20 + i * 0.038
            k.cyl("hole", (a[0] + ux * L * t + side * nx * (R + 0.0002), a[1] + uy * L * t + side * ny * (R + 0.0002), z),
                  0.006, 0.001, axis="x" if abs(nx) > 0.5 else "y", seg=12)
    def at(t, du=0.0, dn=0.0, dz=0.0):
        return (a[0] + ux * (L * t + du) + nx * dn, a[1] + uy * (L * t + du) + ny * dn, z + dz)
    ax_u = "x" if abs(ux) > 0.5 else "y"
    ax_n = "y" if ax_u == "x" else "x"
    def collar(t):
        p0, p1 = at(t, -0.04), at(t, 0.04)
        k.tube("frame", p0, p1, R + 0.007, seg=32)
    if handles == "angled":                             # two grips angled down and out along the bar
        for t, s_ in ((0.44, -1), (0.56, 1)):
            collar(t)
            p1, p2 = at(t, s_ * 0.05, 0, -0.09), at(t, s_ * 0.27, 0, -0.17)
            k.sweep("frame", [at(t, 0, 0, -R + 0.01), p1, p2], k.circle(0.016, 18), bend=0.04, soft=0.0)
            k.tube("rubber", at(t, s_ * 0.11, 0, -0.112), p2, 0.02, soft=0.003)
            k.cyl("plastic", at(t, s_ * 0.276, 0, -0.172), 0.022, 0.012, axis=ax_u, seg=20, soft=0.003)
    elif handles == "flat":                             # a straight pull-up bar hung level under the crossbar
        zb = -0.20
        for t in (0.36, 0.64):
            collar(t)
            k.tube("frame", at(t, 0, 0, -R - 0.004), at(t, 0, 0, zb + 0.02), 0.024, seg=20)      # the drops, 1.9 in tube,
            # from the collar's underside
            k.box("frame", at(t, 0, 0, zb), (0.055, 0.055, 0.045), soft=0.01)
        k.tube("frame", at(0.30, 0, 0, zb), at(0.70, 0, 0, zb), 0.017, seg=20)
        for t0, t1 in ((0.305, 0.35), (0.37, 0.47), (0.53, 0.63), (0.65, 0.695)):
            k.tube("rubber", at(t0, 0, 0, zb), at(t1, 0, 0, zb), 0.021, soft=0.003)
        for t in (0.30, 0.70):
            k.cyl("plastic", at(t, -0.006 if t < 0.5 else 0.006, 0, zb), 0.022, 0.012, axis=ax_u, seg=20, soft=0.003)
    elif handles == "neutral":                          # two pairs of parallel grips across the bar, palms facing
        zb = -0.16
        for t in (0.40, 0.60):
            collar(t)
            k.tube("frame", at(t, 0, 0, -R + 0.01), at(t, 0, 0, zb + 0.03), 0.02, seg=20)
            k.bar("frame", at(t, -0.13, 0, zb + 0.03), at(t, 0.13, 0, zb + 0.03), 0.03, 0.03, up=(0, 0, 1))
            for du in (-0.11, 0.11):
                k.tube("frame", at(t, du, 0, zb + 0.015), at(t, du, 0, zb - 0.005), 0.012, seg=14)
                k.tube("frame", at(t, du, -0.13, zb - 0.015), at(t, du, 0.13, zb - 0.015), 0.014, seg=18)
                k.tube("rubber", at(t, du, -0.11, zb - 0.015), at(t, du, 0.11, zb - 0.015), 0.019, soft=0.003)

def tower(k, c, out):
    """The attached crossover's own tower (37 x 47 x 234 cm): two uprights arched over the top, the base, the stack
    between them, the carriage track on the face toward the Core, the cap; returns the top mount point for the beam."""
    looks(k)
    f = Face(k, c, out)
    hw, hd = 0.20, 0.13             # the uprights' half spacing (u), the base's half depth (v)
    zt0 = 2.24
    f.sweep("frame", [(-hw, 0.0, FOOT_H), (-hw, 0.0, zt0), (hw, 0.0, zt0), (hw, 0.0, FOOT_H)], f.k.rect(LEG, LEG, 0.012),
            bend=0.12, up="v")
    for su in (-1, 1):
        foot(k, *f.p(su * hw, 0.0, 0)[:2], math.atan2(f.o[1], f.o[0]))
        f.bar("frame", (su * hw, -hd, 0.07), (su * hw, hd, 0.07), 0.05, 0.05, up="z",
              cut0=None, cut1=None)
    for z in (ZBC, ZTC):
        f.bar("frame", (-hw + LEG / 2, 0.0, z), (hw - LEG / 2, 0.0, z), CM[0], CM[1], up="z",
              cut0=((-hw + LEG / 2, 0, 0), (1, 0, 0)), cut1=((hw - LEG / 2, 0, 0), (1, 0, 0)), weld=True)
    zt = f.stack(0.0, 0.0, rods=0.30, hang=False)
    f.cable([(0.0, 0.0, zt), (0.0, 0.0, ZTC - CM[1] / 2 - 0.012)])
    face_carriage(f, CM[0] / 2, 1.40)
    f.box("frame", (0.0, 0.0, zt0 + LEG / 2 + 0.006), (0.16, 0.16, 0.012), soft=0.003)
    return f.p(0.0, 0.0, zt0 + LEG / 2 + 0.012)

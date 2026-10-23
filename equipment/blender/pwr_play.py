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
    "plate": dict(color=(0.035, 0.036, 0.04), rough=0.5, metal=0.25, coat=0.0, bump=(1200, 0.05)),
    "grip": dict(color=(0.11, 0.11, 0.12), rough=0.7, coat=0.0, bump=(2500, 0.12)),
    "red": dict(color=(0.6, 0.04, 0.03), rough=0.4, coat=0.0),
    "white": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "stainless": dict(color=(0.86, 0.86, 0.87), rough=0.38, metal=0.55, aniso=0.3),          # satin aluminium (ref_08)
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
HUB = (0.12, 2.27, 2.35)            # the top hub, a small black cap where the legs meet (ref_07 / ref_08): radius, bottom, top
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

    def stack(self, v, vcm, n=16, rods=0.22, pin_at=5, hang=True):
        """A selectorized stack at (0, v), its frame's cross-members at vcm: the base plate on the bottom cross-member,
        n plates 0.26 (u) x 0.125 (v) on their bumper, the chrome rods up to the rod plate (hung on two straps from
        the top cross-member below a top mount's inner pulley, or right under the cross-member), the top plate, the
        stem, the numbers, the pin on the outer (+v) side. Returns the top plate's top z."""
        z0 = ZBC + CM[1] / 2
        lo, hi = min(v - 0.08, vcm - CM[0] / 2), max(v + 0.08, vcm + CM[0] / 2)
        self.box("frame", (0.0, (lo + hi) / 2, z0 + 0.006), (0.40, hi - lo, 0.012), soft=0.002)
        z0 += 0.012
        t = 0.0254
        self.box("rubber", (0.0, v, z0 + 0.025), (0.16, 0.08, 0.05), soft=0.006)
        zb = z0 + 0.05
        for i in range(n):
            self.box("plate", (0.0, v, zb + i * t + t / 2), (0.30, 0.15, t - 0.0012), soft=0.003)
            if i == pin_at:
                self.tube("chrome", (0.0, v + 0.075 - 0.01, zb + i * t + t / 2), (0.0, v + 0.12, zb + i * t + t / 2), 0.0055)
                self.cyl("plastic", (0.0, v + 0.13, zb + i * t + t / 2), 0.016, 0.03, axis="v")
            self.text("white", f"{5 + i * 7.5:g}", (-0.09, v + 0.0751, zb + i * t + t / 2), 0.012)
        ztop = zb + n * t
        self.box("plate", (0.0, v, ztop + 0.03), (0.30, 0.15, 0.06), soft=0.006)
        for su in (-1, 1):                              # the red collars where the rods run into the top plate
            self.cyl("red", (su * rods / 2, v, ztop + 0.065), 0.019, 0.01, seg=24)
        self.tube("chrome", (0.0, v, zb), (0.0, v, ztop + 0.07), 0.0095)
        zr = 1.80 if hang else ZTC - RTR - 0.012
        hi2 = vcm - CM[0] / 2 - 0.004 if hang else vcm
        self.box("frame", (0.0, (lo + hi2) / 2, zr + 0.006), (0.46, hi2 - lo, 0.012), soft=0.002)
        for su in (-1, 1):                              # the rods' bushings in the base and rod plates
            self.cyl("chrome", (su * rods / 2, v, z0 + 0.008), 0.02, 0.016, seg=20)
        if hang:
            for su in (-1, 1):
                self.box("frame", (su * 0.21, vcm - CM[0] / 2 - 0.009, (zr + ZTC - CM[1] / 2) / 2), (0.03, 0.01, ZTC - CM[1] / 2 - zr),
                         soft=0.001)
        for su in (-1, 1):
            self.tube("chrome", (su * rods / 2, v, z0), (su * rods / 2, v, zr), 0.0135)
        return ztop + 0.06


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
            k.bar("frame", (x, y, 0.07), (cx + sx * 0.04, cy + sy * 0.04, 0.07), 0.05, 0.012, up=(0, 0, 1))      # base X
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
    for su in (-1, 1):
        f.box("boom", (su * 0.036, vp, (ZTC + ZTP + 0.06) / 2), (0.008, 0.20, ZTP + 0.06 - ZTC), soft=0.02)
        f.bolt((su * 0.04, vp - 0.012, ZTC), "+u" if su > 0 else "-u", size=0.014)
    f.pulley((0.0, vp, ZTP), RP, axis="u")
    f.tube("chrome", (-0.04, vp, ZTP), (0.04, vp, ZTP), 0.009, seg=12)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.02, vp, ZTP), 0.026, 0.006, axis="u", seg=24)
    f.cable([(0.0, vp - g, zt), (0.0, vp - g, ZTP)])
    return (vp + g, ZTP)


ZBM = 2.31                          # a pulldown / pushdown boom's centre: level with the cap, the very top (ref_08)
RPB = 0.07                          # the pulleys under a boom


def boom_mount(f, reach, zt):
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
    f.bar("boom", (0.0, -0.05, ZBM), (0.0, v1, ZBM), bw, bh, r=0.035, up="z")
    f.box("plastic", (0.0, v1 + 0.005, ZBM), (bw - 0.01, 0.012, bh - 0.01), soft=0.02)            # its end cap
    for vp in (vi, vo):
        for su in (-1, 1):
            f.box("boom", (su * 0.036, vp, (ZBM - bh / 2 + zp - 0.04) / 2), (0.008, 0.13, ZBM - bh / 2 - zp + 0.04), soft=0.02)
            f.bolt((su * 0.04, vp, zp), "+u" if su > 0 else "-u", size=0.016)
        f.pulley((0.0, vp, zp), RPB, axis="u")
        f.tube("chrome", (-0.04, vp, zp), (0.04, vp, zp), 0.009, seg=12)
    f.cable([(0.0, vi - g, zt), (0.0, vi - g, zp)])
    f.cable([(0.0, vi, zp + g), (0.0, vo, zp + g)])
    return (vo + g, zp)


def placard(f, u, z):
    f.box("placard", (u, A + LEG / 2 + 0.001, z), (0.07, 0.002, 0.30), soft=0.0)
    for i in range(3):
        f.box("blue", (u, A + LEG / 2 + 0.0024, z + 0.09 - i * 0.075), (0.05, 0.0008, 0.06), soft=0.0)


def guard(f, z=0.88, bow=0.10):
    """The curved black bar across a station's face just above its stack, bowing out between the face's two legs
    (ref_07 / ref_08)."""
    e = A - LEG / 2
    f.sweep("frame", [(-e, A, z), (-0.22, A + bow, z), (0.22, A + bow, z), (e, A, z)], f.k.circle(0.024, 20), bend=0.12,
            soft=0.0)


def pulldown(k, c, out):
    """Pulldown (LPP-PD), as the render has it (ref_08 / ref_07; the manual's LPP-PD drawing): the stack right behind
    the face; the big boom straight out from the Core's top cap at the very top, the lat bar hung from its end out over
    the seat; the station's post on its own front foot (a floor beam back to the Core) carrying the seat under the bar and
    nearer the Core the knee pads, the adjustment handle on its top; laid out for a seated 1.78 m user (hips under the
    bar, thighs under the pads, hands up to the bar)."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, hang=False)
    vo, zo = boom_mount(f, 0.52, zt)                    # the boom out over the user (ref_08)
    zb = 1.95                                           # the bar at rest, hung from the boom's end over the hips
    f.cable([(0.0, vo, zo), (0.0, vo, zb + 0.06)])
    f.box("steel", (0.0, vo, zb + 0.035), (0.03, 0.02, 0.05), soft=0.002)
    bar = [(-0.60, vo + 0.03, zb - 0.09), (-0.46, vo, zb), (0.46, vo, zb), (0.60, vo + 0.03, zb - 0.09)]
    f.sweep("frame", bar, f.k.circle(0.0145, 18), bend=0.08, soft=0.0)
    for e in (bar[0], bar[-1]):
        f.cyl("chrome", e, 0.0155, 0.012, axis="z", seg=18)
    for s in (-1, 1):                                   # the grey grips most of its length (ref_04 / ref_05)
        f.tube("grip", (s * 0.06, vo, zb), (s * 0.45, vo, zb), 0.019, soft=0.003)
    guard(f)
    # the floor beam out from the bottom cross-member to the station's front foot; the post up from it, leaning in
    # through the seat's bracket to the knee pads' hub and the handle on top
    vf = A + 0.72
    f.bar("frame", (0.0, A + CM[0] / 2, ZBC), (0.0, vf, ZBC), 0.076, 0.076, up="z", cut0=((0, A + CM[0] / 2, 0), (0, 1, 0)),
          weld=True)
    f.box("frame", (0.0, vf, (FOOT_H + ZBC - 0.038) / 2), (0.08, 0.08, ZBC - 0.038 - FOOT_H), soft=0.004)
    f.box("rubber", (0.0, vf, FOOT_H / 2), (0.20, 0.12, FOOT_H), soft=0.006)
    vs, zs = vo + 0.02, 0.45                            # the seat: the hips right under the bar
    vk, zk = vs - 0.30, 0.66                            # the knee pads: over the thighs just behind the knees
    post = [(0.0, vf - 0.06, ZBC + 0.038), (0.0, vs, zs - 0.07), (0.0, vk + 0.02, zk - 0.02), (0.0, vk - 0.01, zk + 0.16)]
    f.sweep("frame", post, f.k.rect(0.065, 0.065, 0.01), bend=0.08, up="u", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    f.box("plastic", (0.0, vk - 0.012, zk + 0.165), (0.07, 0.07, 0.01), soft=0.003)
    f.cyl("plastic", (0.0, vk - 0.012, zk + 0.20), 0.03, 0.06, soft=0.01)                         # the handle's knob
    f.box("frame", (0.0, vs, zs - 0.045), (0.24, 0.24, 0.03), soft=0.004)
    f.box("pad", (0.0, vs + 0.02, zs + 0.005), (0.38, 0.34, 0.09), soft=0.035)
    f.tube("steel", (-0.31, vk, zk), (0.31, vk, zk), 0.018, seg=18)
    f.box("frame", (0.0, vk, zk), (0.12, 0.08, 0.09), soft=0.006)                        # the hub on the post
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
    zt = f.stack(VS, A, hang=False)
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
    f.box("steel", (0.0, va + 0.13, zl), (0.03, 0.03, 0.02), soft=0.002)
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


def carriage_body(f, v, zc, track_w=0.055):
    """An adjustable carriage riding a track at (0, v) of face/frame f, its pulley facing +v (ref_02 / ref_03 / your
    PWR Play render): the black body round the track, the pop pin and its knob on +u, the swivel arm, the big black
    pulley housing (no yellow ring: Roman, 2026-10-23) and the warning label, the cable out of its foot to the snap hook
    and the strap D handle."""
    f.box("frame", (0.0, v, zc), (track_w + 0.045, 0.09, 0.17), soft=0.008)
    f.tube("chrome", (-(track_w / 2 + 0.0225), v, zc + 0.04), (-(track_w / 2 + 0.05), v, zc + 0.04), 0.007, seg=12)
    f.cyl("plastic", (-(track_w / 2 + 0.067), v, zc + 0.04), 0.026, 0.034, axis="u", soft=0.006)      # the pop pin's knob
    f.box("white", (-(track_w / 2 + 0.0226), v, zc - 0.05), (0.0012, 0.05, 0.03), soft=0.0)          # its warning label
    f.box("frame", (0.0, v + 0.065, zc - 0.03), (0.045, 0.04, 0.05), soft=0.004)
    hv, hz, hr = v + 0.13, zc - 0.03, 0.08
    f.cyl("plastic", (0.0, hv, hz), hr, 0.045, axis="u", soft=0.006)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.0232, hv, hz + 0.01), 0.012, 0.0024, axis="u", seg=16)
        f.box("white", (su * 0.0232, hv + 0.02, hz - 0.05), (0.0012, 0.04, 0.02), soft=0.0)
    zh = hz - hr - 0.20
    f.cable([(0.0, hv + 0.03, hz - hr + 0.005), (0.0, hv + 0.03, zh + 0.07)])
    f.disc("chrome", (0.0, hv + 0.03, zh + 0.06), 0.016, 0.011, 0.005, axis="u", seg=20)            # the snap hook
    f.sweep("rubber", [(0.0, hv + 0.03, zh + 0.05), (-0.065, hv + 0.03, zh - 0.005), (0.065, hv + 0.03, zh - 0.005),
                       (0.0, hv + 0.03, zh + 0.05)], f.k.rect(0.003, 0.022, 0.001), bend=0.015, up="v", soft=0.0)
    f.tube("rubber", (-0.06, hv + 0.03, zh - 0.01), (0.06, hv + 0.03, zh - 0.01), 0.016, soft=0.003)


def carriage_post(k, base, toward, z_top, zc=1.30, link=None):
    """The crossover's stand-alone carriage post (ref_02 / ref_04): a stainless channel from its black floor bracket up
    to the crossbar, its row of holes facing `toward`, clamped to the crossbar at z_top (the bar's underside) with the
    pulley the cable comes over; the carriage on it at zc; `link` = (v, z) of a floor bar back to the Core (in the
    post's frame, v negative toward the Core)."""
    looks(k)
    f = Face(k, base, toward)
    tw, td = 0.055, 0.035
    zb = 0.075
    f.box("frame", (0.0, 0.0, 0.006), (0.20, 0.16, 0.012), soft=0.002)
    f.box("frame", (0.0, 0.0, 0.012 + (zb - 0.012) / 2), (0.10, 0.08, zb - 0.012), soft=0.004)
    for su in (-1, 1):
        f.bolt((su * 0.075, 0.0, 0.012), "+z", size=0.014)
    f.box("stainless", (0.0, 0.0, (zb + z_top) / 2), (tw, td, z_top - zb), soft=0.002)
    for i in range(int((z_top - 0.30) / 0.05)):
        for su in (-1, 1):
            f.cyl("hole", (su * (tw / 2 + 0.0003), 0.0, 0.20 + i * 0.05), 0.0065, 0.001, axis="u", seg=14)
    if link:                                            # the black floor plate back to the Core, its tab up to the
        lv = link                                       # bottom cross-member (ref_08)
        f.box("frame", (0.0, (lv - 0.08) / 2, 0.006), (0.14, abs(lv) + 0.08, 0.012), soft=0.003)
        f.box("frame", (0.0, lv + 0.006, (0.012 + ZBC - CM[1] / 2) / 2), (0.12, 0.012, ZBC - CM[1] / 2 - 0.012), soft=0.002)
    f.box("frame", (0.0, 0.0, z_top + 0.035), (0.10, 0.09, 0.09), soft=0.008)                    # the clamp on the bar
    for su in (-1, 1):                                  # the hanger's two plates down from the clamp round the pulley
        f.box("frame", (su * 0.034, 0.03, z_top - 0.035), (0.008, 0.13, 0.13), soft=0.02)
    pv, pz = 0.03, z_top - 0.06
    f.pulley((0.0, pv, pz), 0.055, axis="u")
    f.tube("chrome", (-0.036, pv, pz), (0.036, pv, pz), 0.008, seg=12)
    for su in (-1, 1):
        f.cyl("chrome", (su * 0.015, pv, pz), 0.022, 0.006, axis="u", seg=24)
    carriage_body(f, 0.0, zc, tw)
    f.cable([(0.0, 0.03 + 0.86 * 0.055 - 0.003, z_top - 0.06), (0.0, 0.15, zc - 0.03 + 0.07)])         # down into the housing
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
    f.cable([(0.0, vo - 0.86 * RP + 0.003, zo + 0.86 * RP - 0.003), (0.0, post_v + 0.03, z_bar - 0.06 + 0.044)])   # over to the post's pulley
    base = f.p(0.0, post_v, 0.0)[:2]
    carriage_post(k, base, out, z_bar, link=-(post_v - A - CM[0] / 2))
    placard(f, A, 1.25)


def beam(k, a, b, z, handles=True):
    """The crossbar between two Cores' tops (or a Core and a tower): a round tube (ref_02 / ref_03), its rows of holes,
    the end sleeves; the pull-up handles at its middle angled down and out along it, rubber grips (your render)."""
    looks(k)
    R = 0.04
    k.tube("frame", (a[0], a[1], z), (b[0], b[1], z), R, seg=32)
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    for e in (a, b):                                    # the end caps
        k.cyl("plastic", (e[0] - ux * 0.006 * (1 if e is a else -1), e[1] - uy * 0.006 * (1 if e is a else -1), z), R + 0.003, 0.012,
              axis="x" if abs(ux) > 0.5 else "y", seg=32, soft=0.003)
    for side in (1, -1):
        for i in range(16):
            t = 0.20 + i * 0.038
            k.cyl("hole", (a[0] + ux * L * t + side * nx * (R + 0.0002), a[1] + uy * L * t + side * ny * (R + 0.0002), z),
                  0.006, 0.001, axis="x" if abs(nx) > 0.5 else "y", seg=12)
    if handles:
        for t, s in ((0.44, -1), (0.56, 1)):
            cx, cy = a[0] + ux * L * t, a[1] + uy * L * t
            k.tube("frame", (cx - ux * 0.045, cy - uy * 0.045, z), (cx + ux * 0.045, cy + uy * 0.045, z), R + 0.007, seg=32)
            p0 = (cx, cy, z - R - 0.002)
            p1 = (cx + s * ux * 0.05, cy + s * uy * 0.05, z - 0.09)
            p2 = (cx + s * ux * 0.27, cy + s * uy * 0.27, z - 0.17)
            k.sweep("frame", [(cx, cy, z - R + 0.01), p1, p2], k.circle(0.016, 18), bend=0.04, soft=0.0)
            g0 = (p1[0] + s * ux * 0.06, p1[1] + s * uy * 0.06, p1[2] - 0.022)
            k.tube("rubber", g0, p2, 0.02, soft=0.003)
            k.cyl("plastic", (p2[0] + s * ux * 0.006, p2[1] + s * uy * 0.006, p2[2] - 0.002), 0.022, 0.012,
                  axis="x" if abs(ux) > 0.5 else "y", seg=20, soft=0.003)


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

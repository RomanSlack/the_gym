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
    "frame": dict(color=(0.03, 0.031, 0.034), rough=0.45, metal=0.35, coat=0.0, bump=(1400, 0.06)),   # Charcoal
    "boom": dict(color=(0.026, 0.027, 0.03), rough=0.45, metal=0.35, coat=0.0, bump=(1400, 0.06)),
    "pad": dict(color=(0.014, 0.014, 0.015), rough=0.55, sheen=0.25, bump=(1500, 0.14)),
    "plate": dict(color=(0.02, 0.02, 0.022), rough=0.5, metal=0.2, coat=0.0),
    "chrome": dict(color=(0.8, 0.8, 0.82), rough=0.08, metal=1.0, coat=0.0),
    "steel": dict(color=(0.62, 0.62, 0.64), rough=0.25, metal=1.0, aniso=0.3),
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45, coat=0.0),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, coat=0.0, spec=0.2),
    "cable": dict(color=(0.05, 0.05, 0.055), rough=0.4, coat=0.0),
    "hole": dict(color=(0.004, 0.004, 0.004), rough=0.9),
    "yellow": dict(color=(0.75, 0.6, 0.05), rough=0.4, coat=0.0),
    "placard": dict(color=(0.02, 0.02, 0.022), rough=0.4, coat=0.0),
    "blue": dict(color=(0.08, 0.35, 0.7), rough=0.4, coat=0.0),
    "label": dict(color=(0.75, 0.75, 0.77), rough=0.4, coat=0.0),
    "rope": dict(color=(0.02, 0.02, 0.022), rough=0.8, coat=0.0, bump=(900, 0.3)),
    "bolt": dict(color=(0.55, 0.55, 0.56), rough=0.3, metal=1.0),
}

FOOT_H = 0.021                      # the oval feet (13/16 in, the manual's Foot Dimensions)
A = 0.36                            # the Core's legs' centres from its centre (x and y): 83 cm over the feet
LEG = 0.076                         # the leg tube, square
ZARM = 2.29                         # the legs' arms over the top, into the hub
HUB = (0.13, 2.25, 2.36)            # the top hub: radius, bottom, top; the cap on it to 2.39 (the 239 cm)
ZTC, ZBC = 2.03, 0.13               # the top and bottom cross-members (centres)
CM = (0.05, 0.076)                  # a cross-member: across (v), tall
VS = A - 0.17                       # a station's stack (v), inside the Core behind its face
ZTM = ZTC - CM[1] / 2 - 0.038       # a top mount's boom (centre), bolted under the top cross-member


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

    def stack(self, v, vcm, n=16, rods=0.40, pin_at=5, hang=True):
        """A selectorized stack at (0, v), its frame's cross-members at vcm: the base plate on the bottom cross-member,
        n plates 0.26 (u) x 0.125 (v) on their bumper, the chrome rods up to the rod plate (hung on two straps from
        the top cross-member below a top mount's inner pulley, or right under the cross-member), the top plate, the
        stem, the numbers, the pin on the outer (+v) side. Returns the top plate's top z."""
        z0 = ZBC + CM[1] / 2
        lo, hi = min(v - 0.08, vcm - CM[0] / 2), max(v + 0.08, vcm + CM[0] / 2)
        self.box("frame", (0.0, (lo + hi) / 2, z0 + 0.006), (0.46, hi - lo, 0.012), soft=0.002)
        z0 += 0.012
        t = 0.0254
        self.box("rubber", (0.0, v, z0 + 0.025), (0.16, 0.08, 0.05), soft=0.006)
        zb = z0 + 0.05
        for i in range(n):
            self.box("plate", (0.0, v, zb + i * t + t / 2), (0.26, 0.125, t - 0.0012), soft=0.003)
            if i == pin_at:
                self.tube("chrome", (0.0, v + 0.0625 - 0.01, zb + i * t + t / 2), (0.0, v + 0.11, zb + i * t + t / 2), 0.0055)
                self.cyl("plastic", (0.0, v + 0.12, zb + i * t + t / 2), 0.016, 0.03, axis="v")
            if i % 2 == 0:
                self.text("label", str(5 + i * 5), (0.07, v + 0.0626, zb + i * t + t / 2), 0.011)
        ztop = zb + n * t
        self.box("plate", (0.0, v, ztop + 0.03), (0.26, 0.125, 0.06), soft=0.006)
        self.tube("chrome", (0.0, v, zb), (0.0, v, ztop + 0.07), 0.0095)
        zr = 1.80 if hang else ZTC - CM[1] / 2 - 0.012
        hi2 = vcm - CM[0] / 2 - 0.004 if hang else hi
        self.box("frame", (0.0, (lo + hi2) / 2, zr + 0.006), (0.46, hi2 - lo, 0.012), soft=0.002)
        if hang:
            for su in (-1, 1):
                self.box("frame", (su * 0.21, vcm - CM[0] / 2 - 0.009, (zr + ZTC - CM[1] / 2) / 2), (0.03, 0.01, ZTC - CM[1] / 2 - zr),
                         soft=0.001)
        for su in (-1, 1):
            self.tube("chrome", (su * rods / 2, v, z0), (su * rods / 2, v, zr), 0.0127)
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
            k.sweep("frame", [(x, y, FOOT_H), (x, y, ZARM), (hx, hy, ZARM)], k.rect(LEG, LEG, 0.012), bend=0.20,
                    up=(1, 0, 0), cut0=((0, 0, FOOT_H), (0, 0, 1)), weld=True)       # faces square to the Core's faces
            foot(k, x, y, math.atan2(sy, sx))
            k.bar("frame", (x, y, 0.07), (cx + sx * 0.04, cy + sy * 0.04, 0.07), 0.05, 0.012, up=(0, 0, 1))      # base X
            for i in range(6):
                k.cyl("hole", (x + sx * (LEG / 2 + 0.0002), y, 0.55 + i * 0.20), 0.006, 0.001, axis="x", seg=12)
    k.cyl("frame", (cx, cy, (HUB[1] + HUB[2]) / 2), HUB[0], HUB[2] - HUB[1], seg=48, soft=0.006)
    k.cyl("plastic", (cx, cy, HUB[2] + 0.015), HUB[0] + 0.006, 0.03, seg=48, soft=0.008)
    k.cyl("plastic", (cx, cy, 0.07), 0.07, 0.03, seg=36, soft=0.004)                                # bottom hub
    for o in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        f = Face(k, c, o)
        for z in (ZTC, ZBC):
            f.bar("frame", (-A + LEG / 2, A, z), (A - LEG / 2, A, z), CM[0], CM[1], up="z",
                  cut0=((-A + LEG / 2, 0, 0), (1, 0, 0)), cut1=((A - LEG / 2, 0, 0), (1, 0, 0)), weld=True)
        for i in range(7):
            f.cyl("hole", (-0.15 + i * 0.05, A + CM[0] / 2 + 0.0004, ZTC), 0.006, 0.001, axis="v", seg=12)
    # the Life Fitness script up two legs' outer corners
    for sx, sy in ((1, -1), (-1, 1)):
        x, y = cx + sx * (A + LEG / 2 + 0.001), cy + sy * A
        k.text("label", "Life Fitness", (x, y, 1.45), 0.05, rz=math.pi / 2 * (1 if sx > 0 else -1), depth=0.0006,
               spin=math.pi / 2)


def top_mount(f, length, pulleys=True):
    """A standard top mount on face f: the boom under the top cross-member from over the stack out `length` past the
    face, the inner pulley over the stack and the outer pulley at its end. Returns the outer pulley's bottom (v, z)."""
    v0, v1 = VS - 0.06, A + length
    f.bar("boom", (0.0, v0, ZTM), (0.0, v1, ZTM), 0.06, 0.076, up="z")
    f.box("plastic", (0.0, v1 + 0.004, ZTM), (0.064, 0.008, 0.08), soft=0.002)
    for vb in (A - 0.03, A + 0.03):
        f.bolt((0.0, vb, ZTC + CM[1] / 2), "+z", size=0.014, nut=CM[1] + 0.076)
    r = 0.055
    for vp in (VS, v1 - 0.06):
        for su in (-1, 1):
            f.box("boom", (su * 0.034, vp, ZTM - 0.07), (0.008, 0.12, 0.10), soft=0.002)      # the pulley's cheek plates
        f.pulley((0.0, vp, ZTM - 0.08), r, axis="u")
        f.tube("chrome", (-0.036, vp, ZTM - 0.08), (0.036, vp, ZTM - 0.08), 0.008, seg=12)
    return (v1 - 0.06 + r - 0.003, ZTM - 0.08)


def placard(f, u, z):
    f.box("placard", (u, A + LEG / 2 + 0.001, z), (0.07, 0.002, 0.30), soft=0.0)
    for i in range(3):
        f.box("blue", (u, A + LEG / 2 + 0.0024, z + 0.09 - i * 0.075), (0.05, 0.0008, 0.06), soft=0.0)


def pulldown(k, c, out):
    """Pulldown (LPP-PD): the stack, a long top mount out over the seat, the lat bar hung from it; the seat frame off the
    bottom cross-member with the seat and the knee pads over the thighs (laid out for a seated 1.78 m user)."""
    f = Face(k, c, out)
    zt = f.stack(VS, A)
    vo, zo = top_mount(f, 0.68)
    f.cable([(0.0, VS, zt), (0.0, VS, ZTM - 0.08 - 0.055 + 0.01)])
    f.cable([(0.0, VS + 0.055, ZTM - 0.08), (0.0, vo - 0.11, ZTM - 0.08 + 0.055)])
    zb = 1.86
    f.cable([(0.0, vo, zo), (0.0, vo, zb + 0.06)])
    f.box("steel", (0.0, vo, zb + 0.035), (0.03, 0.02, 0.05), soft=0.002)
    bar = [(-0.62, vo + 0.03, zb - 0.10), (-0.48, vo, zb), (0.48, vo, zb), (0.62, vo + 0.03, zb - 0.10)]
    f.sweep("steel", bar, f.k.circle(0.0145, 18), bend=0.08, soft=0.0)
    for s in (-1, 1):
        f.tube("rubber", (s * 0.30, vo, zb), (s * 0.47, vo, zb), 0.018, soft=0.003)
    # the seat frame: a beam out along the floor from the bottom cross-member to the seat post, its foot
    vs, zs = A + 0.70, 0.45
    f.bar("frame", (0.0, A + CM[0] / 2, ZBC), (0.0, vs + 0.05, ZBC), 0.076, 0.076, up="z",
          cut0=((0, A + CM[0] / 2, 0), (0, 1, 0)), weld=True)
    f.box("rubber", (0.0, vs + 0.05, (FOOT_H + ZBC - 0.038) / 2), (0.16, 0.10, ZBC - 0.038 - FOOT_H + 0.004), soft=0.006)
    f.bar("frame", (0.0, vs, ZBC + 0.038), (0.0, vs, zs - 0.041), 0.07, 0.07, up="v", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)),
          weld=True)
    f.box("frame", (0.0, vs, zs - 0.035), (0.30, 0.26, 0.012), soft=0.002)
    f.box("pad", (0.0, vs, zs), (0.40, 0.34, 0.07), soft=0.03)
    # the knee pads' post from the seat beam up to the roller pair over the thighs, its pop pin
    vk, zk = A + 0.48, 0.67
    f.bar("frame", (0.0, vk, ZBC + 0.038), (0.0, vk, zk - 0.04), 0.06, 0.06, up="v", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)),
          weld=True)
    f.tube("steel", (-0.30, vk, zk), (0.30, vk, zk), 0.018, seg=18)
    f.box("frame", (0.0, vk, zk - 0.01), (0.13, 0.07, 0.08), soft=0.004)            # the hub the pads' shaft runs in
    for s in (-1, 1):
        f.tube("pad", (s * 0.06, vk, zk), (s * 0.28, vk, zk), 0.06, seg=36, soft=0.01)
    f.cyl("plastic", (0.0, vk + 0.045, zk - 0.12), 0.016, 0.03, axis="v")          # its pop pin
    placard(f, A, 1.25)
    return dict(seat=(vs, zs), knee=(vk, zk), bar=(vo, zb))


def row(k, c, out):
    """Row (LPP-RW): the stack, the cable over a short top mount and down the face to the low pulley, the row handle;
    the long bench out along the floor with the foot plate near the Core (the manual's drawing)."""
    f = Face(k, c, out)
    zt = f.stack(VS, A)
    vo, zo = top_mount(f, 0.06)
    f.cable([(0.0, VS, zt), (0.0, VS, ZTM - 0.08 - 0.055 + 0.01)])
    f.cable([(0.0, VS + 0.055, ZTM - 0.08), (0.0, vo - 0.11, ZTM - 0.08 + 0.055)])
    # the low pulley's bracket off the bottom cross-member, the cable down to it and out to the handle
    zl = 0.48
    f.bar("frame", (0.0, A + CM[0] / 2, ZBC), (0.0, A + 0.10, ZBC), 0.07, 0.076, up="z", cut0=((0, A + CM[0] / 2, 0), (0, 1, 0)),
          weld=True)
    f.bar("frame", (0.0, A + 0.10, ZBC + 0.038), (0.0, A + 0.10, zl - 0.06), 0.06, 0.06, up="v",
          cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    for su in (-1, 1):
        f.box("frame", (su * 0.034, A + 0.10, zl), (0.008, 0.12, 0.12), soft=0.002)
    f.pulley((0.0, A + 0.10, zl), 0.055, axis="u")
    f.tube("chrome", (-0.036, A + 0.10, zl), (0.036, A + 0.10, zl), 0.008, seg=12)          # its axle
    for su in (-1, 1):                                  # the spacers from the wheel to the cheeks
        f.tube("steel", (su * 0.008, A + 0.10, zl), (su * 0.031, A + 0.10, zl), 0.014, seg=16)
    f.cable([(0.0, vo, zo), (0.0, A + 0.10 + 0.055, zl + 0.01)])
    f.cable([(0.0, A + 0.10, zl + 0.055), (0.0, A + 0.24, zl + 0.04)])
    f.box("steel", (0.0, A + 0.26, zl + 0.04), (0.03, 0.04, 0.02), soft=0.002)
    f.sweep("steel", [(-0.08, A + 0.36, zl), (-0.03, A + 0.28, zl + 0.04), (0.03, A + 0.28, zl + 0.04), (0.08, A + 0.36, zl)],
            f.k.circle(0.012, 16), bend=0.03, soft=0.0)
    for s in (-1, 1):
        f.tube("rubber", (s * 0.08, A + 0.36, zl), (s * 0.08, A + 0.44, zl - 0.02), 0.017, soft=0.003)
    # the bench: its beam off the bottom bracket out along the floor, the foot plate's post and two angled foot pads, the
    # bench pad on its post, the far leg and foot
    vb0, vb1, zp = A + 0.14, A + 1.70, 0.42
    f.bar("frame", (0.0, A + 0.10 + 0.035, ZBC), (0.0, vb1, ZBC), 0.076, 0.076, up="z", cut0=((0, A + 0.135, 0), (0, 1, 0)),
          weld=True)
    f.box("rubber", (0.0, vb1 - 0.05, (FOOT_H + ZBC - 0.038) / 2), (0.16, 0.10, ZBC - 0.038 - FOOT_H + 0.004), soft=0.006)
    vf = A + 0.42
    f.bar("frame", (0.0, vf, ZBC + 0.038), (0.0, vf - 0.06, 0.36), 0.05, 0.05, up="v", cut0=((0, 0, ZBC + 0.038), (0, 0, 1)),
          weld=True)
    a = math.radians(55)
    for s in (-1, 1):
        f.box("frame", (s * 0.10, vf - 0.08, 0.36), (0.10, 0.012, 0.18), soft=0.003)
        f.box("rubber", (s * 0.10, vf - 0.074, 0.36), (0.09, 0.004, 0.16), soft=0.002)
    f.box("frame", (0.0, vf - 0.075, 0.36), (0.30, 0.02, 0.04), soft=0.003)
    for vpst in (A + 0.85, A + 1.55):
        f.bar("frame", (0.0, vpst, ZBC + 0.038), (0.0, vpst, zp - 0.06), 0.06, 0.06, up="v",
              cut0=((0, 0, ZBC + 0.038), (0, 0, 1)), weld=True)
    f.box("frame", (0.0, (A + 0.75 + A + 1.65) / 2, zp - 0.048), (0.24, 0.92, 0.024), soft=0.002)
    f.box("pad", (0.0, (A + 0.72 + A + 1.68) / 2, zp), (0.30, 0.96, 0.07), soft=0.03)
    placard(f, -A, 1.25)
    return dict(seat=(A + 1.0, zp), foot=(vf - 0.08, 0.36), handle=(A + 0.40, zl))


def triceps(k, c, out):
    """Triceps Pushdown (LPP-TP): the stack, a top mount out past the face, the rope hung from it."""
    f = Face(k, c, out)
    zt = f.stack(VS, A)
    vo, zo = top_mount(f, 0.36)
    f.cable([(0.0, VS, zt), (0.0, VS, ZTM - 0.08 - 0.055 + 0.01)])
    f.cable([(0.0, VS + 0.055, ZTM - 0.08), (0.0, vo - 0.11, ZTM - 0.08 + 0.055)])
    zr = 1.62
    f.cable([(0.0, vo, zo), (0.0, vo, zr + 0.07)])
    f.box("steel", (0.0, vo, zr + 0.05), (0.025, 0.02, 0.04), soft=0.002)
    for s in (-1, 1):
        f.sweep("rope", [(0.0, vo, zr + 0.035), (s * 0.03, vo, zr - 0.02), (s * 0.05, vo, zr - 0.34)], f.k.circle(0.013, 14),
                bend=0.05, soft=0.0)
        f.cyl("rubber", (s * 0.05, vo, zr - 0.36), 0.024, 0.045, soft=0.006)
    placard(f, A, 1.25)


def carriage(f, v_face, zc, handle=True):
    """An adjustable carriage on face f: the chrome track up the face (7-76 in), its brackets top and bottom, the
    carriage at zc with its pop pin, the swivel pulley with the yellow ring, the D handle."""
    vt = v_face + 0.03
    z0, z1 = 0.18, 1.98
    f.box("chrome", (0.0, vt, (z0 + z1) / 2), (0.05, 0.02, z1 - z0), soft=0.002)
    for i in range(36):
        f.box("hole", (0.0, vt + 0.0102, z0 + 0.05 + i * 0.048), (0.016, 0.0006, 0.026), soft=0.0)
    for z in (z0, z1):
        f.box("frame", (0.0, v_face + 0.012, z), (0.07, 0.025, 0.05), soft=0.003)
    f.box("frame", (0.0, vt + 0.04, zc), (0.11, 0.06, 0.20), soft=0.008)
    f.cyl("plastic", (0.0, vt + 0.08, zc + 0.07), 0.018, 0.035, axis="v", soft=0.004)
    f.box("frame", (0.0, vt + 0.09, zc - 0.03), (0.04, 0.04, 0.05), soft=0.004)
    f.cyl("plastic", (0.0, vt + 0.14, zc - 0.03), 0.075, 0.035, axis="u", soft=0.004)
    f.disc("yellow", (0.018, vt + 0.14, zc - 0.03), 0.06, 0.035, 0.002, axis="u", seg=40)
    f.cyl("chrome", (0.02, vt + 0.14, zc - 0.03), 0.012, 0.006, axis="u", seg=16)
    if handle:
        zh = zc - 0.21
        f.cable([(0.0, vt + 0.19, zc - 0.05), (0.0, vt + 0.19, zh + 0.05)])
        f.sweep("steel", [(-0.07, vt + 0.19, zh), (0.0, vt + 0.19, zh + 0.05), (0.07, vt + 0.19, zh), (-0.07, vt + 0.19, zh)],
                f.k.circle(0.006, 10), bend=0.02, soft=0.0)
        f.tube("rubber", (-0.06, vt + 0.19, zh + 0.004), (0.06, vt + 0.19, zh + 0.004), 0.015, soft=0.003)


def crossover_core(k, c, out):
    """The Core's side of the attached crossover (LPP-CC): the stack, the carriage track up the face, the carriage."""
    f = Face(k, c, out)
    zt = f.stack(VS, A, hang=False)
    f.cable([(0.0, VS, zt), (0.0, VS, ZTC - CM[1] / 2 - 0.012)])
    carriage(f, A + CM[0] / 2, 1.40)
    placard(f, A, 1.25)


def beam(k, a, b, z, handles=True):
    """The crossbar connector between two top mounts a and b (x, y), its holes, the pull-up handles hung from it: the
    multi-grip set of three (ref_02)."""
    looks(k)
    k.bar("boom", (a[0], a[1], z), (b[0], b[1], z), 0.076, 0.10, up=(0, 0, 1))
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    for i in range(10):
        t = 0.08 + i * 0.03
        k.cyl("hole", (a[0] + ux * L * t + nx * 0.0385, a[1] + uy * L * t + ny * 0.0385, z), 0.006, 0.001,
              axis="x" if abs(nx) > 0.5 else "y", seg=12)
    if handles:
        for t, w in ((0.36, 0.22), (0.50, 0.22), (0.64, 0.22)):
            cx, cy = a[0] + ux * L * t, a[1] + uy * L * t
            pts = [(cx - ux * w / 2, cy - uy * w / 2, z - 0.05), (cx - ux * w / 2 + ux * 0.02, cy - uy * w / 2 + uy * 0.02, z - 0.24),
                   (cx + ux * w / 2 - ux * 0.02, cy + uy * w / 2 - uy * 0.02, z - 0.24), (cx + ux * w / 2, cy + uy * w / 2, z - 0.05)]
            k.sweep("frame", pts, k.circle(0.016, 16), bend=0.05, soft=0.0)
            k.tube("rubber", (pts[1][0] + ux * 0.03, pts[1][1] + uy * 0.03, z - 0.24), (pts[2][0] - ux * 0.03, pts[2][1] - uy * 0.03, z - 0.24),
                   0.02, soft=0.003)
            for e in (pts[0], pts[3]):
                k.box("frame", (e[0], e[1], z - 0.05 + 0.002), (0.04, 0.05, 0.004), soft=0.001)


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
    carriage(f, CM[0] / 2, 1.40)
    f.box("frame", (0.0, 0.0, zt0 + LEG / 2 + 0.006), (0.16, 0.16, 0.012), soft=0.003)
    return f.p(0.0, 0.0, zt0 + LEG / 2 + 0.012)

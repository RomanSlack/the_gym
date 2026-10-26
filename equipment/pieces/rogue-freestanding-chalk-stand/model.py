"""Rogue Chalk Stand, freestanding, with casters (refs/: ref_01 in a gym, a belt and collars hung on it; ref_02 a hanger:
a plate bolted to the upright with four upturned prongs; ref_03 the base: four plate fins in a cross with the R cut
through, a caster under each; ref_04 a belt and collars on a hanger; ref_05 the whole: the stainless bowl on top).
The linked page: 38.5 in high without wheels, a 2 x 2 in 11-gauge upright, a 0.375 in plate base with the logo cut,
a stainless bowl 13.625 in across and 5 in deep, two sets of bolt-on hangers 5.75 in out, casters optional. Fetched
2026-10-25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Chalk by the platform: hands into the bowl; belts, collars, straps hung on the hangers; rolled where needed.
2. Each mass named (ref_03 / ref_05): the base, four 3/8 in plate fins in a cross welded to the upright's foot, the R
   cut through one, a caster under each fin's tip; the upright, 2 x 2 in, holes up its faces; two hangers, each a
   plate bolted to a face with four prongs turned up; the bowl, stainless, on a plate at the top, chalk in it.
3. Adjustments. The hangers' height (bolted at any hole); rolled on its casters.
4. Load path. The hands in the bowl, the bowl's plate, the upright, the fins, the casters.
5. Fit range. The bowl's rim at 1.06 m (with the casters): about the hips of the 1.78 m user, the waist of the 1.55,
   the upper thigh of the 1.95: every user chalks up without stooping. No figure.
6. Size. About 0.55 x 0.55 x 1.06 m.
Axes: metres, floor z = 0; the fins on the axes, the hangers on the -y and +x faces.
"""
import math

IN = 0.0254
CAST = 0.085                          # the casters' height
H = 38.5 * IN
UP = 2 * IN
R_BOWL, D_BOWL = 13.625 * IN / 2, 5 * IN
FIN = 0.27                            # a fin's reach from the upright's middle

LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.45, coat=0.15, bump=(900, 0.05)),
    "steel": dict(color=(0.75, 0.75, 0.77), rough=0.15, metal=1.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0),
    "wheel": dict(color=(0.02, 0.02, 0.022), rough=0.6, coat=0.0),
    "chalk": dict(color=(0.85, 0.85, 0.84), rough=0.95, coat=0.0, bump=(800, 0.3)),
}
VIEWS = {"three_quarter": (-35, 18, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
DETAILS = {
    "detail_base": ((-0.75, -0.75, 0.45), (0.0, 0.0, 0.10), 35),        # the fins, the R, the casters
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zb = CAST
    for i in range(4):                                  # the fins, a caster under each tip
        a = i * math.pi / 2                             # the fins on the axes (ref_03)
        ca, sa = math.cos(a), math.sin(a)
        t = 0.0095

        def fin(cx, cy, cz, ca=ca, sa=sa):
            r = UP / 2 if cx < 0 else FIN
            z = zb + (0.0 if cz < 0 else (0.20 if cx < 0 else 0.03))
            return (r * ca - cy * t / 2 * sa, r * sa + cy * t / 2 * ca, z)
        k.block("frame", fin, soft=0.001)
        tx, ty = (FIN - 0.03) * ca, (FIN - 0.03) * sa
        k.box("frame", (tx, ty, zb - 0.005), (0.06, 0.06, 0.012), soft=0.002)                         # caster plate
        k.box("frame", (tx, ty, zb - 0.03), (0.035, 0.012, 0.035), soft=0.002)                         # its fork
        k.cyl("wheel", (tx, ty, 0.035), 0.035, 0.025, axis="y", seg=24, soft=0.004)
    k.text("hole", "R", (0.006, -0.10, zb + 0.07), 0.05, rz=math.pi / 2, depth=0.011)             # cut through a fin
    k.bar("frame", (0, 0, zb), (0, 0, zb + H - 0.01), UP, UP, r=0.003)                              # the upright
    z = zb + 0.12
    while z < zb + H - 0.06:                            # its holes
        for ax, sg in (("y", -1), ("x", 1)):
            c = (0, sg * (UP / 2 + 0.0003), z) if ax == "y" else (sg * (UP / 2 + 0.0003), 0, z)
            k.cyl("hole", c, 0.008, 0.0008, axis=ax, seg=12, soft=0.0)
        z += IN
    for ax in ("y", "x"):                               # the two hangers, four prongs each turned up
        zh = zb + 0.62
        if ax == "y":
            k.box("frame", (0, -UP / 2 - 0.004, zh), (0.10, 0.008, 0.10), soft=0.002)
        else:
            k.box("frame", (UP / 2 + 0.004, 0, zh), (0.008, 0.10, 0.10), soft=0.002)
        for j, off in enumerate((-0.04, -0.013, 0.013, 0.04)):
            out = 5.75 * IN
            if ax == "y":
                pts = [(off, -UP / 2 - 0.008, zh - 0.02), (off, -UP / 2 - out, zh - 0.02), (off, -UP / 2 - out - 0.01, zh + 0.03)]
            else:
                pts = [(UP / 2 + 0.008, off, zh - 0.02), (UP / 2 + out, off, zh - 0.02), (UP / 2 + out + 0.01, off, zh + 0.03)]
            k.sweep("frame", pts, k.rect(0.008, 0.012, 0.002), bend=0.02, soft=0.0)
    top = zb + H
    k.box("frame", (0, 0, top - 0.006), (0.16, 0.16, 0.012), soft=0.002)                            # the bowl's plate
    prof = [(0.07, 0.0), (0.10, 0.004), (R_BOWL * 0.85, D_BOWL * 0.35), (R_BOWL - 0.004, D_BOWL * 0.9),
            (R_BOWL + 0.006, D_BOWL), (R_BOWL - 0.004, D_BOWL), (R_BOWL - 0.012, D_BOWL * 0.9),
            (R_BOWL * 0.85 - 0.006, D_BOWL * 0.38), (0.10, 0.008), (0.0, 0.008)]
    k.lathe("steel", (0, 0, top), prof, seg=64)                                                      # the bowl
    k.lathe("chalk", (0, 0, top), [(0.09, 0.008), (0.13, D_BOWL * 0.5), (0.0, D_BOWL * 0.55)], seg=40)    # chalk

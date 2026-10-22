"""Rogue Rubber Hex Dumbbells (kg), a row of pairs on the floor: 5, 10, 20, 30, 40, 50 kg.

Built by eye from Rogue's photo (refs/: ref_01, the full sets on a shelving rack; the rack is not one of the picks).
Every weight is the same dumbbell grown: the head's volume set by its mass (cast iron in a rubber hex, flat down,
about half as long as it is across), the handle the same chrome with a knurled middle and a steel collar into each
head. The three sets in the gym (2.5-50 kg, 52.5-75 kg, 2-40 kg by the den mirror) are this function at other weights.
Axes: metres, floor z = 0, each handle along x, the pairs side by side along y, lightest at -y.
Head: the weight raised on its outer end, ROGUE raised on its top flat.
"""
import math

LOOK = {
    "rubber": dict(color=(0.010, 0.010, 0.011), rough=0.62, coat=0.0, bump=(900, 0.06)),
    "emboss": dict(color=(0.014, 0.014, 0.015), rough=0.45, coat=0.0),
    "chrome": dict(color=(0.74, 0.74, 0.76), rough=0.06, metal=1.0, coat=0.0, aniso=0.3),
    "steel": dict(color=(0.6, 0.6, 0.61), rough=0.25, metal=1.0, coat=0.0, aniso=0.5),
}
VIEWS = {"three_quarter": (-50, 26, 1.0), "front": (-90, 8, 1.0), "side": (0, 8, 1.0), "back_three_quarter": (130, 28, 1.0)}
DETAILS = {"detail_head": ((0.42, -0.62, 0.30), (0.12, -0.42, 0.07), 45)}   # a 20 kg head: the number, the plaque, the handle

WEIGHTS = (5, 10, 20, 30, 40, 50)
GRIP = 0.135                     # between the heads
HR = 0.0165                      # the handle's radius


def head_size(kg):
    """(across the flats, length) of one head: half the dumbbell less the handle, iron in rubber (~6.6 t/m3)."""
    v = max(kg / 2 - 0.6, 0.3) / 6600
    f = max((v / (math.sqrt(3) / 2 * 0.55)) ** (1 / 3), 0.075)
    return f, max(v / (math.sqrt(3) / 2 * f * f), 0.04)        # the light ones: a small head no shorter than 4 cm


def dumbbell(k, kg, y, n):
    f, hl = head_size(kg)
    z = f / 2
    rc = f / math.sqrt(3)
    hexp = __import__("kit")._round_poly([(rc * math.cos(math.radians(60 * i)), rc * math.sin(math.radians(60 * i))) for i in range(6)],
                                         0.006, 3)
    k.look(**{f"knurl{n}": dict(color=(0.30, 0.30, 0.31), rough=0.45, metal=0.85, coat=0.0,
                                knurl=dict(c=(y, z), r=HR, pitch=0.0016, strength=0.8))})
    k.tube("chrome", (-GRIP / 2, y, z), (-0.045, y, z), HR, seg=32)
    k.tube(f"knurl{n}", (-0.045, y, z), (0.045, y, z), HR, seg=32)
    k.tube("chrome", (0.045, y, z), (GRIP / 2, y, z), HR, seg=32)
    for s in (1, -1):
        x0 = s * GRIP / 2
        k.cyl("steel", (x0 - s * 0.004, y, z), 0.024, 0.008, axis="x", seg=32, soft=0.0015)
        k.sweep("rubber", [(x0, y, z), (x0 + s * hl, y, z)], hexp, up=(0, 0, 1), soft=0.004)
        xe = x0 + s * hl
        k.text("emboss", f"{kg}", (xe + s * 0.0008, y, z + f * 0.08), f * 0.32, rz=s * math.pi / 2, depth=0.002)
        k.text("emboss", "KG", (xe + s * 0.0008, y, z - f * 0.24), f * 0.12, rz=s * math.pi / 2, depth=0.002)
        xm = x0 + s * hl / 2
        k.box("emboss", (xm, y, f + 0.0008), (hl * 0.62, rc * 0.78, 0.0016), soft=0.0006)
        k.text("rubber", "ROGUE", (xm, y, f + 0.0019), min(hl * 0.3, rc * 0.2), rz=math.pi / 2, rx=0.0, depth=0.0012)


def build(k):
    ys, y = [], 0.0
    for kg in WEIGHTS:
        f, _ = head_size(kg)
        for _ in range(2):
            ys.append((kg, y + f / 2)); y += f + 0.03
        y += 0.06
    for n, (kg, yy) in enumerate(ys):
        dumbbell(k, kg, yy - y / 2, n)          # the row centred on y = 0

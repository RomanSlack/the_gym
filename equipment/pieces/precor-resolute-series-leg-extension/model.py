"""Precor Resolute Series Leg Extension (RSL0605).
Spec (precor.com): 155 x 127 x 147 cm (L x W x H), stack tower 148 cm, 109 kg stack, 279 kg; upholstery 65 mm
(19 mm plywood + 2 x 19 mm foam + vinyl); welded steel tubing, powder coat (Black Pearl). Wide seat; back pad on a gas
spring, start position + roller pad adjust from the seat (orange handles).
Axes: metres, floor z = 0, the user sits facing -y; x+ = the user's left. The stack tower stands on the user's right.
"""
import math

LOOK = {
    "frame": dict(color=(0.02, 0.02, 0.022), rough=0.32, metal=0.25, coat=0.4, bump=(900, 0.06)),  # Black Pearl
    "pad": dict(color=(0.42, 0.15, 0.06), rough=0.5, sheen=0.3, bump=(1400, 0.1)),                  # cognac vinyl, as the photo
    "seam": dict(color=(0.3, 0.1, 0.04), rough=0.6),
    "accent": dict(color=(0.95, 0.38, 0.02), rough=0.35),                                          # the orange adjusters
    "label": dict(color=(0.9, 0.9, 0.9), rough=0.4),
    "placard": dict(color=(0.12, 0.13, 0.14), rough=0.3, coat=0.5),
}
VIEWS = {"three_quarter": (40, 16, 1.0)}  # the photo's angle: front-left of the user

PIV = (-0.255, -0.24, 0.60)    # knee pivot (axle along x), level with the knee
SEAT_TOP = 0.52


def build(k):
    # ---- the stack tower on the user's right: a D-shaped shroud, flat face towards the seat
    tx0, tx1, ty0, ty1, H = -0.76, -0.31, -0.70, -0.08, 1.47
    cy, half = (ty0 + ty1) / 2, (ty1 - ty0) / 2
    a, b = 0.17, 0.28                       # flat face a in front of the sweep line, half-ellipse b behind it
    base = tx1 - a
    cx = (tx0 + tx1) / 2
    # D outline as (dx, dy) round the sweep line; a vertical sweep maps (u, v) to (-dx, dy)
    D = [(a, -half), (a, half)] + [(b * math.cos(math.radians(90 + 180 * i / 24)), half * math.sin(math.radians(90 + 180 * i / 24))) for i in range(25)]
    uv = lambda sc: [(-dx * sc, dy * sc) for dx, dy in D]
    k.sweep("frame", [(base, cy, 0.03), (base, cy, H - 0.07)], uv(1.0), soft=0.006)
    # top: a dark tray cap, a touch proud all round, a rubber mat in it
    k.sweep("plastic", [(base, cy, H - 0.075), (base, cy, H)], uv(1.03), soft=0.01)
    k.sweep("rubber", [(base, cy, H - 0.012), (base, cy, H + 0.002)], uv(0.9), soft=0.004)
    # base plinth + feet
    k.box("frame", (cx - 0.02, cy, 0.03), (a + b + 0.06, ty1 - ty0 + 0.08, 0.06), soft=0.008)
    for fy in (ty0 + 0.02, ty1 - 0.02):
        k.cyl("rubber", (cx, fy, 0.004), 0.05, 0.012)
    # the face (x = tx1): the slot down the middle with the chrome selector stem, placards each side, the logo
    fx = tx1 + 0.002
    k.box("plastic", (fx, cy, 0.68), (0.006, 0.05, 1.0), soft=0.0)  # dark slot
    k.tube("chrome", (fx - 0.01, cy, 0.25), (fx - 0.01, cy, 1.18), 0.008)
    for s in (-1, 1):
        k.box("placard", (fx + 0.002, cy + s * 0.13, 1.06), (0.004, 0.16, 0.28), soft=0.0015)
    k.box("plastic", (fx + 0.001, cy, 1.24), (0.004, 0.48, 0.035), soft=0.001)
    k.text("label", "PRECOR", (fx + 0.004, cy, 1.33), 0.055, rz=math.pi / 2)
    # the stack inside, seen through the slot's foot: plates + weight numbers
    k.stack((cx + 0.02, cy, 0.03), n=18, w=0.26, d=0.12, rods=0.40, top=H - 0.09)
    for i in range(18):
        k.box("label", (fx + 0.002, cy + 0.045, 0.1 + i * 0.026), (0.003, 0.012, 0.008), soft=0.0)

    # ---- the cam housing on the tower face at the knee pivot, the axle, the start-position dial
    px, py, pz = PIV
    k.cyl("frame", (tx1 + 0.06, py, pz), 0.15, 0.10, axis="x", seg=48, soft=0.01)
    k.cyl("plastic", (tx1 + 0.112, py, pz), 0.125, 0.006, axis="x", seg=48)
    k.tube("chrome", (tx1, py, pz), (px + 0.04, py, pz), 0.02)
    k.disc("frame", (px - 0.035, py, pz), 0.085, 0.02, 0.012, axis="x")
    for i in range(6):  # the numbered holes of the start dial
        a = math.radians(95 + i * 24)
        k.cyl("label", (px - 0.043, py + 0.068 * math.cos(a), pz + 0.068 * math.sin(a)), 0.006, 0.004, axis="x", seg=10)
    k.cyl("alu", (px + 0.03, py, pz), 0.032, 0.02, axis="x")  # silver hub cap
    k.cyl("accent", (px - 0.02, py + 0.04, pz + 0.12), 0.012, 0.05, axis="x")  # the orange start-position pin

    # ---- the lever: one straight oval arm through the pivot, the shin roller low in front, a foam-sleeved end up behind
    d = (0.0, -math.sin(math.radians(28)), -math.cos(math.radians(28)))  # down and forward from the pivot
    lo = (px, py + d[1] * 0.40, pz + d[2] * 0.40)
    hi = (px, py - d[1] * 0.42, pz - d[2] * 0.42)
    k.sweep("frame", [lo, PIV, hi], k.stadium(0.075, 0.04), up=(1, 0, 0))
    k.sweep("rubber", [(px, py - d[1] * 0.26, pz - d[2] * 0.26), (px, py - d[1] * 0.46, pz - d[2] * 0.46)], k.circle(0.032, 24))
    # the roller-pad slider (telescoping, a pop pin) and the roller across under the shins
    k.sweep("frame", [(px, lo[1] - 0.01, lo[2] + 0.02), (px, lo[1] + d[1] * 0.12, lo[2] + d[2] * 0.12)], k.rect(0.06, 0.06, 0.008), up=(1, 0, 0))
    rz_, ry_ = lo[2] + d[2] * 0.10, lo[1] + d[1] * 0.10
    k.cyl("alu", (px - 0.035, lo[1] + 0.04, lo[2] + 0.05), 0.022, 0.02, axis="x")
    k.tube("chrome", (px, ry_, rz_), (0.22, ry_, rz_), 0.015)
    k.cyl("pad", ((px + 0.03 + 0.24) / 2 + 0.0, ry_, rz_), 0.062, 0.40, axis="x", seg=40, soft=0.012)
    k.cyl("plastic", (0.245, ry_, rz_), 0.058, 0.03, axis="x", seg=40, soft=0.006)

    # ---- the frame: a curved oval spine from the tower under the seat to the back post
    sp = k.stadium(0.11, 0.055)
    k.sweep("frame", [(tx1 - 0.02, -0.40, 0.30), (-0.12, -0.28, 0.36), (0.0, -0.05, 0.38), (0.0, 0.40, 0.38), (0.0, 0.55, 0.30)], sp, bend=0.18, up=(0, 0, 1))
    # the user's-left A leg: front foot under the seat front, rear foot behind, on a floor rail
    L = k.rect(0.08, 0.05, 0.012)
    k.sweep("frame", [(0.42, -0.20, 0.03), (0.42, -0.08, 0.40), (0.42, 0.22, 0.40), (0.42, 0.70, 0.03)], L, bend=0.14, up=(1, 0, 0))
    k.bar("frame", (0.42, -0.24, 0.025), (0.42, 0.74, 0.025), 0.07, 0.045)
    for fy in (-0.25, 0.75):
        k.box("rubber", (0.42, fy, 0.006), (0.12, 0.14, 0.012), soft=0.004)
    # cross members to the spine + the floor tie to the tower
    k.bar("frame", (0.0, 0.05, 0.38), (0.42, 0.05, 0.40), 0.07, 0.05)
    k.bar("frame", (tx1 - 0.02, 0.35, 0.03), (0.42, 0.35, 0.03), 0.07, 0.045)
    k.bar("frame", (0.0, 0.40, 0.42), (0.0, 0.40, 0.05), 0.07, 0.05)

    # ---- the seat: wide, on a mounting plate, a touch up at the front
    k.box("frame", (0.0, 0.0, 0.43), (0.30, 0.36, 0.02), soft=0.003)
    k.pad("pad", (0.0, 0.0, SEAT_TOP - 0.0325), (0.44, 0.46, 0.065), r=0.03, rx=-0.05)
    # ---- the back pad on its post, gas spring adjust with the orange lever
    k.bar("frame", (0.0, 0.52, 0.42), (0.0, 0.50, 1.02), 0.08, 0.06, up=(0, 1, 0))
    k.box("frame", (0.0, 0.47, 0.82), (0.16, 0.05, 0.36), rx=math.radians(-10), soft=0.004)
    k.pad("pad", (0.0, 0.40, 0.89), (0.40, 0.70, 0.065), r=0.03, rx=math.radians(80))
    k.tube("cable", (0.0, 0.52, 0.42), (0.0, 0.49, 0.78), 0.012)  # gas spring
    k.box("accent", (0.235, 0.47, 0.78), (0.03, 0.06, 0.11), soft=0.006)
    # ---- hand grips each side of the seat
    for s in (-1, 1):
        x0 = s * 0.20
        k.sweep("frame", [(x0 * 0.6, 0.12, 0.42), (s * 0.28, 0.10, 0.44), (s * 0.30, -0.08, 0.47)], k.circle(0.016), bend=0.06)
        k.sweep("rubber", [(s * 0.30, -0.02, 0.465), (s * 0.30, -0.15, 0.475)], k.circle(0.019, 20))
        k.cyl("alu", (s * 0.30, -0.155, 0.475), 0.02, 0.012, axis="y")


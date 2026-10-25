"""Rogue 10 Bar Holder (refs/: ref_01 / ref_03 empty from the front left and the front; ref_02 loaded with bars on end).
The linked page: 32-3/8 x 26 x 10-1/2 in, 2 x 3 in 11-gauge rails, ten 2 in ID tubes 7 in long, 3/8 in laser-cut end
plates, foot plates with holes to bolt down, black, 75 lb. Fetched 2026-10-24 / 25. Built to the two gates and README
point 9.

DESIGN SPEC (gate 1)
1. Use. Barbells stand on end, a sleeve down in a tube, the knurl off the floor and off each other; a bar is lifted out
   by its shaft and set back.
2. Each mass named (ref_01 / ref_03): two 2 x 3 in rails along the length, a row of five tubes through each (the rows
   staggered half a pitch, ref_03), each tube 2 in inside, 7 in long, its foot clear of the floor; an end plate at each
   end, 3/8 in, arched underneath, ROGUE on its face, the rails' ends welded to it, a foot plate at each of its two
   feet with a hole for an anchor. Colour: Roman's for the Rogue storage (2026-10-25): the end plates red, the rails and
   tubes black (the photos all black).
3. Adjustments. None.
4. Load path. A bar's weight down its sleeve onto the tube's bottom stop, the tube, the rail, the end plates, the feet.
5. Fit range. A 2.2 m bar stands with its top end at 2.3 m and its shaft from 0.5 m up: every user (1.55 / 1.78 /
   1.95 m) takes it by the shaft at the chest and lifts it 0.25 m to clear the tube. No figure.
6. Size. 0.82 x 0.66 x 0.27 m (32-3/8 x 26 x 10-1/2 in).
Axes: metres, floor z = 0; the rails along x, the end plates in y.
"""
import math

IN = 0.0254
L = 32.375 * IN                       # over the end plates
W = 26 * IN                           # the end plates' feet
H = 10.5 * IN                         # the tubes' tops
PE = 0.375 * IN
RW, RH = 2 * IN, 3 * IN               # the rails
Y_ROW = 2.6 * IN                      # the rows (y)
Z_RAIL = 6.0 * IN                     # the rails' centre
R_TUBE, R_IN = 1.25 * IN, 1.0 * IN
PITCH = 6.0 * IN

LOOK = {
    "frame": dict(color=(0.50, 0.012, 0.012), rough=0.32, coat=0.25, bump=(900, 0.05)),        # Rogue red (Roman)
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.85, 0.85, 0.86), rough=0.4, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0),
}
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 10, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 22, 1.0),
         "ref_view": (-40, 18, 1.0)}                  # ref_01
DETAILS = {
    "detail_end": ((-0.75, -0.55, 0.40), (-0.38, 0.0, 0.12), 40),       # an end plate, ROGUE, a foot plate
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    xe = L / 2 - PE / 2
    # the end plates: an arch in y, flat across the top under the rails' ends, a foot at each end
    for sx in (1, -1):
        x = sx * xe
        zt, d = Z_RAIL + RH / 2, 3.5 * IN                 # its top (level with the rails' tops) and its depth
        yo, yi = W / 2 - 0.5 * IN, W / 2 - 2.5 * IN       # a leg's outer and inner edges at the floor
        rc, ri = 2.5 * IN, 2.5 * IN                       # the outer corner's and the arch's corner radius
        sl = 3.2 * IN                                     # the legs slant in by this up to the top (ref_01)
        out = [(yo, 0.012)] + [(yo - sl - rc + rc * math.cos(math.radians(t)), zt - rc + rc * math.sin(math.radians(t)))
                               for t in range(-25, 91, 15)]
        inner = [(yi - sl - ri + ri * math.cos(math.radians(t)), zt - d - ri + ri * math.sin(math.radians(t)))
                 for t in range(-25, 91, 15)]
        prof = (out + [(-y, z) for y, z in out[::-1]] + [(-yi, 0.012)] + [(-y, z) for y, z in inner]
                + inner[::-1] + [(yi, 0.012)])         # round the outside, then back under the arch
        k.slab("frame", prof, x - PE / 2, x + PE / 2, 0.001)
        k.text("label", "ROGUE", (x + sx * (PE / 2 + 0.0003), 0.0, Z_RAIL - 0.005), 0.05, rz=sx * math.pi / 2,
               depth=0.0006)
        for sy in (1, -1):                              # the foot plates, an anchor hole each
            k.box("frame", (x - sx * 0.02, sy * (W / 2 - 1.2 * IN), 0.006), (0.075, 2.4 * IN, 0.012), soft=0.0015)
            k.cyl("hole", (x - sx * 0.02, sy * (W / 2 - 1.0 * IN), 0.0123), 0.3 * IN, 0.0008, seg=16, soft=0.0)
    # the rails and the tubes through them
    for r, sy in enumerate((-1, 1)):
        y = sy * Y_ROW
        k.bar("black", (-xe + PE / 2, y, Z_RAIL), (xe - PE / 2, y, Z_RAIL), RW, RH, r=0.003)
        for i in range(5):
            x = (i - 2) * PITCH + (0.25 if r else -0.25) * PITCH
            z0 = H - 7 * IN
            k.cyl("black", (x, y, (z0 + H) / 2), R_TUBE, H - z0, seg=32, soft=0.002)
            k.cyl("hole", (x, y, H + 0.0003), R_IN, 0.0008, seg=32, soft=0.0)

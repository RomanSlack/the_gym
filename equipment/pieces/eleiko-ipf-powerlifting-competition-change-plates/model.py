"""Eleiko IPF Powerlifting Competition Change Plates, 5 / 2.5 / 1.25 / 0.5 / 0.25 kg (refs/: ref_01 the black 2.5 kg's
front (ELEIKO over and under the bore, 2,5 either side, one turned over) and back (the calibration plugs, ELEIKO round
the rim); ref_02 the same pair; Eleiko's photo of the set stacked on a floor is the IPF plates' ref_04: the white 5 at
the bottom, the black 2.5, the smaller three chromed). Fetched 2026-10-25 off Eleiko's 2.5 kg page (the linked outlet
page is gone). Sizes from a reseller's table (oprema.fit): 228 / 190 / 160 / 134 / 112 mm across, 20 / 15 / 12 / 8 / 7 mm
thick. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. The small calibrated steps for an attempt's last kilos, loaded outside the big plates and inside the collar.
2. Each mass named (ref_01): a steel disc, a lip round the rim on its front, curved edges, the 50.5 mm bore; the 5 kg
   painted white, the 2.5 black, the 1.25 / 0.5 / 0.25 chromed; ELEIKO over and under the bore and the weight either
   side on the front, the calibration plugs on the back.
3. Adjustments. None.
4. Load path. The sleeve in the bore, the plate's face against the next plate and the collar.
5. Fit range. Picked up between finger and thumb; nothing to fit.
6. Size. 228 mm the largest; the five stacked flat, largest at the bottom, as Eleiko photographs them.
Axes: metres, floor z = 0; the stack's axis vertical at the origin, the fronts up.
"""
import math

R_BORE = 0.02525
# (look, ink, label, diameter, thickness), the stack from the floor up
PLATES = (("white", "ink_dark", "5", 0.228, 0.020), ("black", "ink", "2,5", 0.190, 0.015),
          ("chrome", "ink_dark", "1,25", 0.160, 0.012), ("chrome", "ink_dark", "0,5", 0.134, 0.008),
          ("chrome", "ink_dark", "0,25", 0.112, 0.007))

LOOK = {
    "white": dict(color=(0.72, 0.72, 0.71), rough=0.35, coat=0.3),
    "black": dict(color=(0.012, 0.012, 0.013), rough=0.35, coat=0.3),
    "chrome": dict(color=(0.85, 0.85, 0.86), rough=0.08, metal=1.0),
    "steel": dict(color=(0.75, 0.75, 0.76), rough=0.2, metal=1.0),
    "hole": dict(color=(0.02, 0.02, 0.02), rough=0.6),
    "ink": dict(color=(0.9, 0.9, 0.9), rough=0.5, coat=0.0),
    "ink_dark": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 30, 1.0), "front": (0, 12, 1.0), "side": (90, 12, 1.0), "back_three_quarter": (145, 30, 1.0),
         "top": (0, 80, 1.0)}
DETAILS = {
    "detail_stack": ((0.28, -0.32, 0.30), (0.0, 0.0, 0.03), 35),        # IPF ref_02: the stack from above and aside
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    z = 0.0
    for look, ink, label, d, t in PLATES:
        r = d / 2
        zc = z + t / 2
        k.disc(look, (0, 0, zc), r, R_BORE, t, axis="z", seg=96, soft=min(0.003, t * 0.2))
        k.disc("hole", (0, 0, zc), R_BORE, R_BORE - 0.001, t, axis="z", seg=32, soft=0.0)
        zt = z + t
        k.disc(look, (0, 0, zt + 0.0006), r - 0.0015, r - 0.008, 0.0012, axis="z", seg=96, soft=0.0003)     # the lip
        s = r / 0.095
        k.text(ink, "ELEIKO", (0, 0.045 * s, zt + 0.0003), 0.02 * s, rx=0.0, rz=math.pi, depth=0.0005)
        k.text(ink, "ELEIKO", (0, -0.045 * s, zt + 0.0003), 0.02 * s, rx=0.0, depth=0.0005)
        k.text(ink, label, (-0.05 * s, 0, zt + 0.0003), 0.016 * s, rx=0.0, rz=math.pi, depth=0.0005)
        k.text(ink, label, (0.05 * s, 0, zt + 0.0003), 0.016 * s, rx=0.0, depth=0.0005)
        z = zt

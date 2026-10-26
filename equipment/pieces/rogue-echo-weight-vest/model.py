"""Rogue Echo Weight Vest, black, M (refs/: ref_01 worn; ref_02 / ref_03 standing as on a torso: a front and a back plate
carrier joined over the shoulders by padded straps and round the waist by a cummerbund, a hook-and-loop panel on the
front with ROGUE in reflective grey, webbing rows below it; ref_04 / ref_05 the logo close). The linked page: plate
pockets 10.25 x 12.5 in front and back, 20 lb a pocket (40 lb), a 3 in hook-and-loop cummerbund with elastic, 1.5 in
padded shoulder straps, 500D / 1000D Cordura, a reflective ROGUE on the front, a patch panel on the back; plates
(about 11.25 x 9.25 in) sold separately: shown loaded. Fetched 2026-10-25. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Weighted runs, carries, calisthenics: worn snug, the plates high on the chest and back.
2. Each mass named (ref_02): two plate carriers (Cordura, a plate inside each), the front with its hook-and-loop panel
   and ROGUE and two webbing rows; the shoulder straps, padded, over from front to back; the cummerbund round the waist,
   its hook-and-loop closure at the front.
3. Adjustments. The shoulder straps' length; the cummerbund's girth; the plates (to 40 lb).
4. Load path. The plates, the carriers, the straps on the shoulders, the cummerbund round the ribs.
5. Fit range. S / M / L by chest: the M fits the 1.78 m user, S and L the others; the straps set the carriers high on
   every torso. No figure.
6. Size. Standing, about 0.36 x 0.32 x 0.45 m.
Axes: metres, floor z = 0; the front toward -y.
"""
import math

IN = 0.0254
PW, PH, PT = 10.25 * IN, 12.5 * IN, 0.035
YF, YB = -0.13, 0.13                  # the carriers' middles
Z0 = 0.03                             # the carriers' bottoms (on the cummerbund)

LOOK = {
    "cordura": dict(color=(0.012, 0.012, 0.013), rough=0.85, coat=0.0, spec=0.2, bump=(2500, 0.15)),
    "hook": dict(color=(0.018, 0.018, 0.02), rough=0.95, coat=0.0, bump=(5000, 0.3)),
    "reflect": dict(color=(0.45, 0.45, 0.46), rough=0.4, coat=0.0, spec=0.6),
    "web": dict(color=(0.008, 0.008, 0.009), rough=0.9, coat=0.0, bump=(3000, 0.1)),
}
VIEWS = {"three_quarter": (-30, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_front": ((-0.10, -0.75, 0.40), (0.0, -0.15, 0.25), 30),     # the panel, ROGUE, the webbing rows
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    zc = Z0 + PH / 2
    for y in (YF, YB):
        k.box("cordura", (0, y, zc), (PW, PT, PH), soft=0.012)                                     # a carrier
    yf = YF - PT / 2
    k.box("hook", (0, yf - 0.001, zc + 0.06), (PW - 0.04, 0.002, 0.11), soft=0.002)                 # the front panel
    k.text("reflect", "ROGUE", (0, yf - 0.0022, zc + 0.045), 0.056, depth=0.0006)
    for dz in (-0.03, -0.07, -0.11):                    # the webbing rows
        k.box("web", (0, yf - 0.0015, zc + dz), (PW - 0.03, 0.003, 0.022), soft=0.001)
    k.box("hook", (0, YB + PT / 2 + 0.001, zc + 0.04), (PW - 0.06, 0.002, 0.10), soft=0.002)        # the back panel
    for sx in (1, -1):                                  # the shoulder straps, padded, over the top
        x = sx * 0.075
        pts = [(x, YF, zc + PH / 2 - 0.03), (x, YF + 0.02, zc + PH / 2 + 0.07), (x, 0.0, zc + PH / 2 + 0.11),
               (x, YB - 0.02, zc + PH / 2 + 0.07), (x, YB, zc + PH / 2 - 0.03)]
        k.sweep("cordura", pts, k.rect(1.5 * IN + 0.01, 0.018, 0.006), bend=0.05, up=(0, 1, 0), soft=0.0)
    ring = [(0.20 * math.sin(t), 0.17 * -math.cos(t), 0.04) for t in [2 * math.pi * i / 48 for i in range(49)]]
    k.sweep("cordura", ring, k.rect(0.012, 3 * IN, 0.004), up=(0, 0, 1), soft=0.0)                  # the cummerbund
    k.box("hook", (0, -0.17 - 0.007, 0.04), (0.14, 0.003, 3 * IN - 0.01), soft=0.002)              # its closure

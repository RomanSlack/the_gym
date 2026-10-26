"""Manduka Meditation Cushion, sand (refs/: ref_01 / ref_02 the cushion: round, natural canvas, a soft rounded rim,
a carry handle on one side, the manduka label tab; ref_03 its zip open). The linked page (heima.com.hk) was not
fetched: the size (about 16 in across and 5 in high) is an estimate. Built to the two gates and README point 9
(kit.lathe).

DESIGN SPEC (gate 1)
1. Use. Seated meditation and breathwork: sat on, the hips raised above the knees.
2. Each mass named (ref_01): the cushion, a canvas cover over a buckwheat fill, round with a full rim; the handle; the
   label tab; the zip under the rim.
3. Adjustments. The fill (through the zip).
4. Load path. The seat on the fill, the floor.
5. Fit range. 16 in across, 5 in: the hips over the knees cross-legged for every user (1.55-1.95 m). No figure.
6. Size. 0.41 m across, 0.13 m high.
Axes: metres, floor z = 0; the handle toward +x.
"""
import math

IN = 0.0254
R, H = 8 * IN, 5 * IN

LOOK = {
    "canvas": dict(color=(0.55, 0.50, 0.42), rough=0.9, coat=0.0, bump=(2500, 0.1)),
    "seam": dict(color=(0.48, 0.43, 0.36), rough=0.9, coat=0.0),
    "label": dict(color=(0.30, 0.24, 0.17), rough=0.8, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 25, 1.0), "front": (0, 10, 1.0), "side": (90, 10, 1.0), "back_three_quarter": (150, 25, 1.0)}
DETAILS = {
    "detail_label": ((0.0, -0.55, 0.20), (0.0, 0.0, 0.06), 30),         # the label tab
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    prof = [(R - 0.03, 0.0)] + [(R - 0.03 + 0.03 * math.sin(a), H / 2 - H / 2 * math.cos(a)) for a in
                                 [math.pi * i / 16 for i in range(1, 16)]] + [(R - 0.03, H), (0.0, H - 0.004)]
    k.lathe("canvas", (0, 0, 0), prof, seg=64)                                                    # the cushion
    loop = [(R - 0.02, -0.03, H * 0.5), (R + 0.02, -0.03, H * 0.5), (R + 0.02, 0.03, H * 0.5), (R - 0.02, 0.03, H * 0.5)]
    k.sweep("seam", loop, k.rect(0.004, 0.02, 0.001), bend=0.012, up=(0, 0, 1), soft=0.0)            # the handle
    k.box("label", (0, -R - 0.0004, H * 0.5), (0.025, 0.003, 0.07), soft=0.001)                      # the label tab
    k.text("canvas", "manduka", (0, -R - 0.0019, H * 0.5), 0.008, spin=math.pi / 2, depth=0.0004)

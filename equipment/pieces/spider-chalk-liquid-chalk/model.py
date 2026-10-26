"""Spider Chalk liquid chalk (refs/: ref_01-03 the 4 oz bottle: glossy black, a flip cap, SPIDER CHALK in yellow
spray lettering, the label text in white, yellow and green; ref_04 / ref_05 the 2 oz shake bottle with its white
chalk). The linked page was not fetched: the bottles' sizes (4 oz about 135 mm tall and 50 mm across, the 2 oz about
100 x 42 mm) are estimates off the refs and the hand in ref_05. Built to the two gates and README point 9 (kit.lathe).

DESIGN SPEC (gate 1)
1. Use. A squirt into the palm, rubbed in, left to dry: a chalk layer that lasts and doesn't dust the gym.
2. Each mass named (ref_01 / ref_04): the bottle, black PET, round with a shoulder; the flip cap; the lettering.
3. Adjustments. None.
4. Load path. None.
5. Fit range. Hand-held by every user. No figure.
6. Size. The two bottles standing.
Axes: metres, floor z = 0; the lettering toward -y.
"""
import math

LOOK = {
    "pet": dict(color=(0.008, 0.008, 0.009), rough=0.15, coat=0.6, spec=0.6),
    "cap": dict(color=(0.010, 0.010, 0.011), rough=0.4, coat=0.1),
    "yellow": dict(color=(0.70, 0.62, 0.02), rough=0.5, coat=0.0),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 15, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 15, 1.0)}
DETAILS = {
    "detail_label": ((0.0, -0.35, 0.10), (-0.03, 0.0, 0.07), 30),       # the 4 oz's lettering
}


def bottle(k, x, R, H, neck, cap_h):
    prof = [(R - 0.004, 0.0), (R, 0.004), (R, H * 0.76), (R * 0.92, H * 0.83), (R * 0.65, H * 0.89), (neck, H * 0.93),
            (neck, H), (0.0, H)]                       # a Boston round
    k.lathe("pet", (x, 0, 0), prof, seg=48)
    k.cyl("cap", (x, 0, H + cap_h / 2 - 0.002), neck + 0.004, cap_h, seg=40, soft=0.002)                # the flip cap
    k.box("cap", (x, -neck - 0.002, H + cap_h - 0.004), (0.012, 0.004, 0.006), soft=0.001)               # its lip


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for x, R, H, neck, cap, size in ((-0.035, 0.029, 0.135, 0.012, 0.024, 0.019), (0.05, 0.022, 0.10, 0.011, 0.020, 0.013)):
        bottle(k, x, R, H, neck, cap)
        for word, a in (("SPIDER", -0.22), ("CHALK", 0.22)):   # the lettering running up the bottle, two columns
            k.text("yellow", word, (x + (R + 0.0002) * math.sin(a), -(R + 0.0002) * math.cos(a), H * 0.42), size, rz=a,
                   spin=math.pi / 2, depth=0.0016)

"""Hammer Strength Competition Kettlebells, 8-32 kg in 4 kg steps (refs/: ref_01 the 32 kg: a black steel body the same
size at every weight, black cast necks rising from it into a bare steel handle with a flat top and rounded corners, a
red band where they meet, HAMMER / 32 KG / STRENGTH embossed tone-on-tone; ref_02-ref_04 in use; ref_05 a row on a
rack: the bands 12 light blue, 16 yellow, 20 silver-grey, 24 green, 28 orange, 32 red; the rest in use). The shop
refused further requests (HTTP 429): the sizes are the competition standard (the body 210 mm across, 280 mm to the
handle's top, a 35 mm handle; estimates for this make); 8 kg pink by the common code. Built to the two gates and
README point 9 on the shared builder (equipment/blender/kettlebell.py).

DESIGN SPEC (gate 1)
1. Use. Kettlebell sport and training: every weight the same size, so the rack position and the grip never change.
2. Each mass named (ref_01): the body, a black steel ball flattened at the base (hollow, filled to weight, not
   drawn); the necks, black, cast with the body, rising straight; the handle, bare steel, its flat top with rounded
   corners; the colour band where neck meets handle; the embossed HAMMER / weight KG / STRENGTH.
3. Adjustments. None (a weight per bell).
4. Load path. The hand on the handle, the necks, the body.
5. Fit range. One size for all: the window (about 0.14 m wide, 0.10 m high) takes one hand for every user (1.55 / 1.78
   / 1.95 m); the body rests on the forearm in the rack.
6. Size. Seven bells in a row, each 210 mm across, 280 mm tall.
Axes: metres, floor z = 0; the row along x, the faces toward -y.
"""
import kettlebell as kb

BELLS = ((8, "pink"), (12, "lblue"), (16, "yellow"), (20, "grey"), (24, "green"), (28, "orange"), (32, "red"))
R = 0.105
LOOK = {
    "body": dict(color=(0.013, 0.013, 0.014), rough=0.72, metal=0.2, coat=0.0, bump=(1800, 0.15)),   # matte textured
    "ink": dict(color=(0.010, 0.010, 0.011), rough=0.3, metal=0.4, coat=0.4),                       # the embossing
    "steel": dict(color=(0.6, 0.6, 0.61), rough=0.3, metal=1.0, aniso=0.4),
    "pink": dict(color=(0.7, 0.12, 0.25), rough=0.5), "lblue": dict(color=(0.05, 0.35, 0.65), rough=0.5),
    "yellow": dict(color=(0.75, 0.55, 0.03), rough=0.5), "grey": dict(color=(0.55, 0.55, 0.56), rough=0.5),
    "green": dict(color=(0.25, 0.55, 0.05), rough=0.5), "orange": dict(color=(0.8, 0.25, 0.02), rough=0.5),
    "red": dict(color=(0.6, 0.02, 0.03), rough=0.5),
}
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_bell": ((0.62, -0.70, 0.26), (0.66, 0.0, 0.15), 30),        # ref_01: the 32 kg
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = -0.75
    for kg, col in BELLS:
        x += R
        kb.bell(k, (x, 0.0, 0.0), R, 0.0175, 0.065, 0.075, "body", "steel", col,
                [("HAMMER", 0.030, 0.30), (str(kg), 0.058, -0.02), ("KG", 0.012, -0.10), ("STRENGTH", 0.026, -0.42)],
                flat=0.82, arch=0.03, splay=1.12, neck="body")
        x += R + 0.05

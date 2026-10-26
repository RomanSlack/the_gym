"""Life Fitness Cast Iron Kettlebells, 4-32 kg in 4 kg steps (refs/: ref_01 the 24 kg: black, a green band round each
horn, 24KG / 53LB cast in its face; ref_02 the 4 kg (white); ref_03 the 8 kg (pink); ref_04 the 16 kg (yellow); ref_05
four together). The shop refused further requests (HTTP 429): the sizes are ours (estimates): cast iron bells growing
with the weight (the body 230 mm across at 24 kg, scaling with the cube root), the handle 33-38 mm thick; the bands in
the common kettlebell code (4 white, 8 pink, 12 blue, 16 yellow, 20 purple, 24 green, 28 orange, 32 red; ref_01-04
agree). Built to the two gates and README point 9 on the shared builder (equipment/blender/kettlebell.py).

DESIGN SPEC (gate 1)
1. Use. Swings, cleans, presses, goblet squats: the hand(s) in the handle's window, the body hanging under or resting
   on the forearm.
2. Each mass named (ref_01): the body, a cast iron ball flattened at the base; the handle a round loop cast with it,
   its horns splaying out into the shoulders; a colour band round each horn (the weight's code); the weight in kg and lb cast
   on a flat round face. Black powder coat.
3. Adjustments. None (a weight per bell).
4. Load path. The hand on the handle, the horns, the body.
5. Fit range. The window (the horns 0.10-0.15 m apart, 0.08-0.10 m high) takes one hand or both for every user
   (1.55 / 1.78 / 1.95 m); the base flat to stand on.
6. Size. Eight bells in a row on the floor.
Axes: metres, floor z = 0; the row along x, the faces toward -y.
"""
import kettlebell as kb

BELLS = ((4, "white"), (8, "pink"), (12, "blue"), (16, "yellow"), (20, "purple"), (24, "green"), (28, "orange"),
         (32, "red"))
LOOK = {
    "iron": dict(color=(0.016, 0.016, 0.017), rough=0.75, metal=0.1, coat=0.0, bump=(1600, 0.2)),    # textured coat
    "ink": dict(color=(0.03, 0.03, 0.032), rough=0.35, metal=0.3, coat=0.2),                         # the cast lettering
    "white": dict(color=(0.75, 0.75, 0.74), rough=0.5), "pink": dict(color=(0.7, 0.12, 0.25), rough=0.5),
    "blue": dict(color=(0.03, 0.1, 0.5), rough=0.5), "yellow": dict(color=(0.75, 0.55, 0.03), rough=0.5),
    "purple": dict(color=(0.25, 0.05, 0.4), rough=0.5), "green": dict(color=(0.04, 0.4, 0.06), rough=0.5),
    "orange": dict(color=(0.8, 0.25, 0.02), rough=0.5), "red": dict(color=(0.55, 0.02, 0.02), rough=0.5),
}
VIEWS = {"three_quarter": (-30, 18, 1.0), "front": (0, 8, 1.0), "side": (90, 8, 1.0), "back_three_quarter": (150, 20, 1.0)}
DETAILS = {
    "detail_bell": ((0.30, -0.70, 0.30), (0.28, 0.0, 0.16), 35),        # ref_01: the 24 kg's face and band
}


def size(kg):
    f = (kg / 24) ** (1 / 3)
    return 0.115 * f, 0.017 + 0.004 * f, 0.075 * f, 0.075 * f        # R, handle r, the top's half span, rise (ref_01)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    x = -0.85
    for kg, col in BELLS:
        R, hr, hw, hh = size(kg)
        x += R
        kb.bell(k, (x, 0.0, 0.0), R, hr, hw, hh, "iron", "iron", col,
                [(f"{kg}KG", R * 0.24, 0.12), (f"{round(kg * 2.2046)}LB", R * 0.24, -0.20)],
                arch=hw * 0.9, face=R * 0.45)
        x += R + 0.06

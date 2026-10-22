"""Hammer Strength Olympic Weightlifting Bar, the 20 kg men's power bar in stainless steel (28 mm, bushings), on the floor.

Built by eye from Life Fitness's photos (refs/: ref_05 the stainless bar whole, ref_07-ref_13 in use), held to the
Olympic men's bar: 2200 mm, 28 mm shaft, 50 mm sleeves, 1310 mm between the collars, no centre knurl.
Axes: metres, floor z = 0, the bar along x, centred on x = 0 (shared builder: equipment/blender/barbell.py).
Look: a satin stainless shaft, its knurl with the hand marks, bright chrome sleeves, a slim rounded flange collar, the
black end cap printed OLYMPIC / HAMMER STRENGTH / 20KG / BSH 28mm in white.
"""
import barbell

S = dict(
    L=2.200, G=1.310, shaft=0.028, sleeve=0.050,
    collar=[(0.0, 0.030), (0.003, 0.0335), (0.013, 0.0335), (0.016, 0.029), (0.020, 0.0275)],
    knurl=[(0.205, 0.635)], centre=0.0, marks=[0.4075, 0.4575],
    badge=dict(text=["OLYMPIC", "HAMMER", "STRENGTH", "20KG", "BSH 28mm"], size=0.0032, r=0.0205, big=1),
)
STAINLESS = dict(color=(0.66, 0.66, 0.67), rough=0.2, metal=1.0, coat=0.0, aniso=0.5)
CHROME = dict(color=(0.74, 0.74, 0.76), rough=0.06, metal=1.0, coat=0.0, aniso=0.3)
LOOK = {
    "shaft": STAINLESS,
    "knurl": barbell.knurl_look(S, dict(color=(0.24, 0.24, 0.25), rough=0.5, metal=0.7, coat=0.0), strength=0.8),
    "sleeve": CHROME,
    "collar": dict(CHROME, color=(0.7, 0.7, 0.72), rough=0.1, aniso=0.6),
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
    "badge": dict(color=(0.012, 0.012, 0.013), rough=0.35, coat=0.3),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_collar": ((0.47, -0.17, 0.13), (0.63, 0.0, 0.034), 50),     # the collar, the knurl and marks into it
    "detail_end": ((1.24, -0.12, 0.08), (1.10, 0.0, 0.034), 50),         # the end cap
}


def build(k):
    barbell.build(k, S)

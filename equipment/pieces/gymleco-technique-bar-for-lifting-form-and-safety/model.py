"""Gymleco Technique Bar 817T, 10 kg / 170 cm, lying on the floor.

Built by eye from Gymleco's renders (refs/: ref_01 the sleeve end, ref_02 the whole bar with its dimensions, ref_03 /
ref_04 the collar), held to Gymleco's drawing: 1700 mm overall, 1316 mm between the collars, 192 mm from each collar's
inner face to the end, 25 mm shaft, 50 mm sleeves.
Axes: metres, floor z = 0, the bar along x, centred on x = 0 (shared builder: equipment/blender/barbell.py).
Look: brushed stainless, a smooth centre between the knurls with two hand marks in each, a broad thin flange collar
on a short hub (a brass bushing showing at its face), the black end cap: TECHNIQUE BAR, 10kg / 170cm, Gymleco, Art#817T.
"""
import barbell

S = dict(
    L=1.700, G=1.316, shaft=0.025, sleeve=0.050,
    collar=[(0.0, 0.0175), (0.012, 0.0175), (0.012, 0.042), (0.013, 0.044), (0.023, 0.044), (0.024, 0.042), (0.024, 0.0275),
            (0.030, 0.0265)],
    knurl=[(0.157, 0.650)], centre=0.0, marks=[0.362, 0.4525],
    badge=dict(text=["TECHNIQUE BAR", "10kg / 170cm", "Gymleco", "Art#817T"], size=0.0028, r=0.0205, big=2),
    ring=dict(text="", size=0.004, r_in=0.0128, r_out=0.0172),
)
BRUSHED = dict(color=(0.62, 0.62, 0.63), rough=0.22, metal=1.0, coat=0.0, aniso=0.6)
LOOK = {
    "shaft": dict(BRUSHED, rough=0.16),
    "knurl": barbell.knurl_look(S, dict(color=(0.34, 0.34, 0.35), rough=0.45, metal=0.8, coat=0.0), strength=0.8),
    "sleeve": BRUSHED,
    "collar": dict(BRUSHED, rough=0.2, aniso=0.8),
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
    "ring": dict(color=(0.72, 0.52, 0.22), rough=0.3, metal=1.0, coat=0.0),        # the brass bushing
    "ink": dict(color=(0.1, 0.1, 0.1), rough=0.5, coat=0.0),
    "badge": dict(color=(0.03, 0.03, 0.032), rough=0.35, coat=0.3),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_collar": ((0.50, -0.20, 0.14), (0.66, 0.0, 0.044), 50),     # the flange collar on its hub (ref_03)
    "detail_end": ((0.98, -0.14, 0.10), (0.85, 0.0, 0.044), 50),         # the end cap (ref_01)
}


def build(k):
    barbell.build(k, S)

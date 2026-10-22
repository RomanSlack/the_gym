"""Eleiko IWF Weightlifting Competition Bar, 20 kg men's (needle bearings), lying on the floor.

Built by eye from Eleiko's photo (refs/: ref_01, the collar and knurl up close), held to the IWF men's bar: 2200 mm,
28 mm shaft, 50 mm sleeves, 1310 mm between the collars, a 120 mm centre knurl, the hand marks 910 mm apart.
Axes: metres, floor z = 0, the bar along x, centred on x = 0 (shared builder: equipment/blender/barbell.py).
Look: bright chrome shaft and sleeves, the knurl a matte grey, a deep collar turned with chamfered rings, the gold
ring on its inner face lettered ELEIKO IWF COMPETITION 20KG round it.
"""
import barbell

S = dict(
    L=2.200, G=1.310, shaft=0.028, sleeve=0.050,
    collar=[(0.0, 0.031), (0.003, 0.0355), (0.021, 0.0355), (0.0235, 0.0325), (0.030, 0.0325)],
    knurl=[(0.210, 0.640)], centre=0.120, marks=[0.4575],
    badge=dict(text=["ELEIKO", "20 KG"], size=0.006, r=0.019),
    ring=dict(text="IWF COMPETITION  20KG  ELEIKO  ", size=0.0048, r_in=0.0175, r_out=0.0285, full=True),
)
CHROME = dict(color=(0.86, 0.86, 0.87), rough=0.07, metal=1.0, coat=0.0, aniso=0.3)
LOOK = {
    "shaft": CHROME,
    "knurl": barbell.knurl_look(S, dict(color=(0.42, 0.42, 0.43), rough=0.4, metal=1.0, coat=0.0), strength=0.9),
    "sleeve": CHROME,
    "collar": dict(CHROME, color=(0.78, 0.78, 0.8), rough=0.12, aniso=0.6),   # turned, the lines catch the light
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
    "ring": dict(color=(0.72, 0.56, 0.22), rough=0.35, metal=0.9, coat=0.0),
    "badge": dict(color=(0.08, 0.08, 0.085), rough=0.4, coat=0.0),
    "ink": dict(color=(0.22, 0.23, 0.25), rough=0.45, metal=0.2, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_collar": ((0.47, -0.17, 0.13), (0.63, 0.0, 0.034), 50),     # the collar's gold ring, the knurl into it
    "detail_centre": ((0.0, -0.32, 0.16), (0.0, 0.0, 0.035), 50),        # the centre knurl
    "detail_end": ((1.24, -0.12, 0.08), (1.10, 0.0, 0.034), 50),         # the sleeve's end cap
}


def build(k):
    barbell.build(k, S)

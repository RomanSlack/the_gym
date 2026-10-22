"""Strencor Coach's Choice Competition Weightlifting Bar, 15 kg women's (needle bearings), lying on the floor.

Built by eye from Strencor's photos (refs/: ref_02 the whole bar and its cap badge, ref_03 the collar, ref_04 the
knurl and a hand mark), held to the women's bar: 2010 mm, 25 mm shaft, 50 mm sleeves, 1310 mm between the collars,
no centre knurl on the 15 kg (Strencor's page).
Axes: metres, floor z = 0, the bar along x, centred on x = 0 (shared builder: equipment/blender/barbell.py).
Look: polished chrome all over, a plain deep collar, the yellow Coach's Choice cap: 15 KG, BY STRENCOR.
"""
import barbell

S = dict(
    L=2.010, G=1.310, shaft=0.025, sleeve=0.050,
    collar=[(0.0, 0.032), (0.002, 0.034), (0.028, 0.034), (0.030, 0.032)],
    knurl=[(0.215, 0.640)], centre=0.0, marks=[0.4575],
    badge=dict(text=["COACH'S CHOICE", "15 KG", "BY STRENCOR"], size=0.0028, r=0.0205, big=1),
)
CHROME = dict(color=(0.74, 0.74, 0.76), rough=0.06, metal=1.0, coat=0.0, aniso=0.3)
LOOK = {
    "shaft": CHROME,
    "knurl": barbell.knurl_look(S, dict(color=(0.30, 0.30, 0.31), rough=0.4, metal=0.85, coat=0.0), strength=0.9),
    "sleeve": CHROME,
    "collar": dict(CHROME, color=(0.66, 0.66, 0.68), rough=0.14, aniso=0.6),
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
    "badge": dict(color=(0.92, 0.72, 0.01), rough=0.4, coat=0.2),
    "print": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_collar": ((0.47, -0.17, 0.13), (0.63, 0.0, 0.034), 50),     # the collar (ref_03)
    "detail_end": ((1.14, -0.12, 0.08), (1.00, 0.0, 0.034), 50),         # the yellow cap
}


def build(k):
    barbell.build(k, S)

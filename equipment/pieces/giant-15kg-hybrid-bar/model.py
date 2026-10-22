"""GIANT 15kg Hybrid Bar 2.0, the women's bar, lying on the floor.

Built by eye from GIANT's photos (refs/: ref_01 the sleeve end and cap, ref_02 the sleeve and collar from above, ref_03
the dual hand marks close, ref_04 the whole bar on the floor), held to the women's bar: 2010 mm, 25 mm shaft, 50 mm
sleeves, 1310 mm between the collars, no centre knurl, hybrid (both the IWF and the IPF hand marks).
Axes: metres, floor z = 0, the bar along x, centred on x = 0 (shared builder: equipment/blender/barbell.py).
Look: satin stainless all over (the sleeves a soft brushed sheen, not chrome), a deep collar with a stepped lip, the
black end cap with the G mark and HYBRID 2.0.
"""
import barbell

S = dict(
    L=2.010, G=1.310, shaft=0.025, sleeve=0.050,
    collar=[(0.0, 0.0335), (0.002, 0.0355), (0.009, 0.0355), (0.009, 0.0345), (0.040, 0.0345), (0.043, 0.0325)],
    knurl=[(0.215, 0.640)], centre=0.0, marks=[0.4075, 0.4575],
    badge=dict(text=["G", "HYBRID 2.0", "15KG", "GIANT"], size=0.0034, r=0.0205, big=0),
)
SATIN = dict(color=(0.6, 0.6, 0.61), rough=0.18, metal=1.0, coat=0.0, aniso=0.6)
LOOK = {
    "shaft": dict(SATIN, rough=0.14),
    "knurl": barbell.knurl_look(S, dict(color=(0.30, 0.30, 0.31), rough=0.45, metal=0.8, coat=0.0), strength=0.9),
    "sleeve": SATIN,
    "collar": dict(SATIN, rough=0.22),
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5, coat=0.0),
    "badge": dict(color=(0.012, 0.012, 0.013), rough=0.35, coat=0.3),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 22, 1.35), "front": (0, 6, 1.3), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.35)}
DETAILS = {
    "detail_collar": ((0.47, -0.17, 0.13), (0.63, 0.0, 0.034), 50),     # the collar, the knurl into it
    "detail_marks": ((0.43, -0.22, 0.12), (0.43, 0.0, 0.034), 50),       # the two hand marks (ref_03)
    "detail_end": ((1.14, -0.12, 0.08), (1.00, 0.0, 0.034), 50),         # the end cap
}


def build(k):
    barbell.build(k, S)

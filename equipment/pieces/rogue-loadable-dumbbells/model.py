"""Rogue Loadable Dumbbells, the DB-15 and the DB-10, both with the stainless shaft (black zinc is the other option),
each lying on its collars
(refs/: ref_01 the four variants with Rogue's notes (28.5 mm, bushings, U.S.A.); ref_02-ref_04 loaded with change
plates and OSO collars; ref_05 a bright zinc sleeve and its flange). The linked page: DB-10 14.25 in overall, 3.625 in
to load each side, 10 lb with collars; DB-15 20.5 in, 6.75 in, 15 lb; a 28.5 mm knurled handle, bright zinc sleeves on
bronze bushings, Rogue end caps. Fetched 2026-10-24 / 25. Built to the two gates and README point 9 on the shared
barbell builder (equipment/blender/barbell.py).

DESIGN SPEC (gate 1)
1. Use. A short bar loaded with small plates (change plates, the 2.5-25 lb) for heavy or odd dumbbell work: loaded,
   collared, lifted by the knurled handle; the sleeves spin on bushings.
2. Each mass named (ref_01 / ref_05): the handle, 28.5 mm, knurled; the collar each end, a flange the plates stop
   against; the sleeve, bright zinc, 50 mm; the end cap, ROGUE. Stainless shafts.
3. Adjustments. The load (plates and collars, not drawn).
4. Load path. Plates on the sleeves, the bushings, the shaft, the hand.
5. Fit range. The handle (about 5.5 in between the flanges) takes any user's (1.55 / 1.78 / 1.95 m) palm.
6. Size. 0.52 m (DB-15), 0.36 m (DB-10).
Axes: metres, floor z = 0, each bar along x lying on its collars; the DB-15 at y = 0, the DB-10 behind it.
"""
import barbell

IN = 0.0254


def spec(L, load):
    G = L - 2 * (load + 0.024)
    return dict(
        L=L, G=G, shaft=0.0285, sleeve=0.050,
        collar=[(0.0, 0.020), (0.004, 0.020), (0.004, 0.036), (0.006, 0.038), (0.018, 0.038), (0.020, 0.036),
                (0.020, 0.0262), (0.024, 0.0258)],
        knurl=[(0.0, G / 2 - 0.012)], centre=0.0, marks=[],
        badge=dict(text=["ROGUE"], size=0.0045, r=0.019),
    )


S15 = spec(20.5 * IN, 6.75 * IN)
S10 = spec(14.25 * IN, 3.625 * IN)
S = S15                                 # the builder's knurl look reads the bar's axis height from it

BRIGHT = dict(color=(0.82, 0.83, 0.85), rough=0.12, metal=1.0, coat=0.0)                      # bright zinc
STAINLESS = dict(color=(0.62, 0.62, 0.63), rough=0.2, metal=1.0, aniso=0.5)
LOOK = {
    "shaft": STAINLESS,
    "knurl": barbell.knurl_look(S, dict(color=(0.28, 0.28, 0.29), rough=0.55, metal=0.8), strength=0.9),
    "sleeve": BRIGHT,
    "collar": BRIGHT,
    "gap": dict(color=(0.02, 0.02, 0.02), rough=0.5),
    "badge": dict(color=(0.03, 0.03, 0.032), rough=0.35, coat=0.3),
    "print": dict(color=(0.85, 0.85, 0.85), rough=0.4),
}
VIEWS = {"three_quarter": (-30, 25, 1.2), "front": (0, 8, 1.2), "side": (90, 8, 1.0), "back_three_quarter": (150, 25, 1.2)}
DETAILS = {
    "detail_sleeve": ((0.35, -0.25, 0.15), (0.20, 0.0, 0.038), 40),     # ref_05: a sleeve, its flange, the cap
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    barbell.build(k, S15)
    # the DB-10 behind it: built at the origin, then moved back
    before = {key: set(b.verts) for key, b in k.groups.items()}
    barbell.build(k, S10)
    for key, b in k.groups.items():
        for v in b.verts:
            if v not in before.get(key, set()):
                v.co.y += 0.16

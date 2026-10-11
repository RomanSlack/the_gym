"""Schematic layout v1 (2026-10-10): writes model.spaces, model.stairs, and the slab/wall
elements of the column-free frame. One-time authoring script kept for the record.
After this, model/building.json is the source of truth: edit it directly.

Grid: gym wing x A=-29.45 .. C=-6.45, y 1=12.1 .. 7=-34.1 (bays of 7.7 m);
east wing x D=12.0 .. F=30.5, y 8=33.3 .. 13=-9.5 (bays of 8.56 m).

python3 tools/layout_v1.py   (then python3 tools/structure.py)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

R = lambda x0, y0, x1, y1: [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}

# ---------------------------------------------------------------- cores (all levels they pass)
cores = {
    "W1": {"poly": R(-32.05, -18.7, -28.85, -9.7), "levels": ["F4", "F3", "F2", "F1"], "name": "Core W1 · stair + elevator"},
    "W2": {"poly": R(-32.05, -34.1, -28.85, -27.6), "levels": ["F4", "F3", "F2", "F1"], "name": "Core W2 · exit stair"},
    "E": {"poly": R(12.0, 7.62, 17.0, 16.18), "levels": ["E2", "E1"], "name": "Core E · stair + elevator (garage ↔ reception)"},
}
spaces = []
for cid, c in cores.items():
    for L in c["levels"]:
        spaces.append({"id": f"core-{cid}-{L}", "level": L, "kind": "core", "name": c["name"], "poly": c["poly"]})

S = lambda id_, level, kind, name, poly, note=None: spaces.append(
    {"id": id_, "level": level, "kind": kind, "name": name, "poly": poly, **({"note": note} if note else {})})

# cores W1/W2 now sit in the back wall (mostly outside), so the west strip is free on every floor
STRETCH = [[-29.45, -34.1], [-18.2, -34.1], [-18.2, -18.7], [-21.45, -18.7], [-21.45, -9.3], [-29.45, -9.3]]
SPIRAL_BAY = R(-21.45, -18.7, -14.45, -11.0)

LIFTS = {"men": R(-31.25, -4.1, -28.85, -1.7), "women": R(-31.25, 4.7, -28.85, 7.1)}  # 2.4 x 2.4, 0.6 m inside the wall
for g, poly in LIFTS.items():
    for L in ("F4", "F3", "F2", "F1"):
        spaces.append({"id": f"lift-{g}-{L}", "level": L, "kind": "core", "name": f"Express lift · {g}" if L in ("F1", "F4") else "Lift shaft",
                       "poly": poly, "note": f"{g}'s locker room (F1) <-> pool lobby (F4), no stops between"})

# ---------------------------------------------------------------- F1 (gym wing) ±0.00
# Locker block follows Gym V2's walls exactly (x -29.45..-13.6, y -9.3..12.1), split at y 1.5:
# per room = changing room (middle) + wet zone (outer strip), full width to the gallery (Roman: wider, extend east)
S("women-lockers", "F1", "wet", "Women's changing · lockers", R(-29.45, 1.5, -13.6, 7.65))
S("women-wet", "F1", "wet", "Women's wet zone · showers, WCs, grooming", R(-29.45, 7.65, -13.6, 12.1), "floor-to-ceiling WC stalls, private rainfall showers, grooming stations (sauna + steam moved to the F4 thermal suite)")
S("men-lockers", "F1", "wet", "Men's changing · lockers", R(-29.45, -4.2, -13.6, 1.5))
S("men-wet", "F1", "wet", "Men's wet zone · showers, WCs, grooming", R(-29.45, -9.3, -13.6, -4.2), "floor-to-ceiling WC stalls, urinals, private rainfall showers, grooming stations (sauna + steam moved to the F4 thermal suite)")
S("gallery", "F1", "circulation", "Gallery · from the lounge bridge", R(-13.6, -9.3, -6.45, 12.1), "the bridge lands here; both locker doors right off it")
S("sauna-lobby", "F1", "wet", "Sauna lobby (annex)", R(-35.45, -1.5, -29.45, 4.5),
  "add-on outside the west wall, shared by both locker rooms; robes, towel warmer, sandals; door to the sauna path")
S("stretching", "F1", "gym", "Stretching & mobility", STRETCH)
S("spiral-F1", "F1", "circulation", "Spiral stair", R(-21.45, -18.7, -14.45, -9.3))
S("calisthenics", "F1", "gym", "Calisthenics", R(-14.45, -18.7, -6.45, -9.3))
S("cardio-F1", "F1", "gym", "Cardio · river views", R(-17.7, -34.1, -6.45, -18.7))

# ---------------------------------------------------------------- F2 −4.91
S("free-weights", "F2", "gym", "Free weights · mirror wall", STRETCH)
S("olympic", "F2", "gym", "Olympic platforms", R(-29.45, -9.3, -18.2, 12.1))
S("cardio-F2", "F2", "gym", "Cardio · river views", R(-18.2, -11.0, -6.45, 12.1))
S("spiral-F2", "F2", "circulation", "Spiral stair", SPIRAL_BAY)
S("machines", "F2", "gym", "Machines", [[-17.7, -34.1], [-6.45, -34.1], [-6.45, -11.0], [-14.45, -11.0], [-14.45, -18.7], [-17.7, -18.7]])

# ---------------------------------------------------------------- F3 −9.77 (river rim)
S("sled-track", "F3", "gym", "Turf sprint / sled lane · 46 m", R(-24.45, -34.1, -21.45, 12.1))
S("strongman", "F3", "gym", "Strongman · yoke, sleds", R(-29.45, -34.1, -24.45, -11.0))
S("strongman-n", "F3", "gym", "Strongman · atlas stones", R(-29.45, -11.0, -24.45, 12.1))
S("spiral-F3", "F3", "circulation", "Spiral stair (arrival)", SPIRAL_BAY)
S("north-stair-F3", "F3", "circulation", "Stair to F4", R(-21.45, 7.1, -15.45, 12.1))
S("functional", "F3", "gym", "Functional / CrossFit rig",
  [[-21.45, -34.1], [-12.0, -34.1], [-12.0, 12.1], [-15.45, 12.1], [-15.45, 7.1], [-21.45, 7.1], [-21.45, -11.0], [-14.45, -11.0], [-14.45, -18.7], [-21.45, -18.7]])
S("river-edge", "F3", "feature", "River edge · waist-high river window + indoor stream", R(-12.0, -34.1, -6.45, 12.1),
  "river water at -8.77 against the glass (about waist height); indoor stream fed by a gated intake above the falls")

# ---------------------------------------------------------------- F4 −15.39 (pool, recovery)
S("north-stair-F4", "F4", "circulation", "Stair from F3", R(-21.45, 7.1, -15.45, 12.1))
S("thermal", "F4", "wet", "Thermal suite · Finnish sauna, steam, hot/cold plunge, infrared, cryo",
  [[-24.45, 4.4], [-6.45, 4.4], [-6.45, 12.1], [-15.45, 12.1], [-15.45, 7.1], [-21.45, 7.1], [-21.45, 12.1], [-24.45, 12.1]])
S("pool", "F4", "pool", "Lap pool 25 × 10 m · underwater river windows", R(-16.45, -28.1, -6.45, -3.1))
S("pool-deck-w", "F4", "wet", "Pool deck & lounge", R(-24.45, -18.7, -16.45, 4.4))
S("pool-deck-n", "F4", "wet", "Pool deck", R(-16.45, -3.1, -6.45, 4.4))
S("pool-deck-s", "F4", "wet", "Pool deck", R(-16.45, -34.1, -6.45, -28.1))
S("plant", "F4", "service", "Plant room · pool + building", R(-24.45, -34.1, -16.45, -18.7))
S("recovery", "F4", "gym", "Recovery lounge · compression, zero-gravity", R(-29.45, -34.1, -24.45, -11.0))
S("treatment", "F4", "wet", "Treatment rooms (2)", R(-29.45, 7.9, -24.45, 12.1))
S("treatment-s", "F4", "wet", "Treatment room", R(-29.45, -11.0, -24.45, -4.5))
S("pool-lobby", "F4", "circulation", "Pool lobby · express lifts from the locker rooms", R(-29.45, -4.5, -24.45, 7.9), "arrive from the locker rooms in robes, straight onto the pool deck")

# ---------------------------------------------------------------- lounge link (F1)
S("lounge", "F1", "lounge", "Lounge bridge", R(-6.45, -9.5, 12.0, 8.3), "sliding glass walls open fully onto the decks")
S("deck-n", "F1", "outdoor", "Deck · falls view", R(-6.45, 8.3, 12.0, 11.3))
S("deck-s", "F1", "outdoor", "Deck", R(-6.45, -12.5, 12.0, -9.5))

# ---------------------------------------------------------------- east wing E1 +0.12
S("cafe", "E1", "lounge", "Cafe · round island bar", R(12.0, -9.5, 21.25, 7.62))
S("reception", "E1", "circulation", "Reception", R(21.25, -0.94, 30.5, 7.62))
S("wcs", "E1", "wet", "WCs · water station", R(21.25, -9.5, 30.5, -0.94))
S("lobby", "E1", "circulation", "Entry lobby · from the arrival court", R(17.0, 7.62, 30.5, 16.18))
S("daycare-up", "E1", "daycare", "Daycare · upper floor", R(12.0, 16.18, 30.5, 33.3), "own door to the court; round stair to the lower floor")

# ---------------------------------------------------------------- east wing E2 −6.01
S("garage", "E2", "garage", "Garage · 3 cars on the glass, bike storage", R(12.0, -9.5, 30.5, 7.62), "tunnel entry on the east wall")
S("game-room", "E2", "lounge", "Game room", R(17.0, 7.62, 30.5, 16.18))
S("daycare-low", "E2", "daycare", "Daycare · lower floor → sunken garden", R(12.0, 16.18, 30.5, 33.3))

m["spaces"] = spaces

# ---------------------------------------------------------------- stairs
m["stairs"] = [
    {"id": "spiral_west", "kind": "spiral", "center": [-17.95, -14.85], "diameter": 7.0, "from": "F3", "to": "F1",
     "note": "open, sculptural; moved from Gym V2 (-19.5,-13.6) Ø7.9 to fit between beam lines 4 and 5"},
    {"id": "north_f3_f4", "kind": "straight", "rect": [-21.45, 7.1, -15.45, 12.1], "from": "F4", "to": "F3", "run": "north"},
    {"id": "daycare_round", "kind": "spiral", "center": [15.7, 24.2], "diameter": 5.1, "from": "E2", "to": "E1", "note": "Gym V2's round stair"},
]
m["fixtures"] = [
    {"id": "cafe_ring", "kind": "island_bar", "level": "E1", "center": [16.6, -0.94], "diameter": 7.0, "note": "moved from Gym V2 (20,0.2) to sit inside the cafe"},
]

# ---------------------------------------------------------------- slabs + walls (frame envelope)
els = [e for e in m.get("elements", []) if e["type"] not in ("slab", "wall")]
WEST, EAST, LINK = (-29.45, -34.1, -6.45, 12.1), (12.0, -9.5, 30.5, 33.3), (-6.45, -12.5, 12.0, 11.3)
holes = {  # openings through each slab
    "F4": [{"rect": R(-16.45, -28.1, -6.45, -3.1)}],  # pool basin
    "F1": [{"circle": [-17.95, -14.85, 3.5]}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "F2": [{"circle": [-17.95, -14.85, 3.5]}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "F3": [{"rect": R(-21.45, 7.1, -15.45, 12.1)}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "E1": [{"circle": [15.7, 24.2, 2.55]}, {"rect": cores["E"]["poly"]}],
}
for L, rect, thick in (("F4", WEST, 0.6), ("F3", WEST, 0.25), ("F2", WEST, 0.25), ("F1", WEST, 0.25),
                       ("E2", EAST, 0.6), ("E1", EAST, 0.25), ("F1", LINK, 0.3)):
    top = lv[L]
    els.append({"id": f"S-{L}-{'link' if rect is LINK else ('west' if rect is WEST else 'east')}", "type": "slab",
                "material": "concrete", "rect": list(rect), "z": [round(top - thick, 2), top],
                "holes": holes.get(L, []) if rect is not LINK else []})
els.append({"id": "S-F1-annex", "type": "slab", "material": "concrete", "rect": [-35.45, -1.5, -29.45, 4.5], "z": [-0.25, 0.0], "holes": []})
els.append({"id": "S-RF-annex", "type": "slab", "material": "clt", "rect": [-35.45, -1.5, -29.45, 4.5], "z": [3.0, 3.2], "holes": []})
for name, rect in (("west", WEST), ("east", EAST), ("link", (-6.45, -9.5, 12.0, 8.3))):
    els.append({"id": f"S-RF-{name}", "type": "slab", "material": "clt", "rect": list(rect), "z": [5.64, 5.84], "holes": []})


def wall(id_, a, b, t, z0, z1, kind, material):
    if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 0.05:  # zero-length (e.g. a glazing segment closed up by a flush edge)
        return
    els.append({"id": id_, "type": "wall", "kind": kind, "material": material, "from": a, "to": b,
                "size": [t, round(z1 - z0, 2)], "z": [round(z0, 2), round(z1, 2)]})


x0, y0, x1, y1 = WEST
zb, zt = lv["F4"] - 0.6, lv["F1"] - 0.25
wall("W-west-A", [x0, y0], [x0, y1], 0.5, zb, zt, "retaining", "concrete")
els[-1]["openings"] = [{"s": s_, "z": [lv[L], round(lv[L] + 2.3, 2)], "type": "door", "note": f"core {c_} door"}
                       for L in ("F4", "F3", "F2") for c_, s_ in (("W2", [2.6, 4.0]), ("W1", [19.0, 21.0]))] + [
                       {"s": [30.15, 32.25], "z": [lv["F4"], round(lv["F4"] + 2.3, 2)], "type": "door", "note": "men's express lift"},
                       {"s": [38.95, 41.05], "z": [lv["F4"], round(lv["F4"] + 2.3, 2)], "type": "door", "note": "women's express lift"}]
wall("W-west-N", [x0, y1], [x1, y1], 0.5, zb, zt, "retaining", "concrete")
wall("W-west-S", [x0, y0], [x1, y0], 0.5, zb, zt, "retaining", "concrete")
wall("W-west-C", [x1, y0], [x1, y1], 0.4, zb, zt, "river_wall", "concrete")  # windows at F2/F3, underwater at F4
# openings along the river wall: s = metres from its south end (y -34.1), z absolute
F2, F3, F4 = lv["F2"], lv["F3"], lv["F4"]
els[-1]["openings"] = (
    [{"s": [6.0 + 3.2 * k, 8.4 + 3.2 * k], "z": [round(F4 + 0.35, 2), round(F4 + 2.35, 2)], "type": "underwater",
      "note": "thick acrylic, looks into the river at the riverbed"} for k in range(8)]
    + [{"s": [2.0, 44.2], "z": [F3, round(F3 + 2.6, 2)], "type": "river",
        "note": "continuous river window: water surface (-8.77) about 1.0 m above the floor, waist height"}]
    + [{"s": [2.0, 44.2], "z": [round(F2 + 0.45, 2), round(F2 + 3.0, 2)], "type": "window", "note": "ravine view band"}]
)
for g, poly in LIFTS.items():  # shaft walls: stone-clad, rise just above the roof
    (sx0, sy0), _, (sx1, sy1), _ = poly
    for n_, (a_, b_) in {"W": ([sx0, sy0], [sx0, sy1]), "N": ([sx0, sy1], [-29.7, sy1]), "S": ([sx0, sy0], [-29.7, sy0])}.items():
        wall(f"LS-{g}-{n_}", a_, b_, 0.25, lv["F4"] - 0.6, 6.4, "shaft", "concrete")
for cid in ("W1", "W2"):
    (sx0, sy0), _, (sx1, sy1), _ = cores[cid]["poly"]
    for n_, (a_, b_) in {"W": ([sx0, sy0], [sx0, sy1]), "N": ([sx0, sy1], [-29.7, sy1]), "S": ([sx0, sy0], [-29.7, sy0])}.items():
        wall(f"CS-{cid}-{n_}", a_, b_, 0.3, lv["F4"] - 0.6, 6.4, "shaft", "concrete")
    els.append({"id": f"SKY-{cid}", "type": "slab", "material": "glass", "rect": [sx0, sy0, sx1, sy1], "z": [6.4, 6.5], "holes": [],
                "note": "glass skylight: daylight down the stairwell to F4"})
# W2 exit door straight outside at F1 (west face of the shaft)
[e for e in els if e["id"] == "CS-W2-W"][0]["openings"] = [{"s": [2.6, 4.0], "z": [0.0, 2.3], "type": "door", "note": "exit to outside"}]
wall("A-annex-W", [-35.45, -1.5], [-35.45, 4.5], 0.25, 0.0, 3.0, "solid", "timber")
wall("A-annex-N", [-35.45, 4.5], [-32.0, 4.5], 0.25, 0.0, 3.0, "solid", "timber")   # door gap 32.0..-29.45 north = path exit
wall("A-annex-S", [-35.45, -1.5], [-29.45, -1.5], 0.25, 0.0, 3.0, "solid", "timber")
for (a, b, n) in (([x0, y0], [x0, -1.5], "A1"), ([x0, 4.5], [x0, y1], "A2"), ([x0, y1], [x1, y1], "N"), ([x0, y0], [x1, y0], "S"), ([x1, y0], [x1, -9.5], "C1"), ([x1, 8.3], [x1, y1], "C2")):
    wall(f"G-F1-{n}", a, b, 0.15, lv["F1"], 4.34, "glazed", "glass")
x0, y0, x1, y1 = EAST
zb, zt = lv["E2"] - 0.6, lv["E1"] - 0.25
wall("W-east-S", [x0, y0], [x1, y0], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-E1", [x1, y0], [x1, -6.0], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-E2", [x1, 0.0], [x1, y1], 0.4, zb, zt, "retaining", "concrete")  # gap = garage tunnel
wall("G-E2-W", [x0, y0], [x0, 12.0], 0.15, lv["E2"], zt, "glazed", "glass")    # garage glass over the ravine
wall("W-east-W", [x0, 12.0], [x0, y1], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-N1", [x0, y1], [18.0, y1], 0.4, zb, zt, "retaining", "concrete")
wall("G-E2-N", [18.0, y1], [x1, y1], 0.15, lv["E2"], zt, "glazed", "glass")     # daycare onto the sunken garden
for (a, b, n) in (([x0, y0], [x0, -9.5], "W1"), ([x0, 8.3], [x0, y1], "W2"), ([x0, y1], [x1, y1], "N"), ([x1, y0], [x1, y1], "E"), ([x0, y0], [x1, y0], "S")):
    wall(f"G-E1-{n}", a, b, 0.15, lv["E1"], 4.34, "glazed", "glass")
for (a, b, n) in (([-6.45, -9.5], [12.0, -9.5], "S"), ([-6.45, 8.3], [12.0, 8.3], "N")):
    wall(f"G-link-{n}", a, b, 0.12, 0.0, 4.0, "glazed", "glass")  # sliding glass walls

m["elements"] = els
modelio.save(m)
print(len(spaces), "spaces,", len(m["stairs"]), "stairs,", sum(e["type"] == "slab" for e in els), "slabs,", sum(e["type"] == "wall" for e in els), "walls")

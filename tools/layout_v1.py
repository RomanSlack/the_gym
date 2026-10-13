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
    # three identical 3.2 x 9 m stone towers. West facade rhythm every 15.55 m: W2, W1, then the sauna annex
    # flanked by the two express lifts (centre y 1.5). W3 stands fully outside on the north face (no floor area taken).
    "W1": {"poly": R(-32.05, -18.55, -28.85, -9.55), "levels": ["F4", "F3", "F2", "F1"], "name": "Core W1 · stair + elevator"},
    "W2": {"poly": R(-32.05, -34.1, -28.85, -25.1), "levels": ["F4", "F3", "F2", "F1"], "name": "Core W2 · exit stair"},
    "W3": {"poly": R(-17.2, 12.35, -8.2, 15.55), "levels": ["F4", "F3", "F2", "F1"], "name": "Core W3 · exit stair (north)"},
    "E": {"poly": R(20.8, 6.8, 24.0, 16.2), "levels": ["E2", "E1"], "name": "Core E · stair + elevator (garage ↔ reception)"},
}
spaces = []
for cid, c in cores.items():
    for L in c["levels"]:
        spaces.append({"id": f"core-{cid}-{L}", "level": L, "kind": "core", "name": c["name"], "poly": c["poly"]})

S = lambda id_, level, kind, name, poly, note=None, open_=False: spaces.append(
    {"id": id_, "level": level, "kind": kind, "name": name, "poly": poly, **({"note": note} if note else {}), **({"open": True} if open_ else {})})

# cores W1/W2 now sit in the back wall (mostly outside), so the west strip is free on every floor
STRETCH = [[-29.45, -34.1], [-18.2, -34.1], [-18.2, -18.7], [-21.45, -18.7], [-21.45, -9.3], [-29.45, -9.3]]
SPIRAL_BAY = R(-21.45, -18.7, -14.45, -11.0)

LIFTS = {"men": R(-31.25, -4.1, -28.85, -1.7), "women": R(-31.25, 4.7, -28.85, 7.1)}  # 2.4 x 2.4, 0.6 m inside the wall
for g, poly in LIFTS.items():
    for L in ("F4", "F3", "F2", "F1"):
        spaces.append({"id": f"lift-{g}-{L}", "level": L, "kind": "core", "name": f"Express lift · {g}" if L in ("F1", "F4") else "Lift shaft",
                       "poly": poly, "note": f"{g}'s locker room (F1) <-> pool lobby (F4), no stops between"})

# ---------------------------------------------------------------- F1 (gym wing) ±0.00
# Locker block follows Gym V2's walls exactly (x -29.45..-11.6 (pushed 2 m east into the gallery for luxury space; gallery 5 m), y -9.3..12.1), split at y 1.5:
# per room = changing room (middle) + wet zone (outer strip), full width to the gallery (Roman: wider, extend east)
# Roman (2026-10-12): be thoughtful about how the locker rooms work from the bridge. The bridge axis (y -1.35) used to land on the
# men's doorway. Now 'Kilden' (the spring, tools/furnish.py) sits on the axis in the gallery wall, and the two entries flank it
# mirror-symmetric. The women's entry falls on the men's frontage, so a 2.8 x 1.9 m vestibule from the men's room carries it
# north into the women's room (private by its own turn); the men's room keeps the rest.
VEST = [[-14.4, -0.375], [-11.6, -0.375], [-11.6, 1.5], [-14.4, 1.5]]
S("women-lockers", "F1", "wet", "Women's changing · lockers", [[-29.45, 1.5], [-14.4, 1.5], [-14.4, -0.375], [-11.6, -0.375], [-11.6, 7.65], [-29.45, 7.65]],
  "entered from the gallery through its own vestibule, south of the women's room, beside Kilden")
# Roman (2026-10-12): toilets physically apart from the washing, never sharing a floor (the gym nightmare: wash floors mixing with
# toilet floors). Each wet zone splits: the wash zone (showers, Fossen, onsen wash places, grooming) entered only from the changing
# room, and a walled WC room at the east end with its own floor, drain, extract and handwash, entered from the arrival nook on the
# shoe side of the shoes-off line (so gym users in shoes never step into the barefoot zone; toilet slippers for the barefoot).
S("women-wet", "F1", "wet", "Women's wash zone · showers, Fossen, wash places, grooming", R(-29.45, 7.65, -19.4, 12.1), "barefoot, clean: no toilets on this floor")
S("women-wc", "F1", "wet", "Women's WC room", R(-19.4, 7.65, -11.6, 12.1), "own floor, drain + extract; handwash inside; door off the arrival nook (shoe side)")
S("men-lockers", "F1", "wet", "Men's changing · lockers", [[-29.45, -4.2], [-11.6, -4.2], [-11.6, -0.375], [-14.4, -0.375], [-14.4, 1.5], [-29.45, 1.5]],
  "entered from the gallery south of Kilden, an oak baffle inside")
S("men-wet", "F1", "wet", "Men's wash zone · showers, Fossen, wash places, grooming", R(-29.45, -9.3, -19.4, -4.2), "barefoot, clean: no toilets on this floor")
S("men-wc", "F1", "wet", "Men's WC room · urinals enclosed", R(-19.4, -9.3, -11.6, -4.2), "own floor, drain + extract; urinals in their own enclosed room; handwash inside; door off the arrival nook (shoe side)")
S("gallery", "F1", "circulation", "Gallery · from the lounge bridge", R(-11.6, -9.3, -6.45, 12.1), "the bridge lands here; both locker doors right off it")
S("sauna-lobby", "F1", "wet", "Sauna lobby (annex)", R(-35.45, -1.5, -29.45, 4.5),
  "add-on outside the west wall, shared by both locker rooms; robes, towel warmer, sandals; door to the sauna path")
S("stretching", "F1", "gym", "Stretching & mobility", STRETCH)
S("spiral-F1", "F1", "circulation", "Spiral stair", R(-21.45, -18.7, -14.45, -9.3))
S("calisthenics", "F1", "gym", "Calisthenics", R(-14.45, -18.7, -6.45, -9.3))
S("cardio-F1", "F1", "gym", "Cardio · river views", R(-18.2, -34.1, -6.45, -18.7))

# ---------------------------------------------------------------- F2 −4.91
S("free-weights", "F2", "gym", "Free weights · mirror wall", STRETCH)
S("olympic", "F2", "gym", "Olympic platforms", [[-29.45, -9.3], [-21.45, -9.3], [-21.45, -11.0], [-18.2, -11.0], [-18.2, 12.1], [-29.45, 12.1]])
S("cardio-F2", "F2", "gym", "Cardio · river views", R(-18.2, 0.55, -6.45, 12.1))
S("machines-2", "F2", "gym", "Machines · plate-loaded + cable", R(-18.2, -11.0, -6.45, 0.55), "Roman: half the cardio became more machines")
S("spiral-F2", "F2", "circulation", "Spiral stair", SPIRAL_BAY)
S("machines", "F2", "gym", "Machines", [[-18.2, -34.1], [-6.45, -34.1], [-6.45, -11.0], [-14.45, -11.0], [-14.45, -18.7], [-18.2, -18.7]])

# ---------------------------------------------------------------- F3 −9.77 (river rim)
# F3 = "the den" (Roman): dark, locked-in. Free weights along 3/4 of the west wall, floor-to-ceiling mirrors
S("free-weights-F3", "F3", "gym", "Free weights · mirror wall · the den", R(-29.45, -34.1, -21.45, 0.55),
  "34.65 m of floor-to-ceiling mirror on the west wall (mirror-clad flush doors); benches flat/incline/decline facing it; dumbbells 2.5-75 kg")
S("strongman", "F3", "gym", "Strongman · yoke, atlas stones", R(-29.45, 0.55, -21.45, 12.1))
S("spiral-F3", "F3", "circulation", "Spiral stair (arrival)", SPIRAL_BAY)
S("north-stair-F3", "F3", "circulation", "Stair to F4", R(-21.45, 7.1, -15.45, 12.1))
S("functional", "F3", "gym", "Functional / CrossFit rig",
  [[-21.45, -34.1], [-14.45, -34.1], [-14.45, 12.1], [-15.45, 12.1], [-15.45, 7.1], [-21.45, 7.1], [-21.45, -11.0], [-14.45, -11.0], [-14.45, -18.7], [-21.45, -18.7]])
S("sled-track", "F3", "gym", "Turf sprint / sled lane · 46 m", R(-14.45, -34.1, -12.0, 12.1))
S("river-edge", "F3", "feature", "River edge · waist-high river window + indoor stream", R(-12.0, -34.1, -6.45, 12.1),
  "river water at -8.77 against the glass (about waist height); indoor stream fed by a gated intake above the falls")

# ---------------------------------------------------------------- F4 −15.39 (pool, recovery)
S("north-stair-F4", "F4", "circulation", "Stair from F3", R(-21.45, 7.1, -15.45, 12.1))
S("thermal", "F4", "wet", "Thermal · sauna, steam, hot/cold plunge",
  [[-24.45, 4.4], [-6.45, 4.4], [-6.45, 12.1], [-15.45, 12.1], [-15.45, 7.1], [-21.45, 7.1], [-21.45, 12.1], [-24.45, 12.1]])
S("pool", "F4", "pool", "Lap pool 25 × 10 m · underwater river windows", R(-16.45, -28.1, -6.45, -3.1))
S("pool-deck-w", "F4", "wet", "Pool deck & lounge", R(-24.45, -18.7, -16.45, 4.4))
S("pool-deck-n", "F4", "wet", "Pool deck", R(-16.45, -3.1, -6.45, 4.4))
S("pool-deck-s", "F4", "wet", "Pool deck", R(-16.45, -34.1, -6.45, -28.1))
S("plant", "F4", "service", "Plant room · pool + building", R(-24.45, -34.1, -16.45, -18.7))
S("recovery", "F4", "gym", "Recovery lounge · compression, loungers", R(-29.45, -34.1, -24.45, -4.5), "no spa / massage (Roman)")
S("pool-lobby", "F4", "circulation", "Pool lobby · express lifts, towels + robes", R(-29.45, -4.5, -24.45, 12.1), "arrive from the locker rooms in robes, straight onto the pool deck; towel + robe station")

# ---------------------------------------------------------------- lounge link (F1)
S("lounge", "F1", "lounge", "Lounge bridge", R(-6.45, -9.5, 12.0, 6.8), "sliding glass walls open fully onto the decks")
S("deck-n", "F1", "outdoor", "Deck · falls view", R(-6.45, 6.8, 12.0, 11.3))
S("deck-s", "F1", "outdoor", "Deck", R(-6.45, -12.5, 12.0, -9.5))

# ---------------------------------------------------------------- east wing E1 +0.12
# Follows Gym V2: cafe island in the middle of the south half, a central block with the core and public WCs,
# reception desk backed onto it facing the entry (east), daycare north.
S("cafe", "E1", "lounge", "Cafe · round island bar", R(12.0, -9.5, 30.5, 6.8), "back counter along the south wall; opens west onto the lounge bridge")
# Public WCs as in Gym V2: split down the middle (Gym V2 wall x≈17.3), each with its own entrance off the cafe
S("wc-women", "E1", "wet", "Women's WC", R(12.0, 6.8, 16.4, 16.2),
  "own baffled entrance off the cafe; sinks along the entry wall, full-height stalls, one accessible stall")
S("wc-men", "E1", "wet", "Men's WC", R(16.4, 6.8, 20.8, 16.2),
  "own baffled entrance off the cafe; sinks along the entry wall, urinals + full-height stalls, one accessible stall")
S("reception", "E1", "circulation", "Reception · gym + daycare", R(24.0, 6.8, 30.5, 16.2),
  "shared desk backed onto the core, facing the east entrance; glass wall + secure door north into the daycare (sightline from the desk)")
# daycare (upper): Norwegian barnehage layout: entry wardrobe, children's WC + changing, staff, play
S("dc-wardrobe", "E1", "daycare", "Daycare main entrance · check-in + wardrobe", R(24.0, 16.2, 30.5, 21.2),
  "entrance and exit straight off reception, north of the desk (as in Gym V2); each child's cubby, boot racks, drying cabinets")
S("dc-wc", "E1", "wet", "Children's WC + changing", R(17.0, 16.2, 24.0, 21.2),
  "glass wall + open doorway: staff line of sight from play; low stall screens; child-height WCs and basins, changing table with hand shower, accessible WC; stacked over the lower one")
S("dc-staff", "E1", "service", "Staff room + staff toilet", R(12.0, 16.2, 17.0, 21.2))
# drop-in childcare while parents train (Roman: luxury, handles anything, everyone comfortable): zones by age
# Roman: open plan, no walls unless needed -> one open play space; baby/toddler is a gated zone inside it.
S("dc-kids", "E1", "daycare", "Daycare play · open, kids 3–12", R(12.0, 21.2, 21.25, 33.3), "crafts, reading, homework; round stair down to active play", open_=True)
S("daycare-up", "E1", "daycare", "Baby & toddler zone · 0–3", [[21.25, 21.2], [30.5, 21.2], [30.5, 29.3], [27.0, 29.3], [27.0, 33.3], [21.25, 33.3]],
  "open zone, low gate + soft furniture, no walls", open_=True)
S("dc-nursing", "E1", "daycare", "Nursing room", R(27.0, 29.3, 30.5, 33.3), "small, private: chair, bottle prep")

# ---------------------------------------------------------------- east wing E2 −6.01
S("garage", "E2", "garage", "Garage · cars on the glass", R(12.0, -3.5, 30.5, 6.8), "drive-through from the underground parking (east)")
S("bike-moto", "E2", "garage", "Bike + motorcycle parking", R(12.0, -9.5, 30.5, -3.5),
  "along the south wall: ~40 bikes on two-tier racks with e-bike charging, 6 motorcycle bays, bike wash + repair stand; walkway north to the core E lift/stairs up to reception")
S("game-room", "E2", "lounge", "Game room · table tennis on the ravine glass, pool", R(12.0, 6.8, 20.8, 16.18),
  "table tennis parallel to the river right on the glass (the 'floating over the river' shot), classic 9-ft pool table, lounge corner")
S("lift-lobby-e2", "E2", "circulation", "Lift lobby · from the garage", R(24.0, 6.8, 30.5, 16.18))
S("dc-rest", "E2", "daycare", "Rest / sleep room", R(12.0, 16.18, 17.0, 21.2))
S("dc-wc-low", "E2", "wet", "Children's WC + changing", R(17.0, 16.18, 24.0, 21.2), "stacked under the upper one")
S("dc-store", "E2", "service", "Storage · prams, outdoor gear", R(24.0, 16.18, 30.5, 21.2))
S("daycare-low", "E2", "daycare", "Active play · climbing, soft play → sunken garden", R(12.0, 21.2, 30.5, 33.3), "walk-out to the garden; noisy play kept downstairs", open_=True)

# ---------------------------------------------------------------- underground parking under the entry forecourt (E2)
S("parking", "E2", "garage", "Parking · ~30 cars, under the forecourt", R(30.5, -9.5, 60.0, 24.0),
  "drive-through to the east wing garage; ramp tunnel enters on the east wall; the forecourt landscape is its roof")

# ---------------------------------------------------------------- south rock annex (Roman: extra rooms dug into the rock, F2-F4)
SA = (-40.1, -34.1)  # y range: 6 m into the rock south of the gym wing
S("posing", "F2", "gym", "Posing room · stage lighting, mirrors", R(-28.85, SA[0], -22.6, SA[1]), "top-light + side-light rig, 3-way mirrors, warm/cool switchable")
for k, (a_, b_) in enumerate([(-22.6, -17.2), (-17.2, -11.8), (-11.8, -6.45)]):
    S(f"pod-{k + 1}", "F2", "gym", f"Private training pod {k + 1}", R(a_, SA[0], b_, SA[1]), "mirrored walls, adjustable lighting, integrated AV, rack + bench")
S("altitude", "F3", "gym", "Altitude training room · hypoxic", R(-28.85, SA[0], -14.45, SA[1]), "adjustable O2 (sealed room), bikes, rowers, treadmill")
S("breathwork", "F4", "gym", "Breathwork & mobility room", R(-28.85, SA[0], -17.5, SA[1]), "ambient lighting, soft floor, quiet")

# ---------------------------------------------------------------- gym floors F2-F4: WC annex dug into the rock behind the west wall
for L in ("F2", "F3", "F4"):
    S(f"wc-annex-{L}", L, "wet", "WCs · 3 single (1 accessible), water station", R(-33.45, -24.75, -29.45, -18.9), "annex in the rock outside the back wall between W2 and W1, stacked")

# rooms are cut cleanly around every core / shaft that pokes into them (they sit 0.6 m inside the walls)
from shapely.geometry import Polygon
from shapely.ops import unary_union
for L in {sp["level"] for sp in spaces}:
    solid = [Polygon(sp["poly"]) for sp in spaces if sp["level"] == L and sp["kind"] == "core"]
    if not solid:
        continue
    cut = unary_union(solid)
    for sp in spaces:
        if sp["level"] != L or sp["kind"] == "core":
            continue
        pg = Polygon(sp["poly"])
        if pg.intersection(cut).area > 0.05:
            d = pg.difference(cut)
            d = max(d.geoms, key=lambda g: g.area) if d.geom_type == "MultiPolygon" else d
            sp["poly"] = [[round(x, 3), round(y, 3)] for x, y in list(d.exterior.coords)[:-1]]

m["spaces"] = spaces

# ---------------------------------------------------------------- stairs
m["stairs"] = [
    {"id": "spiral_west", "kind": "spiral", "center": [-17.95, -14.85], "diameter": 7.0, "from": "F3", "to": "F1",
     "note": "open, sculptural; moved from Gym V2 (-19.5,-13.6) Ø7.9 to fit between beam lines 4 and 5"},
    {"id": "north_f3_f4", "kind": "straight", "rect": [-21.45, 7.1, -15.45, 12.1], "from": "F4", "to": "F3", "run": "north"},
    {"id": "daycare_round", "kind": "spiral", "center": [16.6, 25.0], "diameter": 5.1, "from": "E2", "to": "E1", "a0": 292.5,
     "note": "Gym V2's round stair, moved 1 m north-east and turned (Roman, 2026-10-12): the top step lands facing north into the play room "
             "(it landed on the staff-room door), the bottom step faces the open lower play room; 1.9 m clear in front of the staff door"},
]
m["fixtures"] = [
    {"id": "cafe_ring", "kind": "island_bar", "level": "E1", "center": [21.25, -1.35], "diameter": 7.0, "note": "centered in the cafe (Gym V2 had it at (20, 0.2))"},
    {"id": "reception_desk", "kind": "counter", "level": "E1", "rect": [24.4, 8.0, 25.4, 14.6], "note": "backed onto core E, facing the east entrance"},
    *[{"id": f"f3_bench_{k}", "kind": "bench", "level": "F3", "rect": [-26.6, y_, -25.3, y_ + 0.5], "height": 0.45,
       "note": ["flat", "incline", "decline"][k % 3] + " bench facing the mirror"} for k, y_ in enumerate([-32.2 + 2.25 * i for i in range(14)])],
    *[{"id": f"f3_dumbbells_{k}", "kind": "rack", "level": "F3", "rect": [-29.1, a_, -28.4, b_], "height": 0.95, "note": "dumbbell rack"}
      for k, (a_, b_) in enumerate([(-29.8, -25.0), (-22.0, -15.8), (-12.6, -1.0)])],
    {"id": "tt_table", "kind": "table", "level": "E2", "rect": [13.48, 10.12, 15.0, 12.86], "height": 0.76, "note": "table tennis, long axis parallel to the river, on the glass"},
    {"id": "pool_table", "kind": "table", "level": "E2", "rect": [17.9, 9.0, 19.17, 11.54], "height": 0.8, "note": "classic 9-ft pool table"},
    {"id": "game_sofa", "kind": "seat", "level": "E2", "rect": [16.6, 14.2, 20.2, 15.1], "height": 0.45, "note": "lounge chairs / sofa"},
    {"id": "game_coffee", "kind": "table", "level": "E2", "rect": [17.6, 13.0, 19.2, 13.8], "height": 0.4, "note": "coffee table"},
    {"id": "cafe_back_counter", "kind": "counter", "level": "E1", "rect": [15.5, -9.2, 27.0, -8.2]},
]

# ---------------------------------------------------------------- slabs + walls (frame envelope)
els = [e for e in m.get("elements", []) if e["type"] not in ("slab", "wall") and not e.get("fixed")]
WEST, EAST, LINK = (-29.45, -34.1, -6.45, 12.1), (12.0, -9.5, 30.5, 33.3), (-6.45, -12.5, 12.0, 11.3)
holes = {  # openings through each slab
    "F4": [{"rect": R(-16.45, -28.1, -6.45, -3.1)}],  # pool basin
    "F1": [{"circle": [-17.95, -14.85, 3.5]}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "F2": [{"circle": [-17.95, -14.85, 3.5]}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "F3": [{"rect": R(-21.45, 7.1, -15.45, 12.1)}, {"rect": cores["W1"]["poly"]}, {"rect": cores["W2"]["poly"]}],
    "E1": [{"circle": [16.6, 25.0, 2.55]}, {"rect": cores["E"]["poly"]}],
}
for L, rect, thick in (("F4", WEST, 0.6), ("F3", WEST, 0.25), ("F2", WEST, 0.25), ("F1", WEST, 0.25),
                       ("E2", EAST, 0.6), ("E1", EAST, 0.25), ("F1", LINK, 0.3)):
    top = lv[L]
    els.append({"id": f"S-{L}-{'link' if rect is LINK else ('west' if rect is WEST else 'east')}", "type": "slab",
                "material": "concrete", "rect": list(rect), "z": [round(top - thick, 2), top],
                "holes": holes.get(L, []) if rect is not LINK else []})
els.append({"id": "S-F1-annex", "type": "slab", "material": "concrete", "rect": [-35.45, -1.5, -29.45, 4.5], "z": [-0.25, 0.0], "holes": []})
els.append({"id": "S-RF-annex", "type": "slab", "material": "clt", "rect": [-35.45, -1.5, -29.45, 4.5], "z": [3.0, 3.2], "holes": []})
for name, rect in (("west", WEST), ("east", EAST), ("link", (-6.45, -9.5, 12.0, 6.8))):
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
                       for L in ("F4", "F3", "F2") for c_, s_ in (("W2", [3.0, 4.4]), ("W1", [19.3, 21.3]), ("WC annex", [11.0, 12.4]))] + [
                       {"s": [30.15, 32.25], "z": [lv["F4"], round(lv["F4"] + 2.3, 2)], "type": "door", "note": "men's express lift"},
                       {"s": [38.95, 41.05], "z": [lv["F4"], round(lv["F4"] + 2.3, 2)], "type": "door", "note": "women's express lift"}]
els[-1]["finishes"] = [{"level": "F3", "face": "interior", "kind": "mirror", "s": [0.0, 34.65], "z": [lv["F3"], round(lv["F3"] + 3.6, 2)],
                         "note": "floor-to-ceiling mirror; the door openings on this stretch get flush mirror-clad doors"}]
wall("W-west-N", [x0, y1], [x1, y1], 0.5, zb, zt, "retaining", "concrete")
els[-1]["openings"] = [{"s": [17.3, 18.5], "z": [lv[L], round(lv[L] + 2.3, 2)], "type": "door", "note": "core W3 (north exit stair)"} for L in ("F4", "F3", "F2")]
wall("W-west-S", [x0, y0], [x1, y0], 0.5, zb, zt, "retaining", "concrete")
els[-1]["openings"] = [{"s": s_, "z": [lv[L], round(lv[L] + 2.3, 2)], "type": "door", "note": n_} for L, s_, n_ in (
    ("F2", [2.5, 3.7], "posing room"), ("F2", [9.0, 10.2], "pod 1"), ("F2", [14.4, 15.6], "pod 2"), ("F2", [19.8, 21.0], "pod 3"),
    ("F3", [6.0, 8.0], "altitude room (airlock door)"), ("F4", [4.0, 5.6], "breathwork room"))]
els[-1]["finishes"] = [{"level": "F3", "face": "interior", "kind": "hangboard", "s": [0.6, 5.6], "z": [lv["F3"], round(lv["F3"] + 3.0, 2)],
                        "note": "grip & finger training wall: hangboards, pinch blocks, rings, campus rungs, wrist roller (no bouldering)"}]
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
# W3 (north): lies ALONG the north wall (3.2 m deep), fully outside the floor plate, mostly underground.
# Above grade it is only a low 2.6 m stone exit with a sod roof and a thin rooflight: discreet, part of the landscape.
for n_, (a_, b_) in {"W": ([-17.2, 12.35], [-17.2, 15.55]), "E": ([-8.2, 12.35], [-8.2, 15.55]), "N": ([-17.2, 15.55], [-8.2, 15.55])}.items():
    wall(f"CS-W3-{n_}", a_, b_, 0.3, lv["F4"] - 0.6, 2.6, "shaft", "concrete")
els.append({"id": "RF-W3-sod", "type": "slab", "material": "sod", "rect": [-17.4, 12.35, -8.0, 15.75], "z": [2.6, 2.95], "holes": [],
            "note": "sod roof over the north exit"})
els.append({"id": "SKY-W3", "type": "slab", "material": "glass", "rect": [-16.6, 13.4, -8.8, 14.4], "z": [2.95, 3.0], "holes": [],
            "note": "thin rooflight strip: daylight down the stairwell"})
[e for e in els if e["id"] == "CS-W3-N"][0]["openings"] = [{"s": [3.6, 5.0], "z": [0.0, 2.3], "type": "door", "note": "exit to outside (north, by the sauna path)"}]
# W2 exit door straight outside at F1 (west face of the shaft)
[e for e in els if e["id"] == "CS-W2-W"][0]["openings"] = [{"s": [2.6, 4.0], "z": [0.0, 2.3], "type": "door", "note": "exit to outside"}]
# south annex structure: retaining walls F4 -> F2 ceiling, roof slab buried under ~1 m of soil
for n_, (a_, b_) in {"S": ([-28.85, -40.1], [-6.45, -40.1]), "W": ([-28.85, -40.1], [-28.85, -34.35]), "E": ([-6.45, -40.1], [-6.45, -34.35])}.items():
    wall(f"SA-{n_}", a_, b_, 0.4, lv["F4"] - 0.6, -1.1, "retaining", "concrete")
els.append({"id": "S-SA-roof", "type": "slab", "material": "concrete", "rect": [-28.85, -40.1, -6.45, -34.1], "z": [-1.5, -1.1], "holes": []})
for L in ("F3", "F2"):
    els.append({"id": f"S-SA-{L}", "type": "slab", "material": "concrete", "rect": [-28.85, -40.1, -6.45, -34.1], "z": [round(lv[L] - 0.25, 2), lv[L]], "holes": []})
els.append({"id": "S-SA-F4", "type": "slab", "material": "concrete", "rect": [-28.85, -40.1, -6.45, -34.1], "z": [round(lv["F4"] - 0.6, 2), lv["F4"]], "holes": []})
for n_, (a_, b_) in {"W": ([-33.45, -24.75], [-33.45, -18.9]), "N": ([-33.45, -18.9], [-29.7, -18.9]), "S": ([-33.45, -24.75], [-29.7, -24.75])}.items():
    wall(f"WA-{n_}", a_, b_, 0.3, lv["F4"] - 0.6, -0.25, "retaining", "concrete")
els.append({"id": "S-WA-roof", "type": "slab", "material": "concrete", "rect": [-33.45, -24.75, -29.45, -18.9], "z": [-0.6, -0.25], "holes": []})
# underground parking: retaining walls, columns on a 8.2 x 11 m grid, roof slab = the forecourt
PZ0, PZ1 = lv["E2"] - 0.6, -1.1
wall("WP-S", [30.5, -9.5], [60.0, -9.5], 0.4, PZ0, PZ1, "retaining", "concrete")
wall("WP-N", [30.5, 24.0], [60.0, 24.0], 0.4, PZ0, PZ1, "retaining", "concrete")
wall("WP-E1", [60.0, -9.5], [60.0, -4.0], 0.4, PZ0, PZ1, "retaining", "concrete")   # gap y -4..2 = ramp tunnel
wall("WP-E2", [60.0, 2.0], [60.0, 24.0], 0.4, PZ0, PZ1, "retaining", "concrete")
for cx_ in (38.7, 46.9, 55.1):
    for cy_ in (-1.0, 11.0):
        els.append({"id": f"C-P-{cx_}-{cy_}", "type": "column", "material": "concrete", "at": [cx_, cy_], "size": [0.4, 0.4], "z": [lv["E2"], -1.5], "fixed": True})
els.append({"id": "S-P-roof", "type": "slab", "material": "concrete", "rect": [30.5, -9.5, 60.0, 24.0], "z": [-1.5, -1.1], "holes": [],
            "note": "buried roof of the parking: ~1 m of soil on top carries the forecourt, moss beds and forest floor"})
els.append({"id": "S-P-floor", "type": "slab", "material": "concrete", "rect": [30.5, -9.5, 60.0, 24.0], "z": [lv["E2"] - 0.3, lv["E2"]], "holes": []})
wall("A-annex-W", [-35.45, -1.5], [-35.45, 4.5], 0.25, 0.0, 3.0, "solid", "timber")
wall("A-annex-N", [-35.45, 4.5], [-32.0, 4.5], 0.25, 0.0, 3.0, "solid", "timber")   # door gap 32.0..-29.45 north = path exit
wall("A-annex-S", [-35.45, -1.5], [-29.45, -1.5], 0.25, 0.0, 3.0, "solid", "timber")
GLASS_A1_NOTE = "west facade: sliding glass y -26.8..-19 opens onto the training deck"
for (a, b, n) in (([x0, y0], [x0, -1.5], "A1"), ([x0, 4.5], [x0, y1], "A2"), ([x0, y1], [x1, y1], "N"), ([x0, y0], [x1, y0], "S"), ([x1, y0], [x1, -9.5], "C1"), ([x1, 6.8], [x1, y1], "C2")):
    wall(f"G-F1-{n}", a, b, 0.15, lv["F1"], 4.34, "glazed", "glass")
    if n == "N":  # discreet flush door from the gallery's north end into exit stair W3
        els[-1]["openings"] = [{"s": [18.6, 19.8], "z": [lv["F1"], 2.3], "type": "door", "swing": -1, "note": "discreet flush door: gallery -> core W3 (north exit stair)"}]
x0, y0, x1, y1 = EAST
zb, zt = lv["E2"] - 0.6, lv["E1"] - 0.25
wall("W-east-S", [x0, y0], [x1, y0], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-E1", [x1, y0], [x1, -6.0], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-E2", [x1, 0.0], [x1, y1], 0.4, zb, zt, "retaining", "concrete")  # gap = garage tunnel
wall("G-E2-W", [x0, y0], [x0, 16.18], 0.15, lv["E2"], zt, "glazed", "glass")    # garage + game room glass over the ravine
wall("W-east-W", [x0, 16.18], [x0, y1], 0.4, zb, zt, "retaining", "concrete")
wall("W-east-N1", [x0, y1], [18.0, y1], 0.4, zb, zt, "retaining", "concrete")
wall("G-E2-N", [18.0, y1], [x1, y1], 0.15, lv["E2"], zt, "glazed", "glass")     # daycare onto the sunken garden
for (a, b, n) in (([x0, y0], [x0, -9.5], "W1"), ([x0, 6.8], [x0, y1], "W2"), ([x0, y1], [x1, y1], "N"), ([x1, y0], [x1, y1], "E"), ([x0, y0], [x1, y0], "S")):
    wall(f"G-E1-{n}", a, b, 0.15, lv["E1"], 4.34, "glazed", "glass")
wall("G-E1-daycare", [24.0, 16.2], [30.5, 16.2], 0.12, lv["E1"], round(lv["E1"] + 3.0, 2), "glazed", "glass")
els[-1]["openings"] = [{"s": [2.6, 4.2], "z": [lv["E1"], round(lv["E1"] + 2.3, 2)], "type": "door", "note": "secure glass door into the daycare (staff / parent release)"}]
for (a, b, n) in (([-6.45, -9.5], [12.0, -9.5], "S"), ([-6.45, 6.8], [12.0, 6.8], "N")):
    wall(f"G-link-{n}", a, b, 0.12, 0.0, 4.0, "glazed", "glass")  # sliding glass walls

m["elements"] = els
modelio.save(m)
print(len(spaces), "spaces,", len(m["stairs"]), "stairs,", sum(e["type"] == "slab" for e in els), "slabs,", sum(e["type"] == "wall" for e in els), "walls")

"""Construction stage 5: interior shell (Roman, 2026-10-11: walls up and finished, floors, linings, ceilings; NO furniture,
equipment, fixtures or doors). Built zone by zone: the reception + the open E1 hall around it first, until its palette is locked.

Everything at real size, with real build-ups (rules of thumb, noted on each element):
  - all interior partitions go up (phase 5): 70 mm studs + 2 x 13 mm gypsum each side, painted; glass partitions framed
  - floors on the suspended slab (finished floor = level; slab top = level - 0.10):
      20 mm impact sound mat + 58 mm screed with underfloor heating + 22 mm white-oiled oak boards 220 mm wide, 1.8-2.4 m, 2 mm joints
  - entry zone inside the east doors: 2.5 m of light honed stone slabs 600 x 1200 (wet boots, snow)
  - ceilings between the exposed glulam roof beams (0.25 x 1.0 @ 8.56 m): pale oak acoustic slats 45 x 20 @ 65 mm on black felt
  - core E faces (behind the reception desk, towards the cafe): vertical oak slats 45 x 20 @ 65 on black battens
  - other walls: 15 mm warm-white lime plaster; the facade band above the glass (4.34 -> 5.64) stays dark inside too
Palette (LOCKED direction, Roman 2026-10-11): light everything, oak slat walls, dark only at the windows. python3 tools/interior.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

PALETTES = {  # Roman, 2026-10-11: light floors, light ceilings, light walls, oak slat walls; dark ONLY at the windows (frames, the facade band)
    "L": {"name": "Light Nordic oak", "floor": "oak_boards_light", "entry": "stone_light", "ceiling": "ash_wave", "feature": "oak_slats_wall",
          "plain": "lime_plaster", "header": "black_lining",
          "note": "white-oiled oak floor, undulating pale ash baffle ceiling between pale spruce glulam beams, oak slat feature walls, warm-white "
                  "lime plaster elsewhere, light honed stone at the door; the only dark surfaces are the window frames and the facade band above them"},
}
FINISH = {  # pattern + material per finish kind
    "oak_boards_light": {"kind": "boards", "w": 0.22, "L": [1.8, 2.4], "gap": 0.002, "dir": "y", "material": "oak_floor", "t": 0.022},
    "stone_light": {"kind": "slabs", "w": 0.6, "L": [1.2], "gap": 0.003, "dir": "y", "material": "stone_light", "t": 0.022},
    "oak_slats_light": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "x", "drop": 0.08, "material": "oak_slat"},
    "ash_wave": {"kind": "wave", "w": 0.03, "pitch": 0.11, "dmin": 0.06, "dmax": 0.32, "wave": 7.0, "drift": 5.0, "drop": 0.0, "d": 0.32, "material": "ash_fin"},
    "oak_slats_wall": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "z", "depth": 0.065, "material": "oak_slat"},
    "lime_plaster": {"kind": "skin", "depth": 0.015, "material": "lime_plaster"},
    # wet rooms (Roman 2026-10-12, VISION "Wet rooms"): light honed stone 600 x 600 in stack bond, glazed tile to 2.6 m, plaster above
    "stone_wet": {"kind": "slabs", "w": 0.6, "L": [0.6], "gap": 0.003, "dir": "y", "bond": "stack", "material": "stone_light", "t": 0.022},
    "tile_wall": {"kind": "tiles", "w": 0.065, "h": 0.26, "gap": 0.002, "d": 0.012, "depth": 0.02, "material": "tile_glazed"},
    "black_lining": {"kind": "skin", "depth": 0.022, "material": "timber_clad"},
}

m = modelio.load()
args = sys.argv[1:]
if "--palette" in args:
    m.setdefault("interior", {})["palette"] = args[args.index("--palette") + 1]
m.setdefault("interior", {})["palette"] = m["interior"].get("palette") if m["interior"].get("palette") in PALETTES else "L"
P = PALETTES[m["interior"]["palette"]]
m["interior"]["palettes"] = {k: {"name": v["name"], "note": v["note"]} for k, v in PALETTES.items()}
lv = {l["id"]: l["elevation"] for l in m["levels"]}
els = [e for e in m["elements"] if not e["id"].startswith("IN-")]
by_id = {e["id"]: e for e in els}
new = []
seq_of = lambda z0: int(round((z0 + 20) * 10))


def add(e):
    e["phase"] = 5
    e.setdefault("seq", seq_of(e["z"][0]))
    new.append(e)


# ---- every interior partition goes up
for e in els:
    if e["type"] == "wall" and e.get("kind") in ("partition", "glazed") and e.get("phase") is None and e["id"].startswith("P-"):
        e["phase"], e["seq"] = 5, seq_of(e["z"][0])
        if e["material"] == "timber_stud":
            e["note"] = "70 mm timber studs + 2 x 13 mm gypsum each side (122 mm), painted"
        else:
            e["mullions"] = []; e["transoms"] = []
            e["note"] = "framed glass partition, laminated safety glass"

# the glass wall between reception and the daycare entrance (desk sightline)
g = by_id.get("G-E1-daycare")
if g:
    g["phase"], g["seq"], g["mullions"], g["transoms"] = 5, seq_of(g["z"][0]), [1.3, 2.6, 3.9, 5.2], [3.0]
    g["z"] = [lv["E1"], lv["RF"]]; g["size"] = [g["size"][0], round(lv["RF"] - lv["E1"], 2)]  # full height to the ceiling: a daycare boundary
    g["note"] = "framed laminated glass: the reception desk sees into the daycare entrance"

# ---- zone: reception + the open E1 hall (cafe) around it
E1 = lv["E1"]
MAT_WELL = [28.3, 9.85, 30.45, 12.75]  # Roman: keep the stone, but a mat inside the doors for grit and snow (flush, in a well in the stone)
FLOORS = {"reception": [24.0, 6.8, 28.0, 16.2], "entry": [28.0, 6.8, 30.5, 16.2], "cafe": [12.0, -9.5, 30.5, 6.8]}
for nm, r in FLOORS.items():
    add({"id": f"IN-E1-{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(E1 - 0.10, 3), round(E1 - 0.08, 3)], "holes": [],
         "note": "20 mm impact sound mat"})
    add({"id": f"IN-E1-{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E1 - 0.08, 3), round(E1 - 0.022, 3)], "holes": [],
         "note": "58 mm screed with underfloor heating pipes"})
    f = FINISH[P["entry"] if nm == "entry" else P["floor"]]
    holes = [{"rect": MAT_WELL, "note": "recessed entrance mat well (the mat itself: tools/furnish.py)"}] if nm == "entry" else []
    add({"id": f"IN-E1-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": f["material"], "rect": r, "z": [round(E1 - f["t"], 3), E1], "holes": holes,
         "pattern": {k: v for k, v in f.items() if k not in ("material", "t")}, "note": f"floor finish: {P['entry'] if nm == 'entry' else P['floor']}"})

RF = lv["RF"]
ceil = FINISH[P["ceiling"]]
for nm, r in (("hall_n", [12.0, 6.8, 30.5, 16.18]), ("hall", [12.0, -9.5, 30.5, 6.8])):
    if nm == "hall_n":
        r = [24.0, 6.8, 30.5, 16.18]  # over the reception only (the WCs and core get their own ceilings later)
    if ceil["kind"] == "wave":
        add({"id": f"IN-E1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": ceil["material"], "rect": r, "z": [round(RF - ceil["dmax"], 3), RF], "holes": [],
             "pattern": {k: v for k, v in ceil.items() if k != "material"}, "between_beams": 0.25,
             "note": "undulating pale ash baffle ceiling: 30 mm fins @ 110 mm, depth waving 60-320 mm, black acoustic felt behind"})
        add({"id": f"IN-E1-ceiling-{nm}-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": r, "z": [round(RF - 0.01, 3), round(RF - 0.002, 3)],
             "holes": [], "note": "black acoustic felt on the CLT behind the fins"})
    elif ceil["kind"] == "slats":
        z1 = round(RF - ceil["drop"], 3)
        add({"id": f"IN-E1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": ceil["material"], "rect": r, "z": [round(z1 - ceil["d"], 3), z1], "holes": [],
             "pattern": {k: v for k, v in ceil.items() if k != "material"}, "between_beams": 0.25,
             "note": "acoustic oak slats 45 x 20 @ 65 mm on black acoustic felt + battens, between the glulam beams"})
        add({"id": f"IN-E1-ceiling-{nm}-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": r, "z": [round(z1 + 0.06, 3), round(z1 + 0.07, 3)],
             "holes": [], "note": "black acoustic felt on battens behind the slats"})
    else:
        add({"id": f"IN-E1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": ceil["material"], "rect": r, "z": [round(RF - 0.003, 3), RF], "holes": [],
             "note": "exposed CLT soffit: " + ("white-oiled spruce" if ceil["material"] == "clt_white" else "natural oiled spruce")})

# ---- walls round the zone: feature on core E, plain on the WC partitions facing the cafe
def lining(wid, finish, side_sign, s_range=None, tag="", ext=(0.0, 0.0), z=None):
    """ext = how far the lining runs past each end of its range (external corners: wall half-thickness + the other lining's depth)."""
    w = by_id[wid]
    (ax, ay), (bx, by) = w["from"], w["to"]
    import math
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy * side_sign, ux * side_sign
    f = FINISH[finish]; d = f.get("depth", 0.015)
    off = w["size"][0] / 2 + d / 2
    s0, s1 = s_range or (0.0, L)
    s0, s1 = s0 - ext[0], s1 + ext[1]
    pa = [round(ax + ux * s0 + nx * off, 3), round(ay + uy * s0 + ny * off, 3)]
    pb = [round(ax + ux * s1 + nx * off, 3), round(ay + uy * s1 + ny * off, 3)]
    zz = list(z or w["z"])
    ops = [{**o, "s": [round(o["s"][0] - s0, 2), round(o["s"][1] - s0, 2)]} for o in w.get("openings", [])
           if o["s"][1] > s0 and o["s"][0] < s1 and o["z"][1] > zz[0] and o["z"][0] < zz[1]]
    add({"id": f"IN-lining-{wid}{tag}", "type": "wall", "kind": "lining", "material": f["material"], "from": pa, "to": pb, "size": [d, round(zz[1] - zz[0], 2)],
         "z": zz, "pattern": {k: v for k, v in f.items() if k not in ("material", "depth")}, "openings": ops, "face_normal": [round(nx, 3), round(ny, 3)],
         "note": f"interior lining: {finish}"})


lining("P-E1-2", P["feature"], -1, ext=(0.065, 0.0))   # core E east face -> reception; wraps the SE corner over the cafe-side slats
lining("P-E1-0", P["feature"], -1)   # core E south face -> cafe
lining("P-E1-4", P["feature"], 1)    # WC block facing the cafe: oak slats like the core beside it (Roman: the plain wall was lame)
lining("P-E1-5", P["feature"], 1)
# interior face of the facade header bands round the hall (E + S facades)
for wid, sign, rng_ in (("EN-header-G-E1-E", 1, (0.0, 25.7)), ("EN-header-G-E1-S", 1, None)):
    lining(wid, P["header"], sign, rng_)

# ---- zone: the public WCs (E1, between the cafe and the daycare; VISION "Wet rooms")
TILE_TOP = round(E1 + 2.6, 2)
WC = {"wc-women": [12.0, 6.8, 16.4, 16.2], "wc-men": [16.4, 6.8, 20.8, 16.2]}
wet = FINISH["stone_wet"]
for sid, r in WC.items():
    nm = sid.split("-")[1]
    add({"id": f"IN-E1-wc{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(E1 - 0.10, 3), round(E1 - 0.08, 3)], "holes": [], "note": "20 mm impact sound mat"})
    add({"id": f"IN-E1-wc{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E1 - 0.08, 3), round(E1 - wet["t"], 3)], "holes": [],
         "note": "58 mm screed with underfloor heating + liquid waterproofing membrane, turned 150 mm up the walls"})
    add({"id": f"IN-E1-wc{nm}-floor", "type": "slab", "kind": "floor_finish", "material": wet["material"], "rect": r, "z": [round(E1 - wet["t"], 3), E1], "holes": [],
         "pattern": {k: v for k, v in wet.items() if k not in ("material", "t")}, "note": "floor finish: light honed stone 600 x 600, stack bond, R10"})
    # Roman: the 5.5 m void over the cells felt odd. A real WC ceiling at 2.75 (the top of the solid facade wall, so the frosted
    # clerestory sits above it): white-oiled oak acoustic slats on black felt, a closed plasterboard lid above for the extract
    # ductwork; the cells run floor to ceiling = proper full-height cubicles.
    WCC = round(E1 + 2.75, 2)
    add({"id": f"IN-E1-ceiling-wc{nm}", "type": "slab", "kind": "ceiling", "material": "oak_slat", "rect": [r[0], r[1], r[2], r[3]],
         "z": [round(WCC - 0.02, 3), WCC], "holes": [], "pattern": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "x"},
         "ignore_beams": True, "note": "oak acoustic slat ceiling at 2.75 m (45 x 20 @ 65) on black felt"})
    add({"id": f"IN-E1-ceiling-wc{nm}-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": [r[0], r[1], r[2], r[3]],
         "z": [round(WCC + 0.03, 3), round(WCC + 0.04, 3)], "holes": [], "note": "black acoustic felt behind the slats"})
    add({"id": f"IN-E1-ceiling-wc{nm}-lid", "type": "slab", "kind": "ceiling", "material": "timber_stud", "rect": [r[0], r[1], r[2], r[3]],
         "z": [round(WCC + 0.04, 3), round(WCC + 0.065, 3)], "holes": [], "note": "plasterboard lid closing the WC rooms (plenum above for extract air)"})

# every wall inside the WCs: tile to 2.6 m, plaster above. s ranges stop at the faces of the walls they meet
# (partition half 0.075, core half 0.125, facade half 0.2) + the tile depth, so the corners close without overlaps.
TD = FINISH["tile_wall"]["depth"]
WCW = [  # (wall, side towards the WC, s range, tag)
    ("P-E1-4", -1, (0.075 + TD, 4.4 - 0.2 - TD), "-wcw"),       # women's south (with the baffled entry)
    ("P-E1-5", -1, (0.125 + TD, 4.4 - 0.075 - TD), "-wcm"),     # men's south
    ("P-E1-6", 1, (0.075, 9.4 - 0.075), "-wcw"),                # women's east (shared partition)
    ("P-E1-6", -1, (0.075, 9.4 - 0.075), "-wcm"),               # men's west
    ("P-E1-7", 1, (0.075 + TD, 4.4 - 0.2 - TD), "-wcw"),        # women's north
    ("P-E1-8", 1, (0.125 + TD, 3.8), "-wcm"),                   # men's north (to the daycare WC)
    ("P-E1-9", 1, (0.0, 0.6 - 0.075 - TD), "-wcm"),             # men's north, last 0.6 m
    ("P-E1-1", -1, (0.125 + 0.075, 9.65 - 0.125 - 0.075), "-wcm"),  # men's east: core E
]
for wid, side, rng_, tag in WCW:
    w_ = by_id[wid]
    lining(wid, "tile_wall", side, rng_, tag + "-tile", z=[E1, round(E1 + 2.75, 2)])  # tile all the way to the new ceiling
# the women's west wall is the facade: solid black timber to 2.72, frosted clerestory above. Tile up to the clerestory sill.
fw = by_id["EN-G-E1-W2-0-wall"]
lining("EN-G-E1-W2-0-wall", "tile_wall", -1, (0.075 + TD, 9.4 - 0.075 - TD), "-wcw-tile", z=[E1, fw["z"][1]])

# ---- zone: the daycare upper floor (E1; VISION "Daycare: playful, still Nordic"): the light shell, oak floors,
# stone + tile in the children's WC, the ash wave ceiling everywhere; play and colour come from the furniture (tools/furnish.py)
_ds = next(st for st in m["stairs"] if st["id"] == "daycare_round")
STAIR_HOLE = {"circle": [*_ds["center"], _ds["diameter"] / 2], "note": "round stair down to the daycare lower floor (E2)"}
DC = {"dckids": ([12.0, 21.2, 30.5, 33.3], "floor", [STAIR_HOLE]), "dcward": ([24.0, 16.2, 30.5, 21.2], "floor", []),
      "dcstaff": ([12.0, 16.2, 17.0, 21.2], "floor", []), "dcwc": ([17.0, 16.2, 24.0, 21.2], "wet", [])}
for nm, (r, fk, holes) in DC.items():
    f = FINISH[P["floor"]] if fk == "floor" else wet
    add({"id": f"IN-E1-{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(E1 - 0.10, 3), round(E1 - 0.08, 3)], "holes": holes,
         "note": "20 mm impact sound mat"})
    add({"id": f"IN-E1-{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E1 - 0.08, 3), round(E1 - f["t"], 3)], "holes": holes,
         "note": "screed with underfloor heating" + (" + liquid waterproofing" if fk == "wet" else "")})
    add({"id": f"IN-E1-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": f["material"], "rect": r, "z": [round(E1 - f["t"], 3), E1], "holes": holes,
         "pattern": {k: v for k, v in f.items() if k not in ("material", "t")}, "note": "floor finish: " + ("white-oiled oak boards" if fk == "floor" else "light honed stone 600 x 600, R10")})
    cr = [r[0], max(r[1], 16.18), r[2], min(r[3], 33.3)]
    add({"id": f"IN-E1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": ceil["material"], "rect": cr, "z": [round(RF - ceil["dmax"], 3), RF], "holes": [],
         "pattern": {k: v for k, v in ceil.items() if k != "material"}, "between_beams": 0.25, "note": "undulating pale ash baffle ceiling (as the reception)"})
    add({"id": f"IN-E1-ceiling-{nm}-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": cr,
         "z": [round(RF - 0.01, 3), round(RF - 0.002, 3)], "holes": [], "note": "black acoustic felt behind the fins"})
# children's WC: tile to 2.6 m + plaster above on its four solid walls (the north side is the safeguarding glass)
for wid, side, rng_, tag in (("P-E1-12", 1, (0.075, 5.0 - 0.075 - TD), "-dcwc"),      # west wall (to the staff room)
                             ("P-E1-8", -1, (0.125, 3.8 - 0.075), "-dcwc"),            # south, behind the children's WCs
                             ("P-E1-3", -1, (0.2, 3.45 - 0.125), "-dcwc"),             # south: core E's north face
                             ("P-E1-10", -1, (0.075, 5.0 - 0.125 - TD), "-dcwc")):     # east wall (to the wardrobe)
    w_ = by_id[wid]
    lining(wid, "tile_wall", side, rng_, tag + "-tile", z=[E1, TILE_TOP])
    lining(wid, P["plain"], side, rng_, tag + "-plaster", z=[TILE_TOP, w_["z"][1]])

# ---- the lounge bridge floor (Roman: the floor dipped down to the bridge): the gym is at F1 0.00, the cafe at E1 0.12, so the
# bridge's finished oak floor rises 120 mm over its 18.45 m (1:150, imperceptible): flush at both ends, no step, no ramp.
# Build-up on the suspended link slab (top -0.10): impact mat, screed (falls with the floor), white-oiled oak boards.
F1v = lv["F1"]; BR = [-6.45, -9.5, 12.0, 6.8]
SLOPE = [[-6.45, 0.0], [12.0, round(E1 - F1v, 3)]]
# the walk-on glass panels (cast openings in tools/structure_stage.py): the build-up stops at each panel's 1.04 m steel frame
GLASS = [{"rect": [round(h["glass_floor"][0] - 0.52, 3), round(h["glass_floor"][1] - 0.52, 3), round(h["glass_floor"][0] + 0.52, 3), round(h["glass_floor"][1] + 0.52, 3)],
          "note": "walk-on glass panel in its steel frame"} for h in by_id["S-F1-link"].get("holes", []) if h.get("glass_floor")]
add({"id": "IN-F1-bridge-impact", "type": "slab", "material": "impact_mat", "rect": BR, "z": [round(F1v - 0.10, 3), round(F1v - 0.08, 3)], "holes": GLASS,
     "pattern": {"kind": "poured", "joint": 20.0}, "note": "20 mm impact sound mat"})
add({"id": "IN-F1-bridge-screed", "type": "slab", "kind": "floor_finish", "material": "screed", "rect": BR, "z": [round(F1v - 0.08, 3), round(F1v - 0.022, 3)], "holes": GLASS,
     "pattern": {"kind": "poured", "joint": 6.0}, "slope": SLOPE, "slope_top_only": True,
     "note": "screed with underfloor heating, laid to the 1:150 rise; its top under the oak; cut round the glass panels"})
fb = FINISH[P["floor"]]
# the oak stops at the sliding glass walls' floor track, just inside the posts (tools/furnish.py); outside it a drained grating
add({"id": "IN-F1-bridge-floor", "type": "slab", "kind": "floor_finish", "material": fb["material"], "rect": [BR[0], -9.375, BR[2], 6.675], "z": [round(F1v - fb["t"], 3), F1v], "holes": GLASS,
     "pattern": {**{k: v for k, v in fb.items() if k not in ("material", "t")}, "dir": "x"}, "slope": SLOPE,
     "note": "white-oiled oak boards running the length of the bridge (east-west, they lead on to the gym), rising 0.00 (gym) -> 0.12 "
             "(cafe) at 1:150: no step at either end; cut round the glass panels"})
# bridge ceiling (Roman: minimal, the light sculpture is the feature): oak acoustic slats on black felt running the length of the
# bridge, between the five glulam beams (they cross it every 4.47 m); no wave here
BR_BEAMS = sorted(e["from"][0] for e in by_id.values() if e["id"].startswith("ST3-link-roofbeam-"))
zc_ = round(RF - 0.08, 3)
add({"id": "IN-F1-ceiling-bridge", "type": "slab", "kind": "ceiling", "material": "oak_slat", "rect": BR, "z": [round(zc_ - 0.02, 3), zc_], "holes": [],
     "pattern": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "x"}, "ignore_beams": True,
     "split_x": [[round(x - 0.145, 3), round(x + 0.145, 3)] for x in BR_BEAMS],
     "note": "oak acoustic slats 45 x 20 @ 65 mm along the bridge, on black felt + battens, stopping at each glulam beam"})
add({"id": "IN-F1-ceiling-bridge-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": BR, "z": [round(zc_ + 0.06, 3), round(zc_ + 0.07, 3)],
     "holes": [], "note": "black acoustic felt on battens behind the slats"})
for wid, sign in (("EN-header-G-link-S", 1), ("EN-header-G-link-N", -1)):  # the header band over the glass stays dark inside (as in the cafe)
    lining(wid, P["header"], sign)

# ---- the decks (outdoors, cantilevered over the river; Roman: standing tables + outdoor sofas). Build-up on the deck slab (top -0.10):
# a torch-on waterproofing membrane laid to falls towards the edge gutters, adjustable pedestals on rubber pads, and 28 x 120 mm
# Kebony (furfurylated pine, weathers silver like the old boat houses) with 6 mm gaps, running east-west like the oak inside, its top
# 15 mm under the bridge floor (a slot drain at the threshold takes the step: level access when the glass walls open)
DECKS = {"n": ([-6.39, 6.98, 11.8, 11.22], []), "s": ([-6.39, -12.42, 11.92, -9.68], [{"rect": [-6.67, -11.32, -6.23, -10.68], "note": "gym facade column C4"}])}
for nm, (r, holes) in DECKS.items():
    add({"id": f"IN-F1-deck{nm}-membrane", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(F1v - 0.10, 3), round(F1v - 0.095, 3)], "holes": holes,
         "pattern": {"kind": "poured", "joint": 20.0}, "note": "torch-on bitumen waterproofing to falls, under the pedestals"})
    add({"id": f"IN-F1-deck{nm}-boards", "type": "slab", "kind": "floor_finish", "material": "decking", "rect": r, "z": [round(F1v - 0.015 - 0.028, 3), round(F1v - 0.015, 3)],
         "holes": holes, "pattern": {"kind": "boards", "w": 0.126, "L": [3.0, 3.6, 4.2], "gap": 0.006, "dir": "x"}, "slope": SLOPE,
         "note": "28 x 120 Kebony decking, 6 mm gaps, on adjustable pedestals; top 15 mm below the bridge floor, rising with it at 1:150"})

# ---- zone: the gallery + the F1 gym hall (Roman, 2026-10-12: as the bridge lands it becomes the gym: proper gym flooring, different
# lighting, a different vibe). The oak ends at a blackened-steel threshold on the facade line (x -6.45); from there:
#   - floor (Roman: the high-grade impact tiles luxury + commercial gyms have, the tiles visible): 1.0 x 1.0 m interlocking rubber
#     tiles, 30 mm (free-weight grade: a dense 3 mm EPDM wear layer in black with grey + oat fleck over a shock-absorbing SBR base,
#     hidden connectors, as SPORTEC Style at Third Space), every tile its own piece with eased edges and a tight dark seam, on an
#     acoustic underlay over the screed; through the gallery and the whole F1 hall (equipment zones come with the hall)
#   - ceiling: wood-wool acoustic panels (600 x 1200 x 35, natural) between the glulam beams, on battens under the CLT
#   - the gallery wall across from the bridge: oak slats 45 @ 65 on black battens up to the beams' soffit (4.34), the locker entries
#     and the Kilden niche cut through; warm plaster above
GAL = [-11.6, -9.3, -6.45, 12.1]
HALL = [-29.45, -34.1, -6.45, -9.3]
_sp = next(st for st in m["stairs"] if st["id"] == "spiral_west")
HALL_HOLES = [{"circle": [*_sp["center"], _sp["diameter"] / 2], "note": "spiral stair"},
              {"rect": [-29.45, -18.55, -28.85, -9.55], "note": "core W1"}, {"rect": [-29.45, -34.1, -28.85, -25.1], "note": "core W2"}]
RUB = {"kind": "slabs", "w": 1.0, "L": [1.0], "gap": 0.0025, "dir": "y", "bond": "stack", "bevel": 0.003}
for nm, r, holes in (("gallery", GAL, []), ("hall", HALL, HALL_HOLES)):
    add({"id": f"IN-F1-{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(F1v - 0.10, 3), round(F1v - 0.08, 3)], "holes": holes,
         "pattern": {"kind": "poured", "joint": 30.0}, "note": "20 mm impact sound mat"})
    add({"id": f"IN-F1-{nm}-screed", "type": "slab", "kind": "floor_finish", "material": "screed", "rect": r, "z": [round(F1v - 0.08, 3), round(F1v - 0.038, 3)],
         "holes": holes, "pattern": {"kind": "poured", "joint": 6.0}, "note": "screed with underfloor heating"})
    add({"id": f"IN-F1-{nm}-pad", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(F1v - 0.038, 3), round(F1v - 0.03, 3)], "holes": holes,
         "pattern": {"kind": "poured", "joint": 30.0}, "note": "8 mm acoustic underlay (the seams between the tiles read dark on it)"})
    add({"id": f"IN-F1-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": "gym_rubber", "rect": r, "z": [round(F1v - 0.03, 3), F1v], "holes": holes,
         "pattern": RUB, "note": "floor finish: 30 mm interlocking rubber impact tiles 1.0 x 1.0, EPDM wear layer, black with grey + oat fleck"})
WBEAMS = sorted(e["from"][1] for e in by_id.values() if e["type"] == "beam" and e["id"].endswith("-RF-west"))
for nm, r in (("gallery", GAL), ("hall", [-29.45, -34.1, -6.45, -9.3])):
    beam_cuts = [{"rect": [r[0], round(yb - 0.17, 3), r[2], round(yb + 0.17, 3)], "note": "glulam beam"} for yb in WBEAMS if r[1] - 0.2 < yb < r[3] + 0.2]
    add({"id": f"IN-F1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": "wood_wool", "rect": r, "z": [round(RF - 0.06, 3), round(RF - 0.025, 3)],
         "holes": beam_cuts + ([{"circle": [*_sp["center"], _sp["diameter"] / 2], "note": "spiral stair"}] if nm == "hall" else []),
         "pattern": {"kind": "slabs", "w": 0.6, "L": [1.2], "gap": 0.004, "dir": "x", "bond": "stack"},
         "note": "wood-wool acoustic panels 600 x 1200 x 35, natural, on battens under the CLT, between the glulam beams"})
# Kilden, the spring, on the bridge axis (y -1.35) between the two locker entries: a 1.6 m niche cut through the men's gallery wall
# (its granite lining, water wall, trough and taps: tools/furnish.py)
KW = next(e for e in by_id.values() if e["id"].startswith("P-F1-") and set(e.get("between", [])) == {"men-lockers", "gallery"})
ks = lambda y: round(abs(y - KW["from"][1]), 3)
KW["openings"].append({"s": sorted([ks(-2.15), ks(-0.55)]), "z": [F1v, 2.5], "type": "opening", "note": "Kilden: the spring niche on the bridge axis"})
# the gallery wall across from the bridge (gallery faces of the locker partitions): oak slats to the beams, plaster above
for e in [e for e in by_id.values() if e["id"].startswith("P-F1-") and "gallery" in e.get("between", [])]:
    sg = 1 if (e["to"][1] - e["from"][1]) > 0 else -1  # the gallery is east (+x) of these walls
    lining(e["id"], P["feature"], -sg, tag="-gal", z=[F1v, 4.34])
    lining(e["id"], P["plain"], -sg, tag="-gal-top", z=[4.34, RF])

# ---- zone: the F1 locker rooms, the shell (Roman, 2026-10-13: the actual interior first, then the facilities). Plan + rules in
# model/layouts/lockers.json (tools/locker_layout.py, blueprint/layout.html) and VISION "Locker rooms: hygiene zoning".
#   changing rooms (barefoot): white-oiled oak boards on UFH; warm plaster walls; riven slate courses to 1.0 m along the stream wall;
#     an oak slat ceiling at 3.2 m on felt + a lid (extract plenum above), cut round for an oculus over each round locker room
#   shoe zones (gallery -> WC room door): light honed stone
#   wash zones (barefoot, clean): light honed stone 600 x 600, R11; tile to 2.6, plaster above; open to the clerestory, no ceiling
#   WC rooms: their own floor (grey porcelain 300 x 300, photocatalytic), tile to a 2.75 m oak slat ceiling + lid (negative pressure)
#   the stream (Bekken): a 350 mm slate channel cut 120 mm into the floor (furnish: the channel, pebbles, water)
import json as _json
from shapely.geometry import LineString as _LS, Polygon as _Poly, box as _box
from shapely.ops import unary_union as _union
LK = _json.loads((ROOT / "model" / "layouts" / "lockers.json").read_text())
_sp = {s_["id"]: s_ for s_ in m["spaces"]}
_wall_els = [e for e in els if e["type"] == "wall" and e.get("kind") not in ("lining", "trim") and e["z"][0] <= F1v + 1.0 <= e["z"][1]
             and min(e["from"][0], e["to"][0]) < -5 and max(e["from"][0], e["to"][0]) > -36 and min(e["from"][1], e["to"][1]) < 13 and max(e["from"][1], e["to"][1]) > -10]
def _foot(e):
    return _LS([e["from"], e["to"]]).buffer(e["size"][0] / 2, cap_style=2)
_walls_u = _union([_foot(e) for e in _wall_els])
def clear(room):
    return _Poly(_sp[room]["poly"]).difference(_walls_u)
def line_rooms(room, finish, z, tag, only=None, skip=()):
    """Line every wall face of a room with a finish, each lining exactly between the faces of the walls it meets."""
    cp = clear(room); f = FINISH[finish]; dep = f.get("depth", 0.015)
    for e in _wall_els:
        if e["id"] in skip or (only and e["id"] not in only):
            continue
        (ax, ay), (bx, by) = e["from"], e["to"]; L = math.hypot(bx - ax, by - ay)
        if L < 0.2:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        for sg in (1, -1):
            nx, ny = -uy * sg, ux * sg; off = e["size"][0] / 2 + 0.004
            ln = _LS([(ax + nx * off, ay + ny * off), (bx + nx * off, by + ny * off)]).intersection(cp.buffer(0.002))
            for g in getattr(ln, "geoms", [ln]):
                if g.is_empty or g.geom_type != "LineString" or g.length < 0.15:
                    continue
                ss = sorted(((c[0] - ax) * ux + (c[1] - ay) * uy) for c in g.coords)
                s0, s1 = max(0.0, ss[0]), min(L, ss[-1])
                if s1 - s0 > 0.15:
                    lining(e["id"], finish, sg, (round(s0 + dep * 0 , 3), round(s1, 3)), tag=f"-{tag}-{sg}-{round(s0, 1)}", z=z)
import math
FINISH["slate_courses"] = {"kind": "courses", "h": [0.035, 0.05, 0.065, 0.08], "L": [0.3, 0.42, 0.55, 0.7], "gap": 0.004, "depth": 0.03, "material": "slate_riven"}
FINISH["wc_tile_floor"] = {"kind": "slabs", "w": 0.3, "L": [0.3], "gap": 0.002, "dir": "y", "bond": "stack", "material": "porcelain_grey", "t": 0.012}
# floors
_streams = [i for i in LK["items"] if i["kind"] == "stream"]
def _stream_holes(rect):
    hs = []
    for st in _streams:
        w2 = st["width"] / 2 + 0.03
        for (xa, ya), (xb, yb) in zip(st["pts"], st["pts"][1:]):
            r_ = [min(xa, xb) - w2, min(ya, yb) - w2, max(xa, xb) + w2, max(ya, yb) + w2]
            r_ = [max(r_[0], rect[0]), max(r_[1], rect[1]), min(r_[2], rect[2]), min(r_[3], rect[3])]
            if r_[2] - r_[0] > 0.05 and r_[3] - r_[1] > 0.05:
                hs.append({"rect": [round(v, 3) for v in r_], "note": "the stream's slate channel"})
    for pb in [i for i in LK["items"] if i["kind"] == "pool_basin"]:
        r_ = [pb["x"] - pb["w"] / 2 - 0.03, pb["y"] - pb["d"] / 2 - 0.03, pb["x"] + pb["w"] / 2 + 0.03, pb["y"] + pb["d"] / 2 + 0.03]
        r_ = [max(r_[0], rect[0]), max(r_[1], rect[1]), min(r_[2], rect[2]), min(r_[3], rect[3])]
        if r_[2] - r_[0] > 0.05 and r_[3] - r_[1] > 0.05:
            hs.append({"rect": [round(v, 3) for v in r_], "note": "the stream's pool"})
    return hs
LIFT_M, LIFT_W = [-29.45, -4.1, -28.85, -1.7], [-29.45, 4.7, -28.85, 7.1]
LKF = {  # name: rect, finish, extra holes
    "mchg": ([-29.45, -4.2, -14.4, 1.5], "oak", [{"rect": LIFT_M}]), "wchg": ([-29.45, 1.5, -14.4, 7.65], "oak", [{"rect": LIFT_W}]),
    "mshoe": ([-14.4, -4.2, -11.6, -0.375], "shoe", []), "wshoe": ([-14.4, -0.375, -11.6, 7.65], "shoe", []),
    "mwash": ([-29.45, -9.3, -19.4, -4.2], "wet", []), "wwash": ([-29.45, 7.65, -19.4, 12.1], "wet", []),
    "mwc": ([-19.4, -9.3, -11.6, -4.2], "wc", []), "wwc": ([-19.4, 7.65, -11.6, 12.1], "wc", []),
    "lobby": ([-35.45, -1.5, -29.45, 4.5], "wet", []),
}
for nm, (r, fk, extra) in LKF.items():
    f = {"oak": {**FINISH[P["floor"]], "dir": "x"}, "shoe": FINISH["stone_light"], "wet": wet, "wc": FINISH["wc_tile_floor"]}[fk]
    holes = extra + _stream_holes(r)
    add({"id": f"IN-F1-{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(F1v - 0.10, 3), round(F1v - 0.08, 3)], "holes": holes,
         "pattern": {"kind": "poured", "joint": 30.0}, "note": "20 mm impact sound mat"})
    add({"id": f"IN-F1-{nm}-screed", "type": "slab", "kind": "floor_finish", "material": "screed", "rect": r, "z": [round(F1v - 0.08, 3), round(F1v - f["t"], 3)], "holes": holes,
         "pattern": {"kind": "poured", "joint": 6.0}, "note": "screed with underfloor heating" + ("" if fk in ("oak", "shoe") else " + liquid waterproofing, laid to the drains")})
    add({"id": f"IN-F1-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": f["material"], "rect": r, "z": [round(F1v - f["t"], 3), F1v], "holes": holes,
         "pattern": {k: v for k, v in f.items() if k not in ("material", "t")},
         "note": {"oak": "white-oiled oak boards (barefoot)", "shoe": "light honed stone (the shoe zone)", "wet": "light honed stone 600 x 600, R11",
                  "wc": "the WC room's own floor: grey porcelain 300 x 300, photocatalytic glaze, to falls"}[fk]})
# walls
for room in ("men-wet", "women-wet"):
    line_rooms(room, "tile_wall", [F1v, 2.6], "lkw")
    line_rooms(room, P["plain"], [2.6, 5.64], "lkwp", skip=[e["id"] for e in _wall_els if e.get("kind") == "clad"])
for room in ("men-wc", "women-wc"):
    line_rooms(room, "tile_wall", [F1v, 2.75], "lkt")
for room in ("men-lockers", "women-lockers"):
    wetwall = [e["id"] for e in _wall_els if set(e.get("between", [])) & {"men-wet", "women-wet", "men-wc", "women-wc"} and room in e.get("between", [])]
    line_rooms(room, "slate_courses", [F1v, 1.0], "lks", only=wetwall)
    line_rooms(room, P["plain"], [1.0, 3.2], "lkp", only=wetwall)
    line_rooms(room, P["plain"], [F1v, 3.2], "lkp", skip=wetwall)
line_rooms("sauna-lobby", P["plain"], [F1v, 2.9], "lkl")
# the men's urinal room: tiled stud walls inside the WC room (from the layout)
for it in [i for i in LK["items"] if i["kind"] == "partition"]:
    rr = math.radians(it["rot"]); hx, hy = math.cos(rr) * it["w"] / 2, math.sin(rr) * it["w"] / 2
    wid = f"IN-F1-{it['id']}"
    w_ = {"id": wid, "type": "wall", "kind": "partition", "material": "timber_stud", "from": [round(it["x"] - hx, 3), round(it["y"] - hy, 3)],
          "to": [round(it["x"] + hx, 3), round(it["y"] + hy, 3)], "size": [0.1, 2.75], "z": [F1v, 2.75], "openings": [], "note": it["label"]}
    add(w_); by_id[wid] = w_
    for sg in (1, -1):
        lining(wid, "tile_wall", sg, (0.0, it["w"]), tag=f"-t{sg}", z=[F1v, 2.75])
# ceilings: changing rooms at 3.2 with an oculus over each round locker room; WC rooms at 2.75
for room, rect in (("men-lockers", [-29.375, -4.275, -11.675, 1.425]), ("women-lockers", [-29.375, 1.575, -11.675, 7.575])):
    ocs = [{"circle": [r_["x"], r_["y"], 1.0], "note": "oculus over a round locker room"} for r_ in LK["items"] if r_["kind"] == "locker_ring" and r_["room"] == room]
    nm = room.split("-")[0]
    add({"id": f"IN-F1-ceiling-{nm}chg", "type": "slab", "kind": "ceiling", "material": "oak_slat", "rect": rect, "z": [3.18, 3.2], "holes": ocs,
         "pattern": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "x"}, "ignore_beams": True,
         "note": "oak acoustic slats at 3.2 m on black felt, cut round the oculi over the round locker rooms"})
    add({"id": f"IN-F1-ceiling-{nm}chg-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": rect, "z": [3.23, 3.24], "holes": ocs,
         "pattern": {"kind": "poured", "joint": 0.25}, "note": "black acoustic felt behind the slats"})
    add({"id": f"IN-F1-ceiling-{nm}chg-lid", "type": "slab", "kind": "ceiling", "material": "timber_stud", "rect": rect, "z": [3.24, 3.265], "holes": ocs,
         "pattern": {"kind": "poured", "joint": 0.25}, "note": "plasterboard lid (extract + supply plenum above)"})
add({"id": "IN-F1-ceiling-lobby", "type": "slab", "kind": "ceiling", "material": "clt_white", "rect": [-35.45, -1.5, -29.45, 4.5], "z": [2.996, 3.0], "holes": [],
     "note": "the sauna lobby's CLT soffit, white-oiled"})
for nm, rect in (("mwash", [-29.45, -9.3, -19.4, -4.2]), ("wwash", [-29.45, 7.65, -19.4, 12.1])):  # wash zones: open to the clerestory
    add({"id": f"IN-F1-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": "clt_white", "rect": rect, "z": [round(RF - 0.004, 3), RF], "holes": [],
         "note": "the CLT soffit, white-oiled (moisture-tolerant finish; the wash zones stay tall and daylit)"})
for room, rect in (("men-wc", [-19.325, -9.225, -11.675, -4.275]), ("women-wc", [-19.325, 7.725, -11.675, 11.9])):
    nm = room.split("-")[0]
    add({"id": f"IN-F1-ceiling-{nm}wc", "type": "slab", "kind": "ceiling", "material": "oak_slat", "rect": rect, "z": [2.73, 2.75], "holes": [],
         "pattern": {"kind": "slats", "w": 0.045, "d": 0.02, "pitch": 0.065, "dir": "x"}, "ignore_beams": True, "note": "oak slat ceiling at 2.75 m"})
    add({"id": f"IN-F1-ceiling-{nm}wc-lid", "type": "slab", "kind": "ceiling", "material": "timber_stud", "rect": rect, "z": [2.79, 2.815], "holes": [],
         "note": "plasterboard lid: the WC room is a closed box at negative pressure (extract plenum above)"})

# ---- the staff toilet: a small walled room in the staff room's south-east corner (Roman: not an odd booth), stud walls to 2.7 m with
# a plastered lid (the staff room stays tall and open to its new forest window), tiled inside like every wet room
SW_ = [("IN-E1-staffwc-W", [15.3, 16.275], [15.3, 18.5], []),
       ("IN-E1-staffwc-N", [15.25, 18.45], [16.925, 18.45], [{"s": [0.35, 1.25], "z": [E1, round(E1 + 2.1, 2)], "type": "door", "note": "staff toilet door"}])]
for wid, a_, b_, ops in SW_:
    w_ = {"id": wid, "type": "wall", "kind": "partition", "material": "timber_stud", "from": a_, "to": b_, "size": [0.1, 2.7],
          "z": [E1, round(E1 + 2.7, 2)], "openings": ops, "note": "70 mm studs + gypsum, painted outside, tiled inside"}
    add(w_); by_id[wid] = w_
add({"id": "IN-E1-staffwc-lid", "type": "slab", "material": "lime_plaster", "rect": [15.25, 16.275, 16.925, 18.5], "z": [round(E1 + 2.7, 2), round(E1 + 2.75, 2)],
     "holes": [], "note": "plastered lid over the staff toilet"})
for wid, side, rng_, tag in (("IN-E1-staffwc-W", -1, (0.0, 2.175 - 0.05 - TD), "-in"), ("IN-E1-staffwc-N", -1, (0.05 + TD, 1.675), "-in"),
                             ("P-E1-12", -1, (2.75, 4.925 - TD), "-staffwc"), ("P-E1-7", -1, (0.0, 1.0), "-staffwc"), ("P-E1-9", -1, (0.075, 0.6), "-staffwc")):
    lining(wid, "tile_wall", side, rng_, tag + "-tile", z=[E1, round(E1 + 2.6, 2)])

# ---- zone: the daycare lower floor (E2, under the upper one): active play walking out to the sunken garden, the sleep room,
# the children's WC (stacked), the pram + outdoor-gear store. Same light shell; the ceiling is the wave hung under the E1 slab
# between its beams (slab soffit -0.23, beams to -0.88).
E2 = lv["E2"]; SOF = -0.23
DL = {"dclow": ([12.0, 21.2, 30.5, 33.3], "floor", [STAIR_HOLE]), "dcrest": ([12.0, 16.18, 17.0, 21.2], "floor", []),
      "dcwclow": ([17.0, 16.18, 24.0, 21.2], "wet", []), "dcstore": ([24.0, 16.18, 30.5, 21.2], "wet", [])}
for nm, (r, fk, holes) in DL.items():
    f = FINISH[P["floor"]] if fk == "floor" else wet
    if nm == "dcrest":  # Roman: a soft carpeted floor in the sleep room (mats + blankets on it): 10 mm wool carpet on felt underlay
        add({"id": f"IN-E2-{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E2 - 0.08, 3), round(E2 - 0.012, 3)], "holes": [],
             "note": "screed with underfloor heating"})
        add({"id": f"IN-E2-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": "carpet_wool", "rect": r, "z": [round(E2 - 0.012, 3), E2], "holes": [],
             "note": "floor finish: wall-to-wall oat wool carpet on felt underlay"})
        continue
    add({"id": f"IN-E2-{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E2 - 0.08, 3), round(E2 - f["t"], 3)], "holes": [],
         "note": "screed with underfloor heating on the raft (insulated below)" + (" + liquid waterproofing" if fk == "wet" else "")})
    add({"id": f"IN-E2-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": f["material"], "rect": r, "z": [round(E2 - f["t"], 3), E2], "holes": [],
         "pattern": {k: v for k, v in f.items() if k not in ("material", "t")}, "note": "floor finish: " + ("white-oiled oak boards" if fk == "floor" else "light honed stone 600 x 600, R10")})
    if nm != "dcrest":  # the sleep room gets its own star ceiling (tools/furnish.py)
        tr = by_id.get("ST3-trimmer-dc-stair")
        add({"id": f"IN-E2-ceiling-{nm}", "type": "slab", "kind": "ceiling", "material": ceil["material"], "rect": r, "z": [round(SOF - ceil["dmax"], 3), SOF],
             "holes": holes, "cut_x": [[round(tr["from"][0] - 0.3, 2), round(tr["from"][0] + 0.3, 2)]] if tr and r[0] < tr["from"][0] < r[2] else [],
             "pattern": {k: v for k, v in ceil.items() if k != "material"}, "between_beams": 0.5,
             "note": "ash wave ceiling under the E1 slab, between its beams, cut round the stairwell and the stair trimmer"})
        add({"id": f"IN-E2-ceiling-{nm}-felt", "type": "slab", "kind": "ceiling", "material": "felt_black", "rect": r, "z": [round(SOF - 0.01, 3), round(SOF - 0.002, 3)],
             "holes": [STAIR_HOLE] if holes else [], "note": "black acoustic felt on the slab soffit"})
# the concrete retaining walls of the play room: warm lime plaster (the climbing wall goes on the west one)
for wid, side, rng_ in (("W-east-W", -1, (5.02 + 0.075, 17.12 - 0.2 - 0.015)), ("W-east-N1", -1, (0.2, 6.0))):
    lining(wid, P["plain"], side, rng_, "-dclow", z=[E2, -0.88])
lining("W-east-W", P["plain"], -1, (0.2 + 0.0, 5.02 - 0.075), "-dcrest", z=[E2, -0.88])
lining("W-east-E2", P["plain"], 1, (21.275, 33.24), "-dclow", z=[E2, -0.88])      # east concrete wall of the play room
lining("W-east-E2", P["plain"], 1, (16.305, 21.125), "-dcstore", z=[E2, -0.88])   # and of the pram store
for wid, side, rng_, tag in (("P-E2-25", -1, (0.075 + TD, 5.02 - 0.075), "-dcwclow"),   # west (to the sleep room)
                             ("P-E2-23", -1, (0.125, 3.8 - 0.075), "-dcwclow"),          # south, behind the children's WCs
                             ("P-E2-20", -1, (0.2, 3.325 - 0.0), "-dcwclow"),            # core E's north face
                             ("P-E2-27", -1, (0.075, 5.0 - 0.125 - TD), "-dcwclow")):    # east (to the store)
    w_ = by_id[wid]
    lining(wid, "tile_wall", side, rng_, tag + "-tile", z=[E2, round(E2 + 2.6, 2)])
    lining(wid, P["plain"], side, rng_, tag + "-plaster", z=[round(E2 + 2.6, 2), w_["z"][1]])

m["elements"] = els + new
modelio.save(m)
print(f"phase-5 elements: {sum(1 for e in m['elements'] if e.get('phase') == 5)}; reception palette {m['interior']['palette']} ({P['name']})")

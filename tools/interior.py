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
FLOORS = {"reception": [24.0, 6.8, 28.0, 16.2], "entry": [28.0, 6.8, 30.5, 16.2], "cafe": [12.0, -9.5, 30.5, 6.8]}
for nm, r in FLOORS.items():
    add({"id": f"IN-E1-{nm}-impact", "type": "slab", "material": "impact_mat", "rect": r, "z": [round(E1 - 0.10, 3), round(E1 - 0.08, 3)], "holes": [],
         "note": "20 mm impact sound mat"})
    add({"id": f"IN-E1-{nm}-screed", "type": "slab", "material": "screed", "rect": r, "z": [round(E1 - 0.08, 3), round(E1 - 0.022, 3)], "holes": [],
         "note": "58 mm screed with underfloor heating pipes"})
    f = FINISH[P["entry"] if nm == "entry" else P["floor"]]
    add({"id": f"IN-E1-{nm}-floor", "type": "slab", "kind": "floor_finish", "material": f["material"], "rect": r, "z": [round(E1 - f["t"], 3), E1], "holes": [],
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
def lining(wid, finish, side_sign, s_range=None, tag=""):
    w = by_id[wid]
    (ax, ay), (bx, by) = w["from"], w["to"]
    import math
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy * side_sign, ux * side_sign
    f = FINISH[finish]; d = f.get("depth", 0.015)
    off = w["size"][0] / 2 + d / 2
    s0, s1 = s_range or (0.0, L)
    pa = [round(ax + ux * s0 + nx * off, 3), round(ay + uy * s0 + ny * off, 3)]
    pb = [round(ax + ux * s1 + nx * off, 3), round(ay + uy * s1 + ny * off, 3)]
    ops = [{**o, "s": [round(o["s"][0] - s0, 2), round(o["s"][1] - s0, 2)]} for o in w.get("openings", []) if o["s"][1] > s0 and o["s"][0] < s1]
    add({"id": f"IN-lining-{wid}{tag}", "type": "wall", "kind": "lining", "material": f["material"], "from": pa, "to": pb, "size": [d, round(w["z"][1] - w["z"][0], 2)],
         "z": list(w["z"]), "pattern": {k: v for k, v in f.items() if k not in ("material", "depth")}, "openings": ops, "face_normal": [round(nx, 3), round(ny, 3)],
         "note": f"interior lining: {finish}"})


lining("P-E1-2", P["feature"], -1)   # core E east face -> reception (the wall behind the desk)
lining("P-E1-0", P["feature"], -1)   # core E south face -> cafe
lining("P-E1-4", P["plain"], 1)      # WC partitions facing the cafe
lining("P-E1-5", P["plain"], 1)
# interior face of the facade header bands round the hall (E + S facades)
for wid, sign, rng_ in (("EN-header-G-E1-E", 1, (0.0, 25.7)), ("EN-header-G-E1-S", 1, None)):
    lining(wid, P["header"], sign, rng_)

m["elements"] = els + new
modelio.save(m)
print(f"phase-5 elements: {sum(1 for e in m['elements'] if e.get('phase') == 5)}; reception palette {m['interior']['palette']} ({P['name']})")

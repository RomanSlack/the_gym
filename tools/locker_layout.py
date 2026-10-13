"""Locker rooms, F1: the proposed 2D layout (Roman, 2026-10-12: "get the exact dimensions, then look at it top down in 2D to place
all the elements before we devote time to 3D"). Writes model/layouts/lockers.json, which is then the source of truth: it is edited
by hand in the layout page (blueprint/layout.html, dragging + saving) and read by the 3D later. Only written if missing, or with
--force (that throws away the edits).

Exact geometry (wall FACES, from model/building.json): facade walls 0.4 thick, partitions 0.15, lift walls 0.25.
  men's changing   x -29.375 .. -11.675, y -4.275 .. 1.425 (the women's vestibule notch x > -14.4, y > -0.45; Kilden's box
                   x > -12.36, y -2.4 .. -0.45; lift x < -28.725, y -4.225 .. -1.575; sauna door y -0.5 .. 0.5 in the west wall)
  men's wet        x -29.25 .. -11.675, y -9.225 .. -4.275; openings to the changing room x -27.37/-25.57, -21.42/-19.62, -15.48/-13.68
  women's changing x -29.375 .. -11.675, y 1.575 .. 7.575 (+ vestibule x -14.325 .. -11.675, y -0.3 .. 1.575; lift y 4.575 .. 7.225;
                   sauna door y 2.5 .. 3.5)
  women's wet      x -29.25 .. -11.675, y 7.725 .. 11.9; the same three openings
  sauna lobby      x -35.325 .. -29.525, y -1.375 .. 4.375 (annex outside the west wall)
Planning rules (refs: commercial changing-room guidance + club practice; see VISION "Locker rooms"):
  - the lockers in small enclosed groups, not round the perimeter of one big room (club guidance: U-shaped bays feel private and
    calm); made unique (Roman): three ROUND locker rooms carved out of one oak block per room, full-height oak lockers
    (400 at the face x 550 deep x 2000) on the curve, >= 1.0 m between the locker faces and the round seat, a >= 1.5 m main aisle
  - a screen on the vestibule line hides the bays from the entry; an arrival nook at the door: shoes off (Norwegian habit, winter),
    towels; the west end kept clear in front of the express lift + the sauna-lobby door (1.5 m turning circle)
  - private showers with their own dry area (shower 1.2 + dry 0.9 deep, ~0.98 wide), one accessible shower (1.8 wide) per room;
    'Fossen', a walk-in experience shower per wet zone (tiered rain, a cold bucket, a stone wall) under the west clerestory;
    full-height WC cells (1.0 x 1.8) + an accessible WC (2.0 x 2.2, TEK17); urinals in the men's; vanity troughs + a grooming
    station on the changing-room side of the wet zone; a cleaner's cupboard per wet zone
terrain/.venv/bin/python tools/locker_layout.py [--force]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "layouts" / "lockers.json"
if OUT.exists() and "--force" not in sys.argv:
    print("kept (edited by hand in blueprint/layout.html):", OUT.relative_to(ROOT), "· --force to regenerate")
    sys.exit(0)

KINDS = {  # plan size defaults (w along the piece, d front-to-back), height, front clearance to keep free, colour key
    "lockers": {"label": "Lockers 400 x 550, full height", "d": 0.55, "h": 2.0, "unit": 0.4, "clear": 1.2, "mat": "oak"},
    "bench": {"label": "Walnut bench", "d": 0.45, "h": 0.45, "mat": "walnut"},
    "screen": {"label": "Oak screen, full height", "d": 0.1, "h": 2.6, "mat": "oak"},
    "oak_block": {"label": "Oak block (closed storage between the drums)", "d": 4.2, "h": 2.6, "mat": "oak_solid"},
    "locker_ring": {"label": "Round locker room", "d": 3.9, "h": 2.0, "mat": "oak"},
    "round_seat": {"label": "Round seat", "d": 0.8, "h": 0.45, "mat": "walnut"},
    "stream": {"label": "Bekken: the stream (slate channel, pebble bed, moving water)", "d": 0.35, "h": -0.12, "mat": "water"},
    "spring_basin": {"label": "Spring basin: where the stream rises", "d": 0.6, "h": 0.5, "mat": "stone"},
    "bridge_slab": {"label": "Granite slab over the stream (flush)", "d": 0.6, "h": 0.0, "mat": "stone"},
    "wash_station": {"label": "Seated wash place (onsen): oak stool, hand shower, bucket, slate shelf", "d": 1.0, "h": 1.2, "clear": 0.6, "mat": "wet"},
    "floor_zone": {"label": "Floor zone (its own floor)", "d": 1.0, "h": 0.0, "mat": "zone"},
    "partition": {"label": "Partition, full height, tiled", "d": 0.1, "h": 2.6, "mat": "wall"},
    "slipper_rack": {"label": "Toilet slippers in a UV-C cabinet (onsen habit; sanitised between users)", "d": 0.35, "h": 0.6, "mat": "oak"},
    "robot": {"label": "Vaskebjørn: cleaning robot (420 cube, oak panels, steel chassis, smoked-glass face, zone ring)", "d": 0.42, "h": 0.42, "mat": "robot"},
    "robot_dock": {"label": "Robot dock (charge, auto-empty + refill)", "d": 0.5, "h": 0.5, "mat": "steel"},
    "uvc_plate": {"label": "UV-C sole plate: walk over it, soles sanitised", "d": 0.9, "h": 0.0, "mat": "uvc"},
    "far_uvc": {"label": "Far-UVC lamp (222 nm, ceiling)", "d": 0.25, "h": 0.0, "mat": "uvc"},
    "fossen": {"label": "Fossen: experience shower (tiered rain, cold bucket, stone wall)", "d": 2.1, "h": 2.6, "clear": 1.2, "mat": "wet_feature"},
    "shoe_bench": {"label": "Shoe bench + rack (shoes off)", "d": 0.4, "h": 0.45, "mat": "walnut"},
    "towels": {"label": "Fresh towels", "d": 0.45, "h": 1.8, "mat": "oak"},
    "towel_return": {"label": "Towel return", "d": 0.5, "h": 0.9, "mat": "steel"},
    "shower": {"label": "Shower, private, with dry area", "d": 2.1, "h": 2.6, "clear": 0.9, "mat": "wet"},
    "shower_acc": {"label": "Accessible shower (seat, rails)", "d": 2.1, "h": 2.6, "clear": 1.5, "mat": "wet"},
    "wc": {"label": "WC cell, full height", "d": 1.8, "h": 2.6, "clear": 0.9, "mat": "wc"},
    "wc_acc": {"label": "Accessible WC (TEK17)", "d": 2.2, "h": 2.6, "clear": 1.5, "mat": "wc"},
    "urinal": {"label": "Urinal + oak screen", "d": 0.45, "h": 1.5, "clear": 0.9, "mat": "wc"},
    "vanity": {"label": "Vanity trough + mirror", "d": 0.6, "h": 0.86, "clear": 0.9, "mat": "stone"},
    "grooming": {"label": "Grooming station (dryers, mirror)", "d": 0.5, "h": 0.86, "clear": 0.9, "mat": "stone"},
    "cleaner": {"label": "Cleaner's cupboard", "d": 0.6, "h": 2.6, "mat": "steel"},
    "robe_hooks": {"label": "Robe hooks + sandal rack", "d": 0.35, "h": 1.8, "mat": "oak"},
    "towel_warmer": {"label": "Towel warmer", "d": 0.45, "h": 1.6, "mat": "steel"},
}
items = []


def put(room, kind, x, y, w, rot=0.0, label=None, **kw):
    """x, y = centre; w = length along the piece; rot = which way its front faces (0 = +y / north, 90 = -x / west, 180 = -y, -90 = +x)."""
    k = KINDS[kind]
    items.append({"id": f"{room}-{kind}-{sum(1 for i in items if i['room'] == room and i['kind'] == kind) + 1}", "room": room, "kind": kind,
                  "label": label or k["label"], "x": round(x, 3), "y": round(y, 3), "w": round(w, 3), "d": kw.pop("d", k["d"]), "rot": rot,
                  "h": k["h"], **({"n": kw.pop("n")} if "n" in kw else {}), **kw})


def lockers(room, x, y, length, rot):
    n = int(length / 0.4 + 1e-6)
    put(room, "lockers", x, y, round(n * 0.4, 3), rot, n=n)
    return n


def changing(room, s):
    """One changing room (Roman: visually unique, luxury): a solid oak block stands against the shared M/W wall, and three ROUND
    locker rooms are carved out of it (3.9 m across), each opening onto the main aisle through a 1.2 m mouth. Oak lockers line each
    drum on the curve (radial: 400 at the face, wider at the back), a round seat in the middle; the oak between the drums is closed
    storage (linen, cleaning). The ring language of Steinringen + Kronen, made into rooms. s = +1 men (block off the north wall,
    aisle along the south), -1 women (mirrored)."""
    wall = 1.425 if s > 0 else 1.575                 # the shared M/W wall face
    depth = 4.2                                      # the block, off the wall
    front = wall - s * depth                         # its face on the aisle
    xs, xe = -27.0, -14.475
    put(room, "oak_block", (xs + xe) / 2, (wall + front) / 2, xe - xs, 0, d=depth, label="Oak block: three round locker rooms carved out")
    R_out, R_in, mouth = 1.95, 1.4, 1.2
    cy = (wall + front) / 2
    sp = (xe - xs) / 3
    n = 0
    for k in range(3):
        cx = xs + sp * (k + 0.5)
        ang = 2 * 3.141592653589793 * R_in
        nl = int((ang - mouth) / 0.4)
        put(room, "locker_ring", cx, cy, 2 * R_out, 0 if s < 0 else 180, d=2 * R_out, r_in=R_in, r_out=R_out, mouth=mouth, n=nl,
            label=f"Round locker room: {nl} lockers on the curve")
        put(room, "round_seat", cx, cy, 0.8, 0, d=0.8, label="Round seat (walnut + wool)")
        n += nl
    # the screen on the vestibule line: hides the drums' mouths from the entry
    put(room, "screen", -14.4, (wall + front - s * 0.25) / 2, abs(depth + 0.25), 90, d=0.1)
    return n, front


nm, tip_m = changing("men-lockers", 1)
nw, tip_w = changing("women-lockers", -1)
# the shoe zones (Roman's hygiene rule): stone from the gallery to the WC room door; beyond the line (x -14.4) barefoot only
put("men-lockers", "floor_zone", (-14.4 - 11.675) / 2, (-4.275 - 0.45) / 2, -11.675 + 14.4, 0, d=-0.45 + 4.275,
    label="Shoe zone: stone, from the gallery to the WC room door; shoes off at the line (x -14.4)")
put("women-lockers", "floor_zone", (-14.4 - 11.675) / 2, (-0.3 + 7.575) / 2, -11.675 + 14.4, 0, d=7.575 + 0.3,
    label="Shoe zone: stone, from the gallery to the WC room door; shoes off at the line (x -14.4)")
# arrival nooks: shoes off, fresh towels
put("men-lockers", "shoe_bench", -13.5, -0.68, 1.6, 180)
put("men-lockers", "towels", -14.15, -1.3, 1.0, -90, d=0.45)
put("women-lockers", "shoe_bench", -13.0, 1.8, 1.6, 0)
put("women-lockers", "towels", -12.0, 3.8, 1.2, 90)
put("women-lockers", "towels", -12.0, 5.2, 1.2, 90)

# ---- wet zones (Roman: toilets physically apart from the washing, never sharing a floor; urinals enclosed). The wash zone
# (barefoot, clean: Fossen, showers, onsen wash places, grooming) is entered only from the changing room through its two openings;
# the WC room beside it has its own floor, drain, extract (negative pressure) and handwash, and its door opens off the arrival nook on
# the shoe side, so gym users in shoes never step into the barefoot zone; toilet slippers at the door for the barefoot (onsen habit).
import json as _json
_m = _json.loads((ROOT / "model" / "building.json").read_text())
def openings(a, b):
    """x ranges of the wall openings between two rooms (from the generated partitions)."""
    w = next(e for e in _m["elements"] if e["id"].startswith("P-F1-") and set(e.get("between", [])) == {a, b})
    x0, sgn = w["from"][0], (1 if w["to"][0] > w["from"][0] else -1)
    return sorted([sorted([round(x0 + sgn * o["s"][0], 3), round(x0 + sgn * o["s"][1], 3)]) for o in w["openings"]])
WASH_X = (-29.25, -19.475)    # wash zone: west facade face .. the WC room wall
WC_X = (-19.325, -11.675)     # WC room
def wash(room, s):
    back = -9.225 if s > 0 else 11.9               # the wall the cells stand against
    front = -4.275 if s > 0 else 7.725             # the changing-room wall (with the two openings)
    r = 0 if s > 0 else 180
    dsh = 2.1 if s > 0 else 1.9                    # shower + dry area (the women's zone is 0.8 m shallower)
    put(room, "fossen", WASH_X[0] + 1.2, back + s * dsh / 2, 2.4, r, d=dsh)  # the experience shower, west end, under the clerestory
    put(room, "shower_acc", WASH_X[1] - 0.9, back + s * dsh / 2, 1.8, r, d=dsh)
    x0, x1 = WASH_X[0] + 2.4, WASH_X[1] - 1.8
    n_sh = 5; w_sh = round((x1 - x0) / n_sh, 4)
    for k in range(n_sh):
        put(room, "shower", x0 + w_sh * (k + 0.5), back + s * dsh / 2, w_sh, r, d=dsh)
    rv = 180 if s > 0 else 0
    (o1a, o1b), (o2a, o2b) = openings(room.replace("wet", "lockers"), room)
    put(room, "grooming", (WASH_X[0] + o1a) / 2 - 0.05, front - s * 0.25, round(o1a - WASH_X[0] - 0.2, 2), rv)
    for k in range(3):
        put(room, "wash_station", o1b + 0.1 + (o2a - o1b - 0.2) * (k + 0.5) / 3, front - s * 0.5, 0.95, rv, d=1.0)
    put(room, "vanity", (o2b + WASH_X[1]) / 2, front - s * 0.3, round(WASH_X[1] - o2b - 0.1, 2), rv, n=2)
    return (o1a, o1b), (o2a, o2b)

def wc_room(room, s):
    back = -9.225 if s > 0 else 11.9
    front = -4.275 if s > 0 else 7.725
    r = 0 if s > 0 else 180; rv = 180 if s > 0 else 0
    put(room, "floor_zone", sum(WC_X) / 2, (back + front) / 2, WC_X[1] - WC_X[0], 0, d=abs(front - back),
        label="WC floor: own tile, drain + extract (negative pressure); slippers at the door")
    door = openings(room.replace("wc", "lockers"), room)[0]
    put(room, "wc_acc", WC_X[1] - 1.0, back + s * 1.1, 2.0, r, d=2.2)
    if s > 0:   # men: 4 WC cells + the urinals in their own enclosed room at the west end
        uw = -17.7
        n_wc = 4; w_wc = round((WC_X[1] - 2.0 - (uw + 0.05)) / n_wc, 4)
        for k in range(n_wc):
            put(room, "wc", uw + 0.05 + w_wc * (k + 0.5), back + 0.9, w_wc, r, d=1.8)
        ur_top = -6.3
        put(room, "partition", uw, (back + ur_top) / 2, abs(ur_top - back), 90, d=0.1, label="Urinal room wall, full height, tiled")
        put(room, "partition", (WC_X[0] + uw) / 2 + 0.45, ur_top, uw - WC_X[0] - 0.9, 0, d=0.1, label="Urinal room wall (entry gap at its west end)")
        for k in range(3):
            put(room, "urinal", WC_X[0] + 0.225, back + 0.55 + k * 0.8, 0.6, -90)
        put(room, "floor_zone", (WC_X[0] + uw) / 2, (back + ur_top) / 2, uw - WC_X[0], 0, d=abs(ur_top - back), label="Urinal room: own drain")
        put(room, "vanity", WC_X[1] - 0.3, (-7.025 + front) / 2, 2.2, 90, n=3, label="Handwash (before you leave)")  # on the gallery wall
        put(room, "cleaner", -18.75, front - 0.3, 1.0, rv)
        put(room, "slipper_rack", door[0] - 0.7, front - 0.2, 1.0, rv)
    else:       # women: 6 WC cells
        n_wc = 6; w_wc = round((WC_X[1] - 2.0 - WC_X[0]) / n_wc, 4)
        for k in range(n_wc):
            put(room, "wc", WC_X[0] + w_wc * (k + 0.5), back - 0.9, w_wc, r, d=1.8)
        put(room, "vanity", -17.3, front + 0.3, 3.4, rv, n=4, label="Handwash (before you leave)")
        put(room, "cleaner", (door[1] + WC_X[1]) / 2, front + 0.3, 1.0, rv)
        put(room, "slipper_rack", door[0] - 0.7, front + 0.2, 1.0, rv)

ops_m = wash("men-wet", 1); wc_room("men-wc", 1)
ops_w = wash("women-wet", -1); wc_room("women-wc", -1)

# Bekken, the stream (Roman: rivers flowing round the edges, moving water; onsen x Nordic, more Nordic): it rises at a spring basin
# just past the WC door, runs along the edge of the changing room's aisle at the foot of the wash-zone wall (granite slabs carry the
# floor over it at the openings), turns down the west side of the westmost opening into the wash zone and ends in Fossen's front
def stream(room_c, room_w, s, ops):
    y = (-4.275 + 0.25) if s > 0 else (7.575 - 0.25)
    ye = -7.0 if s > 0 else 9.85
    xw = ops[0][0] + 0.17
    pts_c = [[-15.3, y], [xw + 0.3, y], [xw, y - s * 0.3]]
    pts_w = [[xw, y - s * 0.3], [xw, ye]]
    put(room_c, "spring_basin", -15.0, y, 0.6, 0, d=0.6)
    items.append({"id": f"{room_c}-stream", "room": room_c, "kind": "stream", "label": KINDS["stream"]["label"], "pts": pts_c, "width": 0.35})
    items.append({"id": f"{room_w}-stream", "room": room_w, "kind": "stream", "label": KINDS["stream"]["label"], "pts": pts_w, "width": 0.35})
    for xa, xb in ops:
        put(room_c, "bridge_slab", (xa + xb) / 2, y, xb - xa + 0.2, 0, d=0.6)
stream("men-lockers", "men-wet", 1, ops_m)
stream("women-lockers", "women-wet", -1, ops_w)
# towel returns: slots in the oak block's aisle face, between the drums
for room, s in (("men-lockers", 1), ("women-lockers", -1)):
    blk = next(i for i in items if i["room"] == room and i["kind"] == "oak_block")
    fy = blk["y"] - s * blk["d"] / 2
    for xr in (-22.825, -18.65):
        put(room, "towel_return", xr, fy - s * 0.02, 0.6, 180 if s > 0 else 0, d=0.04, label="Towel return slot in the oak block")

# ---- hygiene tech (Roman, 2026-10-13: robots that keep cleaning, something that sanitises your shoes as you walk in, technology
# that keeps the floors clean): 'Vaskebjørn' (the raccoon, literally 'wash bear'), little cleaning robots, one per zone and never
# crossing zones (a lingon ring = WC rooms, fjord = wash zones, as hospitals colour-code). Each lives in its own dock and cleans
# when its zone is empty (occupancy sensors), keeping to the walls; anyone comes in, it goes home. UV-C sole plates at every way in
# from the gallery and outside the WC doors; far-UVC (222 nm, safe with people) in the WC ceilings; self-cleaning photocatalytic
# tile in the WC rooms.
for room, s_ in (("men-wc", 1), ("women-wc", -1)):
    cl = next(i for i in items if i["room"] == room and i["kind"] == "cleaner")
    put(room, "robot_dock", cl["x"] + 0.5 * (1 if s_ > 0 else -1) * 0 + (0.75 if s_ > 0 else -0.75), cl["y"], 0.5, cl["rot"], label="Robot dock: a floor flap into the cleaner's cupboard (auto-empty + refill)")
    put(room, "robot", -16.2, -6.6 if s_ > 0 else 9.2, 0.42, 30, d=0.42, label="Vaskebjørn (WC room, lingon ring)")
    for x in (-17.0, -13.2):
        put(room, "far_uvc", x, -6.4 if s_ > 0 else 9.0, 0.25, 0, d=0.25)
for room, s_ in (("men-wet", 1), ("women-wet", -1)):
    v = next(i for i in items if i["room"] == room and i["kind"] == "vanity")
    put(room, "robot_dock", v["x"], v["y"], 0.5, v["rot"], label="Robot garage recessed under the vanity")
    put(room, "robot", -24.6, -6.5 if s_ > 0 else 9.2, 0.42, -20, d=0.42, label="Vaskebjørn (wash zone, fjord ring)")
# UV-C sole plates: the men's entry, the women's vestibule entry, and in front of each WC door on the shoe side
put("men-lockers", "uvc_plate", -12.15, -3.145, 1.5, -90, d=0.9)
put("women-lockers", "uvc_plate", -12.15, 0.45, 1.5, -90, d=0.9)
put("men-lockers", "uvc_plate", -13.5, -3.85, 1.0, 180, d=0.7)
put("women-lockers", "uvc_plate", -13.5, 7.15, 1.0, 0, d=0.7)

# sauna lobby annex (shared): robes + sandals along the west wall, a towel warmer, a bench
put("sauna-lobby", "robe_hooks", -35.325 + 0.175, 1.5, 4.2, -90)
put("sauna-lobby", "towel_warmer", -31.0, 4.375 - 0.225, 1.2, 180)
put("sauna-lobby", "bench", -32.6, -1.375 + 0.3, 2.4, 0, d=0.45)

data = {"note": "F1 locker rooms: the 2D layout (see tools/locker_layout.py for the rules). Edited in blueprint/layout.html; x, y = centre in "
                "project metres, w along the piece, d front-to-back, rot = the way its front faces (0 = north).",
        "rooms": ["men-lockers", "men-wet", "men-wc", "women-lockers", "women-wet", "women-wc", "sauna-lobby", "gallery"],
        "view": [-36.6, -13.4, 31.0, 23.6], "kinds": KINDS, "items": items}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, indent=1))
print(f"wrote {OUT.relative_to(ROOT)}: {len(items)} items; lockers men {nm}, women {nw}")

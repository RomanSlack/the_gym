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
# arrival nooks: shoes off, fresh towels
put("men-lockers", "shoe_bench", -13.5, -0.68, 1.6, 180)
put("men-lockers", "towels", -14.15, -1.3, 1.0, -90, d=0.45)
put("women-lockers", "shoe_bench", -13.0, 1.8, 1.6, 0)
put("women-lockers", "towels", -12.0, 3.8, 1.2, 90)
put("women-lockers", "towels", -12.0, 5.2, 1.2, 90)

# ---- wet zones
def wet(room, s):
    """s = +1 men (cells on the south wall, vanities on the north), -1 women (cells on the north facade, vanities on the south)."""
    back = -9.225 if s > 0 else 11.9               # the wall the cells stand against
    front = -4.275 if s > 0 else 7.725             # the changing-room wall (with the three openings)
    r = 0 if s > 0 else 180                        # cells face away from their back wall
    x = -11.675
    put(room, "wc_acc", x - 1.0, back + s * 1.1, 2.0, r, d=2.2); x -= 2.0
    nwc = 4 if s > 0 else 6
    for _ in range(nwc):
        put(room, "wc", x - 0.5, back + s * 0.9, 1.0, r, d=1.8); x -= 1.0
    put(room, "shower_acc", x - 0.9, back + s * 1.05, 1.8, r); x -= 1.8
    put(room, "fossen", -29.25 + 1.2, back + s * 1.05, 2.4, r)             # the experience shower at the west end, under the clerestory
    n_sh = 7 if s > 0 else 5
    w_sh = round((x - (-29.25 + 2.4)) / n_sh, 4)
    for _ in range(n_sh):
        put(room, "shower", x - w_sh / 2, back + s * 1.05, w_sh, r); x -= w_sh
    rv = 180 if s > 0 else 0                        # vanities face into the zone, away from the changing-room wall
    for xa, xb in ((-25.57, -21.42), (-19.62, -15.48)):
        put(room, "vanity", (xa + xb) / 2, front - s * 0.3, 3.6, rv, n=4)
    put(room, "grooming", (-29.25 - 27.37) / 2, front - s * 0.25, 1.6, rv)
    put(room, "cleaner", (-13.68 - 11.675) / 2, front - s * 0.3, 1.0, rv)
    if s > 0:  # urinals on the east wall, between the accessible WC and the changing-room wall
        for k in range(3):
            put(room, "urinal", -11.675 - 0.225, -6.6 + k * 0.8, 0.6, -90 + 180)
    put(room, "towel_return", -13.68 - 0.1 - 0.4, front - s * 0.25 if s > 0 else front - s * 0.25, 0.8, rv)


wet("men-wet", 1)
wet("women-wet", -1)
# onsen part, made Nordic: seated wash places replace the first vanity trough in each wet zone (the west one, near Fossen)
for room in ("men-wet", "women-wet"):
    v = next(i for i in items if i["room"] == room and i["kind"] == "vanity")
    items.remove(v)
    for k in range(4):
        put(room, "wash_station", -25.57 + 0.15 + 0.5 + k * 0.95, v["y"] + (-0.2 if room == "men-wet" else 0.2), 0.9, v["rot"], d=1.0)

# Bekken, the stream (Roman: rivers flowing round the edges, moving water; onsen x Nordic, more Nordic): it rises at a spring basin
# by each entry, runs along the edge of the changing room's aisle at the foot of the wet-zone wall, turns through the westmost
# opening into the wet zone and ends in Fossen. Granite slabs carry the floor over it at the openings.
def stream(room_c, room_w, s, pts_c, pts_w):
    put(room_c, "spring_basin", pts_c[0][0] + 0.35, pts_c[0][1], 0.6, 0, d=0.6)
    items.append({"id": f"{room_c}-stream", "room": room_c, "kind": "stream", "label": KINDS["stream"]["label"], "pts": pts_c, "width": 0.35})
    items.append({"id": f"{room_w}-stream", "room": room_w, "kind": "stream", "label": KINDS["stream"]["label"], "pts": pts_w, "width": 0.35})
    for xa, xb in ((-15.48, -13.68), (-21.42, -19.62), (-27.37, -25.57)):
        put(room_c, "bridge_slab", (xa + xb) / 2, pts_c[0][1], xb - xa + 0.2, 0, d=0.6)
ym = -4.275 + 0.25; yw = 7.575 - 0.25
# into the wet zone down the west side of the westmost opening (x -27.2), straight into Fossen's front: no one crosses it there
stream("men-lockers", "men-wet", 1, [[-14.2, ym], [-26.9, ym], [-27.2, -4.3]], [[-27.2, -4.3], [-27.2, -7.0]])
stream("women-lockers", "women-wet", -1, [[-14.2, yw], [-26.9, yw], [-27.2, 7.7]], [[-27.2, 7.7], [-27.2, 9.6]])

# sauna lobby annex (shared): robes + sandals along the west wall, a towel warmer, a bench
put("sauna-lobby", "robe_hooks", -35.325 + 0.175, 1.5, 4.2, -90)
put("sauna-lobby", "towel_warmer", -31.0, 4.375 - 0.225, 1.2, 180)
put("sauna-lobby", "bench", -32.6, -1.375 + 0.3, 2.4, 0, d=0.45)

data = {"note": "F1 locker rooms: the 2D layout (see tools/locker_layout.py for the rules). Edited in blueprint/layout.html; x, y = centre in "
                "project metres, w along the piece, d front-to-back, rot = the way its front faces (0 = north).",
        "rooms": ["men-lockers", "men-wet", "women-lockers", "women-wet", "sauna-lobby", "gallery"],
        "view": [-36.6, -13.4, 31.0, 23.6], "kinds": KINDS, "items": items}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, indent=1))
print(f"wrote {OUT.relative_to(ROOT)}: {len(items)} items; lockers men {nm}, women {nw}")

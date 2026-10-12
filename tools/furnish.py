"""Stage 5b: furniture, fixtures and doors for the reception + the cafe south of it (Roman, 2026-10-11). Every piece is designed
here (construction/furniture.py builds the geometry); nothing is downloaded but textures.

Design: Nordic mid-century, regional, minimal. Light oak, cream boucle, cognac leather, sheepskin, light honed stone, dark
bronze / blackened steel only for small hardware. Sizes are real (seat 0.45, bar 1.05, counter 0.90, tables 0.74, desk 1.05 / 0.76).
Layout (E1 = 0.12):
  - entrance: a glass vestibule (vindfang, needed for heat in a Norwegian winter): outer sliding doors in the east facade
    between two mullions, inner sliding doors 2.5 m in, glass sides, an oak slat lid at 3.0 m; a boot bench inside it (shoes off)
  - reception desk backed onto the slatted core wall, facing the doors: 4.6 m, slatted oak front, light stone ledge at 1.05,
    accessible low end at 0.76, staff side 1.1 m deep; three opal pendants over it
  - a two-chair waiting nook by the window, north of the vestibule
  - core E: hidden slatted stair door (the slats run over it), bronze lift doors with a call plate
  - public WCs: privacy baffle screens inside the open entries (VISION: airport-style, no door)
  - daycare: framed glass secure door in the glass wall
  - cafe: the round island bar (outer bar 1.05 with stools, staff ring, inner back counter 0.90 with espresso machine + grinder),
    a big oak + linen ring pendant over it; tables for four by the east glass; a long communal table + benches and a
    sofa corner on a wool rug by the lounge-bridge entrance; a window counter with stools along the south glass
python3 tools/furnish.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402
if len(sys.argv) > 2 and sys.argv[1] == '--art':
    _m = modelio.load(); _m.setdefault('interior', {})['reception_art'] = sys.argv[2]; modelio.save(_m)

m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}
E1 = lv["E1"]
F = []


def put(kind, x, y, rot=0.0, zone="reception", **kw):
    F.append({"id": f"{kind}-{len(F):03d}", "kind": kind, "level": "E1", "at": [round(x, 3), round(y, 3)], "z": E1, "rot_deg": rot, "zone": zone, **kw})


# ---- entrance: facade opening + vestibule (front of every piece = +y in its own frame; rot turns it)
by_id = {e["id"]: e for e in m["elements"]}
fac = by_id["EN-G-E1-E-0"]  # facade glass x = 30.5 from y -9.5; mullions at s 19.566 / 22.011 frame the doors
fac["openings"] = [{"s": [19.60, 21.976], "z": [E1, round(E1 + 2.6, 2)], "type": "door", "note": "main entrance: automatic sliding doors"}]
put("sliding_doors", 30.5, -9.5 + (19.60 + 21.976) / 2, rot=90, zone="entrance", width=2.376, height=2.6, note="outer automatic sliding doors (vestibule)")
# the vestibule (vindfang) stands OUTSIDE, under the 2.5 m eave: the facade doors are its inner doors (Roman: keep the hall free)
VY0, VY1, VX0, VX1 = 9.3, 13.3, 30.5, 32.9
put("porch_floor", (VX0 + VX1) / 2, (VY0 + VY1) / 2, zone="entrance", size=[VX1 - VX0 + 0.1, VY1 - VY0 + 0.1], note="honed stone porch floor on a concrete plinth")
put("glass_screen", VX1, (VY0 + VY1) / 2, rot=90, zone="entrance", width=VY1 - VY0, height=3.0, door=2.2, note="outer glass screen with automatic sliding doors")
put("glass_screen", (VX0 + VX1) / 2, VY0, rot=0, zone="entrance", width=VX1 - VX0, height=3.0, door=0.0, note="vestibule side glass")
put("glass_screen", (VX0 + VX1) / 2, VY1, rot=0, zone="entrance", width=VX1 - VX0, height=3.0, door=0.0, note="vestibule side glass")
put("vestibule_lid", (VX0 + VX1) / 2, (VY0 + VY1) / 2, zone="entrance", size=[VX1 - VX0, VY1 - VY0], height=3.0, note="oak slat lid at 3.0 m, under the eave")
# entrance matting in two zones (Roman: the stone stays, but grit and snow need a mat): an open steel scraper grate in the
# vestibule floor at the outer doors, then a textile wiper mat in a flush well inside the facade doors (well cut in tools/interior.py)
put("entrance_mat", 32.05, (VY0 + VY1) / 2, zone="entrance", size=[1.5, 2.6], style="scraper", note="scraper grate over a drained pit, blackened steel")
put("entrance_mat", (28.3 + 30.45) / 2, (9.85 + 12.75) / 2, zone="entrance", size=[2.15, 2.9], style="wiper",
    note="recessed wiper mat: charcoal textile ribs with rubber scraper strips in a blackened-steel frame, flush with the stone")
put("boot_bench", (VX0 + VX1) / 2, VY0 + 0.32, rot=0, zone="entrance", length=1.8, note="boot bench: shoes off, as at home in Norway")

# ---- reception
put("reception_desk", 25.7, 11.3, rot=-90, length=4.6, note="desk faces the doors (east); staff side to the slatted core wall")
ART = {"valley": "docs/art/artvalleyoil_0.png", "abstract": "docs/art/artabstracthills_0.png", "mist": "docs/art/artmistforest_0.png"}
art_pick = m.get("interior", {}).get("reception_art", "valley")
put("canvas_art", 24.22, 11.3, rot=-90, width=6.0, height=2.9, image=str(ROOT / ART[art_pick]),
    note=f"painting behind the desk ({art_pick}), generated with gpt-image-2, stretched canvas in an oak float frame")
# desk + painting lighting (Roman: the pendants blocked the painting): slim wall lights either side of the canvas,
# downlights in the ceiling over the desk, two gallery spots washing the painting. All in blackened steel.
for y in (8.17, 14.47):  # in the gaps between the canvas (8.3-14.3) and the stair door / lift frames
    put("wall_light", 24.22, y, rot=-90, light={"type": "AREA", "energy": 35, "size": 0.05, "size_y": 0.8, "offset": [0, 0.06, 2.75], "aim": None, "color": [1.0, 0.82, 0.62]},
        note="slim vertical wall light, 60 x 900, glows up and down along the slats")
for y in (9.9, 11.3, 12.7):
    put("downlight", 25.75, y, z_ceiling=5.02, light={"type": "SPOT", "energy": 220, "spot_deg": 50, "offset": [0, 0, 4.85], "aim": [25.75, y, 0.12], "color": [1.0, 0.86, 0.7]},
        note="recessed-look downlight over the desk, 2700 K")
for y in (8.9, 10.5, 12.1, 13.7):  # four soft wall-washers, each on its own quarter of the canvas: an even wash, no hotspot
    put("gallery_spot", 26.9, y, z_ceiling=5.02, light={"type": "SPOT", "energy": 70, "spot_deg": 75, "blend": 1.0, "radius": 0.15, "offset": [0, 0, 4.85],
        "aim": [24.25, y, 2.6], "color": [1.0, 0.9, 0.78]}, note="soft wall-washer on the painting")
put("lounge_chair", 28.7, 14.55, rot=-60, zone="reception")
put("lounge_chair", 28.7, 15.65, rot=-120, zone="reception")
put("side_table", 29.45, 15.1, zone="reception")
put("door_slatted", 24.19, 7.55, rot=-90, width=1.0, height=2.3, note="hidden stair door: the oak slats run over the leaf")
put("lift_doors", 24.19, 15.3, rot=-90, width=1.2, height=2.3, note="lift: dark bronze centre-opening doors, call plate")
put("glass_door", 27.4, 16.2, rot=0, width=1.6, height=2.3, note="daycare secure door (glass, staff / parent release)")
by_id["G-E1-daycare"]["mullions"] = [1.3, 2.6, 4.2, 5.35]  # mullions clear the door

# ---- WC baffles (open entries, VISION: no doors on the public WCs); 2.2 wide leaves 0.9-1.0 m to walk round either end
put("baffle_screen", 14.2, 7.9, rot=0, zone="wc", width=2.2, height=2.4, note="women's WC privacy baffle")
put("baffle_screen", 18.6, 7.9, rot=0, zone="wc", width=2.2, height=2.4, note="men's WC privacy baffle")

# ---- public WCs (VISION "Wet rooms"): tile faces (interior.py) women x 12.22 / 16.305, men x 16.495 / 20.655, north y 16.105
WARM = [1.0, 0.86, 0.7]
def wc_room(stall_x, stall_rot, stall_y, n_stalls, van_x, van_rot, acc_cx, acc_pan, acc_door, store_cx, aisle_x, urinal_y=None, tag=""):
    put("wc_cells", stall_x, stall_y, rot=stall_rot, zone="wc", n=n_stalls, w=1.1, depth=1.65, style="wc", note=f"{tag} WC cells: oak boxes with lids")
    out = 1 if stall_rot == -90 else -1  # +x or -x into the room
    for k in range(n_stalls):
        cy = stall_y + (n_stalls / 2 - k - 0.5) * 1.1 * (1 if stall_rot == -90 else -1)
        put("cell_light", stall_x + out * 0.85, cy, zone="wc", z_ceiling=2.6,
            light={"type": "POINT", "energy": 18, "radius": 0.05, "offset": [0, 0, 2.5], "color": WARM}, note="light in the cell lid")
    put("wc_cells", acc_cx, 16.105, rot=180, zone="wc", n=1, w=2.5, depth=2.4, style="accessible", door_at=acc_door, pan_at=acc_pan,
        note=f"{tag} accessible WC: its own door, rails, basin, fold-down changing table")
    put("cell_light", acc_cx, 14.9, zone="wc", z_ceiling=2.6, light={"type": "POINT", "energy": 35, "radius": 0.05, "offset": [0, 0, 2.5], "color": WARM})
    put("wc_cells", store_cx, 16.105, rot=180, zone="wc", n=1, w=1.4, depth=1.0, style="store", note="cleaner's cupboard")
    put("vanity", van_x, 10.7, rot=van_rot, zone="wc", length=3.0, n=3, note=f"{tag} stone trough vanity, mirror, light")
    vin = 1 if van_rot == -90 else -1
    put("light_only", van_x + vin * 0.06, 10.7, zone="wc",
        light={"type": "AREA", "energy": 60, "size": 2.9, "size_y": 0.04, "offset": [0, 0, 2.2], "aim": [van_x + vin * 1.2, 10.7, 0.9], "color": WARM},
        note="linear light above the mirror (the fitting is part of the vanity)")
    for y in (8.6, 11.0, 13.0):
        put("downlight", aisle_x, y, zone="wc", z_ceiling=5.02,
            light={"type": "SPOT", "energy": 200, "spot_deg": 60, "offset": [0, 0, 4.85], "aim": [aisle_x, y, 0.12], "color": WARM})
    if urinal_y is not None:
        put("urinals", 20.655, urinal_y, rot=90, zone="wc", n=3, pitch=0.75, note="urinals with oak screens, one at child height")

wc_room(12.22, -90, 11.25, 4, 16.305, 90, 13.5, 0.75, -0.6, 15.55, 14.8, tag="women's")
wc_room(20.655, 90, 12.45, 2, 16.495, -90, 19.405, -0.745, 0.705, 17.25, 18.0, urinal_y=10.0, tag="men's")

# ---- cafe: island bar + ring pendant
cx, cy = 21.25, -1.35
put("cafe_island", cx, cy, zone="cafe", r_out=3.5, gap_deg=225, note="round island bar: outer bar, staff ring, back counter")
put("ring_pendant", cx, cy, zone="cafe", r=3.15, hang=3.35, note="oak + linen ring light over the bar")
R = 3.5 + 0.38
n = int(2 * math.pi * R / 0.66)
for k in range(n):
    a = 360 * k / n
    if abs(((a - 225) + 180) % 360 - 180) < 14:
        continue
    ar = math.radians(a)
    put("bar_stool", cx + R * math.cos(ar), cy + R * math.sin(ar), rot=a + 90, zone="cafe", height=0.76)  # seat faces the bar
# tables for four by the east glass
for x in (26.7, 29.0):
    for y in (-7.2, -4.3, -1.4, 1.5):
        put("cafe_table", x, y, zone="cafe")
        for d in (0, 90, 180, 270):  # each chair faces the table: rot = d + 90
            put("dining_chair", x + 0.62 * math.cos(math.radians(d)), y + 0.62 * math.sin(math.radians(d)), rot=d + 90, zone="cafe")
# communal table + benches by the bridge entrance, sofa corner on a rug
put("communal_table", 14.3, -5.6, rot=90, zone="cafe", length=4.0)
put("bench", 13.62, -5.6, rot=90, zone="cafe", length=3.6)
put("bench", 14.98, -5.6, rot=-90, zone="cafe", length=3.6)
put("rug", 15.0, 0.6, zone="cafe", size=[2.6, 3.0])
put("sofa", 13.4, 0.6, rot=-90, zone="cafe", length=2.2)
put("lounge_chair", 16.55, 0.0, rot=60, zone="cafe")
put("lounge_chair", 16.55, 1.25, rot=120, zone="cafe")
put("coffee_table", 15.0, 0.6, zone="cafe")
# window counter along the south glass
put("window_counter", 21.25, -8.95, rot=0, zone="cafe", length=11.0)
for k in range(15):
    put("bar_stool", 16.15 + k * 0.73, -8.35, rot=180, zone="cafe", height=0.76)

m["furnishings"] = F
# the old schematic fixtures for E1 are replaced by real pieces (drawings keep them as symbols)
for f in m.get("fixtures", []):
    if f["id"] == "reception_desk":
        f["rect"] = [25.3, 9.0, 26.1, 13.6]
modelio.save(m)
print("furnishings:", len(F), {k: sum(1 for f in F if f["kind"] == k) for k in sorted({f["kind"] for f in F})})

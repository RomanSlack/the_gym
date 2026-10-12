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
COL = ["lingon", "cloud", "moss", "fjord", "heather"]
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

# ---- daycare upper floor (VISION "Daycare: playful, still Nordic"): play and colour from the furniture, light shell
DCART = {"forest": "docs/art/artdcforest_0.png", "lake": "docs/art/artdclake_0.png"}
def dl(x, y, energy=200, zone="daycare"):
    put("downlight", x, y, zone=zone, z_ceiling=5.02, light={"type": "SPOT", "energy": energy, "spot_deg": 60, "offset": [0, 0, 4.85], "aim": [x, y, 0.12], "color": WARM})

# round stair down to the lower daycare: guards round the opening + up both edges of the helix (the way on stays open)
# tube slide inside the stair's eye (Roman): find where the stair runs alongside the tube at an adult's reach -> rescue hatches
# in the tube + lockable gates in the stair's inner balustrade opposite them
T_TOP, T_TURN, TZ0, TZ1 = 300.0, 690.0, 0.36, -5.39
tz = lambda th: TZ0 + (TZ1 - TZ0) * (th - T_TOP) / T_TURN
sz = lambda al: -6.13 + (int((al - 90) / 15) + 1) * 6.13 / 35
HATCH, GATES = [], []
for th in range(int(T_TOP) + 20, int(T_TOP + T_TURN) - 20, 2):
    for al in (th - 360 * j for j in range(-1, 4)):
        if 95 <= al <= 600 and 0.45 <= tz(th) - sz(al) <= 0.95 and all(abs(th - h) >= 150 for h in HATCH):
            HATCH.append(th); GATES.append(al)
put("stair_guard", 15.7, 24.2, zone="daycare", gaps=[[233.0, 262.0], [290.0, 310.0]], gates=GATES, r_in=1.45,
    note="child-safe guards: 1.2 m oak staves round the opening, balustrades on the helix, rescue gates by the tube's hatches")
put("tube_slide", 15.7, 24.2, zone="daycare", hatches=HATCH,
    note="tube slide down the stair's eye: stainless below, clear polycarbonate above, rescue hatches, oak bridge at the top")
# the 'tree house' play loft against the north glass (forest view from the deck), den underneath
put("play_loft", 14.5, 30.55, rot=180, zone="daycare", length=4.0, D=2.6, deck=1.6, note="oak play loft: deck 1.6 m, gable frame, stair, slide, den")
# craft tables at child height
for (tx, ty, tc) in ((18.0, 27.4, "cloud"), (18.6, 31.0, "moss")):
    put("kid_table", tx, ty, zone="daycare", colour=tc)
    for k in range(5):
        a = 90 + 72 * k
        put("kid_chair", tx + 0.78 * math.cos(math.radians(a)), ty + 0.78 * math.sin(math.radians(a)), rot=a + 90, zone="daycare", colour=COL[(k + 2) % 5])
# reading: the den under the loft is the reading nook (cushions + a felt curtain); a low face-out bookshelf beside it
put("low_shelf", 17.2, 33.0, rot=180, zone="daycare", length=1.6, h=0.8, note="face-out picture books by the den")
# the line between the kids' (3-12) and toddlers' (0-3) zones at x 21.25: low shelves, a gate, the story wall with the forest painting
put("low_shelf", 21.25, 23.5, rot=90, zone="daycare", length=3.8, h=0.8)
put("gate", 21.25, 25.9, rot=90, zone="daycare", width=0.9)
put("story_wall", 21.25, 28.6, rot=90, zone="daycare", length=4.4, note="freestanding: the forest painting to the kids, books + pin board to the toddlers")
put("canvas_art", 21.25 - 0.06, 28.6, rot=90, zone="daycare", width=4.0, height=2.0, image=str(ROOT / DCART["forest"]),
    note="'forest friends', gpt-image-2 gouache, at children's eye level (0.45-2.45)", )
F[-1]["z0"] = 0.45
# name plaques under each animal (Roman: English, a little educational); positions in image fractions (u from left, v from top)
put("art_labels", 21.25 - 0.06, 28.6, rot=90, zone="daycare", width=4.0, height=2.0, z0=0.45, size=0.034,
    labels=[[0.075, 0.725, "Red squirrel"], [0.35, 0.745, "Moose calf"], [0.235, 0.85, "Hedgehog"], [0.46, 0.82, "Red fox"],
            [0.665, 0.335, "Tawny owl"], [0.83, 0.88, "Mountain hare"], [0.195, 0.29, "Willow tit"], [0.93, 0.44, "Bullfinch"]],
    note="educational name plaques on the forest painting")
put("low_shelf", 21.25, 32.0, rot=90, zone="daycare", length=2.2, h=0.8)
# toddlers: soft play, cushions, the lake painting low on the nursing room wall
put("soft_play", 24.8, 26.4, zone="daycare", note="felt-covered foam steps, ramp, hump, arch on a round mat")
put("canvas_art", 28.75, 29.225, rot=180, zone="daycare", width=3.0, height=1.5, image=str(ROOT / DCART["lake"]), note="'moose by the lake', low for toddlers")
F[-1]["z0"] = 0.4
put("art_labels", 28.75, 29.225, rot=180, zone="daycare", width=3.0, height=1.5, z0=0.4, size=0.03,
    labels=[[0.19, 0.64, "Moose"], [0.31, 0.82, "Moose calf"], [0.69, 0.865, "Mallard ducks"]], note="name plaques on the lake painting")
put("rug_round", 28.7, 27.8, zone="daycare", d=2.2, colour="oat")
for (cx, cy, c) in ((28.0, 28.0, "heather"), (28.9, 27.4, "cloud"), (29.5, 28.3, "fjord")):
    put("floor_cushion", cx, cy, zone="daycare", colour=c, r=0.36)
put("low_shelf", 24.0, 32.9, rot=180, zone="daycare", length=3.0, h=0.6)
# felt clouds over both zones (acoustics + colour from above), offset from the downlight grid
for (cx, cy, c, sc) in ((18.0, 29.2, "oat", 1.1), (19.6, 24.0, "cloud", 0.9), (14.8, 22.4, "fjord", 0.8), (25.8, 23.9, "heather", 1.1),
                        (23.4, 30.4, "oat", 1.0), (27.4, 26.2, "moss", 0.9), (19.9, 32.2, "lingon", 0.8)):
    put("felt_cloud", cx, cy, zone="daycare", colour=c, s=sc, hang=round(3.4 + (cx * 7 % 5) / 10, 2))
for x in (13.6, 17.4, 21.2, 25.0, 28.6):
    for y in (22.7, 26.0, 29.2, 32.3):
        if not (27.0 < x and y > 29.3):
            dl(x, y)
# wardrobe (check-in): cubbies on the west wall, drying cabinets, a parents' bench on the glass, a check-in stand by the door
put("cubbies", 24.095, 18.1, rot=-90, zone="daycare", length=3.4, n=8, note="a cubby per child, felt backs, pegs, boot slots")
for y in (20.2, 20.82):
    put("drying_cabinet", 24.095, y, rot=-90, zone="daycare", note="drying cabinet for wet outdoor clothes")
put("boot_bench", 30.18, 18.7, rot=90, zone="daycare", length=2.0, note="parents' bench along the glass")
put("side_table", 28.95, 17.0, zone="daycare", note="check-in stand (tablet)")
for y in (17.6, 19.8):
    dl(27.2, y, 160)
# children's WC (safeguarding glass to the play zone): low cells, a child-height trough, changing unit, accessible WC
put("kid_wc_cells", 18.9, 16.295, rot=0, zone="daycare", n=4, w=0.85, depth=1.2, note="children's WCs: low screens, coloured half doors")
put("vanity", 17.095, 19.0, rot=-90, zone="daycare", length=2.4, n=3, top=0.55, note="children's trough basin at 0.55, low mirror")
put("light_only", 17.16, 19.0, zone="daycare", light={"type": "AREA", "energy": 45, "size": 2.3, "size_y": 0.04, "offset": [0, 0, 1.9], "aim": [18.3, 19.0, 0.7], "color": WARM})
put("changing_unit", 23.905, 19.95, rot=90, zone="daycare", length=1.8, note="changing unit with steps + hand shower")
put("wc_cells", 22.65, 16.345, rot=0, zone="daycare", n=1, w=2.5, depth=2.4, style="accessible", door_at=-0.6, pan_at=0.7, note="accessible adult WC")
put("cell_light", 22.65, 17.55, zone="daycare", z_ceiling=2.6, light={"type": "POINT", "energy": 35, "radius": 0.05, "offset": [0, 0, 2.5], "color": WARM})
for x in (18.6, 21.2):
    dl(x, 19.6, 160)
# staff room: kitchenette on the (solid) facade wall, a table for four, a staff WC cell
put("kitchenette", 12.22, 17.9, rot=-90, zone="daycare", length=2.4)
put("cafe_table", 14.3, 18.6, zone="daycare")
for d in (0, 90, 180, 270):
    put("dining_chair", 14.3 + 0.62 * math.cos(math.radians(d)), 18.6 + 0.62 * math.sin(math.radians(d)), rot=d + 90, zone="daycare")
put("wc_cells", 16.15, 16.275, rot=0, zone="daycare", n=1, w=1.4, depth=1.8, style="wc", door_at=0.0, note="staff WC")
put("lounge_chair", 16.2, 20.3, rot=200, zone="daycare")
dl(14.3, 18.6, 160)
# the two private daycare rooms get real doors (oak-slatted leaves, like the reception's stair door)
put("door_slatted", 26.905, 31.3, rot=90, zone="daycare", width=1.0, height=2.1, note="nursing room door")
put("door_slatted", 14.5, 21.295, rot=0, zone="daycare", width=1.0, height=2.1, note="staff room door")
# nursing room: a lounge chair, side table, a small bottle-prep basin, a soft wall light
put("lounge_chair", 29.5, 32.3, rot=135, zone="daycare")
put("side_table", 28.7, 32.75, zone="daycare")
put("vanity", 29.6, 29.395, rot=0, zone="daycare", length=1.2, n=1, note="bottle prep: small stone basin")
put("rug_round", 29.0, 31.6, zone="daycare", d=1.8, colour="heather")
put("wall_light", 30.425, 31.0, rot=90, zone="daycare", light={"type": "AREA", "energy": 30, "size": 0.05, "size_y": 0.8, "offset": [0, 0.06, 2.75], "aim": None, "color": [1.0, 0.8, 0.6]})

# ---- daycare lower floor (E2): active play walking out to the garden, sleep room, children's WC, pram store
E2 = lv["E2"]
def put2(kind, x, y, rot=0.0, **kw):
    put(kind, x, y, rot=rot, zone=kw.pop("zone", "daycare"), level="E2", z=E2, **kw)
def dl2(x, y, energy=300):
    put2("downlight", x, y, z_ceiling=5.0, light={"type": "SPOT", "energy": energy, "spot_deg": 60, "offset": [0, 0, 4.82], "aim": [x, y, E2], "color": WARM})

# the garden door: a pair of glass doors in the north glazing between two mullions, straight onto the garden floor
gn = by_id["EN-G-E2-N-0"]
gn["openings"] = [{"s": [5.03, 7.47], "z": [E2, round(E2 + 2.4, 2)], "type": "door", "note": "daycare garden doors"}]
put2("glass_door", 24.25, 33.3, width=2.4, height=2.4, note="garden doors (pair)")
# active play: bouldering wall + crash mat on the west wall, wall bars, two nest swings from the beam, soft play, a balance beam
put2("climbing_wall", 12.215, 30.25, rot=-90, length=5.5, note="children's bouldering wall, 2.7 m, crash mat")
put2("wall_bars", 30.285, 22.95, rot=90, length=2.7, note="ribbevegg")
for x in (22.8, 26.6):
    put2("nest_swing", x, 24.74, top=round(-0.88 - E2, 2), note="nest swing hung from the E1 beam")
put2("foam_fortress", 20.8, 29.8, note="foam fortress: felt-covered foam blocks to build, knock down and throw")
put2("rolling_hill", 27.0, 29.5, note="lekebakke: a carpeted rolling hill with a crawl tunnel")
# wheels corner (Roman): caster boards, balance bikes and tricycles, a rack on the store wall
put2("wheel_rack", 25.45, 21.275, length=2.3, note="rack for balance bikes, caster boards, helmets")
for k, x in enumerate((24.7, 25.4, 26.1)):
    put2("strider", x, 21.95, rot=0, colour=COL[k + 1], note="balance bike")
for k, (x, y, r) in enumerate(((24.9, 23.0, 80), (25.4, 23.25, 95), (25.9, 22.95, 70))):
    put2("ripstick", x, y, rot=r, colour=COL[k * 2 % 5], note="caster board")
for k, x in enumerate((28.1, 28.9, 29.6)):
    put2("tricycle", x, 22.2, rot=-90 + 10 * k, colour=COL[(k + 3) % 5], note="tricycle")
put2("balance_beam", 16.8, 31.6, length=3.0)
# mudroom by the garden door (grovgarderobe): boot-wash trough, cubbies, drying cabinets on the east wall
put2("vanity", 30.285, 25.6, rot=90, length=1.6, n=2, top=0.5, note="boot + hand wash trough at child height")
put2("cubbies", 30.285, 28.5, rot=90, length=3.4, n=8, note="outdoor-clothes cubbies by the garden door")
for y in (30.6, 31.25):
    put2("drying_cabinet", 30.285, y, rot=90)
for x in (14.5, 18.5, 22.5, 26.5):
    for y in (22.8, 27.0, 31.0):
        dl2(x, y)
# sleep room (Roman: no bunks; a soft carpeted floor with mats + blankets, they sleep where they like): wall-to-wall wool
# carpet (tools/interior.py), mats laid out loosely, the rest on a low shelf, a star canopy, a soft wall light
put2("star_ceiling", 14.56, 18.69, size=[4.6, 4.7], hang=3.2, note="fibre-optic star canopy")
for k, (x, y, r) in enumerate(((13.1, 17.3, 8), (13.9, 17.5, -6), (14.9, 17.2, 15), (13.2, 19.0, -4), (14.3, 19.4, 22), (15.6, 19.1, -12),
                              (13.6, 20.5, 80), (15.4, 20.6, 95))):
    put2("sleep_mat", x, y, rot=r, colour=COL[k % 5], note="sleeping mat + blanket")
put2("mat_shelf", 16.925, 17.2, rot=90, length=1.6, note="mats + blankets between naps")
put2("wall_light", 16.925, 19.2, rot=90, light={"type": "AREA", "energy": 30, "size": 0.05, "size_y": 0.8, "offset": [0, 0.06, 2.75], "aim": None, "color": [1.0, 0.75, 0.5]})
for y in (17.6, 19.8):
    dl2(14.6, y, 140)
# children's WC (stacked under the upper one, same layout)
put2("kid_wc_cells", 18.9, 16.275, n=4, w=0.85, depth=1.2)
put2("vanity", 17.095, 19.0, rot=-90, length=2.4, n=3, top=0.55)
put2("light_only", 17.16, 19.0, light={"type": "AREA", "energy": 45, "size": 2.3, "size_y": 0.04, "offset": [0, 0, 1.9], "aim": [18.3, 19.0, E2 + 0.7], "color": WARM})
put2("changing_unit", 23.905, 19.95, rot=90, length=1.8)
put2("wc_cells", 22.65, 16.345, n=1, w=2.5, depth=2.4, style="accessible", door_at=-0.6, pan_at=0.7)
put2("cell_light", 22.65, 17.55, z_ceiling=2.6, light={"type": "POINT", "energy": 35, "radius": 0.05, "offset": [0, 0, 2.5], "color": WARM})
for x in (18.6, 21.2):
    dl2(x, 19.6, 320)
# pram + outdoor-gear store
for k, (x, c) in enumerate(((25.0, "fjord"), (26.2, "moss"), (28.6, "oat"), (29.6, "heather"))):
    put2("pram", x, 17.55, colour=c, note="pram parking")
put2("gear_rack", 30.285, 18.7, rot=90, length=4.0)
for y in (19.6, 20.25):
    put2("drying_cabinet", 24.075, y, rot=-90)
for x in (25.6, 28.8):
    for y in (17.6, 19.9):
        dl2(x, y, 300)

# ---- the sunken garden (outdoors, floor -6.15; Norwegian barnehage practice: gapahuk + fire, sand, swings, a playhouse,
# a trike loop, an embankment slide, outdoor napping in prams under a shelter, loose natural things; no fence along the top)
GZ = -6.15
def putg(kind, x, y, rot=0.0, z=GZ, **kw):
    put(kind, x, y, rot=rot, zone="garden", level="garden", z=z, **kw)
putg("sandbox", 27.3, 35.6, note="sandbox with a sit-on oak edge, by the door (the youngest play close to the building)")
putg("pram_shelter", 32.4, 37.0, rot=90, note="vognskur: the toddlers nap outdoors in their prams")
for y in (36.2, 37.8):
    putg("pram", 32.5, y, rot=90, colour="fjord" if y < 37 else "moss")
putg("mud_kitchen", 22.5, 36.3, rot=-90, note="gjørmekjøkken")
putg("playhouse", 24.3, 40.2, rot=-90, note="lekehus: the building in miniature, tarred boards + sod roof")
putg("trike_loop", 28.6, 41.0, rx=2.6, ry=2.3, note="tricycle loop, poured rubber")
for (x, y, r, c) in ((31.2, 41.4, 0, "cloud"), (28.2, 38.7, 90, "lingon")):
    putg("tricycle", x, y, rot=r, colour=c)
putg("communal_table", 28.6, 41.0, length=2.0, note="picnic table inside the loop: lunch outdoors")
for y, r in ((40.32, 0), (41.68, 180)):
    putg("bench", 28.6, y, rot=r, length=1.8)
putg("swing_frame", 33.7, 41.5, rot=90, note="nest swing + seat swing on a bark fall surface")
putg("gapahuk", 25.0, 45.7, rot=180, note="gapahuk facing the fire")
putg("fire_pit", 25.2, 42.9, note="bålplass")
putg("log_bench", 23.7, 43.0, rot=90, length=1.6)
for (x, y) in ((26.3, 43.6), (26.0, 42.2)):
    putg("stump", x, y, r=0.2, h=0.4)
putg("terrace_slide", 29.6, 48.4, rot=180, z=-3.45, drop=2.7, note="freestanding slide off the terrace edge, stair beside it")
for k, y in enumerate((36.5, 37.3, 38.2, 39.0, 40.0, 41.1, 42.0)):  # stepping stumps along the west terrace
    putg("stump", 20.3 + (0.25 if k % 2 else -0.15), y, z=-3.6, r=0.17, h=0.25 + 0.1 * (k % 3))

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

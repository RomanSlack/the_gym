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
def wc_room(run_x, run_rot, cells, pan_side, open_, occupied, store_x, store_rot, van_x, van_rot, aisle_x, urinal_y=None, tag=""):
    """One continuous run of cells on the long wall, flush from the north wall (Roman: no slivers, no doors at 90 deg, doors
    open outward); the accessible WC is the widest cell of the same run; the cleaner's closet sits flush in the opposite corner."""
    W = sum(c[0] for c in cells); cy = 16.105 - W / 2
    put("wc_run", run_x, cy, rot=run_rot, zone="wc", cells=cells, depth=1.8, open_=open_, occupied=occupied, pan_side=pan_side,
        note=f"{tag} WC run: fluted oak cells, outward doors, the accessible WC the last + widest cell")
    out = 1 if run_rot == -90 else -1
    edge = cy + W / 2 if run_rot == -90 else cy - W / 2   # where the first cell starts
    for w, st in cells:
        c = edge - out * w / 2
        put("cell_light", run_x + out * 0.9, c, zone="wc", z_ceiling=2.73,
            light={"type": "POINT", "energy": 35 if st == "accessible" else 18, "radius": 0.05, "offset": [0, 0, 2.6], "color": WARM})
        edge -= out * w
    put("wc_run", store_x, 16.105 - 0.7, rot=store_rot, zone="wc", cells=[[1.4, "store"]], depth=0.6, note="cleaner's closet, flush in the corner")
    put("vanity", van_x, 10.7, rot=van_rot, zone="wc", length=3.0, n=3, note=f"{tag} stone trough vanity, mirror, light")
    vin = 1 if van_rot == -90 else -1
    put("light_only", van_x + vin * 0.06, 10.7, zone="wc",
        light={"type": "AREA", "energy": 60, "size": 2.9, "size_y": 0.04, "offset": [0, 0, 2.2], "aim": [van_x + vin * 1.2, 10.7, 0.9], "color": WARM},
        note="linear light above the mirror (the fitting is part of the vanity)")
    for y in (8.2, 9.9, 11.6, 13.2, 14.8):  # recessed in the 2.75 m slat ceiling
        put("cell_light", aisle_x, y, zone="wc", z_ceiling=2.77,
            light={"type": "SPOT", "energy": 70, "spot_deg": 80, "blend": 1.0, "radius": 0.05, "offset": [0, 0, 2.7], "aim": [aisle_x, y, 0.12], "color": WARM})
    if urinal_y is not None:
        put("urinals", 20.655, urinal_y, rot=90, zone="wc", n=3, pitch=0.85, note="splash-free Nautilus urinals with oak screens, one at child height")

WCS = [1.1, "wc"]
wc_room(12.22, -90, [[2.4, "accessible"], WCS, WCS, WCS, WCS], -1, [0, 2], [3], 16.305, 90, 16.305, 90, 14.9, tag="women's")
wc_room(20.655, 90, [WCS, WCS, [2.4, "accessible"]], 1, [0, 2], [1], 16.495, -90, 16.495, -90, 17.9, urinal_y=9.9, tag="men's")

# ---- daycare upper floor (VISION "Daycare: playful, still Nordic"): play and colour from the furniture, light shell
DCART = {"forest": "docs/art/artdcforest_0.png", "lake": "docs/art/artdclake_0.png"}
def dl(x, y, energy=200, zone="daycare"):
    put("downlight", x, y, zone=zone, z_ceiling=5.02, light={"type": "SPOT", "energy": energy, "spot_deg": 60, "offset": [0, 0, 4.85], "aim": [x, y, 0.12], "color": WARM})

# round stair down to the lower daycare: guards round the opening + up both edges of the helix (the way on stays open)
# tube slide inside the stair's eye (Roman): find where the stair runs alongside the tube at an adult's reach -> rescue hatches
# in the tube + lockable gates in the stair's inner balustrade opposite them. Stair turned (Roman): bottom step at a0, top step
# 525 deg on; the tube starts at a bridge on the west side and ends heading north into the lower play room.
DS = next(st for st in m["stairs"] if st["id"] == "daycare_round"); SCX, SCY = DS["center"]; SA0 = DS.get("a0", 90.0)
T_TOP, T_TURN, TZ0, TZ1 = 200.0, 520.0, 0.36, -5.39
tz = lambda th: TZ0 + (TZ1 - TZ0) * (th - T_TOP) / T_TURN
sz = lambda al: -6.13 + (int((al - SA0) / 15) + 1) * 6.13 / 35
HATCH, GATES = [], []
for th in range(int(T_TOP) + 20, int(T_TOP + T_TURN) - 20, 2):
    for al in (th - 360 * j for j in range(-2, 4)):
        if SA0 + 5 <= al <= SA0 + 510 and 0.45 <= tz(th) - sz(al) <= 0.95 and all(abs(th - h) >= 150 for h in HATCH):
            HATCH.append(th); GATES.append(al)
top_c = (SA0 + 517.5) % 360  # the top tread: step off radially there
put("stair_guard", SCX, SCY, zone="daycare", gaps=[[top_c - 15, top_c + 15], [T_TOP - 10, T_TOP + 10]], gates=GATES, r_in=1.45, a0=SA0,
    note="child-safe guards: 1.2 m oak staves round the opening, balustrades on the helix, rescue gates by the tube's hatches")
put("tube_slide", SCX, SCY, zone="daycare", hatches=HATCH, a_top=T_TOP, turns_deg=T_TURN, run=2.4, stair_a0=SA0,
    note="tube slide down the stair's eye: stainless below, clear polycarbonate above, rescue hatches, oak bridge at the top")
# the 'tree house' play loft against the north glass (forest view from the deck), den underneath
put("play_loft", 18.9, 30.55, rot=180, zone="daycare", length=4.0, D=2.6, deck=1.6, note="oak play loft: deck 1.6 m, gable frame, stair, slide, den")
# craft tables at child height
for (tx, ty, tc) in ((14.7, 28.7, "cloud"), (13.9, 31.5, "moss")):
    put("kid_table", tx, ty, zone="daycare", colour=tc)
    for k in range(5):
        a = 90 + 72 * k
        put("kid_chair", tx + 0.78 * math.cos(math.radians(a)), ty + 0.78 * math.sin(math.radians(a)), rot=a + 90, zone="daycare", colour=COL[(k + 2) % 5])
# reading: the den under the loft is the reading nook (cushions + a felt curtain); a low face-out bookshelf beside it
put("low_shelf", 15.6, 33.0, rot=180, zone="daycare", length=1.6, h=0.8, note="face-out picture books by the den")
# the line between the kids' (3-12) and toddlers' (0-3) zones at x 21.25: low shelves, a gate, the story wall with the forest painting
put("low_shelf", 21.25, 28.8, rot=90, zone="daycare", length=3.8, h=0.8)
put("gate", 21.25, 21.85, rot=90, zone="daycare", width=0.9)  # at the south end, by the children's WC, well away from where the tree-house slide lands
put("story_wall", 21.25, 24.6, rot=90, zone="daycare", length=4.4, note="freestanding: the forest painting to the kids, books + pin board to the toddlers")
put("canvas_art", 21.25 - 0.06, 24.6, rot=90, zone="daycare", width=4.0, height=2.0, image=str(ROOT / DCART["forest"]),
    note="'forest friends', gpt-image-2 gouache, at children's eye level (0.45-2.45)", )
F[-1]["z0"] = 0.45
# name plaques under each animal (Roman: English, a little educational); positions in image fractions (u from left, v from top)
put("art_labels", 21.25 - 0.06, 24.6, rot=90, zone="daycare", width=4.0, height=2.0, z0=0.45, size=0.034,
    labels=[[0.075, 0.725, "Red squirrel"], [0.35, 0.745, "Moose calf"], [0.235, 0.85, "Hedgehog"], [0.46, 0.82, "Red fox"],
            [0.665, 0.335, "Tawny owl"], [0.83, 0.88, "Mountain hare"], [0.195, 0.29, "Willow tit"], [0.93, 0.44, "Bullfinch"]],
    note="educational name plaques on the forest painting")
put("low_shelf", 21.25, 31.95, rot=90, zone="daycare", length=2.2, h=0.8)
# the toddler zone, 0-3 (Roman: high effort, something structural; references: Råå day care's gables, Kočevje's built-in nooks,
# Montessori + Pikler practice): 'Kronen', an oval oak sunburst canopy hung at 2.75 m that gives the toddlers their own low sky,
# over the nest, a stepped oak amphitheatre with a soft felt pit; a Pikler arch; a cushioned window nest along the forest glass;
# a low mirror with a pull-up barre under the lake painting; sensory panels on the nursing-room wall; a low snack table
KX, KY = 25.2, 27.0
put("canopy_crown", KX, KY, zone="daycare", note="Kronen: oval oak sunburst canopy at 2.75 m with a glowing linen oculus, hung from the roof",
    light={"type": "AREA", "energy": 80, "size": 1.0, "size_y": 0.8, "offset": [0, 0, 2.7], "aim": [KX, KY, E1], "color": [1.0, 0.82, 0.6]})
put("light_only", KX, KY, zone="daycare", light={"type": "POINT", "energy": 120, "radius": 0.4, "offset": [0, 0, 3.4], "color": [1.0, 0.85, 0.65]},
    note="glow over the crown onto the ceiling")
put("nest", KX, KY, zone="daycare", note="the nest: stepped oak amphitheatre, felt-topped tiers, soft felt pit with cushions, a ramp in from the south")
put("pikler_arch", 28.9, 24.0, zone="daycare", note="Pikler climbing arch with a ramp")
put("window_nest", 30.44, 25.2, rot=90, zone="daycare", length=7.0, note="cushioned window nest with a low rail along the forest glass")
put("canvas_art", 28.75, 29.225, rot=180, zone="daycare", width=3.0, height=1.5, image=str(ROOT / DCART["lake"]), note="'moose by the lake', at toddler eye level over the mirror")
F[-1]["z0"] = 0.85
put("art_labels", 28.75, 29.225, rot=180, zone="daycare", width=3.0, height=1.5, z0=0.85, size=0.03,
    labels=[[0.19, 0.64, "Moose"], [0.31, 0.82, "Moose calf"], [0.69, 0.865, "Mallard ducks"]], note="name plaques on the lake painting")
put("dance_mirror", 28.35, 29.225, rot=180, zone="daycare", length=2.2, h=0.6, barre=0.4, note="low Montessori mirror with a pull-up barre at 0.40")
put("sensory_panel", 26.925, 30.05, rot=90, zone="daycare", style="maze", note="sensory panel: bead maze, spinners, felt textures")
put("sensory_panel", 26.925, 32.55, rot=90, zone="daycare", style="peek", note="sensory panel: peekaboo flaps, mirrors, pockets")
put("toddler_table", 23.4, 22.6, zone="daycare", note="low oval snack table")
for k, (dx, dy, r) in enumerate(((-0.45, -0.62, 0), (0.45, -0.62, 0), (-0.45, 0.62, 180), (0.45, 0.62, 180), (-1.05, 0, -90), (1.05, 0, 90))):
    put("kid_chair", 23.4 + dx, 22.6 + dy, rot=r, zone="daycare", colour=COL[k % 5], seat=0.22)
put("low_shelf", 24.0, 32.9, rot=180, zone="daycare", length=3.0, h=0.6)
# felt clouds over both zones (acoustics + colour from above), offset from the downlight grid
for (cx, cy, c, sc) in ((14.6, 30.0, "oat", 1.1), (19.6, 23.4, "cloud", 0.9), (13.6, 22.6, "fjord", 0.8), (23.2, 22.7, "heather", 1.0),
                        (23.4, 30.4, "oat", 1.0), (29.2, 22.4, "moss", 0.8), (13.4, 32.6, "lingon", 0.7)):
    put("felt_cloud", cx, cy, zone="daycare", colour=c, s=sc, hang=round(3.4 + (cx * 7 % 5) / 10, 2))
for x in (13.6, 17.4, 21.2, 25.0, 28.6):
    for y in (22.7, 26.0, 29.2, 32.3):
        if not (27.0 < x and y > 29.3) and ((x - 25.2) / 3.4) ** 2 + ((y - 27.0) / 2.7) ** 2 > 1:  # none over the nursing room or the crown
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
# staff room (Roman: it had no windows and a booth): it now looks west at the forest through divided glass; a kitchenette on the
# south wall, a walled + tiled staff toilet in the south-east corner (tools/interior.py), oak staff lockers on the east wall, the
# table for four by the window
put("kitchenette", 13.7, 16.275, rot=0, zone="daycare", length=2.4)
put("door_slatted", 15.95, 18.5, rot=0, zone="daycare", width=0.9, height=2.1, note="staff toilet door")
put("staff_wc_fit", 16.905, 17.35, rot=90, zone="daycare", note="staff toilet: WC, roll holder, hook")
put("vanity", 15.85, 16.295, rot=0, zone="daycare", length=0.6, n=1, note="staff toilet basin + mirror")
put("cell_light", 16.1, 17.4, zone="daycare", z_ceiling=2.7, light={"type": "POINT", "energy": 35, "radius": 0.05, "offset": [0, 0, 2.6], "color": WARM})
put("staff_lockers", 16.925, 19.75, rot=90, zone="daycare", n=6, note="staff lockers")
put("cafe_table", 13.4, 19.2, zone="daycare")
for d in (0, 90, 180, 270):
    put("dining_chair", 13.4 + 0.62 * math.cos(math.radians(d)), 19.2 + 0.62 * math.sin(math.radians(d)), rot=d + 90, zone="daycare")
dl(13.4, 19.2, 160)
dl(14.2, 17.4, 140)
# the two private daycare rooms get real doors (oak-slatted leaves, like the reception's stair door)
put("door_slatted", 26.905, 31.3, rot=90, zone="daycare", width=1.0, height=2.1, note="nursing room door")
put("door_slatted", 14.5, 21.295, rot=0, zone="daycare", width=1.0, height=2.1, note="staff room door (1.9 m clear in front of it now)")
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
    put2("downlight", x, y, z_ceiling=5.0, light={"type": "SPOT", "energy": energy, "spot_deg": 75, "blend": 1.0, "radius": 0.25, "offset": [0, 0, 4.82], "aim": [x, y, E2], "color": WARM})

# the garden door: a pair of glass doors in the north glazing between two mullions, straight onto the garden floor
gn = by_id["EN-G-E2-N-0"]
gn["openings"] = [{"s": [5.03, 7.47], "z": [E2, round(E2 + 2.4, 2)], "type": "door", "note": "daycare garden doors"}]
put2("glass_door", 24.25, 33.3, width=2.4, height=2.4, note="garden doors (pair)")
# active play: bouldering wall + crash mat on the west wall, wall bars, two nest swings from the beam, soft play, a balance beam
put2("climbing_wall", 12.215, 30.25, rot=-90, length=5.5, note="children's bouldering wall, 2.7 m, crash mat")
put2("wall_bars", 30.285, 22.95, rot=90, length=2.7, note="ribbevegg")
for x in (22.8, 26.6):
    put2("nest_swing", x, 24.74, top=round(-0.88 - E2, 2), note="nest swing hung from the E1 beam")
put2("foam_fortress", 21.6, 29.6, note="foam fortress: felt-covered foam blocks to build, knock down and throw")
put2("rolling_hill", 26.5, 29.6, note="lekebakke: a carpeted rolling hill with a crawl tunnel")
# floor games inlaid in linoleum (Roman: the floor was bleak): a race track looping round the fortress and the hill, a hopscotch
put2("floor_track", 24.0, 29.6, note="race track inlaid in the floor: a loop for trikes + balance bikes, start line, chevrons")
put2("hopscotch", 20.0, 22.35, note="hopscotch, numbered squares inlaid in the floor")
# wheels corner (Roman): caster boards, balance bikes and tricycles, a rack on the store wall
put2("wheel_rack", 25.45, 21.275, length=2.3, note="rack for balance bikes, caster boards, helmets")
for k, x in enumerate((24.7, 25.4, 26.1)):
    put2("strider", x, 21.95, rot=0, colour=COL[k + 1], note="balance bike")
for k, (x, y, r) in enumerate(((24.9, 23.0, 80), (25.4, 23.25, 95), (25.9, 22.95, 70))):
    put2("ripstick", x, y, rot=r, colour=COL[k * 2 % 5], note="caster board")
for k, x in enumerate((28.1, 28.9, 29.6)):
    put2("tricycle", x, 22.2, rot=-90 + 10 * k, colour=COL[(k + 3) % 5], note="tricycle")
# the north wall beside the climbing wall (Roman: a lame corner): a music wall + a low dance mirror with a barre; and a balance
# trail in front of the mirror instead of a single beam
NW = 33.3 - 0.2 - 0.015  # plaster face of the north wall
put2("music_wall", 15.1, NW, rot=180, length=1.9, note="music wall: xylophone, chimes, drums, rain stick")
put2("dance_mirror", 16.95, NW, rot=180, length=1.5, note="low safety mirror + barre at 0.55 (stays on the wall: it ends 0.25 m before the glass)")
# the upper walls (Roman: fill them out, fun for the kids): tall felt banners with appliqué motifs, and pennant bunting across
MOTIFS = ["sun", "mountains", "spruce", "waves", "moon"]
BAN = [(12.215, y, -90, 1.9) for y in (22.6, 25.9, 27.9, 29.4, 30.9, 32.4)] + \
      [(30.285, y, 90, 2.0) for y in (22.5, 24.6, 26.7, 28.8, 30.9)] + \
      [(x, NW, 180, 1.8) for x in (14.2, 16.5)] + [(x, 21.275, 0, 1.9) for x in (25.0, 28.9)]
for k, (x, y, r, h) in enumerate(BAN):
    put2("felt_banner", x, y, rot=r, motif=MOTIFS[k % 5], colour=COL[(k * 2 + 1) % 5], h=h, note="felt wall banner with an appliqué motif")
for y, z in ((27.6, 4.6), (31.2, 4.4)):  # bunting from the west wall to the east wall, high over the race track
    put("bunting", 12.25, y, zone="daycare", level="E2", z=round(E2 + z, 2), length=18.0, sag=0.7, note="felt pennant bunting")
put2("balance_trail", 16.0, 31.1, note="balance trail: zig-zag beams, stepping pods, a wobble board")
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

# ---- sanitation everywhere it belongs (Roman: the level of detail): a towel dispenser + waste bin beside every vanity, nappy bins,
# gloves + liners at the changing units (in their builders), sanitiser at the entrances, waste sorting (kildesortering)
for (x, y, r, z) in ((16.305, 8.95, 90, None), (16.495, 8.95, -90, None),            # public WCs, south of each vanity
                     (17.095, 20.65, -90, "E1"), (17.095, 20.65, -90, "E2"),         # children's WCs (towels at child height)
                     (30.285, 24.55, 90, "E2"),                                      # garden mudroom trough
                     (28.6, 29.395, 0, "E1")):                                      # nursing room bottle prep
    kw = {"level": "E2", "z": E2} if z == "E2" else {}
    put("towel_station", x, y, rot=r, zone="wc" if z is None else "daycare", **kw)
put("sanitiser", 29.6, 9.6, zone="entrance", note="hand sanitiser inside the main doors")
put("sanitiser", 26.4, 16.6, zone="daycare", note="hand sanitiser by the daycare door")
put("sanitiser", 24.6, 21.6, zone="daycare", note="hand sanitiser at the toddler zone")
put2("sanitiser", 22.9, 32.9, note="hand sanitiser at the garden doors")
put("recycling", 13.0, 21.125, rot=180, zone="daycare", length=1.2, note="staff room waste sorting")
put("recycling", 28.2, -9.25, rot=0, zone="cafe", length=1.2, note="cafe waste sorting (kildesortering) by the dining tables")

# ---- detail pass (Roman: the daycare's level of detail is the bare minimum everywhere): reception, public WCs, cafe, services
def putz(kind, x, y, dz, rot=0.0, zone="cafe", **kw):  # a piece standing on a surface dz above the floor
    put(kind, x, y, rot=rot, zone=zone, **kw); F[-1]["z"] = round(E1 + dz, 3)
# reception: coat stand + umbrellas inside the doors, a reading lamp and magazines in the waiting nook
put("coat_rack", 29.9, 13.5, rot=90, zone="reception", note="coat stand + umbrella stand inside the doors")
put("floor_lamp", 29.95, 15.85, zone="reception", light={"type": "POINT", "energy": 25, "radius": 0.15, "offset": [0, 0, 1.4], "color": [1.0, 0.8, 0.58]},
    note="reading lamp in the waiting nook")
putz("magazines", 29.45, 15.1, 0.525, zone="reception")
# safety: AED + extinguisher + first aid on core E's cafe face; a second point in the daycare wardrobe, a third downstairs
put("safety_point", 23.45, 6.61, rot=180, zone="cafe", note="hjertestarter (AED), 6 kg extinguisher, first-aid kit")
put("safety_point", 24.095, 20.95, rot=-90, zone="daycare", aed=False, note="extinguisher + first aid at the daycare entrance")
put2("safety_point", 30.285, 21.95, rot=90, aed=False, note="extinguisher + first aid on the lower floor")
# exit signs over the exits
put("exit_sign", 30.44, 11.29, rot=90, zone="entrance", mount=2.85, note="nødutgang over the main doors")
put("exit_sign", 27.4, 16.13, rot=180, zone="reception", mount=2.5, note="over the daycare door")
put("exit_sign", 24.19 + 0.07, 7.55, rot=-90, zone="reception", mount=2.5, note="over the core E stair door")
put2("exit_sign", 24.25, 33.24, rot=180, mount=2.6, note="over the garden doors")
# wayfinding, Norwegian + English, burnt into oak
# pictograms (Roman: the text signs were lame): blackened-steel plates with brass figures beside each entrance, and steel portals
WCF = 6.8 - 0.075 - 0.065  # face of the oak slats on the WC block
for (px, kinds) in ((15.45, ("woman", "accessible", "baby")), (19.85, ("man", "accessible", "baby"))):
    for j, kd in enumerate(kinds):
        put("pictogram", px, WCF, rot=180, zone="cafe", figure=kd, size=0.36 if j == 0 else 0.17, mount=1.62 if j == 0 else 1.29, note=f"WC pictogram: {kd}")
        if j:
            F[-1]["at"][0] = round(px + (0.08 if j == 1 else -0.08), 3)
for x in (14.2, 18.6):
    put("portal_frame", x, 6.8 + 0.075 + 0.02, rot=180, zone="cafe", width=1.6, height=2.4, depth=0.25, note="blackened-steel portal")
put("pictogram", 12.95, WCF, rot=180, zone="cafe", figure="gym", size=0.3, mount=1.62, note="to the gym (west, over the bridge)")
put("pictogram", 26.6, 16.17, rot=180, zone="reception", figure="child", size=0.3, mount=1.62, note="daycare")
put("pictogram", 24.26, 16.0, rot=-90, zone="reception", figure="lift", size=0.2, mount=1.4, note="lift to the garage")
# public WCs: a floor drain in each, an amenity tray on every vanity (period products in the women's)
for x in (14.75, 18.05):
    put("floor_drain", x, 12.4, zone="wc")
for y in (10.2, 11.2):
    putz("amenity_tray", 16.305, y, 0.86, rot=90, zone="wc", products=True)
    putz("amenity_tray", 16.495, y, 0.86, rot=-90, zone="wc", products=False)
# cafe settings: tealights on every table, carafes on the dining tables; water station; bar menus; high chairs parked by the
# water station; downlights over each seating group
for x in (27.0, 29.4):
    putz("table_setting", x, -7.0, 0.74, rot=30)
for (x, y) in ((28.2, -3.3), (28.2, 1.6)):
    putz("table_setting", x, y, 0.395, carafe=False)
for x in (17.9, 21.3, 24.7):
    putz("table_setting", x, -8.45, 0.525, carafe=False)
for (dx, dy) in ((-0.25, 0.1), (0.2, -0.15), (0.05, 0.25)):
    putz("table_setting", 15.4 + dx, -4.6 + dy, 0.421, carafe=False)
put("water_station", 22.0, 6.61, rot=180, zone="cafe", note="water, glasses, cutlery, napkins, trays; waste sorting in the base")
putz("menu_board", 21.25 + 3.3 * math.cos(math.radians(100)), -1.35 + 3.3 * math.sin(math.radians(100)), 1.05, rot=10)
putz("menu_board", 21.25 + 3.3 * math.cos(math.radians(330)), -1.35 + 3.3 * math.sin(math.radians(330)), 1.05, rot=240)
put("high_chair", 20.3, 6.2, rot=180, zone="cafe")
put("high_chair", 19.85, 6.25, rot=170, zone="cafe")
for (x, y) in ((27.0, -7.0), (29.4, -7.0), (28.2, -3.3), (28.2, 1.6), (17.9, -8.2), (21.3, -8.2), (24.7, -8.2)):
    dl(x, y, 160, zone="cafe")
# building services in every ceiling (TEK17): sprinklers on a ~3 m grid, smoke detectors one per ~7 m, dropped below the fins
def services(x0, x1, y0, y1, level, z, ceil, avoid=()):
    k = 0; floor = lv[level]
    nx, ny = int((x1 - x0) / 3.1) + 1, int((y1 - y0) / 3.1) + 1
    for i in range(nx):
        for j in range(ny):
            x, y = x0 + i * 3.1, y0 + j * 3.1
            if any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
                continue
            put("ceiling_services", round(x, 2), round(y, 2), zone="services", level=level, device="smoke" if k % 4 == 0 else "sprinkler",
                z_local=round(z - floor, 3), ceiling=round(ceil - floor, 3))
            F[-1]["z"] = floor
            k += 1
services(13.3, 30.4, -8.7, 6.7, "E1", 5.05, 5.62, avoid=((21.25, -1.35, 3.6), (15.4, -4.6, 2.0)))
services(24.2, 30.4, 6.9, 16.0, "E1", 5.05, 5.62)                                                    # reception
services(13.0, 20.6, 8.4, 16.0, "E1", 2.74, 2.8)                                                     # WCs: in their 2.75 ceiling                  # cafe, reception, WCs
services(13.1, 30.4, 17.0, 33.0, "E1", 5.05, 5.62, avoid=((25.2, 27.0, 3.2), (16.6, 25.0, 2.7)))   # daycare upper (crown has its own)
services(13.1, 30.4, 17.0, 33.0, "E2", -0.6, -0.24, avoid=((16.6, 25.0, 2.7),))                    # daycare lower

# ---- cafe: island bar + ring pendant
cx, cy = 21.25, -1.35
put("cafe_island", cx, cy, zone="cafe", r_out=3.5, gap_deg=225, note="round island bar: outer bar, staff ring, back counter")
put("ring_pendant", cx, cy, zone="cafe", r=3.15, hang=3.35, note="oak + linen ring light over the bar")
R = 3.5 + 0.38
n = int(2 * math.pi * R / 0.66)
for k in range(n):  # stools only on the arc facing the reception + the east lounges (Roman: fewer stools, fewer plain chairs)
    a = 360 * k / n
    if 140 < a < 300:
        continue
    ar = math.radians(a)
    put("bar_stool", cx + R * math.cos(ar), cy + R * math.sin(ar), rot=a + 90, zone="cafe", height=0.76)  # seat faces the bar
# the centrepiece: Steinringen, a built-in conversation ring round a glacial granite boulder, under 'Elva', the oak river
put("conversation_ring", 15.4, -4.6, zone="cafe", note="Steinringen: built-in curved oak + wool banquette, open twice")
put("boulder_table", 15.4, -4.6, rot=20, zone="cafe", note="flyttblokk: glacial granite boulder, top sawn + honed")
put("elva", 12.9, -0.6, zone="cafe", note="Elva: ~210 suspended oak fins tracing a river through the room")
# view lounge along the south glass (Roman: low, looking out, not a stool counter): pairs of lounge chairs + low side tables
for x in (17.9, 21.3, 24.7):
    put("lounge_chair", x - 0.6, -8.35, rot=200, zone="cafe")
    put("lounge_chair", x + 0.6, -8.35, rot=160, zone="cafe")
    put("side_table", x, -8.45, zone="cafe")
    put("rug_round", x, -8.3, zone="cafe", d=2.4, colour="oat")
# two conversation groups along the east glass: a sofa facing the forest, two lounge chairs, a coffee table, on a rug
for y in (-3.3, 1.6):
    put("rug", 28.2, y, zone="cafe", size=[3.4, 2.8])
    put("sofa", 26.85, y, rot=-90, zone="cafe", length=2.2)
    put("coffee_table", 28.2, y, zone="cafe")
    put("lounge_chair", 29.55, y - 0.85, rot=110, zone="cafe")
    put("lounge_chair", 29.55, y + 0.85, rot=70, zone="cafe")
# (the north-west sofa corner by the bridge is gone (2026-10-12): the members' gates stand at the bridge mouth and people walk off
# them right there; Steinringen beside the gates is the meeting point)
# two tables for four in the south-east corner, for those who want to eat at a table
for x in (27.0, 29.4):
    put("cafe_table", x, -7.0, zone="cafe")
    for d in (0, 90, 180, 270):
        put("dining_chair", x + 0.62 * math.cos(math.radians(d)), -7.0 + 0.62 * math.sin(math.radians(d)), rot=d + 90, zone="cafe")

# ---- the lounge bridge + its decks (Roman, 2026-10-12): a minimal pass-through as you enter the gym. Members' gates at the cafe
# mouth (the phone is the key), 'Laksetrappa', a flowing ladder of light down the middle, two mirrored rows of walk-on glass in the
# floor looking down to the river, two benches and nothing else inside; standing tables + outdoor versions of the cafe sofas on the
# decks. The bridge floor rises 0.00 -> 0.12 over its 18.45 m: everything on it stands at zf(x).
F1 = lv["F1"]
zf = lambda x: round(F1 + (E1 - F1) * min(1.0, max(0.0, (x + 6.45) / 18.45)), 4)
def putb(kind, x, y, rot=0.0, zone="bridge", z=None, **kw):
    put(kind, x, y, rot=rot, zone=zone, level="F1", z=zf(x) if z is None else z, **kw)
BAX, BAY = 2.775, -1.35   # the bridge's centre (x mid-span, y on the axis between the glass walls)
BEAMS = sorted(e["from"][0] for e in m["elements"] if e["id"].startswith("ST3-link-roofbeam-"))
SLATS, CLT_ = 5.54, 5.62  # underside of the bridge's slat ceiling; the CLT behind it
BEAM_BOT = next(e["z"][0] for e in m["elements"] if e["id"] == "ST3-link-roofbeam-0")

# members' gates on the column line at the cafe mouth (x 12.0): column D12 stands in the middle of the bank as its spine; each side
# a 650 lane + a 1000 lane (wheelchairs, prams, kit); 200 cabinets. Frameless 1.2 m glass closes the line to the glass walls.
GX, GY = 12.0, -0.94      # column D12
CABS_W = [-0.585, 0.265, 1.465, -1.295, -2.145, -3.345]           # cabinet centres (world y)
LANES_W = [[0.365, 1.365], [-0.485, 0.165], [-2.045, -1.395], [-3.245, -2.245]]
loc = lambda y: round(-(y - GY), 3)                                # local x of the bank (rot -90: local +y faces the cafe)
put("speed_gates", GX, GY, rot=-90, zone="bridge", cabs=[[loc(y), 0.2] for y in CABS_W], lanes=sorted([sorted([loc(a), loc(b)]) for a, b in LANES_W]),
    open_=[0], note="members' speed gates: tap the phone (NFC / BLE), glass wings, fail-safe open on fire alarm")
put("glass_fence", GX, (1.565 + 6.65) / 2, rot=90, zone="bridge", length=round(6.65 - 1.565, 3), note="frameless 1.2 m glass to the WC wall")
put("glass_fence", GX, (-9.275 - 3.445) / 2, rot=90, zone="bridge", length=round(9.275 - 3.445, 3), note="frameless 1.2 m glass to column D13")
put("floor_strip", GX, (-3.445 + 1.565) / 2, rot=90, zone="bridge", length=5.01, w=0.04, note="blackened-steel threshold where the bridge oak meets the cafe oak")
put("gate_release", GX + 0.175, GY, rot=-90, zone="bridge", note="nødåpning: emergency release for the gates (cafe side)")
put("gate_release", GX - 0.175, GY, rot=90, zone="bridge", note="nødåpning (bridge side)")
# the walk-on glass (openings cast in tools/structure_stage.py): each panel's sleeve runs from the floor down to the deck soffit
for h in next(e for e in m["elements"] if e["id"] == "S-F1-link")["holes"]:
    if h.get("glass_floor"):
        x, y = h["glass_floor"]
        putb("glass_floor", x, y, depth=round(zf(x) + 0.40, 2), note="1.0 m walk-on glass, frit top ply, steel sleeve to the soffit")
# Laksetrappa: two oak rails grow out of the ceiling at x -5.2 and 10.6 (clear of the end beams), dip to ~3.4-4.2 m along the
# middle (under the three inner beams, bottoms at 4.64), swaying in plan and rolling round each other; rungs of light every 0.3 m.
# Roman: two more in the same style, one either side, symmetric, drawing you in: they start wide, high and flat over the outer bays
# at the cafe end and sweep in towards the middle one as they run to the gym, tapering, dropping and rolling over as they go, so all
# three lines converge on the way into the gym (the side pair is one shape, mirrored about the axis).
XA, XB = -5.2, 10.6
def lad_mid(u):
    e_ = max(0.0, 1 - min(u, 1 - u) / 0.17); bl = e_ * e_          # e^2: leaves the ceiling steeply, levels out smoothly
    zc = (3.72 + 0.28 * math.sin(2 * math.pi * 1.5 * u + 0.4)) * (1 - bl) + SLATS * bl
    yc = 0.5 * math.sin(2 * math.pi * 1.1 * u + 0.5) * (1 - 0.5 * bl)
    w = (0.40 + 0.16 * math.sin(2 * math.pi * 2.2 * u + 1.1)) * (1 - bl) + 0.2 * bl
    th = 0.45 * math.sin(2 * math.pi * 0.85 * u + 0.7) * (1 - bl)
    return XA + (XB - XA) * u, yc, zc, w, th
def lad_side(sg):  # u = 0 at the gym end (west), 1 at the cafe end; sg = +1 north, -1 south (mirror)
    def f(u):
        e_ = max(0.0, 1 - min(u, 1 - u) / 0.15); bl = e_ * e_
        g = u ** 1.35
        zc = (3.7 + 0.5 * g) * (1 - bl) + SLATS * bl                  # low near the gym, high + flat at the cafe
        yc = sg * (1.85 + 2.75 * g + 0.12 * math.sin(2 * math.pi * 1.2 * u))  # sweeps in to the middle towards the gym
        w = (0.16 + 0.44 * g) * (1 - bl) + 0.15 * bl                  # tapers towards the gym
        th = -sg * 1.15 * (1 - g) * (1 - bl)                          # rolls over (inner rail down) as it goes in
        return XA + (XB - XA) * u, yc, zc, w, th
    return f
def ladder(lad):
    def rails_at(u):
        x, yc, zc, w, th = lad(u); x2, yc2 = lad(min(1, u + 1e-3))[:2]; x1, yc1 = lad(max(0, u - 1e-3))[:2]
        tx, ty = x2 - x1, yc2 - yc1; n_ = math.hypot(tx, ty); nx, ny = -ty / n_, tx / n_
        return [[round(x - BAX + s_ * w * math.cos(th) * nx, 4), round(yc + s_ * w * math.cos(th) * ny, 4), round(zc + s_ * w * math.sin(th), 4)] for s_ in (1, -1)]
    R2 = [rails_at(k / 400) for k in range(401)]
    rails = [[r[0] for r in R2], [r[1] for r in R2]]
    for rl in rails:  # the rail ends stop at the slats, whatever their offset
        for i in (0, -1):
            rl[i][2] = SLATS
    rungs = []
    for k in range(60):
        d = 0.25 + 0.3 * k
        if d > XB - XA - 0.25:
            break
        a_, b_ = rails_at(d / (XB - XA))
        if max(a_[2], b_[2]) < SLATS - 0.25:
            rungs.append([a_, b_])
    cables = []
    for xc in (-3.6, BEAMS[1], (BEAMS[1] + BEAMS[2]) / 2, BEAMS[2], (BEAMS[2] + BEAMS[3]) / 2, BEAMS[3], 8.9):
        for p_ in rails_at((xc - XA) / (XB - XA)):
            on_beam = any(abs(xc - b) < 0.13 for b in BEAMS)
            cables.append([p_[0], p_[1], round(p_[2] + 0.03, 3), BEAM_BOT if on_beam else CLT_])
    return rails, rungs, cables
for u in [k / 200 for k in range(201)]:  # the beams cross every ladder: stay under them (bottoms at 4.64) where they do
    for lad in (lad_mid, lad_side(1), lad_side(-1)):
        x, yc, zc, w, th = lad(u)
        if any(abs(x - b) < 0.3 for b in BEAMS) and zc + w * abs(math.sin(th)) + 0.032 > BEAM_BOT - 0.1:
            raise SystemExit(f"ladder hits a roof beam at x {x:.2f}")
fish = []
for k, (xf, Lf) in enumerate(((8.15, 0.42), (6.3, 0.34), (4.0, 0.3))):  # leaping west, up the ladder, towards the gym
    _, yc, zc, _, _ = lad_mid((xf - XA) / (XB - XA))
    fish.append([round(xf - BAX, 3), round(yc + 0.08 * (-1) ** k, 3), round(zc + 0.2 + 0.06 * k, 3), math.pi, Lf, 0.32, CLT_])
rails, rungs, cables = ladder(lad_mid)
putb("laksetrappa", BAX, BAY, z=F1, rails=rails, rungs=rungs, cables=cables, fish=fish,
     note="Laksetrappa: a flowing oak ladder of light down the bridge, opal rungs, three steel trout leaping up it")
for sg in (1, -1):
    rails, rungs, cables = ladder(lad_side(sg))
    putb("laksetrappa", BAX, BAY, z=F1, rails=rails, rungs=rungs, cables=cables, fish=[],
         note="side ladder: sweeps in from the outer bay at the cafe towards the middle at the gym, tapering + rolling over")
for lad, n_, e_ in ((lad_mid, 10, 45), (lad_side(1), 7, 30), (lad_side(-1), 7, 30)):  # the rungs are the light: real sources along each ladder, 2700 K
    for k in range(n_):
        x, yc, zc, _, _ = lad(0.12 + 0.76 * k / (n_ - 1))
        putb("light_only", x, BAY + yc, z=F1, light={"type": "AREA", "energy": e_, "size": 1.2, "size_y": 0.3, "offset": [0, 0, round(zc - 0.06, 3)],
             "aim": [x, BAY + yc, 0.0], "color": [1.0, 0.82, 0.6]}, note="light from the Laksetrappa rungs")
# (rugs tried down the middle, 2026-10-12; Roman: out of place, removed. The oak runs clear from the cafe to the gym.)
# two benches and nothing else: backless walnut planks in the outer bays, facing the view (falls north, the gorge south)
putb("bridge_bench", BAX, -8.45, rot=180, length=3.2, note="bench facing the gorge downstream")
putb("bridge_bench", BAX, 5.75, rot=0, length=3.2, note="bench facing the falls")
# the doorway to each deck: one lift-and-slide leaf per side slid open behind its neighbour (bay x 5.01-7.24, between the posts)
for gid, yl, yin in (("EN-G-link-N-0", 6.8, 6.68), ("EN-G-link-S-0", -9.5, -9.38)):
    by_id[gid]["openings"] = [{"s": [11.495, 13.655], "z": [F1, 3.0], "type": "door", "note": "lift-and-slide leaf, slid open: the way out to the deck"}]
    putb("slide_panel", 4.0, yin, rot=0, w=2.23, h=2.93, note="lift-and-slide leaf, slid open on its inner track")
    putb("floor_strip", 5.03, yin, length=4.34, w=0.02, note="recessed inner track, flush")
# services: sprinklers + smoke detectors in the slat ceiling, mid-bay between the beams, clear of the ladder; exit signs at both ends
k = 0
for i in range(4):
    for y in (-8.0, -4.9, 2.1, 5.2):
        putb("ceiling_services", round((BEAMS[i] + BEAMS[i + 1]) / 2, 3), y, zone="services", z=F1, device="smoke" if (k % 4 == 1 and abs(y) < 5) else "sprinkler",
             z_local=5.48, ceiling=CLT_)
        k += 1
putb("exit_sign", BEAMS[-1], BAY + 0.9, rot=90, z=F1, mount=2.75, hang_to=BEAM_BOT, note="nødutgang: towards the cafe + the main doors")
putb("exit_sign", BEAMS[0], BAY + 0.9, rot=-90, z=F1, mount=2.75, hang_to=BEAM_BOT, note="nødutgang: towards the gym's exit stairs")

# decks: boards 15 mm under the bridge floor (tools/interior.py), a slot drain along each threshold
zd = lambda x: round(zf(x) - 0.015, 4)
def putd(kind, x, y, rot=0.0, z=None, **kw):
    putb(kind, x, y, rot=rot, zone="deck", z=zd(x) if z is None else z, **kw)
for yd, x1 in ((6.92, 11.8), (-9.62, 11.92)):
    xs_ = [-6.39 + 2.0 * i for i in range(int((x1 + 6.39) / 2.0) + 1)] + [x1]
    for xa, xb in zip(xs_, xs_[1:]):
        putd("floor_strip", (xa + xb) / 2, yd, length=round(xb - xa, 3), w=0.12, style="grate", note="slot drain at the threshold")
def group(xg, yb, face):  # the cafe's sofa group made for the deck: sofa with its back to the glass, a granite table, two chairs
    s_ = 1 if face == "N" else -1; r0 = 0 if face == "N" else 180
    putd("deck_sofa", xg, yb + s_ * 0.4, rot=r0, length=2.2, note="outdoor sofa (the cafe's, in oiled oak + canvas)")
    putd("deck_table", xg, yb + s_ * 1.5, d=0.9, h=0.38, note="low table, honed granite")
    putd("deck_chair", xg - 1.45, yb + s_ * 1.6, rot=r0 - s_ * 60)
    putd("deck_chair", xg + 1.45, yb + s_ * 1.6, rot=r0 + s_ * 60)
    putd("blanket_basket", xg + 1.47, yb + s_ * 0.2, note="wool blankets")
    putb("ir_heater", xg, yb + s_ * 0.9, zone="deck", z=F1, z_top=5.615, note="infrared heater under the eave (cold evenings)")
NB, SB = 7.35, -10.06   # sofa backs: 0.4 m off the glass (the slot drain + room for the sliding leaves)
for xg in (-2.4, 8.6):    # north deck, the falls view: one group on the falls' axis (x ~ -3), one at the east end
    group(xg, NB, "N")
for xt in (1.2, 2.9, 4.6):  # standing tables at the balustrade between the groups: stand facing the falls
    putd("standing_table", xt, 10.75, note="standing table, oiled oak on steel")
    putd("table_setting", xt + 0.12, 10.75, z=round(zd(xt) + 1.08, 3), carafe=False)
# south deck (the sun deck, downstream view; 2.7 m deep): two sofas facing south with a side table + blankets, standing tables between
for xs in (-0.6, 9.2):
    putd("deck_sofa", xs, SB - 0.4, rot=180, length=2.2, note="outdoor sofa facing the sun")
    putd("deck_table", xs + 1.45, SB - 0.45, d=0.5, h=0.5, note="side table, honed granite")
    putd("blanket_basket", xs - 1.47, SB - 0.3)
    putb("ir_heater", xs, SB - 0.6, zone="deck", z=F1, z_top=5.615)
for xt in (-4.0, 2.0, 3.7):
    putd("standing_table", xt, -11.95)
    putd("table_setting", xt - 0.12, -11.95, z=round(zd(xt) + 1.08, 3), carafe=False)
for (x, y) in ((-2.4, 8.9), (2.9, 8.9), (8.6, 8.9), (-0.6, -11.0), (2.85, -11.0), (9.2, -11.0)):  # in the oak eave soffit
    putb("downlight", x, y, zone="deck", z=F1, z_ceiling=5.6, light={"type": "SPOT", "energy": 120, "spot_deg": 70, "blend": 1.0, "radius": 0.05,
         "offset": [0, 0, 5.42], "aim": [x, y, 0.0], "color": WARM})

m["furnishings"] = F
# the old schematic fixtures for E1 are replaced by real pieces (drawings keep them as symbols)
for f in m.get("fixtures", []):
    if f["id"] == "reception_desk":
        f["rect"] = [25.3, 9.0, 26.1, 13.6]
modelio.save(m)
print("furnishings:", len(F), {k: sum(1 for f in F if f["kind"] == k) for k in sorted({f["kind"] for f in F})})

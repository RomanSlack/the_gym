"""Kulpen, the outdoor sauna (Roman, 2026-10-14): the 2D layout before any 3D, like the locker rooms.

Writes model/layouts/sauna.json (shown and edited in blueprint/layout.html?name=sauna). Once Roman edits it there, the JSON is the source;
this script won't overwrite it without --force.

The site (model.site.features.sauna): the pad at +0.50 on the west bank, the dipping pool (water -1.42, bed -2.7) to the east, the bank
dropping ~2 m over 4 m between them. VISION "Kulpen":
  building  5 x 8 m (outer faces x -25.5 .. -20.5, y 92.0 .. 100.0), floor +0.60, gable sod roof (ridge N-S), the berm on W + N
  porch     the south 1.4 m under the roof, open to the path (S) and the landing (E)
  changing  4.5 x 2.4 clear; the heater's firebox opens into it through the hot-room wall
  hot room  4.5 x 3.55 clear, 2.3 high; two tiers in an L (west + north) facing the window (E) and the heater (S): the U closed by the fire
  landing   at floor level east of the porch + changing room, steps down to the lower deck by the water (Kebony)
  lower deck  the badestamp (wood-fired hot tub, hybrid), the flume + tipping bucket, granite slab steps into the pool
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "layouts" / "sauna.json"
if OUT.exists() and "--force" not in sys.argv:
    print("kept (edited by hand in blueprint/layout.html?name=sauna):", OUT.relative_to(ROOT), "· --force to regenerate")
    sys.exit(0)

FL = 0.60            # finished floor (the pad is +0.50; slab on grade + boards)
DECK_LO = -0.25      # the lower deck, 1.17 above the pool
WATER = -1.42
X0, X1, Y0, Y1 = -25.5, -20.5, 92.0, 100.0   # outer faces; Y0 = the porch front
T, TP = 0.25, 0.15   # exterior walls, the hot-room wall
YP = 93.4            # porch / changing-room wall (outer face)
YH = 96.05           # changing / hot-room wall (changing-room face)
PLATE = FL + 2.45    # top of the wall plate (hot room ceiling at FL + 2.3 under it)

KINDS = {  # plan size defaults (w along the piece, d front-to-back), height, front clearance, colour key
    "bench_upper": {"label": "Upper tier: thermo-aspen, seat FL + 1.00 (the hot one; 600 a person)", "d": 0.6, "h": 1.0, "mat": "aspen"},
    "bench_lower": {"label": "Lower tier / step: thermo-aspen, seat FL + 0.55", "d": 0.5, "h": 0.55, "mat": "aspen_low"},
    "heater": {"label": "Soapstone mass heater, hybrid: wood-fired from the changing room + electric in the same mass", "d": 0.75, "h": 1.6, "clear": 0.35, "mat": "soapstone"},
    "firebox": {"label": "Firebox door + hearth plate (slate), changing-room side", "d": 0.8, "h": 0.0, "mat": "stone"},
    "kindling": {"label": "Kindling basket", "d": 0.35, "h": 0.4, "mat": "oak"},
    "bench": {"label": "Walnut bench", "d": 0.45, "h": 0.45, "mat": "walnut"},
    "peg_rail": {"label": "Hooks (oak pegs on a slat rail)", "d": 0.12, "h": 1.7, "mat": "oak"},
    "towels": {"label": "Towel shelf (fresh, rolled)", "d": 0.4, "h": 1.8, "mat": "oak"},
    "tap_station": {"label": "Water: slate panel, chilled tap, birch cups", "d": 0.3, "h": 1.2, "mat": "stone"},
    "firewood": {"label": "Firewood stacked under the eave (birch)", "d": 0.45, "h": 1.8, "mat": "wood"},
    "sandals": {"label": "Robe hooks + sandal rack (porch)", "d": 0.35, "h": 1.7, "mat": "oak"},
    "porch_bench": {"label": "Porch bench (split log on stones)", "d": 0.4, "h": 0.45, "mat": "wood"},
    "deck": {"label": "Deck, Kebony", "d": 0.0, "h": 0.0, "mat": "deck"},
    "steps": {"label": "Steps (Kebony treads, 5 risers)", "d": 0.0, "h": 0.0, "mat": "deck_step"},
    "stone_steps": {"label": "Granite slab steps into the pool (6 risers, handrail)", "d": 0.0, "h": 0.0, "mat": "stone"},
    "badestamp": {"label": "Badestamp: wood-fired hot tub, 2.0 m (8 people), hybrid (wood stove + electric)", "d": 2.0, "h": 1.0, "shape": "circle", "mat": "tub"},
    "stamp_stove": {"label": "The tub's wood stove (steel, chimney pipe)", "d": 0.6, "h": 0.9, "mat": "steel"},
    "stamp_steps": {"label": "Oak steps up to the tub", "d": 0.6, "h": 0.5, "mat": "oak"},
    "flume": {"label": "Split-log flume on posts (pumped from the pool) to the tipping bucket", "d": 0.0, "h": 2.4, "mat": "water"},
    "tip_bucket": {"label": "Tipping bucket shower (cold)", "d": 0.8, "h": 2.4, "clear": 0.6, "mat": "wet_feature"},
    "duckboard": {"label": "Oak duckboards", "d": 1.0, "h": 0.03, "mat": "oak_solid"},
    "water_bucket": {"label": "Oak bucket + ladle (brass rim)", "d": 0.3, "h": 0.3, "mat": "oak"},
    "route": {"label": "Route (people flow)", "d": 0.0, "h": 0.0, "mat": "route"},
    "width_check": {"label": "Clear width at a pinch point", "d": 0.0, "h": 0.0, "mat": "route"},
}
items = []


def put(room, kind, x, y, w, rot=0.0, label=None, **kw):
    """x, y = centre; w = length along the piece; rot = which way its front faces (0 = +y / north, 90 = -x / west, 180 = -y, -90 = +x)."""
    k = KINDS[kind]
    items.append({"id": f"{room}-{kind}-{sum(1 for i in items if i['room'] == room and i['kind'] == kind) + 1}", "room": room, "kind": kind,
                  "label": label or k["label"], "x": round(x, 3), "y": round(y, 3), "w": round(w, 3), "d": kw.pop("d", k["d"]), "rot": rot,
                  "h": k["h"], **kw})


def poly(room, kind, pts, label=None, **kw):
    items.append({"id": f"{room}-{kind}-{sum(1 for i in items if i['room'] == room and i['kind'] == kind) + 1}", "room": room, "kind": kind,
                  "label": label or KINDS[kind]["label"], "pts": [[round(x, 3), round(y, 3)] for x, y in pts], **kw})


# ---------------------------------------------------------------- the shell (walls: centre line, thickness, z; openings along the wall)
xi0, xi1 = X0 + T, X1 - T                     # clear inside: -25.25 .. -20.75
yc0, yc1 = YP + T, YH                         # changing room: 93.65 .. 96.05
yh0, yh1 = YH + TP, Y1 - T                    # hot room: 96.20 .. 99.75
walls = [
    {"id": "KU-W-west", "from": [X0 + T / 2, Y0], "to": [X0 + T / 2, Y1], "size": [T, PLATE - FL], "z": [FL, PLATE], "kind": "exterior",
     "note": "the berm side: the porch's west wall too (holds the berm by the porch)"},
    {"id": "KU-W-north", "from": [X0, Y1 - T / 2], "to": [X1, Y1 - T / 2], "size": [T, PLATE - FL], "z": [FL, PLATE], "kind": "exterior"},
    {"id": "KU-W-east", "from": [X1 - T / 2, YP], "to": [X1 - T / 2, Y1], "size": [T, PLATE - FL], "z": [FL, PLATE], "kind": "exterior",
     "openings": [{"s": [0.9, 1.8], "z": [FL, FL + 2.05], "type": "door", "note": "out to the landing (glazed oak door)"},
                  {"s": [3.2, 5.7], "z": [FL + 0.7, FL + 2.1], "type": "window", "note": "the hot room's window to the pool: 3 panes, sill under the lower tier's eyes"}]},
    {"id": "KU-W-porch", "from": [X0, YP + T / 2], "to": [X1, YP + T / 2], "size": [T, PLATE - FL], "z": [FL, PLATE], "kind": "exterior",
     "openings": [{"s": [0.9, 1.8], "z": [FL, FL + 2.05], "type": "door", "note": "the way in from the porch (tarred plank door)"}]},
    {"id": "KU-W-hot", "from": [xi0, YH + TP / 2], "to": [xi1, YH + TP / 2], "size": [TP, FL + 2.3 - FL], "z": [FL, FL + 2.3], "kind": "partition",
     "openings": [{"s": [1.5, 2.0], "z": [FL + 0.3, FL + 0.75], "type": "firebox", "note": "the heater's firebox, fired from the changing room"},
                  {"s": [3.5, 4.25], "z": [FL, FL + 1.9], "type": "door", "note": "hot-room door: glass in an aspen frame, opens out"}]},
]
spaces = [
    {"id": "ku-porch", "name": "Porch", "poly": [[xi0, Y0], [X1, Y0], [X1, YP], [xi0, YP]]},
    {"id": "ku-changing", "name": "Changing", "poly": [[xi0, yc0], [xi1, yc0], [xi1, yc1], [xi0, yc1]]},
    {"id": "ku-hot", "name": "Hot room", "poly": [[xi0, yh0], [xi1, yh0], [xi1, yh1], [xi0, yh1]]},
]

# ---------------------------------------------------------------- hot room: the L of two tiers, the heater closes the U
UP, LO = 0.6, 0.5
put("ku-hot", "bench_upper", xi0 + UP / 2, (yh0 + yh1) / 2, yh1 - yh0, -90)                        # west run, faces east (the window)
put("ku-hot", "bench_upper", (xi0 + UP + xi1) / 2, yh1 - UP / 2, xi1 - xi0 - UP, 180)              # north run, faces south (the fire)
xh = -23.35
yl1 = yh1 - UP
put("ku-hot", "bench_lower", xi0 + UP + LO / 2, (yh0 + yl1) / 2, yl1 - yh0, -90)                   # west
put("ku-hot", "bench_lower", (xi0 + UP + LO + xi1) / 2, yl1 - LO / 2, xi1 - xi0 - UP - LO, 180)
put("ku-hot", "heater", xh, yh0 + 0.05 + 0.375, 0.9, 0)
put("ku-hot", "water_bucket", xh + 0.75, yh0 + 0.45, 0.3, 0)
put("ku-hot", "duckboard", (xi0 + UP + LO + xi1) / 2 - 0.15, (yh0 + 0.9 + yl1 - LO) / 2, 2.6, 0, d=yl1 - LO - yh0 - 0.9)
# ---------------------------------------------------------------- changing room
put("ku-changing", "firebox", xh, yc1 - 0.4, 0.9, 180)
put("ku-changing", "kindling", xh + 0.75, yc1 - 0.2, 0.4, 180)
put("ku-changing", "bench", xi0 + 0.225, (yc0 + yc1) / 2, 2.0, -90)
put("ku-changing", "peg_rail", xi0 + 0.06, (yc0 + yc1) / 2, 2.0, -90, label="Hooks over the bench (10 oak pegs)")
put("ku-changing", "towels", -22.2, yc0 + 0.2, 1.2, 0)
put("ku-changing", "tap_station", -21.15, yc0 + 0.15, 0.6, 0)
# ---------------------------------------------------------------- porch
put("ku-porch", "firewood", xi0 + 0.225, (Y0 + YP) / 2, YP - Y0 - 0.2, -90)
put("ku-porch", "sandals", -22.3, YP - 0.175, 2.6, 180)
put("ku-porch", "porch_bench", -23.6, Y0 + 0.4, 1.4, 0)
# ---------------------------------------------------------------- landing, steps, the lower deck, the pool
LX = -18.6
poly("ku-deck", "deck", [[X1, Y0], [LX, Y0], [LX, 95.6], [X1, 95.6]], label=f"Landing, Kebony, at the floor (+{FL - 0.02:.2f})", z=FL - 0.02)
poly("ku-deck", "steps", [[LX, 92.6], [LX + 1.2, 92.6], [LX + 1.2, 95.0], [LX, 95.0]], label="Steps down to the lower deck: 5 risers of 166, treads 300", z=[DECK_LO, FL - 0.02])
DE = -14.4  # the deck's east edge: ~2 m out over the water
poly("ku-deck", "deck", [[LX + 1.2, Y0], [DE, Y0], [DE, 98.6], [-18.0, 98.6], [-18.0, 95.6], [LX + 1.2, 95.6]],
     label=f"Lower deck, Kebony, {DECK_LO:+.2f} (1.17 above the pool), on piles to the rock", z=DECK_LO)
poly("ku-deck", "stone_steps", [[DE, 93.4], [DE + 2.1, 93.4], [DE + 2.1, 95.0], [DE, 95.0]],
     label="Granite slab steps into the pool: 6 risers down to 0.5 below the water", z=[WATER - 0.5, DECK_LO - 0.17])
put("ku-deck", "badestamp", -16.35, 97.3, 2.0, 180)
put("ku-deck", "stamp_stove", -14.95, 97.95, 0.6, 90)
put("ku-deck", "stamp_steps", -16.35, 95.95, 0.8, 180)
put("ku-deck", "tip_bucket", -15.3, 92.55, 0.8, 0)
poly("ku-deck", "flume", [[-14.6, 92.5], [-13.6, 92.5], [-12.4, 92.9]], label=KINDS["flume"]["label"], width=0.22)

# ---------------------------------------------------------------- checks: people flow + clear widths, seats, headroom
walls_u = []
for w in walls:
    (ax, ay), (bx, by) = w["from"], w["to"]
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; s0 = 0.0
    for a_, b_ in sorted(o["s"] for o in w.get("openings", []) if o["type"] == "door") + [[L, L]]:
        if a_ > s0:
            walls_u.append(LineString([(ax + ux * s0, ay + uy * s0), (ax + ux * a_, ay + uy * a_)]).buffer(w["size"][0] / 2, cap_style=2))
        s0 = max(s0, b_)
walk = unary_union([Polygon(s["poly"]) for s in spaces]).buffer(0.13, join_style=2).difference(unary_union(walls_u))


def foot(it):
    if it["kind"] in ("route", "width_check", "firebox", "duckboard", "flume") or "pts" in it:
        return None
    r = math.radians(it.get("rot", 0)); c, s = math.cos(r), math.sin(r); w, d = it["w"] / 2, it["d"] / 2
    return Polygon([(it["x"] + x * c - y * s, it["y"] + x * s + y * c) for x, y in ((-w, -d), (w, -d), (w, d), (-w, d))])


walk = walk.difference(unary_union([f for f in map(foot, [i for i in items if i["room"] != "ku-deck"]) if f is not None]))


def check(room, a, b, label, need):
    g = LineString([a, b]).intersection(walk)
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "LineString"]
    if not parts:
        return
    p = max(parts, key=lambda p: p.length); w = round(p.length, 2)
    st = "ok" if w >= need - 1e-4 else ("tight" if w >= 0.9 else "narrow")
    items.append({"id": f"chk-{len(items)}", "room": room, "kind": "width_check", "label": f"{label}: {w:.2f} m (needs {need})",
                  "pts": [[round(c[0], 3), round(c[1], 3)] for c in p.coords], "width": w, "need": need, "status": st})


check("ku-changing", (-23.0, yc0), (-23.0, yc1), "changing room, by the firebox hearth", 1.2)
check("ku-changing", (xi0, 95.0), (xi1, 95.0), "changing room, across", 1.5)
check("ku-hot", (-21.4, yh0), (-21.4, yh1), "hot room, from the door to the benches", 0.9)
check("ku-porch", (xi0, 92.7), (X1, 92.7), "porch, path to the door", 1.2)
for w in walls:
    for o in w.get("openings", []):
        if o["type"] == "door":
            (ax, ay), (bx, by) = w["from"], w["to"]; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
            a_, b_ = o["s"]; cw = round(b_ - a_, 2)
            items.append({"id": f"chk-{len(items)}", "room": "door", "kind": "width_check", "label": f"{o['note']}: {cw:.2f} m (needs 0.7 sauna / 0.9 other)",
                          "pts": [[round(ax + ux * a_, 3), round(ay + uy * a_, 3)], [round(ax + ux * b_, 3), round(ay + uy * b_, 3)]], "width": cw,
                          "need": 0.7 if "hot" in o["note"] else 0.9, "status": "ok" if cw >= (0.7 if "hot" in o["note"] else 0.9) else "narrow"})


def route(room, pts, label, cls="main"):
    items.append({"id": f"route-{len(items)}", "room": room, "kind": "route", "label": label, "pts": pts, "cls": cls})


route("ku-porch", [[-23.0, 90.6], [-23.0, 92.5], [-24.15, 93.0], [-24.15, 94.4]], "from the sauna path (the gym, 85 m) · robe off on the porch hooks")
route("ku-changing", [[-23.4, 94.6], [-21.4, 95.3], [-21.4, 97.0]], "into the hot room")
route("ku-changing", [[-21.4, 94.6], [-19.6, 94.75], [-18.2, 94.0], [-16.4, 94.0], [-14.6, 94.2]], "out to the deck, down the steps, into the pool", "wash")
route("ku-deck", [[-16.6, 94.2], [-16.35, 95.6]], "the hot tub", "branch")
route("ku-deck", [[-16.6, 93.6], [-15.6, 92.9]], "the tipping bucket", "branch")

seats_up = sum(i["w"] for i in items if i["kind"] == "bench_upper") / 0.6
seats_lo = sum(i["w"] for i in items if i["kind"] == "bench_lower") / 0.6
head_up = (FL + 2.3) - (FL + 1.0)
summary = [f"hot room {xi1 - xi0:.2f} x {yh1 - yh0:.2f} m clear, {(xi1 - xi0) * (yh1 - yh0):.1f} m2, {((xi1 - xi0) * (yh1 - yh0) * 2.3):.0f} m3",
           f"upper tier {int(seats_up)} seats, lower {int(seats_lo)} (600 a person): {int(seats_up)} in the heat",
           f"headroom over the upper tier {head_up:.2f} m (>= 1.1)",
           f"changing {xi1 - xi0:.2f} x {yc1 - yc0:.2f} m clear",
           f"floor +{FL:.2f} · landing +{FL - 0.02:.2f} · lower deck {DECK_LO:+.2f} · pool {WATER:+.2f}"]

# ---------------------------------------------------------------- the site under it: contours (0.5 m) from the finished ground + the water
H = np.load(ROOT / "construction" / "out" / "finished_1m.npy")
Wt = np.load(ROOT / "terrain" / "out" / "ravine" / "water_1m.npy")
vx0, vy0, vx1, vy1 = -32, 86, -8, 106
sub = H[1000 + vy0:1000 + vy1 + 1, 1000 + vx0:1000 + vx1 + 1]
import contourpy  # noqa: E402
cg = contourpy.contour_generator(np.arange(vx0, vx1 + 1, dtype=float), np.arange(vy0, vy1 + 1, dtype=float), sub)
contours = []
for z in np.arange(-3.0, 2.01, 0.5):
    for ln in cg.lines(z):
        if len(ln) > 2:
            contours.append({"z": round(float(z), 2), "pts": [[round(float(x), 2), round(float(y), 2)] for x, y in ln]})
wsub = ~np.isnan(Wt[1000 + vy0:1000 + vy1 + 1, 1000 + vx0:1000 + vx1 + 1])
wc = contourpy.contour_generator(np.arange(vx0, vx1 + 1, dtype=float), np.arange(vy0, vy1 + 1, dtype=float), wsub.astype(float))
water = [[[round(float(x), 2), round(float(y), 2)] for x, y in p] for p in wc.filled(0.5, 1.5)[0]] if wsub.any() else []

dims = [{"a": xi0, "b": xi1, "off": Y1 + 0.6, "horiz": True, "label": f"{xi1 - xi0:.2f} clear"},
        {"a": X0, "b": X1, "off": Y1 + 1.2, "horiz": True, "label": f"{X1 - X0:.2f}"},
        {"a": yh0, "b": yh1, "off": X0 - 0.6, "horiz": False, "label": f"{yh1 - yh0:.2f} hot room"},
        {"a": yc0, "b": yc1, "off": X0 - 0.6, "horiz": False, "label": f"{yc1 - yc0:.2f} changing"},
        {"a": Y0, "b": YP, "off": X0 - 0.6, "horiz": False, "label": f"{YP - Y0:.2f} porch"},
        {"a": Y0, "b": Y1, "off": X0 - 1.2, "horiz": False, "label": f"{Y1 - Y0:.2f}"}]

data = {"title": "Kulpen · the outdoor sauna · 2D",
        "note": "Kulpen, the outdoor sauna: the 2D layout (rules in tools/sauna_layout.py). Edited in blueprint/layout.html?name=sauna; x, y = centre "
                "in project metres, w along the piece, d front-to-back, rot = the way its front faces (0 = north). Walls and rooms are this file's own "
                "(the sauna is not in building.json yet).",
        "levels": {"floor": FL, "landing": FL - 0.02, "deck": DECK_LO, "water": WATER, "plate": PLATE, "hot_ceiling": FL + 2.3},
        "cut": FL + 1.5, "rooms": [s["id"] for s in spaces], "spaces": spaces, "walls": walls, "dims": dims, "summary": summary,
        "site": {"contours": contours, "water": water}, "view": [-31.0, -101.8, 20.0, 12.8], "kinds": KINDS, "items": items}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, indent=1))
print(f"wrote {OUT.relative_to(ROOT)}: {len(items)} items")
for s in summary:
    print(" ", s)
for i in items:
    if i["kind"] == "width_check":
        print(f"  [{i['status']:6s}] {i['label']}")

"""The gym floors' equipment, in 2D first (Roman, 2026-10-26): "place the equipment now that we have it all, in 2D first, sort of
top-down view, start planning off the original zones too, but now that we know the exact equipment that is the more source of
truth, to fit it in comfortably with the islands idea, to make it feel tight-knit but not just a maze, and not too expansive,
so you get the buff from other humans near you".

Writes model/layouts/gym_f1.json, gym_f2.json, gym_f3.json, gym_annex.json (shown + edited in blueprint/layout.html?name=gym_f2
...). Once Roman edits one there, the JSON is the source: this script won't overwrite it without --force.

Each piece is drawn at its true footprint from the equipment library (equipment/lineups/showroom_sizes.json, the bounding box of
the model as built), turned so that rot = the way its user faces (0 = north, 90 = west, -90 = east, 180 = south); `face` in its
kind says which of the model's own axes the user faces, so the 3D build can turn the model.py the same way. The dashed box round
each piece is its use + loading clearance (front, back, left, right as the user sees it). The PWR Play maze is drawn from its
Cores, stations and crossbars (equipment/lineups/pwr_play_stations.json, from equipment/tools/pwr_survey.py) and drags as one.
Floor-standing pieces only: bars, plates, collars, bells, mats, bands and the like live in the storage pieces drawn here.

    terrain/.venv/bin/python tools/gym_layout.py [--force]      # write the layouts
    terrain/.venv/bin/python tools/gym_layout.py check           # check the saved layouts (overlaps, walls, keep-clears, counts)
"""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
EQ = ROOT / "equipment"
OUTD = ROOT / "model" / "layouts"
M = json.loads((ROOT / "model" / "building.json").read_text())
SIZES = json.loads((EQ / "lineups" / "showroom_sizes.json").read_text())
PWR = json.loads((EQ / "lineups" / "pwr_play_stations.json").read_text())
LV = {l["id"]: l["elevation"] for l in M["levels"]}
BBOX = (-40.0, -41.0, -5.0, 16.0)                 # the gym wing + its annexes
SPIRAL = next(s for s in M["stairs"] if s["id"] == "spiral_west")
SPC, SPR = SPIRAL["center"], SPIRAL["diameter"] / 2
SPE = next(e for e in M["elements"] if e["id"] == "ST3-spiral_west")
BEAMS_Y = [-26.4, -18.7, -11.0, -3.3, 4.4]

LINKS = [{"name": "gym_f1", "label": "F1 · the hall: cardio, stretching, calisthenics"},
         {"name": "gym_f2", "label": "F2 · strength: free weights, olympic, legs, cardio"},
         {"name": "gym_f3", "label": "F3 · the den: upper-body maze, dumbbells, functional, strongman"},
         {"name": "lockers", "label": "F1 · the locker rooms"}, {"name": "sauna", "label": "Kulpen, the sauna"}]


# ---------------------------------------------------------------------------------------------------------------- the pieces
def title(piece):
    j = json.loads((EQ / "pieces" / piece / "piece.json").read_text())
    b, m_ = j.get("brand", ""), j.get("model") or j.get("title", piece)
    return m_ if m_.startswith(b) else f"{b} {m_}".strip()


def front_az(piece):
    import re
    t = (EQ / "pieces" / piece / "model.py").read_text()
    m_ = re.search(r'"front":\s*\((-?\d+)', t)
    return int(m_.group(1)) if m_ else 0


# the axis of the model the user faces (model.py "Axes:" lines); everything else faces -y
FACE = {"woodway-4front": "+y", "hammer-strength-hd-tread": "+y", "stairmaster-8gx-stepmill": "+y", "versaclimber-ts-magnetic": "+y",
        "body-solid-gvkr60b-vertical-knee-raise-dip": "-x", "gmwd-multi-functional-seal-row-bench-sr05": "-x",
        "atlantis-incline-calf-raise-m318": "-x", "hammer-strength-select-standing-calf": "+y", "life-fitness-axiom-series-leg-curl": "-x",
        "rogue-adjustable-bench-3-0": "-x", "rogue-manta-ray-adjustable-bench": "-x", "rogue-flat-utility-bench-2-0": "-x",
        "atlantis-olympic-flat-bench-press-with-pivot-p337": "-x", "atlantis-olympic-incline-bench-press-with-pivot-p338": "-x",
        "atlantis-olympic-flat-decline-bench-press-with-pivot-p339": "-x", "life-fitness-olympic-flat-bench": "-x",
        "hammer-strength-back-extension": "-x", "the-abs-company-the-nordic-curl": "-x", "titan-atlas-stone-platform": "+y",
        "life-fitness-pwr-play": "+y"}
AXV = {"+x": (1, 0), "-x": (-1, 0), "+y": (0, 1), "-y": (0, -1)}


def footprint(piece):
    """(w across the user, d along the way the user faces) from the showroom's box (the model turned by -front_az)."""
    s = SIZES[piece]
    az = front_az(piece) % 360
    mx, my = (s["w"], s["d"]) if az in (0, 180) else (s["d"], s["w"])     # the model's own x / y extents
    f = FACE.get(piece, "-y")
    return (my, mx) if f[1] == "x" else (mx, my)


# (tag, colour, use clearance front / back / left / right as the user faces), per piece; the defaults by kind of piece below
P = {}
def kind(tag, mat, use, *pieces):
    for p_ in pieces:
        P[p_] = (tag, mat, use)


C_TREAD, C_STAND, C_SEAT = (0.3, 2.0, 0.45, 0.45), (0.3, 0.6, 0.45, 0.45), (0.3, 0.5, 0.4, 0.4)
kind("treadmill", "cardio", C_TREAD, "woodway-4front"); kind("HD tread", "cardio", C_TREAD, "hammer-strength-hd-tread")
kind("stepmill", "cardio", C_STAND, "stairmaster-8gx-stepmill"); kind("elliptical", "cardio", C_STAND, "life-fitness-club-series-elliptical-cross-trainer")
kind("versaclimber", "cardio", (0.2, 0.9, 0.4, 0.4), "versaclimber-ts-magnetic")
kind("upright bike", "cardio", C_SEAT, "life-fitness-club-series-upright-lifecycle-bike"); kind("recumbent", "cardio", C_SEAT, "life-fitness-club-series-recumbent-lifecycle-bike")
kind("IC7", "cardio", C_SEAT, "life-fitness-ic7-indoor-cycle"); kind("air bike", "cardio", (0.3, 0.5, 0.5, 0.5), "hammer-strength-hd-air-bike")
kind("rower", "cardio", (0.3, 0.4, 0.55, 0.55), "life-fitness-row-hx-trainer"); kind("SkiErg", "cardio", (1.1, 0.2, 0.4, 0.4), "concept2-skierg")
C_SEL, C_PL = (0.7, 0.4, 0.5, 0.5), (0.8, 0.5, 0.75, 0.75)          # selectorized; plate-loaded (the plates go on at the sides)
for p_, t_ in (("life-fitness-insignia-series-leg-extension", "leg ext · LF"), ("hammer-strength-select-leg-extension", "leg ext · HS"),
               ("precor-resolute-series-leg-extension", "leg ext · Precor"), ("life-fitness-insignia-series-seated-leg-curl", "seated curl"),
               ("life-fitness-axiom-series-leg-curl", "lying curl"), ("hammer-strength-select-hip-abduction", "abduction"),
               ("hammer-strength-select-hip-adduction", "adduction"), ("life-fitness-insignia-series-calf-extension", "calf ext"),
               ("hammer-strength-select-standing-calf", "standing calf"), ("life-fitness-insignia-series-glute", "glute kickback"),
               ("hammer-strength-select-chest-press", "chest press"), ("hammer-strength-select-pectoral-fly-rear-deltoid", "pec fly / rear delt"),
               ("hammer-strength-select-biceps-curl", "biceps"), ("hammer-strength-seated-arm-curl", "preacher")):
    kind(t_, "machine", C_SEL, p_)
for p_, t_ in (("hammer-strength-plate-loaded-iso-lateral-leg-extension", "iso leg ext"), ("hammer-strength-plate-loaded-linear-leg-press", "leg press"),
               ("hammer-strength-plate-loaded-hack-squat", "hack squat"), ("hammer-strength-plate-loaded-pendulum-x-squat", "pendulum"),
               ("hammer-strength-plate-loaded-v-squat", "V-squat"), ("hammer-strength-plate-loaded-belt-squat", "belt squat"),
               ("hammer-strength-plate-loaded-glute-drive", "glute drive"), ("hammer-strength-plate-loaded-seated-calf-raise", "seated calf"),
               ("hammer-strength-plate-loaded-tibia-dorsi-flexion", "tibia"), ("hammer-strength-mts-kneeling-leg-curl", "kneeling curl"),
               ("atlantis-incline-calf-raise-m318", "incline calf M318"), ("hammer-strength-glute-ham-reverse-hyper-combo", "GHD / rev hyper"),
               ("hammer-strength-plate-loaded-iso-lateral-bench-press", "iso chest"), ("hammer-strength-plate-loaded-iso-lateral-incline-press", "iso incline"),
               ("hammer-strength-plate-loaded-iso-lateral-row", "iso row"), ("hammer-strength-plate-loaded-iso-lateral-front-lat-pulldown", "iso pulldown"),
               ("hammer-strength-plate-loaded-iso-lateral-shoulder-press", "iso shoulder"), ("hammer-strength-plate-loaded-t-bar-row", "T-bar row"),
               ("hammer-strength-plate-loaded-abdominal-oblique-crunch", "ab crunch")):
    kind(t_, "plate_loaded", C_PL, p_)
kind("smith", "plate_loaded", (1.0, 0.4, 0.4, 0.4), "life-fitness-smith-machine")
kind("rack", "rack", (0.0, 0.0, 0.0, 0.0), "rep-pr-5000-rack-builder", "rogue-monster-half-rack", "rogue-monster-lite-half-rack")
kind("rack platform", "platform", (1.2, 0.2, 0.0, 0.0), "titan-series-power-rack-lifting-platform")
kind("platform", "platform", (1.2, 0.6, 0.5, 0.5), "hammer-strength-impact-suppression-platform")
kind("rack platform", "platform", (1.2, 0.2, 0.2, 0.2), "hammer-strength-rubber-platform")
kind("deadlift platform", "platform", (1.0, 0.4, 0.4, 0.4), "rogue-deadlift-platform")
C_BST = (0.6, 0.3, 0.55, 0.55)                                   # bench stations: the feet clear, the plates at the bar's ends
kind("flat bench press", "bench", C_BST, "atlantis-olympic-flat-bench-press-with-pivot-p337", "life-fitness-olympic-flat-bench")
kind("incline bench press", "bench", C_BST, "atlantis-olympic-incline-bench-press-with-pivot-p338")
kind("decline bench press", "bench", C_BST, "atlantis-olympic-flat-decline-bench-press-with-pivot-p339")
C_BN = (0.5, 0.5, 0.8, 0.8)                                       # a free bench: the dumbbells swing out at its sides
kind("adj bench", "bench", C_BN, "rogue-adjustable-bench-3-0"); kind("Manta Ray", "bench", C_BN, "rogue-manta-ray-adjustable-bench")
kind("flat bench", "bench", (0.4, 0.4, 0.7, 0.7), "rogue-flat-utility-bench-2-0")
kind("seal row", "bench", (0.5, 0.5, 0.7, 0.7), "gmwd-multi-functional-seal-row-bench-sr05")
kind("GHD", "machine", (0.6, 0.6, 0.4, 0.4), "hammer-strength-fixed-pad-glute-ham")
kind("back ext", "machine", (0.6, 0.6, 0.4, 0.4), "hammer-strength-back-extension")
kind("nordic ham", "machine", (0.6, 1.2, 0.4, 0.4), "hammer-strength-assisted-nordic-ham"); kind("nordic curl", "machine", (1.2, 0.4, 0.4, 0.4), "the-abs-company-the-nordic-curl")
kind("VKR / dip", "machine", (0.6, 0.2, 0.3, 0.3), "body-solid-gvkr60b-vertical-knee-raise-dip")
C_RK = (1.3, 0.05, 0.2, 0.2)                                      # storage you pick from: room in front
kind("DB rack", "storage", C_RK, "hammer-strength-three-tier-dumbbell-rack"); kind("KB / accessory rack", "storage", C_RK, "life-fitness-3-tier-accessory-rack")
kind("plate tree", "storage", (0.6, 0.6, 0.6, 0.6), "life-fitness-olympic-weight-tree"); kind("bar holder", "storage", (0.9, 0.9, 0.3, 0.3), "rogue-10-bar-holder")
kind("fixed bars", "storage", C_RK, "life-fitness-barbell-rack"); kind("bumper rack", "storage", C_RK, "rogue-monster-bumper-rack")
kind("mass storage", "storage", C_RK, "rogue-monster-mass-storage"); kind("accessory rack", "storage", C_RK, "life-fitness-accessory-rack")
kind("med ball tree", "storage", (0.8, 0.1, 0.2, 0.2), "life-fitness-vertical-medicine-ball-storage")
kind("chalk", "storage", (0.5, 0.5, 0.5, 0.5), "rogue-freestanding-chalk-stand")
kind("jerk blocks", "platform", (0.8, 0.8, 0.5, 0.5), "rogue-wood-jerk-blocks")
kind("pull blocks", "platform", (0.3, 0.3, 0.3, 0.3), "titan-deadlift-pulling-blocks")
C_WALL = (1.2, 0.0, 0.1, 0.1)
kind("mat rack", "wallkit", C_WALL, "life-fitness-adjustable-wall-mounted-mat-rack"); kind("belts + bands", "wallkit", (0.8, 0, 0, 0), "rogue-belt-and-band-hanger")
kind("wall bars", "wallkit", (1.4, 0.0, 0.2, 0.2), "gymleco-wooden-wall-bars-with-chins-rack"); kind("timer", "wallkit", (0, 0, 0, 0), "rogue-echo-gym-timer-2-0")
kind("hangboard", "wallkit", (1.4, 0, 0.2, 0.2), "beastmaker-2000-series-hangboard"); kind("campus board", "wallkit", (1.6, 0, 0.2, 0.2), "metolius-wood-grips-campus-rungs")
kind("pegboard", "wallkit", (1.6, 0, 0.3, 0.3), "rogue-pine-maple-peg-board"); kind("wall-ball targets", "wallkit", (2.5, 0, 0.3, 0.3), "life-fitness-escape-endura-wall-balls")
kind("rig", "rack", (1.2, 1.2, 0.6, 0.6), "rogue-monster-rig-2-0"); kind("monkey rig", "rack", (1.4, 1.4, 0.6, 0.6), "rogue-monster-lite-monkey-rig-2-0")
kind("plyo boxes", "functional", (1.0, 0.2, 0.2, 0.2), "hammer-strength-3-in-1-wood-plyo-box", "hammer-strength-3-in-1-soft-plyo-box")
kind("plyo stack", "functional", (1.0, 0.2, 0.2, 0.2), "hammer-strength-stackable-plyo-box")
kind("battle rope", "functional", (0.0, 0.0, 0.0, 0.0), "life-fitness-battle-rope")
kind("yoke", "strongman", (1.5, 1.5, 0.4, 0.4), "rogue-yoke"); kind("stone platform", "strongman", (1.4, 0.3, 0.4, 0.4), "titan-atlas-stone-platform")
kind("atlas stones", "strongman", (0.6, 0.6, 0.3, 0.3), "rogue-rubber-atlas-stones")
kind("push sled", "strongman", (0.0, 1.2, 0.0, 0.0), "life-fitness-push-pull-weight-sled"); kind("drag sled", "strongman", (0.0, 0.0, 0.0, 0.0), "life-fitness-acft-sled-with-strap")
kind("stretch trainer", "machine", (0.4, 0.6, 0.4, 0.4), "life-fitness-flexibility-trainer"); kind("3D scanner", "machine", (1.0, 0.4, 0.3, 0.3), "fit3d-proscanner")
kind("parallel bars", "rack", (0.0, 0.0, 0.8, 0.8), "rogue-rig-mount-parallel-bars")
kind("parallettes", "functional", (0.3, 0.3, 0.3, 0.3), "rogue-bolt-together-parallette-set")
kind("stability balls", "storage", (0.6, 0.0, 0.1, 0.1), "hammer-strength-stability-ball")

KINDS_FIXED = {
    "void": {"label": "The spiral's opening (open to the floors above / below)", "d": 0, "h": 0, "mat": "void", "tag": "spiral"},
    "keep_clear": {"label": "Keep clear: a door's landing, the spiral's step-off, a lift's call space", "d": 0, "h": 0, "mat": "zone"},
    "turf": {"label": "Sled lane: 20 m of sled turf from the south wall (built, tools/interior.py)", "d": 0, "h": 0, "mat": "turf", "tag": "sled lane"},
    "den_river": {"label": "Bekken i hulen: the den's river (built: the rock base, the pool, the outfall slit)", "d": 0, "h": 0, "mat": "feature", "tag": "the den river"},
    "stair": {"label": "Stair (opening)", "d": 0, "h": 0, "mat": "void", "tag": "stair"},
    "tap_station": {"label": "Water station: chilled tap (built)", "d": 0.13, "h": 1.2, "mat": "fixture", "tag": "water"},
    "safety_point": {"label": "Safety point: AED, extinguisher, first aid (built)", "d": 0.15, "h": 1.5, "mat": "fixture", "tag": "AED"},
    "wipe_station": {"label": "Wipes + bin, brushed stainless (built as placeholders: repositioned with the equipment)", "d": 0.36, "h": 1.1, "mat": "fixture", "tag": "wipes", "use": [0.5, 0, 0, 0]},
    "floor_zone": {"label": "Floor zone", "d": 1.0, "h": 0.0, "mat": "zone"},
    "select_shoulder": {"label": "Hammer Strength Select Shoulder Press (not picked or modelled yet: the HS Select line, to match the chest press; size estimated)",
                        "d": 1.3, "h": 1.6, "mat": "machine", "tag": "shoulder press", "use": [0.7, 0.4, 0.5, 0.5]},
    "rig_spur": {"label": "Pull-up station (to model: from the Monster Lite Monkey Rig's parts): two 108 in uprights on floor plates, a pull-up bar between them at 2.47 m+ (the 6 ft 3 in dead-hang rule)",
                 "d": 0.08, "h": 2.74, "mat": "rack", "tag": "pull-up bar", "use": [0.9, 0.9, 0.15, 0.15]},
    "pwr_core": {"label": "Life Fitness PWR Play: a Core (four faces, a station on each)", "d": PWR["core"][1], "h": 2.415, "mat": "pwr", "tag": "core"},
    "pwr_bar": {"label": "PWR Play crossbar (Long connector) with pull-up handles, over the aisle at 2.31 m", "d": 0.08, "h": 2.35, "mat": "pwr"},
}
ST_USE = {"pulldown": 0.35, "row": 0.3, "triceps": 1.0, "adjustable": 1.5, "crossover": 1.5, "dualhigh": 1.3, "duallow": 1.3, "dip": 0.6,
          "panel": 0.0, "step": 0.7, "handles": 0.6, "stallbars": 1.0, "ropepull": 0.9, "powerpivot": 0.8, "dipchin": 0.4}
ST_TAG = {"pulldown": "pulldown", "row": "row", "triceps": "triceps", "adjustable": "adj pulley", "crossover": "crossover", "dualhigh": "dual high",
          "duallow": "dual low", "dip": "dip", "panel": "", "step": "step", "handles": "handles", "stallbars": "stall bars", "ropepull": "rope pull",
          "powerpivot": "power pivot", "dipchin": "assist dip/chin"}
for st, use in ST_USE.items():
    KINDS_FIXED[f"pwr_{st}"] = {"label": f"PWR Play station: {ST_TAG[st] or 'blank panel'}", "d": 0, "h": 2.3, "mat": "pwr",
                                "tag": ST_TAG[st], "use": [use, 0, 0.1, 0.1]}


def kinds_for(pieces):
    out = dict(KINDS_FIXED)
    for p_ in sorted(pieces):
        tag, mat, use = P.get(p_, (p_.split("-")[-1], "machine", (0.6, 0.4, 0.4, 0.4)))
        w, d = footprint(p_)
        out[p_] = {"label": title(p_), "d": round(d, 3), "h": SIZES[p_]["h"], "mat": mat, "tag": tag, "use": list(use),
                   "face": FACE.get(p_, "-y"), "piece": p_}
    return out


# ---------------------------------------------------------------------------------------------------------------- the building
def walls(level):
    z = LV[level] + 1.0
    x0, y0, x1, y1 = BBOX
    out = []
    for e in M["elements"]:
        if e["type"] != "wall" or e.get("kind") in ("lining", "stone", "trim") or not e.get("from"):
            continue
        if not (e["z"][0] <= z <= e["z"][1]):
            continue
        (fx, fy), (tx, ty) = e["from"], e["to"]
        if max(fx, tx) < x0 or min(fx, tx) > x1 or max(fy, ty) < y0 or min(fy, ty) > y1:
            continue
        ops = []
        for o in e.get("openings", []):
            if o["z"][0] <= z <= o["z"][1]:
                t = "window" if o["type"] in ("window", "river") else o["type"]
                ops.append({"s": o["s"], "z": [round(o["z"][0] - LV[level], 3), round(o["z"][1] - LV[level], 3)], "type": t, "note": o.get("note", "")})
        out.append({"id": e["id"], "type": "wall", "kind": e.get("kind"), "material": e.get("material", ""), "from": e["from"], "to": e["to"],
                    "size": e["size"], "z": [round(e["z"][0] - LV[level], 3), round(e["z"][1] - LV[level], 3)], "openings": ops})
    return out


def spaces(level, ids=None):
    out = []
    for s in M["spaces"]:
        if s["level"] != level:
            continue
        xs = [p_[0] for p_ in s["poly"]]
        if max(xs) < BBOX[0] or min(xs) > -6.0:
            continue
        if ids and s["id"] not in ids:
            continue
        out.append({"id": s["id"], "level": s["level"], "name": s["name"], "poly": s["poly"]})
    return out


def landings(ws, level, room):
    """A keep-clear landing in front of every door / lift opening, on the room side (1.5 m deep)."""
    out = []
    for w in ws:
        (ax, ay), (bx, by) = w["from"], w["to"]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        for o in w["openings"]:
            if o["type"] not in ("door", "opening"):
                continue
            s0, s1 = o["s"]; mx, my = ax + ux * (s0 + s1) / 2, ay + uy * (s0 + s1) / 2
            for sg in (1, -1):
                nx, ny = -uy * sg, ux * sg
                c = (mx + nx * (w["size"][0] / 2 + 0.75), my + ny * (w["size"][0] / 2 + 0.75))
                if room.contains(Point(c)):
                    W, D = s1 - s0 + 0.3, 1.5
                    pts = [(mx + ux * a + nx * (w["size"][0] / 2 + b), my + uy * a + ny * (w["size"][0] / 2 + b))
                           for a, b in ((-W / 2, 0), (W / 2, 0), (W / 2, D), (-W / 2, D))]
                    out.append({"id": f"clear-{w['id']}-{s0:.2f}-{sg}", "room": "", "kind": "keep_clear", "label": f"Keep clear: {o['note'] or o['type']}",
                                "pts": [[round(x, 3), round(y, 3)] for x, y in pts], "fixed": True})
    return out


def overhead(level, light=True):
    out = []
    for e in M["elements"]:
        if e["type"] == "beam" and e["id"].endswith(f"-{level}-west") or (e["type"] == "beam" and level == "F1" and e["id"].endswith("-RF-west")):
            if level == "F1" and not e["id"].endswith("-RF-west"):
                continue
            out.append({"pts": [e["from"], e["to"]], "cls": "beam", "label": f"{e['id']}: beam overhead, {e['size'][0]} x {e['size'][1]} m"})
    if light:
        for f in M["furnishings"]:
            if f["kind"] == "gym_line" and f["level"] == level:
                x, y = f["at"][:2]; L = f.get("L", 1.0)
                out.append({"pts": [[x - L / 2, y], [x + L / 2, y]], "cls": "light", "label": f"light line overhead ({f.get('temp', '')} K)"})
    return out


def fixtures(level):
    out = []
    for f in M["furnishings"]:
        if f["level"] != level or f["kind"] not in ("tap_station", "safety_point", "wipe_station"):
            continue
        x, y = f["at"][:2]
        if not (BBOX[0] < x < -6.0 and BBOX[1] < y < BBOX[3]):
            continue
        k = f["kind"]
        w = {"tap_station": 0.35, "safety_point": 0.6, "wipe_station": 0.36}[k]
        out.append({"id": f"{k}-{level}-{x:.1f}-{y:.1f}", "room": "", "kind": k, "label": KINDS_FIXED[k]["label"], "x": x, "y": y,
                    "w": w, "d": KINDS_FIXED[k]["d"], "rot": f.get("rot_deg", 0) or 0, "fixed": k != "wipe_station", "note": f.get("note", "")})
    return out


def circle(c, r, n=48):
    return [[round(c[0] + r * math.cos(2 * math.pi * i / n), 3), round(c[1] + r * math.sin(2 * math.pi * i / n), 3)] for i in range(n)]


def spiral_items(level):
    """The spiral's opening + the walk round it, and where you step on / off on this floor."""
    out = [{"id": f"spiral-{level}", "room": "", "kind": "void", "label": KINDS_FIXED["void"]["label"], "pts": circle(SPC, SPR), "fixed": True}]
    z0, z1 = SPE["z"]; rr = (z1 - z0) / SPE["risers"]
    if level == "F3":
        a = SPE["a0"]
    elif level == "F2":
        a = SPE["a0"] + SPE["step_deg"] * (round((LV["F2"] - z0) / rr) - 1)
    else:
        a = SPE["a0"] + SPE["step_deg"] * SPE["risers"] + 22.5
    a = math.radians(a % 360)
    W, D = 1.6, 1.8
    ux, uy = math.cos(a), math.sin(a); tx, ty = -uy, ux
    cx, cy = SPC[0] + ux * SPR, SPC[1] + uy * SPR
    pts = [(cx + tx * s + ux * t, cy + ty * s + uy * t) for s, t in ((-W / 2, 0), (W / 2, 0), (W / 2, D), (-W / 2, D))]
    out.append({"id": f"spiral-landing-{level}", "room": "", "kind": "keep_clear", "label": "Keep clear: the spiral's step-off on this floor",
                "pts": [[round(x, 3), round(y, 3)] for x, y in pts], "fixed": True})
    return out


# ---------------------------------------------------------------------------------------------------------------- placing
class Floor:
    def __init__(self, level, title_, view, rooms=None):
        self.level, self.title, self.view = level, title_, view
        self.items, self.n, self.targets, self.notes = [], {}, {}, []
        self.rooms = rooms
        self.room_ids, self.walls = [], []

    def put(self, piece, x, y, rot=0, zone="", note="", on=None, n=None):
        """A piece at (x, y), its user facing rot (0 N, 90 W, -90 E, 180 S)."""
        w, d = footprint(piece)
        self.n[piece] = self.n.get(piece, 0) + 1
        it = {"id": f"{piece}-{self.n[piece]}", "room": zone, "kind": piece, "label": title(piece), "x": round(x, 3), "y": round(y, 3),
              "w": round(w, 3), "d": round(d, 3), "rot": rot, "h": SIZES[piece]["h"]}
        if note:
            it["note"] = note
        if on:
            it["on"] = on
        self.items.append(it)
        return it

    def row(self, pieces, x, y, rot, gap, zone="", align="front", note=""):
        """A row of pieces side by side (across the way their users face), from (x, y) along the users' left-to-right... simply
        along +x for rot 0/180 and along +y for rot +-90; `align` lines up their fronts (default) or centres."""
        out = []
        along = (1, 0) if rot in (0, 180) else (0, 1)
        fdir = (-math.sin(math.radians(rot)), math.cos(math.radians(rot)))
        pos = 0.0
        for p_ in pieces:
            w, d = footprint(p_)
            cx = x + along[0] * (pos + w / 2); cy = y + along[1] * (pos + w / 2)
            if align == "front":                                    # (x, y) is on the fronts' line
                cx -= fdir[0] * d / 2; cy -= fdir[1] * d / 2
            out.append(self.put(p_, cx, cy, rot, zone, note))
            pos += w + gap
        return out

    def zone(self, label, x0, y0, x1, y1, zid=None):
        self.items.append({"id": zid or f"zone-{len(self.items)}", "room": "", "kind": "floor_zone", "label": label,
                           "x": round((x0 + x1) / 2, 3), "y": round((y0 + y1) / 2, 3), "w": round(x1 - x0, 3), "d": round(y1 - y0, 3), "rot": 0})

    def maze(self, name, cores, faces, bars, origin=(0.0, 0.0), zone=""):
        """A PWR Play maze: cores {n: (i, j)} on the Long connector's grid from origin; faces {(n, 'N'|'E'|'S'|'W'): station};
        bars [(a, b)]. Everything in it shares the group."""
        D = PWR["spacing"]["long"]; cw = PWR["core"][0]
        g = f"maze-{name}"
        pos = {n: (origin[0] + i * D, origin[1] + j * D) for n, (i, j) in cores.items()}
        for n, (cx, cy) in pos.items():
            self.items.append({"id": f"{g}-core-{n}", "room": zone, "kind": "pwr_core", "label": f"PWR Play Core {n}", "x": round(cx, 3), "y": round(cy, 3),
                               "w": cw, "d": cw, "rot": 0, "group": g})
        rots = {"N": 0, "W": 90, "S": 180, "E": -90}
        dirs = {"N": (0, 1), "W": (-1, 0), "S": (0, -1), "E": (1, 0)}
        for (n, f), st in faces.items():
            if st is None:
                continue
            s = PWR["stations"][st]; out_ = max(s["out"], cw / 2 + 0.02)
            depth = out_ - cw / 2
            if depth < 0.03:
                continue
            (cx, cy), (dx, dy) = pos[n], dirs[f]
            c = (cx + dx * (cw / 2 + depth / 2), cy + dy * (cw / 2 + depth / 2))
            self.items.append({"id": f"{g}-{n}{f}-{st}", "room": zone, "kind": f"pwr_{st}", "label": f"PWR Play {ST_TAG[st] or 'panel'} (Core {n}, {f} face)",
                               "x": round(c[0], 3), "y": round(c[1], 3), "w": round(2 * s["half"], 3), "d": round(depth, 3), "rot": rots[f], "group": g,
                               "core": n, "face": f, "station": st})
        for a, b in bars:
            (xa, ya), (xb, yb) = pos[a], pos[b]
            horiz = abs(yb - ya) < 1e-6
            L = abs(xb - xa) + abs(yb - ya) - cw
            self.items.append({"id": f"{g}-bar-{a}{b}", "room": zone, "kind": "pwr_bar", "label": f"PWR Play crossbar {a}-{b} (pull-ups)",
                               "x": round((xa + xb) / 2, 3), "y": round((ya + yb) / 2, 3), "w": round(L, 3), "d": 0.08, "rot": 0 if horiz else 90, "group": g,
                               "bar": [a, b]})
        self.items.append({"id": f"{g}-meta", "room": zone, "kind": "pwr_meta", "label": f"maze {name}", "group": g, "fixed": True,
                           "cores": {n: list(v) for n, v in cores.items()}, "origin": list(origin), "spacing": D,
                           "faces": {f"{n},{f}": st for (n, f), st in faces.items()}, "bars": [list(b_) for b_ in bars]})

    def route(self, rid, pts, label, cls="main", width=1.7):
        """A walking route (drawn as an arrow): nothing may stand in its width."""
        self.items.append({"id": rid, "room": "", "kind": "route", "label": f"Route: {label}", "pts": [list(p_) for p_ in pts], "cls": cls,
                           "width": width, "fixed": True})

    def target(self, piece, n):
        self.targets[piece] = self.targets.get(piece, 0) + n

    def write(self, name, ws, sps, extra, dims=None, summary=None):
        """(walls + room ids are also kept on the floor for auto_wipes: set_room before placing)"""
        pieces = {it["kind"] for it in self.items if it["kind"] in SIZES} | set(self.targets)
        data = {"note": f"{self.title}: the 2D equipment layout (tools/gym_layout.py writes the first proposal; edited in blueprint/layout.html?name={name}). "
                        "x, y = centre in project metres; w across the user, d along the way the user faces; rot = the way the user faces (0 = north, 90 = west, -90 = east).",
                "title": self.title, "level": self.level, "cut": 1.0, "rooms": [],
                "view": [self.view[0], -self.view[3], round(self.view[2] - self.view[0], 3), round(self.view[3] - self.view[1], 3)],   # svg x, y (= -north), w, h "links": LINKS,
                "walls": ws, "spaces": sps, "overhead": extra.get("overhead", []), "dims": dims or [],
                "summary": summary or [], "kinds": kinds_for(pieces), "targets": dict(sorted(self.targets.items(), key=lambda kv: kv[0])),
                "items": extra.get("fixed", []) + self.items}
        f = OUTD / f"{name}.json"
        if f.exists() and "--force" not in sys.argv:
            print("kept (edited in blueprint/layout.html):", f.relative_to(ROOT), "· --force to regenerate")
            return
        f.write_text(json.dumps(data, indent=1))
        print("wrote", f.relative_to(ROOT), len(self.items), "items")


def room_poly(level, ids):
    return unary_union([Polygon(s["poly"]) for s in M["spaces"] if s["level"] == level and s["id"] in ids])


# ---------------------------------------------------------------------------------------------------------------- checking
def item_poly(it, kinds, use=False):
    if it.get("poly") is not None:
        return it["poly"]
    if it.get("pts"):
        return Polygon(it["pts"])
    if "x" not in it:
        return None
    w, d = it.get("w", 1), it.get("d", 1)
    f = b = l = r = 0.0
    if use:
        u = kinds.get(it["kind"], {}).get("use")
        if not u:
            return None
        f, b, l, r = u
    loc = box(-w / 2 - l, -d / 2 - b, w / 2 + r, d / 2 + f)
    a = math.radians(it.get("rot", 0) or 0)
    from shapely import affinity
    return affinity.translate(affinity.rotate(loc, a, origin=(0, 0), use_radians=True), it["x"], it["y"])


def check(name):
    data = json.loads((OUTD / f"{name}.json").read_text())
    K = data["kinds"]
    room = unary_union([Polygon(s["poly"]) for s in data["spaces"]])
    wallp = []
    for w in data["walls"]:
        (ax, ay), (bx, by) = w["from"], w["to"]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; t = w["size"][0] / 2
        wallp.append(Polygon([(ax - uy * t, ay + ux * t), (bx - uy * t, by + ux * t), (bx + uy * t, by - ux * t), (ax + uy * t, ay - ux * t)]))
    walls_u = unary_union(wallp)
    eq = [it for it in data["items"] if not it.get("fixed") and it["kind"] not in ("floor_zone", "pwr_meta", "pwr_bar")]
    keep = [it for it in data["items"] if it["kind"] in ("keep_clear", "void", "stair", "den_river")]
    from shapely.geometry import LineString
    for r_ in [it for it in data["items"] if it["kind"] == "route"]:
        keep.append({"id": r_["id"], "kind": "route", "poly": LineString(r_["pts"]).buffer(r_.get("width", 1.7) / 2, cap_style=2)})
    probs = []
    bodies = {it["id"]: item_poly(it, K) for it in eq}
    uses = {it["id"]: item_poly(it, K, use=True) for it in eq}
    for it in eq:
        bp = bodies[it["id"]]
        if bp is None:
            continue
        if bp.intersection(walls_u).area > 0.005:
            probs.append(f"! {it['id']}: into a wall ({bp.intersection(walls_u).area:.2f} m²)")
        if not room.buffer(0.4, join_style=2).difference(walls_u).buffer(0.02).contains(bp):   # the zones are drawn to the walls' centre lines
            probs.append(f"! {it['id']}: outside the rooms")
        for k_ in keep:
            a_ = bp.intersection(item_poly(k_, K)).area
            if a_ > 0.01:
                probs.append(f"! {it['id']}: on {k_['kind']} {k_['id']} ({a_:.2f} m²)")
    byid = {it["id"]: it for it in data["items"]}
    def root(it):
        while it.get("on") in byid:
            it = byid[it["on"]]
        return it["id"]
    quiet = ("storage", "fixture")                                   # trees / racks you load from sit in the use space on purpose
    for i, a in enumerate(eq):
        for b in eq[i + 1:]:
            if root(a) == root(b) or (a.get("group") and a.get("group") == b.get("group")):
                continue
            pa, pb = bodies[a["id"]], bodies[b["id"]]
            if pa is None or pb is None:
                continue
            ov = pa.intersection(pb).area
            if ov > 0.005:
                probs.append(f"! {a['id']} x {b['id']}: overlap {ov:.2f} m²")
                continue
            for x_, y_ in ((a, b), (b, a)):
                u = uses[x_["id"]]
                if u is not None and x_.get("on") is None and y_.get("on") is None and K.get(y_["kind"], {}).get("mat") not in quiet and K.get(x_["kind"], {}).get("mat") not in quiet:
                    ov = u.intersection(bodies[y_["id"]]).area
                    if ov > 0.2:
                        probs.append(f"~ {y_['id']} in {x_['id']}'s use space ({ov:.2f} m²)")
    # wall kit must touch a wall
    for it in eq:
        if K.get(it["kind"], {}).get("mat") == "wallkit" and bodies[it["id"]].distance(walls_u) > 0.06:
            probs.append(f"! {it['id']}: wall-mounted but not on a wall ({bodies[it['id']].distance(walls_u):.2f} m off)")
    cnt = {}
    for it in data["items"]:
        cnt[it["kind"]] = cnt.get(it["kind"], 0) + 1
    for k_, t in data.get("targets", {}).items():
        if cnt.get(k_, 0) < t:
            probs.append(f"! short: {k_} {cnt.get(k_, 0)}/{t}")
    area = room.area - sum(item_poly(k_, K).intersection(room).area for k_ in keep if k_["kind"] in ("void", "stair", "den_river"))
    used = unary_union([p_ for p_ in list(bodies.values()) + [u for u in uses.values() if u is not None] if p_ is not None]).intersection(room).area
    body = unary_union([p_ for p_ in bodies.values() if p_ is not None]).intersection(room).area
    print(f"{name}: {len(eq)} pieces · floor {area:.0f} m² · equipment {body:.0f} m² ({100 * body / area:.0f}%) · with use space {used:.0f} m² ({100 * used / area:.0f}%)")
    for p_ in probs:
        print("  ", p_)
    return probs


# ---------------------------------------------------------------------------------------------------------------- the floors
from gym_layout_plan import plan_f1, plan_f2, plan_f3, plan_annex  # noqa: E402  (the placements: tools/gym_layout_plan.py)

if __name__ == "__main__":
    if sys.argv[1:2] == ["check"]:
        for nm in (sys.argv[2:] or ["gym_f1", "gym_f2", "gym_f3"]):
            if (OUTD / f"{nm}.json").exists():
                check(nm)
        sys.exit(0)
    for fn in (plan_f1, plan_f2, plan_f3, plan_annex):
        fn(sys.modules[__name__])

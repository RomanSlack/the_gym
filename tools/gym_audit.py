"""Spacing audit of the gym layouts against the NSCA facility numbers (docs/GYM_DESIGN_PRINCIPLES.md): barbell stations 0.9 m clear,
benches 0.9 m apart, machines 0.6 m, cardio 0.5 m, pull-up stations 1.2 m; plates within 0.9 m of every loaded station without its
own horns; bumpers within 1.5 m of every olympic platform. Back-to-back machines and a pod's own bench show up; they're fine.

    cd tools && ../terrain/.venv/bin/python gym_audit.py gym_f1 gym_f2 gym_f3
"""
import json, sys
from pathlib import Path
import gym_layout as G
ROOT = Path(__file__).resolve().parents[1]
def cat(it, K):
    t = (K.get(it["kind"], {}).get("tag") or "").lower(); k = it["kind"]
    if k.startswith("pwr_") or it["id"].startswith("maze-"): return None
    if "parallette" in k: return "kit"
    if any(c in k for c in ("elliptical", "stepmill", "versaclimber", "bike", "ic7", "row-hx", "skierg", "air-bike", "rower", "woodway", "tread")): return "cardio"
    if k in ("floor_zone", "keep_clear", "route", "void", "pwr_meta", "wipe_station", "tap_station", "safety_point", "stair", "den_river", "turf"): return None
    if "platform" in t and "rack" not in t: return "platform"
    if t in ("rack", "smith", "deadlift platform") or "half-rack" in k: return "barbell"
    if "bench press" in t: return "barbell"
    if "bench" in t: return "bench"
    if t in ("pull-up bar", "muscle-up bar"): return "pullup"
    if "treadmill" in t or "tread" in t: return "tread"
    if any(s in t for s in ("plate tree", "bumper rack", "bar holder", "chalk", "timer", "belts", "db rack", "kb", "rack platform", "jerk", "pull blocks", "water", "wipes", "accessory", "mat rack", "med ball", "storage", "ball")): return "kit"
    return "machine"
NEED = {("barbell", "*"): 0.9, ("platform", "*"): 0.9, ("bench", "bench"): 0.9, ("machine", "machine"): 0.6, ("pullup", "pullup"): 1.2, ("bench", "machine"): 0.6, ("cardio", "cardio"): 0.5}
def need(a, b):
    for x, y in ((a, b), (b, a)):
        if (x, "*") in NEED and y not in ("kit", "platform"): return NEED[(x, "*")]
        if (x, y) in NEED: return NEED[(x, y)]
    return None
from shapely.geometry import LineString  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
for name in sys.argv[1:]:
    d = json.load(open(ROOT / "model" / "layouts" / f"{name}.json")); K = d["kinds"]
    WALLS = unary_union([LineString([w["from"], w["to"]]).buffer(w["size"][0] / 2) for w in d["walls"]])
    its = [it for it in d["items"] if "x" in it and cat(it, K)]
    P = {it["id"]: G.item_poly(it, K) for it in its}
    probs = []
    for i, a in enumerate(its):
        for b in its[i + 1:]:
            if a.get("on") == b["id"] or b.get("on") == a["id"]: continue
            n = need(cat(a, K), cat(b, K))
            if n is None or P[a["id"]] is None or P[b["id"]] is None: continue
            if P[a["id"]].intersects(P[b["id"]]): continue   # sits on it (rack on its platform)
            if LineString([P[a["id"]].centroid, P[b["id"]].centroid]).intersects(WALLS): continue   # a wall between them
            g = P[a["id"]].distance(P[b["id"]])
            if g < n - 0.05: probs.append((round(n - g, 2), f"{a['id']} [{cat(a,K)}] <-> {b['id']} [{cat(b,K)}]: {g:.2f} m, want {n}"))
    kits = [it for it in its if (K.get(it["kind"], {}).get("tag") or "") in ("plate tree", "bumper rack")]
    for a in its:
        if cat(a, K) == "platform" and "impact-suppression" in a["kind"]:
            dmin = min([P[a["id"]].distance(P[k["id"]]) for k in kits] or [99])
            if dmin > 1.5: probs.append((dmin, f"{a['id']} [olympic platform]: nearest bumper storage {dmin:.1f} m"))
    for a in its:
        if cat(a, K) == "barbell" and not any(s_ in a["kind"] for s_ in ("rep-pr-5000", "half-rack", "atlantis", "smith")):   # built-in plate posts / horns
            dmin = min([P[a["id"]].distance(P[k["id"]]) for k in kits] or [99])
            if dmin > 0.9: probs.append((dmin, f"{a['id']} [{K[a['kind']]['tag']}]: nearest plate storage {dmin:.1f} m"))
    print(f"== {name}: {len(probs)}")
    for s, p in sorted(probs, reverse=True): print("  ", p)

# ---- placement sense (2026-10-30, Roman: "a dip bar positioned right in front of the medical equipment ... look for other obvious
# issues like that"): nothing hung on or parked against a mirror, wall pieces on a wall, no tall kit over a wall light, no wipes
# station in a walkway or on a platform (the AED / water access zones are keep-clears in gym_layout.fixtures, so G.check flags those)
from shapely.geometry import LineString, Point  # noqa: E402
_M = json.loads((ROOT / "model" / "building.json").read_text())
_lv = {l_["id"]: l_["elevation"] for l_ in _M["levels"]}
for name in sys.argv[1:]:
    d = json.loads((ROOT / "model" / "layouts" / f"{name}.json").read_text()); K = d["kinds"]; z = _lv[d["level"]]
    mirrors = [LineString([e["from"], e["to"]]) for e in _M["elements"] if e.get("material") == "mirror" and e.get("kind") == "lining" and abs(e["z"][0] - z) < 1.0]
    walls = [LineString([w["from"], w["to"]]).buffer(w["size"][0] / 2) for w in d["walls"]]
    lights = [Point(f["at"]) for f in _M["furnishings"] if f["kind"] == "eclipse_sconce" and f.get("level") == d["level"]]
    no_wipes = [G.item_poly(i, K) for i in d["items"] if i["kind"] == "floor_zone" and i["label"].startswith(("Walkway", "The pod's"))]
    out = []
    for it in d["items"]:
        if "x" not in it or it.get("fixed") or it["kind"] in ("floor_zone", "route", "keep_clear"):
            continue
        p = G.item_poly(it, K)
        if p is None:
            continue
        dm = min([p.distance(l_) for l_ in mirrors] or [99])   # (2026-10-31: dumbbell racks under the mirror are right; NSCA: 6 in clear of the glass)
        if it["kind"] != "wipe_station" and not it.get("on") and (dm < 0.14 or (dm < 0.3 and K.get(it["kind"], {}).get("mat") == "wallkit")):
            out.append(f"{it['id']}: on / against a mirror ({dm:.2f} m)")
        if K.get(it["kind"], {}).get("wall") and not any(p.distance(w) < 0.05 for w in walls):
            out.append(f"{it['id']}: a wall piece off the wall")
        if it.get("h", 0) > 1.4 and any(p.distance(s) < 0.3 for s in lights):
            out.append(f"{it['id']}: tall kit over a wall light")
        if it["kind"] == "wipe_station" and any(z_ is not None and z_.intersects(p) for z_ in no_wipes):
            out.append(f"{it['id']}: wipes in a walkway / on a platform")
    print(f"== {name} placement: {len(out)}")
    for o in out:
        print("  ", o)

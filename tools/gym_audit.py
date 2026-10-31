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
    if t in ("pull-up bar",): return "pullup"
    if "treadmill" in t or "tread" in t: return "tread"
    if any(s in t for s in ("plate tree", "bumper rack", "bar holder", "chalk", "timer", "belts", "db rack", "kb", "rack platform", "jerk", "pull blocks", "water", "wipes", "accessory", "mat rack", "med ball", "storage", "ball")): return "kit"
    return "machine"
NEED = {("barbell", "*"): 0.9, ("platform", "*"): 0.9, ("bench", "bench"): 0.9, ("machine", "machine"): 0.6, ("pullup", "pullup"): 1.2, ("bench", "machine"): 0.6, ("cardio", "cardio"): 0.5}
def need(a, b):
    for x, y in ((a, b), (b, a)):
        if (x, "*") in NEED and y not in ("kit", "platform"): return NEED[(x, "*")]
        if (x, y) in NEED: return NEED[(x, y)]
    return None
for name in sys.argv[1:]:
    d = json.load(open(ROOT / "model" / "layouts" / f"{name}.json")); K = d["kinds"]
    its = [it for it in d["items"] if "x" in it and cat(it, K)]
    P = {it["id"]: G.item_poly(it, K) for it in its}
    probs = []
    for i, a in enumerate(its):
        for b in its[i + 1:]:
            if a.get("on") == b["id"] or b.get("on") == a["id"]: continue
            n = need(cat(a, K), cat(b, K))
            if n is None or P[a["id"]] is None or P[b["id"]] is None: continue
            if P[a["id"]].intersects(P[b["id"]]): continue   # sits on it (rack on its platform)
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

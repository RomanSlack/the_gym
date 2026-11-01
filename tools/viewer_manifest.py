"""The gym layouts as a scenewalk manifest (~/tools/scenewalk; Roman 2026-11-01: iterate on the layouts "without the full rebuild
and render"). Places every piece from model/layouts/gym_f*.json the way construction/equipment_place.py does, using the prototypes
construction/viewer_export.py exported from the saved scene; a piece with no exported prototype yet shows as a box of its
footprint. Takes well under a second, and scenewalk reloads as soon as the manifest changes:

    python3 tools/viewer_manifest.py            # after any layout run
    ~/tools/scenewalk/target/release/scenewalk construction/out/viewer/gym.json

-> construction/out/viewer/gym.json
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "construction" / "out" / "viewer"
AXV = {"+x": (1, 0), "-x": (-1, 0), "+y": (0, 1), "-y": (0, -1)}


def T(x, y, z):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]


def Rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mul(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = [[sum(out[i][k] * m[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    return out


def turn(face, rot):
    """The z rotation (deg) taking the model's user-facing axis to the plan's rot (equipment_place._turn)."""
    fx, fy = AXV[face]
    return rot + 90 - math.degrees(math.atan2(fy, fx))


base = lambda name: re.sub(r"\.\d{3}$", "", name)


def main():
    idx = json.loads((OUT / "index.json").read_text())
    protos = {}
    for name, e in idx["protos"].items():
        protos.setdefault(base(name), []).append(e)
    attach = {base(k): v for k, v in idx.get("attach", {}).items()}
    on = {base(k): v for k, v in idx.get("on", {}).items()}
    lv = {l["id"]: l["elevation"] for l in json.loads((ROOT / "model" / "building.json").read_text())["levels"]}
    models, boxes, missing = {"shell.glb": [T(0, 0, 0)]}, [], set()

    def add(name, M, it=None, h=1.0):
        e = protos.get(base(name))
        if e:
            models.setdefault(e[0]["file"], []).append(M)
            return e[0]
        missing.add(base(name))
        if it is not None:                                    # a placeholder: the footprint, translucent orange
            boxes.append({"pos": [M[0][3], M[1][3], M[2][3] + h / 2], "size": [it.get("w", 0.6), it.get("d", 0.6), h],
                          "rot": it.get("rot", 0), "color": [1.0, 0.5, 0.1, 0.6], "label": it["id"]})
        return None

    def place(it, K, z):
        kd = it["kind"]; piece = K[kd]["piece"]
        name = f"eq_{piece}" + ("_wall" if K[kd].get("wall") else "")
        e = protos.get(name)
        cx, cy = e[0]["centre"] if e else (0.0, 0.0)
        return name, mul(T(it["x"], it["y"], z + it.get("lift", 0.0)), Rz(turn(K[kd]["face"], it.get("rot", 0))), T(-cx, -cy, 0))

    for nm in ("gym_f1", "gym_f2", "gym_f3"):
        data = json.loads((ROOT / "model" / "layouts" / f"{nm}.json").read_text())
        K, z = data["kinds"], lv[data["level"]]
        byid = {it["id"]: it for it in data["items"]}
        for it in data["items"]:
            kd = it["kind"]
            if it.get("fixed") and kd != "pwr_meta":
                continue
            if kd == "wipe_station":
                f = idx.get("furn", {}).get(kd)
                if f:
                    models.setdefault(f["file"], []).append(mul(T(it["x"], it["y"], z), Rz(it.get("rot", 0))))
                continue
            piece = K.get(kd, {}).get("piece")
            if piece == "rogue-rig-mount-parallel-bars" and it.get("on") in byid:
                rig = byid[it["on"]]
                pname = f"eq_{piece}_wall_{rig['kind']}"
                if pname in on:
                    _, Mr = place(rig, K, z)
                    add(pname, mul(Mr, on[pname]["m"]))
                continue
            if piece:
                name, M = place(it, K, z)
                if add(name, M, it, K[kd].get("h", 1.0)):
                    for a in attach.get(base(name), []):         # a bench's bar, a hanger's bands + belts
                        add(a["proto"], mul(M, a["m"]))
            elif kd == "rig_spur":
                add(f"eq_mubar3_{it['w']:.2f}", mul(T(it["x"], it["y"], z), Rz(it.get("rot", 0))), it, 2.5)
            elif kd == "pwr_meta":
                sig = json.dumps({k_: it.get(k_) for k_ in ("spacing", "cores", "faces", "bars")}, sort_keys=True)
                e = next((e for e in protos.get(f"eq_{it['group']}", []) if e.get("sig") == sig), None)
                ox, oy = it["origin"]
                if e:
                    models.setdefault(e["file"], []).append(T(ox, oy, z))
                else:
                    missing.add(f"eq_{it['group']} (changed: re-export)")
    F1, F2, F3 = lv["F1"] + 1.6, lv["F2"] + 1.6, lv["F3"] + 1.6
    manifest = {
        "version": 1, "title": "The Gym: F1-F3 layouts", "up": "z", "background": [0.62, 0.66, 0.7],
        "ambient": 900.0, "sun": {"dir": [0.35, 0.25, -1.0], "illuminance": 5000.0, "shadows": False},
        "eye_height": 1.6, "speed": 3.0,
        "spawn": {"pos": [-10.6, -11.6, F1], "yaw": 160, "pitch": -5},
        "bookmarks": [
            {"name": "F1 in from the gallery", "pos": [-10.6, -11.6, F1], "yaw": 160, "pitch": -5},
            {"name": "F1 calisthenics", "pos": [-20.0, -25.0, F1], "yaw": 200, "pitch": -5},
            {"name": "F2 spiral, south", "pos": [-14.2, -18.6, F2], "yaw": 150, "pitch": -5},
            {"name": "F2 forecourt, north", "pos": [-16.5, -10.2, F2], "yaw": 20, "pitch": -5},
            {"name": "F2 leg room", "pos": [-13.4, 4.0, F2], "yaw": 80, "pitch": -5},
            {"name": "F3 spiral foot", "pos": [-12.8, -10.4, F3], "yaw": 210, "pitch": -5},
            {"name": "F3 den", "pos": [-16.0, -19.5, F3], "yaw": 160, "pitch": -5},
            {"name": "F3 north", "pos": [-13.2, -4.0, F3], "yaw": 0, "pitch": -5},
            {"name": "F3 functional", "pos": [-24.5, -10.6, F3], "yaw": 20, "pitch": -5}],
        "models": [{"src": f, "instances": [{"m": M} for M in ms]} for f, ms in models.items()],
        "boxes": boxes,
    }
    (OUT / "gym.json").write_text(json.dumps(manifest, separators=(",", ":")))
    n = sum(len(v) for v in models.values())
    print(f"viewer manifest: {n} instances of {len(models)} models, {len(boxes)} placeholder boxes -> {OUT / 'gym.json'}")
    if missing:
        print("  not exported yet (boxes; run construction/viewer_export.py -- eq):", ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()

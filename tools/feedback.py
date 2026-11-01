"""Roman's marked-up viewer captures (Roman 2026-11-01: "press a button, it takes a screenshot of the exact view ... draw on it
... queue them up, and then you can go do them, check them off"). In tools/walk.sh, P saves the view to feedback/ (the image plus
the eye pose); the markup app (~/tools/scenewalk/markup, http://localhost:5290) draws on it, takes the notes and queues it.

    python3 tools/feedback.py                    # the queue: notes, pins, the floor, what's in view, what each pin points at
    python3 tools/feedback.py --status all       # everything (draft | queued | done | accepted | all)
    python3 tools/feedback.py shot ID            # the view now, from the capture's exact pose (after a layout change)
    python3 tools/feedback.py done ID "reply"    # shoot the after image from the same pose, attach it, mark done

Each pin is cast through its pixel onto the floor, so "pin 2: too tight here" comes with the floor point and the nearest pieces.
Look at the marked image (feedback/ID.marked.png) too: the arrows and boxes only live there.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FB = ROOT / "feedback"
MARKUP = Path.home() / "tools" / "scenewalk" / "markup" / "markup.py"
SCENEWALK = Path.home() / "tools" / "scenewalk" / "target" / "release" / "scenewalk"
MANIFEST = ROOT / "construction" / "out" / "viewer" / "gym.json"


def floors():
    lv = {l["id"]: l["elevation"] for l in json.loads((ROOT / "model" / "building.json").read_text())["levels"]}
    out = []
    for nm in ("gym_f1", "gym_f2", "gym_f3"):
        d = json.loads((ROOT / "model" / "layouts" / f"{nm}.json").read_text())
        items = [it for it in d["items"] if "x" in it and "y" in it and it.get("kind") not in ("void",)]
        out.append((d["level"], lv[d["level"]], items, d["kinds"]))
    return out


def basis(yaw, pitch):
    """Forward, right, up in plan axes for the viewer's yaw (0 = north, + = counter-clockwise) and pitch (+ = up)."""
    p, q = math.radians(yaw), math.radians(pitch)
    f = (-math.sin(p) * math.cos(q), math.cos(p) * math.cos(q), math.sin(q))
    r = (math.cos(p), math.sin(p), 0.0)
    u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
    return f, r, u


def ray(cap, px, py):
    w, h = cap["size"]
    t = math.tan(math.radians(cap.get("fov", 65)) / 2)
    xn, yn = (2 * px / w - 1) * t * w / h, (1 - 2 * py / h) * t
    f, r, u = basis(cap["yaw"], cap["pitch"])
    return tuple(f[i] + xn * r[i] + yn * u[i] for i in range(3))


def label(it, kinds):
    return it["id"] if it["id"].startswith(it["kind"]) else f"{it['id']} ({it['kind']})"


def context(item, fl):
    cap, m = item["capture"], item["markup"]
    ex, ey, ez = cap["pos"]
    name, elev, items, kinds = min(fl, key=lambda f: abs(f[1] - cap.get("floor", ez - 1.6)))
    out = [f"  where: {name}, eye ({ex:.2f}, {ey:.2f}) {ez - elev:.2f} m above the floor, looking yaw {cap['yaw']:.0f} pitch {cap['pitch']:.0f}"]
    f, _, _ = basis(cap["yaw"], 0)
    hh = math.degrees(math.atan(math.tan(math.radians(cap.get("fov", 65)) / 2) * cap["size"][0] / cap["size"][1]))
    seen = []
    for it in items:
        dx, dy = it["x"] - ex, it["y"] - ey
        d = math.hypot(dx, dy)
        if d < 0.3 or d > 14:
            continue
        ang = math.degrees(math.acos(max(-1, min(1, (dx * f[0] + dy * f[1]) / d))))
        if ang <= hh + 4:
            seen.append((d, it))
    seen.sort(key=lambda s: s[0])
    if seen:
        out.append("  in view (nearest first): " + ", ".join(f"{label(it, kinds)} {d:.1f} m" for d, it in seen[:14])
                   + (f" ... +{len(seen) - 14}" if len(seen) > 14 else ""))
    for sh in sorted((s for s in m.get("shapes", []) if s["t"] == "pin"), key=lambda s: s["n"]):
        rx, ry, rz = ray(cap, sh["x"], sh["y"])
        if rz < -1e-3:                                   # hits the floor
            t = (elev - ez) / rz
            gx, gy = ex + t * rx, ey + t * ry
            near = sorted(items, key=lambda it: math.hypot(it["x"] - gx, it["y"] - gy))[:4]
            out.append(f"  pin {sh['n']} hits the floor at ({gx:.2f}, {gy:.2f}), {t * math.hypot(rx, ry):.1f} m out: near "
                       + ", ".join(f"{label(it, kinds)} {math.hypot(it['x'] - gx, it['y'] - gy):.1f} m" for it in near))
        else:                                            # above the horizon: the pieces along that bearing
            b = math.atan2(ry, rx)
            along = sorted(((abs(math.remainder(math.atan2(it["y"] - ey, it["x"] - ex) - b, math.tau)), it) for it in items
                            if 0.5 < math.hypot(it["x"] - ex, it["y"] - ey) < 14), key=lambda s: s[0])[:4]
            out.append(f"  pin {sh['n']} is above the horizon (wall/ceiling), bearing {math.degrees(b):.0f} deg (plan, 0 = east): along it "
                       + ", ".join(label(it, kinds) for _, it in along))
    return out


def run_list(status):
    r = subprocess.run([sys.executable, str(MARKUP), "list", "--dir", str(FB), "--status", status, "--json"],
                       capture_output=True, text=True, check=True)
    its = json.loads(r.stdout)
    fl = floors()
    print(f"{len(its)} {status} in {FB.relative_to(ROOT)}  (look at each image: arrows and boxes are only in it)")
    for it in its:
        c, m = it["capture"], it["markup"]
        print(f"\n{it['id']}  [{m['status']}, round {m.get('round', 0)}]" + (f"  {m['title']}" if m.get("title") else ""))
        print(f"  image: feedback/{it['marked'] or c['image']}")
        if m.get("notes", "").strip():
            print("  notes: " + m["notes"].strip().replace("\n", "\n         "))
        for n, txt in sorted(m.get("pins", {}).items(), key=lambda kv: int(kv[0])):
            if txt.strip():
                print(f"  pin {n}: {txt.strip()}")
        for rep in m.get("replies", []):
            print(f"  {'Claude' if rep['by'] == 'fixer' else 'Roman'}: {rep['text']}" + (f"  [{rep['after']}]" if rep.get("after") else ""))
        print("\n".join(context(it, fl)))


def shoot(i, out):
    cap = FB / f"{i}.json"
    if not cap.exists():
        sys.exit(f"no capture {i}")
    c = json.loads(cap.read_text())
    w, h = c["size"]
    if w > 1920:
        w, h = 1920, round(1920 * h / w)
    subprocess.run([sys.executable, str(ROOT / "tools" / "viewer_manifest.py")], check=True, stdout=subprocess.DEVNULL)
    r = subprocess.run(["nice", "-n", "10", str(SCENEWALK), str(MANIFEST), "--shot", str(out), "--view", str(cap),
                        "--width", str(w), "--height", str(h)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"scenewalk --shot failed ({r.returncode}): {r.stderr[-400:]}")
    return out


def main():
    a = sys.argv[1:]
    if not a or a[0] == "--status":
        return run_list(a[1] if len(a) > 1 else "queued")
    if a[0] == "shot" and len(a) == 2:
        out = Path("/tmp") / f"feedback_{a[1]}_now.png"
        print(shoot(a[1], out))
        return
    if a[0] == "done" and len(a) == 3:
        out = shoot(a[1], Path("/tmp") / f"feedback_{a[1]}_after.png")
        subprocess.run([sys.executable, str(MARKUP), "done", "--dir", str(FB), a[1], a[2], "--after", str(out)], check=True)
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()

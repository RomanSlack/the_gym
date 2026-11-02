"""Roman's marked-up viewer captures (Roman 2026-11-01: "press a button, it takes a screenshot of the exact view ... draw on it
... queue them up, and then you can go do them, check them off"). In tools/walk.sh, P saves the view to feedback/ (the image plus
the eye pose); the markup app (~/tools/scenewalk/markup, http://localhost:5290) draws on it, takes the notes and queues it.

    python3 tools/feedback.py                    # the queue: notes, pins, the floor, what's in view, what each pin points at
    python3 tools/feedback.py --status all       # everything (draft | queued | working | done | accepted | all)
    python3 tools/feedback.py take [ID ...]      # tell Roman's app these are being worked on (default: every queued one)
    python3 tools/feedback.py shot ID            # the view now, from the capture's exact pose (after a layout change)
    python3 tools/feedback.py done ID "reply"    # shoot the after image from the same pose, attach it, mark done (+ the replay copies)
    python3 tools/feedback.py resolve CAP.json MARKUP.json   # (the markup app) JSON: what each mark points at
    python3 tools/feedback.py pick CAP.json X Y              # (the markup app) JSON: the piece under one pixel

Every mark is cast through its pixels into the layout (each piece as its footprint box w x d x h, the walls, the floor), so
"pin 2: too tight here" comes with the piece it lands on; a box or a circled area lists what it covers.
Look at the marked image (feedback/ID.marked.png) too: the arrows and boxes only live there.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FB = ROOT / "feedback"
MARKUP = Path.home() / "tools" / "scenewalk" / "markup" / "markup.py"
SCENEWALK = Path.home() / "tools" / "scenewalk" / "target" / "release" / "scenewalk"
MANIFEST = ROOT / "construction" / "out" / "viewer" / "gym.json"


def floors():
    levels = json.loads((ROOT / "model" / "building.json").read_text())["levels"]
    lv = {l["id"]: l["elevation"] for l in levels}
    west = sorted(l["elevation"] for l in levels if l.get("wing") in ("west", "west+east"))
    out = []
    for nm in ("gym_f1", "gym_f2", "gym_f3"):
        d = json.loads((ROOT / "model" / "layouts" / f"{nm}.json").read_text())
        items = [it for it in d["items"] if "x" in it and "y" in it and it.get("kind") not in ("void",)]
        e = lv[d["level"]]
        ceiling = min((z for z in west if z > e + 1), default=e + 4.5) - 0.5     # under the slab above (about)
        out.append((d["level"], e, items, d["kinds"], d.get("walls", []), ceiling))
    return out


def solids(elev, items, kinds, walls):
    """Everything a ray can stop on: (centre x, y, rot deg, half w, half d, z0, z1, what)."""
    out = []
    for it in items:
        h = it.get("h") or kinds.get(it["kind"], {}).get("h") or 0
        if "w" not in it or h <= 0:
            continue
        z0 = elev + it.get("lift", 0.0)
        out.append((it["x"], it["y"], it.get("rot", 0), it["w"] / 2, it["d"] / 2, z0, z0 + h, it))
    for w in walls:
        (ax, ay), (bx, by) = w["from"], w["to"]
        z0, z1 = w.get("z", [0, 3])
        if not z0 <= elev <= z1:                         # the layout's own walls give z from their floor
            z0, z1 = elev + z0, elev + z1
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-6:
            continue
        rot = math.degrees(math.atan2(by - ay, bx - ax)) - 90     # local w along the wall's thickness, d along it
        out.append(((ax + bx) / 2, (ay + by) / 2, rot, w.get("size", [0.2])[0] / 2, L / 2, z0, z1,
                    {"id": w.get("id", "wall"), "kind": f"wall ({w.get('kind', '')})", "label": f"{w.get('kind', '')} wall".strip(), "wall": True}))
    return out


def short(label):
    """A layout label without its description: "Wipes + bin, brushed stainless (built as ...)" -> "Wipes + bin"."""
    return re.split(r" \(|: | - |, ", label or "", maxsplit=1)[0].strip()[:60]


def cast(E, D, sol, elev, ceiling=math.inf):
    """The first thing along E + t D: (distance, what, hit point); the floor if nothing else."""
    best, boxes = (math.inf, None, None), []
    for cx, cy, rot, hw, hd, z0, z1, what in sol:
        a = math.radians(-rot)
        c, s_ = math.cos(a), math.sin(a)
        ox, oy = E[0] - cx, E[1] - cy
        lo = (c * ox - s_ * oy, s_ * ox + c * oy, E[2])
        ld = (c * D[0] - s_ * D[1], s_ * D[0] + c * D[1], D[2])
        t0, t1 = 0.0, math.inf
        for o, d_, lo_, hi in ((lo[0], ld[0], -hw, hw), (lo[1], ld[1], -hd, hd), (lo[2], ld[2], z0, z1)):
            if abs(d_) < 1e-12:
                if not lo_ <= o <= hi:
                    t0 = math.inf
                    break
                continue
            ta, tb = (lo_ - o) / d_, (hi - o) / d_
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 <= t1 and t1 > 0:
            boxes.append((max(t0, 1e-6), t1, hw * hd * (z1 - z0), what))
    if boxes:                       # the nearest box; inside it, the most specific piece (bars on a rig, a bench in a rack)
        first = min(boxes, key=lambda b: b[0])
        inner = [b for b in boxes if b[0] < first[1] and not b[3].get("wall")] or [first]
        pick_ = min(inner, key=lambda b: b[2])
        best = (pick_[0], pick_[3], first[3] if pick_ is not first and not first[3].get("wall") else None)
    if D[2] < -1e-9:
        tf = (elev - E[2]) / D[2]
        if tf < best[0]:
            best = (tf, {"id": "floor", "kind": "floor", "label": "floor"}, None)
    if D[2] > 1e-9:
        tc = (ceiling - E[2]) / D[2]
        if tc < best[0]:
            best = (tc, {"id": "ceiling", "kind": "ceiling", "label": "ceiling"}, None)
    t, what, host = best
    if what is None:
        return None
    n = math.sqrt(sum(d * d for d in D))
    out = {"dist": round(t * n, 2), "at": [round(E[i] + t * D[i], 2) for i in range(3)], "id": what["id"], "kind": what["kind"],
           "label": short(what.get("label", what["kind"]))}
    if host:
        out["in"] = {"id": host["id"], "label": short(host.get("label", host["kind"]))}
    return out


def nearest_piece(hit, items):
    it = min(items, key=lambda it: math.hypot(it["x"] - hit["at"][0], it["y"] - hit["at"][1]))
    return {"id": it["id"], "label": short(it.get("label", it["kind"])), "off": round(math.hypot(it["x"] - hit["at"][0], it["y"] - hit["at"][1]), 2)}


def scene_for(cap, fl):
    ez = cap["pos"][2]
    name, elev, items, kinds, walls, ceiling = min(fl, key=lambda f: abs(f[1] - cap.get("floor", ez - 1.6)))
    return name, elev, items, solids(elev, items, kinds, walls), ceiling


def pick(cap, px, py, fl=None, sc=None):
    _, elev, items, sol, ceiling = sc or scene_for(cap, fl or floors())
    h = cast(cap["pos"], ray(cap, px, py), sol, elev, ceiling)
    if h and h["id"] == "floor":
        h["near"] = nearest_piece(h, items)
    return h


def inside(pt, poly):
    x, y, c = pt[0], pt[1], False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            c = not c
    return c


def samples(sh):
    """Pixels to cast for one mark, and whether they cover an area."""
    t = sh["t"]
    if t == "pin":
        return [(sh["x"], sh["y"])], False
    if t == "text":
        return [(sh["x"], sh["y"] + sh.get("size", 30) * 0.6)], False
    if t == "arrow":
        return [(sh["x2"], sh["y2"])], False                       # what it points at
    if t == "line":
        return [(sh["x1"], sh["y1"]), (sh["x2"], sh["y2"])], False
    if t in ("rect", "ell"):
        x0, y0, w, h = min(sh["x"], sh["x"] + sh["rw"]), min(sh["y"], sh["y"] + sh["rh"]), abs(sh["rw"]), abs(sh["rh"])
        pts = [(x0 + w * (i + .5) / 9, y0 + h * (j + .5) / 7) for i in range(9) for j in range(7)]
        if t == "ell":
            pts = [p for p in pts if ((p[0] - x0 - w / 2) / (w / 2)) ** 2 + ((p[1] - y0 - h / 2) / (h / 2)) ** 2 <= 1]
        return pts, True
    pts = sh["pts"]                                                 # pen / highlighter
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    if len(pts) > 8 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.3 * diag:   # a loop: what's inside it
        g = [(min(xs) + (max(xs) - min(xs)) * (i + .5) / 10, min(ys) + (max(ys) - min(ys)) * (j + .5) / 8) for i in range(10) for j in range(8)]
        inner = [p for p in g if inside(p, pts)]
        if inner:
            return inner, True
    step = max(1, len(pts) // 16)
    return [tuple(p) for p in pts[::step]], sh["t"] == "hl"


def resolve(cap, markup, fl=None):
    sc = scene_for(cap, fl or floors())
    out = []
    for i, sh in enumerate(markup.get("shapes", [])):
        pts, area = samples(sh)
        hits = [h for h in (pick(cap, x, y, sc=sc) for x, y in pts) if h]
        count = {}
        for h in hits:
            key = h["near"]["id"] if h["id"] == "floor" and h["near"]["off"] < 0.8 else h["id"]
            lab = h["near"]["label"] if key != h["id"] else h["label"]
            c = count.setdefault(key, {"id": key, "label": lab, "n": 0, "dist": h["dist"], "kind": h["kind"] if key == h["id"] else ""})
            c["n"] += 1
            if h.get("in") and key == h["id"]:
                c["in"] = h["in"]["label"]
            c["dist"] = min(c["dist"], h["dist"])
        ranked = sorted(count.values(), key=lambda c: -c["n"])
        if not area:
            ranked = ranked[:2]
        else:                                                           # an area: the pieces it covers, floor/walls last
            ranked = [c for c in ranked if c["id"] not in ("floor", "ceiling") and not c["kind"].startswith("wall")][:8] or ranked[:2]
        r = {"i": i, "t": sh["t"], "hits": [{"id": c["id"], "label": c["label"], "dist": c["dist"], "share": round(c["n"] / max(1, len(hits)), 2),
                                             **({"in": c["in"]} if c.get("in") else {})} for c in ranked]}
        if sh["t"] == "pin":
            r["n"] = sh["n"]
        if len(pts) == 1 and hits:
            r["at"] = hits[0]["at"]
            if hits[0]["id"] == "floor":
                r["near"] = hits[0]["near"]
        out.append(r)
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
    name, elev, items, kinds = min(fl, key=lambda f: abs(f[1] - cap.get("floor", ez - 1.6)))[:4]
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
    names = {"pin": "pin", "arrow": "arrow (head)", "line": "line", "rect": "box", "ell": "ellipse", "pen": "pen", "hl": "highlight", "text": "text"}
    for r in resolve(cap, m, fl):
        sh = m["shapes"][r["i"]]
        what = f"pin {r['n']}" if r["t"] == "pin" else f"{sh['c']} {names[r['t']]}" + (f" '{sh['text']}'" if r["t"] == "text" else "")
        hits = "; ".join(f"{h['label']} [{h['id']}]" + (f" on {h['in']}" if h.get("in") else "") + f" {h['dist']:.1f} m" + (f" ({h['share']:.0%})" if len(r["hits"]) > 1 else "") for h in r["hits"])
        at = f" at ({r['at'][0]:.2f}, {r['at'][1]:.2f}, {r['at'][2] - elev:.2f} up)" if "at" in r else ""
        near = f", nearest piece {r['near']['label']} [{r['near']['id']}] {r['near']['off']:.1f} m off" if "near" in r else ""
        out.append(f"  {what} -> {hits}{at}{near}")
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
    if a[0] == "take":
        subprocess.run([sys.executable, str(MARKUP), "take", "--dir", str(FB), *a[1:]], check=True)
        return
    if a[0] == "resolve" and len(a) == 3:
        cap = json.loads(Path(a[1]).read_text())
        mk = json.loads(Path(a[2]).read_text()) if Path(a[2]).exists() else {}
        print(json.dumps(resolve(cap, mk)))
        return
    if a[0] == "pick" and len(a) == 4:
        print(json.dumps(pick(json.loads(Path(a[1]).read_text()), float(a[2]), float(a[3]))))
        return
    if a[0] == "shot" and len(a) == 2:
        out = Path("/tmp") / f"feedback_{a[1]}_now.png"
        print(shoot(a[1], out))
        return
    if a[0] == "done" and len(a) == 3:
        out = shoot(a[1], Path("/tmp") / f"feedback_{a[1]}_after.png")
        subprocess.run([sys.executable, str(MARKUP), "done", "--dir", str(FB), a[1], a[2], "--after", str(out)], check=True)
        keep_for_replay(a[1])
        return
    if a[0] == "replay":                         # (backfill) every capture's marked + after images into feedback/replay/
        for p_ in sorted(FB.glob("*.markup.json")):
            keep_for_replay(p_.name.split(".")[0])
        return
    sys.exit(__doc__)


def keep_for_replay(i):
    """Small JPEG copies the replay picks up (the PNGs stay local): feedback/replay/<id>_0marked.jpg, <id>_after_vNNN.jpg
    (Roman: "this system is also being captured in the replay right?"); committed with the fix."""
    from PIL import Image
    out = FB / "replay"
    out.mkdir(exist_ok=True)
    src = [(FB / f"{i}.marked.png", f"{i}_0marked.jpg")] + [(p_, f"{i}_after_{p_.name.split('_')[-1][:4]}.jpg") for p_ in sorted(FB.glob(f"{i}.after_v*.png"))]
    if not src[0][0].exists():
        src[0] = (FB / f"{i}.png", src[0][1])
    for p_, name in src:
        if p_.exists() and not (out / name).exists():
            im = Image.open(p_).convert("RGB")
            im.thumbnail((1280, 1280))
            im.save(out / name, quality=82)


if __name__ == "__main__":
    main()

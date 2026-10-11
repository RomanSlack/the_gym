"""Interior walls + doors, generated from the room layout (model.spaces).

Rules:
  - A partition goes on every shared boundary where at least one side is an ENCLOSED room
    (wet areas, cores, daycare rooms, rock-annex rooms, thermal, ...). Open gym zones stay open.
  - Boundaries that already have an envelope wall (retaining walls, facades, glass walls) are skipped.
  - Every enclosed room gets a door (1.0 m leaf, accessible) to its best neighbour:
    explicit rules first (DOORS), else circulation > lounge > gym > daycare > anything, on the longest
    shared edge. Doors swing into the room.
  - Partitions run floor to the slab above.

python3 tools/partitions.py      (after tools/layout_v1.py + tools/structure.py)
"""
import sys
from pathlib import Path

from shapely.geometry import LineString, Polygon
from shapely.ops import linemerge, unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}
CEIL = {"F1": 5.64, "F2": -0.25, "F3": -5.16, "F4": -10.02, "E1": 5.64, "E2": -0.13}

ENCLOSED_KINDS = {"wet", "core", "service", "daycare"}
# Roman: "as open floor plan as we can get it everywhere" -> walls only where needed (wet, cores, plant, thermal,
# privacy); GLASS where separation is needed but not privacy; everything else stays open.
ENCLOSED_IDS = {"posing", "pod-1", "pod-2", "pod-3", "altitude", "breathwork", "thermal", "game-room", "plant", "sauna-lobby"}
GLASS_IDS = {"game-room", "dc-kids", "daycare-up", "dc-hall", "daycare-low", "dc-wardrobe"}  # see-through, still separated
OPEN_PAIRS = {frozenset(p) for p in [("pool-lobby", "pool-deck-w"), ("lobby", "reception")]}
# explicit doors: room -> list of neighbours it opens to
DOORS = {
    "women-wet": ["women-lockers"], "men-wet": ["men-lockers"],
    "women-lockers": ["gallery"], "men-lockers": ["gallery"],
    "sauna-lobby": ["women-lockers", "men-lockers"],
    "dc-wc": ["dc-kids"], "dc-staff": ["dc-kids"], "dc-wardrobe": ["dc-hall"], "dc-hall": [],
    "dc-wc-low": ["daycare-low"], "dc-rest": ["daycare-low"], "dc-store": ["daycare-low"],
    "dc-nursing": ["dc-hall"], "dc-kids": ["dc-hall"], "daycare-up": ["dc-hall"],
    "wcs": ["cafe"], "game-room": ["garage"],
    "thermal": ["pool-deck-n"],
}
RANK = {"circulation": 0, "lounge": 1, "gym": 2, "daycare": 3, "garage": 4}
# Roman's principle: no door unless it is needed (privacy, fire, heat, security, cars, sleeping kids).
# Otherwise an open doorway ("opening", wider) or a privacy-baffled open entry ("baffle").
PASSAGE = {  # (room, neighbour) -> opening type
    ("women-wet", "women-lockers"): "opening", ("men-wet", "men-lockers"): "opening",
    ("women-lockers", "gallery"): "baffle", ("men-lockers", "gallery"): "baffle",
    ("dc-kids", "dc-hall"): "opening", ("daycare-up", "dc-hall"): "opening", ("dc-wardrobe", "dc-hall"): "opening",
}
WIDTH = {"door": 1.0, "opening": 1.8, "baffle": 1.6}
DOOR_W = 1.0

spaces = m["spaces"]
enclosed = lambda sp: (sp["kind"] in ENCLOSED_KINDS or sp["id"] in ENCLOSED_IDS) and not sp["id"].startswith("pool-deck")
env_walls = [e for e in m["elements"] if e["type"] == "wall" and not e["id"].startswith("P-")]


def on_envelope(seg: LineString, level: str) -> bool:
    z = lv[level] + 1.0
    for w in env_walls:
        if not (w["z"][0] <= z <= w["z"][1]):
            continue
        wl = LineString([w["from"], w["to"]])
        if wl.buffer(w["size"][0] / 2 + 0.35).contains(seg.interpolate(0.5, normalized=True)):
            return True
    return False


els = [e for e in m["elements"] if not e["id"].startswith("P-")]
walls, doors = [], []
k = 0
for L in sorted({sp["level"] for sp in spaces}):
    S = [sp for sp in spaces if sp["level"] == L]
    shared = {}  # (a, b) -> list of LineStrings
    for i, a in enumerate(S):
        pa = Polygon(a["poly"])
        for b in S[i + 1:]:
            pb = Polygon(b["poly"])
            inter = pa.boundary.intersection(pb.boundary)
            if inter.is_empty or inter.length < 0.3:
                continue
            parts = unary_union([g for g in getattr(inter, "geoms", [inter]) if g.geom_type in ("LineString", "MultiLineString")])
            lines = linemerge(parts) if parts.geom_type == "MultiLineString" else parts
            segs = [g for g in getattr(lines, "geoms", [lines]) if g.length >= 0.3]
            if segs:
                shared[(a["id"], b["id"])] = segs
    # partitions
    for (ia, ib), segs in shared.items():
        A = next(s for s in S if s["id"] == ia); B = next(s for s in S if s["id"] == ib)
        if not (enclosed(A) or enclosed(B)) or frozenset((ia, ib)) in OPEN_PAIRS:
            continue
        if A["kind"] == "core" and B["kind"] == "core":
            continue
        for seg in segs:
            if on_envelope(seg, L):
                continue
            (x0, y0), (x1, y1) = seg.coords[0], seg.coords[-1]
            glass = (ia in GLASS_IDS or ib in GLASS_IDS) and not ({ia, ib} & {"dc-wc", "dc-wc-low", "dc-staff", "dc-rest", "dc-store", "dc-nursing", "wcs"}) \
                and A["kind"] != "core" and B["kind"] != "core"
            walls.append({"id": f"P-{L}-{k}", "type": "wall", "kind": "glazed" if glass else "partition", "material": "glass" if glass else "timber_stud",
                          "from": [round(x0, 3), round(y0, 3)], "to": [round(x1, 3), round(y1, 3)], "size": [0.15, round(CEIL[L] - lv[L], 2)],
                          "z": [lv[L], CEIL[L]], "level": L, "between": [ia, ib], "openings": []})
            k += 1
    # doors
    for sp in S:
        if not enclosed(sp) or sp["kind"] == "core" and sp["id"].startswith(("core-W", "lift-")):
            continue
        targets = DOORS.get(sp["id"])
        if targets is None:
            nb = []
            for (ia, ib), segs in shared.items():
                if sp["id"] in (ia, ib):
                    other = next(s for s in S if s["id"] == (ib if ia == sp["id"] else ia))
                    if enclosed(other) and other["kind"] != "daycare":
                        continue
                    nb.append((RANK.get(other["kind"], 9), -max(g.length for g in segs), other["id"]))
            targets = [sorted(nb)[0][2]] if nb else []
        for t in targets:
            cands = [w for w in walls if w["level"] == L and set(w["between"]) == {sp["id"], t}]
            if not cands:
                continue
            w = max(cands, key=lambda w: LineString([w["from"], w["to"]]).length)
            Lw = LineString([w["from"], w["to"]]).length
            otype = PASSAGE.get((sp["id"], t), "door")
            width = min(WIDTH[otype], Lw - 0.3)
            if width < 0.9:
                continue
            s0 = round(Lw / 2 - width / 2, 2)
            # swing into the enclosed room: which side of the wall is it on?
            (x0, y0), (x1, y1) = w["from"], w["to"]
            nx, ny = -(y1 - y0) / Lw, (x1 - x0) / Lw
            c = Polygon(sp["poly"]).representative_point()
            side = 1 if (c.x - x0) * nx + (c.y - y0) * ny > 0 else -1
            w["openings"].append({"s": [s0, round(s0 + width, 2)], "z": [lv[L], round(lv[L] + (2.1 if otype == "door" else 2.4), 2)], "type": otype,
                                  "swing": side, "note": f"{sp['name'].split(' · ')[0]} ↔ {next(s for s in S if s['id'] == t)['name'].split(' · ')[0]}"})
            doors.append((L, sp["id"], t))

m["elements"] = els + walls
modelio.save(m)
print(len(walls), "partitions,", len(doors), "doors")
missing = [sp["id"] for sp in spaces if enclosed(sp) and sp["kind"] != "core" and not any(d[1] == sp["id"] for d in doors)]
print("enclosed rooms without a generated door (reached via envelope openings or by design):", missing)

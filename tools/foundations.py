"""Construction stage 1: foundations / substructure.

Adds phase-1 elements to model/building.json and writes the construction pit heightfield.
Rules of thumb (no engineering calcs), noted on each element:
  - blinding 75 mm lean concrete under every raft
  - rafts: existing F4 / E2 / annex / parking slabs; thickened 0.5 m x 1.6 m strip footings under retaining walls
  - rock anchors under F4 + the pool + south annex: Ø150 grouted bars, 8 m into rock, 2.5 m grid (uplift: river 6.6 m above F4)
  - pad footings 2.0 x 2.0 x 0.6 under the parking columns
  - waterproofing membrane on the earth side of every retaining wall; river wall = watertight concrete ("white tank")
  - 0.3 m drainage gravel + Ø150 perimeter drain behind retaining walls (not the river wall)
  - temporary cofferdam: steel sheet piles in the river, 2.5 m off the river wall, toe -22, top 1 m above water
  - construction pit: footprints + 1.0 m working space, floor at foundation bottom, rock faces cut at ~75°
  - garage ramp: open-cut trench with retaining walls, cut-and-cover tunnel roof into the parking
python3 tools/foundations.py   (run after tools/build_model.py)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}
els = [e for e in m["elements"] if not e["id"].startswith("FDN-")]
by_id = {e["id"]: e for e in els}
new, seq = [], [0]


def add(e, s):
    e["phase"], e["seq"] = 1, s
    new.append(e)


# ---- existing substructure elements join phase 1
SUB_WALL = ("W-west-", "W-east-", "WP-", "SA-", "WA-", "CS-W", "LS-")
SUB_SLAB = ("S-F4-", "S-E2-", "S-SA-F4", "S-P-floor")
for e in els:
    if (e["type"] == "wall" and e["id"].startswith(SUB_WALL) and e["material"] == "concrete") or \
       (e["type"] == "slab" and e["id"].startswith(SUB_SLAB)):
        e["phase"], e["seq"] = 1, (70 if e["type"] == "slab" else 80)

# ---- rafts for the cores / annexes that only had walls
CORE_RAFTS = {
    "W1": ([-32.05, -18.55, -28.85, -9.55], lv["F4"]), "W2": ([-32.05, -34.1, -28.85, -25.1], lv["F4"]),
    "W3": ([-17.2, 12.35, -8.2, 15.55], lv["F4"]), "WCA": ([-33.45, -24.75, -29.45, -18.9], lv["F4"]),
    "LIFTM": ([-31.25, -4.1, -28.85, -1.7], lv["F4"] - 1.2), "LIFTW": ([-31.25, 4.7, -28.85, 7.1], lv["F4"] - 1.2),
}
for k, (r, top) in CORE_RAFTS.items():
    add({"id": f"FDN-raft-{k}", "type": "slab", "material": "concrete", "rect": r, "z": [round(top - 0.6, 2), round(top, 2)],
         "note": "0.6 m raft" + (" (lift pit 1.2 m)" if k.startswith("LIFT") else "")}, 70)
# pool basin: deeper raft + basin walls
pool = [-16.45, -28.1, -6.45, -3.1]
add({"id": "FDN-pool-raft", "type": "slab", "material": "concrete", "rect": pool, "z": [round(lv["F4"] - 2.6, 2), round(lv["F4"] - 2.0, 2)],
     "note": "pool basin floor, 0.6 m, rock-anchored"}, 70)
x0, y0, x1, y1 = pool
for n, (a, b) in {"S": ([x0, y0], [x1, y0]), "N": ([x0, y1], [x1, y1]), "W": ([x0, y0], [x0, y1])}.items():
    add({"id": f"FDN-pool-wall-{n}", "type": "wall", "material": "concrete", "from": a, "to": b, "size": [0.4, 2.0],
         "z": [round(lv["F4"] - 2.0, 2), round(lv["F4"] - 0.6, 2)], "note": "pool basin wall (east side = river wall)"}, 75)

# ---- foundation bottoms per footprint (for blinding, anchors, pit)
F4B, E2B = round(lv["F4"] - 0.6, 2), round(lv["E2"] - 0.6, 2)
FOOT = [  # rect, bottom z (top of blinding)
    ([-29.45, -34.1, -6.45, 12.1], F4B), ([-28.85, -40.1, -6.45, -34.1], F4B),
    *[(r, round(t - 0.6, 2)) for r, t in CORE_RAFTS.values()], (pool, round(lv["F4"] - 2.6, 2)),
    ([12.0, -9.5, 30.5, 33.3], E2B), ([30.5, -9.5, 60.0, 24.0], round(lv["E2"] - 0.3, 2)),
]
for k, (r, b) in enumerate(FOOT):
    add({"id": f"FDN-blinding-{k}", "type": "blinding", "material": "lean", "rect": r, "z": [round(b - 0.075, 3), b], "note": "75 mm blinding"}, 40)

# ---- strip footings under retaining walls (thickened raft edge)
for e in els:
    if e.get("phase") == 1 and e["type"] == "wall" and e["id"].startswith(("W-west-", "W-east-", "WP-", "SA-")):
        b = e["z"][0]
        add({"id": f"FDN-strip-{e['id']}", "type": "strip_footing", "material": "concrete", "from": e["from"], "to": e["to"],
             "size": [1.6, 0.5], "z": [round(b - 0.5, 2), b], "note": "thickened raft edge under the retaining wall"}, 50)

# ---- rock anchors (2.5 m grid) under the F4 raft, south annex and pool
def grid_in(r, step=2.5, inset=1.0):
    xs = np.arange(r[0] + inset, r[2] - inset + 1e-6, step); ys = np.arange(r[1] + inset, r[3] - inset + 1e-6, step)
    return [[round(float(x), 2), round(float(y), 2)] for x in xs for y in ys]


pts_f4 = [p for p in grid_in([-29.45, -34.1, -6.45, 12.1]) + grid_in([-28.85, -40.1, -6.45, -34.1])
          if not (pool[0] - 0.5 < p[0] < pool[2] + 0.5 and pool[1] - 0.5 < p[1] < pool[3] + 0.5)]
add({"id": "FDN-anchors-F4", "type": "anchor_field", "material": "steel", "points": pts_f4, "dia": 0.15, "z": [F4B - 0.075 - 8.0, F4B - 0.075],
     "note": "grouted rock anchors Ø150, 8 m, 2.5 m grid: hold the F4 raft down (river 6.6 m above F4)"}, 30)
add({"id": "FDN-anchors-pool", "type": "anchor_field", "material": "steel", "points": grid_in(pool, 2.0, 0.8), "dia": 0.15,
     "z": [round(lv["F4"] - 2.675 - 8.0, 2), round(lv["F4"] - 2.675, 2)], "note": "rock anchors under the pool basin, 2.0 m grid"}, 30)

# ---- pad footings under the parking columns
for e in els:
    if e["type"] == "column" and e["id"].startswith("C-P-"):
        add({"id": f"FDN-pad-{e['id']}", "type": "pad_footing", "material": "concrete", "at": e["at"], "size": [2.0, 2.0],
             "z": [round(lv["E2"] - 0.3 - 0.6, 2), round(lv["E2"] - 0.3, 2)], "note": "2.0 x 2.0 x 0.6 pad footing"}, 60)

# ---- waterproofing + drainage on the earth side of retaining walls
CENTRES = [((-17.95, -14.0), ("W-west-", "SA-", "WA-", "CS-W", "LS-")), ((21.25, 11.9), ("W-east-",)), ((45.0, 7.0), ("WP-",))]
for e in els:
    if e.get("phase") != 1 or e["type"] != "wall" or e["id"] == "W-west-C":
        continue
    cen = next((c for c, pre in CENTRES if e["id"].startswith(pre)), None)
    if cen is None:
        continue
    (ax, ay), (bx, by) = e["from"], e["to"]
    L = math.hypot(bx - ax, by - ay)
    if L < 0.5:
        continue
    nx, ny = -(by - ay) / L, (bx - ax) / L
    mx, my = (ax + bx) / 2, (ay + by) / 2
    if (cen[0] - mx) * nx + (cen[1] - my) * ny > 0:  # point the normal away from the building
        nx, ny = -nx, -ny
    t = e["size"][0] / 2
    off = lambda d: ([round(ax + nx * d, 3), round(ay + ny * d, 3)], [round(bx + nx * d, 3), round(by + ny * d, 3)])
    a, b = off(t + 0.01)
    add({"id": f"FDN-membrane-{e['id']}", "type": "membrane", "material": "membrane", "from": a, "to": b, "size": [0.02, 0], "z": e["z"],
         "note": "bentonite / bituminous waterproofing membrane"}, 85)
    a, b = off(t + 0.17)
    add({"id": f"FDN-gravel-{e['id']}", "type": "drain_layer", "material": "gravel", "from": a, "to": b, "size": [0.3, 0],
         "z": [e["z"][0], round(min(e["z"][1], -1.0), 2)], "note": "0.3 m free-draining gravel"}, 90)
    a, b = off(t + 0.25)
    add({"id": f"FDN-drain-{e['id']}", "type": "drain_pipe", "material": "pipe", "from": a, "to": b, "dia": 0.15, "z": [round(e["z"][0] + 0.15, 2), round(e["z"][0] + 0.15, 2)],
         "note": "Ø150 perforated perimeter drain, falls to the pumped sump"}, 90)

# ---- temporary cofferdam (river side of the west wing)
WL = m["site"]["water_level"]
CD = [[-4.0, 16.0], [-4.0, -43.0]]
for n, (a, b) in {"main": (CD[0], CD[1]), "north": ([-7.6, 16.0], CD[0]), "south": ([-7.6, -43.0], CD[1])}.items():
    add({"id": f"FDN-cofferdam-{n}", "type": "sheetpile", "material": "sheetpile", "from": a, "to": b, "size": [0.4, 0], "z": [-22.0, round(WL + 1.0, 2)],
         "note": "TEMPORARY steel sheet-pile cofferdam; removed after the river wall is built", "temporary": True}, 10)

# ---- garage ramp: open-cut trench walls + cut-and-cover tunnel roof
F = m["site"]["features"]; rp = F["garage_ramp"]
H = np.load(ROOT / "terrain" / "out" / "ravine" / "eroded_1m.npy")
pts = np.array(rp["points"], float)
seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
z_top = float(H[int(pts[0, 1] + 1000), int(pts[0, 0] + 1000)])
ramp_z = lambda s: z_top + (rp["z_end"] - z_top) * s / seg[-1]
hw = rp["width"] / 2 + 0.2
for k in range(len(pts) - 1):
    a, b = pts[k], pts[k + 1]
    d = (b - a) / np.linalg.norm(b - a); n = np.array([-d[1], d[0]])
    zl = min(ramp_z(seg[k]), ramp_z(seg[k + 1])) - 0.6
    for side, sgn in (("L", 1), ("R", -1)):
        p0, p1 = a + n * hw * sgn, b + n * hw * sgn
        top = float(max(H[int(p0[1] + 1000), int(p0[0] + 1000)], H[int(p1[1] + 1000), int(p1[0] + 1000)])) + 0.3
        add({"id": f"FDN-ramp-wall-{k}{side}", "type": "wall", "material": "concrete", "from": p0.round(2).tolist(), "to": p1.round(2).tolist(),
             "size": [0.35, 0], "z": [round(zl, 2), round(top, 2)], "note": "garage-ramp retaining wall"}, 95)
tun = [p for p in pts if p[0] <= rp["tunnel_from_x"]]
x_a, x_b = min(p[0] for p in pts if p[0] <= rp["tunnel_from_x"] + 0.01), rp["tunnel_from_x"]
add({"id": "FDN-ramp-tunnel-roof", "type": "slab", "material": "concrete", "rect": [round(x_a, 2), -1.0 - hw, round(x_b, 2), -1.0 + hw],
     "z": [-1.6, -1.2], "note": "cut-and-cover tunnel roof, backfilled + landscaped"}, 96)

m["elements"] = els + new
modelio.save(m)

# ---- construction pit heightfield + dewatered river cells
g = np.arange(-1000, 1000) + 0.5
X, Y = np.meshgrid(g, g)
pit = np.full(X.shape, 1e6, np.float32)
tan_face = math.tan(math.radians(75))
for r, b in FOOT:
    x0, y0, x1, y1 = r[0] - 1.0, r[1] - 1.0, r[2] + 1.0, r[3] + 1.0
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0); dy = np.maximum(np.maximum(y0 - Y, Y - y1), 0)
    d = np.hypot(dx, dy)
    pit = np.minimum(pit, (b - 0.15) + d * tan_face)
for k in range(len(pts) - 1):  # ramp trench
    a, b = pts[k], pts[k + 1]
    L = np.linalg.norm(b - a); d_ = (b - a) / L
    t = np.clip(((X - a[0]) * d_[0] + (Y - a[1]) * d_[1]) / L, 0, 1)
    dist = np.hypot(X - (a[0] + t * (b[0] - a[0])), Y - (a[1] + t * (b[1] - a[1])))
    floor = ramp_z(seg[k] + t * L) - 0.8
    pit = np.minimum(pit, floor + np.maximum(dist - hw - 1.0, 0) * tan_face)
out = ROOT / "construction" / "out"; out.mkdir(parents=True, exist_ok=True)
np.save(out / "pit_1m.npy", pit.astype(np.float32))
W = np.load(ROOT / "terrain" / "out" / "ravine" / "water_1m.npy")
dry = (~np.isnan(W)) & (X < -4.0) & (Y > -43) & (Y < 16)
np.save(out / "dewatered_1m.npy", dry.astype(np.uint8))
from collections import Counter
print("phase-1 elements:", sum(1 for e in m["elements"] if e.get("phase") == 1), dict(Counter(e["type"] for e in m["elements"] if e.get("phase") == 1)))
print("anchors:", len(pts_f4), "+ pool", len(grid_in(pool, 2.0, 0.8)))

"""Place the forest over the 2 km site square from the real forest data (docs/ECOLOGY.md, model/forest_sr16.npz).

Per 4 m cell (SR16 is 16 m): species, dominant height and crown cover set what grows there:
  - trees per cell = cover x cell area / crown area of that species at that height; positions jittered, a minimum spacing kept
  - height = dominant height x 0.75-1.05 (a few veterans in the tallest class)
  - clear-cut cells (dominant height < 4 m): dense young spruce regrowth, the odd seed pine left standing
Cleared: the building + every enclosed volume + 6 m, roads / drop-off / ramp (+4 m), paths and the trail (+1.5 m), the garden,
lawns, decks, the sauna, water, and steep bare rock. Design trees placed by hand: the old pine on the drop-off island and the
pine in the west garden (VISION.md).
Writes construction/out/forest_points.npz: x, y, z, variant index, scale, rotation.
python3 tools/forest_scatter.py   (terrain/.venv python)
"""
import json
import math
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
RV, OUT = ROOT / "terrain" / "out" / "ravine", ROOT / "construction" / "out"
m = json.loads((ROOT / "model" / "building.json").read_text())
F = np.load(ROOT / "model" / "forest_sr16.npz")
fin, fm = np.load(RV / "eroded_1m.npy"), np.load(RV / "features_1m.npy").astype(int)
water, rock = np.load(RV / "water_1m.npy"), np.load(RV / "rock_1m.npy")
rng = np.random.default_rng(16)

# library variants (must match construction/tree_lib.py VARIANTS order)
VAR = {"spruce": [(0, 16), (1, 15), (2, 17), (3, 14), (4, 18), (5, 13)], "pine": [(6, 14), (7, 13), (8, 15), (9, 12)],
       "young": [(10, 3.0), (11, 2.2), (12, 3.8)]}
CROWN_R = {1: lambda h: 0.12 * h + 0.6, 2: lambda h: 0.16 * h + 0.6}  # crown radius (m) at height h: spruce narrow, pine wider

# ---- what is cleared (1 m grid, rows = y + 1000, cols = x + 1000)
g = np.arange(-1000, 1000) + 0.5
X, Y = np.meshgrid(g, g); P2 = np.stack([X.ravel(), Y.ravel()], 1)
clear = np.zeros(fin.shape, bool)
bits = lambda *b: (fm & sum(b)) > 0
MASK = {"asphalt": 1, "shoulder": 2, "court": 4, "ramp": 8, "garden": 16, "path": 32, "sauna": 64, "tunnel": 128, "trail": 256,
        "planting": 512, "stone": 1024, "gravel": 2048, "lawn": 4096, "deck": 8192}
dil = lambda a, r: ndi.binary_dilation(a, iterations=int(r)) if r else a
clear |= dil(bits(MASK["asphalt"], MASK["shoulder"], MASK["court"], MASK["ramp"], MASK["gravel"]), 4)
clear |= dil(bits(MASK["path"], MASK["trail"], MASK["stone"]), 1.5)
clear |= dil(bits(MASK["garden"], MASK["lawn"], MASK["deck"], MASK["sauna"], MASK["planting"]), 1)
voids = json.loads((OUT / "voids.json").read_text()) if (OUT / "voids.json").exists() else []
for (x0, y0, x1, y1), _, _ in voids:
    clear |= (X > x0 - 6) & (X < x1 + 6) & (Y > y0 - 6) & (Y < y1 + 6)
for p in m["site"]["pads"]:
    clear |= dil(MPath(p["poly"]).contains_points(P2).reshape(fin.shape), 6)
lounge = [-6.45, -12.5, 12.0, 11.3]
clear |= (X > lounge[0] - 4) & (X < lounge[2] + 4) & (Y > lounge[1] - 4) & (Y < lounge[3] + 4)
clear |= dil(~np.isnan(water), 1)
gy, gx = np.gradient(fin); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
clear |= (rock > 0.5) & (slope > 42)

# ---- trees per 4 m cell
sp, dh, cov = F["species"], F["dom_height_m"], F["cover"]
step = float(F["step"]); o = float(F["origin"])
pts = []
for i, j in zip(*np.nonzero(sp > 0)):
    x0, y0 = o + j * step, o + i * step
    s, h, c = int(sp[i, j]), float(dh[i, j]), float(cov[i, j])
    if h < 4.0:  # clear-cut: regrowth (planted spruce ~2000/ha thins to ~1200), the odd seed pine
        n = rng.poisson(step * step * 0.12)
        pts += [(x0 + rng.random() * step, y0 + rng.random() * step, "young", rng.uniform(0.8, 4.0)) for _ in range(n)]
        if s == 2 and rng.random() < step * step / 500:
            pts.append((x0 + rng.random() * step, y0 + rng.random() * step, "pine", rng.uniform(13, 18)))
        continue
    kind = "pine" if s == 2 else "spruce"  # broadleaf cells (1 %) -> spruce until birch exists (see ECOLOGY.md)
    r = CROWN_R[2 if kind == "pine" else 1](h)
    n = rng.poisson(max(c, 8) / 100 * step * step / (math.pi * r * r))
    for _ in range(n):
        ht = h * rng.uniform(0.75, 1.05)
        if h > 17 and rng.random() < 0.15:
            ht = rng.uniform(19, 24)  # veterans in the mature stands
        pts.append((x0 + rng.random() * step, y0 + rng.random() * step, kind, ht))

# ---- clear, space out, ground them
pts = np.array([(x, y, {"spruce": 1, "pine": 2, "young": 3}[k], h) for x, y, k, h in pts if -999 < x < 999 and -999 < y < 999])
ci, cj = (pts[:, 1] + 1000).astype(int), (pts[:, 0] + 1000).astype(int)
pts = pts[~clear[ci, cj]]
order = rng.permutation(len(pts)); pts = pts[order]
keep, grid = [], {}
for k, (x, y, s, h) in enumerate(pts):
    rmin = 0.9 if s == 3 else 0.55 * CROWN_R[int(min(s, 2))](h)
    key = (int(x // 4), int(y // 4))
    if any(math.hypot(x - pts[q][0], y - pts[q][1]) < rmin for dx in (-1, 0, 1) for dy in (-1, 0, 1) for q in grid.get((key[0] + dx, key[1] + dy), [])):
        continue
    grid.setdefault(key, []).append(k); keep.append(k)
pts = pts[keep]

# design trees (VISION.md): the big old pine on the drop-off island, the pine in the west garden
special = []
for sid in ("loop_island", "west_bed_1"):
    srf = next((s_ for s_ in m["site"]["features"]["surfaces"] if s_["id"] == sid), None)
    if srf:
        cx, cy = (srf["circle"][:2] if "circle" in srf else np.array(srf["poly"]).mean(0))
        special.append((float(cx), float(cy), 2, 21.0 if sid == "loop_island" else 17.0))
if special:
    pts = np.vstack([pts, np.array(special)])

idx, scl = [], []
for x, y, s, h in pts:
    pool = VAR["young"] if s == 3 else VAR["pine" if s == 2 else "spruce"]
    v, hv = min(pool, key=lambda q: abs(q[1] - h) + rng.random() * 2.5)  # near in height, with variety
    idx.append(v); scl.append(float(np.clip(h / hv, 0.45, 1.6)))
z = fin[(pts[:, 1] + 1000).astype(int), (pts[:, 0] + 1000).astype(int)] - 0.15
np.savez_compressed(OUT / "forest_points.npz", x=pts[:, 0].astype(np.float32), y=pts[:, 1].astype(np.float32), z=z.astype(np.float32),
                    index=np.array(idx, np.int32), scale=np.array(scl, np.float32), rot=(rng.random(len(pts)) * 2 * math.pi).astype(np.float32))
det = (pts[:, 0] > -320) & (pts[:, 0] < 620) & (pts[:, 1] > -320) & (pts[:, 1] < 900)
print(f"trees: {len(pts)} on the 2 km square ({det.sum()} in the detail area); spruce {(pts[:, 2] == 1).sum()}, pine {(pts[:, 2] == 2).sum()}, "
      f"young regrowth {(pts[:, 2] == 3).sum()}, design trees {len(special)}")

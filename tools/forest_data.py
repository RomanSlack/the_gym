"""Real forest at the site from NIBIO SR16 (national forest resource map, 16 m; open data, CC BY 4.0, (c) NIBIO).

The WMS exposes no raw values, so each layer is fetched as an image around the site and decoded against its legend swatches:
  SRRTRESLAG  dominant species: gran (Norway spruce) / furu (Scots pine) / lauv (broadleaf: birch, aspen, alder ...)
  SRRHOYDEM   mean tree height, 2 m classes (dm in the legend)
  SRRHOYDEO   dominant (top) height, same classes
  SRRKRONEDEK crown cover, 10 % classes
  SRRBONITET  site index H40 (B6..B26: dominant height at 40 years, m)
then resampled onto the local site grid (x east, y north, metres; same grid as terrain/out/ravine, 2000 x 2000 at 1 m, here every 4 m).
Writes model/forest_sr16.npz (species code 0 none / 1 spruce / 2 pine / 3 broadleaf, height_m, cover, site_index) + a summary.
python3 tools/forest_data.py   (terrain/.venv python: needs pyproj, numpy, PIL)
"""
import io
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".cache" / "the_gym" / "nibio"; CACHE.mkdir(parents=True, exist_ok=True)
m = json.loads((ROOT / "model" / "building.json").read_text())
geo = m["site"]["georef"]
OX, OY = geo["origin_utm"]; ROT = math.radians(geo["rotation_deg"])
WMS = "https://wms.nibio.no/cgi-bin/sr16"
STEP = 4.0  # local grid step written out (SR16 itself is 16 m)
HALF = 1000.0

# legend classes, top to bottom (matching the swatches in GetLegendGraphic)
CLASSES = {
    "SRRTRESLAG": [1, 2, 3],                                                     # gran, furu, lauv
    "SRRHOYDEM": [1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 16.5, 18.5],         # class centre, m
    "SRRHOYDEO": [1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 16.5, 18.5],         # dominant (top) height, class centre, m
    "SRRKRONEDEK": [5, 15, 25, 35, 45, 55, 65, 75, 85, 95],                      # %
    "SRRBONITET": [6, 8, 11, 14, 17, 20, 23, 26],                                # H40, m
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "the_gym/1.0"}), timeout=60) as r:
        return r.read()


def legend_colours(layer, n):
    p = CACHE / f"leg_{layer}.png"
    if not p.exists():
        p.write_bytes(get(f"{WMS}?version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer={layer}&format=image/png&STYLE=default&language=nor"))
    im = np.array(Image.open(p).convert("RGB")).astype(int)
    col = im[:, 6]  # the swatch column
    rows, cur = [], None
    for y, c in enumerate(col):
        sw = tuple(c) != (255, 255, 255) and not (abs(c[0] - c[1]) < 4 and abs(c[1] - c[2]) < 4 and c[0] < 120)  # skip white + grey text/frames
        if sw and cur is None:
            cur = [y, y]
        elif sw:
            cur[1] = y
        elif cur is not None:
            rows.append(cur); cur = None
    if cur:
        rows.append(cur)
    cols = [tuple(im[(a + b) // 2, 6]) for a, b in rows if b - a >= 4]  # the swatch centre (its border is a lighter shade)
    if len(cols) != n:
        raise SystemExit(f"{layer}: found {len(cols)} legend swatches, expected {n}")
    return np.array(cols)


def local_to_utm33(x, y):
    return OX + x * math.cos(ROT) - y * math.sin(ROT), OY + x * math.sin(ROT) + y * math.cos(ROT)


# axis-aligned UTM33 box round the rotated local square
corners = [local_to_utm33(sx * HALF, sy * HALF) for sx in (-1, 1) for sy in (-1, 1)]
E0, E1 = min(c[0] for c in corners) - 50, max(c[0] for c in corners) + 50
N0, N1 = min(c[1] for c in corners) - 50, max(c[1] for c in corners) + 50
PX = 4.0
W, H = int((E1 - E0) / PX), int((N1 - N0) / PX)

g = np.arange(-HALF, HALF, STEP) + STEP / 2
LX, LY = np.meshgrid(g, g)  # rows = y (north), cols = x (east)
UE = OX + LX * math.cos(ROT) - LY * math.sin(ROT)
UN = OY + LX * math.sin(ROT) + LY * math.cos(ROT)
pi = np.clip(((N1 - UN) / PX).astype(int), 0, H - 1); pj = np.clip(((UE - E0) / PX).astype(int), 0, W - 1)

out = {}
for layer, vals in CLASSES.items():
    p = CACHE / f"map_{layer}.png"
    if not p.exists():
        p.write_bytes(get(f"{WMS}?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS={layer}&STYLES=&SRS=EPSG:25833&BBOX={E0},{N0},{E1},{N1}"
                          f"&WIDTH={W}&HEIGHT={H}&FORMAT=image/png&TRANSPARENT=TRUE"))
    im = np.array(Image.open(io.BytesIO(p.read_bytes())).convert("RGBA")).astype(int)
    leg = legend_colours(layer, len(vals))
    rgb, a = im[..., :3], im[..., 3]
    d = np.linalg.norm(rgb[..., None, :] - leg[None, None, :, :], axis=-1)
    idx = d.argmin(-1); ok = (a > 128) & (d.min(-1) < 40)
    grid = np.where(ok, np.array(vals, float)[idx], 0.0)
    out[layer] = grid[pi, pj]
    print(layer, f"{ok.mean() * 100:.0f} % of the map decoded")

sp = out["SRRTRESLAG"].astype(np.uint8)
np.savez_compressed(ROOT / "model" / "forest_sr16.npz", species=sp, height_m=out["SRRHOYDEM"].astype(np.float32), dom_height_m=out["SRRHOYDEO"].astype(np.float32),
                    cover=out["SRRKRONEDEK"].astype(np.float32), site_index=out["SRRBONITET"].astype(np.float32),
                    step=STEP, origin=-HALF, attribution="NIBIO SR16, CC BY 4.0")
# summary for the ecology note: detail area (construction scenes) and the whole 2 km square
for name, sel in (("detail area", (LX > -320) & (LX < 620) & (LY > -320) & (LY < 900)), ("2 km square", np.ones_like(LX, bool))):
    f = sel & (sp > 0)
    n = f.sum()
    mix = {k: f"{((sp == v) & f).sum() / max(n, 1) * 100:.0f} %" for k, v in (("spruce", 1), ("pine", 2), ("broadleaf", 3))}
    print(f"{name}: forested {n / sel.sum() * 100:.0f} %, mix {mix}, mean height {out['SRRHOYDEM'][f].mean():.1f} m, "
          f"cover {out['SRRKRONEDEK'][f].mean():.0f} %, site index H40 {out['SRRBONITET'][f & (out['SRRBONITET'] > 0)].mean():.1f}")
    dh = out["SRRHOYDEO"][f]
    print("   dominant height:", {k: f"{((dh >= a) & (dh < b)).mean() * 100:.0f} %" for k, (a, b) in
                                   {"clear-cut / regrowth < 4 m": (0, 4), "young 4-10 m": (4, 10), "mid 10-16 m": (10, 16), "mature > 16 m": (16, 99)}.items()})
    for v, nm in ((1, "spruce"), (2, "pine")):
        q = f & (sp == v)
        print(f"   {nm}: mean height {out['SRRHOYDEM'][q].mean():.1f} m, top height {out['SRRHOYDEO'][q].mean():.1f} m, cover {out['SRRKRONEDEK'][q].mean():.0f} %, H40 {out['SRRBONITET'][q & (out['SRRBONITET'] > 0)].mean():.1f}")

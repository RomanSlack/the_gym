"""Scout real Norwegian terrain for a site that fits the gym.

What we look for (from VISION.md):
  - a narrow incised gorge/ravine, 12-35 m deep (river at the bottom)
  - the ground right around it is mellow (drivable road, walkable trail)
  - real hills within ~2 km (relief 60-250 m), not alpine
  - below the tree line (forested)

Method on a 10 m DTM:
  gorge depth  = morphological black top-hat (closing - height) with an ~80 m wide
                 structuring element, so only *narrow* depressions show up
  mellowness   = mean slope of the "gorge-filled" (closed) surface within 250 m
  hills        = relief of the smoothed surface within a 2 km window

Run: .venv/bin/python scout.py   → out/scout/*.png + candidates.json
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from pyproj import Transformer
from dtm import fetch
from runlog import Run

RES = 10
HALF = 12_500
REGIONS = {  # centre in UTM33 (from lon/lat of a nearby town)
    "Nordmarka": (259518, 6664840),
    "Hurdal": (279883, 6705988),
    "Elverum": (313302, 6754320),
    "Trysil": (353817, 6800373),
    "Lillehammer": (256052, 6784604),
    "Kongsberg": (198837, 6626810),
    "Notodden": (175295, 6616476),
    "Meraker": (330024, 7031325),
}
OUT = Path(__file__).parent / "out" / "scout"


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def analyse(H):
    filled = np.where(np.isnan(H), np.nanmedian(H), H)
    closed = ndi.grey_closing(filled, footprint=disk(4))
    depth = closed - filled
    sm = ndi.gaussian_filter(closed, 2)
    gy, gx = np.gradient(sm, RES)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    mellow = ndi.uniform_filter(slope, 51)
    big = ndi.gaussian_filter(filled, 5)
    relief = ndi.maximum_filter(big, 201) - ndi.minimum_filter(big, 201)
    return depth, mellow, relief, filled


def candidates(name, cx, cy):
    H = fetch(cx - HALF, cy - HALF, cx + HALF, cy + HALF, RES)
    depth, mellow, relief, filled = analyse(H)
    ok = (
        (depth > 12) & (depth < 35) & (mellow < 7) & (relief > 60) & (relief < 250)
        & (filled > 60) & (filled < 650) & ~np.isnan(H)
    )
    lab, n = ndi.label(ok, structure=np.ones((3, 3)))
    found = []
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        m = lab[sl] == k
        if m.sum() < 15:  # under ~150 m of gorge
            continue
        d = np.where(m, depth[sl], 0)
        j, i = np.unravel_index(np.argmax(d), d.shape)
        j += sl[0].start; i += sl[1].start
        score = (
            -abs(depth[j, i] - 20) / 10    # ~20 m deep is ideal
            - mellow[j, i] / 4             # flatter surroundings
            + min(m.sum(), 80) / 40        # longer gorge
            - abs(relief[j, i] - 120) / 120
        )
        found.append({
            "region": name, "x": int(cx - HALF + i * RES), "y": int(cy - HALF + j * RES),
            "depth": round(float(depth[j, i]), 1), "mellow_slope": round(float(mellow[j, i]), 1),
            "relief_2km": round(float(relief[j, i]), 0), "elev": round(float(filled[j, i]), 0),
            "gorge_len_m": int(m.sum() * RES), "score": round(float(score), 2),
        })
    # keep the best per ~3 km so one long gorge doesn't fill the list
    found.sort(key=lambda c: -c["score"])
    kept = []
    for c in found:
        if all(np.hypot(c["x"] - o["x"], c["y"] - o["y"]) > 3000 for o in kept):
            kept.append(c)
    print(f"{name}: {n} raw, {len(kept)} kept")
    return kept[:4]


def sheet(cands, run):
    ls = LightSource(azdeg=315, altdeg=40)
    to_ll = Transformer.from_crs(25833, 4326, always_xy=True)
    n = len(cands)
    cols = 4
    fig, axs = plt.subplots((n + cols - 1) // cols, cols, figsize=(5 * cols, 5.4 * ((n + cols - 1) // cols)))
    for ax, (k, c) in zip(axs.flat, enumerate(cands, 1)):
        h = 1250
        H = fetch(c["x"] - h, c["y"] - h, c["x"] + h, c["y"] + h, RES)
        H = np.where(np.isnan(H), np.nanmin(H), H)
        ax.imshow(ls.shade(H, plt.cm.gist_earth, vert_exag=2, blend_mode="soft", dx=RES, dy=RES),
                  origin="lower", extent=[-h, h, -h, h])
        ax.contour(np.linspace(-h, h, H.shape[1]), np.linspace(-h, h, H.shape[0]), H,
                   levels=np.arange(0, 2000, 10), colors="k", linewidths=0.25, alpha=0.5)
        ax.plot(0, 0, "o", ms=14, mfc="none", mec="red", mew=2)
        lon, lat = to_ll.transform(c["x"], c["y"])
        c["lonlat"] = [round(lon, 5), round(lat, 5)]
        ax.set_title(f"#{k} {c['region']}  ({lat:.4f}, {lon:.4f})\n"
                     f"gorge {c['depth']} m deep · {c['gorge_len_m']} m long · "
                     f"slope {c['mellow_slope']}° · hills {c['relief_2km']:.0f} m · {c['elev']:.0f} masl",
                     fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    for ax in list(axs.flat)[n:]:
        ax.axis("off")
    fig.suptitle("Site scout · 2.5 × 2.5 km each · real terrain © Kartverket (CC BY 4.0)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "candidates.png", dpi=90)
    run.preview(fig, "candidates.png", dpi=90)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    run = Run("scout", {"res_m": RES, "half_m": HALF, "regions": REGIONS,
                        "criteria": "depth 12-35 m, mellow slope < 7 deg, 2 km relief 60-250 m, 60-650 masl"})
    allc = []
    for name, (cx, cy) in REGIONS.items():
        allc += candidates(name, cx, cy)
    allc.sort(key=lambda c: -c["score"])
    top = allc[:12]
    sheet(top, run)
    js = json.dumps(top, indent=1)
    (OUT / "candidates.json").write_text(js)
    (run.dir / "candidates.json").write_text(js)
    run.output("candidates.json", js.encode(), count=len(top))
    print("run", run.close())
    print(json.dumps(top, indent=1))

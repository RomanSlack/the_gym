"""Lock the Elverum site into project coordinates.

Project frame: x east, y north, metres, origin at the real gorge's thalweg centroid,
rotated so the real gorge flows due south (bearing 121° → 180°). The surrounding
land's drainage stays consistent with a north→south river.

  utm = ORIGIN + R(ROT) · (x, y)

Outputs (out/site/, not committed; reproducible):
  core_1m.npy     2 x 2 km, 1 m   (x, y in [-1000, 1000))
  context_4m.npy  8 x 8 km, 4 m   (x, y in [-4000, 4000))
  thalweg.json    the real gorge bottom line in project coords (for measuring principles)
Writes model/building.json site.georef and a versioned run with previews.
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from dtm import fetch
from runlog import Run

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).parent / "out" / "site"
ORIGIN = (303729.0, 6763432.0)  # EPSG:25833, real gorge thalweg centroid (compare run 20261010T235929Z)
ROT = 59.0                      # degrees CCW from project frame to UTM grid
REAL_THALWEG = Path(__file__).parent / "runs" / "20261010T235929Z_compare" / "summary.json"


def R():
    a = np.radians(ROT)
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def to_utm(x, y):
    u = R() @ np.stack([np.ravel(x), np.ravel(y)])
    return u[0] + ORIGIN[0], u[1] + ORIGIN[1]


def to_project(e, n):
    p = R().T @ np.stack([np.ravel(e) - ORIGIN[0], np.ravel(n) - ORIGIN[1]])
    return p[0], p[1]


def build(half, res):
    """Resample real terrain onto the rotated project grid. Row 0 = south (y = -half)."""
    g = np.arange(-half, half, res) + res / 2
    X, Y = np.meshgrid(g, g)
    E, N = to_utm(X, Y)
    m = half * 1.45 + 50  # rotated square needs a bigger axis-aligned fetch
    x0, y0 = ORIGIN[0] - m, ORIGIN[1] - m
    src = fetch(x0, y0, ORIGIN[0] + m, ORIGIN[1] + m, res)
    rows = (N - y0) / res - 0.5
    cols = (E - x0) / res - 0.5
    out = ndi.map_coordinates(np.nan_to_num(src, nan=np.nanmin(src)), [rows, cols], order=1)
    return out.reshape(X.shape).astype(np.float32)


def shade(ax, H, half, title):
    ls = LightSource(azdeg=315, altdeg=35)
    step = max(1, H.shape[0] // 1000)
    Hs = H[::step, ::step]
    ax.imshow(ls.shade(Hs, plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", dx=2 * half / Hs.shape[0], dy=2 * half / Hs.shape[0]),
              origin="lower", extent=[-half, half, -half, half])
    g = np.linspace(-half, half, Hs.shape[0])
    ax.contour(g, g, Hs, levels=np.arange(0, 2000, 5 if half <= 1000 else 20), colors="k", linewidths=0.2, alpha=0.5)
    ax.set_title(title)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    run = Run("site", {"site": "Elverum", "epsg": 25833, "origin_utm": ORIGIN, "rotation_deg": ROT,
                       "core": {"half_m": 1000, "res_m": 1}, "context": {"half_m": 4000, "res_m": 4}})
    core = build(1000, 1.0)
    context = build(4000, 4.0)
    np.save(OUT / "core_1m.npy", core)
    np.save(OUT / "context_4m.npy", context)
    run.output("core_1m.npy", core.tobytes(), shape=list(core.shape))
    run.output("context_4m.npy", context.tobytes(), shape=list(context.shape))

    # the real gorge's thalweg, in project coords (compare.py measured it around the old centre)
    s = json.loads(REAL_THALWEG.read_text())["elverum"]
    cu = s["utm33"]
    t = np.array(s["thalweg_xyz"])
    tx, ty = to_project(t[:, 0] + cu[0], t[:, 1] + cu[1])
    thalweg = [[round(float(a), 1), round(float(b), 1), float(z)] for a, b, z in zip(tx, ty, t[:, 2])]
    (OUT / "thalweg.json").write_text(json.dumps(thalweg))

    origin_masl = float(core[1000, 1000])
    import modelio
    m = modelio.load()
    m["site"]["georef"] = {
        "name": "Elverum, Norway", "epsg": 25833, "origin_utm": list(ORIGIN), "rotation_deg": ROT,
        "transform": "utm = origin_utm + R(rotation_deg) · (x, y), CCW", "terrain_source": "Kartverket DTM 1 m (CC BY 4.0)",
        "real_terrain_at_origin_masl": round(origin_masl, 2),
    }
    modelio.save(m)

    fig, axs = plt.subplots(1, 2, figsize=(18, 9))
    shade(axs[0], context, 4000, "Context 8 x 8 km (4 m), project frame, north up")
    axs[0].add_patch(plt.Rectangle((-1000, -1000), 2000, 2000, fill=False, ec="red"))
    shade(axs[1], core, 1000, "Core 2 x 2 km (1 m), real gorge flows south")
    axs[1].plot(tx, ty, "b-", lw=1.5)
    axs[1].plot(0, 0, "r+", ms=14)
    fig.tight_layout()
    run.preview(fig, "site.png", dpi=55)
    print("origin masl", origin_masl, "thalweg y range", float(ty.min()), float(ty.max()))
    print("run", run.close())

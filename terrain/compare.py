"""Compare shortlisted sites at 1 m: gorge axis, flow direction, bed steps, cross-section.

.venv/bin/python compare.py  → run record in runs/<time>_compare/ (+ heightfields in out/sites/)
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

SITES = {  # Roman's picks (lat, lon)
    "elverum": (60.957134978644476, 11.374034776801052),
    "kongsberg": (59.73026381543895, 9.819572022369893),
}
HALF = 1000  # 2 x 2 km
RES = 1.0
OUT = Path(__file__).parent / "out" / "sites"


def thalweg(H, cx, cy, radius=350):
    """Points along the gorge bottom near the centre: local depth (top-hat) > 6 m."""
    small = H[::4, ::4]  # 4 m grid for speed
    closed = ndi.grey_closing(np.nan_to_num(small, nan=np.nanmean(small)), size=(25, 25))
    depth = closed - small
    jj, ii = np.nonzero(depth > 6)
    x, y = ii * 4 - HALF, jj * 4 - HALF
    keep = np.hypot(x, y) < radius
    return x[keep], y[keep], depth[jj[keep], ii[keep]]


def analyse(name, H):
    x, y, d = thalweg(H, 0, 0)
    pts = np.stack([x, y], 1).astype(float)
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis = vt[0]  # unit vector along the gorge
    # longitudinal profile: lowest point in each 10 m slab across the axis
    s = (pts - c) @ axis
    bins = np.arange(-radius_of(s), radius_of(s) + 10, 10)
    prof = []
    for b0, b1 in zip(bins[:-1], bins[1:]):
        m = (s >= b0) & (s < b1)
        if m.any():
            k = np.argmin([H[int(py + HALF), int(px + HALF)] for px, py in zip(x[m], y[m])])
            px, py = x[m][k], y[m][k]
            prof.append(((b0 + b1) / 2, float(H[int(py + HALF), int(px + HALF)]), float(px), float(py)))
    prof = np.array(prof)
    # orient axis downstream
    if prof[0, 1] < prof[-1, 1]:
        axis, prof = -axis, np.column_stack([-prof[::-1, 0], prof[::-1, 1:]])
    bearing = (np.degrees(np.arctan2(axis[0], axis[1])) + 360) % 360  # flow direction, 0 = north
    drops = np.diff(prof[:, 1])
    steepest = float(-drops.min()) if len(drops) else 0
    # cross-section through the centre, perpendicular to the axis
    n = np.array([-axis[1], axis[0]])
    t = np.arange(-150, 151, 1.0)
    cs = [H[int(np.clip(c[1] + n[1] * u + HALF, 0, 2 * HALF - 1)), int(np.clip(c[0] + n[0] * u + HALF, 0, 2 * HALF - 1))] for u in t]
    return {"center_offset": c.tolist(), "axis": axis.tolist(), "flow_bearing_deg": round(float(bearing)),
            "bed_drop_over_profile_m": round(float(prof[0, 1] - prof[-1, 1]), 1),
            "steepest_10m_drop_m": round(steepest, 1), "profile": prof,
            "thalweg_xyz": [[round(r[2], 1), round(r[3], 1), round(r[1], 2)] for r in prof],
            "step_at": int(np.argmin(drops)) if len(drops) else 0, "cross": (t, np.array(cs))}


def radius_of(s):
    return float(np.ceil(np.abs(s).max() / 10) * 10)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    run = Run("compare", {"sites_latlon": SITES, "half_m": HALF, "res_m": RES})
    to_utm = Transformer.from_crs(4326, 25833, always_xy=True)
    ls = LightSource(azdeg=315, altdeg=35)
    fig, axs = plt.subplots(len(SITES), 3, figsize=(21, 7 * len(SITES)), gridspec_kw={"width_ratios": [1.2, 1, 1]})
    summary = {}
    for row, (name, (lat, lon)) in enumerate(SITES.items()):
        cx, cy = to_utm.transform(lon, lat)
        cx, cy = round(cx), round(cy)
        H = fetch(cx - HALF, cy - HALF, cx + HALF, cy + HALF, RES)
        np.save(OUT / f"{name}_1m.npy", H)
        a = analyse(name, H)
        summary[name] = {k: v for k, v in a.items() if k not in ("profile", "cross")} | {"utm33": [cx, cy], "elev_range": [float(np.nanmin(H)), float(np.nanmax(H))]}
        run.output(f"{name}_1m.npy", H.tobytes(), shape=list(H.shape), utm33_center=[cx, cy])

        ax = axs[row, 0]
        Hf = np.where(np.isnan(H), np.nanmin(H), H)
        ax.imshow(ls.shade(Hf[::2, ::2], plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", dx=2, dy=2),
                  origin="lower", extent=[-HALF, HALF, -HALF, HALF])
        g = np.arange(-HALF, HALF, 4.0)
        ax.contour(g, g, Hf[::4, ::4], levels=np.arange(0, 2000, 5), colors="k", linewidths=0.2, alpha=0.5)
        ax.arrow(*a["center_offset"], *(np.array(a["axis"]) * 200), width=6, color="#1e6fd9")
        ax.set_title(f"{name}: flow toward {a['flow_bearing_deg']}° (0 = north), 2 x 2 km, 5 m contours")
        ax = axs[row, 1]
        p = a["profile"]
        ax.plot(p[:, 0], p[:, 1], "-o", ms=2)
        ax.set_title(f"riverbed along gorge (downstream →): drop {summary[name]['bed_drop_over_profile_m']} m, steepest 10 m: {summary[name]['steepest_10m_drop_m']} m")
        ax.set_xlabel("m along gorge"); ax.set_ylabel("masl"); ax.grid(alpha=0.3)
        ax = axs[row, 2]
        t, cs = a["cross"]
        ax.fill_between(t, cs, np.nanmin(cs) - 5, color="#b9a88f")
        ax.set_aspect("equal"); ax.set_title("cross-section at centre (true scale)"); ax.set_xlabel("m"); ax.grid(alpha=0.3)
    fig.tight_layout()
    run.preview(fig, "compare.png", dpi=55)
    (run.dir / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    print("run", run.close())

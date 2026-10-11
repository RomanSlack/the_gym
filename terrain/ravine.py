"""Build the site terrain: real Elverum surroundings + our parametric ravine.

1. Erase the real gorge between the two junctions with the real stream (GPU harmonic fill).
2. Carve the ravine from model site.ravine.stations:
     carve(p) = bed + max(0, |d| - half_bed) * tan(wall_angle)        (d = distance to centerline)
     terrain  = smooth_min(base, carve)                               (rounded rims; crisp in rock)
   with low-amplitude noise on widths, walls and bed so it doesn't look extruded.
3. Building pads (excavations) from site.pads.
4. Water surface grid and rock mask.

Heights are stored relative to the ±0.00 datum (F1 = model project.datum.masl).
.venv/bin/python ravine.py  → out/ravine/*.npy + run record (plan, long profile, sections)
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree
from matplotlib.path import Path as MPath
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import modelio
from principles import harmonic_fill
from runlog import Run

HERE = Path(__file__).parent
SITE, OUT = HERE / "out" / "site", HERE / "out" / "ravine"
HALF, RES = 1000, 1.0
g = np.arange(-HALF, HALF, RES) + RES / 2
X, Y = np.meshgrid(g, g)  # row 0 = south


def fbm(seed, scale_m, octaves=4):
    """Smooth noise in [-1, 1]-ish with features around `scale_m`."""
    rng = np.random.default_rng(seed)
    out = np.zeros(X.shape, np.float32)
    amp = 1.0
    for o in range(octaves):
        s = scale_m / (2 ** o)
        n = ndi.gaussian_filter(rng.standard_normal(X.shape).astype(np.float32), s / RES / 2)
        out += amp * n / (n.std() + 1e-9)
        amp *= 0.5
    return out / 1.9


def upstream_real_path(H):
    """Greedy trace of the real stream from y=380 north to y=660 (lowest point per row)."""
    pts, x = [], -12
    for y in range(380, 661, 4):
        xs = np.arange(max(-990, x - 40), min(990, x + 40))
        row = H[y + HALF, xs + HALF]
        x = int(xs[np.argmin(row)])
        pts.append((x, y))
    return np.array(pts, float)


def erase_real(H, path, y_lo, y_hi, reach=75.0):
    tree = cKDTree(path)
    d, _ = tree.query(np.stack([X.ravel(), Y.ravel()], 1), distance_upper_bound=reach + 1)
    mask = (d.reshape(X.shape) < reach) & (Y > y_lo - 70) & (Y < y_hi + 20)
    filled = harmonic_fill(H, mask)
    dist = ndi.distance_transform_edt(mask) * RES
    taper = np.clip((Y - y_lo) / 60, 0, 1) * np.clip((y_hi - Y) / 40, 0, 1)
    w = np.clip(dist / 15, 0, 1) * taper
    return (H * (1 - w) + np.maximum(H, filled) * w).astype(np.float32)


def centerline(stations, step=0.5):
    st = sorted(stations, key=lambda s: -s["y"])
    ys = np.array([s["y"] for s in st], float)
    yy = np.arange(ys[0], ys[-1] - 1e-6, -step)
    xfn = PchipInterpolator(ys[::-1], np.array([s["x"] for s in st], float)[::-1])
    attr = lambda k: np.interp(yy, ys[::-1], np.array([float(s[k]) for s in st])[::-1])
    P = np.stack([xfn(yy), yy], 1)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    return P, T, {k: attr(k) for k in ("bed", "water", "half_bed", "wall_w", "wall_e", "rock")}


def fill_sinks(H, keep, min_depth=0.3):
    """Every cell must drain: find closed depressions (morphological reconstruction),
    except inside `keep` (the river channel and its pools), and fill them smoothly."""
    from skimage.morphology import reconstruction
    seed = H.copy()
    seed[1:-1, 1:-1] = H.max()
    filled = reconstruction(seed, H, method="erosion")
    sink = (filled - H > min_depth) & ~ndi.binary_dilation(keep, iterations=3)
    if not sink.any():
        return H
    mask = ndi.binary_dilation(sink, iterations=8)
    smooth = harmonic_fill(np.maximum(H, filled).astype(np.float32), mask)
    out = np.where(mask, np.maximum(smooth, filled), H).astype(np.float32)
    print(f"filled {int(sink.sum())} m² of closed depressions")
    return out


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    m = modelio.load()
    rv, datum = m["site"]["ravine"], m["project"]["datum"]["masl"]
    run = Run("ravine", {"stations": rv["stations"], "pads": m["site"]["pads"], "datum_masl": datum, "noise_seeds": [1, 2, 3, 4]})

    real = np.load(SITE / "core_1m.npy") - datum
    down = np.array(json.loads((SITE / "real_thalweg_full.json").read_text()))
    path = np.vstack([upstream_real_path(real + datum)[::-1], down])
    base = erase_real(real, path, rv["joins_real_stream"]["south_y"], rv["joins_real_stream"]["north_y"])

    P, T, A = centerline(rv["stations"])
    tree = cKDTree(P)
    pts = np.stack([X.ravel(), Y.ravel()], 1)
    d, idx = tree.query(pts, distance_upper_bound=250)
    near = np.isfinite(d) & (idx > 2) & (idx < len(P) - 3)  # ignore caps beyond the end stations
    idx = np.where(np.isfinite(d), idx, 0)
    d = np.where(np.isfinite(d), d, 1e9).reshape(X.shape)
    near = near.reshape(X.shape)
    idx = idx.reshape(X.shape)
    c = P[idx]
    t = T[idx]
    side_e = (t[..., 0] * (Y - c[..., 1]) - t[..., 1] * (X - c[..., 0])) > 0  # east of the flow (flow runs south)
    rock = A["rock"][idx]
    n_width, n_wall, n_bed, n_ledge = fbm(1, 30), fbm(2, 20), fbm(3, 8), fbm(4, 6, 3)
    half = A["half_bed"][idx] * (1 + 0.18 * n_width)
    wall = np.where(side_e, A["wall_e"][idx], A["wall_w"][idx]) + 5 * n_wall * (0.5 + 0.5 * rock)
    wall = np.clip(wall, 15, 87.5)
    bed = A["bed"][idx] + 0.35 * n_bed
    carve = bed + np.maximum(0, d - half) * np.tan(np.radians(wall))
    carve += rock * 0.6 * np.round(n_ledge * 2) / 2 * (d > half)  # blocky ledges on rock walls
    carve = np.where(near, carve, 1e6)
    k = 2.5 * (1 - rock) + 0.5 * rock
    terrain = smin(base, carve, k).astype(np.float32)

    terrain = fill_sinks(terrain, keep=near & (d < A["half_bed"][idx] + 30))

    pad_mask = np.zeros(X.shape, bool)
    for pad in m["site"]["pads"]:
        inside = MPath(pad["poly"]).contains_points(pts).reshape(X.shape)
        terrain[inside] = pad["z"]
        pad_mask |= inside

    water_lvl = A["water"][idx]
    wet = near & (terrain < water_lvl) & (d < A["half_bed"][idx] + 25) & ~pad_mask
    lab, _ = ndi.label(wet)
    on_line = np.unique(lab[(d < 1.0) & wet])
    wet &= np.isin(lab, on_line[on_line > 0])
    water = np.where(wet, water_lvl, np.nan).astype(np.float32)
    gy, gx = np.gradient(terrain, RES)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    rockmask = np.clip((slope - 38) / 15, 0, 1) * np.clip(0.3 + rock, 0, 1)
    rockmask = np.maximum(rockmask, np.clip((slope - 55) / 10, 0, 1))  # any very steep face is rock
    np.save(OUT / "terrain_1m.npy", terrain)
    np.save(OUT / "water_1m.npy", water)
    np.save(OUT / "rock_1m.npy", rockmask.astype(np.float32))
    np.save(OUT / "centerline.npy", np.column_stack([P, A["bed"], A["water"]]))
    for name in ("terrain_1m", "water_1m", "rock_1m"):
        run.output(f"{name}.npy", np.load(OUT / f"{name}.npy").tobytes())

    # ---- previews ----
    ls = LightSource(azdeg=315, altdeg=35)
    fig = plt.figure(figsize=(24, 16))
    ax = fig.add_subplot(2, 3, (1, 4))
    cw = 320
    sl = slice(HALF - cw, HALF + cw)
    Z = terrain[sl, sl]
    ax.imshow(ls.shade(Z, plt.cm.gist_earth, vert_exag=1.2, blend_mode="soft", dx=1, dy=1), origin="lower", extent=[-cw, cw, -cw, cw])
    ax.imshow(np.where(np.isnan(water[sl, sl]), np.nan, 1), origin="lower", extent=[-cw, cw, -cw, cw], cmap="Blues", vmin=0, vmax=1.4, alpha=0.8)
    ax.contour(g[sl], g[sl], Z, levels=np.arange(-60, 30, 2), colors="k", linewidths=0.2, alpha=0.5)
    for pad in m["site"]["pads"]:
        pp = np.array(pad["poly"] + [pad["poly"][0]])
        ax.plot(pp[:, 0], pp[:, 1], "r-", lw=1)
    for s in rv["stations"]:
        if abs(s["y"]) < cw and abs(s["x"]) < cw:
            ax.annotate(s["id"], (s["x"], s["y"]), fontsize=7, color="navy")
    ax.set_title("plan ±320 m: terrain, water, building pads (red), stations")
    ax = fig.add_subplot(2, 3, 2)
    ax.imshow(ls.shade(terrain[::2, ::2], plt.cm.gist_earth, vert_exag=1.2, blend_mode="soft", dx=2, dy=2), origin="lower", extent=[-HALF, HALF, -HALF, HALF])
    ax.plot(P[:, 0], P[:, 1], "b-", lw=0.8)
    ax.set_title("core 2 x 2 km")
    ax = fig.add_subplot(2, 3, 3)
    tline = ndi.map_coordinates(terrain, [P[:, 1] + HALF - 0.5, P[:, 0] + HALF - 0.5], order=1)
    ax.plot(P[:, 1], tline, color="#8a7658", label="terrain on centerline")
    ax.plot(P[:, 1], A["water"], color="#2a7ab0", label="water")
    for s in rv["stations"]:
        ax.plot(s["y"], s["bed"], "k.", ms=4)
    for lv in m["levels"]:
        ax.axhline(lv["elevation"], color="gray", lw=0.5, ls="--")
        ax.text(-520, lv["elevation"], lv["id"], fontsize=7, va="bottom")
    ax.invert_xaxis(); ax.set_xlabel("y (north ← → south)"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("long profile along the river (levels dashed)")
    for i, (yc, ttl) in enumerate(((0, "y = 0 (through the link)"), (37, "y = 37 (falls 1 / rustic bridge)"), (-150, "y = -150 (falls 2)"))):
        ax = fig.add_subplot(4, 3, 9 + i)
        j = int(yc + HALF)
        xs = g[HALF - 80:HALF + 80]
        ax.fill_between(xs, terrain[j, HALF - 80:HALF + 80], -45, color="#b9a88f")
        ax.plot(xs, water[j, HALF - 80:HALF + 80], color="#2a7ab0", lw=2)
        for lv in m["levels"]:
            ax.axhline(lv["elevation"], color="gray", lw=0.4, ls="--")
        ax.set_aspect("equal"); ax.set_ylim(-30, 10); ax.set_title(ttl, fontsize=9)
    fig.tight_layout()
    run.preview(fig, "ravine.png", dpi=55)
    print("water cells", int(wet.sum()), "terrain range", float(terrain.min()), float(terrain.max()))
    print("run", run.close())

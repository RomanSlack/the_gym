"""Measure the real Elverum gorge's shape rules, then erase it from the core terrain.

1. Trace the full thalweg (gorge bottom) through the core by following the lowest
   point, stepping downstream.
2. Every 10 m, cut a cross-section perpendicular to the flow and measure depth,
   rim-to-rim width, width at half depth, bed width and wall steepness.
3. Longitudinal profile: gradient, steps (knickpoints) and pools, step spacing.
4. Planform: sinuosity and meander wavelength / amplitude.
5. Erase the gorge (fill it to the surrounding plateau surface and blend), giving
   base_1m.npy: real surroundings, ready for our parametric ravine.

.venv/bin/python principles.py → principles/elverum_gorge.json + run record
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from runlog import Run

HERE = Path(__file__).parent
SITE = HERE / "out" / "site"
HALF, RES = 1000, 1.0


def sample(H, x, y):
    """Bilinear height at project coords (arrays ok)."""
    return ndi.map_coordinates(H, [np.asarray(y) / RES + HALF / RES - 0.5, np.asarray(x) / RES + HALF / RES - 0.5], order=1, mode="nearest")


def trace(H, start, heading, step=5.0, search=20.0, ymin=-960):
    """Follow the gorge bottom downstream from `start`."""
    p, d = np.array(start, float), np.array(heading, float) / np.linalg.norm(heading)
    pts = [p.copy()]
    while abs(p[0]) < 960 and p[1] > ymin and len(pts) < 600:
        q = p + d * step
        n = np.array([-d[1], d[0]])
        offs = np.linspace(-search, search, 41)
        cand = q[None] + offs[:, None] * n[None]
        z = sample(H, cand[:, 0], cand[:, 1]) + 0.002 * offs ** 2  # gentle pull to straight ahead
        nq = cand[np.argmin(z)]
        nd = (nq - p) / np.linalg.norm(nq - p)
        d = 0.7 * d + 0.3 * nd
        d /= np.linalg.norm(d)
        p = nq
        pts.append(p.copy())
    return np.array(pts)


def trace_up(H, start, heading, step=5.0, search=20.0):
    """Follow the gorge upstream: the lowest point across, while it stays incised."""
    p, d = np.array(start, float), np.array(heading, float) / np.linalg.norm(heading)
    pts = [p.copy()]
    while abs(p[0]) < 960 and abs(p[1]) < 960 and len(pts) < 300:
        q = p + d * step
        n = np.array([-d[1], d[0]])
        offs = np.linspace(-search, search, 41)
        cand = q[None] + offs[:, None] * n[None]
        z = sample(H, cand[:, 0], cand[:, 1]) + 0.002 * offs ** 2
        nq = cand[np.argmin(z)]
        side = sample(H, nq[0] + n[0] * np.array([-50, 50]), nq[1] + n[1] * np.array([-50, 50]))
        if side.min() - sample(H, [nq[0]], [nq[1]])[0] < 3:  # no longer a gorge
            break
        nd = (nq - p) / np.linalg.norm(nq - p)
        d = 0.7 * d + 0.3 * nd
        d /= np.linalg.norm(d)
        p = nq
        pts.append(p.copy())
    return np.array(pts)


def cross_sections(H, path, every=10.0):
    seg = np.diff(path, axis=0)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(seg, axis=1))])
    out = []
    t = np.arange(-70, 70.5, 0.5)
    for si in np.arange(0, s[-1], every):
        k = min(np.searchsorted(s, si), len(path) - 2)
        p, d = path[k], seg[k] / np.linalg.norm(seg[k])
        n = np.array([-d[1], d[0]])
        z = sample(H, p[0] + t * n[0], p[1] + t * n[1])
        bed = z[np.abs(t) < 8].min()
        left, right = z[t < 0], z[t > 0]
        rim = min(left.max(), right.max())
        depth = rim - bed
        if depth < 3:
            continue

        def width_at(level):
            inside = np.nonzero(z <= level)[0]
            c = np.argmin(np.abs(t))
            lo = c
            while lo > 0 and z[lo - 1] <= level: lo -= 1
            hi = c
            while hi < len(z) - 1 and z[hi + 1] <= level: hi += 1
            return float(t[hi] - t[lo])

        slopes = np.degrees(np.arctan(np.abs(np.gradient(z, 0.5))))
        wall = slopes[(z > bed + 0.15 * depth) & (z < rim - 0.15 * depth)]
        out.append({"s": float(si), "x": float(p[0]), "y": float(p[1]), "bed": float(bed), "rim": float(rim),
                    "depth": float(depth), "w_rim": width_at(rim - 0.5), "w_half": width_at(bed + depth / 2),
                    "w_bed": width_at(bed + 0.5), "wall_deg_med": float(np.median(wall)) if wall.size else None,
                    "wall_deg_max": float(wall.max()) if wall.size else None})
    return out


def harmonic_fill(H, mask, iters=(4000, 1500, 600, 300)):
    """Replace H inside `mask` with the smoothest surface matching H at the mask edge
    (Laplace equation), solved coarse-to-fine on the GPU."""
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    Ht = torch.tensor(H, device=dev)
    Mt = torch.tensor(mask, device=dev)
    levels = len(iters)
    Z = None
    for li, n in enumerate(iters):
        f = 2 ** (levels - 1 - li)
        h = torch.nn.functional.avg_pool2d(Ht[None, None], f)[0, 0] if f > 1 else Ht
        m = torch.nn.functional.max_pool2d(Mt[None, None].float(), f)[0, 0] > 0 if f > 1 else Mt
        if Z is None:
            Z = h.clone()
        else:
            Z = torch.nn.functional.interpolate(Z[None, None], size=h.shape, mode="bilinear", align_corners=False)[0, 0]
        Z = torch.where(m, Z, h)
        for _ in range(n):
            avg = torch.nn.functional.avg_pool2d(torch.nn.functional.pad(Z[None, None], (1, 1, 1, 1), mode="replicate"), 3, 1)[0, 0]
            Z = torch.where(m, avg, h)
    return Z.cpu().numpy()


def erase(H, path, reach=75.0, ymin=-500.0):
    """Remove the real gorge near `path` (north of ymin): harmonic fill, feathered edge."""
    yy, xx = np.mgrid[0:H.shape[0], 0:H.shape[1]]
    X, Y = xx * RES - HALF + 0.5, yy * RES - HALF + 0.5
    mask = np.zeros(H.shape, bool)
    for p in path[::2]:
        if p[1] < ymin:
            continue
        i, j = int(p[0] + HALF), int(p[1] + HALF)
        r = int(reach)
        sl = (slice(max(0, j - r), j + r), slice(max(0, i - r), i + r))
        mask[sl] |= np.hypot(X[sl] - p[0], Y[sl] - p[1]) < reach
    # taper the south end so the erased reach blends into the real valley that continues
    taper = np.clip((Y - ymin) / 60.0, 0, 1)
    filled = harmonic_fill(H, mask)
    dist = ndi.distance_transform_edt(mask) * RES
    w = np.clip(dist / 15.0, 0, 1) * taper  # feather inside the mask edge
    return (H * (1 - w) + np.maximum(H, filled) * w).astype(np.float32)


if __name__ == "__main__":
    H = np.load(SITE / "core_1m.npy")
    real = np.array(json.loads((SITE / "thalweg.json").read_text()))
    run = Run("principles", {"source": "core_1m.npy (site run 20261011T000314Z)", "trace_step_m": 5, "section_every_m": 10})
    start = real[0, :2]
    down = trace(H, start, real[3, :2] - real[0, :2])
    up = trace_up(H, start, real[0, :2] - real[3, :2])
    path = np.vstack([up[::-1], down[1:]])
    xs = cross_sections(H, path)
    A = {k: np.array([c[k] for c in xs if c[k] is not None]) for k in xs[0]}

    # longitudinal profile
    bed = A["bed"]; s = A["s"]
    drops = -np.diff(bed)
    steps = [(float(s[i]), float(drops[i])) for i in np.nonzero(drops > 1.5)[0]]
    step_spacing = np.diff([a for a, _ in steps]).tolist()
    # planform
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    length = float(seg.sum())
    chord = float(np.linalg.norm(path[-1] - path[0]))
    axis = (path[-1] - path[0]) / chord
    lateral = (path - path[0]) @ np.array([-axis[1], axis[0]])
    zc = np.nonzero(np.diff(np.sign(lateral - lateral.mean())))[0]
    half_waves = np.diff(np.concatenate([[0], np.cumsum(seg)])[zc]) if len(zc) > 1 else np.array([np.nan])

    P = {
        "source": "Elverum, Kartverket DTM 1 m, traced in project frame",
        "traced_length_m": round(length), "sinuosity": round(length / chord, 3),
        "meander_wavelength_m_median": round(float(np.median(half_waves) * 2), 1),
        "meander_amplitude_m": round(float(np.percentile(np.abs(lateral - lateral.mean()), 90)), 1),
        "depth_m": {"median": round(float(np.median(A["depth"])), 1), "p90": round(float(np.percentile(A["depth"], 90)), 1), "max": round(float(A["depth"].max()), 1)},
        "width_rim_m_median": round(float(np.median(A["w_rim"])), 1),
        "width_half_depth_m_median": round(float(np.median(A["w_half"])), 1),
        "bed_width_m_median": round(float(np.median(A["w_bed"])), 1),
        "rim_width_to_depth": round(float(np.median(A["w_rim"] / A["depth"])), 2),
        "wall_slope_deg": {"median": round(float(np.median(A["wall_deg_med"])), 1), "p90_of_max": round(float(np.percentile(A["wall_deg_max"], 90)), 1)},
        "bed_gradient_pct": round(float((bed[0] - bed[-1]) / (s[-1] - s[0]) * 100), 2),
        "steps_gt_1_5m": [{"at_m": round(a), "drop_m": round(d, 1)} for a, d in steps],
        "step_spacing_m_median": round(float(np.median(step_spacing)), 1) if step_spacing else None,
        "note": "1 m lidar smooths vertical rock; real walls are steeper than wall_slope_deg suggests.",
    }
    (HERE / "principles").mkdir(exist_ok=True)
    js = json.dumps(P, indent=1)
    (HERE / "principles" / "elverum_gorge.json").write_text(js)
    (run.dir / "elverum_gorge.json").write_text(js)
    run.output("elverum_gorge.json", js.encode())

    base = erase(H, path)
    np.save(SITE / "base_1m.npy", base)
    run.output("base_1m.npy", base.tobytes(), note="core with the real gorge erased")
    (SITE / "real_thalweg_full.json").write_text(json.dumps(path.round(1).tolist()))

    ls = LightSource(azdeg=315, altdeg=35)
    fig, axs = plt.subplots(2, 3, figsize=(24, 15))
    for ax, Z, ttl in ((axs[0, 0], H, "real core (gorge traced in blue)"), (axs[0, 1], base, "base: real gorge erased")):
        ax.imshow(ls.shade(Z[::2, ::2], plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", dx=2, dy=2), origin="lower", extent=[-HALF, HALF, -HALF, HALF])
        g = np.arange(-HALF, HALF, 2.0)
        ax.contour(g, g, Z[::2, ::2], levels=np.arange(400, 600, 5), colors="k", linewidths=0.2, alpha=0.5)
        ax.set_title(ttl)
    axs[0, 0].plot(path[:, 0], path[:, 1], "b-", lw=1)
    ax = axs[0, 2]
    ax.plot(s, bed, label="bed"); ax.plot(s, A["rim"], label="rim (lower side)")
    for a, d in steps: ax.axvline(a, color="r", alpha=0.3)
    ax.set_title("longitudinal: bed and rim (red = steps > 1.5 m)"); ax.set_xlabel("m downstream"); ax.legend(); ax.grid(alpha=0.3)
    ax = axs[1, 0]
    ax.plot(s, A["depth"], label="depth"); ax.plot(s, A["w_rim"], label="rim width"); ax.plot(s, A["w_bed"], label="bed width")
    ax.set_title("cross-section measures"); ax.legend(); ax.grid(alpha=0.3); ax.set_xlabel("m downstream")
    ax = axs[1, 1]
    t = np.arange(-70, 70.5, 0.5)
    for c in xs[::max(1, len(xs) // 12)]:
        k = int(np.argmin(np.linalg.norm(path - [c["x"], c["y"]], axis=1)))
        d = path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]; d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
        z = sample(H, c["x"] + t * n[0], c["y"] + t * n[1])
        ax.plot(t, z - c["rim"], lw=0.8, alpha=0.7)
    ax.set_aspect("equal"); ax.set_title("cross-sections, aligned to rim (true scale)"); ax.grid(alpha=0.3)
    ax = axs[1, 2]
    ax.axis("off")
    ax.text(0, 1, js, va="top", family="monospace", fontsize=9)
    fig.tight_layout()
    run.preview(fig, "principles.png", dpi=50)
    print(js)
    print("run", run.close())

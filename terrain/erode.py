"""GPU erosion pass over the carved site (PyTorch, CUDA).

Hydraulic: "virtual pipes" shallow-water model (Mei, Decaudin, Hu 2007): rain →
flux between cells → velocity → sediment capacity → erode / deposit → advect
sediment → evaporate. Thermal: material above its talus angle slides downhill
(soil ~34°, rock ~75°). Designed features (riverbed, pools, sills, pads) are
protected and restored, so erosion only naturalises the land around them.

.venv/bin/python erode.py [steps]  → out/ravine/eroded_1m.npy, frames in .capture/terrain/<run>/
"""
import sys
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import modelio
from runlog import Run

HERE = Path(__file__).parent
RV = HERE / "out" / "ravine"
dev = "cuda"

P = dict(steps=int(sys.argv[1]) if len(sys.argv) > 1 else 1500, dt=0.05, rain=0.004, evap=0.02,
         Kc=0.6, Ks=0.012, Kd=0.02, min_slope=0.03, talus_soil=34.0, talus_rock=75.0, thermal_rate=0.15,
         rock_erodibility=0.15, micro_relief_m=0.15, veg_slope_deg=(8.0, 20.0), seed=7)


def shift(a, dy, dx):
    """a shifted so that out[i,j] = a[i-dy, j-dx], edges replicated."""
    p = F.pad(a[None, None], (1, 1, 1, 1), mode="replicate")[0, 0]
    return p[1 - dy:p.shape[0] - 1 - dy, 1 - dx:p.shape[1] - 1 - dx]


def fbm(shape, seed, scales=(20, 10, 5)):
    rng = np.random.default_rng(seed)
    out = np.zeros(shape, np.float32)
    for k, s in enumerate(scales):
        n = ndi.gaussian_filter(rng.standard_normal(shape).astype(np.float32), s / 2)
        out += n / (n.std() + 1e-9) * 0.5 ** k
    return out / 1.75


if __name__ == "__main__":
    m = modelio.load()
    H0 = np.load(RV / "terrain_1m.npy")
    water_design = np.load(RV / "water_1m.npy")
    rock = np.load(RV / "rock_1m.npy")
    run = Run("erode", P | {"input": "out/ravine/terrain_1m.npy"})

    # protected = designed water bodies + pads (+ a margin), softly feathered
    protect = ~np.isnan(water_design) | (np.load(RV / "features_1m.npy") > 0)  # river + site works
    from matplotlib.path import Path as MPath
    g = np.arange(-1000, 1000) + 0.5
    X, Y = np.meshgrid(g, g)
    pts = np.stack([X.ravel(), Y.ravel()], 1)
    for pad in m["site"]["pads"]:
        protect |= MPath(pad["poly"]).contains_points(pts).reshape(X.shape)
    protect = ndi.gaussian_filter(ndi.binary_dilation(protect, iterations=3).astype(np.float32), 1.5).clip(0, 1)

    H0 = H0 + P["micro_relief_m"] * fbm(H0.shape, P["seed"]) * (1 - protect) * (1 - 0.6 * rock)

    t = lambda a: torch.tensor(a, device=dev, dtype=torch.float32)
    h, R, keep = t(H0), t(rock), t(protect)
    w = torch.zeros_like(h); s = torch.zeros_like(h)
    fL = torch.zeros_like(h); fR = torch.zeros_like(h); fT = torch.zeros_like(h); fB = torch.zeros_like(h)
    # forest floor (roots, moss) holds gentle ground: erosion only bites on steeper banks
    gy0, gx0 = np.gradient(ndi.gaussian_filter(H0, 2))
    slope0 = np.degrees(np.arctan(np.hypot(gx0, gy0)))
    lo, hi = P["veg_slope_deg"]
    veg = t(np.clip((slope0 - lo) / (hi - lo), 0, 1))
    erodibility = (1 - R * (1 - P["rock_erodibility"])) * (1 - keep) * veg
    talus = torch.tan(torch.deg2rad(P["talus_soil"] + R * (P["talus_rock"] - P["talus_soil"])))
    dt, g_ = P["dt"], 9.81
    ls = LightSource(azdeg=315, altdeg=35)
    crop = slice(1000 - 256, 1000 + 256)
    fig = plt.figure(figsize=(6, 6))

    for it in range(P["steps"]):
        w = w + P["rain"] * dt
        H = h + w
        # outflow flux to each neighbour (left, right, top=+y, bottom=-y)
        fL = torch.clamp(fL + dt * g_ * (H - shift(H, 0, 1)), min=0)
        fR = torch.clamp(fR + dt * g_ * (H - shift(H, 0, -1)), min=0)
        fT = torch.clamp(fT + dt * g_ * (H - shift(H, -1, 0)), min=0)
        fB = torch.clamp(fB + dt * g_ * (H - shift(H, 1, 0)), min=0)
        out = (fL + fR + fT + fB) * dt
        K = torch.clamp(w / (out + 1e-9), max=1.0)
        fL, fR, fT, fB = fL * K, fR * K, fT * K, fB * K
        inflow = shift(fR, 0, 1) + shift(fL, 0, -1) + shift(fT, 1, 0) + shift(fB, -1, 0)
        w_new = torch.clamp(w + dt * (inflow - (fL + fR + fT + fB)), min=0)
        wm = 0.5 * (w + w_new) + 1e-4
        vx = (shift(fR, 0, 1) - fL + fR - shift(fL, 0, -1)) / 2 / wm
        vy = (shift(fT, 1, 0) - fB + fT - shift(fB, -1, 0)) / 2 / wm
        w = w_new
        # sediment capacity, erosion / deposition
        gx = (shift(h, 0, -1) - shift(h, 0, 1)) / 2
        gy = (shift(h, -1, 0) - shift(h, 1, 0)) / 2
        sin_a = torch.clamp(torch.sqrt(gx * gx + gy * gy) / torch.sqrt(1 + gx * gx + gy * gy), min=P["min_slope"])
        C = P["Kc"] * sin_a * torch.sqrt(vx * vx + vy * vy) * torch.clamp(w * 10, max=1)
        dep = torch.where(C > s, -P["Ks"] * (C - s) * erodibility, P["Kd"] * (s - C))
        h = h + dep
        s = torch.clamp(s - dep, min=0)
        # advect sediment (semi-Lagrangian, bilinear)
        H_, W_ = h.shape
        yy, xx = torch.meshgrid(torch.arange(H_, device=dev, dtype=torch.float32), torch.arange(W_, device=dev, dtype=torch.float32), indexing="ij")
        sx = (xx - vx * dt) / (W_ - 1) * 2 - 1
        sy = (yy - vy * dt) / (H_ - 1) * 2 - 1
        s = F.grid_sample(s[None, None], torch.stack([sx, sy], -1)[None], align_corners=True, padding_mode="border")[0, 0]
        w = w * (1 - P["evap"] * dt)
        # thermal: move material that exceeds the talus slope toward lower neighbours
        if it % 2 == 0:
            moved = torch.zeros_like(h)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nb = shift(h, dy, dx)
                dist = (dx * dx + dy * dy) ** 0.5
                excess = torch.clamp(h - nb - talus * dist, min=0) * P["thermal_rate"] * 0.125 * (1 - keep)
                moved = moved - excess + shift(excess, -dy, -dx)
            h = h + moved
        if it % 25 == 0 or it == P["steps"] - 1:
            hc = h[crop, crop].cpu().numpy()
            fig.clf()
            ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
            ax.imshow(ls.shade(hc, plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", vmin=-30, vmax=15), origin="lower")
            ax.imshow(np.clip(w[crop, crop].cpu().numpy() * 8, 0, 1), origin="lower", cmap="Blues", alpha=0.35, vmin=0, vmax=1)
            run.frame(it, fig)
            print(it, f"water {w.mean().item():.4f} sediment {s.mean().item():.5f} dh {(h - t(H0)).abs().mean().item():.4f}", flush=True)

    Hn = h.cpu().numpy()
    Hn = H0 + ndi.gaussian_filter(Hn - H0, 0.8)  # remove grid-aligned noise from the change field
    Hn = Hn * (1 - protect) + np.load(RV / "terrain_1m.npy") * protect  # restore designed features exactly
    np.save(RV / "eroded_1m.npy", Hn.astype(np.float32))
    run.output("eroded_1m.npy", Hn.astype(np.float32).tobytes(), mean_abs_change_m=float(np.abs(Hn - H0).mean()))

    fig2, axs = plt.subplots(1, 3, figsize=(24, 8))
    before = np.load(RV / "terrain_1m.npy")[crop, crop]
    for ax, Z, ttl in ((axs[0], before, "carved (before)"), (axs[1], Hn[crop, crop], f"eroded, {P['steps']} steps")):
        ax.imshow(ls.shade(Z, plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", vmin=-30, vmax=15), origin="lower", extent=[-256, 256, -256, 256])
        ax.set_title(ttl)
    im = axs[2].imshow(Hn[crop, crop] - before, origin="lower", cmap="RdBu", vmin=-1.5, vmax=1.5, extent=[-256, 256, -256, 256])
    axs[2].set_title("change (m): blue = deposited, red = eroded"); plt.colorbar(im, ax=axs[2], shrink=0.7)
    fig2.tight_layout()
    run.preview(fig2, "erode.png", dpi=55)
    print("run", run.close())

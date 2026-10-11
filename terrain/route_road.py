"""Lay out the forest road like a road engineer would: least-cost route over the
terrain (steep ground, the ravine and the buildings are expensive), smoothed into
flowing curves, then a vertical profile capped at the max grade. Writes the
alignment into model site.features.road so it becomes editable design data.

.venv/bin/python route_road.py
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.interpolate import splprep, splev
from skimage.graph import route_through_array
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import modelio
from runlog import Run

C = 4.0  # cost grid resolution (m)
H = np.load("out/ravine/eroded_1m.npy")
m = modelio.load()
F = m["site"]["features"]
road = F["road"]
end = np.array(F["arrival_court"]["center"], float)

h = H.reshape(500, 4, 500, 4).mean((1, 3))
gy, gx = np.gradient(ndi.gaussian_filter(h, 1.5), C)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
cost = 1 + (slope / 5.0) ** 2.5                      # gentle ground is cheap
cl = np.load("out/ravine/centerline.npy")[:, :2]
g = np.arange(-1000, 1000, C) + C / 2
X, Y = np.meshgrid(g, g)
from scipy.spatial import cKDTree
d_river, _ = cKDTree(cl).query(np.stack([X.ravel(), Y.ravel()], 1))
cost += 400 * (d_river.reshape(X.shape) < 35)        # never along / across the ravine
keep_out = [(-40, -40, 34, 60), (10, 30, 45, 62)]    # buildings, garden, bridge landing (xmin, ymin, xmax, ymax)
for x0, y0, x1, y1 in keep_out:
    cost += 400 * ((X > x0) & (X < x1) & (Y > y0) & (Y < y1))

to_ij = lambda p: (int((p[1] + 1000) / C), int((p[0] + 1000) / C))
best = None
for ys in range(-400, 650, 50):  # try entries along the east edge
    path, c = route_through_array(cost, to_ij((996, ys)), to_ij(end), fully_connected=True, geometric=True)
    if best is None or c < best[1]:
        best = (path, c, ys)
path, total, ys = best
P = np.array([[g[j], g[i]] for i, j in path])
# drop the last stretch and finish with a straight approach into the court from the east
P = P[np.linalg.norm(P - end, axis=1) > 110]
P = np.vstack([P, end + [70, -2], end + [40, 0], end + [15, 0], end])
# smooth into flowing curves, keeping the terrain's smaller bends
tck, _ = splprep([P[:, 0], P[:, 1]], s=len(P) * 6)
L = np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))
u = np.linspace(0, 1, int(L / 2))
S = np.stack(splev(u, tck), 1)
S[-1] = end
# vertical profile: smoothed ground, then cap the grade in both directions
zg = ndi.map_coordinates(H, [S[:, 1] + 999.5, S[:, 0] + 999.5], order=1)
seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))]
z = ndi.gaussian_filter1d(zg, 12)
z[-1] = F["arrival_court"]["z"]
blend = np.clip((seg - (seg[-1] - 90)) / 90, 0, 1)  # ease into the court over the last 90 m
z = z * (1 - blend) + F["arrival_court"]["z"] * blend
gmax = road["max_grade_pct"] / 100
for _ in range(3):
    for k in range(len(z) - 2, -1, -1):  # from the court outward
        z[k] = np.clip(z[k], z[k + 1] - gmax * (seg[k + 1] - seg[k]), z[k + 1] + gmax * (seg[k + 1] - seg[k]))
    for k in range(1, len(z)):
        z[k] = np.clip(z[k], z[k - 1] - gmax * (seg[k] - seg[k - 1]), z[k - 1] + gmax * (seg[k] - seg[k - 1]))
pts = np.column_stack([S, z])[::5]  # every ~10 m
pts[-1] = [*end, F["arrival_court"]["z"]]
road["points"] = [[round(float(a), 1), round(float(b), 1), round(float(c), 2)] for a, b, c in pts]
road["length_m"] = round(float(seg[-1]))
road["entry"] = f"east edge of the core at y = {ys}"
modelio.save(m)

run = Run("road", {"cost": "1 + (slope/5deg)^2.5, ravine and buildings excluded", "grid_m": C,
                   "max_grade_pct": road["max_grade_pct"], "entry_tried": "east edge y -400..600 step 50"})
fig, axs = plt.subplots(1, 2, figsize=(22, 9), gridspec_kw={"width_ratios": [1, 1.4]})
ls = LightSource(azdeg=315, altdeg=35)
axs[0].imshow(ls.shade(H[::2, ::2], plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", dx=2, dy=2), origin="lower", extent=[-1000, 1000, -1000, 1000])
axs[0].plot(S[:, 0], S[:, 1], "k-", lw=2.5); axs[0].plot(cl[:, 0], cl[:, 1], "b-", lw=1)
axs[0].set_title(f"road: {seg[-1]:.0f} m from the east edge (y={ys}) to the arrival court")
grade = np.gradient(z, seg) * 100
axs[1].plot(seg, zg, color="#8a7658", label="ground"); axs[1].plot(seg, z, "k", label="road")
ax2 = axs[1].twinx(); ax2.plot(seg, grade, color="r", alpha=0.4); ax2.set_ylabel("grade %", color="r")
axs[1].legend(); axs[1].grid(alpha=0.3); axs[1].set_title(f"profile, max grade {np.abs(grade).max():.1f}%")
fig.tight_layout()
run.preview(fig, "road.png", dpi=55)
run.output("road", str(road["points"]).encode(), length_m=road["length_m"])
print(road["entry"], road["length_m"], "m, max grade", round(float(np.abs(grade).max()), 1))
print("run", run.close())

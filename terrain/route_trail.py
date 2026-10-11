"""Lay out the 2-mile trail loop: least-cost legs between design waypoints (gentle
ground cheap, buildings/garden/court/ravine expensive except at the two crossings),
waypoints scaled about the loop centre until the loop is ~3.2 km, smoothed, with a
graded profile. Stream crossings become bridge spans (terrain is not filled there).

.venv/bin/python route_trail.py → model site.features.trail + run record
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree
from skimage.graph import route_through_array
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import modelio
from runlog import Run

C = 4.0
H = np.load("out/ravine/eroded_1m.npy")
m = modelio.load()
F = m["site"]["features"]
tr = F["trail"]
crossings = np.array([c["at"] for c in tr["crossings"]], float)

h = H.reshape(500, 4, 500, 4).mean((1, 3))
gy, gx = np.gradient(ndi.gaussian_filter(h, 1.5), C)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
g = np.arange(-1000, 1000, C) + C / 2
X, Y = np.meshgrid(g, g)
cl = np.load("out/ravine/centerline.npy")[:, :2]
# the real stream continues north of our ravine (y > 660): trace it so the trail treats it as water too
Hs = ndi.gaussian_filter(H, 2)
ext, x = [], int(cl[0, 0])
for y in range(int(cl[0, 1]), 995, 3):
    xs = np.arange(max(-995, x - 12), min(995, x + 12))
    x = int(xs[np.argmin(Hs[y + 1000, xs + 1000])])
    ext.append((x, y))
cl = np.vstack([np.array(ext[::-1], float), cl])
d_river = cKDTree(cl).query(np.stack([X.ravel(), Y.ravel()], 1))[0].reshape(X.shape)
d_cross = cKDTree(crossings).query(np.stack([X.ravel(), Y.ravel()], 1))[0].reshape(X.shape)
cost = 1 + (slope / 6.0) ** 3.0
cost += 300 * ((d_river < 13) & (d_cross > 22))           # stay out of the ravine except at the crossings
for x0, y0, x1, y1 in tr["keep_out"]:
    cost += 300 * ((X > x0) & (X < x1) & (Y > y0) & (Y < y1))
road_xy = np.array([p[:2] for p in F["road"]["points"]])
cost += 6 * (cKDTree(road_xy).query(np.stack([X.ravel(), Y.ravel()], 1))[0].reshape(X.shape) < 8)
to_ij = lambda p: (int(np.clip((p[1] + 1000) / C, 0, 499)), int(np.clip((p[0] + 1000) / C, 0, 499)))

# direction-aware graph: each step costs its length x (1 + (grade along the step / comfort)^4),
# so climbing straight up a bank is expensive and diagonal traverses / switchbacks win
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
hs = ndi.gaussian_filter(h, 1.0)
N = 500
idx = np.arange(N * N).reshape(N, N)
penalty = (cost - (1 + (slope / 6.0) ** 3.0))  # river / keep-out / road penalties only
rows, cols, wts = [], [], []
for di, dj in ((0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)):
    a = idx[max(0, -di):N - max(0, di), max(0, -dj):N - max(0, dj)]
    b = idx[max(0, di):N - max(0, -di) or None, max(0, dj):N - max(0, -dj) or None]
    L = C * (2 ** 0.5 if di and dj else 1.0)
    dz = hs.ravel()[b] - hs.ravel()[a]
    w = L * (1 + (np.abs(dz) / L / 0.07) ** 4) + L * penalty.ravel()[b]
    rows.append(a.ravel()); cols.append(b.ravel()); wts.append(w.ravel())
G = coo_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(N * N, N * N)).tocsr()


def leg(a, b):
    sa, sb = idx[to_ij(a)], idx[to_ij(b)]
    _, pred = dijkstra(G, indices=sa, return_predecessors=True)
    out, k = [], sb
    while k != sa and k >= 0:
        out.append(k); k = pred[k]
    out.append(sa)
    return [[g[k % N], g[k // N]] for k in out[::-1]]


def route(wps):
    pts = []
    direct = set(tr.get("direct_legs", []))
    for i, (a, b) in enumerate(zip(wps, wps[1:] + wps[:1])):
        if i in direct:  # hand-placed leg (bridge approaches near the buildings): straight, no routing
            n = max(2, int(np.hypot(b[0] - a[0], b[1] - a[1]) / 2))
            pts += [[a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n] for k in range(n)]
        else:
            pts += leg(a, b)[:-1]
    P = np.array(pts)
    return P, float(np.sum(np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)))


base = np.array(tr["waypoints"], float)
fixed = np.array(tr["fixed"], bool)          # waypoints that must not move (bridges, sauna)
centre = base.mean(0)
k = 1.0
for _ in range(12 if not fixed.all() else 1):  # scale the free waypoints until the loop is ~target
    wps = np.where(fixed[:, None], base, centre + (base - centre) * k)
    P, L = route(wps.tolist())
    if abs(L - tr["target_m"]) < 60:
        break
    k *= (tr["target_m"] / L) ** 0.9
# remove out-and-back spurs: if the path comes back within 8 m of an earlier point after a short detour, cut the detour
changed = True
while changed:
    changed = False
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    tree = cKDTree(P)
    for i in range(len(P)):
        for j in sorted(tree.query_ball_point(P[i], 8.0), reverse=True):
            if j > i + 4 and 25 < arc[j] - arc[i] < 900:
                P = np.vstack([P[:i + 1], P[j + 1:]])
                changed = True
                break
        if changed:
            break
L = float(np.sum(np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)))
tck, _ = splprep([P[:, 0], P[:, 1]], s=len(P) * 1.5, per=True)
u = np.linspace(0, 1, int(L / 2), endpoint=False)
S = np.stack(splev(u, tck), 1)
# snap onto fixed bridge decks (the rustic bridge): no smoothing bulge over the falls
on_deck = np.zeros(len(S), bool)
for c in tr["crossings"]:
    if "axis" in c:
        a0, a1 = np.array(c["axis"], float)
        ab = a1 - a0; t_ = np.clip(((S - a0) @ ab) / (ab @ ab), 0, 1)
        proj = a0 + t_[:, None] * ab
        near = (np.linalg.norm(S - proj, axis=1) < 12) & (t_ > 0) & (t_ < 1)
        S[near] = proj[near]
        on_deck |= near
seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))]
zg = ndi.map_coordinates(ndi.gaussian_filter(H, 3), [S[:, 1] + 999.5, S[:, 0] + 999.5], order=1)
z = ndi.gaussian_filter1d(zg, 4, mode="wrap")
# bridges: where the trail passes within the crossing zones over the river, hold a level deck
dr = cKDTree(cl).query(S)[0]
dc = cKDTree(crossings).query(S)[0]
axis_xs = [c for c in tr["crossings"] if "axis" in c]
far_from_decks = np.ones(len(S), bool)
for c in axis_xs:
    far_from_decks &= np.linalg.norm(S - np.array(c["at"]), axis=1) > 30
over = on_deck | ((dr < 16) & (dc < 30) & far_from_decks)
lab, n = ndi.label(over)
bridges = []
for b in range(1, n + 1):
    idx = np.nonzero(lab == b)[0]
    i0, i1 = max(idx[0] - 2, 0), min(idx[-1] + 2, len(S) - 1)
    fixed_deck = [c.get("deck_z") for c in tr["crossings"] if np.hypot(*(np.array(c["at"]) - S[idx].mean(0))) < 40]
    if fixed_deck and fixed_deck[0] is not None:
        deck = fixed_deck[0]
    else:  # span the little valley high, at forest-floor level, so the trail stays level
        deck = min(zg[max(i0 - 12, 0)], zg[min(i1 + 12, len(S) - 1)])
        while i0 > 0 and zg[i0] < deck - 1.0:
            i0 -= 1
        while i1 < len(S) - 1 and zg[i1] < deck - 1.0:
            i1 += 1
    z[i0:i1 + 1] = deck
    bridges.append({"from": [round(float(S[i0, 0]), 1), round(float(S[i0, 1]), 1)],
                    "to": [round(float(S[i1, 0]), 1), round(float(S[i1, 1]), 1)], "deck_z": round(float(deck), 2),
                    "span_m": round(float(seg[i1] - seg[i0]), 1)})
grade = np.abs(np.gradient(z, seg)) * 100
tr["points"] = [[round(float(a), 1), round(float(b), 1), round(float(c), 2), int(o)] for a, b, c, o in zip(S[::3, 0], S[::3, 1], z[::3], over[::3])]
tr["length_m"] = round(float(seg[-1]))
tr["bridges"] = bridges
tr["max_grade_pct"] = round(float(np.percentile(grade, 98)), 1)
modelio.save(m)

run = Run("trail", {"target_m": tr["target_m"], "waypoints": tr["waypoints"], "scale": round(k, 3), "crossings": tr["crossings"]})
fig, axs = plt.subplots(1, 2, figsize=(22, 10), gridspec_kw={"width_ratios": [1, 1.3]})
ls = LightSource(azdeg=315, altdeg=35)
axs[0].imshow(ls.shade(H[::2, ::2], plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft", dx=2, dy=2), origin="lower", extent=[-1000, 1000, -1000, 1000])
axs[0].plot(S[:, 0], S[:, 1], "-", color="#d2691e", lw=2)
axs[0].plot(cl[:, 0], cl[:, 1], "b-", lw=1)
axs[0].plot(road_xy[:, 0], road_xy[:, 1], "k-", lw=2)
for b in bridges:
    axs[0].plot(*np.array([b["from"], b["to"]]).T, "r-", lw=5)
axs[0].set_xlim(-650, 750); axs[0].set_ylim(-150, 1000)
axs[0].set_title(f"trail loop {seg[-1]:.0f} m ({seg[-1] / 1609:.2f} mi), bridges in red")
axs[1].plot(seg, zg, color="#8a7658", label="ground"); axs[1].plot(seg, z, color="#d2691e", label="trail")
axs[1].legend(); axs[1].grid(alpha=0.3); axs[1].set_title(f"profile (98th pct grade {tr['max_grade_pct']}%)")
fig.tight_layout()
run.preview(fig, "trail.png", dpi=50)
run.output("trail", str(tr["points"]).encode(), length_m=tr["length_m"])
print("length", tr["length_m"], "m, bridges", [(b["span_m"], b["deck_z"]) for b in bridges], "grade98", tr["max_grade_pct"], "scale", round(k, 2))
print("run", run.close())

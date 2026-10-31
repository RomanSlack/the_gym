"""Walk the gym layouts the way members would (Roman 2026-10-31: "do some simulations of someone walking through how a crowd would
use it ... make sure ... it makes sense with the orientation of stuff"; "you literally have to phase through machines").

The floor on a 0.1 m grid: the walls (doors open), every piece's body, the spiral, the stair openings and the den river are solid.
Every piece also has its training space (its use clearance from gym_layout: in front of the user, the loading sides, behind);
walking through someone else's training space is allowed but costs 8x (they're lifting there). A member is a 0.6 m wide body
(0.3 m from their centre line to anything solid); where only a sideways squeeze gets through (0.46 m) the piece is "squeeze only".

1. Access: from the floor's ways in (the spiral's step-off, every door's landing), the cheapest walk to each piece's own training
   space. Flags: no way in at all, a squeeze only, the best way in crosses someone else's training space (the "phasing").
2. Crowd: 400 members each do a session (a warm-up piece, 4-6 stations, a wipes station after each, out again), the paths summed
   into a traffic map; the pieces whose training space the crowd walks through most, and the busy pinch points (< 1.2 m clear).

    cd tools && ../terrain/.venv/bin/python gym_walk_sim.py gym_f2 [--png /tmp/x.png]
"""
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
import shapely

import gym_layout as G

ROOT = Path(__file__).resolve().parents[1]
RES = 0.1
R_BODY, R_SQUEEZE = 0.3, 0.23
USE_COST = 8.0
QUIET = ("floor_zone", "route", "keep_clear", "pwr_meta", "pwr_bar", "turf", "void", "stair", "den_river")


def wall_polys(data, parts=False):
    """The walls as solids, their doors + openings (from the floor) cut out."""
    out = []
    for w in data["walls"]:
        (ax, ay), (bx, by) = w["from"], w["to"]
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-6:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L; t = w["size"][0] / 2
        segs, s = [], 0.0
        for o in sorted((o for o in w["openings"] if o["type"] in ("door", "opening") and o["z"][0] < 0.2), key=lambda o: o["s"][0]):
            segs.append((s, o["s"][0])); s = o["s"][1]
        segs.append((s, L))
        for s0, s1 in segs:
            if s1 - s0 < 1e-3:
                continue
            p0, p1 = (ax + ux * s0, ay + uy * s0), (ax + ux * s1, ay + uy * s1)
            out.append(Polygon([(p0[0] - uy * t, p0[1] + ux * t), (p1[0] - uy * t, p1[1] + ux * t), (p1[0] + uy * t, p1[1] - ux * t), (p0[0] + uy * t, p0[1] - ux * t)]))
    return out if parts else unary_union(out)


class Floor:
    def __init__(self, name):
        self.name = name
        self.d = json.loads((ROOT / "model" / "layouts" / f"{name}.json").read_text())
        d, K = self.d, self.d["kinds"]
        K = {k_: dict(v) for k_, v in K.items()}
        for v in K.values():   # a treadmill's 2 m run-off is kept clear of things, not of people: you walk behind a treadmill
            if v.get("tag") in ("treadmill", "HD tread") and v.get("use"):
                v["use"] = [v["use"][0], 0.4, v["use"][2], v["use"][3]]
        self.K = K
        self.room = unary_union([Polygon(s["poly"]) for s in d["spaces"]]).buffer(0.3, join_style=2)   # spaces are drawn to the walls' centre lines
        self.walls = wall_polys(d)
        byid = {it["id"]: it for it in d["items"]}
        self.items = [it for it in d["items"] if it["kind"] not in QUIET]
        self.bodies, self.uses, self.flat = {}, {}, set()
        for it in self.items:
            p = G.item_poly(it, K)
            if p is None or p.is_empty:
                continue
            self.bodies[it["id"]] = p
            u = G.item_poly(it, K, use=True) if it["kind"] in K and K[it["kind"]].get("use") and not it.get("fixed") else None
            if it["kind"] == "wipe_station":
                u = None
            low = K.get(it["kind"], {}).get("mat") == "platform" and (it.get("h") or K[it["kind"]].get("h", 1)) < 0.13
            if low:                                    # a lifting platform is floor you step onto: all of it is its training space
                self.flat.add(it["id"])
            if u is not None and it.get("on") is None:
                self.uses[it["id"]] = u if low else u.difference(p)
        # a piece on another (a rack on its platform, a bench in a rack) trains in its carrier's space
        self.carrier = {}
        for it in self.items:
            r = it
            while r.get("on") in byid:
                r = byid[r["on"]]
            self.carrier[it["id"]] = r["id"]
        solid = [self.walls] + [p for i, p in self.bodies.items() if i not in self.flat]
        solid += [G.item_poly(it, K) for it in d["items"] if it["kind"] in ("void", "stair", "den_river")]
        self.solid = unary_union([s for s in solid if s is not None])
        self.ways_in = [(it["id"], G.item_poly(it, K).centroid) for it in d["items"]
                        if it["kind"] == "keep_clear" and (it["id"].startswith("clear-") or it["id"].startswith("spiral-landing"))]
        x0, y0, x1, y1 = self.room.bounds
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int((x1 - x0) / RES) + 1, int((y1 - y0) / RES) + 1
        xs = x0 + (np.arange(self.nx) + 0.5) * RES; ys = y0 + (np.arange(self.ny) + 0.5) * RES
        self.X, self.Y = np.meshgrid(xs, ys, indexing="ij")
        inside = shapely.contains_xy(self.room, self.X, self.Y)
        hard = shapely.contains_xy(self.solid, self.X, self.Y)
        free = inside & ~hard
        self.clear = ndimage.distance_transform_edt(free) * RES          # distance to the nearest solid / outside
        self.walk = self.clear >= R_BODY
        self.squeeze = self.clear >= R_SQUEEZE
        self.use_owner = np.full((self.nx, self.ny), -1, dtype=int)
        self.use_ids = list(self.uses)
        for k, i in enumerate(self.use_ids):
            m = shapely.contains_xy(self.uses[i], self.X, self.Y)
            self.use_owner[m & (self.use_owner < 0)] = k
        soft = np.array([K.get(next(t["kind"] for t in self.items if t["id"] == i), {}).get("mat") in ("storage", "wallkit") for i in self.use_ids] + [True])
        self.soft = soft                                   # racks + trees you pick from: walking in front of them is what they're for
        self.in_use = (self.use_owner >= 0) & ~soft[self.use_owner]

    def cell(self, x, y):
        return int((x - self.x0) / RES), int((y - self.y0) / RES)

    def graph(self, ok, own=None):
        """8-connected walk graph over ok cells; training spaces cost USE_COST except `own` (a piece's own space)."""
        nx, ny = self.nx, self.ny
        idx = np.arange(nx * ny).reshape(nx, ny)
        w = np.where(self.in_use, USE_COST, 1.0)
        if own is not None:
            w = np.where(own, 1.0, w)
        rows, cols, vals = [], [], []
        for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
            if dy < 0:
                a = ok[:nx - dx, -dy:]; b = ok[dx:, :ny + dy]
                ia = idx[:nx - dx, -dy:]; ib = idx[dx:, :ny + dy]
                wa = w[:nx - dx, -dy:]; wb = w[dx:, :ny + dy]
            else:
                ia = idx[:nx - dx, :ny - dy]; ib = idx[dx:, dy:]
                wa = w[:nx - dx, :ny - dy]; wb = w[dx:, dy:]
                a = ok[:nx - dx, :ny - dy]; b = ok[dx:, dy:]
            m = a & b
            L = RES * math.hypot(dx, dy)
            c = (wa[m] + wb[m]) / 2 * L
            rows += [ia[m], ib[m]]; cols += [ib[m], ia[m]]; vals += [c, c]
        return coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nx * ny, nx * ny)).tocsr()

    def entry_cells(self, iid):
        """Where you stand to use a piece: its own training space (or its carrier's), else a ring round its body."""
        c = self.carrier.get(iid, iid)
        area = self.uses.get(c)
        if area is None or area.is_empty or area.area < 0.05:
            area = self.bodies[c].buffer(0.45).difference(self.bodies[c])
        return shapely.contains_xy(area, self.X, self.Y)


def run(name, png=None, n_members=400, seed=7):
    F = Floor(name)
    print(f"== {name}: {len(F.bodies)} pieces + fixtures, {len(F.ways_in)} ways in, grid {F.nx} x {F.ny}")
    src = [F.cell(p.x, p.y) for _, p in F.ways_in]
    src = [i * F.ny + j for i, j in src if 0 <= i < F.nx and 0 <= j < F.ny]
    targets = [it for it in F.items if it["id"] in F.bodies and not it.get("fixed") and it.get("on") is None
               and it["kind"] not in ("wipe_station", "rogue-freestanding-chalk-stand") and not it["kind"].startswith("pwr_core")]
    gw, gs = F.graph(F.walk), F.graph(F.squeeze)
    plain = np.where(F.walk, 1.0, 0.0)
    dist_w, pred_w, _ = dijkstra(gw, indices=src, min_only=True, return_predecessors=True)
    dist_s = dijkstra(gs, indices=src, min_only=True)
    probs = []
    for it in targets:
        e = F.entry_cells(it["id"]).ravel()
        own_k = F.use_ids.index(F.carrier[it["id"]]) if F.carrier[it["id"]] in F.use_ids else -1
        dw = np.where(e & F.walk.ravel(), dist_w, np.inf)
        if not np.isfinite(dw).any():
            ds = np.where(e & F.squeeze.ravel(), dist_s, np.inf)
            probs.append((3, f"{it['id']}: {'squeeze only (< 0.6 m)' if np.isfinite(ds).any() else 'NO WAY IN'}"))
            continue
        k = int(np.argmin(dw))
        # walk the path back, measure what it crosses
        crossed, n, cur = {}, 0, k
        while cur >= 0 and n < 100000:
            i, j = divmod(cur, F.ny)
            o = F.use_owner[i, j]
            if o >= 0 and o != own_k and not e[cur] and not F.soft[o]:   # (its own space, where it overlaps another's, is its own)
                crossed[F.use_ids[o]] = crossed.get(F.use_ids[o], 0) + 1
            cur = pred_w[cur]; n += 1
        serves = F.K.get(it["kind"], {}).get("mat") == "storage"     # a tree between two plate-loaded machines is loaded from their sides
        bad = {c_: v * RES for c_, v in crossed.items() if v * RES >= 0.6 and F.carrier.get(c_) != F.carrier[it["id"]]
               and not (serves and F.K.get(next(t["kind"] for t in F.items if t["id"] == c_), {}).get("mat") == "plate_loaded")}
        if bad:
            probs.append((2, f"{it['id']}: the way in crosses " + ", ".join(f"{c_} ({v:.1f} m)" for c_, v in sorted(bad.items(), key=lambda kv: -kv[1]))))
    print(f"   access: {len(targets)} pieces, {len(probs)} problems")
    for s, p in sorted(probs, key=lambda x: -x[0]):
        print("    ", "!" if s == 3 else "~", p)

    # ---- the crowd
    rnd = random.Random(seed)
    tgt = [it for it in targets if np.isfinite(np.where(F.entry_cells(it["id"]).ravel() & F.walk.ravel(), dist_w, np.inf)).any()
           and F.K.get(it["kind"], {}).get("mat") not in ("storage", "wallkit")]
    wipes = [it for it in F.items if it["kind"] == "wipe_station"]
    heat = np.zeros(F.nx * F.ny)
    through = {}
    gw_paths = {}
    def field(key, cells):
        if key not in gw_paths:
            gw_paths[key] = dijkstra(gw, indices=cells, min_only=True, return_predecessors=True)[:2]
        return gw_paths[key]
    def best_cell(it):
        e = (F.entry_cells(it["id"]) & F.walk).ravel()
        cs = np.flatnonzero(e)
        return cs[len(cs) // 2] if len(cs) else None
    cells = {it["id"]: best_cell(it) for it in tgt + wipes}
    def walk_to(from_cell, it):
        """the path from from_cell to the piece's training space (the field from its space, walked back)."""
        e = np.flatnonzero((F.entry_cells(it["id"]) & F.walk).ravel())
        if not len(e):
            return from_cell
        dist, pred = field(it["id"], e[:: max(1, len(e) // 40)])
        cur, n, own = from_cell, 0, F.carrier[it["id"]]
        if not np.isfinite(dist[cur]):
            return from_cell
        while cur >= 0 and n < 100000:
            heat[cur] += 1
            i, j = divmod(cur, F.ny); o = F.use_owner[i, j]
            if o >= 0 and F.use_ids[o] != own and not F.soft[o]:
                through[F.use_ids[o]] = through.get(F.use_ids[o], 0) + 1
            nxt = pred[cur]
            if nxt < 0:
                break
            cur, n = nxt, n + 1
        return cur
    for m in range(n_members):
        cur = rnd.choice(src)
        plan = rnd.sample(tgt, min(len(tgt), rnd.randint(5, 7)))
        for it in plan:
            cur = walk_to(cur, it)
            if wipes and rnd.random() < 0.7:
                wi = min(wipes, key=lambda w_: math.hypot(w_["x"] - F.X.ravel()[cur], w_["y"] - F.Y.ravel()[cur]))
                cur = walk_to(cur, wi)
        out = min(src, key=lambda s_: math.hypot(F.X.ravel()[s_] - F.X.ravel()[cur], F.Y.ravel()[s_] - F.Y.ravel()[cur]))
        d_, p_ = field(("out", out), [out])
        while cur >= 0 and cur != out and np.isfinite(d_[cur]):
            heat[cur] += 1; cur = p_[cur]
    heat = heat.reshape(F.nx, F.ny)
    # crossings per training space, per 100 members
    print("   the crowd walks through these training spaces most (crossings per 100 members):")
    for k_, v in sorted(through.items(), key=lambda kv: -kv[1])[:15]:
        print(f"     {k_}: {100 * v / n_members / 10:.0f} m walked through")
    width = 2 * ndimage.maximum_filter(F.clear, size=int(0.9 / RES))     # the corridor's width there: its centre line's clearance, x2
    busy = (heat > np.percentile(heat[heat > 0], 90)) & (width < 1.1) & F.walk
    lab, nlab = ndimage.label(busy)
    pins = []
    for l_ in range(1, nlab + 1):
        ii, jj = np.nonzero(lab == l_)
        if len(ii) < 3:
            continue
        pins.append((float(F.X[ii, jj].mean()), float(F.Y[ii, jj].mean()), float(width[ii, jj].min())))
    print(f"   busy pinch points (corridor < 1.1 m wide, top-10 % traffic): {len(pins)}")
    for x, y, w in pins:
        print(f"     ({x:.1f}, {y:.1f}) {w:.2f} m")
    if png:
        draw(F, heat, probs, pins, png)
    return probs, pins


def draw(F, heat, probs, pins, png, n_members=400):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MP
    x0, y0 = F.x0, F.y0
    ext = (x0, x0 + F.nx * RES, y0, y0 + F.ny * RES)
    h = F.ny * RES / (F.nx * RES)
    fig, ax = plt.subplots(figsize=(12, max(8, 12 * h)))
    hm = np.ma.masked_where(heat <= 0, np.log1p(heat))
    ax.imshow(hm.T, origin="lower", extent=ext, cmap="inferno_r", alpha=0.75)
    def poly(p, **kw):
        for g in getattr(p, "geoms", [p]):
            if not g.is_empty and hasattr(g, "exterior"):
                ax.add_patch(MP(list(g.exterior.coords), **kw))
    for wp in wall_polys(F.d, parts=True):
        poly(wp, fc="#222", ec="none")
    bad = {p.split(":")[0] for _, p in probs}
    for i, p in F.bodies.items():
        it = next(t for t in F.items if t["id"] == i)
        poly(p, fc="#e33" if i in bad else ("#7a7" if it["kind"] == "wipe_station" else "#9cf"), ec="#036", lw=0.4)
    for i, u in F.uses.items():
        poly(u, fc="none", ec="#888", lw=0.3, ls=":")
    for x, y, w in pins:
        ax.add_patch(plt.Circle((x, y), 0.5, fc="none", ec="#f0f", lw=1.5))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal")
    ax.set_title(f"{F.name}: {n_members} members' sessions, traffic (log scale); red = reached only through someone's training space; magenta = busy pinch < 1.1 m", fontsize=8)
    plt.tight_layout(); plt.savefig(png, dpi=90); plt.close(fig)
    print("   wrote", png)


if __name__ == "__main__":
    args = sys.argv[1:]
    png = None
    if "--png" in args:
        k = args.index("--png"); png = args[k + 1]; args = args[:k] + args[k + 2:]
    for nm in args:
        run(nm, png=png.replace(".png", f"_{nm}.png") if png and len(args) > 1 else png)

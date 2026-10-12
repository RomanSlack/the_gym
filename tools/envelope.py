"""Construction stage 4: envelope (style B, locked: dark tarred timber, sod roofs, divided glazing, stone plinth).

Read off the style references (docs/style/bdarksod_*.jpg) and turned into real build-ups (rules of thumb, noted on each element):
  - facades above grade (F1, E1, lounge, E2 glass): divided glazing, dark aluminium mullions on the structural rhythm
    (mullions at every column, panes <= 1.3 m; lounge sliding panels <= 2.3 m), a transom on glass taller than 3.6 m.
  - privacy rooms on a facade (changing, wet zones, WCs, staff, nursing): solid black timber wall + high obscured clerestory band
    (the solid dark panels in the references). Glass stays everywhere else (open plan).
    Timber wall build-up, outside -> in: 22 mm black tarred board-on-board pine, 48 mm battens / ventilated cavity, wind barrier,
    250 mm insulated timber frame, vapour barrier, 50 mm service cavity, lining = 0.40 m.
  - a solid black timber header band between the glass head and the roof (the dark band above the glass in the references).
  - stone plinth: 150 mm dry-laid granite on a 50 mm cavity, on every concrete wall face that shows above the finished ground
    (river wall, gorge faces, towers, lift shafts). The river-wall openings run through it.
  - river glazing: structural acrylic in the river-wall openings (F4 underwater windows, F3 waist-high river window in ~3 m panels,
    F2 view band divided like the facades).
  - sod roofs: on the CLT: membrane, 250 mm PIR (tapered to falls), drainage mat, 120 mm sedum / meadow substrate + turf = 0.45 m;
    a thin dark folded-aluminium roof edge on every free edge, oak soffit boards under the eaves (beam tails stay exposed).
  - glass balustrades (1.1 m) on the lounge decks over the river.
  - skylights + the W3 sod roof (already in the model) join phase 4.
python3 tools/envelope.py   (run by tools/build_model.py, after structure_stage)
"""
import math
import sys
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}
els = [e for e in m["elements"] if not e["id"].startswith("EN-")]
by_id = {e["id"]: e for e in els}
new = []
seq_of = lambda z0: int(round((z0 + 20) * 10))


def add(e):
    e["phase"] = 4
    e.setdefault("seq", seq_of(e["z"][0]))
    new.append(e)


# ---- existing envelope bits join phase 4
for e in els:
    if e.get("phase") is None and ((e["type"] == "slab" and e["material"] in ("glass", "sod"))):
        e["phase"], e["seq"] = 4, seq_of(e["z"][0])

# ---- facade glulam posts get the black tar stain of the cladding (the dark posts in the references); beams + soffits stay warm
for e in els:
    if e["type"] == "column" and e["material"] == "glulam":
        e["finish"] = "black_stain"
    if e["id"].startswith("A-annex-"):  # sauna-lobby annex: CLT walls get the same black tarred boards
        e["finish"] = "black_stain"

# ---- facades: split every facade glass wall by the room behind it
PRIVATE = ("changing", "wet zone", "WC", "Nursing", "sleep")  # not the staff room (Roman): it looks out at the forest; its toilet is an inner room
spaces = {}
for s in m["spaces"]:
    spaces.setdefault(s["level"], []).append((s, MPath(s["poly"])))


def level_of(z0):
    return min(("F1", "E1", "E2", "F2", "F3", "F4"), key=lambda L: abs(lv[L] - z0))


def space_at(L, x, y):
    for s, p in spaces.get(L, []):
        if p.contains_point((x, y)):
            return s
    return None


cols = [e["at"] for e in els if e["type"] == "column" and e["material"] == "glulam"] + \
       [e["at"] for e in els if e["id"].startswith("ST3-link-post-")]


def mullions(a, b, s0, s1, ux, uy, pane):
    """Mullion stations (metres along the wall) between s0 and s1: one at every column on the line, panes <= `pane`."""
    on = sorted({round((cx - a[0]) * ux + (cy - a[1]) * uy, 3) for cx, cy in cols
                 if abs((cx - a[0]) * uy - (cy - a[1]) * ux) < 0.05 and s0 + 0.3 < (cx - a[0]) * ux + (cy - a[1]) * uy < s1 - 0.3})
    st = [s0] + on + [s1]
    out = []
    for p, q in zip(st, st[1:]):
        n = max(1, math.ceil((q - p) / pane - 1e-6))
        out += [round(p + (q - p) * k / n, 3) for k in range(1, n)]
    return sorted(set(out + on))


TOP = {"F1": 4.34, "E1": 4.34}
for g in [e for e in els if e["type"] == "wall" and e["id"].startswith("G-") and e["id"] != "G-E1-daycare"]:
    g["phase"] = "replaced"  # by the EN- segments below (dropped at the end)
    a, b = g["from"], g["to"]; z0, z1 = g["z"]
    e2 = g["id"].startswith("G-E2-")
    if e2:  # garage / garden glass stops under the E1 floor beams; a dark band covers beam + slab edge
        z1 = min(e["z"][0] for e in els if e["type"] == "beam" and e["id"].endswith("-E1-east"))
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    lvl = "F1" if g["id"].startswith("G-link") else level_of(z0)
    nin = None  # inward normal: the side with rooms behind the glass
    for sg in (1, -1):
        nx, ny = -uy * sg, ux * sg
        hits = sum(space_at(lvl, a[0] + ux * s + nx * 0.9, a[1] + uy * s + ny * 0.9) is not None for s in np.linspace(0.5, L - 0.5, 9))
        if nin is None or hits > nin[2]:
            nin = (nx, ny, hits)
    nx, ny, _ = nin
    runs = []  # (s0, s1, kind)
    for s in np.arange(0.05, L, 0.1):
        x, y = a[0] + ux * s, a[1] + uy * s
        out = space_at(lvl, x - nx * 0.6, y - ny * 0.6)
        if out is not None and out["kind"] == "core":
            k = "core"  # the core wall closes this stretch
        else:
            sp = space_at(lvl, x + nx * 0.9, y + ny * 0.9)
            k = "clad" if sp is not None and any(w in sp["name"] for w in PRIVATE) else "glass"
        if runs and runs[-1][2] == k:
            runs[-1][1] = s + 0.05
        else:
            runs.append([max(0.0, s - 0.05), s + 0.05, k])
    runs[-1][1] = L
    for r_ in runs:  # slivers next to cores (< 0.6 m) close solid
        if r_[2] == "glass" and r_[1] - r_[0] < 0.6:
            r_[2] = "clad"
    pane = 2.3 if g["id"].startswith("G-link") else 1.3
    for k, (s0, s1, kind) in enumerate(runs):
        s0, s1 = round(s0, 2), round(s1, 2)
        if kind == "core":
            xm, ym = a[0] + ux * (s0 + s1) / 2 - nx * 0.6, a[1] + uy * (s0 + s1) / 2 - ny * 0.6
            core = space_at(lvl, xm, ym)
            if core["id"].startswith("core-W3"):  # low exit core: its sod roof tops out at 2.95, the facade continues above
                pa, pb = [round(a[0] + ux * s0, 3), round(a[1] + uy * s0, 3)], [round(a[0] + ux * s1, 3), round(a[1] + uy * s1, 3)]
                add({"id": f"EN-{g['id']}-{k}-over-W3", "type": "wall", "kind": "glazed", "material": "glass", "from": pa, "to": pb, "size": [0.12, round(z1 - 2.95, 2)],
                     "z": [2.95, z1], "mullions": [round(v - s0, 3) for v in mullions(a, b, s0, s1, ux, uy, 1.3)], "transoms": [],
                     "note": "glass band above the low W3 exit roof"})
            continue
        if s1 - s0 < 0.2:
            continue
        pa, pb = [round(a[0] + ux * s0, 3), round(a[1] + uy * s0, 3)], [round(a[0] + ux * s1, 3), round(a[1] + uy * s1, 3)]
        ops = [{**o, "s": [round(o["s"][0] - s0, 2), round(o["s"][1] - s0, 2)]} for o in g.get("openings", []) if s0 <= o["s"][0] and o["s"][1] <= s1]
        mul = [round(v - s0, 3) for v in mullions(a, b, s0, s1, ux, uy, pane)]
        base = {"level": g.get("level", lvl), "openings": ops} if ops else {}
        if kind == "glass":
            tr = [round(z0 + 3.0, 2)] if z1 - z0 > 3.6 else []
            add({"id": f"EN-{g['id']}-{k}", "type": "wall", "kind": "glazed", "material": "glass", "from": pa, "to": pb, "size": [0.12, round(z1 - z0, 2)],
                 "z": [z0, z1], "mullions": mul, "transoms": tr, **base,
                 "note": "triple-glazed, dark aluminium frames; mullions on the column rhythm" + (" (sliding panels, stack between posts)" if pane > 2 else "")})
        else:
            zc = round(z0 + 2.6, 2)
            add({"id": f"EN-{g['id']}-{k}-wall", "type": "wall", "kind": "clad", "material": "timber_clad", "from": pa, "to": pb, "size": [0.4, round(zc - z0, 2)],
                 "z": [z0, zc], **base, "note": "solid for privacy: black tarred board-on-board pine on a 0.40 m insulated timber frame"})
            add({"id": f"EN-{g['id']}-{k}-clerestory", "type": "wall", "kind": "glazed", "material": "glass_obscured", "from": pa, "to": pb, "size": [0.12, round(z1 - zc, 2)],
                 "z": [zc, z1], "mullions": mul, "transoms": [], "note": "high obscured clerestory: daylight without views in"})
    # header band from the glass head to the roof soffit (above grade only)
    if e2:
        add({"id": f"EN-band-{g['id']}", "type": "wall", "kind": "clad", "material": "timber_clad", "from": a, "to": b, "size": [0.75, round(lv["E1"] - z1, 2)],
             "z": [z1, lv["E1"]], "note": "black timber band over the E1 beam and slab edge"})
    if lvl in ("F1", "E1"):
        add({"id": f"EN-header-{g['id']}", "type": "wall", "kind": "clad", "material": "timber_clad", "from": a, "to": b, "size": [0.4, round(lv["RF"] - z1, 2)],
             "z": [z1, lv["RF"]], "note": "black timber header band between the glass head and the roof; beam tails pass through"})
els = [e for e in els if e.get("phase") != "replaced"]

# ---- stone plinth on every concrete face above the finished ground
fin = np.load(ROOT / "terrain" / "out" / "ravine" / "eroded_1m.npy")
from scipy import ndimage as ndi  # noqa: E402
g_ = np.arange(-1000, 1000) + 0.5
GX, GY = np.meshgrid(g_, g_)
in_pad = np.zeros(fin.shape, bool)  # the wings' own excavation: not "ground" for the facade
for pad in m["site"]["pads"]:
    if pad["id"] in ("west_wing", "east_wing"):
        in_pad |= MPath(pad["poly"]).contains_points(np.stack([GX.ravel(), GY.ravel()], 1)).reshape(fin.shape)
in_pad = ndi.binary_dilation(in_pad, iterations=1)
cell = lambda x, y: (int(np.clip(y + 1000, 0, 1999)), int(np.clip(x + 1000, 0, 1999)))
ground = lambda x, y: np.nan if in_pad[cell(x, y)] else float(fin[cell(x, y)])
CENTRE = {"W-west-": (-17.95, -14.0), "SA-": (-17.65, -37.1), "WA-": (-31.45, -21.8), "W-east-": (21.25, 11.9),
          "CS-W1-": (-30.45, -14.05), "CS-W2-": (-30.45, -29.6), "CS-W3-": (-12.7, 13.95), "LS-men-": (-30.05, -2.9), "LS-women-": (-30.05, 5.9),
          "FDN-garden-wall-W": (-20.0, 40.0)}  # garden wall: its exposed face is the garden (east) side
for e in els:
    pre = next((p for p in CENTRE if e["id"].startswith(p)), None)
    if pre is None or e["type"] != "wall" or e["material"] != "concrete":
        continue
    (ax, ay), (bx, by) = e["from"], e["to"]
    L = math.hypot(bx - ax, by - ay)
    if L < 0.5:
        continue
    nx, ny = -(by - ay) / L, (bx - ax) / L
    cx, cy = CENTRE[pre]
    if (cx - (ax + bx) / 2) * nx + (cy - (ay + by) / 2) * ny > 0:
        nx, ny = -nx, -ny
    t = e["size"][0] / 2
    ext = (1.0 + t) / L  # look past the wall ends too: the ground dips at corners
    zs = [ground(ax + (bx - ax) * f + nx * (t + 1.6), ay + (by - ay) * f + ny * (t + 1.6)) for f in np.linspace(-ext, 1 + ext, max(5, int(L) + 3))]
    zs = [z for z in zs if not np.isnan(z)]
    if not zs:
        continue
    zg = min(zs)
    z0, z1 = max(e["z"][0], round(zg - 0.8, 2)), e["z"][1]
    if pre in ("W-west-", "W-east-") and (abs(z1 - (lv["F1"] - 0.25)) < 0.02 or abs(z1 - (lv["E1"] - 0.25)) < 0.02):
        z1 = lv["E1"] if pre == "W-east-" else lv["F1"]  # the stone runs up over the slab edge to the floor line
    if z1 - z0 < 0.4:
        continue
    off = lambda d: ([round(ax + nx * d, 3), round(ay + ny * d, 3)], [round(bx + nx * d, 3), round(by + ny * d, 3)])
    pa, pb = off(t + 0.03 + 0.1)  # 50 mm cavity (membrane sits in it below grade) + 150 mm stone, centred
    r_ = t + 0.2  # run past both ends so the stone wraps the corners
    pa = [round(pa[0] - (bx - ax) / L * r_, 3), round(pa[1] - (by - ay) / L * r_, 3)]
    pb = [round(pb[0] + (bx - ax) / L * r_, 3), round(pb[1] + (by - ay) / L * r_, 3)]
    st = {"id": f"EN-stone-{e['id']}", "type": "wall", "kind": "stone", "material": "stone", "from": pa, "to": pb, "size": [0.15, round(z1 - z0, 2)],
          "z": [z0, z1], "note": "150 mm dry-laid granite plinth on a 50 mm cavity, tied back to the concrete"}
    if e.get("openings"):
        st["openings"] = e["openings"]
    add(st)

# ---- the sauna-lobby annex sits on a low granite plinth (no gap under its timber walls)
for e in els:
    if e["id"].startswith("A-annex-"):
        add({"id": f"EN-stone-{e['id']}", "type": "wall", "kind": "stone", "material": "stone", "from": e["from"], "to": e["to"], "size": [round(e["size"][0] + 0.1, 2), 0.7],
             "z": [-0.7, 0.0], "note": "granite plinth under the annex wall, 0.7 m into the ground"})

# ---- river glazing in the river-wall openings
rw = by_id["W-west-C"]
(ax, ay), (bx, by) = rw["from"], rw["to"]
for k, o in enumerate(rw.get("openings", [])):
    if o["type"] not in ("underwater", "river", "window"):
        continue
    L = o["s"][1] - o["s"][0]
    pane = {"underwater": L + 1, "river": 3.0, "window": 1.3}[o["type"]]
    n = max(1, math.ceil(L / pane - 1e-6))
    pa, pb = [ax, round(ay + o["s"][0], 3)], [ax, round(ay + o["s"][1], 3)]
    mat = "glass" if o["type"] == "window" else "acrylic"
    add({"id": f"EN-river-{o['type']}-{k}", "type": "wall", "kind": "glazed", "material": mat, "from": pa, "to": pb, "size": [0.2 if mat == "acrylic" else 0.12, round(o["z"][1] - o["z"][0], 2)],
         "z": o["z"], "mullions": [round(L * j / n, 3) for j in range(1, n)], "transoms": [],
         "note": {"underwater": "200 mm structural acrylic, one panel: looks into the river at the riverbed",
                  "river": "structural acrylic panels ~3 m, stainless joints: the river at waist height",
                  "window": "triple glazing, divided like the facades"}[o["type"]]})

# ---- sod roofs, roof edges, soffits
ROOFS = [e for e in els if e["type"] == "slab" and e["id"].startswith("S-RF-") and e["material"] == "clt"]
outline = lambda r: (lambda x0, y0, x1, y1, w, s, ea, n: [x0 - w, y0 - s, x1 + ea, y1 + n])(*r["rect"], *r.get("eaves", (0, 0, 0, 0)))
OUTL = {r["id"]: outline(r) for r in ROOFS}
SOD = 0.45
for r in ROOFS:
    ox0, oy0, ox1, oy1 = o = OUTL[r["id"]]
    top = r["z"][1]
    add({"id": f"EN-sod-{r['id']}", "type": "slab", "material": "sod", "rect": o, "z": [top, round(top + SOD, 2)], "holes": r.get("holes", []),
         "note": "sod roof: membrane, 250 mm PIR to falls, drainage mat, 120 mm substrate + turf"})
    # dark roof edge on every free edge (not where it meets the neighbouring roof)
    sides = {"S": ((ox0, oy0), (ox1, oy0), (0, -1)), "N": ((ox0, oy1), (ox1, oy1), (0, 1)), "W": ((ox0, oy0), (ox0, oy1), (-1, 0)), "E": ((ox1, oy0), (ox1, oy1), (1, 0))}
    for sd, ((x0, y0), (x1, y1), (dx, dy)) in sides.items():
        L = math.hypot(x1 - x0, y1 - y0); runs = []
        for s in np.arange(0.05, L, 0.1):
            px, py = x0 + (x1 - x0) * s / L + dx * 0.05, y0 + (y1 - y0) * s / L + dy * 0.05
            free = not any(q != r["id"] and OUTL[q][0] < px < OUTL[q][2] and OUTL[q][1] < py < OUTL[q][3] for q in OUTL)
            if free and runs and runs[-1][1] >= s - 0.11:
                runs[-1][1] = s + 0.05
            elif free:
                runs.append([s - 0.05, s + 0.05])
        for j, (s0, s1) in enumerate(runs):
            if s1 - s0 < 0.3:
                continue
            pa = [round(x0 + (x1 - x0) * s0 / L + dx * 0.025, 3), round(y0 + (y1 - y0) * s0 / L + dy * 0.025, 3)]
            pb = [round(x0 + (x1 - x0) * s1 / L + dx * 0.025, 3), round(y0 + (y1 - y0) * s1 / L + dy * 0.025, 3)]
            add({"id": f"EN-edge-{r['id']}-{sd}{j}", "type": "wall", "kind": "trim", "material": "steel_dark", "from": pa, "to": pb, "size": [0.05, 0],
                 "z": [round(r["z"][0] - 0.02, 2), round(top + SOD + 0.05, 2)], "note": "folded dark aluminium roof edge, 50 mm proud of the turf"})
    # oak soffit under the eaves (between the beam tails)
    x0, y0, x1, y1 = r["rect"]; W_, S_, E_, N_ = r.get("eaves", (0, 0, 0, 0))
    strips = {"S": (ox0, oy0, ox1, y0) if S_ > 0 else None, "N": (ox0, y1, ox1, oy1) if N_ > 0 else None,
              "W": (ox0, max(y0, oy0), x0, min(y1, oy1)) if W_ > 0 else None, "E": (x1, max(y0, oy0), ox1, min(y1, oy1)) if E_ > 0 else None}
    for sd, st in strips.items():
        if st:
            add({"id": f"EN-soffit-{r['id']}-{sd}", "type": "slab", "material": "oak", "rect": [round(v, 3) for v in st], "z": [round(r["z"][0] - 0.025, 3), r["z"][0]],
                 "holes": r.get("holes", []) if sd == "W" else [], "note": "weathered oak soffit boards under the eave; glulam tails stay exposed below"})

# ---- annex roofs below the main roof line are sod roofs too (south rock annex, WC annex)
for rid in ("S-SA-roof", "S-WA-roof"):
    r = by_id[rid]
    add({"id": f"EN-sod-{rid}", "type": "slab", "material": "sod", "rect": r["rect"], "z": [r["z"][1], round(r["z"][1] + SOD, 2)], "holes": [],
         "note": "sod roof over the rock annex: membrane, insulation, drainage, substrate + turf, flush with the meadow"})
    x0, y0, x1, y1 = r["rect"]; zt = round(r["z"][1] + SOD + 0.05, 2)
    for sd, (pa, pb) in {"S": ([x0, y0 - 0.025], [x1, y0 - 0.025]), "N": ([x0, y1 + 0.025], [x1, y1 + 0.025]),
                         "W": ([x0 - 0.025, y0], [x0 - 0.025, y1]), "E": ([x1 + 0.025, y0], [x1 + 0.025, y1])}.items():
        add({"id": f"EN-edge-{rid}-{sd}", "type": "wall", "kind": "trim", "material": "steel_dark", "from": pa, "to": pb, "size": [0.05, 0],
             "z": [r["z"][0], zt], "note": "folded dark aluminium roof edge"})

# ---- dark steel edge on the lounge deck slab: reads as a thin dark plate over the water
dk = by_id["S-F1-link"]; x0, y0, x1, y1 = dk["rect"]
for sid, (pa, pb) in {"S": ([x0, y0 - 0.03], [x1, y0 - 0.03]), "N": ([x0, y1 + 0.03], [x1, y1 + 0.03]), "SE": ([x1 + 0.03, y0], [x1 + 0.03, -9.5])}.items():
    add({"id": f"EN-deckedge-{sid}", "type": "wall", "kind": "trim", "material": "steel_dark", "from": pa, "to": pb, "size": [0.06, 0],
         "z": [round(dk["z"][0] - 0.05, 2), round(dk["z"][1] + 0.05, 2)], "note": "dark steel edge plate over the deck slab edge"})

# ---- glass balustrades on the lounge decks
for sid, (pa, pb) in {"S": ([-6.45, -12.45], [12.0, -12.45]), "N": ([-6.45, 11.25], [12.0, 11.25]), "SE": ([11.95, -12.5], [11.95, -9.5])}.items():
    add({"id": f"EN-balustrade-{sid}", "type": "wall", "kind": "glazed", "material": "glass", "from": pa, "to": pb, "size": [0.03, 1.1], "z": [0.0, 1.1],
         "mullions": [], "transoms": [], "note": "1.1 m laminated glass balustrade, oak handrail"})

m["elements"] = els + new
modelio.save(m)

# ---- backfill: the finished ground for the construction scenes. Enclosed volumes (wings, cores, shafts, annexes, parking)
# must not have ground running through them: inside each footprint the grid is refilled from the nearest outside ground
# (no 1 m V-gap against the walls), and the scene cuts the volumes out exactly. Ground above a buried roof stays.
import json  # noqa: E402
sl = {e["id"]: e for e in m["elements"]}
cores = {s_["id"].rsplit("-", 1)[0]: s_["poly"] for s_ in m["spaces"] if s_["kind"] == "core" and s_["level"] in ("F1", "E1")}
VOIDS = [[[-29.45, -34.1, -6.45, 12.1], -17.0, 6.0], [[12.0, -9.5, 30.5, 33.3], -7.0, 6.0]]  # wings (rect at wall centre lines, bottom, top)
for cid, poly in cores.items():
    xs, ys = [p_[0] for p_ in poly], [p_[1] for p_ in poly]
    top = max((e["z"][1] for e in m["elements"] if e["type"] == "wall" and e.get("kind") == "shaft"
               and min(xs) - 0.2 <= e["from"][0] <= max(xs) + 0.2 and min(ys) - 0.2 <= e["from"][1] <= max(ys) + 0.2), default=6.0)
    VOIDS.append([[min(xs), min(ys), max(xs), max(ys)], -17.5, top])
for rid, zb, zt in (("S-WA-roof", -17.0, None), ("S-SA-roof", -17.0, None), ("S-P-roof", -7.0, None), ("S-F1-annex", None, 3.2)):
    r = sl[rid]
    VOIDS.append([r["rect"], r["z"][0] if zb is None else zb, r["z"][0] if zt is None else zt])
H = fin.copy()
for (x0_, y0_, x1_, y1_), zb, zt in VOIDS:
    inside = (GX > x0_) & (GX < x1_) & (GY > y0_) & (GY < y1_) & (H < zt)
    if inside.any():
        _, (iy, ix) = ndi.distance_transform_edt(inside, return_indices=True)
        H = np.where(inside, H[iy, ix], H)
OUTD = ROOT / "construction" / "out"; OUTD.mkdir(parents=True, exist_ok=True)
np.save(OUTD / "finished_1m.npy", H.astype(np.float32))
(OUTD / "voids.json").write_text(json.dumps(VOIDS))
print("backfill:", len(VOIDS), "enclosed volumes cut out of the finished ground")
from collections import Counter
p4 = [e for e in m["elements"] if e.get("phase") == 4]
print("phase-4 elements:", len(p4), dict(Counter(e.get("kind") or e["type"] for e in p4)))

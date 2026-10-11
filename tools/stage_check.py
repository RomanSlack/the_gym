"""Construction coverage check: everything designed must be built by some stage, and nothing a built stage owns may be missing.

Written after an oversight: the sunken daycare garden was designed in the site model, but no construction stage dug it,
so the daycare's walk-out glass faced untouched ground in the stage 1 and 3 renders (caught by Roman, not by us).
Runs last in tools/build_model.py and prints a report; it never blocks the build.

Sweeps:
  1. terrain: every cell where the designed site differs from the natural ground (cut or fill) belongs to a site-work kind;
     each kind must be owned by a stage, and once that stage is built, the construction terrain must have done the cut.
  2. site features: every entry in site.features (and every surface / path / stepping-stone line) must be owned by a stage,
     and an owner stage that is already built must show evidence (elements or earthworks).
  3. elements: every element has a phase or a planned later stage; every stair and core stair is built once stage 3 is.
  4. once the ground is back (stage 4+): nothing meant to be buried (footings, membranes, drainage, pipes) shows above the
     finished ground, and no wall or footing hangs above the ground beside it unless something below covers it (toe, plinth).
     Added after Roman spotted membranes, footings and gaps showing at the garden corners and tower bases.
When you add something to the design, give it an owner here; when a stage is built, its evidence has to exist.
python3 tools/stage_check.py
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
els = m["elements"]
ids = {e["id"] for e in els}
BUILT = max(e.get("phase", 0) for e in els)  # highest construction stage built so far
issues, notes = [], []

# ---- 1. terrain: site works (terrain/ravine.py MASK kinds) and the stage that does the earthworks
KIND = {"asphalt": 1, "shoulder": 2, "court": 4, "ramp": 8, "garden": 16, "path": 32, "sauna": 64, "tunnel": 128, "trail": 256,
        "planting": 512, "stone": 1024, "gravel": 2048, "lawn": 4096, "deck": 8192}
EARTHWORKS_STAGE = {"asphalt": 1, "shoulder": 1, "court": 1, "ramp": 1, "garden": 1, "sauna": 1, "tunnel": 1, "gravel": 1,
                    "path": 6, "trail": 6, "planting": 6, "stone": 6, "lawn": 6, "deck": 6, "pad": 1}
RV, OUT = ROOT / "terrain" / "out" / "ravine", ROOT / "construction" / "out"
nat, des, fm = np.load(RV / "natural_1m.npy"), np.load(RV / "terrain_1m.npy"), np.load(RV / "features_1m.npy").astype(int)
stage_t = nat.copy()
if BUILT >= 1:
    stage_t = np.minimum(nat + np.load(OUT / "earthworks_1m.npy"), np.load(OUT / "pit_1m.npy"))
g = np.arange(-1000, 1000) + 0.5
X, Y = np.meshgrid(g, g)
pad = np.zeros(X.shape, bool)
for p in m["site"]["pads"]:
    pad |= MPath(p["poly"]).contains_points(np.stack([X.ravel(), Y.ravel()], 1)).reshape(X.shape)
changed = np.abs(des - nat) > 0.3
_, (iy, ix) = ndi.distance_transform_edt(fm == 0, return_indices=True)
owner_bits = np.where(fm > 0, fm, np.where(ndi.distance_transform_edt(fm == 0) <= 25, fm[iy, ix], 0))  # side slopes -> nearest work
unowned = changed & (owner_bits == 0) & ~pad
if unowned.sum() > 20:
    issues.append(f"terrain: {int(unowned.sum())} m2 of site works with no feature tag (bbox x {X[unowned].min():.0f}..{X[unowned].max():.0f}, "
                  f"y {Y[unowned].min():.0f}..{Y[unowned].max():.0f}): tag it in terrain/ravine.py and give it a stage here")
undug = changed & (des < stage_t - 0.3)  # designed lower than what the built stages have dug
for k, b in list(KIND.items()) + [("pad", None)]:
    cells = pad if b is None else (owner_bits & b) > 0
    work = changed & cells
    if not work.any():
        continue
    st = EARTHWORKS_STAGE.get(k)
    if st is None:
        issues.append(f"terrain: site-work kind '{k}' ({int(work.sum())} m2) has no construction stage")
    elif st <= BUILT and (undug & cells).sum() > 20:
        u = undug & cells
        issues.append(f"terrain: '{k}' belongs to stage {st} (built) but {int(u.sum())} m2 / {float((stage_t - des)[u].sum()):.0f} m3 is not dug "
                      f"(bbox x {X[u].min():.0f}..{X[u].max():.0f}, y {Y[u].min():.0f}..{Y[u].max():.0f})")

# ---- 2. site features: owner stages + evidence once a stage is built ("terrain" = covered by sweep 1, else an element id prefix)
FEATURES = {
    "road": {1: "terrain", 6: None}, "garage_ramp": {1: "FDN-ramp-"}, "daycare_garden": {1: "FDN-garden-wall-", 4: "EN-stone-FDN-garden-wall-", 6: None},
    "sauna": {6: None}, "sauna_path": {6: None}, "trail": {6: None}, "bike_shelter": {6: None}, "trailhead_sign": {6: None},
    "outdoor_rig": {6: None},
}
LIST_STAGE = {"asphalt": {1: "terrain", 6: None}, "gravel": {1: "terrain", 6: None}, "lawn": {6: None}, "planting": {6: None}, "deck": {6: None}}
for name, v in m["site"]["features"].items():
    if not isinstance(v, (dict, list)):
        continue
    entries = [(name, FEATURES.get(name))] if isinstance(v, dict) else \
        [(f"{name}:{it['id']}", LIST_STAGE.get(it.get("kind"), {6: None}) if name == "surfaces" else {6: None}) for it in v]
    for label, own in entries:
        if own is None:
            issues.append(f"feature '{label}' has no construction stage: add it to FEATURES in tools/stage_check.py and to CONSTRUCTION_PLAN.md")
            continue
        for st, ev in own.items():
            if st <= BUILT and ev not in (None, "terrain") and not any(i.startswith(ev) for i in ids):
                issues.append(f"feature '{label}': stage {st} is built but nothing matches '{ev}*'")

# ---- 3. elements, stairs, cores
LATER = [(lambda e: e.get("material") == "glass" or e.get("kind") == "glazed", 4), (lambda e: e.get("material") == "sod", 4),
         (lambda e: e.get("kind") == "partition" or e.get("material") == "timber_stud", 5)]
for e in els:
    if e.get("phase") is None and not any(f(e) for f, _ in LATER):
        issues.append(f"element {e['id']} ({e['type']} {e.get('material')}) has no phase and no planned stage")
later = {}
for e in els:
    if e.get("phase") is None:
        st = next(s for f, s in LATER if f(e)); later[st] = later.get(st, 0) + 1
notes.append("waiting for later stages: " + ", ".join(f"stage {s}: {n} elements" for s, n in sorted(later.items())))
if BUILT >= 3:
    for st in m["stairs"]:
        ev = f"ST3-{st['id']}" if st["kind"] == "spiral" else "ST3-stair-N34" if st["id"] == "north_f3_f4" else None
        if ev is None or ev not in ids and not any(i.startswith(ev) for i in ids):
            issues.append(f"stair {st['id']} is not built in stage 3")
    for c in {s["id"].split("-")[1] for s in m["spaces"] if s["kind"] == "core" and "stair" in s["name"]}:
        if not any(i.startswith(f"ST3-stair-{c}-") for i in ids):
            issues.append(f"core {c} has a stair in the plan but no stair flights")
notes.append(f"fixtures (stage 5): {len(m.get('fixtures', []))}")

# ---- 4. buried things stay buried, nothing floats (only once the site is backfilled)
if BUILT >= 4:
    import math
    fin = np.load(RV / "eroded_1m.npy")
    bpad = np.zeros(fin.shape, bool)
    for p in m["site"]["pads"]:
        if p["id"] in ("west_wing", "east_wing"):
            bpad |= MPath(p["poly"]).contains_points(np.stack([X.ravel(), Y.ravel()], 1)).reshape(fin.shape)
    bpad = ndi.binary_dilation(bpad, iterations=1)  # the building's own footprint (+ its 1 m grid edge) is not "ground"

    def gnd(x, y):
        i, j = int(np.clip(y + 1000, 0, 1999)), int(np.clip(x + 1000, 0, 1999))
        return None if bpad[i, j] else float(fin[i, j])

    def along(e, n=None):
        (ax, ay), (bx, by) = e["from"], e["to"]; L = max(math.hypot(bx - ax, by - ay), 0.01)
        return [(ax + (bx - ax) * f, ay + (by - ay) * f) for f in np.linspace(0, 1, n or max(2, int(L) + 1))], L, (ax, ay, bx, by)

    BURIED = ("strip_footing", "membrane", "drain_layer", "drain_pipe", "pad_footing")
    for e in els:
        if e["type"] not in BURIED:
            continue
        pts = along(e)[0] if "from" in e else [tuple(e["at"])]
        bad = [(x, y, g) for x, y in pts if (g := gnd(x, y)) is not None and e["z"][1] > g + 0.05]
        if bad:
            x, y, g = max(bad, key=lambda b: e["z"][1] - b[2])
            issues.append(f"buried {e['type']} {e['id']} shows {e['z'][1] - g:.2f} m above the finished ground at ({x:.0f}, {y:.0f})")
    lowers = [e for e in els if e["type"] in ("wall", "strip_footing") and "from" in e]
    for e in els:
        if e["type"] not in ("wall", "strip_footing") or "from" not in e or e.get("phase") is None or e.get("kind") in ("partition", "glazed", "trim", "clad"):
            continue
        pts, L, (ax, ay, bx, by) = along(e)
        nx, ny = -(by - ay) / L, (bx - ax) / L; t = e["size"][0] / 2
        for x, y in pts[1:-1] or pts:
            gs = [g for sg in (1, -1) for d in (0.6, 1.4, 2.0) if (g := gnd(x + nx * sg * (t + d), y + ny * sg * (t + d))) is not None]
            if not gs or min(gs) >= e["z"][0] - 0.1:
                continue
            # covered if another wall / footing on (nearly) the same line reaches lower here
            cov = any(o is not e and o["z"][0] <= min(gs) + 0.1 and abs((x - o["from"][0]) * (o["to"][1] - o["from"][1]) - (y - o["from"][1]) * (o["to"][0] - o["from"][0]))
                      / max(math.hypot(o["to"][0] - o["from"][0], o["to"][1] - o["from"][1]), 0.01) < 0.6 for o in lowers)
            if not cov:
                issues.append(f"{e['type']} {e['id']} hangs {e['z'][0] - min(gs):.2f} m above the ground beside it at ({x:.0f}, {y:.0f})")
                break

print(f"stage check (built up to stage {BUILT}): " + ("OK" if not issues else f"{len(issues)} issue(s)"))
for i in issues:
    print("  !", i)
for n in notes:
    print("  ·", n)

"""Construction stage 3: structure (the frame that stands on the foundations).

Tags the existing frame as phase 3 and adds what the frame still lacked. Rules of thumb (no engineering calcs), noted on each element:
  - existing frame joins phase 3: suspended slabs, post-tensioned + glulam beams, pilasters, glulam facade columns,
    parking columns + buried roof, annex CLT walls; build order (seq) runs bottom-up by elevation
  - roofs: CLT 300 (7-layer, spans 7.7 / 8.56 m between glulam beams under sod) with 2.5 m eaves on every free edge.
    `eaves` = overhang per side [W, S, E, N]; negative = the plate stops short because the neighbouring roof's eave covers it.
    The glulam roof beams run on past the facades as tapered tails (1.3 / 1.0 m -> 0.3 m at the tip) that carry the long-side eaves;
    on the short ends the CLT cantilevers 2.5 m off the end beam (back-span 7.7 m). Towers and lift shafts punch through.
  - lounge bridge: no trusses (the sliding glass walls open fully, so nothing diagonal in the walls).
    Floor = four dark steel box girders 0.45 x 1.0 m wing to wing under a 0.3 m deck; tapered steel outriggers carry the decks
    (3 m south, 4.5 m north). Roof = five glulam beams spanning across the lounge on slim steel posts in the glass lines,
    with the same tapered tails over the decks: the lounge reads as a small wing turned 90 degrees.
  - cores: every wall between a core / lift and a room becomes 250 mm concrete (fire-rated shafts that also brace the floors);
    core E gets its concrete shaft too. Core stairs: precast concrete doglegs (2 x 1.0 m flights, 0.175 rise, 0.28 going).
  - spiral F1 -> F3: open helix, no centre post: inner + outer dark steel helical stringers, solid oak treads.
  - F3 -> F4 north stair: built as a dogleg in its 6 x 5 m opening (two 2.7 m flights).
python3 tools/structure_stage.py   (run by tools/build_model.py, after foundations)
"""
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
lv = {l["id"]: l["elevation"] for l in m["levels"]}
els = [e for e in m["elements"] if not e["id"].startswith("ST3-")]
by_id = {e["id"]: e for e in els}
new = []
EAVE, CLT = 2.5, 0.3
seq_of = lambda z0: int(round((z0 + 20) * 10))  # bottom-up build order


def add(e):
    e["phase"] = 3
    e.setdefault("seq", seq_of(e["z"][0]))
    new.append(e)


# ---- suspended slabs sit 100 mm under the finished floor level (finish build-up: impact mat, screed + underfloor heating,
# floor finish; the PT beam tops already sit at level - 0.10). Ground rafts (F4, E2) keep their levels for now.
SUSP = {"S-F1-west": "F1", "S-F2-west": "F2", "S-F3-west": "F3", "S-E1-east": "E1", "S-F1-link": "F1", "S-F1-annex": "F1", "S-SA-F2": "F2", "S-SA-F3": "F3"}
for e in els:
    if e["id"] in SUSP:
        t = round(e["z"][1] - e["z"][0], 2)
        e["z"] = [round(lv[SUSP[e["id"]]] - 0.10 - t, 2), round(lv[SUSP[e["id"]]] - 0.10, 2)]

# ---- existing frame joins phase 3
for e in els:
    if e.get("phase") is not None:
        continue
    if e["type"] in ("column", "beam") or (e["type"] == "slab" and e["material"] in ("concrete", "clt")) \
            or (e["type"] == "wall" and e["id"].startswith("A-annex-")):
        e["phase"], e["seq"] = 3, seq_of(e["z"][0])

# ---- cores: walls between a core / lift and a room become concrete shaft walls
for e in els:
    if e["type"] == "wall" and e.get("kind") == "partition" and any(b.startswith(("core-", "lift-")) for b in e.get("between", [])):
        e.update(material="concrete", kind="core", size=[0.25, e["size"][1]], phase=3, seq=seq_of(e["z"][0]),
                 note="250 mm concrete core wall: fire-rated shaft, braces the floors")

# core walls are drawn centre line to centre line: where two meet, the outer corner square was missing. Run each core wall
# on by half its thickness at every end that meets another core wall, so corners close (inside and out).
import math as _m
cores_ = [e for e in els if e["type"] == "wall" and e.get("kind") in ("core", "shaft")]
for e in cores_:
    (ax, ay), (bx, by) = e["from"], e["to"]; L_ = _m.hypot(bx - ax, by - ay)
    if L_ < 0.1 or e.get("_ext"):
        continue
    ux, uy = (bx - ax) / L_, (by - ay) / L_; t2 = e["size"][0] / 2
    meets = lambda p: any(o is not e and min(_m.dist(p, o["from"]), _m.dist(p, o["to"])) < 0.06 for o in cores_)
    if meets((ax, ay)):
        e["from"] = [round(ax - ux * t2, 3), round(ay - uy * t2, 3)]
    if meets((bx, by)):
        e["to"] = [round(bx + ux * t2, 3), round(by + uy * t2, 3)]
    e["_ext"] = True
    if e.get("openings") and meets((ax, ay)):  # openings are measured from 'from': keep them where they were
        for o in e["openings"]:
            o["s"] = [round(o["s"][0] + t2, 3), round(o["s"][1] + t2, 3)]

# ---- roofs: CLT 300 with 2.5 m eaves
LINK = [-6.45, -9.5, 12.0, 6.8]  # lounge glass lines
TOWERS = [[-32.05, -18.55, -28.85, -9.55], [-32.05, -34.1, -28.85, -25.1], [-31.25, -4.1, -28.85, -1.7], [-31.25, 4.7, -28.85, 7.1]]
EAVES = {"S-RF-west": [EAVE, EAVE, EAVE, EAVE], "S-RF-east": [EAVE, EAVE, EAVE, EAVE], "S-RF-link": [-EAVE, EAVE, -EAVE, EAVE]}
for rid, ev in EAVES.items():
    r = by_id[rid]
    top = lv["RF"] + CLT
    r.update(z=[lv["RF"], round(top, 2)], eaves=ev,
             note=f"CLT {int(CLT * 1000)} roof (7-layer) on glulam beams; eaves {ev} m [W,S,E,N] (negative = meets the neighbouring eave)")
    if rid == "S-RF-link":
        r["rect"] = list(LINK)
    if rid == "S-RF-west":
        r["holes"] = [{"rect": [[a, b], [c, b], [c, d], [a, d]]} for a, b, c, d in TOWERS]

by_id["S-RF-annex"].update(eaves=[0.6, 0.6, 0.0, 0.6], note="CLT roof of the sauna lobby annex, 0.6 m drip edge (it sits under the main eave)")

# glulam roof beam tails: 2.5 m past the facade, tapered to 0.3 m; none into the lounge, the towers or under the lounge roof
link_y = (LINK[1] - EAVE, LINK[3] + EAVE)
inside = lambda x, y, r, tol=0.0: r[0] + tol < x < r[2] - tol and r[1] + tol < y < r[3] - tol
for e in els:
    if e["type"] != "beam" or "-RF-" not in e["id"]:
        continue
    (x0, y), (x1, _) = e["from"], e["to"]
    hw = e["size"][0] / 2
    cant = []
    for xe, sgn in ((x0, -1), (x1, 1)):
        tip_x = xe + sgn * EAVE
        faces_link = (sgn == 1 and abs(xe - LINK[0]) < 0.01) or (sgn == -1 and abs(xe - LINK[2]) < 0.01)
        hits_tower = any(min(xe, tip_x) < t[2] and max(xe, tip_x) > t[0] and y - hw < t[3] - 0.05 and y + hw > t[1] + 0.05 for t in TOWERS)
        cant.append(0.0 if (faces_link and link_y[0] <= y <= link_y[1]) or hits_tower else EAVE)
    e["cantilever"], e["tip_depth"] = cant, 0.3
    e["note"] = "glulam GL30c; tails run 2.5 m past the facade, tapered to 0.3 m, carrying the eaves" if any(cant) else "glulam GL30c"

# ---- lounge bridge
DECK_Z = by_id["S-F1-link"]["z"]
for k, y in enumerate(np.linspace(LINK[1], LINK[3], 4)):
    add({"id": f"ST3-link-girder-{k}", "type": "beam", "material": "steel_dark", "from": [LINK[0], round(float(y), 2)], "to": [LINK[2], round(float(y), 2)],
         "size": [0.45, 1.0], "z": [round(DECK_Z[0] - 1.0, 2), DECK_Z[0]],
         "note": "steel box girder 0.45 x 1.0, 18.5 m wing to wing; west end in a pocket in the river wall, east end on the ledge"})
add({"id": "ST3-link-ledge-E", "type": "beam", "material": "concrete", "from": [12.0, -9.5], "to": [12.0, 7.62], "size": [0.5, 0.6],
     "z": [round(DECK_Z[0] - 1.6, 2), round(DECK_Z[0] - 1.0, 2)], "note": "concrete bearing ledge between columns D13-D11 for the lounge girders"})
for k, x in enumerate(np.linspace(LINK[0] + 0.45, LINK[2] - 0.45, 7)):
    x = round(float(x), 2)
    for side, (ya, yb) in {"S": (LINK[1], -12.5), "N": (LINK[3], 11.3)}.items():
        add({"id": f"ST3-link-outrigger-{side}{k}", "type": "beam", "material": "steel_dark", "from": [x, ya], "to": [x, yb], "size": [0.3, 1.0],
             "tip_depth": 0.3, "z": [round(DECK_Z[0] - 1.0, 2), DECK_Z[0]], "note": f"tapered steel outrigger: the {side} deck cantilevers off the edge girder"})
LR_X = np.linspace(LINK[0] + 0.3, LINK[2] - 0.3, 5)
for k, x in enumerate(LR_X):
    x = round(float(x), 2)
    add({"id": f"ST3-link-roofbeam-{k}", "type": "beam", "material": "glulam", "from": [x, LINK[1]], "to": [x, LINK[3]], "size": [0.25, 1.0],
         "cantilever": [EAVE, EAVE], "tip_depth": 0.3, "z": [round(lv["RF"] - 1.0, 2), lv["RF"]],
         "note": "glulam 0.25 x 1.0 across the lounge (16.3 m) with 2.5 m tapered tails over the decks"})
    for y in (LINK[1], LINK[3]):
        add({"id": f"ST3-link-post-{k}{'S' if y < 0 else 'N'}", "type": "column", "material": "steel_dark", "at": [x, y], "size": [0.15, 0.15],
             "z": [DECK_Z[1], round(lv["RF"] - 1.0, 2)], "note": "slim steel post in the glass line; the sliding panels stack between posts"})

# ---- core E: concrete shaft from the E2 raft to the roof
for n_, (a_, b_) in {"W": ([20.8, 6.8], [20.8, 16.2]), "E": ([24.0, 6.8], [24.0, 16.2]), "S": ([20.8, 6.8], [24.0, 6.8]), "N": ([20.8, 16.2], [24.0, 16.2])}.items():
    if any(e["type"] == "wall" and e.get("kind") == "core" and sorted([tuple(e["from"]), tuple(e["to"])]) == sorted([tuple(a_), tuple(b_)]) for e in els):
        continue
    add({"id": f"ST3-core-E-{n_}", "type": "wall", "kind": "core", "material": "concrete", "from": a_, "to": b_, "size": [0.25, 0], "z": [lv["E2"], lv["RF"]],
         "note": "250 mm concrete core wall"})

# ---- core W3 at F1: lies outside the north facade, so its south side needs its own wall (the gallery door goes in it)
add({"id": "ST3-core-W3-S-F1", "type": "wall", "kind": "core", "material": "concrete", "from": [-17.2, 12.35], "to": [-8.2, 12.35], "size": [0.25, 0],
     "z": [lv["F1"], 2.6], "openings": [{"s": [7.1, 8.3], "z": [lv["F1"], 2.3], "type": "door", "swing": -1, "note": "discreet flush door: gallery -> core W3"}],
     "note": "250 mm concrete: the W3 core's south wall at F1 (below F1 it is wall W-west-N)"})

# ---- stairs
RISE, GOING, WAIST = 0.175, 0.28, 0.2


def dogleg(cid, lanes, axis, start, far, levels, landing=1.0, going=GOING, waist=WAIST, slab=WAIST):
    """Two flights per storey: up along lane 0 from `start` towards `far`, mid landing, back along lane 1; floor landings at `start`."""
    sgn = 1 if far > start else -1
    pt = lambda lane_c, s: [round(s, 2), round(lane_c, 2)] if axis == "x" else [round(lane_c, 2), round(s, 2)]
    for lo, hi in zip(levels, levels[1:]):
        zlo, zhi = lv[lo], lv[hi]; half = (zhi - zlo) / 2; n = max(2, round(half / RISE))
        g = min(going, (abs(far - start) - 2 * landing) / (n - 1))
        s0 = start + sgn * landing; s1 = s0 + sgn * g * (n - 1)
        for j, (lane, (sa, sb), (za, zb)) in enumerate(((lanes[0], (s0, s1), (zlo, zlo + half)), (lanes[1], (s1, s0), (zlo + half, zhi)))):
            add({"id": f"ST3-stair-{cid}-{lo}-{j}", "type": "stair_flight", "material": "precast", "from": pt(lane[0], sa), "to": pt(lane[0], sb),
                 "size": [lane[1], waist], "z": [round(za, 3), round(zb, 3)], "risers": n,
                 "note": f"precast flight, {n} risers {half / n:.3f}, going {g:.3f}"})
        lane_lo, lane_hi = min(l[0] - l[1] / 2 for l in lanes), max(l[0] + l[1] / 2 for l in lanes)
        mid = sorted([s1, s1 + sgn * landing])
        r = [mid[0], lane_lo, mid[1], lane_hi] if axis == "x" else [lane_lo, mid[0], lane_hi, mid[1]]
        add({"id": f"ST3-landing-{cid}-{lo}", "type": "slab", "material": "precast", "rect": [round(v, 2) for v in r],
             "z": [round(zlo + half - slab, 3), round(zlo + half, 3)], "holes": [], "note": f"half landing, {int(slab * 1000)} mm"})
    for L in levels:
        fl = sorted([start, start + sgn * landing])
        lane_lo, lane_hi = min(l[0] - l[1] / 2 for l in lanes), max(l[0] + l[1] / 2 for l in lanes)
        r = [fl[0], lane_lo, fl[1], lane_hi] if axis == "x" else [lane_lo, fl[0], lane_hi, fl[1]]
        add({"id": f"ST3-landing-{cid}-{L}-floor", "type": "slab", "material": "precast", "rect": [round(v, 2) for v in r],
             "z": [round(lv[L] - slab, 3), lv[L]], "holes": [], "note": "floor landing"})


W_LANES = [(-31.38, 1.0), (-30.22, 1.0)]  # 2.2 m clear between the core wall and wall A
dogleg("W1", W_LANES, "y", -12.2, -18.4, ["F4", "F3", "F2", "F1"], landing=1.3)  # lift in the north 2.25 m, opening onto the floor landing
dogleg("W2", W_LANES, "y", -25.25, -33.95, ["F4", "F3", "F2", "F1"], landing=1.4)
dogleg("W3", [(13.1, 1.2), (14.65, 1.2)], "x", -8.35, -17.05, ["F4", "F3", "F2", "F1"], landing=1.4)  # 3.05 m clear north of wall N
dogleg("E", [(21.6, 1.2), (23.2, 1.2)], "y", 6.95, 13.45, ["E2", "E1"], landing=1.2)  # lift in the north 2.5 m
dogleg("N34", [(-19.95, 2.7), (-16.95, 2.7)], "y", 7.1, 12.1, ["F4", "F3"], landing=1.2, going=0.25, waist=0.3, slab=0.35)  # open feature stair: heavier
for e in new:  # its half landing runs into the north wall, which carries it
    if e["id"] == "ST3-landing-N34-F4":
        e["rect"][3] = 12.35; e["material"] = "concrete"; e["note"] = "350 mm in-situ half landing, built into the north wall (W-west-N carries it)"

# core doors moved onto the floor landings (a door can't open onto a flight); lift doors added where missing
def door(wid, s, z_list, note, match=None):
    w = by_id[wid]; ops = [o for o in w.get("openings", []) if not (match and match in o.get("note", ""))]
    w["openings"] = ops + [{"s": s, "z": [z, round(z + 2.3, 2)], "type": "door", "note": note} for z in z_list]


below = [lv["F4"], lv["F3"], lv["F2"]]
door("W-west-A", [20.6, 21.8], below, "core W1 door (floor landing)", "core W1")
door("W-west-A", [22.75, 23.85], below, "core W1 lift")
door("W-west-A", [7.55, 8.75], below, "core W2 door (floor landing)", "core W2")
door("W-west-N", [19.8, 21.0], below, "core W3 (north exit stair, floor landing)", "core W3")
door("CS-W2-W", [7.55, 8.75], [lv["F1"]], "exit to outside", "exit")
door("CS-W3-N", [7.55, 8.75], [lv["F1"]], "exit to outside (north, by the sauna path)", "exit")
door("P-F1-30", [5.05, 6.25], [lv["F1"]], "core W1 door (floor landing)")
door("P-F1-30", [7.2, 8.3], [lv["F1"]], "core W1 lift")
door("P-F1-31", [7.55, 8.75], [lv["F1"]], "core W2 door (floor landing)")
for wid, z in (("P-E1-2", lv["E1"]), ("P-E2-19", lv["E2"])):
    door(wid, [0.25, 1.25], [z], "core E stair (floor landing)", "Core E")
    door(wid, [7.9, 9.1], [z], "core E lift")

for st in m["stairs"]:
    if st["kind"] != "spiral":
        continue
    zlo, zhi = lv[st["from"]], lv[st["to"]]; n = round((zhi - zlo) / RISE)
    R = st["diameter"] / 2
    add({"id": f"ST3-{st['id']}", "type": "spiral_stair", "material": "steel_dark", "center": st["center"], "r": [round(R * 0.36, 2), R],
         "z": [zlo, zhi], "risers": n, "step_deg": 15, "a0": 90,
         "note": f"open helix, no centre post: inner + outer dark steel helical stringers, {n} solid oak treads ({(zhi - zlo) / n:.3f} rise, 15 deg each)"})

m["elements"] = els + new
modelio.save(m)
from collections import Counter
p3 = [e for e in m["elements"] if e.get("phase") == 3]
print("phase-3 elements:", len(p3), dict(Counter(e["type"] for e in p3)))

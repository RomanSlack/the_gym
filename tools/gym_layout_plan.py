"""The first proposal for the gym floors' equipment (tools/gym_layout.py builds the files from these).

The reasoning (Roman 2026-10-26: islands, tight-knit but not a maze, not too expansive, the buff from the people near you):
- Every floor keeps its original zones where the real equipment fits them; where it doesn't, the equipment wins (noted below).
- Islands: kit that shares something is grouped round it, facing out: bench stations round their plate trees and bar holder,
  benches round a dumbbell rack, plate-loaded machines back to back with the plate trees between their horns, the PWR Play
  maze. Between the islands, aisles ~1.2-2 m: you train a step from someone else, never in a corridor of machines.
- The edges: the mirror wall (west) gets the lifts that want a mirror (racks, platforms, dumbbells); the river (east) gets
  the seats you stay in (cardio, selectorized machines facing the ravine / the water).
- Doors, the lift, the WCs, the spiral's step-off and the water / safety points keep a clear landing.

F2 (strength): free weights + olympic on the mirror wall, the legs, cardio on the river band. The upper-body maze + machines
moved down to the den (F3): with everything on F2 the floor came out ~100 % full with use space (no aisles left), the den had
~250 m² to spare, and upper body + dumbbells + the maze read as one floor ("the den").
"""

XW, XE, YS, YN = -29.2, -6.65, -33.85, 11.85      # the gym floors' wall faces (F2 / F3: wall A, the river wall, S, N)


def plan_f2(G):
    F = G.Floor("F2", "F2 · strength: free weights, olympic, legs, cardio, the pods", [-30.5, -41.0, -5.4, 13.2])
    ws = G.walls("F2")
    ids = ["free-weights", "olympic", "cardio-F2", "machines-2", "machines", "spiral-F2", "posing", "pod-1", "pod-2", "pod-3"]
    F.room_ids, F.walls = ids, ws
    sps = G.spaces("F2", ids)
    room = G.room_poly("F2", ids)
    fixed = G.spiral_items("F2") + G.landings(ws, "F2", room) + [i for i in G.fixtures("F2") if i["kind"] != "wipe_station"]

    # --- the mirror wall: the walkway to the stairs, the WCs and the glass lift, then the rack row facing the mirror
    F.zone("Walkway: the W2 + W1 stairs, the WCs, the AED, the glass lift (keep it clear)", XW, -27.2, -27.0, -9.2)
    F.zone("South walk: the posing room + the three pods", -27.6, YS, -7.0, -32.05)
    plat = "titan-series-power-rack-lifting-platform"
    for k in range(6):
        y = -30.43 + 3.14 * k
        p_ = F.put(plat, -24.215, y, 90, "free weights", "rack platform: the lifter faces the mirror")
        r_ = F.put("rep-pr-5000-rack-builder", -23.59, y, 90, "free weights", "on its platform; spotter arms, landmine, dip, band pegs on some", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.3, y, 90, "free weights", "lives in the rack", on=r_["id"])
    for k, y in enumerate((-11.82, -9.36)):
        p_ = F.put("hammer-strength-rubber-platform", -24.685, y, 90, "free weights", "half rack platform")
        r_ = F.put("rogue-monster-half-rack", -24.56, y, 90, "free weights", "on its platform", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.9, y, 90, "free weights", "lives in the rack", on=r_["id"])
    dl = F.put("rogue-deadlift-platform", -24.91, -6.4, 90, "free weights", "deadlifts; the crash cushions on it")
    F.put("rogue-belt-and-band-hanger", XW + 0.155, -7.2, -90, "free weights", "belts, straps, sleeves, wraps on loan; the bands")
    F.put("rogue-freestanding-chalk-stand", -22.4, -12.0, 0, "free weights")

    # --- olympic: two lines of four platforms facing the mirror, their storage at the south end
    for row_x, ys in ((-27.27, (9.6, 6.13, 2.66, -0.81)), (-23.91, (7.865, 4.395, 0.925, -2.545))):   # the second line staggered: it sees the mirror
        for y in ys:
            F.put("hammer-strength-impact-suppression-platform", row_x, y, 90, "olympic", "8 x 6 ft: the bar along y, the lifter faces the mirror")
    for x in (-28.0, -26.7, -25.4):
        F.put("rogue-monster-bumper-rack", x, -4.6, 0, "olympic", "bumpers + the competition / change plates")
    F.put("rogue-10-bar-holder", -24.0, -4.6, 0, "olympic", "the Eleiko / Strencor / technique bars")
    F.put("rogue-freestanding-chalk-stand", -25.55, 1.0, 0, "olympic")
    F.put("rogue-freestanding-chalk-stand", -25.55, 8.0, 0, "olympic")
    F.put("rogue-wood-jerk-blocks", -23.91, 7.865, 90, "olympic", "set up on the last platform", on="hammer-strength-impact-suppression-platform-5")
    F.put("titan-deadlift-pulling-blocks", -23.91, 4.395, 90, "olympic", "on a platform", on="hammer-strength-impact-suppression-platform-6")
    F.put("rogue-echo-gym-timer-2-0", XW + 0.09, 4.4, -90, "olympic", "on the mirror wall over the platforms")

    # --- the bench island: two rows of stations back to back, their plate trees + bar holder down the middle
    yc = -28.6
    for x, p_ in zip((-21.0, -17.6, -14.2, -10.8), ("atlantis-olympic-incline-bench-press-with-pivot-p338",) * 3 + ("atlantis-olympic-flat-decline-bench-press-with-pivot-p339",)):
        w, d = G.footprint(p_)
        F.put(p_, x, yc + 0.6 + d / 2, 0, "bench island")
    for x, p_ in zip((-21.0, -17.6, -14.2), ("atlantis-olympic-flat-bench-press-with-pivot-p337", "life-fitness-olympic-flat-bench", "life-fitness-olympic-flat-bench")):
        w, d = G.footprint(p_)
        F.put(p_, x, yc - 0.6 - d / 2, 180, "bench island")
    F.put("life-fitness-olympic-weight-tree", -19.3, yc, 0, "bench island")
    F.put("rogue-10-bar-holder", -15.9, yc, 0, "bench island", "power bars, women's bars, the specialty bars")
    F.put("life-fitness-olympic-weight-tree", -12.5, yc, 0, "bench island")

    # --- the dumbbell island: two racks back to back, benches off both ends
    F.put("hammer-strength-three-tier-dumbbell-rack", -17.95, -22.14, 0, "dumbbell island", "Rogue rubber hex 2.5-25 kg")
    F.put("hammer-strength-three-tier-dumbbell-rack", -17.95, -23.06, 180, "dumbbell island", "Rogue rubber hex 27.5-50 kg")
    for y in (-21.8, -23.4):
        F.put("rogue-adjustable-bench-3-0", -20.5, y, 90, "dumbbell island")
        F.put("rogue-adjustable-bench-3-0", -15.4, y, -90, "dumbbell island")
    dl2 = F.put("rogue-deadlift-platform", -12.3, -22.6, -90, "free weights", "deadlifts; the crash cushions on it")

    # --- the river band: the selectorized legs facing the ravine, in groups (calves, hamstrings, hips, quads)
    row = ["hammer-strength-select-standing-calf", "life-fitness-insignia-series-calf-extension", "hammer-strength-plate-loaded-tibia-dorsi-flexion", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl",
           "life-fitness-axiom-series-leg-curl", None,
           "hammer-strength-select-hip-abduction", "hammer-strength-select-hip-adduction", "hammer-strength-select-hip-abduction",
           "hammer-strength-select-hip-adduction", "life-fitness-insignia-series-glute", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl"]
    y = -31.55
    for p_ in row:
        if p_ is None:
            y += 0.55
            continue
        w, d = G.footprint(p_)
        F.put(p_, -7.35 - d / 2, y + w / 2, -90, "legs by the river")
        y += w + 0.62

    # --- east of the spiral: the hacks + pendulum facing the river, a gap left for the spiral's step-off
    for p_, y0 in (("hammer-strength-plate-loaded-hack-squat", -19.6), ("hammer-strength-plate-loaded-hack-squat", -14.9),
                   ("hammer-strength-plate-loaded-pendulum-x-squat", -12.12)):
        w, d = G.footprint(p_)
        F.put(p_, -11.2 - d / 2, y0 + w / 2, -90, "the squat hub")
    F.put("life-fitness-olympic-weight-tree", -12.3, -20.25, 0, "the squat hub")
    F.put("life-fitness-olympic-weight-tree", -12.3, -12.73, 0, "the squat hub")

    # --- the leg hub north of the spiral: plate-loaded machines back to back, plate trees between their horns
    def hub(pieces, x0, yb, rot, pair=0.9):
        x, prev = x0, "tree"
        for p_ in pieces:
            if p_ == "tree":
                F.put("life-fitness-olympic-weight-tree", x + 0.42, yb + (-0.36 if rot == 180 else 0.36), 0, "the leg hub")
                x += 0.84 + 0.3
            else:
                if prev != "tree":
                    x += pair                             # two machines side by side: room for both sets of horns
                w, d = G.footprint(p_)
                F.put(p_, x + w / 2, yb + (-d / 2 if rot == 180 else d / 2), rot, "the leg hub")
                x += w + 0.3
            prev = p_
    lp = "hammer-strength-plate-loaded-linear-leg-press"
    hub([lp, "tree", lp, "tree", lp, "tree", "hammer-strength-plate-loaded-v-squat"], -22.2, -6.3, 180)
    hub(["hammer-strength-plate-loaded-glute-drive", "tree", "hammer-strength-plate-loaded-glute-drive", "hammer-strength-plate-loaded-belt-squat", "tree",
         "hammer-strength-plate-loaded-belt-squat"], -22.2, -5.7, 0, pair=0.5)
    hub(["hammer-strength-plate-loaded-iso-lateral-leg-extension", "tree", "atlantis-incline-calf-raise-m318", "hammer-strength-plate-loaded-seated-calf-raise"], -22.2, 3.2, 180)
    hub(["life-fitness-smith-machine", "life-fitness-smith-machine", "hammer-strength-glute-ham-reverse-hyper-combo"], -22.2, 3.8, 0)
    # --- the leg extension island (Roman: "only 3 leg extensions? ... the core super popular ones there need to be enough of for
    # everyone"): eight selectorized, back to back, the kneeling curl at its end; with the plate-loaded iso, nine in the gym
    def lrow(pieces, x, yb, rot, gap=0.7):
        for p_ in pieces:
            w, d = G.footprint(p_)
            F.put(p_, x + w / 2, yb + (d / 2 if rot == 0 else -d / 2), rot, "leg extension island")
            x += w + gap
    LF, HS, PR = "life-fitness-insignia-series-leg-extension", "hammer-strength-select-leg-extension", "precor-resolute-series-leg-extension"
    lrow([LF, LF, PR, PR, "hammer-strength-mts-kneeling-leg-curl"], -22.2, 8.4, 0)
    lrow([LF, HS, HS, HS, "hammer-strength-select-hip-abduction", "hammer-strength-select-hip-adduction"], -22.2, 8.0, 180)
    # more of the busy ones (Roman, 2026-10-26: yes to the counts): a fourth leg press + a third glute drive sharing a tree at the
    # cardio's south end, a third smith by the bench island
    w, d = G.footprint(lp)
    F.put(lp, -11.25 + w / 2, -2.6 - d / 2, 180, "the leg hub")
    F.put("life-fitness-olympic-weight-tree", -9.15, -2.95, 0, "the leg hub")
    w, d = G.footprint("hammer-strength-plate-loaded-glute-drive")
    F.put("hammer-strength-plate-loaded-glute-drive", -8.6 + w / 2, -2.6 - d / 2, 180, "the leg hub")
    F.put("life-fitness-smith-machine", -11.4, -30.9, 0, "free weights")

    # --- cardio on the river band: the seats by the glass, the standing machines behind (they see over them)
    y = -1.6
    for p_ in ["life-fitness-row-hx-trainer"] * 3 + ["life-fitness-club-series-upright-lifecycle-bike"] * 3 + ["life-fitness-ic7-indoor-cycle"] * 2:
        w, d = G.footprint(p_)
        F.put(p_, -7.05 - d / 2, y + w / 2, -90, "cardio")
        y += w + 0.75
    y = -1.8
    for p_ in ["woodway-4front"] * 4:
        w, d = G.footprint(p_)
        F.put(p_, -9.75 - d / 2, y + w / 2, -90, "cardio")
        y += w + 0.55

    # --- a PWR Play island by the cardio (Roman: "sub islands of the play station thing ... 2 modules or so on F1 and F2 ... the
    # consistency to hit lats or any of the cable ones for super setting"): two Cores on a crossbar, the pulldowns facing in
    F.maze("f2", {"A": (0, 0), "B": (0, 1)},
           {("A", "W"): "pulldown", ("B", "W"): "pulldown", ("A", "E"): "row", ("B", "E"): "triceps",
            ("A", "S"): "step", ("B", "N"): "crossover", ("A", "N"): "dualhigh", ("B", "S"): "duallow"},
           [("A", "B")], origin=(-10.9, 5.6), zone="PWR Play island")

    # --- the three pods (south annex): the half rack on the flush platform facing the mirror (east wall), a bench, the dumbbells
    for k, (a_, b_) in enumerate([(-22.6, -17.2), (-17.2, -11.8), (-11.8, -6.45)]):
        xa, xb = a_ + 0.075, (b_ - 0.075 if k < 2 else b_ - 0.2)
        cx = (xa + 0.5 + xb) / 2
        fixed.append({"id": f"pod{k + 1}-platform", "room": "", "kind": "floor_zone", "label": "The pod's lifting platform (built, flush): oak centre, rubber drop zones",
                      "x": round(cx, 3), "y": -38.33, "w": 2.44, "d": 2.44, "rot": 0, "fixed": True})
        F.put("rogue-monster-lite-half-rack", cx - 0.25, -38.33, -90, f"pod {k + 1}", "on the pod's platform, the lifter facing the mirror wall")
        F.put("rogue-adjustable-bench-3-0", cx - 0.6, -36.4, -90, f"pod {k + 1}")
        F.put("hammer-strength-three-tier-dumbbell-rack", xb - 0.46, -35.75, 90, f"pod {k + 1}", "Hammer Strength urethane 5-75 lb")

    # --- the posing room: the body scanner in its south-west corner (private: scans are done in underwear), out of the stage's light
    fixed += [{"id": "posing-stage", "room": "", "kind": "keep_clear", "label": "The posing stage + its rig (built)",
               "pts": [[-26.26, -38.025], [-24.46, -38.025], [-24.46, -36.225], [-26.26, -36.225]], "fixed": True},
              {"id": "posing-mirror", "room": "", "kind": "keep_clear", "label": "The posing room's mirror wall + the viewing space before it (built)",
               "pts": [[-23.9, -39.9], [-22.675, -39.9], [-22.675, -34.35], [-23.9, -34.35]], "fixed": True}]
    F.put("fit3d-proscanner", -27.8, -38.85, 0, "posing room", "the body scanner: private (scans are taken in underwear), beside the stage")

    auto_wipes(F, G, fixed, 18)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    F.write("gym_f2", ws, sps, {"fixed": fixed, "overhead": G.overhead("F2")},
            summary=["F2 · strength (first proposal, 2026-10-26)",
                     "Mirror wall: 6 power racks + 2 half racks + a deadlift platform facing the mirror; 8 olympic platforms in two staggered lines.",
                     "Islands: the bench island (7 stations round their trees + bar holder), the dumbbell island, the leg hub, the leg extension island (8).",
                     "River band: the selectorized legs facing the ravine; cardio (seats by the glass, standing behind).",
                     "Upper body (PWR Play maze + machines) is on F3, the den: F2 had no room left for it."])


def wipes(F, G, lvl, spots):
    for x, y_, r in spots:
        F.items.append({"id": f"wipes-{lvl}-{x}-{y_}", "room": "", "kind": "wipe_station", "label": G.KINDS_FIXED["wipe_station"]["label"],
                        "x": x, "y": y_, "w": 0.36, "d": 0.36, "rot": r})


def _front(G, it, kinds):
    """Where the user of a piece trains: its body grown by its front clearance only."""
    f = kinds[it["kind"]]["use"][0]
    return G.item_poly({**it, "kind": "_f"}, {"_f": {"use": [f, 0, 0, 0]}}, use=True)


def auto_wipes(F, G, fixed, n, reach=5.0, spacing=3.5):
    """n wipes stations (Roman 2026-10-26: "need like 3 times the wipe stations"), spread so every piece has one close: greedy over
    free spots (clear of every piece and its use space, the routes, the landings, the walls), each pick covering the most pieces not
    yet within `reach` m of a station, then the furthest-off pieces; never two closer than `spacing`."""
    import math
    from shapely.geometry import LineString, Point, Polygon, box
    from shapely.ops import unary_union
    kinds = G.kinds_for({it["kind"] for it in F.items if it["kind"] in G.SIZES})
    room = unary_union([Polygon(s_["poly"]) for s_ in G.M["spaces"] if s_["level"] == F.level and s_["id"] in F.room_ids])
    walls = unary_union([LineString([w["from"], w["to"]]).buffer(w["size"][0] / 2) for w in F.walls])
    room = room.difference(walls)
    occ, eq, bodies = [], [], []
    for it in F.items + fixed:
        if it["kind"] in ("floor_zone", "pwr_meta"):
            continue
        if it["kind"] == "route":
            occ.append(LineString(it["pts"]).buffer(it.get("width", 1.7) / 2)); continue
        p_ = G.item_poly(it, kinds)
        if p_ is None:
            continue
        occ.append(p_)
        u = G.item_poly(it, kinds, use=True)
        f_ = kinds.get(it["kind"], {}).get("use")
        if u is not None and f_ and f_[0] >= 0.5 and not it.get("fixed"):   # stay out of where the user trains (their front), not the rest
            occ.append(_front(G, it, kinds))
        bodies.append(p_)
        if not it.get("fixed") and it["kind"] in kinds and kinds[it["kind"]].get("mat") not in ("storage", "wallkit", "fixture", "platform") or it["kind"].startswith("pwr_core"):
            eq.append(p_.centroid)
    free = room.buffer(-0.2).difference(unary_union(occ).buffer(0.19))     # up against things is fine (Roman): they blend in
    snug = unary_union(bodies)
    x0, y0, x1, y1 = free.bounds
    cands = [Point(x0 + 0.4 * i, y0 + 0.4 * j) for i in range(int((x1 - x0) / 0.4) + 1) for j in range(int((y1 - y0) / 0.4) + 1)]
    cands = [c for c in cands if free.contains(c)]
    picks = []
    for _ in range(n):
        best, key = None, None
        for c in cands:
            if any(c.distance(p_) < spacing for p_ in picks):
                continue
            unc = [e for e in eq if min([e.distance(p_) for p_ in picks] or [99]) > reach]
            k_ = (sum(1 for e in unc if e.distance(c) <= reach), -round(c.distance(snug), 1))     # then tucked against something
            if key is None or k_ > key:
                best, key = c, k_
        if best is None:
            break
        picks.append(best)
    for c in picks:
        e = min(eq, key=lambda e: e.distance(c))
        rot = round(math.degrees(math.atan2(-(e.x - c.x), e.y - c.y)) / 90) * 90
        F.items.append({"id": f"wipes-{F.level}-{c.x:.1f}-{c.y:.1f}", "room": "", "kind": "wipe_station", "label": G.KINDS_FIXED["wipe_station"]["label"],
                        "x": round(c.x, 2), "y": round(c.y, 2), "w": 0.36, "d": 0.36, "rot": rot, "note": "wipes + spray + bin"})
    far = [e for e in eq if min(e.distance(p_) for p_ in picks) > reach]
    print(f"  {F.level}: {len(picks)} wipes stations; {len(far)} pieces further than {reach} m from one")


def place_row(F, G, pieces, x_front, y0, rot, gap, zone, note=""):
    """Pieces side by side along +y, users facing east (rot -90) or west (90), their fronts on x_front."""
    y = y0
    for p_ in pieces:
        if p_ is None:
            y += 0.6
            continue
        w, d = G.footprint(p_)
        F.put(p_, x_front - d / 2 if rot == -90 else x_front + d / 2, y + w / 2, rot, zone, note)
        y += w + gap
    return y


def plan_f3(G):
    F = G.Floor("F3", "F3 · the den: upper-body maze, dumbbells, functional, strongman, altitude", [-30.5, -41.0, -5.4, 13.2])
    ws = G.walls("F3")
    ids = ["free-weights-F3", "strongman", "functional", "sled-track", "river-edge", "spiral-F3", "north-stair-F3", "altitude"]
    F.room_ids, F.walls = ids, ws
    sps = G.spaces("F3", ids)
    room = G.room_poly("F3", ids)
    fixed = G.spiral_items("F3") + G.landings(ws, "F3", room) + [i for i in G.fixtures("F3") if i["kind"] != "wipe_station"]
    fixed += [{"id": "sled-lane", "room": "", "kind": "turf", "label": G.KINDS_FIXED["turf"]["label"], "x": -13.2, "y": -23.725, "w": 2.4, "d": 20.25, "rot": 0, "fixed": True},
              {"id": "den-river", "room": "", "kind": "den_river", "label": G.KINDS_FIXED["den_river"]["label"],
               "pts": [[-8.25, -33.85], [-6.65, -33.85], [-6.65, 11.85], [-8.25, 11.85]], "fixed": True},
              {"id": "north-stair", "room": "", "kind": "stair", "label": "The stair down to F4 (opening)", "pts": [[-21.45, 7.1], [-15.45, 7.1], [-15.45, 11.85], [-21.45, 11.85]], "fixed": True}]
    F.zone("Walkway: the W2 + W1 stairs, the WCs, the AED, the glass lift (keep it clear)", XW, -27.2, -27.0, -9.2)

    # --- the dumbbell den (Roman: "staggered rows so everyone has the optimal mirror positioning ... 4 deep is retarded"): two rows
    # facing the mirror wall, the second row in the first row's gaps so every bench sees the mirror; 2.6 m between benches in a
    # row (the dumbbells swing clear); the racks moved off the mirror into an island behind the second row
    benches = ["rogue-adjustable-bench-3-0"] * 16 + ["rogue-manta-ray-adjustable-bench"] * 2
    k = 0
    for x, y0 in ((-25.8, -31.9), (-23.4, -30.6)):
        for j in range(9):
            F.put(benches[k], x, y0 + 2.6 * j, 90, "dumbbell den", "facing the mirror; " + ("first row" if x < -25 else "second row: sees the mirror through the first row's gaps"))
            k += 1
    for y in (-26.48, -24.42):
        F.put("hammer-strength-three-tier-dumbbell-rack", -19.86, y, 90, "dumbbell den", "Rogue rubber hex to 75 kg: faces the bench rows")
        F.put("hammer-strength-three-tier-dumbbell-rack", -18.94, y, -90, "dumbbell den", "Rogue rubber hex 2.5-50 kg")
    F.put("life-fitness-3-tier-accessory-rack", -19.4, -28.4, 180, "dumbbell den", "LF cast iron kettlebells 4-32 kg")
    F.put("life-fitness-3-tier-accessory-rack", -19.4, -22.5, 0, "dumbbell den", "HS competition kettlebells 8-32 kg")
    for y in (-26.9, -24.0):
        F.put("rogue-adjustable-bench-3-0", -16.4, y, -90, "dumbbell den", "off the island's east side")
    F.put("rogue-freestanding-chalk-stand", -21.2, -31.6, 0, "dumbbell den")
    F.put("rogue-belt-and-band-hanger", XW + 0.155, -8.8, -90, "dumbbell den", "belts, straps, sleeves, wraps on loan; dip belts")
    # the grip wall on the south wall, either side of the altitude room's door
    for x in (-27.3, -20.6, -19.3, -18.0, -16.7):
        F.put("beastmaker-2000-series-hangboard", x, YS + 0.087, 0, "grip wall", "pinch blocks, cannonball grips, wrist roller hang beside")
    F.put("beastmaker-2000-series-hangboard", -24.9, YS + 0.087, 0, "grip wall")
    F.put("metolius-wood-grips-campus-rungs", -15.4, YS + 0.075, 0, "grip wall")
    # posterior chain by the sled lane
    F.put("hammer-strength-fixed-pad-glute-ham", -15.9, -29.4, 0, "functional")
    F.put("hammer-strength-fixed-pad-glute-ham", -17.2, -29.4, 0, "functional")
    F.put("the-abs-company-the-nordic-curl", -16.0, -20.9, 0, "functional")
    for p_, y in (("hammer-strength-fixed-pad-glute-ham", -11.6), ("hammer-strength-fixed-pad-glute-ham", -8.9),
                  ("hammer-strength-back-extension", -6.3), ("hammer-strength-back-extension", -3.9)):
        F.put(p_, -13.2, y, 0, "posterior chain", "moved down from F2 for the leg extension island")
    F.put("hammer-strength-plate-loaded-glute-drive", -15.4, -10.9, 0, "posterior chain", "the fourth glute drive")
    y = -2.4
    for p_ in ("hammer-strength-select-chest-press", "hammer-strength-select-chest-press", "hammer-strength-select-pectoral-fly-rear-deltoid",
               "hammer-strength-select-pectoral-fly-rear-deltoid", "select_shoulder", "select_shoulder"):
        if p_ == "select_shoulder":
            w, d = 1.35, 1.3
            F.items.append({"id": f"select-shoulder-{y:.1f}", "room": "upper beside the maze", "kind": "select_shoulder", "label": G.KINDS_FIXED["select_shoulder"]["label"],
                            "x": round(-11.9 - d / 2, 3), "y": round(y + w / 2, 3), "w": w, "d": d, "rot": -90})
        else:
            w, d = G.footprint(p_)
            F.put(p_, -11.9 - d / 2, y + w / 2, -90, "upper beside the maze", "facing the river")
        y += w + 0.9

    # --- the rig on the functional floor (north-west): pull-up / squat bays, rings + climbing ropes hung from it
    rig = F.put("rogue-monster-rig-2-0", -24.8, -1.0, 0, "functional", "rings, climbing ropes, the parallel bars + a landmine on it")
    F.put("rogue-rig-mount-parallel-bars", -23.4, -1.0, 0, "functional", "on the rig", on=rig["id"])
    F.put("rogue-10-bar-holder", -26.2, -8.2, 0, "functional", "the rig's bars")
    F.put("rogue-freestanding-chalk-stand", -22.9, -3.4, 0, "functional")

    # --- the upper-body maze (PWR Play, 2 x 3 Cores): pulldowns, rows + triceps on the outside, crossovers + dual cables down
    # the aisles, pull-up handles on every crossbar
    cores = {"A": (0, 0), "B": (1, 0), "C": (0, 1), "D": (1, 1), "E": (0, 2), "F": (1, 2)}
    faces = {("A", "W"): "row", ("C", "W"): "adjustable", ("E", "W"): "dipchin",
             ("B", "E"): "pulldown", ("D", "E"): "row", ("F", "E"): "pulldown",
             ("A", "S"): "powerpivot", ("B", "S"): "triceps", ("E", "N"): "stallbars", ("F", "N"): "row",
             ("A", "E"): "crossover", ("B", "W"): "crossover", ("C", "E"): "dualhigh", ("D", "W"): "duallow",
             ("E", "E"): "ropepull", ("F", "W"): "handles",
             ("A", "N"): "crossover", ("C", "S"): "crossover", ("C", "N"): "dip", ("E", "S"): "step",
             ("B", "N"): "dualhigh", ("D", "S"): "duallow", ("D", "N"): "crossover", ("F", "S"): "crossover"}
    bars = [("A", "B"), ("C", "D"), ("E", "F"), ("A", "C"), ("C", "E"), ("B", "D"), ("D", "F")]
    F.maze("den", cores, faces, bars, origin=(-20.0, -1.9), zone="the maze")

    # --- the plate-loaded upper hub between the maze and the spiral: back to back, the trees between the horns
    def hub(pieces, x0, yb, rot):
        x, prev = x0, "tree"
        for p_ in pieces:
            if p_ == "tree":
                F.put("life-fitness-olympic-weight-tree", x + 0.42, yb + (-0.36 if rot == 180 else 0.36), 0, "upper hub")
                x += 0.84 + 0.3
            else:
                if prev != "tree":
                    x += 0.9
                w, d = G.footprint(p_)
                F.put(p_, x + w / 2, yb + (-d / 2 if rot == 180 else d / 2), rot, "upper hub")
                x += w + 0.3
            prev = p_
    hub(["hammer-strength-plate-loaded-iso-lateral-bench-press", "tree", "hammer-strength-plate-loaded-iso-lateral-incline-press",
         "hammer-strength-plate-loaded-iso-lateral-shoulder-press"], -22.1, -7.5, 180)
    hub(["hammer-strength-plate-loaded-iso-lateral-row", "tree", "hammer-strength-plate-loaded-iso-lateral-front-lat-pulldown",
         "hammer-strength-plate-loaded-iso-lateral-shoulder-press"], -22.1, -6.9, 0)

    # --- strongman (north-west): the carry lane down the mirror wall, the yoke at its head, the stones by the stair
    F.zone("Carry lane: yoke, farmers, sandbags (down the wall, 11 m)", XW, -0.2, -26.3, 11.0, "zone-carry")
    F.put("rogue-yoke", -27.75, 9.9, 180, "strongman", "carried south down the lane")
    F.put("rogue-farmers-walk-handles", -25.2, 9.2, 180, "strongman")
    F.put("titan-atlas-stone-platform", -22.95, 8.2, 90, "strongman", "loaded from the west")
    F.put("rogue-rubber-atlas-stones", -22.95, 5.9, 90, "strongman")
    F.put("rogue-strongman-sandbags", -25.2, 11.25, 180, "strongman", "25-400 lb along the north wall")
    F.put("rogue-10-bar-holder", -22.6, 11.3, 180, "strongman", "log, axle, the hex bars")
    F.put("hammer-strength-plate-loaded-t-bar-row", -24.4, 5.4, 0, "strongman", "T-bar row (the landmine pulls) by the strongman bays")
    # the functional floor (west, between the lift and the strongman): wall balls + pegboard on the mirror wall, storage, open floor
    F.zone("Open floor: classes, wall balls, plyo", -27.0, -9.2, -22.6, -3.2, "zone-open")
    F.put("life-fitness-escape-endura-wall-balls", XW + 0.405, -6.5, -90, "functional", "the targets above, the balls on the shelf")
    F.put("rogue-pine-maple-peg-board", XW + 0.12, -3.4, -90, "functional")
    F.put("rogue-monster-mass-storage", -28.55, 1.1, -90, "functional", "slam balls, Sandbag 2.0s, medicine balls, battle ropes, jump ropes, AbMats, vests")
    F.put("life-fitness-vertical-medicine-ball-storage", -28.85, 2.6, -90, "functional")
    for x in (-25.9, -25.1, -24.3):
        F.put("hammer-strength-3-in-1-wood-plyo-box", x, 2.75, 180, "functional", "a stack of three")
    for x in (-23.5,):
        F.put("hammer-strength-3-in-1-soft-plyo-box", x, 2.75, 180, "functional", "soft boxes stacked")
    F.put("hammer-strength-stackable-plyo-box", -22.6, 2.7, 180, "functional")
    F.put("rogue-freestanding-chalk-stand", -21.0, 1.6, 0, "the maze")
    F.put("rogue-echo-gym-timer-2-0", XW + 0.09, -1.2, -90, "functional", "over the open floor")
    F.put("life-fitness-barbell-rack", -9.1, 5.65, -90, "upper by the river", "the Hammer Strength fixed straight barbells")
    F.put("life-fitness-barbell-rack", -8.85, 8.0, -90, "upper by the river", "the Life Fitness 12-sided fixed EZ bars")

    # --- by the river (east of the sled lane): the upper selectorized + conditioning, facing the water
    y = place_row(F, G, ["concept2-skierg"] * 3 + [None] + ["hammer-strength-hd-air-bike"] * 4 + [None] + ["life-fitness-row-hx-trainer"] * 4,
                  -8.4, -32.4, -90, 0.55, "conditioning by the river")
    y = place_row(F, G, [None, "hammer-strength-select-chest-press"] * 1 + ["hammer-strength-select-chest-press"] * 2 + [None]
                  + ["hammer-strength-select-pectoral-fly-rear-deltoid"] * 2 + [None, "hammer-strength-select-biceps-curl", "hammer-strength-seated-arm-curl",
                  None, "hammer-strength-plate-loaded-abdominal-oblique-crunch", "body-solid-gvkr60b-vertical-knee-raise-dip",
                  "gmwd-multi-functional-seal-row-bench-sr05", "hammer-strength-back-extension"], -8.4, y + 0.4, -90, 0.7, "upper by the river")
    F.put("hammer-strength-assisted-nordic-ham", -10.1, 8.0, 180, "by the river")

    # --- the sled lane: the sleds parked at its ends, the harnesses on mass storage by its south end
    for y in (-33.1, -32.0):
        pass
    F.put("life-fitness-push-pull-weight-sled", -13.9, -32.9, 0, "sled lane", "parked at the start line")
    F.put("life-fitness-push-pull-weight-sled", -12.6, -32.9, 0, "sled lane", "parked at the start line")
    F.put("life-fitness-push-pull-weight-sled", -13.9, -14.3, 180, "sled lane", "parked at the far end")
    F.put("life-fitness-acft-sled-with-strap", -12.6, -15.0, 180, "sled lane", "parked at the far end")
    F.put("life-fitness-acft-sled-with-strap", -12.6, -30.6, 0, "sled lane", "parked at the start line")
    F.put("rogue-monster-mass-storage", -9.4, -33.35, 0, "sled lane", "harnesses, cones, hurdles, the agility ladder")

    # --- the altitude room (south annex): bikes in front, treadmills + rowers behind, all facing the display on the west wall
    fixed.append({"id": "airlock", "room": "", "kind": "keep_clear", "label": "The altitude room's airlock (built)",
                  "pts": [[-23.95, -36.4], [-20.95, -36.4], [-20.95, -34.35], [-23.95, -34.35]], "fixed": True})
    place_row(F, G, ["life-fitness-ic7-indoor-cycle", "life-fitness-club-series-upright-lifecycle-bike", "life-fitness-club-series-upright-lifecycle-bike",
                     "life-fitness-ic7-indoor-cycle"], -26.2, -39.55, 90, 0.6, "altitude", "facing the altitude display")
    place_row(F, G, ["life-fitness-row-hx-trainer", "woodway-4front", "woodway-4front", "life-fitness-row-hx-trainer"], -20.4, -39.55, 90, 0.6, "altitude",
              "facing the altitude display")

    auto_wipes(F, G, fixed, 17)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    F.write("gym_f3", ws, sps, {"fixed": fixed, "overhead": G.overhead("F3")},
            summary=["F3 · the den (first proposal, 2026-10-26)",
                     "Mirror wall: the dumbbell den, 18 bench stations in two staggered rows (every bench sees the mirror), the racks + kettlebells on an island behind them.",
                     "Islands: the PWR Play maze (2 x 3 Cores, 7 crossbars), the plate-loaded upper hub, the den island (dumbbells + kettlebells).",
                     "The rig on the functional floor with wall balls + pegboard; strongman + the carry lane by the stair; the grip wall on the south wall.",
                     "By the river: SkiErgs, air bikes, rowers, then the selectorized upper body facing the water.",
                     "Upper body moved here from F2 (the maze + its machines): F2 had no room for it."])


def plan_f1(G):
    F = G.Floor("F1", "F1 · the hall: cardio, stretching, calisthenics", [-30.5, -35.0, -5.4, -8.0])
    ws = G.walls("F1")
    ids = ["stretching", "calisthenics", "cardio-F1", "spiral-F1"]
    F.room_ids, F.walls = ids, ws
    sps = G.spaces("F1", ids)
    room = G.room_poly("F1", ids)
    fixed = G.spiral_items("F1") + G.landings(ws, "F1", room) + [i for i in G.fixtures("F1") if i["kind"] != "wipe_station"]
    fixed.append({"id": "clear-gallery", "room": "", "kind": "keep_clear", "label": "Keep clear: the way in from the gallery (the bridge, the lockers)",
                  "pts": [[-11.6, -11.0], [-6.51, -11.0], [-6.51, -9.375], [-11.6, -9.375]], "fixed": True})
    XWF, XEF, YSF, YNF = -28.725, -6.51, -34.04, -9.375          # the core walls' faces, the glass, the locker block's wall

    # --- cardio along the glass: the treadmills facing the river, the standing machines behind them, the bikes on the south glass
    place_row(F, G, ["woodway-4front"] * 5 + ["hammer-strength-hd-tread"] * 2 + ["woodway-4front"] * 5, XEF - 0.3, -33.55, -90, 0.5, "cardio by the river")
    place_row(F, G, ["life-fitness-club-series-elliptical-cross-trainer"] * 7 + [None] + ["stairmaster-8gx-stepmill"] * 3 + ["versaclimber-ts-magnetic"],
              -10.75, -33.55, -90, 0.5, "cardio by the river")

    # --- two PWR Play islands, one either side of the spiral (lats + cables on every floor, for supersets)
    F.maze("f1w", {"A": (0, 0), "B": (0, 1)},
           {("A", "W"): "pulldown", ("B", "W"): "pulldown", ("A", "E"): "handles", ("B", "E"): "triceps",
            ("A", "S"): "dualhigh", ("B", "N"): "duallow", ("A", "N"): "crossover", ("B", "S"): "crossover"},
           [("A", "B")], origin=(-24.0, -17.0), zone="PWR Play island (garden side)")
    F.maze("f1e", {"A": (0, 0), "B": (0, 1)},
           {("A", "E"): "pulldown", ("B", "E"): "pulldown", ("A", "W"): "handles", ("B", "W"): "panel",
            ("A", "S"): "step", ("B", "N"): "ropepull", ("A", "N"): "crossover", ("B", "S"): "crossover"},
           [("A", "B")], origin=(-12.0, -17.3), zone="PWR Play island (river side)")
    x = -22.6
    for p_ in ["life-fitness-club-series-recumbent-lifecycle-bike"] * 3 + ["life-fitness-club-series-upright-lifecycle-bike"] * 3:
        w, d = G.footprint(p_)
        F.put(p_, x + w / 2, YSF + 0.3 + d / 2, 180, "bikes on the south glass", "facing the forest")
        x += w + 0.75

    # --- the walking routes (1.7 m clear; nothing stands in them): in from the gallery down the river side (behind the treadmills)
    # and along the locker wall past the spiral to the W1 stair + lift; down the garden side to the W2 stair; along the bikes
    F.route("r-gallery-cardio", [(-9.55, -9.4), (-9.55, -33.0)], "in from the gallery, down the river side behind the treadmills")
    F.route("r-gallery-west", [(-10.4, -10.5), (-27.1, -10.5)], "in from the gallery along the locker wall: the spiral, the W1 stair + lift", width=1.6)
    F.route("r-garden-side", [(-26.3, -10.5), (-26.3, -30.4), (-13.8, -30.4)], "down the garden side: the W2 stair, the mats, the bikes")

    # --- calisthenics in the middle of the hall (seen from the gallery and the spiral): the Monkey Rig, its parallel bars, the
    # VKR + parallettes beside it, wall bars on the W1 core
    mr = F.put("rogue-monster-lite-monkey-rig-2-0", -17.95, -23.6, 0, "calisthenics", "rings on the 2.47 m bars; the parallel bars on it")
    F.put("rogue-rig-mount-parallel-bars", -15.6, -23.6, 0, "calisthenics", "on the rig", on=mr["id"])
    F.put("body-solid-gvkr60b-vertical-knee-raise-dip", -20.4, -27.4, 0, "calisthenics")
    # three pull-up stations a little north of the rig, their bars parallel to it (Roman: "rotate them 90 degrees from how you have
    # them now and put them out a little bit north of the monkey rig"): freestanding, hung from either side
    for dx in (-2.6, 0.0, 2.6):
        F.items.append({"id": f"pullup-{dx:+.1f}", "room": "calisthenics", "kind": "rig_spur", "label": G.KINDS_FIXED["rig_spur"]["label"],
                        "x": round(-17.95 + dx, 3), "y": -20.3, "w": 1.5, "d": 0.08, "rot": 0,
                        "note": "pull-ups, chin-ups, hanging leg raises, muscle-ups; hang facing the rig or the spiral"})
    for x in (-18.9, -17.9, -16.9):
        for y in (-27.4, -28.2):
            F.put("rogue-bolt-together-parallette-set", x, y, 0, "calisthenics", "L-sits, planche, push-ups")
    F.zone("Skills floor: handstands, levers, L-sits (gymnastics mat)", -21.6, -29.5, -14.3, -26.2, "zone-skills")
    for y in (-17.75, -16.25, -14.75):
        F.put("gymleco-wooden-wall-bars-with-chins-rack", XWF + 0.315, y, -90, "calisthenics", "on the W1 core wall (the chin bar can't meet the 2.47 m rule)")
    F.put("gymleco-wooden-wall-bars-with-chins-rack", XWF + 0.315, -28.0, -90, "stretching", "on the W2 core wall")
    F.put("rogue-belt-and-band-hanger", -13.2, YNF - 0.155, 180, "calisthenics", "dip belts, bands")

    # --- stretching + mobility round the rig and on the garden side: the mat floor, the kit beside it
    F.zone("Open mat floor: stretching, mobility, small classes (mats from the racks)", -25.4, -29.5, -21.6, -26.2, "zone-mats")
    F.zone("Mat floor", -25.4, -26.2, -22.4, -20.6, "zone-mats-2")
    for y in (-33.2, -31.7):
        F.put("life-fitness-adjustable-wall-mounted-mat-rack", XWF + 0.135, y + 0.7, -90, "stretching", "core + yoga mats")
    F.put("life-fitness-adjustable-wall-mounted-mat-rack", -20.3, YNF - 0.135, 180, "stretching", "core + yoga mats")
    for x in (-24.0, -22.45):
        F.put("life-fitness-accessory-rack", x, -19.9, 180, "stretching", "foam rollers, bands, straps, blocks, massage balls, Theraguns")
    F.put("life-fitness-accessory-rack", -15.6, -28.9, 0, "stretching", "foam rollers, bands, straps, blocks, massage balls, Theraguns")
    F.put("hammer-strength-stability-ball", -25.0, -23.5, 90, "stretching", "stability balls, BOSUs, balance + slant boards beside")
    F.put("life-fitness-vertical-medicine-ball-storage", -13.9, -27.2, 0, "stretching")
    F.put("life-fitness-flexibility-trainer", -23.6, -21.9, 0, "stretching")
    F.put("life-fitness-flexibility-trainer", -23.6, -24.5, 0, "stretching")
    F.put("rogue-manta-ray-adjustable-bench", -24.0, -28.3, 90, "stretching", "ab bench")

    auto_wipes(F, G, fixed, 8)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    F.write("gym_f1", ws, sps, {"fixed": fixed, "overhead": G.overhead("F1")},
            summary=["F1 · the hall (first proposal, 2026-10-26)",
                     "Cardio on the glass: 10 treadmills facing the river, the ellipticals, stepmills + VersaClimber behind, the bikes facing the forest.",
                     "Calisthenics in the middle of the hall: the Monkey Rig with three pull-up stations just north of it, a skills floor + 6 parallettes south of it, wall bars on the core.",
                     "Walking routes kept clear: in from the gallery, along the locker wall to the spiral + W1, down the garden side.",
                     "The body scanner is in the posing room on F2 (private)."])


def plan_annex(G):
    pass  # the pods are on gym_f2, the altitude room on gym_f3

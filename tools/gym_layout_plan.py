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
    """F2 as rooms within the room (Roman 2026-10-28, after walking it: "the walking spaces seem way too cluttered ... artificial walls
    ... focus clusters ... so it isn't just a warehouse feel"; the mix of partitions, ~15-20 % of the kit cut). The partitions are
    building walls (tools/interior.py ZONE_WALLS). One spine runs north-south from the pods to the cardio, the rooms open off it:
    the rack room (tall wall behind the racks), the pulling corner, olympic (tall south wall, low east wall), the bench room and the
    dumbbell bay (a low wall between them), the leg hub, the leg room (tall wall at its south), the river legs + the squat corner,
    cardio. Cut: 2 olympic platforms, a deadlift platform, the decline station, a smith, the V-squat, a Precor leg extension, an
    abduction + adduction, a seated + a lying curl, a rower + an upright bike."""
    F = G.Floor("F2", "F2 · strength: free weights, olympic, legs, cardio, the pods", [-30.5, -41.0, -5.4, 13.2])
    ws = G.walls("F2")
    ids = ["free-weights", "olympic", "cardio-F2", "machines-2", "machines", "spiral-F2", "posing", "pod-1", "pod-2", "pod-3"]
    F.room_ids, F.walls = ids, ws
    sps = G.spaces("F2", ids)
    room = G.room_poly("F2", ids)
    fixed = G.spiral_items("F2") + G.landings(ws, "F2", room) + [i for i in G.fixtures("F2") if i["kind"] != "wipe_station"]

    # --- the walking routes (nothing stands in them): the spine from the pods to the cardio, jogging west round the treadmills;
    # in from the W1 stairs + lift past the spiral; the south walk to the pods
    F.route("r-spine", [(-11.8, -33.0), (-11.8, -3.2), (-12.55, -2.0), (-12.55, 11.0)], "the spine: the pods to the cardio, every room opens off it", width=1.8)
    F.route("r-w1", [(-27.4, -12.05), (-21.9, -12.05), (-20.7, -10.3), (-12.7, -10.3)], "in from the W1 stairs + lift, past the spiral to the spine", width=1.6)
    F.zone("Walkway: the W2 + W1 stairs, the WCs, the AED, the glass lift (keep it clear)", XW, -27.2, -27.0, -9.2)
    F.zone("South walk: the posing room + the three pods", -27.6, YS, -7.0, -32.05)

    # --- the rack room: six racks facing the mirror, their backs to a tall slat wall
    plat = "titan-series-power-rack-lifting-platform"
    for k in range(6):
        y = -30.43 + 3.14 * k
        p_ = F.put(plat, -24.215, y, 90, "rack room", "rack platform: the lifter faces the mirror")
        r_ = F.put("rep-pr-5000-rack-builder", -23.59, y, 90, "rack room", "on its platform; spotter arms, landmine, dip, band pegs on some", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.3, y, 90, "rack room", "lives in the rack", on=r_["id"])
    F.put("rogue-freestanding-chalk-stand", -28.55, -32.9, 0, "rack room")
    # --- the pulling corner (behind the W1 doors, its own tall wall): the half racks + the deadlift platform
    for y in (-9.9, -6.85):   # 1.2 m between the racks (NSCA 0.9)
        p_ = F.put("hammer-strength-rubber-platform", -24.685, y, 90, "pulling corner", "half rack platform")
        r_ = F.put("rogue-monster-half-rack", -24.56, y, 90, "pulling corner", "on its platform", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.9, y, 90, "pulling corner", "lives in the rack", on=r_["id"])
    F.put("rogue-deadlift-platform", -24.9, -3.06 - 0.1 - 1.381 / 2, 0, "pulling corner", "deadlifts; the crash cushions on it; along the olympic wall, 0.9 m+ clear of the half rack (NSCA)")
    F.put("life-fitness-olympic-weight-tree", -22.9, -4.0, 90, "pulling corner", "the deadlift's plates, within 0.9 m of the bar (NSCA)")
    F.put("rogue-belt-and-band-hanger", -22.4 - 0.06 - 0.155, -8.4, 90, "pulling corner", "belts, straps, sleeves, wraps on loan; the bands; on the slat wall (not the mirror)")
    F.put("rogue-freestanding-chalk-stand", -23.0, -10.3, 0, "pulling corner")

    # --- olympic: six platforms in two staggered lines facing the mirror, bumpers between them, the bars on the tall south wall, a low wall east
    for row_x, ys in ((-27.27, (9.6, 6.13, 2.66)), (-23.91, (7.865, 4.395, 0.925))):
        for y in ys:
            F.put("hammer-strength-impact-suppression-platform", row_x, y, 90, "olympic", "8 x 6 ft: the bar along y, the lifter faces the mirror")
    for x, y in ((-27.27, 7.865), (-27.27, 4.395), (-23.91, 6.13), (-23.91, 2.66)):   # (2026-10-30, NSCA: the plates beside every platform)
        F.put("rogue-monster-bumper-rack", x, y, 0, "olympic", "bumpers + change plates, in the gap between two platforms")
    F.put("rogue-10-bar-holder", -23.6, -2.57, 0, "olympic", "the Eleiko / Strencor / technique bars")
    F.put("rogue-freestanding-chalk-stand", -25.55, 1.0, 0, "olympic")
    F.put("rogue-freestanding-chalk-stand", -25.55, 8.0, 0, "olympic")
    F.put("rogue-wood-jerk-blocks", -23.91, 7.865, 90, "olympic", "set up on a platform", on="hammer-strength-impact-suppression-platform-4")
    F.put("titan-deadlift-pulling-blocks", -23.91, 4.395, 90, "olympic", "on a platform", on="hammer-strength-impact-suppression-platform-5")
    F.put("rogue-echo-gym-timer-2-0", -25.3, -3.0 + 0.06 + 0.09, 0, "olympic", "on the tall south wall, in view of every platform (not on the mirror)")

    # --- the bench room: three stations each side of the trees + bar holder, a low wall to its north
    yc = -28.6
    for x, p_ in zip((-21.0, -17.6, -14.2), ("atlantis-olympic-incline-bench-press-with-pivot-p338",) * 3):
        w, d = G.footprint(p_)
        F.put(p_, x, yc + 0.6 + d / 2, 0, "bench room")
    for x, p_ in zip((-21.0, -17.6, -14.2), ("atlantis-olympic-flat-bench-press-with-pivot-p337", "life-fitness-olympic-flat-bench", "life-fitness-olympic-flat-bench")):
        w, d = G.footprint(p_)
        F.put(p_, x, yc - 0.6 - d / 2, 180, "bench room")
    F.put("life-fitness-olympic-weight-tree", -19.3, yc, 0, "bench room")
    F.put("life-fitness-olympic-weight-tree", -15.9, yc, 0, "bench room", "the Life Fitness flat benches have no horns: plates within 0.9 m (NSCA)")
    F.put("rogue-10-bar-holder", -15.9, -31.3, 0, "bench room", "power bars, women's bars, the specialty bars")

    # --- the dumbbell bay: two racks back to back, benches off both ends
    F.put("hammer-strength-three-tier-dumbbell-rack", -17.95, -22.14, 0, "dumbbell bay", "Rogue rubber hex 2.5-25 kg")
    F.put("hammer-strength-three-tier-dumbbell-rack", -17.95, -23.06, 180, "dumbbell bay", "Rogue rubber hex 27.5-50 kg")
    for y in (-21.8, -23.4):
        F.put("rogue-adjustable-bench-3-0", -20.5, y, 90, "dumbbell bay")
        F.put("rogue-adjustable-bench-3-0", -15.4, y, -90, "dumbbell bay")

    # --- the river legs: the selectorized legs facing the ravine, in groups (calves, hamstrings, hips)
    row = ["hammer-strength-select-standing-calf", "life-fitness-insignia-series-calf-extension", "hammer-strength-plate-loaded-tibia-dorsi-flexion", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl", None,
           "hammer-strength-select-hip-abduction", "hammer-strength-select-hip-adduction", "life-fitness-insignia-series-glute", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl"]
    y = -31.55
    for p_ in row:
        if p_ is None:
            y += 0.55
            continue
        w, d = G.footprint(p_)
        F.put(p_, -7.35 - d / 2, y + w / 2, -90, "river legs")
        y += w + 0.62
    F.notes.append(f"river legs end at y {y:.2f}")
    # --- the squat corner at the river legs' north end: the hacks + the pendulum facing the river, trees between
    y = y + 0.4
    for p_ in ("hammer-strength-plate-loaded-hack-squat", "tree", "hammer-strength-plate-loaded-hack-squat", "tree", "hammer-strength-plate-loaded-pendulum-x-squat"):
        w, d = (0.84, 0.71) if p_ == "tree" else G.footprint(p_)
        if p_ == "tree":
            F.put("life-fitness-olympic-weight-tree", -8.3, y + w / 2, 90, "squat corner", "loaded from both sides")
        else:
            F.put(p_, -7.35 - d / 2, y + w / 2, -90, "squat corner")
        y += w + 0.15
    F.notes.append(f"squat corner ends at y {y:.2f}")

    # --- the leg hub (between the spiral and the leg room's tall wall): plate-loaded back to back, plate trees between their horns
    def hub(pieces, x0, yb, rot, zone, pair=0.9):
        x, prev = x0, "tree"
        for p_ in pieces:
            if p_ == "tree":
                F.put("life-fitness-olympic-weight-tree", x + 0.42, yb + (-0.36 if rot == 180 else 0.36), 0, zone)
                x += 0.84 + 0.3
            else:
                if prev != "tree":
                    x += pair
                w, d = G.footprint(p_)
                F.put(p_, x + w / 2, yb + (-d / 2 if rot == 180 else d / 2), rot, zone)
                x += w + 0.3
            prev = p_
        return x
    lp, gd, bs = "hammer-strength-plate-loaded-linear-leg-press", "hammer-strength-plate-loaded-glute-drive", "hammer-strength-plate-loaded-belt-squat"
    F.notes.append("leg hub A ends %.2f" % hub([lp, "tree", lp, "tree", lp], -21.5, -5.95, 180, "leg hub"))
    F.notes.append("leg hub B ends %.2f" % hub([gd, "tree", gd, bs], -21.5, -5.35, 0, "leg hub", pair=0.5))
    # --- the leg room (north of the tall wall): a row backed onto the wall, the smith / calf island, the leg extension island
    F.notes.append("leg room wall row ends %.2f" % hub([lp, "tree", bs, "tree", gd], -21.6, -2.17, 0, "leg room"))
    F.notes.append("leg room 1 ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-leg-extension", "tree", "atlantis-incline-calf-raise-m318",
                                                 "hammer-strength-plate-loaded-seated-calf-raise"], -21.6, 3.8, 180, "leg room"))
    F.notes.append("leg room 2 ends %.2f" % hub(["life-fitness-smith-machine", "life-fitness-smith-machine", "hammer-strength-glute-ham-reverse-hyper-combo"],
                                                -21.6, 4.4, 0, "leg room"))
    def lrow(pieces, x, yb, rot, gap=0.65):
        for p_ in pieces:
            w, d = G.footprint(p_)
            F.put(p_, x + w / 2, yb + (d / 2 if rot == 0 else -d / 2), rot, "leg extension island")
            x += w + gap
        return x
    LF, HS, PR = "life-fitness-insignia-series-leg-extension", "hammer-strength-select-leg-extension", "precor-resolute-series-leg-extension"
    F.notes.append("leg ext 1 ends %.2f" % lrow([LF, LF, PR, "hammer-strength-mts-kneeling-leg-curl"], -21.75, 9.4, 0))
    F.notes.append("leg ext 2 ends %.2f" % lrow([LF, HS, HS, "hammer-strength-select-hip-abduction", "hammer-strength-select-hip-adduction"], -21.75, 9.0, 180))   # one HS cut for the 0.65 m gaps

    # --- cardio on the river band: the seats by the glass, the treadmills behind (they see over them), a PWR Play island north
    y = -1.6
    for p_ in ["life-fitness-row-hx-trainer"] * 2 + ["life-fitness-club-series-upright-lifecycle-bike"] * 2 + ["life-fitness-ic7-indoor-cycle"] * 2:
        w, d = G.footprint(p_)
        F.put(p_, -7.05 - d / 2, y + w / 2, -90, "cardio")
        y += w + 0.75
    y = -1.8
    for p_ in ["woodway-4front"] * 4:
        w, d = G.footprint(p_)
        F.put(p_, -9.75 - d / 2, y + w / 2, -90, "cardio")
        y += w + 0.55
    # (Roman: "sub islands of the play station thing ... 2 modules or so on F1 and F2 ... for super setting")
    F.maze("f2", {"A": (0, 0), "B": (0, 1)},
           {("A", "W"): "pulldown", ("B", "W"): "pulldown", ("A", "E"): "row", ("B", "E"): "triceps",
            ("A", "S"): "step", ("B", "N"): "crossover", ("A", "N"): "dualhigh", ("B", "S"): "duallow"},
           [("A", "B")], origin=(-10.55, 5.9), zone="PWR Play island")

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

    auto_wipes(F, G, fixed, 16)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    print("  F2:", "; ".join(F.notes))
    F.write("gym_f2", ws, sps, {"fixed": fixed, "overhead": G.overhead("F2")},
            summary=["F2 · strength, zoned (2026-10-28: rooms within the room, partitions, ~15 % of the kit cut)",
                     "The spine: one clear walk from the pods to the cardio; every room opens off it.",
                     "West: the rack room (6 racks, a tall slat wall behind them), the pulling corner (2 half racks + deadlift), olympic (6 platforms).",
                     "Middle: the bench room (6 stations) + the dumbbell bay behind a low wall, the spiral, the leg hub, the leg room (tall wall).",
                     "River: the selectorized legs + the squat corner facing the ravine, cardio + a PWR Play island."])


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
        if it["kind"] == "floor_zone" and not it.get("label", "").startswith(("Walkway", "The pod's lifting platform")):
            continue                                   # (a wipes station may stand on a mat floor's edge, not in a walkway or on a platform)
        if it["kind"] == "pwr_meta":
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
    # zoned (Roman 2026-10-28: "artificial walls ... focus clusters ... so it isn't just a warehouse feel"; the partitions are building
    # walls, tools/interior.py ZONE_WALLS): the den behind a tall wall with its racks on it, the posterior chain room, the functional
    # room with the rig on its tall wall, a low wall down the sled lane; one spine from the grip wall to the north stair. Cut: 4 den
    # benches (+ the 2 off the old island), a GHD, a back extension, an iso shoulder press, a SkiErg, an air bike, a rower.
    # (the spiral + the sled lane split the floor: south of them the spine runs from the spiral's step-off to the grip wall, north of
    # them from the W1 walk to the north stair; the walkway down the mirror wall links the two)
    F.route("r-spine-s", [(-16.0, -20.3), (-16.0, -33.0)], "the spine south: the spiral's step-off to the grip wall + altitude", width=1.8)
    F.route("r-spine-n", [(-13.2, -12.6), (-13.2, 10.5)], "the spine north: past the maze to the north stair", width=1.8)
    F.route("r-w1", [(-27.4, -12.4), (-21.8, -12.4), (-20.5, -10.2), (-13.2, -10.2)], "in from the W1 stairs + lift, past the spiral to the spine", width=1.6)

    # --- the dumbbell den (Roman: "staggered rows so everyone has the optimal mirror positioning"): two rows facing the mirror wall,
    # the second in the first row's gaps; the dumbbells + kettlebells on the den's tall wall behind them, facing the benches
    benches = ["rogue-adjustable-bench-3-0"] * 12 + ["rogue-manta-ray-adjustable-bench"] * 2
    k = 0
    for x, y0 in ((-26.0, -31.9), (-23.6, -30.6)):
        for j in range(7):
            F.put(benches[k], x, y0 + 2.6 * j, 90, "dumbbell den", "facing the mirror; " + ("first row" if x < -25 else "second row: sees the mirror through the first row's gaps"))
            k += 1
    y = -31.6
    for p_, note in (("life-fitness-3-tier-accessory-rack", "LF cast iron kettlebells 4-32 kg"), ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 2.5-25 kg"),
                     ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 27.5-50 kg"), ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 52.5-75 kg"),
                     ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex, the doubles"), ("life-fitness-3-tier-accessory-rack", "HS competition kettlebells 8-32 kg")):
        w, d = G.footprint(p_)
        F.put(p_, -20.6 - 0.125 - d / 2, y + w / 2, 90, "dumbbell den", note + "; on the den's wall, facing the benches")
        y += w + 0.3
    F.put("rogue-freestanding-chalk-stand", -21.6, -18.9, 0, "dumbbell den")
    F.put("rogue-belt-and-band-hanger", XW + 0.155, -8.8, -90, "functional", "belts, straps, sleeves, wraps on loan; dip belts")
    # the grip wall on the south wall, either side of the altitude room's door
    for x in (-27.3, -20.6, -19.3, -18.0, -16.7):
        F.put("beastmaker-2000-series-hangboard", x, YS + 0.087, 0, "grip wall", "pinch blocks, cannonball grips, wrist roller hang beside")
    F.put("beastmaker-2000-series-hangboard", -24.9, YS + 0.087, 0, "grip wall")
    F.put("metolius-wood-grips-campus-rungs", -15.4, YS + 0.075, 0, "grip wall")
    # --- the posterior chain room (between the den's wall and the spine): GHDs, back extensions, the nordic curl, a glute drive
    for p_, x, y in (("hammer-strength-fixed-pad-glute-ham", -19.6, -30.5), ("hammer-strength-fixed-pad-glute-ham", -19.6, -27.4),
                     ("hammer-strength-fixed-pad-glute-ham", -19.6, -24.3), ("the-abs-company-the-nordic-curl", -19.6, -21.4),
                     ("hammer-strength-back-extension", -17.7, -30.7), ("hammer-strength-back-extension", -17.7, -27.9),
                     ("hammer-strength-plate-loaded-glute-drive", -17.75, -24.9)):
        F.put(p_, x, y, 0, "posterior chain")
    # --- the selectorized upper body beside the maze: back to back with the river row, facing the spine + the maze
    y = -11.8
    for p_ in ("hammer-strength-select-chest-press", "hammer-strength-select-chest-press", "hammer-strength-select-pectoral-fly-rear-deltoid",
               "hammer-strength-select-pectoral-fly-rear-deltoid", "select_shoulder", "select_shoulder"):
        if p_ == "select_shoulder":
            w, d = 1.35, 1.3
            F.items.append({"id": f"select-shoulder-{y:.1f}", "room": "upper beside the maze", "kind": "select_shoulder", "label": G.KINDS_FIXED["select_shoulder"]["label"],
                            "x": round(-10.45 - d / 2, 3), "y": round(y + w / 2, 3), "w": w, "d": d, "rot": 90})
        else:
            w, d = G.footprint(p_)
            F.put(p_, -10.45 - d / 2, y + w / 2, 90, "upper beside the maze", "facing the maze, its back to the river row")
        y += w + 0.9
    F.notes.append(f"upper column ends {y:.2f}")

    # --- the functional room (west, its own tall wall): the rig on the wall (rings, ropes, the parallel bars), wall balls + pegboard
    # on the mirror wall, the plyo boxes on its low north wall
    rig = F.put("rogue-monster-rig-2-0", -22.6 - 0.125 - 1.77 / 2 - 0.05, -6.2, 90, "functional", "on the functional room's tall wall: rings, climbing ropes, the parallel bars")
    F.notes.append("rig at %.2f" % rig["x"])
    F.put("rogue-rig-mount-parallel-bars", rig["x"], -6.2 + 1.0, 90, "functional", "on the rig, in its 49 in squat cell", on=rig["id"])
    F.put("rogue-10-bar-holder", -26.2, -8.5, 0, "functional", "the rig's bars")
    F.put("rogue-freestanding-chalk-stand", -25.0, -8.9, 0, "functional")
    F.zone("Open floor: classes, wall balls, plyo", -27.0, -9.2, -25.7, -3.6, "zone-open")
    F.put("life-fitness-escape-endura-wall-balls", XW + 0.405, -6.5, -90, "functional", "the targets above, the balls on the shelf")
    F.put("rogue-pine-maple-peg-board", XW + 0.12, -4.2, -90, "functional")
    yb = -3.0 - 0.125
    for x in (-26.55, -25.95, -25.35):
        F.put("hammer-strength-3-in-1-wood-plyo-box", x, yb - 0.38, 180, "functional", "a stack of three")
    F.put("hammer-strength-3-in-1-soft-plyo-box", -24.75, yb - 0.38, 180, "functional", "soft boxes stacked")
    F.put("rogue-monster-mass-storage", -24.0, -3.0 + 0.125 + 0.395, 0, "strongman", "slam balls, Sandbag 2.0s, medicine balls, battle ropes, jump ropes, AbMats, vests")
    F.put("life-fitness-vertical-medicine-ball-storage", -25.3, -3.0 + 0.125 + 0.3, 0, "strongman")

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

    # --- the plate-loaded upper hub between the maze and the spiral, its west end on the functional room's wall
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
        return x
    F.notes.append("hub A ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-bench-press", "tree", "hammer-strength-plate-loaded-iso-lateral-incline-press",
                                            "hammer-strength-plate-loaded-iso-lateral-shoulder-press"], -21.7, -7.5, 180))
    F.notes.append("hub B ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-row", "tree", "hammer-strength-plate-loaded-iso-lateral-front-lat-pulldown"],
                                           -21.7, -6.9, 0))

    # --- strongman (north-west): the carry lane down the mirror wall, the yoke at its head, the stones by the stair
    F.zone("Carry lane: yoke, farmers, sandbags (down the wall, 11 m)", XW, -0.2, -26.3, 11.0, "zone-carry")
    F.put("rogue-yoke", -27.75, 9.9, 180, "strongman", "carried south down the lane")
    F.put("rogue-farmers-walk-handles", -25.2, 9.2, 180, "strongman")
    F.put("titan-atlas-stone-platform", -22.95, 8.2, 90, "strongman", "loaded from the west")
    F.put("rogue-rubber-atlas-stones", -22.95, 5.9, 90, "strongman")
    F.put("rogue-strongman-sandbags", -25.2, 11.25, 180, "strongman", "25-400 lb along the north wall")
    F.put("rogue-10-bar-holder", -22.6, 11.3, 180, "strongman", "log, axle, the hex bars")
    F.put("hammer-strength-plate-loaded-t-bar-row", -24.4, 5.4, 0, "strongman", "T-bar row (the landmine pulls) by the strongman bays")
    F.put("rogue-freestanding-chalk-stand", -21.0, 1.6, 0, "the maze")
    F.put("rogue-echo-gym-timer-2-0", XW + 0.09, -1.2, -90, "strongman", "over the carry lane")
    F.put("life-fitness-barbell-rack", -9.1, 5.65, -90, "upper by the river", "the Hammer Strength fixed straight barbells")
    F.put("life-fitness-barbell-rack", -8.85, 8.0, -90, "upper by the river", "the Life Fitness 12-sided fixed EZ bars")

    # --- by the river (east of the sled lane's low wall): conditioning, then the upper selectorized, facing the water
    y = place_row(F, G, ["concept2-skierg"] * 2 + [None] + ["hammer-strength-hd-air-bike"] * 3 + [None] + ["life-fitness-row-hx-trainer"] * 3,
                  -8.4, -32.4, -90, 0.55, "conditioning by the river")
    y = place_row(F, G, [None, "hammer-strength-select-chest-press"] * 1 + ["hammer-strength-select-chest-press"] * 2 + [None]
                  + ["hammer-strength-select-pectoral-fly-rear-deltoid"] * 2 + [None, "hammer-strength-select-biceps-curl", "hammer-strength-seated-arm-curl",
                  None, "hammer-strength-plate-loaded-abdominal-oblique-crunch", "body-solid-gvkr60b-vertical-knee-raise-dip",
                  "gmwd-multi-functional-seal-row-bench-sr05"], -8.4, y + 0.4, -90, 0.7, "upper by the river")
    F.notes.append(f"river row ends {y:.2f}")
    F.put("hammer-strength-assisted-nordic-ham", -10.75, 8.0, 180, "by the river")

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

    auto_wipes(F, G, fixed, 16)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    print("  F3:", "; ".join(F.notes))
    F.write("gym_f3", ws, sps, {"fixed": fixed, "overhead": G.overhead("F3")},
            summary=["F3 · the den, zoned (2026-10-28: rooms within the room, partitions, ~10 % of the kit cut)",
                     "The spine: one clear walk from the grip wall to the north stair, beside the sled lane.",
                     "The dumbbell den: 14 benches in two staggered rows facing the mirror, the dumbbells + kettlebells on its tall wall.",
                     "The posterior chain room; the functional room with the rig on its tall wall; strongman + the carry lane; the PWR Play maze + the upper hub.",
                     "By the river, behind a low wall down the sled lane: SkiErgs, air bikes, rowers, then the selectorized upper body.",
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
    y = -19.3
    for p_ in ["life-fitness-club-series-recumbent-lifecycle-bike"] * 3 + ["life-fitness-club-series-upright-lifecycle-bike"] * 3:
        w, d = G.footprint(p_)
        F.put(p_, -15.0, y - w / 2, -90, "bikes behind the stepmills", "facing the river (the south glass is the calisthenics wall now)")
        y -= w + 0.75

    # --- the walking routes (1.7 m clear; nothing stands in them): in from the gallery down the river side (behind the treadmills)
    # and along the locker wall past the spiral to the W1 stair + lift; down the garden side to the W2 stair; along the bikes
    F.route("r-gallery-cardio", [(-9.55, -9.4), (-9.55, -33.0)], "in from the gallery, down the river side behind the treadmills")
    F.route("r-gallery-west", [(-10.4, -10.5), (-27.1, -10.5)], "in from the gallery along the locker wall: the spiral, the W1 stair + lift", width=1.6)
    F.route("r-garden-side", [(-26.3, -10.5), (-26.3, -29.0)], "down the garden side: the W2 stair, the mats, the calisthenics wall")

    # --- calisthenics along the south glass (Roman 2026-10-30: "take up the whole back wall or most of it ... without those
    # barriers"): the Monkey Rig with its back to the forest, two pull-up stations carrying the line east, the skills floor +
    # parallettes in front, the VKR + wall bars on the W2 core at the west end. No partitions: the open mats run straight into it
    mx = -27.0 + 7.493 / 2
    mr = F.put("rogue-monster-lite-monkey-rig-2-0", mx, YSF + 0.3 + 2.106 / 2, 180, "calisthenics", "back to the south glass: rings on the 2.47 m bars; the parallel bars on it")
    F.put("rogue-rig-mount-parallel-bars", mx + 3.07, mr["y"], 180, "calisthenics", "on the rig, in its east 43 in bay", on=mr["id"])
    F.put("body-solid-gvkr60b-vertical-knee-raise-dip", XWF + 0.5, -32.6, -90, "calisthenics", "its back to the W2 core, in the corner by the rig (clear of the AED)")
    for x in (-18.0, -15.2):   # 1.2 m apart (NSCA)
        F.items.append({"id": f"pullup-{x:+.2f}", "room": "calisthenics", "kind": "rig_spur", "label": G.KINDS_FIXED["rig_spur"]["label"],
                        "x": x, "y": round(YSF + 0.3 + 1.0, 3), "w": 1.6, "d": 0.18, "rot": 0,
                        "note": "pull-ups, chin-ups, hanging leg raises, muscle-ups: the rig's line carried east along the glass"})
    F.zone("Skills floor: handstands, levers, L-sits (gymnastics mat)", -25.4, -30.4, -19.9, -28.0, "zone-skills")
    for x in (-24.9, -23.8, -22.7, -21.6, -20.5, -19.4):
        F.put("rogue-bolt-together-parallette-set", x, -27.4, 0, "calisthenics", "L-sits, planche, push-ups")
    for y in (-17.75, -16.25, -14.75):
        F.put("gymleco-wooden-wall-bars-with-chins-rack", XWF + 0.315, y, -90, "calisthenics", "on the W1 core wall (the chin bar can't meet the 2.47 m rule)")
    F.put("gymleco-wooden-wall-bars-with-chins-rack", XWF + 0.315, -28.0, -90, "calisthenics", "on the W2 core wall")
    F.put("rogue-belt-and-band-hanger", -13.2, YNF - 0.155, 180, "calisthenics", "dip belts, bands")
    F.put("life-fitness-vertical-medicine-ball-storage", -20.9, -19.9, 180, "stretching", "beside the accessory racks")

    # --- stretching + mobility north of the calisthenics (the garden glass beside it): the mat floor, the kit round it
    F.zone("Open mat floor: stretching, mobility, small classes (mats from the racks)", -25.3, -23.6, -19.0, -20.5, "zone-mats")
    for x in (-23.5, -20.3, -17.1):   # all three on the north wall by the mat floor (2026-10-30: the W2 core is calisthenics + the AED)
        F.put("life-fitness-adjustable-wall-mounted-mat-rack", x, YNF - 0.135, 180, "stretching", "core + yoga mats")
    for x in (-24.0, -22.45):
        F.put("life-fitness-accessory-rack", x, -19.9, 180, "stretching", "foam rollers, bands, straps, blocks, massage balls, Theraguns")
    F.put("hammer-strength-stability-ball", -24.6, -21.9, 90, "stretching", "stability balls, BOSUs, balance + slant boards beside")
    F.put("life-fitness-flexibility-trainer", -18.2, -21.0, 90, "stretching")
    F.put("life-fitness-flexibility-trainer", -18.2, -23.0, 90, "stretching")

    auto_wipes(F, G, fixed, 8)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    F.write("gym_f1", ws, sps, {"fixed": fixed, "overhead": G.overhead("F1")},
            summary=["F1 · the hall (first proposal, 2026-10-26)",
                     "Cardio on the glass: 10 treadmills facing the river, the ellipticals, stepmills + VersaClimber behind, the bikes facing the forest.",
                     "Calisthenics along the south glass (2026-10-30, no partitions): the Monkey Rig + two pull-up stations facing the room, the skills floor + parallettes, wall bars on the cores.",
                     "Walking routes kept clear: in from the gallery, along the locker wall to the spiral + W1, down the garden side.",
                     "The body scanner is in the posing room on F2 (private)."])


def plan_annex(G):
    pass  # the pods are on gym_f2, the altitude room on gym_f3

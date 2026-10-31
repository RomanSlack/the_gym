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
    """F2 as rooms within the room (Roman 2026-10-28: "artificial walls ... focus clusters ... so it isn't just a warehouse feel").
    The partitions are building walls (tools/interior.py ZONE_WALLS). One spine runs north-south from the pods to the PWR Play, the
    rooms open off it.

    2026-10-31, after Roman walked it at eye level ("over half of all the placement ... is actually blocking a lot of things", "you
    literally have to phase through machines", "I don't think you're really taking into account the actual orientation of things"),
    rebuilt round access, checked by tools/gym_walk_sim.py (every piece reached without crossing anyone's training space):
    - every row has its backs to a wall or to another row, its users facing into an aisle; a plate-loaded machine keeps 0.6 m clear
      on the side you get on, a plate tree is never in that gap; every room has a clear way through (>= 1.5 m main, 0.9 m side)
    - the rack room stops a rack short: the opening by the spiral (half blocked by the stair) is now a 5.4 m forecourt
    - olympic: four platforms in one line facing the mirror, the aisle behind them, bumpers between (the inner line of the old two
      could only be reached across the outer); its west gap (onto the platforms' fronts) closed, in from the leg room's walk
    - the leg room: the leg extensions turned to face the room with their backs on the north wall, one island (smiths back to back
      with the calf machines, 0.6 m between), a 1.5 m walk down its west side to olympic, 1.5 m aisles either side of the island
    - the bench room: a 1.2 m aisle between the incline + flat rows (the trees stood in a 0.6 m one), the trees between the flats
    - the dumbbell bay: the racks on the racks wall's new mirror, the benches facing it, the rest of the bay open
    - no cardio on F2 (Roman: "people should just go run outside"): two stepmills by the legs for supersets, the PWR Play to the corner
    Cut: rack 6, the deadlift platform + its tree, 2 olympic platforms, 2 leg presses, a glute drive, a belt squat, an LF + an HS leg
    extension, an abduction + adduction, 3 adjustable benches, 4 treadmills, 2 rowers, 2 upright bikes, 2 IC7s."""
    F = G.Floor("F2", "F2 · strength: free weights, olympic, legs, the pods", [-30.5, -41.0, -5.4, 13.2])
    ws = G.walls("F2")
    ids = ["free-weights", "olympic", "cardio-F2", "machines-2", "machines", "spiral-F2", "posing", "pod-1", "pod-2", "pod-3"]
    F.room_ids, F.walls = ids, ws
    sps = G.spaces("F2", ids)
    room = G.room_poly("F2", ids)
    fixed = G.spiral_items("F2") + G.landings(ws, "F2", room) + [i for i in G.fixtures("F2") if i["kind"] != "wipe_station"]

    # --- the walking routes (nothing stands in them): the spine from the pods to the PWR Play; in from the W1 stairs + lift through
    # the forecourt, past the spiral; the south walk to the pods
    F.route("r-spine", [(-11.8, -33.0), (-11.8, 11.0)], "the spine: the pods to the PWR Play, every room opens off it", width=1.8)
    F.route("r-w1", [(-27.4, -12.05), (-21.9, -12.05), (-20.7, -10.3), (-12.7, -10.3)], "in from the W1 stairs + lift, through the forecourt, past the spiral to the spine", width=1.6)
    F.route("r-oly", [(-21.6, -1.6), (-21.6, 10.9)], "the leg room's west walk: olympic's two ways in", width=1.2)
    F.zone("Walkway: the W2 + W1 stairs, the WCs, the AED, the glass lift (keep it clear)", XW, -27.2, -27.0, -9.2)
    F.zone("South walk: the posing room + the three pods", -27.6, YS, -7.0, -32.05)

    # --- the rack room: five racks facing the mirror, their backs to a tall wall (its other face the dumbbell bay's mirror)
    plat = "titan-series-power-rack-lifting-platform"
    for k in range(5):
        y = -30.43 + 3.14 * k
        p_ = F.put(plat, -24.215, y, 90, "rack room", "rack platform: the lifter faces the mirror")
        r_ = F.put("rep-pr-5000-rack-builder", -23.59, y, 90, "rack room", "on its platform; spotter arms, landmine, dip, band pegs on some", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.3, y, 90, "rack room", "lives in the rack", on=r_["id"])
    F.put("rogue-freestanding-chalk-stand", -28.55, -32.9, 0, "rack room")
    # --- the pulling corner (off the forecourt, its own tall walls): the two half racks facing the mirror
    for y in (-9.9, -6.85):   # 1.2 m between the racks (NSCA 0.9)
        p_ = F.put("hammer-strength-rubber-platform", -24.685, y, 90, "pulling corner", "half rack platform")
        r_ = F.put("rogue-monster-half-rack", -24.56, y, 90, "pulling corner", "on its platform", on=p_["id"])
        F.put("rogue-flat-utility-bench-2-0", -24.9, y, 90, "pulling corner", "lives in the rack", on=r_["id"])
    F.put("rogue-belt-and-band-hanger", -22.4 - 0.06 - 0.155, -8.4, 90, "pulling corner", "belts, straps, sleeves, wraps on loan; the bands; on the slat wall (not the mirror)")
    F.put("rogue-freestanding-chalk-stand", -23.0, -4.2, 0, "pulling corner")

    # --- olympic: four platforms in one line facing the mirror, bumpers between them, the aisle behind them along the low wall
    w_, d_ = G.footprint("hammer-strength-impact-suppression-platform")
    px = XW + 1.2 + d_ / 2
    ys = [-3.0 + 0.06 + 0.5 + w_ / 2 + k * (w_ + 1.2) for k in range(4)]
    for y in ys:
        F.put("hammer-strength-impact-suppression-platform", px, y, 90, "olympic", "8 x 6 ft: the bar along y, the lifter faces the mirror")
    for a_, b_ in zip(ys, ys[1:]):   # (NSCA: the plates beside every platform)
        F.put("rogue-monster-bumper-rack", px, (a_ + b_) / 2, -90, "olympic", "bumpers + change plates, between two platforms, loaded from the aisle")
    F.put("rogue-10-bar-holder", -23.6, -2.57, 0, "olympic", "the Eleiko / Strencor / technique bars")
    for a_, b_ in (ys[0:2], ys[2:4]):
        F.put("rogue-freestanding-chalk-stand", px + d_ / 2 + 0.6 + 0.3, (a_ + b_) / 2, 0, "olympic")
    F.put("rogue-wood-jerk-blocks", px, ys[2], 90, "olympic", "set up on a platform", on="hammer-strength-impact-suppression-platform-3")
    F.put("titan-deadlift-pulling-blocks", px, ys[1], 90, "olympic", "on a platform", on="hammer-strength-impact-suppression-platform-2")
    F.put("rogue-echo-gym-timer-2-0", -25.3, -3.0 + 0.06 + 0.09, 0, "olympic", "on the tall south wall, in view of every platform (not on the mirror)")

    # --- the bench room: the inclines facing the mirrored wall north, the flats facing south, a 1.2 m aisle between their backs
    for x, p_ in zip((-21.0, -17.6, -14.2), ("atlantis-olympic-incline-bench-press-with-pivot-p338",) * 3):
        w, d = G.footprint(p_)
        F.put(p_, x, -25.06 - 0.65 - d / 2, 0, "bench room", "faces the mirrored wall")
    for x, p_ in zip((-21.0, -17.6, -14.2), ("atlantis-olympic-flat-bench-press-with-pivot-p337", "life-fitness-olympic-flat-bench", "life-fitness-olympic-flat-bench")):
        w, d = G.footprint(p_)
        F.put(p_, x, -29.16 - d / 2, 180, "bench room")   # 1.8 m behind the inclines: 1.2 m clear past both rows' 0.3 m
    F.put("life-fitness-olympic-weight-tree", -19.2, -29.95, 0, "bench room", "between the flats")
    F.put("life-fitness-olympic-weight-tree", -15.9, -29.95, 0, "bench room", "the Life Fitness flat benches have no horns: plates within 0.9 m (NSCA)")
    F.put("rogue-10-bar-holder", -21.8, -28.26, -90, "bench room", "power bars, women's bars, the specialty bars; at the aisle's end, 0.15 m off the mirror")

    # --- the dumbbell bay: the racks on the mirror (the racks wall's east face), the benches facing it, the bay open to the spine
    y = -24.7
    for p_, note in (("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 2.5-25 kg"), ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 27.5-50 kg")):
        w, d = G.footprint(p_)
        F.put(p_, -22.34 + 0.012 + 0.15 + d / 2, y + w / 2, -90, "dumbbell bay", note + "; in front of the mirror, 0.15 m off it (NSCA)")
        y += w + 0.1
    for y in (-24.3, -22.6, -19.7):   # a walk between the pair and the third, to the racks (four closed the racks off)
        F.put("rogue-adjustable-bench-3-0", -18.75, y, 90, "dumbbell bay", "facing the mirror, the dumbbells in front of it")

    # --- the river legs: the selectorized legs facing the ravine, in groups (calves, hamstrings, hips)
    row = ["hammer-strength-select-standing-calf", "life-fitness-insignia-series-calf-extension", "hammer-strength-plate-loaded-tibia-dorsi-flexion", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl", "W",
           "hammer-strength-select-hip-abduction", "hammer-strength-select-hip-adduction", "life-fitness-insignia-series-glute", None,
           "life-fitness-insignia-series-seated-leg-curl", "life-fitness-axiom-series-leg-curl"]
    def xf(p_):   # the fronts: 0.7 / 0.8 m of the user's space clear of the glass
        return -6.65 - (0.82 if G.P.get(p_, ("", "", (0.7,)))[2][0] > 0.75 else 0.72)
    y = -31.55
    for p_ in row:
        if p_ in (None, "W"):   # W: a bay at the glass for a wipes station, half way down the 20 m row
            y += 0.55 if p_ is None else 1.8
            continue
        w, d = G.footprint(p_)
        F.put(p_, xf(p_) - d / 2, y + w / 2, -90, "river legs")
        y += w + 0.62
    F.notes.append(f"river legs end at y {y:.2f}")
    # --- the squat corner at the river legs' north end: the hacks + the pendulum facing the river, trees between
    y = y + 0.4
    for p_ in ("hammer-strength-plate-loaded-hack-squat", "tree", "hammer-strength-plate-loaded-hack-squat", "tree", "hammer-strength-plate-loaded-pendulum-x-squat"):
        w, d = (0.84, 0.71) if p_ == "tree" else G.footprint(p_)
        if p_ == "tree":
            F.put("life-fitness-olympic-weight-tree", -8.5, y + w / 2, 90, "squat corner", "loaded from both sides")
        else:
            F.put(p_, xf(p_) - d / 2, y + w / 2, -90, "squat corner")
        y += w + 0.15
    F.notes.append(f"squat corner ends at y {y:.2f}")
    # --- the stepmills by the legs (Roman: "a random one or two stair-stepper machines over by ... the most clustered area of leg
    # equipments to let people power set"), the kneeling curl + the GHD, all facing the river
    y = place_row(F, G, ["stairmaster-8gx-stepmill"] * 2, -6.65 - 0.4, y + 0.8, -90, 0.62, "stepmills by the legs", "superset the legs without going up to F1")
    y = place_row(F, G, ["hammer-strength-glute-ham-reverse-hyper-combo"], -6.65 - 0.82, y + 0.4, -90, 0.75, "by the river")
    F.notes.append(f"stepmills + GHD end at y {y:.2f}")

    def hub(pieces, x0, yb, rot, zone):
        """A row of plate-loaded machines, backs on a wall at yb, a tree only where it leaves 0.6 m clear both sides."""
        x, prev = x0, None
        for p_ in pieces:
            w, d = (0.84, 0.71) if p_ == "tree" else G.footprint(p_)
            if prev is not None:
                x += 0.6 if "tree" in (p_, prev) else 0.9
            if p_ == "tree":
                F.put("life-fitness-olympic-weight-tree", x + w / 2, yb + (-0.36 if rot == 180 else 0.36), rot, zone, "0.6 m clear either side: you get on past it")
            else:
                F.put(p_, x + w / 2, yb + (-d / 2 if rot == 180 else d / 2), rot, zone)
            x += w
            prev = p_
        return x
    lp, gd, bs = "hammer-strength-plate-loaded-linear-leg-press", "hammer-strength-plate-loaded-glute-drive", "hammer-strength-plate-loaded-belt-squat"
    # --- the leg hub (between the forecourt and the legs wall): one row, backs on the wall, the floor in front open
    F.notes.append("leg hub ends %.2f" % hub([lp, "tree", gd, gd], -21.9, -2.36, 180, "leg hub"))
    kw_, kd_ = G.footprint("hammer-strength-mts-kneeling-leg-curl")      # its back to the walk in, facing the row across 1.6 m
    F.put("hammer-strength-mts-kneeling-leg-curl", -18.0, -9.45 + 0.5 + kd_ / 2, 0, "leg hub", "its back to the walk in from W1")
    # --- the leg room: a row on the legs wall, the leg extensions on the north wall facing the room, one island between
    F.notes.append("leg room south row ends %.2f" % hub([lp, "tree", bs], -20.3, -2.24, 0, "leg room"))
    LF, HS, PR = "life-fitness-insignia-series-leg-extension", "hammer-strength-select-leg-extension", "precor-resolute-series-leg-extension"
    x = -20.5
    for p_ in (LF, LF, PR, HS):   # (Roman: "rotate that entire row 180 degrees and then push it up against the wall")
        w, d = G.footprint(p_)
        F.put(p_, x + w / 2, YN - 0.05 - d / 2, 180, "leg room", "its back on the north wall, facing the room")
        x += w + 0.65
    F.notes.append(f"leg extensions end {x:.2f}")
    sm, sd = G.footprint("life-fitness-smith-machine")
    ys_ = 9.54 - 1.5 - 1.0 - sd / 2                                   # the north aisle 1.5 m clear of both rows' spaces
    x = -20.3
    for _ in range(2):
        F.put("life-fitness-smith-machine", x + sm / 2, ys_, 0, "leg room island", "facing north; 0.9 m to the calf machines behind (NSCA)")
        x += sm + 0.9
    yb = ys_ - sd / 2 - 0.9
    F.notes.append("island south half ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-leg-extension", "tree", "atlantis-incline-calf-raise-m318",
                                                      "hammer-strength-plate-loaded-seated-calf-raise"], -20.25, yb, 180, "leg room island"))

    # --- the PWR Play island in the north-east corner (Roman: "sub islands of the play station thing ... for super setting")
    F.maze("f2", {"A": (0, 0), "B": (0, 1)},
           {("A", "W"): "pulldown", ("B", "W"): "pulldown", ("A", "E"): "row", ("B", "E"): "triceps",
            ("A", "S"): "step", ("B", "N"): "crossover", ("A", "N"): "dualhigh", ("B", "S"): "duallow"},
           [("A", "B")], origin=(-9.3, round(y + 0.3 + 0.7 + 0.51 + 0.465, 2)), zone="PWR Play island")   # (clear of the W3 door's landing)

    # --- the three pods (south annex): the half rack on the flush platform facing the mirror (east wall), a bench, the dumbbells
    for k, (a_, b_) in enumerate([(-22.6, -17.2), (-17.2, -11.8), (-11.8, -6.45)]):
        xa, xb = a_ + 0.075, (b_ - 0.075 if k < 2 else b_ - 0.2)
        cx = (xa + 0.5 + xb) / 2
        fixed.append({"id": f"pod{k + 1}-platform", "room": "", "kind": "floor_zone", "label": "The pod's lifting platform (built, flush): oak centre, rubber drop zones",
                      "x": round(cx, 3), "y": -38.33, "w": 2.44, "d": 2.44, "rot": 0, "fixed": True})
        F.put("rogue-monster-lite-half-rack", cx - 0.25, -38.33, -90, f"pod {k + 1}", "on the pod's platform, the lifter facing the mirror wall")
        F.put("rogue-adjustable-bench-3-0", cx - 0.6, -36.4, -90, f"pod {k + 1}")
        F.put("hammer-strength-three-tier-dumbbell-rack", xb - 0.46 - 0.16, -35.75, 90, f"pod {k + 1}", "Hammer Strength urethane 5-75 lb; the mirror behind it, 0.15 m off (NSCA)")

    # --- the posing room: the body scanner in its south-west corner (private: scans are done in underwear), out of the stage's light
    fixed += [{"id": "posing-stage", "room": "", "kind": "keep_clear", "label": "The posing stage + its rig (built)",
               "pts": [[-26.26, -38.025], [-24.46, -38.025], [-24.46, -36.225], [-26.26, -36.225]], "fixed": True},
              {"id": "posing-mirror", "room": "", "kind": "keep_clear", "label": "The posing room's mirror wall + the viewing space before it (built)",
               "pts": [[-23.9, -39.9], [-22.675, -39.9], [-22.675, -34.35], [-23.9, -34.35]], "fixed": True}]
    F.put("fit3d-proscanner", -27.8, -38.85, 0, "posing room", "the body scanner: private (scans are taken in underwear), beside the stage")

    auto_wipes(F, G, fixed, 22)   # (a cap: wall spots first, every piece within 7.5 m (the vendors: 7.6-15 m, one per ~46 m²))
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    print("  F2:", "; ".join(F.notes))
    F.write("gym_f2", ws, sps, {"fixed": fixed, "overhead": G.overhead("F2")},
            summary=["F2 · strength, zoned; rebuilt round access 2026-10-31 (tools/gym_walk_sim.py: no piece reached through another's training space)",
                     "The spine: one clear walk from the pods to the PWR Play; every room opens off it; the forecourt by the W1 doors.",
                     "West: the rack room (5 racks), the pulling corner (2 half racks), olympic (4 platforms in a line, the aisle behind).",
                     "Middle: the bench room (6 stations, a 1.2 m aisle) + the dumbbell bay on a mirror, the spiral, the leg hub, the leg room (1 island).",
                     "River: the selectorized legs + the squat corner, two stepmills, the kneeling curl + GHD; the PWR Play in the corner. No cardio."])


def wipes(F, G, lvl, spots):
    for x, y_, r in spots:
        F.items.append({"id": f"wipes-{lvl}-{x}-{y_}", "room": "", "kind": "wipe_station", "label": G.KINDS_FIXED["wipe_station"]["label"],
                        "x": x, "y": y_, "w": 0.36, "d": 0.36, "rot": r})


def auto_wipes(F, G, fixed, n, reach=7.5, spacing=3.5):
    """n wipes stations (Roman 2026-10-26: "need like 3 times the wipe stations"), every piece within `reach` m of one. Where
    (2026-10-31, Roman: "wipe locations are literally blocking machines ... wipes should always be closer to walls if they can"):
    against a wall or a partition, a corner first; never in anyone's training space (the whole use clearance: in front, the
    loading sides, behind), a route, a landing or a door, a walkway or a platform. Only a piece no wall spot
    reaches gets an island one, tucked against the back of a piece. Never two closer than `spacing`."""
    import math
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import nearest_points, unary_union
    kinds = G.kinds_for({it["kind"] for it in F.items if it["kind"] in G.SIZES})
    kinds.update({k_: v for k_, v in G.KINDS_FIXED.items() if k_ not in kinds})
    room = unary_union([Polygon(s_["poly"]) for s_ in G.M["spaces"] if s_["level"] == F.level and s_["id"] in F.room_ids])
    wl = [LineString([w["from"], w["to"]]).buffer(w["size"][0] / 2, cap_style=2) for w in F.walls]
    walls = unary_union(wl)
    room = room.difference(walls)
    z = G.LV[F.level]
    occ, eq, bodies = [], [], []          # (a wipes bin may stand at a mirror's foot: the training spaces in front of it are kept clear anyway)
    for it in F.items + fixed:
        if it["kind"] == "floor_zone" and not it.get("label", "").startswith(("Walkway", "The pod's lifting platform", "Muscle-up")):
            continue
        if it["kind"] in ("pwr_meta", "pwr_bar"):
            continue
        if it["kind"] == "route":
            occ.append(LineString(it["pts"]).buffer(it.get("width", 1.7) / 2)); continue
        p_ = G.item_poly(it, kinds)
        if p_ is None:
            continue
        occ.append(p_)
        u = G.item_poly(it, kinds, use=True) if not it.get("fixed") else None
        if u is not None:
            occ.append(u)
        if it["kind"] not in ("floor_zone", "keep_clear", "void", "stair", "den_river", "turf"):
            bodies.append(p_)
        if not it.get("fixed") and it["kind"] in kinds and kinds[it["kind"]].get("mat") not in ("storage", "wallkit", "fixture", "platform") or it["kind"].startswith("pwr_core"):
            eq.append(p_.centroid)
    free = room.buffer(-0.19).difference(unary_union(occ).buffer(0.19))
    snug = unary_union(bodies)
    x0, y0, x1, y1 = free.bounds
    cands = [Point(x0 + 0.2 * i, y0 + 0.2 * j) for i in range(int((x1 - x0) / 0.2) + 1) for j in range(int((y1 - y0) / 0.2) + 1)]
    cands = [c for c in cands if free.contains(c)]
    def wall_n(c):
        return sum(1 for w in wl if c.distance(w) < 0.3)
    on_wall = []                                                   # along every wall's faces, 0.2 m out (the bin's centre)
    for w in F.walls:
        (ax, ay), (bx, by) = w["from"], w["to"]; L_ = math.hypot(bx - ax, by - ay)
        if L_ < 0.4:
            continue
        ux, uy = (bx - ax) / L_, (by - ay) / L_
        for sg in (1, -1):
            o_ = w["size"][0] / 2 + 0.2
            for k in range(int(L_ / 0.2) + 1):
                c = Point(ax + ux * k * 0.2 - uy * sg * o_, ay + uy * k * 0.2 + ux * sg * o_)
                if free.contains(c):
                    on_wall.append(c)
    occ_u = unary_union(occ + [walls])
    def across(c):   # the narrowest way across the floor through c (an aisle's width): rays both ways along x, y and the diagonals
        best = 99.0
        for dx, dy in ((1, 0), (0, 1), (0.707, 0.707), (0.707, -0.707)):
            tot = 0.0
            for sg in (1, -1):
                ray = LineString([(c.x, c.y), (c.x + sg * dx * 6, c.y + sg * dy * 6)])
                hit = ray.intersection(occ_u)
                tot += 6.0 if hit.is_empty else c.distance(hit)
            best = min(best, tot)
        return best
    island = [c for c in cands if wall_n(c) == 0 and c.distance(snug) < 0.65 and across(c) > 1.9]   # tucked behind a piece, never in an aisle
    picks = []
    def cover(c, pool):
        return sum(1 for e in pool if e.distance(c) <= reach)
    for _ in range(n):
        unc = [e for e in eq if min([e.distance(p_) for p_ in picks] or [99]) > reach]
        best, key = None, None
        for c in on_wall:
            if any(c.distance(p_) < spacing for p_ in picks):
                continue
            far = [e for e in eq if min([e.distance(p_) for p_ in picks] or [99]) > reach / 2]
            k_ = (cover(c, unc), cover(c, far), min(wall_n(c), 2))
            if k_[0] + k_[1] and (key is None or k_ > key):
                best, key = c, k_
        if (best is None or key[0] == 0) and unc:                  # a piece no wall spot reaches: an island spot
            for c in island:
                if any(c.distance(p_) < spacing for p_ in picks):
                    continue
                k_ = (cover(c, unc), -round(c.distance(snug), 1))
                if k_[0] and (key is None or (k_[0], 0, 0) > key):
                    best, key = c, (k_[0], 0, 0)
        if best is None:
            break
        picks.append(best)
    for c in picks:
        wp = nearest_points(c, walls)[1]
        if c.distance(walls) < 0.3:                                  # its front away from the wall
            rot = round(math.degrees(math.atan2(-(c.x - wp.x), c.y - wp.y)) / 90) * 90
        else:                                                        # its back to the piece it stands against
            bp = nearest_points(c, snug)[1]
            rot = round(math.degrees(math.atan2(-(c.x - bp.x), c.y - bp.y)) / 90) * 90
        F.items.append({"id": f"wipes-{F.level}-{c.x:.1f}-{c.y:.1f}", "room": "", "kind": "wipe_station", "label": G.KINDS_FIXED["wipe_station"]["label"],
                        "x": round(c.x, 2), "y": round(c.y, 2), "w": 0.36, "d": 0.36, "rot": rot, "note": "wipes + spray + bin"})
    far = [e for e in eq if min([e.distance(p_) for p_ in picks] or [99]) > reach]
    print(f"  {F.level}: {len(picks)} wipes stations ({sum(1 for c in picks if wall_n(c))} on walls); {len(far)} pieces further than {reach} m from one")


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
    fixed += [{"id": "sled-lane", "room": "", "kind": "turf", "label": "Sled lane: 15 m of sled turf from the south wall (built; it stops short of the spiral's low first turn)", "x": -13.2, "y": -26.425, "w": 2.4, "d": 14.85, "rot": 0, "fixed": True},
              {"id": "carry-lane", "room": "", "kind": "turf", "label": "Carry lane: 12 m of turf for the yoke, farmers + sandbag carries (built)", "x": -25.0, "y": 4.4, "w": 2.4, "d": 12.4, "rot": 0, "fixed": True},
              {"id": "den-river", "room": "", "kind": "den_river", "label": G.KINDS_FIXED["den_river"]["label"],
               "pts": [[-8.25, -33.85], [-6.65, -33.85], [-6.65, 11.85], [-8.25, 11.85]], "fixed": True},
              {"id": "north-stair", "room": "", "kind": "stair", "label": "The stair down to F4 (its flights + the spine wall between them, glass guards round the opening)", "pts": [[-21.45, 8.3], [-15.45, 8.3], [-15.45, 11.85], [-21.45, 11.85]], "fixed": True},
              {"id": "clear-N34-landing", "room": "", "kind": "keep_clear", "label": "Keep clear: the stair's landing on F3 (up from the pool)", "pts": [[-21.45, 6.5], [-15.45, 6.5], [-15.45, 8.3], [-21.45, 8.3]], "fixed": True}]
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

    # --- the dumbbell den (Roman: "staggered rows so everyone has the optimal mirror positioning"), turned round 2026-10-31 (Roman: "it
    # is just kind of awkward that it's facing the bathrooms and a bunch of doors ... rotated the full thing 180 degrees and then made
    # the whole back wall mirrors ... the dumbbell racks on the mirrors"): the den's tall wall is mirror now, the dumbbells +
    # kettlebells along its foot, the benches face it in two staggered rows, the ends cut (14 -> 11); behind them a 1 m walk on to
    # the W stairs + WCs
    xr1, xr2 = -23.685, -25.675   # (1.2 m from the dumbbells to the first row's benches)
    for y in (-31.0, -28.3, -25.6, -22.9, -20.2):
        F.put("rogue-adjustable-bench-3-0", xr1, y, -90, "dumbbell den", "facing the den's mirror wall, the dumbbells in front of it; first row")
    for y in (-29.65, -26.95, -24.25, -21.55):
        F.put("rogue-adjustable-bench-3-0", xr2, y, -90, "dumbbell den", "second row: sees the mirror through the first row's gaps")
    for y in (-17.6, -15.6):
        F.put("rogue-manta-ray-adjustable-bench", -24.5, y, 90, "dumbbell den", "north of the den wall, facing the west mirror")
    y = -31.6
    for p_, note in (("life-fitness-3-tier-accessory-rack", "LF cast iron kettlebells 4-32 kg"), ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 2.5-25 kg"),
                     ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 27.5-50 kg"), ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex 52.5-75 kg"),
                     ("hammer-strength-three-tier-dumbbell-rack", "Rogue rubber hex, the doubles"), ("life-fitness-3-tier-accessory-rack", "HS competition kettlebells 8-32 kg")):
        w, d = G.footprint(p_)
        F.put(p_, -20.6 - 0.06 - 0.012 - 0.15 - d / 2, y + w / 2, 90, "dumbbell den", note + "; along the mirror's foot, 0.15 m off it, facing the benches")
        y += w + 0.3
    F.put("rogue-freestanding-chalk-stand", -28.6, -32.8, 0, "grip wall", "by the grip wall (it stood in the den's north way out)")
    F.put("rogue-belt-and-band-hanger", XW + 0.155, -8.8, -90, "functional", "belts, straps, sleeves, wraps on loan; dip belts")
    # the grip wall on the south wall, either side of the altitude room's door
    for x in (-27.3, -20.6, -19.3, -18.0, -16.7):
        F.put("beastmaker-2000-series-hangboard", x, YS + 0.087, 0, "grip wall", "pinch blocks, cannonball grips, wrist roller hang beside")
    F.put("beastmaker-2000-series-hangboard", -24.9, YS + 0.087, 0, "grip wall")
    F.put("metolius-wood-grips-campus-rungs", -15.4, YS + 0.075, 0, "grip wall")
    # --- the posterior chain room (between the den's wall and the spine): GHDs, back extensions, the nordic curl, a glute drive
    for p_, x, y in (("hammer-strength-fixed-pad-glute-ham", -19.8, -30.5), ("hammer-strength-fixed-pad-glute-ham", -19.8, -27.4),
                     ("hammer-strength-fixed-pad-glute-ham", -19.8, -24.3), ("the-abs-company-the-nordic-curl", -19.8, -21.4),
                     ("hammer-strength-back-extension", -17.7, -30.7), ("hammer-strength-back-extension", -17.7, -27.9)):   # (the glute drive cut: it sat on the spine; F2 has two)
        F.put(p_, x, y, 0, "posterior chain")
    # --- the functional room (west, its own tall wall): the rig on the wall (rings, ropes, the parallel bars), wall balls + pegboard
    # on the mirror wall, the plyo boxes on its low north wall
    rig = F.put("rogue-monster-rig-2-0", -22.6 - 0.06 - 0.012 - 0.15 - 1.77 / 2, -6.2, 90, "functional", "on the functional room's tall wall: rings, climbing ropes, the parallel bars")
    F.notes.append("rig at %.2f" % rig["x"])
    F.put("rogue-rig-mount-parallel-bars", rig["x"], -6.2 + 1.0, 90, "functional", "on the rig, in its 49 in squat cell", on=rig["id"])
    F.put("rogue-10-bar-holder", XW + 0.33, -7.7, -90, "functional", "the rig's bars; on the west wall (it stood in the room's way in)")
    F.put("rogue-freestanding-chalk-stand", -25.0, -8.9, 0, "functional")
    F.zone("Open floor: classes, wall balls, plyo", -27.0, -9.2, -25.7, -3.6, "zone-open")
    F.put("life-fitness-escape-endura-wall-balls", XW + 0.405, -6.5, -90, "functional", "the targets above, the balls on the shelf")
    pb = F.put("rogue-pine-maple-peg-board", XW + 0.12, -4.2, -90, "functional", "hung with its foot at 2.0 m (it was 0.75): you start from a hang, feet off the mat, and climb to 4.3 m")
    pb["lift"] = 1.25
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
             ("A", "S"): "powerpivot", ("B", "S"): "triceps", ("E", "N"): "stallbars", ("F", "N"): None,   # (F N: its row's seat faced the stair opening, no way in)
             ("A", "E"): "crossover", ("B", "W"): "crossover", ("C", "E"): "dualhigh", ("D", "W"): "duallow",
             ("E", "E"): "ropepull", ("F", "W"): "handles",
             ("A", "N"): "crossover", ("C", "S"): "crossover", ("C", "N"): "dip", ("E", "S"): "step",
             ("B", "N"): "dualhigh", ("D", "S"): "duallow", ("D", "N"): "crossover", ("F", "S"): "crossover"}
    bars = [("A", "B"), ("C", "D"), ("E", "F"), ("A", "C"), ("C", "E"), ("B", "D"), ("D", "F")]
    F.maze("den", cores, faces, bars, origin=(-20.0, -1.9), zone="the maze")

    # --- the plate-loaded upper hub between the maze and the spiral, its west end on the functional room's wall
    def hub(pieces, x0, yb, rot):   # (2026-10-31: a tree leaves 0.6 m either side, you get on past it)
        x, prev = x0, None
        for p_ in pieces:
            w, d = (0.84, 0.71) if p_ == "tree" else G.footprint(p_)
            if prev is not None:
                x += 0.6 if "tree" in (p_, prev) else 0.9
            if p_ == "tree":
                F.put("life-fitness-olympic-weight-tree", x + w / 2, yb + (-0.36 if rot == 180 else 0.36), rot, "upper hub")
            else:
                F.put(p_, x + w / 2, yb + (-d / 2 if rot == 180 else d / 2), rot, "upper hub")
            x += w
            prev = p_
        return x
    F.notes.append("hub A ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-bench-press", "tree", "hammer-strength-plate-loaded-iso-lateral-incline-press"], -21.7, -7.125, 180))
    F.notes.append("hub B ends %.2f" % hub(["hammer-strength-plate-loaded-iso-lateral-row", "tree", "hammer-strength-plate-loaded-iso-lateral-front-lat-pulldown"],
                                           -21.7, -6.675, 0))   # (backs 0.45 apart: their space is in front, and not a short cut)

    # --- strongman (north-west) round its carry lane (2026-10-31, Roman: "the area to the west of the PlayStation ... kind of an empty
    # area"; the lane was only drawn, the floor read empty): 12 m of turf through the middle of it, the yoke at its head, the stones
    # + their platform along its east side, the farmers + the T-bar row on the walk down the west wall
    F.put("rogue-yoke", -25.0, 8.6, 180, "strongman", "at the carry lane's head: carried south down the turf")
    F.put("rogue-farmers-walk-handles", -27.9, 9.0, 180, "strongman", "beside the lane's head")
    F.put("titan-atlas-stone-platform", -22.6, 7.6, 90, "strongman", "loaded from the turf side")
    F.put("rogue-rubber-atlas-stones", -22.6, 5.4, 90, "strongman")
    F.put("rogue-strongman-sandbags", -25.0, 11.25, 180, "strongman", "25-400 lb along the north wall, at the lane's head")
    F.put("rogue-10-bar-holder", -27.6, 11.3, 180, "strongman", "log, axle, the hex bars; on the north wall by the farmers")
    F.put("hammer-strength-plate-loaded-t-bar-row", -28.0, 3.6, -90, "strongman", "T-bar row (the landmine pulls), its back to the west wall")
    F.put("rogue-freestanding-chalk-stand", -21.0, 1.6, 0, "the maze")
    F.put("rogue-echo-gym-timer-2-0", XW + 0.09, -1.2, -90, "strongman", "over the carry lane")
    # --- by the river: one row of the selectorized upper body facing the water (2026-10-31, Roman: "the machines are a little too
    # close to the water ... if you have to enter them from the front it's just kind of impossible"; the second column back to back
    # with it is gone): their fronts 1.6 m off the river's edge (0.7 m their own, a 0.9 m walk along the water), their backs to the
    # sled lane's low wall; a bay half way for the wipes. No cardio here now (Roman: "get rid of all the cardio machines on floors
    # that aren't floor one"). Cut: the chest press in the walk by the spiral, a chest press, a pec fly, the SkiErgs, air bikes, rowers
    CP, PF = "hammer-strength-select-chest-press", "hammer-strength-select-pectoral-fly-rear-deltoid"
    ISH = "hammer-strength-plate-loaded-iso-lateral-shoulder-press"
    y = -31.1
    for p_ in [CP, CP, CP, None, PF, PF, PF, "W", ISH, "tree", None, "hammer-strength-select-biceps-curl", "hammer-strength-seated-arm-curl",
               None, "hammer-strength-plate-loaded-abdominal-oblique-crunch", "body-solid-gvkr60b-vertical-knee-raise-dip", "gmwd-multi-functional-seal-row-bench-sr05"]:
        if p_ in (None, "W"):
            y += 0.4 if p_ is None else 1.2
            continue
        f_ = 0.8 if p_ in ("hammer-strength-plate-loaded-abdominal-oblique-crunch", ISH) else 0.7
        xf = -8.25 - 0.9 - f_
        if p_ == "tree":
            w, d = 0.84, 0.71
            F.put("life-fitness-olympic-weight-tree", xf - d / 2, y + w / 2, -90, "upper by the river", "the iso shoulder's plates")
        else:
            w, d = G.footprint(p_)
            F.put(p_, xf - d / 2, y + w / 2, -90, "upper by the river", "facing the water, a walk in front of it")
        y += w + 0.7
    F.notes.append(f"river row ends {y:.2f}")
    for yb_, note in ((y + 0.2, "the Hammer Strength fixed straight barbells"), (y + 1.6, "the Life Fitness 12-sided fixed EZ bars")):
        F.put("life-fitness-barbell-rack", -8.25 - 0.1 - 0.54, yb_, 90, "upper by the river", note + "; its back to the river")
    F.put("hammer-strength-assisted-nordic-ham", -10.75, 8.0, 180, "by the river")

    # --- the sled lane: the sleds parked at its ends, the harnesses on mass storage by its south end
    for y in (-33.1, -32.0):
        pass
    F.put("life-fitness-push-pull-weight-sled", -13.9, -32.9, 0, "sled lane", "parked at the start line")
    F.put("life-fitness-push-pull-weight-sled", -12.6, -32.9, 0, "sled lane", "parked at the start line")
    F.put("life-fitness-push-pull-weight-sled", -13.9, -19.7, 180, "sled lane", "parked at the far end")
    F.put("life-fitness-acft-sled-with-strap", -12.6, -20.3, 180, "sled lane", "parked at the far end")
    F.put("life-fitness-acft-sled-with-strap", -12.6, -30.6, 0, "sled lane", "parked at the start line")
    F.put("rogue-monster-mass-storage", -10.2, -33.16, -90, "sled lane", "harnesses, cones, hurdles, the agility ladder; by the lane's start, its back to the turf")

    # --- the altitude room (south annex): bikes in front, treadmills + rowers behind, all facing the display on the west wall
    fixed.append({"id": "airlock", "room": "", "kind": "keep_clear", "label": "The altitude room's airlock (built)",
                  "pts": [[-23.95, -36.4], [-20.95, -36.4], [-20.95, -34.35], [-23.95, -34.35]], "fixed": True})
    place_row(F, G, ["life-fitness-ic7-indoor-cycle", "life-fitness-club-series-upright-lifecycle-bike", "life-fitness-club-series-upright-lifecycle-bike",
                     "life-fitness-ic7-indoor-cycle"], -26.2, -39.55, 90, 0.6, "altitude", "facing the altitude display")
    # (2026-10-31: a rower cut, a 1.2 m walk between the treadmills: the sim had everyone squeezing between them)
    place_row(F, G, ["life-fitness-row-hx-trainer", "woodway-4front"], -20.4, -39.55, 90, 0.9, "altitude", "facing the altitude display")
    place_row(F, G, ["woodway-4front"], -20.4, -39.55 + 0.57 + 0.9 + 0.89 + 1.2, 90, 0.9, "altitude", "facing the altitude display")

    auto_wipes(F, G, fixed, 20)
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
    # (Roman 2026-10-31: "add three more stair-stepper machines and get rid of three elliptical machines"); 0.1 m further back so the
    # treadmills' 2 m run-off behind them stays clear of the ellipticals' own space
    place_row(F, G, ["life-fitness-club-series-elliptical-cross-trainer"] * 4 + [None] + ["stairmaster-8gx-stepmill"] * 6 + ["versaclimber-ts-magnetic"],
              -10.85, -33.55, -90, 0.5, "cardio by the river")

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
    F.route("r-gallery-cardio", [(-9.8, -9.4), (-9.8, -33.0)], "in from the gallery, down the river side behind the treadmills (in their run-off, clear of their users)", width=1.4)
    F.route("r-gallery-west", [(-10.4, -10.5), (-27.1, -10.5)], "in from the gallery along the locker wall: the spiral, the W1 stair + lift", width=1.6)
    F.route("r-garden-side", [(-26.3, -10.5), (-26.3, -29.0)], "down the garden side: the W2 stair, the mats, the calisthenics wall")

    # --- calisthenics along the south glass (Roman 2026-10-30: "take up the whole back wall or most of it ... without those
    # barriers"): the Monkey Rig with its back to the forest, two pull-up stations carrying the line east, the skills floor +
    # parallettes in front, the VKR + wall bars on the W2 core at the west end. No partitions: the open mats run straight into it
    mx = -26.6 + 7.493 / 2   # (0.4 m east of the W2 core: the AED's access space)
    mr = F.put("rogue-monster-lite-monkey-rig-2-0", mx, YSF + 1.4 + 2.106 / 2, 180, "calisthenics", "1.4 m off the south glass (a kip on its outer bar swung into the glass at 0.3 m): rings on the 2.47 m bars; the parallel bars on it")
    F.put("rogue-rig-mount-parallel-bars", mx + 3.07, mr["y"], 180, "calisthenics", "on the rig, in its east 43 in bay", on=mr["id"])
    F.put("body-solid-gvkr60b-vertical-knee-raise-dip", XWF + 0.5, -32.6, -90, "calisthenics", "its back to the W2 core, in the corner by the rig (clear of the AED)")
    # the two muscle-up bars (Roman 2026-10-31: "the pull-up bars we have restrict muscle-ups ... we really want that to be
    # highlighted"): the bar on top of its uprights, nothing above it (the old station's crossmember ran 0.27 m over the bar), the
    # swing kept clear 1.8 m in front and behind, 1.2 m between them (NSCA), on their own mat; no wipes or anything between them
    ymu = round(YSF + 1.9, 3)
    F.zone("Muscle-up bars: 1.8 m swing clear front + back, nothing over the bars (gymnastics mat)", -18.5, YSF, -13.7, round(ymu + 1.85, 3), "zone-muscle-up")
    for x in (-17.5, -14.7):
        F.items.append({"id": f"muscleup-{x:+.2f}", "room": "calisthenics", "kind": "rig_spur", "label": G.KINDS_FIXED["rig_spur"]["label"],
                        "x": x, "y": ymu, "w": 1.6, "d": 0.18, "rot": 0,
                        "note": "muscle-ups, pull-ups, toes-to-bar: the bar on top of its uprights, nothing above it"})
    F.zone("Skills floor: handstands, levers, L-sits (gymnastics mat)", -25.4, -29.1, -19.9, -26.7, "zone-skills")
    for x in (-24.6, -23.5, -22.4, -21.3, -20.2, -19.1):
        F.put("rogue-bolt-together-parallette-set", x, -26.2, 0, "calisthenics", "L-sits, planche, push-ups")
    for y in (-17.75, -16.25, -14.75):
        F.put("gymleco-wooden-wall-bars-with-chins-rack", XWF + 0.315, y, -90, "calisthenics", "on the W1 core wall (the chin bar can't meet the 2.47 m rule)")
    for y in (-28.05, -27.1):   # (Roman: "there's none over by the calisthenics area ... where they are right now ... is right in front of the stairs")
        F.put("life-fitness-adjustable-wall-mounted-mat-rack", XWF + 0.1, y, -90, "calisthenics", "core + yoga mats, by the skills floor + the rig")
    F.put("rogue-belt-and-band-hanger", -13.2, YNF - 0.155, 180, "calisthenics", "dip belts, bands")
    F.put("life-fitness-vertical-medicine-ball-storage", -20.2, -19.9, 180, "stretching", "beside the accessory racks, a walk between")

    # --- stretching + mobility north of the calisthenics (the garden glass beside it): the mat floor, the kit round it
    F.zone("Open mat floor: stretching, mobility, small classes (mats from the racks)", -25.3, -23.6, -19.0, -20.5, "zone-mats")
    for x in (-24.0, -22.45):
        F.put("life-fitness-accessory-rack", x, -19.9, 180, "stretching", "foam rollers, bands, straps, blocks, massage balls, Theraguns")
    F.put("hammer-strength-stability-ball", -24.6, -22.6, 90, "stretching", "stability balls, BOSUs, balance + slant boards beside")
    F.put("life-fitness-flexibility-trainer", -18.2, -21.0, 90, "stretching")
    F.put("life-fitness-flexibility-trainer", -18.2, -23.0, 90, "stretching")

    auto_wipes(F, G, fixed, 10)
    for it in F.items:
        if it["kind"] in G.SIZES:
            F.targets[it["kind"]] = F.targets.get(it["kind"], 0) + 1
    F.write("gym_f1", ws, sps, {"fixed": fixed, "overhead": G.overhead("F1")},
            summary=["F1 · the hall (first proposal, 2026-10-26)",
                     "Cardio on the glass: 12 treadmills facing the river, 4 ellipticals, 6 stepmills + the VersaClimber behind, the bikes.",
                     "Calisthenics along the south glass: the Monkey Rig, two muscle-up bars (nothing over them, 1.8 m swing clear), the skills floor + parallettes, mat racks + wall bars on the cores.",
                     "Walking routes kept clear: in from the gallery, along the locker wall to the spiral + W1, down the garden side.",
                     "The body scanner is in the posing room on F2 (private)."])


def plan_annex(G):
    pass  # the pods are on gym_f2, the altitude room on gym_f3

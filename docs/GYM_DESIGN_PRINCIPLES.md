# Gym design principles

Adopted 2026-10-30 (Roman: "research gym philosophy and interior design ... i feel like we are missing some principles", then
"incorporate those things"). The numbers are NSCA's facility guidance unless noted; vendors (VERVE, Skelcore) are looser or tighter.
Check a layout against them with `cd tools && ../terrain/.venv/bin/python gym_audit.py gym_f1 gym_f2 gym_f3`.

## In the layouts

1. **Space per station, not just walkways.** Barbell stations 0.9 m clear, benches 0.9 m apart, selectorized machines 0.6 m side to
   side, cardio 0.5 m, pull-up stations 1.2 m apart, walkways 1.6 to 1.8 m. Back-to-back machines can sit closer: their use space is
   in front. Done: F1 two pull-up stations 1.2 m apart (was three at 0.3 m); F2 half racks 1.2 m apart, the deadlift platform turned
   along the olympic wall (0.26 m from a rack before), the leg extension island at 0.65 m gaps (one Hammer Strength leg extension cut
   for it); F3 the assisted nordic clear of the EZ bar rack.
2. **A home for every loose thing, beside where it's used.** Plates within 0.9 m of every loaded station that has no horns of its
   own (the PR-5000s, the half racks, the Atlantis benches and the smiths have them). Done: a bumper rack in each gap between the
   olympic platforms (they were 2 to 8 m away on the south wall), a plate tree by the deadlift platform and by the second Life Fitness
   flat bench (the bar holder moves south of the flat benches).
3. **Order from calm to intense.** F1 (in from the gallery): cardio, mobility, calisthenics on the south glass; F2: strength;
   F3, deepest: the den, functional, sleds. Already the case.
4. **Let beginners see in.** Half-height partitions where nothing backs onto them, so every room reads from the spine before you
   step in. Already the case (2026-10-28 zoning).

## In the building

5. **No light over a lifter's face.** Someone on a bench looks straight up. `tools/furnish.py` slides a gym light line that would
   pass within 0.5 m of a bench to the nearest clear spot (off the beams); the pods' west line moved clear of the bench. The F3 den
   (two bench rows at 1.3 m, one line a bay) can't clear every bench: its lines sit as far from them as they can, at its low 3000 K.
6. **Mirrors start 0.51 m up** (NSCA safety checklist: a rolling plate can't reach the glass), blackened steel below (F2 + F3 west
   walls, the pods). Not facing the glazing, not along a walkway.
7. **Room acoustics.** Glass and light hard surfaces ring. The gym soffits were already wood-wool; the zoning partitions now have
   black acoustic felt behind their oak slats, and oak boards over their open ends.
8. **Impact.** The gym floors are concrete / precast with an impact mat under the gym flooring; olympic lifting is on dedicated
   impact suppression platforms. 18 to 25 mm rubber where bars drop, 8 to 12 mm elsewhere.
9. **Headroom.** NSCA: 3.7 m minimum, 4.3 m for olympic lifting and rigs. F2 and F3 are about 4.5 m to the soffit, 3.4 m under the
   1.1 m beams; no overhead lift happens under a beam (the one olympic platform under the y 4.4 beam carries the pulling blocks).
10. **Air by effort.** 20 to 22 C, RH about 50 % (60 % max), 8 to 12 air changes an hour (2 to 4 fresh), CO2 under 1000 ppm; the
    sled lane and conditioning want more air than stretching. A brief for the HVAC design, not modelled yet.

## Added 2026-10-31 (Roman walked the floors at eye level: "you literally have to phase through machines")

11. **Access before fit.** Every piece is reached from the floor's ways in without crossing someone else's training space;
    `tools/gym_walk_sim.py` checks it and simulates 400 sessions (maps in docs/traffic_sims/). Rows have their backs to a wall or to
    another row and face into an aisle (never a wall, never the water); main walks 1.5 m+, side aisles 0.9 m+ (NSCA, ADA 36 in).
12. **The side you get on stays open.** A plate-loaded machine keeps 0.6 m clear on its loading side; a plate tree is never in that gap.
13. **Wipes on walls.** Against a wall or partition (a corner first), at the rooms' edges; never in a training space, an aisle, a
    walkway or a door's landing. Every piece within 7.5 m of one (vendors: 7.6-15 m).
14. **Fixtures out of doorways.** Water and the AED points never in a door's landing; the space in front of them kept clear.
    `G.check` flags both.
15. **Muscle-ups need nothing above the bar.** The bar sits on its uprights (no crossmember over it), 1.8 m swing clear front and
    back, 1.2 m between bars.
16. **Headroom 2.1 m or a guard.** Anywhere a stair's underside is under 2.1 m is guarded (the spiral's first turn on F3: a glass
    ring guard); every stair opening has guards (the stair to F4: a spine wall + glass). The sled lane stops short of the spiral.
17. **Pegboard foot at about 2.0 m**, so you start from a hang with your feet off the mat.
18. **Mirrors where the lifting faces.** Dumbbell racks along a mirror's foot, 0.15 m off it (NSCA 6 in); benches face the mirror;
    the pods' whole wall; both faces of the bench room's wall; behind the F3 rig. Never hung kit on glass.
19. **Cardio upstairs.** Treadmills, bikes, rowers, ellipticals on F1 (and the altitude room); only stepmills by the F2 legs, for
    supersets. "There's so much beautiful nature ... people should just go run outside."
20. **Passing the access check isn't enough: a room has to read as designed.** Rows share a front (or back) line and a centre
    axis, the gaps between pieces are the same (0.9 m, 0.6 m by a tree), and the room's rows face one thing (its mirror). Pieces
    that each pass the sim but sit on their own lines read as "stuff thrown over there" (Roman, F2's leg room, second walk).
21. **Guards are one line, not two.** Under a stair's low turn the bars come down from the stringers (the balustrade carried on),
    never a second rail ring beside the stair's own: two rails 8 cm apart at different heights read as clipping. Glass guards stop
    at the wall's lining and keep wipes and bins off their line.
22. **Grip bars read at gym scale.** A 1.5 in bar you can see against the glass, not a 1.25 in line ("too thin" meant the grip
    bar). Keep the frame plain: no braces or gussets added for looks ("remove side supports and weird things like those triangles").

## Open

- **Wayfinding by floor material** (a change of floor at each zone edge) would change the locked light-floor palette: Roman's call.
- **Daylight**: cardio, warm-up and mobility face the views (done on F1 and the river bands); watch low west sun on the mirrors.
- **Density**: size each zone for its peak users (about 9 to 14 m² per free-weight user, vendor figure), not its kit count.

Sources: NSCA facility design (open-exam-prep.com study guide; nsca.com TSAC module 5; the NSCA safety checklist), VERVE Fitness and
Skelcore layout guides, IOA papers on lightweight gym floors, Colorado State biophilic exercise study, gym air quality studies.

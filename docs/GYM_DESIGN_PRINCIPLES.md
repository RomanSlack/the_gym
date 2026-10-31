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

## Open

- **Wayfinding by floor material** (a change of floor at each zone edge) would change the locked light-floor palette: Roman's call.
- **Daylight**: cardio, warm-up and mobility face the views (done on F1 and the river bands); watch low west sun on the mirrors.
- **Density**: size each zone for its peak users (about 9 to 14 m² per free-weight user, vendor figure), not its kit count.

Sources: NSCA facility design (open-exam-prep.com study guide; nsca.com TSAC module 5; the NSCA safety checklist), VERVE Fitness and
Skelcore layout guides, IOA papers on lightweight gym floors, Colorado State biophilic exercise study, gym air quality studies.

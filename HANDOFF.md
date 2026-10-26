# Handoff (read first in a new session)

**Latest equipment work (2026-10-25):** the cardio, to the rigour Roman approved on the elliptical ("nice work, now apply that same rigour to the others"): README point 9 (name each big shape's mechanical role first, measure the side view in px), the two gates, settings that render each user. Done and committed: LF Club Series elliptical (v024), upright Lifecycle (v006), recumbent (v005), IC7 (v006), Row HX (v004), HS HD Air Bike (v007, a solved crank-rocker four-bar), Concept2 SkiErg on its floor stand (v005), Fit3D ProScanner (v003; Fit3D has no hardware photos any more, refs from third-party pages). Kit gained `slab` (moulded shrouds from a side outline, `halfw` for plan shape), `block` (a box from eight placed corners: tapered / leaning beams) and `text(ry=)`. The four cardio pieces from 2026-10-23 then brought to the gates (spec written in, users 1.55 / 1.78 / 1.95): StairMaster v005 and VersaClimber v004 had their hands in the air, now solved onto the rails / grips by `equipment/blender/reach.py` (new: solves body.py's arm onto a target, reports the miss; use it for every grip); the VersaClimber's grip carriages moved to the mast's sides (ref_14); HD Tread and Woodway v004 needed no geometry change. All cardio is done. Then the Rogue rig and storage group (2026-10-25, Roman: "keep going"): Monster Rig 2.0 (v009), Monster Lite Monkey Rig 2.0 (v002), Monster Bumper Rack (v002), Monster Mass Storage (v001), Monster Landmine 2.0 (v004), Monster Safety Spotter Arms 2.0 (v002), Rig Mount Parallel Bars (v003), Monster Band Pegs 2.0 (v001), 10 Bar Holder (v004). Roman's rules from it: every pull-up bar lets a 6 ft 3 in user dead-hang legs long with the feet clear (the Monster Rig went to 108 in uprights, the bars on the top holes, lower bar 2.47 m; the Monkey Rig's pull-up bars raised to 2.47); Rogue rigs and storage in red uprights with black crossmembers, coloured bumper plates where the photos show them. Attachments are shown on display sections of a red Monster upright (not part of the piece). Kit gained sphere(). Then plates, collars and bars (2026-10-25, Roman: "go for it"): Eleiko IWF plates (v003) and IPF plates (v002) and change plates (v001), Eleiko IWF collars (v003), HS urethane round plates (v002), HS rubber bumpers (v002), Lock-Jaw Oly 2 collars (v003), Rogue Axle (v002), CB-1 camber (v003), SB-1 SSB (v004), MG-1 multi-grip (v002), HS fixed barbells straight + EZ 20-110 lb (v003), HS curl bar = the EZ (v002; the listing photo shows the straight variant), HS hex bar (v002), LF multi-grip (v002). shop.lifefitness.com answered HTTP 429 after a few fetches: the HS / LF accessories' sizes are estimates marked in their specs; re-check them with one polite fetch each later. reach.py gained low= (elbows down for a bar on the back); studio.py frames fit views on the piece + the user. Then dumbbells and kettlebells (2026-10-25): HS 4-sided urethane dumbbells 5-75 lb (v001) and the HS three-tier rack loaded with them (v002; equipment/blender/hs_urethane.py shares the dumbbell, tilt= for the sloping trays), Rogue loadable dumbbells (v002), LF cast iron kettlebells 4-32 kg (v005) and HS competition kettlebells 8-32 kg (v002) on equipment/blender/kettlebell.py. Then strongman (2026-10-25, Roman: "go for it"): Rogue log bar (v003), Rogue Y-1 yoke (v003, carry settings), Rogue farmers walk handles (v001, carry settings), Rogue rubber atlas stones 225 lb set (v002), Titan atlas stone platform built on the T-3 yoke it hangs on (v002, load settings; titan.fitness rate-limited the page, sizes from a search result), Rogue Sandbag 2.0 S/M/L (v005), Rogue strongman sandbags 25-400 lb (v002), LF push-pull weight sled (v004, push settings), LF ACFT sled with strap (v003), Rogue sled harness laid flat with its 9 ft strap (v004). Both LF sleds' sizes are estimates off the photos (LF shop 429, the cache has no sizes). Gotcha found: a piece's LOOK role inherits the kit's frame look for keys it doesn't set, so the frame's clearcoat made webbing glossy: set coat=0.0 on every soft-goods role. Next: the small accessories. Before that, see "Equipment, 2026-10-22 / 23" below.

**Latest (2026-10-18):** F4 is finished: the pool hall plus every room round it (lobby, deck + loungers, recovery lounge, thermal suite, breathwork), with a detail pass. Before that came the F3 den river, the glass lifts and the equipment passes (both leg extensions are modelled, `docs/` + `equipment/pieces/`). The stage 5 interiors still to do: see "Then" below. The block that follows is the 2026-10-12 state, kept for the detail standard it sets.

**State on 2026-10-12 (end of session ec5888c8 + its continuation):** stages 0-4 are built (site, foundations, structure, envelope in the LOCKED exterior style B). In stage 5, **the whole east wing (E1 + E2 daycare) is finished** to the baseline detail standard:
- **Reception:** the prototype, with the entrance matting, a fitted-out desk and the waiting nook.
- **Cafe (reworked, VISION "Cafe rethink"):**
  - Steinringen: a conversation ring round a granite boulder
  - Elva: the suspended river sculpture with brass tips and steel fish
  - a view lounge on the south glass and sofa groups on the east glass
  - only two dining tables
  - pictogram signs, and an oak-slat WC wall with steel portals
- **Public WCs (VISION "Public WCs, reworked"):**
  - an oak slat ceiling at 2.75 m and full-height cells in one flush run per room
  - outward doors with green/red turn indicators
  - the accessible WC as the widest cell (TEK17 kit, wall-mounted pull cord, real accessible basin)
  - Nautilus splash-free urinals
- **Daycare:**
  - upper floor: the tree house, the tube slide down the round stair, and the toddler zone with 'Kronen' + the nest
  - lower floor: the race track, foam fortress, music wall, banners, and a sleep room with mats
  - the sunken garden, with no fence along the top
  - staff and nursing rooms

All choices are in VISION.md: "Interior direction", "Wet rooms", "Daycare", "Baseline detail everywhere", "Cafe rethink" and "Public WCs, reworked".

**The detail standard (Roman, 2026-10-12): the level of detail now in the east wing is the bare MINIMUM for every zone, before any final styling.** Concretely, every zone gets:
- real fittings: bins, soap, towels, nappy/sanitary bins, brushes, pull cords, floor drains
- safety: an AED / extinguisher / first-aid point, lit exit signs, sprinklers + smoke detectors (`services()` in furnish.py)
- pictogram wayfinding: brass figures on blackened-steel plates (Roman found text signs lame)
- things set out the way they're used (desk kit, table settings, menus, cups)
- furniture joints that really join (no floating stretchers)
- lighting with no dark blotches (soft spots, sources outside the fittings)
- a catalogue sheet for every new piece

Do a "does this make sense" pass per zone, and look at every render yourself before showing Roman. Check:
- circulation, and doors versus stairs
- windows where people sit
- no slivers between built-ins, no doors clashing at 90 deg
- no empty voids above things
- nothing hanging mid-room that should be on a wall

Roman reacts badly to "IKEA" sameness: he wants centrepieces, places to meet people, and views used well.

**The lounge bridge + decks: first pass done (2026-10-12, VISION "Lounge bridge + decks"; renders `stage_5_br_*`, `stage_5_deck_*`).**
- **Gates:** members' phone-tap speed gates on the column line at the cafe mouth (x 12.0), with frameless glass to the walls. The cafe's NW sofa corner was removed for the landing.
- **Ladders:** three Laksetrappa ladders of light. The middle one has the fish; the side pair is mirrored and converges into the gym. The shapes are `lad_mid` / `lad_side` + `ladder()` in furnish.py, with a beam-clearance guard.
- **Glass floor:** 2 x 9 walk-on panels mid-bay between the girders, low-iron with an anti-reflective coating and no frit (Roman: see the river). The openings are cast in `S-F1-link` (structure_stage.py, holes flagged `glass_floor`); interior.py and furnish.py read them from there.
- **Shell:** oak along the bridge, slat ceiling between the beams (`split_x`), Kebony decks with slot drains.
- **Furniture:** two walnut benches inside, outdoor cafe sofa groups and standing tables on the decks.
- **Rejected by Roman:** rugs on the bridge (out of place).
- Anything on the bridge floor sits at `zf(x) = 0.12 * (x + 6.45) / 18.45`, and on the decks at `zf(x) - 0.015`.
- **Glass walls:** slide-and-turn, fully opening (`slide_wall` in furniture.py; state in `model.interior.bridge_walls`).
- **The gallery is done (VISION "The gallery"):**
  - Kilden on the bridge axis, with the locker entries re-planned mirror-symmetric round it (layout_v1.py polygons + partitions.py `PLACE`).
  - Impact-tile floor and wood-wool ceiling over the gallery + the F1 hall (interior.py).
  - 3500 K linear lights and a floor grazer.
  - Cameras `gal_*`; bridge + gallery cameras get +2.2 exposure, not +2.8.

**Kulpen, the outdoor sauna (2026-10-14, Roman: work on it now):** VISION "Kulpen". 2D first (`model/layouts/sauna.json`, `tools/sauna_layout.py`, `blueprint/layout.html?name=sauna`), then 3D as the first stage-6 build: the shell is `construction/sauna.py` (foundation, frame, envelope, sod roof + berm, chimney, inside, decks, pool steps, flume; `grade()` lowers the ground under the decks; `keep_trees()` keeps the forest off); the pieces are furnishings with `phase: 6` (`tools/furnish.py` section "Kulpen"; scene.py only builds furnishings whose phase <= the stage). Render: `scene.py -- 6 render` (cameras `ku_*`; the hot room + changing room get +1.6 exposure).

**Gym floors finished + lit (2026-10-14):** F2 + F3 finishes in `tools/interior.py` (zone 'the gym floors'), the light in `tools/furnish.py` ('the gym floors' light': `gym_line`, `wall_washer`); cameras `gym_*`. Watch out: an emissive diffuser inside a solid box is invisible (the first renders looked switched off).

**Bekken i hulen, the den's river (reworked 2026-10-17, VISION; Roman: done):** a base of split dark granite in eight thin strata under the F3 river glass, wall to wall; a slit the window's length at the river's surface; the water steps down the ledges into a flush pool on black sand under ~14000 generated near-black stones (`_pebbles` in furniture.py; they stay black only if glossy, matte ones go grey under the soffit grazers), out through a slit across the floor at the south end. The pool is 0.3 m deep, so `tools/structure_stage.py` drops the F3 slab there (`ST3-F3-den-tank`), lowers the floor beams under it and clips F4 partitions that ran up into the slab. Cameras `gym_den_river`, `gym_den_fall`, `gym_den_slit`, `gym_den_outfall`, `gym_den_glass`. Note: the `river_small_rocks` texture never fully downloaded (only ao.jpg in the cache), so don't use it.

**The gym equipment (2026-10-17, Roman: he shops for real high-end equipment himself, we model it):** a system of its own in `equipment/`, separate from the building pipeline so it has fewer ways to fail.
- `equipment/list.json`: the master list (~200 types, from the old wishlist + FIT_STUDY + VISION; `maybe` = beyond the fit study, Roman decides).
- `python3 equipment/serve.py` → http://localhost:5290: Roman pastes a product link per item (it checks off), skips maybes, adds items. Every click is one line in `equipment/history/curation.jsonl` (the curation replay) and is folded into `equipment/picks.json`. The server fetches each link's title + og:image into `equipment/refs/` (git-ignored: shop photos).
- **Equipment replay** (for the YouTube section: how we curated, then how we modelled): `python3 equipment/replay/build.py` → open `equipment/replay/out/index.html` (git-ignored, rebuilt after every turn by `tools/capture/checkpoint.py`, guarded so it can't break the other replays). Three views: Curation (every item as a tile that lights up with its product photo as Roman found it, real time with long gaps squeezed, play/scrub), Piece (one item: its finds, then every model version with the prompt under it), Overview (product photo beside the latest model). V = video mode (full screen, no chrome, autoplay) for screen recording; `?video` in the URL starts in it.
- **Roman's picks are in (2026-10-17), the library is a side mission as big as the architecture:** read `equipment/README.md` first (his decisions, the layout, the playbook). One folder per real product he linked: `equipment/pieces/<piece>/` (piece.json with brand, link, price; refs/ photos, local only; models/). `python3 equipment/tools/pieces.py sync` / `fetch` (polite: one cached request per page, 5-10 s apart; Roman doesn't want his IP flagged).
- **Every iteration of every piece is kept (Roman, 2026-10-17):** each modelling pass = one version number with its renders `equipment/pieces/<piece>/models/<piece>_<view>_vNNN.jpg` AND its geometry `<piece>_vNNN.glb`, never overwritten (`equipment/tools/versions.py`: `v = next_version(piece)`, `path(piece, view, v)`, `model_path(piece, v)`). Commit each pass on its own so the replay gets the Prompt trailer per version.
- **First up: the four leg extensions** (Hammer Strength Select, LF Insignia, HS Plate Loaded Iso-Lateral, Precor Resolute), dialled in, also in the rendered gym; then write the playbook. Default brand Life Fitness / Hammer Strength; upper body = a maze of modular PWR Play cable towers.
- Next: model each piece from its refs.

**Equipment, 2026-10-21 (Roman: the easier ones, benches and the like):** modelled, each committed per pass: the Rogue Flat Utility 2.0 (approved, "that is the level of quality"), the LF Signature Olympic flat, the Rogue AB-3 and Manta Ray (with its foot catch for decline), the GMWD SR05 seal row, the Atlantis P337 / P338 / P339 (P338 + P339 reuse P337's towers), the Hammer Strength plyo box set, the Rogue crash cushions and wood jerk blocks, the Titan pulling blocks, the AbMat blocks, the ABS Nordic Curl, the Body-Solid VKR and the Hammer Strength back extension. `equipment/tools/lineup.py` renders pieces together (`equipment/lineups/`). Open: the .glb exports lose the procedural looks (sheen, bumps, wood grain: pads read grey, the jerk blocks white), so the line-ups build each piece from its model.py instead; fix the export (or place pieces from model.py) before putting them in the gym. Gotchas in equipment/README.

**Equipment, 2026-10-22 (Roman: some of the accessories):** the five bars on one shared builder, `equipment/blender/barbell.py` (each bar's model.py holds a spec: lengths, collar lathe profile, knurl runs + hand marks, end cap, Eleiko's lettered collar ring): Eleiko IWF 20 kg, Hammer Strength 20 kg stainless, GIANT 15 kg Hybrid 2.0, Strencor 15 kg (its photos fetched off the product page), Gymleco 817T technique bar (to its dimensioned drawing). The kit gained a diamond knurl look (`knurl=dict(c=(y, z), r, pitch)`: the bar's axis runs along x through (y, z) in object coordinates, so a bar must be built along x and moved as an object) and `text(spin=)`. Also the Life Fitness dual-height hex bar and the Rogue rubber hex dumbbells (one dumbbell grown by weight: `dumbbell(k, kg, y, n)`, the gym's three sets are that at other weights; the rack in Rogue's photo is not a pick). Line-up: `equipment/lineups/accessories_*_v001.jpg`.

**Equipment, 2026-10-22 later (Roman: what is next / go for it):** the four platforms (Hammer Strength impact 6x8 and rubber 6x8, Titan 36 in, Rogue deadlift; the HS "with ramp" left out, no photo shows it); the kit gained `spec=` on looks (matte rubber 0.15: flat tops no longer wash out in the studio) and remember the kit's colours are linear (wood ~0.5, not 0.8), grain scale ~5-10 to read at room distance. The racks on a shared builder `equipment/blender/rack.py` (Rogue Monster Collegiate half rack, Monster Lite half rack, REP PR-5000 built as REP's matte black photo: its width/depth/extension read off the photo). The Life Fitness Signature Smith (one photo exists; to its 87 x 49 x 93 in spec). The eight Hammer Strength plate-loaded legs, each held to Life Fitness's spec sheet: hack squat v003 (release lever, start handle, pop pin), linear leg press, V-squat, Pendulum-X (grey Charcoal, as its studio render), belt squat (no dip attachment, the variant picked), glute drive (its round back pad still a plain half round), seated calf, tibia. Line-ups: `equipment/lineups/{platforms,racks,plate_loaded_legs}_*_v001.jpg`. Next: the selectorized legs, then cardio.

**Equipment, 2026-10-22 / 23 (the selectorized legs, then "easier smaller ones"):**
- **Shared stack towers:** `equipment/blender/stack_tower.py`, one style per maker: Hammer Strength Select open tower, Life Fitness "insignia" (uprights, curved bevelled gloss cap, two satin panels with a chrome channel, placards), "axiom" (rounded side uprights, arched cap), "atlantis" (corner posts, gloss side panels with the red A logo, placard band, rounded cap). Roman called the first box towers "absolutely terrible": measure a tower from a square-on photo and check a close-up beside it.
- **Modelled:** the HS Select leg extension, standing calf, biceps curl, hip ab/adduction (one model, `ADDUCTION` switch), the MTS kneeling leg curl and the seated arm curl; the four Insignia (leg extension, seated leg curl, glute, calf extension); the Axiom leg curl; the Atlantis M318 incline calf raise (v009); the HS Assisted Nordic Ham (v003, 30d381f, not yet reviewed by Roman).
- **Fit check (new, use it on every machine):** `equipment/blender/body.py` is our own capsule figure at any height, posed by segment angles from the ball of the foot (Drillis & Contini fractions). Give a model.py `fit()` → {label: pose} (+ `FIT_VIEWS`) and studio.py renders `fit_<label>_<view>` per version, never in the piece, its .glb or its check. Examples: the M318 (standing, leaning into a pad) and the Nordic Ham (kneeling: `sole=180, shank=90`). README checklist step 2b: lay the machine out from the user before the frame (Roman on the M318's first foot plates: "not proper at all, use your intuition of how a human would use it").
- **Modelled 2026-10-23 (later):** the HS Glute Ham / Reverse Hyper combo (v005, Silver as its photos; the photos put the pad's top at 1.36 m, so the spec's 53 in reads as the pad, not the foot unit), the HS Fixed Pad Glute/Ham (v003, from its one studio render, Roman: "its fine"), and the cardio: StairMaster 8Gx (v004), VersaClimber TS-M floor mount (v003, the variant Roman linked), HS HD Tread (v003), Woodway 4Front with the 21 in screen (v003; four more photos fetched off the linked page's gallery). The kit's looks gained `emit=` for lit displays.
- **LF PWR Play (2026-10-23, Roman: "the most polished of all of them", it is repeated in the maze):** one shared builder, `equipment/blender/pwr_play.py`; the 5-station set (`life-fitness-pwr-play`, v031) and the first maze (`life-fitness-pwr-play-maze`, 6 Cores in a 3 x 2 grid) are both layouts: `build_layout(k, dict(cores, faces={(core, "N/E/S/W"): station}, bars=[(a, b, handles)]))`. Stations: pulldown (knee pads on a pivot arm with a pop pin), row (J beam, twin foot plates), triceps, adjustable / crossover (stainless carriage post under a round boom), dualhigh, duallow, dip, panel. Crossbars only at the manual's connector spacings (`spacing("short"/"medium"/"long"/"xlong")` = 187/217/248/255 cm clear + 0.796) and butted onto round booms with thin sleeve joints (ref_03); none on a pulldown's or triceps' face. Heavy stacks (pulldown, row) 5-260, the rest 5-125, numbers top-down. Placards are our own art (`equipment/blender/art/pwr_play/make_placards.py`). Refs (local): the assembly manual PDF (April 2025, the module list + drawings) and ref_01-08 (photos decide shapes). Not built yet: Assisted Dip Chin, stall bars, rope pull, Power Pivot, step, handle storage. Where the maze stands in the gym, and its size, is still Roman's call.
- **The kit's check now catches pass-throughs** (ray parity on every part's vertices and points every 1 cm along its edges; any cable through material). Still look at the close-ups yourself: Roman caught clashes the old vertex-only test missed, and a floating crossbar no test flags.
- **Still unmodelled:** the remaining list items.
- **Open questions for Roman:** the M318's width (spec 38 in, modelled 0.66 m); whether the HS open towers get the square-on rework too; the REP rack configuration; the Nordic Ham's frame colour (our Charcoal vs the photos' silver) and its link geometry (no pivot close-up exists).

**The glass lifts (2026-10-17, VISION "The glass lifts"):** `glass_lift` in furniture.py, one per shaft, placed in tools/furnish.py ("the glass lifts"); stops = (z, glass height, reveal, lintel[, proud]). Openings + the removed A3/A4 columns in tools/structure_stage.py (`lift_front`). Cameras `gym_lift_f3`, `gym_lift_f3_close`, `gym_lift_f1`, `lk_lift_men`, `rec_lift`. Watch out: a new builder's kwargs only reach it if the kind is in `PARAMS` (furniture.py), otherwise it silently builds with its defaults. F4 (pool lobby) and the E2 lift lobby have no interiors yet, so those stops stand in raw rooms.

**F4, the pool hall (2026-10-17, VISION "F4, the pool hall"):** shell in tools/interior.py ("F4, the pool hall": deck, ink tile linings, charcoal ceiling); `lap_pool`, `river_wall_f4` (black tile cut round the windows: `_rect_minus`), `river_volume` (the river's body outside, a volume box) in furniture.py, placed + lit in tools/furnish.py ("F4, the pool hall"). Cameras `pool_from_lobby`, `pool_south`, `pool_edge`, `pool_windows`. Materials in bl_common: `stone_blue`, `stone_nero(_honed)`, `stone_white`, `tile_ink`, `pool_mosaic(_black)`. Roman rejected procedural marble outright: use real textures (granite_tile has a baked tile grid, dark_rock reads as crumpled foil at wall scale; smooth_concrete_floor tinted works). The rooms round the hall (VISION "The rooms round it"): `plunge`, `sauna_cabin`, `sauna_heater_el`, `steam_room`, `rinse_shower`, `pool_lounger`, `recovery_bay` (Remedy Place LA refs in reference/f4_recovery/), `plant_pot`, `eclipse_sconce`, `towel_bin`, `breath_mat` in furniture.py, placed in tools/furnish.py ("F4, the rooms"); finishes in tools/interior.py ("F4, the rooms off the pool hall": `line_rooms(..., walls=_wall4)` lines F4 rooms); the plunges' raft holes are `PLUNGES` in tools/layout_v1.py. Cameras `pool_lobby`, `pool_loungers`, `pool_recovery`, `pool_recovery_bay`, `pool_thermal`, `pool_thermal_w`, `pool_sauna`, `pool_steam`, `pool_plunge`, `pool_breathwork`. The W3 exit door opens into the thermal suite at x -9.05 (structure_stage moves it): keep its landing clear.
  - **The pool's size (Roman 2026-10-18):** a true 25 m between the finished end walls (25.02, structural rect y -28.58..-3.1 in layout_v1 / foundations / interior `POOL4`), four 2.4 m lanes, 1.25 m deep at the steps falling to 1.5 m at the south end (`lap_pool(d_n, d_s, raft)`; the raft top is F4-1.6, the fall is in the screed). Change it in all four places together.
  - **Detail pass (2026-10-18, VISION):** the deck floor is real flamed granite (`stone_blue` uses `granite_flamed_gridless`, a grid-free texture `tools/assets.py derive_gridless` makes from granite_tile_03, because the source has a baked tile grid); the recovery lounge follows Remedy Place (velvet daybeds in curtained bays, compression boots `_air_boot` + a pump, opal globes, smoked oak floor, venetian plaster); `pool_lounger` has a real frame (Roman caught floating parts). Helpers new in furniture.py: `_loft`, `_zprism`, `_stadium`, `_velvet`, `_foliage`. More cameras: `pool_boots_close`, `pool_lounger_close`.
  - **Watch out:** `furnish.put`'s first argument is `kind`, so no builder may take a kwarg called `kind` (plant_pot uses `species`); builder and helper names clash silently (`_leaf` is the door leaf, so foliage is `_foliage`).

**The gym WCs (2026-10-18, VISION "The gym WCs, F2-F4"):** the WC annex is a T (layout_v1 `wc-gym-women/men-<L>` polygons, walls `WA-*`, slabs `S-WA-<L>` body + `S-WA-<L>n` neck, roofs `S-WA-roof` + `S-WA-roof-n`, the spine `SP-WA-spine`); the rooms are one builder, `gym_wc` in furniture.py (men's local frame u/v, the women's mirrored with `hand=-1`, `pool=True` on F4), placed + lit in tools/furnish.py ("the gym WCs"), the shell in tools/interior.py. Cameras `gwc_*` (+1.0 exposure: they read grey at +2.2). Fixed on the way: the annex walls' membrane + gravel were generated inside the rooms (foundations' soil side came from the gym's centre), and wall A's granite plinth ran down its back inside the annex (envelope.py now opens it there).

**The south annex rooms (2026-10-18, VISION "The south annex rooms"):** posing + 3 pods (F2), altitude (F3). Shell: tools/interior.py ("the south rock annex on F2 + F3": `gym_floor`, `ww_ceiling`, `pod_plat`); pieces: furniture.py ("the south annex rooms": `posing_wall`, `posing_stage`, `stage_rig`, `light_boom`, `velvet_backdrop`, `pod_wall`, `platform_inlay`, `airlock`, `sky_coffer` (+ `_sky_mat`, a node gradient), `altitude_display`, `altitude_station`, `vent_grille`, `hypoxic_plant`, `scene_keypad`, `ceiling_speaker`; `glass_door(privacy=True)`); placed + lit in tools/furnish.py ("the south annex rooms"). New wall `SP-SA-alt` (F3, x -14.45) closes the altitude room; the bay east of it is the hypoxic plant. Wall S's granite plinth was running through the annex rooms (envelope.py now opens it there, as wall A's). Equipment slots are written in furnish.py's comment: they're filled from the equipment library. Cameras `ann_*` (+1.0).

**Then:**
1. the gym equipment (from `docs/FIT_STUDY.md`, hand-designed), with the focused pools over racks/platforms/rig; F1 hall walls. The locker rooms are done (first full pass).
2. E2: garage, bike/moto parking, game room, lift lobby
3. F2, then F3 (the darker "den", see VISION). F4 is done (2026-10-18).

For each zone:
- First the shell: floors, ceilings and linings, in `tools/interior.py`.
- Then furniture, fixtures and doors: `tools/furnish.py` + `construction/furniture.py`.
- Then lighting.
- Show Roman a couple of cameras per zone before moving on.

Gym equipment comes from `docs/FIT_STUDY.md` and is hand-designed by us, like the furniture.

**Locker rooms: in 2D first (Roman, 2026-10-12).** The layout page is `blueprint/layout.html` (run `npx vite --port 5280` in blueprint/, then open /layout.html; the drawing set links to it).
- It draws walls, openings, columns and rooms from building.json, and every element from `model/layouts/lockers.json`, at true size with dimensions.
- Drag, R / [ ] to rotate, arrows to nudge, D to duplicate, Del, Ctrl Z, Ctrl S. Saving goes through the dev server's `/api/layout`. `?view=x0,y0,x1,y1` frames an area.
- `tools/locker_layout.py` wrote the first proposal and won't overwrite it without `--force`. Once Roman edits it, the JSON is the source.
- **The locker rooms: first full pass done (2026-10-13; VISION "Locker rooms: wall waterfalls + the changing rooms in 3D"; renders `stage_5_lk_*`).**
  - **Changing rooms:**
    - The oak block with three round locker rooms (18 lockers each, fully modelled inside, two open in each middle drum).
    - **Room colours instead of numbers** (Roman: numbers are lame): Multe / Mose / Fjord, as a stained-glass band over each mouth and a glass chip on every door.
    - Round seats, the shoes-off screen + shoe bench + cubbies, towels, the grooming bar, tap stations, UV-C plates, the WC auto door.
  - **Wall waterfalls:** three per changing/wash wall, with empty planters. **The plants come at the very end, by Roman.**
  - **Wash zones:**
    - Fossen, a grotto carved into a stone west end wall.
    - Private showers + an accessible one, onsen wash places with eyelid sconces, a vanity with a robot garage.
    - An open oak slat canopy at 3.05 filtering the clerestory daylight.
  - **WC rooms:** the fluted oak cell run with the accessible WC, the urinal room, handwash, the cleaner's cupboard, the UV-C slipper cabinet, far-UVC lamps.
  - **Robots:** Vaskebjørn robots + docks, one per zone.
  - **Sauna lobby:** rolled robes, a robe-hook rail, sandals, a birch log store, a towel warmer, a tap station, a duckboard at the door out.
  - **Light (Roman: zen, not too bright, lock in):** low warm pools, warm lines under the lockers, seats and shower fronts. The waterfalls and Fossen's water are the brightest things. lk_ cameras get +0.8 exposure.
- **Watch out:**
  - The men's changing-side wall face is y -4.125 (the wash side is -4.275). The room is 5.55 m deep.
  - Builder names in `furniture.py` BUILDERS must be unique. A second `water_station` once silently replaced the cafe's; the locker-room one is `tap_station`.
  - Glow materials are emissive: a large disc at strength 9 (the old oculus) floods a room. Check emitters before blaming lamps.
- **Still open in the locker rooms:** the plants at the waterfalls (last), and the sauna itself (outside).

## Commands
- **Source of truth:** `model/building.json`. Rebuild everything derived with `terrain/.venv/bin/python tools/build_model.py`. It runs layout → structure → partitions → room numbers → foundations → stage-3 structure → stage-4 envelope → stage-5 interior → furnish → stage coverage check, and must end with `stage check ... OK`.
- **Downloaded inputs** (CC0 textures, HDRI): `python3 tools/assets.py`. Cached in `~/.cache/the_gym/`; manifest in `assets/manifest.json`. Nothing downloaded is committed (the repo is public).
- **Trees:**
  - tree library (generated, 13 variants × 3 LODs): `blender -b --factory-startup -t 12 --python construction/tree_lib.py` → `construction/out/tree_lib.blend`
  - forest points: `terrain/.venv/bin/python tools/forest_scatter.py`
  - real forest data: `tools/forest_data.py` (see `docs/ECOLOGY.md`)
- **Construction scenes:** `nice -n 19 blender -b --factory-startup -t 12 --python construction/scene.py -- <stage> render [only:cam1,cam2]`.
  - Night views: add `night` (the sky near black, only the building's lights; renders named `*_night`).
  - Stage 4+ renders in Cycles (GPU, small tiles). **GPU or nothing** (Roman 2026-10-17: never grind on the CPU): `bc.gpu_or_stop()` in every render script quits with exit 3 and `!! NO GPU` when CUDA/OptiX is unreachable. Then tell Roman to fix it (so far: an NVIDIA driver update without a reboot, `nvidia-smi` showing Driver/library version mismatch); don't render on the CPU instead. A GPU draft frame should take seconds to tens of seconds, not minutes.
  - Stage 5 adds the interior and furniture.
  - **Quick looks: add `draft`** (48 samples, 80 %: Roman found renders slow). With `only:` the scene builds just the furnishings within 45 m of those cameras and does not overwrite the saved full .blend. `[time]` lines in the log show where the time goes (2026-10-14: furniture 72 s -> 21 s after `Part.box` was built directly and `Part.rods` batches bars; a draft frame ~40 s).
  - Cameras are in the `CAMS` dict in `scene.py`; reception and cafe cameras are named `rec_*` / `cafe_*`.
- **Drawings:** `cd blueprint && npx vite --port 5280` (H = replay, P = A1 sheets, D = dark). Re-export the PDF only when Roman asks: `node tools/export/export_pdf.js`.
- **Cameras:** every zone's cameras are in `CAMS` in `construction/scene.py` (prefixes `rec_`, `cafe_`, `wc_`, `dc_`, `garden_`, `br_`, `deck_`; deck cameras are outdoors and get no extra exposure). Interiors get +2.8 exposure by prefix: add yours (e.g. `br_`) to that tuple in scene.py.
- **Component catalogue** (every designed piece alone in a studio, 4 angles, one sheet each + an overview): `nice -n 19 blender -b --factory-startup -t 12 --python construction/catalog.py -- [zone:daycare,garden] [only:kind1,kind2]` → `construction/renders/catalog/<kind>_vNNN.jpg`, every single view also kept in `construction/renders/catalog/views/<kind>_<angle>_vNNN.jpg` (composed by `tools/catalog_sheets.py`). **Roman treasures the catalogue: it is a permanent, versioned record; never delete or overwrite any of it.**
- **New in this session:** `tools/partitions.py` splits L-shaped shared edges into straight legs (ids kept). Round slab openings are cut through the structural slabs too. The daycare stair's position + start angle live in `model.stairs` (`layout_v1.py`), and the opening, trimmer beam, floor/ceiling cuts, guards and tube follow from it. Sanitation + safety builders (`towel_station`, `safety_point`, `exit_sign`, `ceiling_services`, ...) are in `construction/furniture.py`.
- **Art:** generated with gpt-image-2 via the imagegen skill into `docs/art/`. The reception painting is `artvalleyoil_0.png`.

## Where the design lives
- **Decision docs:**
  - `VISION.md`: ground truth, including the LOCKED exterior style B, the LOCKED interior direction and the primary metal
  - `STRUCTURE.md`
  - `CONSTRUCTION_PLAN.md` (stages + rules)
  - `DECISIONS_PENDING.md`
  - `docs/AUDIT.md`, `docs/FIT_STUDY.md`, `docs/ECOLOGY.md`
- **Code per stage:**
  - `tools/foundations.py`, `tools/structure_stage.py`, `tools/envelope.py`
  - `tools/interior.py`: finish palette `PALETTES["L"]`; floor, ceiling and lining patterns
  - `tools/furnish.py`: what goes where
  - `construction/furniture.py`: how each piece is built
  - `construction/bl_common.py`: materials, incl. `blackened_steel`, `brass_accent`, `arch_glass`, `pbr_material`, `rock_material`, `water_material`
  - `construction/trees.py`, `construction/ground.py`

## The locked interior language (from the reception)
- **Light everything:**
  - white-oiled oak boards, 220 mm wide
  - an undulating pale ash wave ceiling between the pale spruce glulam beams
  - oak slat walls (45 mm at 65 mm on black battens) as features
  - warm-white plaster elsewhere
  - light stone only at entries
- **Dark only at the windows:** the frames and the facade band.
- **Metal:** blackened, waxed steel is the primary metal. Brass only as small accents, never a whole component.
- **Loose furniture:** oiled walnut (contrast to the oak floor), oat wool, cognac leather, sheepskin. Backs rake back. Minimal Nordic mid-century, regional.
- **Lights:** no pendants in front of art; slim steel wall lights, downlights and soft wall-washers. Every fitting is a real light source.
- **Green** comes from the art and the views of the forest, not from paint.

## Roman's standing rules
- **Design:** open plan, no door unless needed; column-free; Gym V2 is his intent reference; realistic and to real scale everywhere.
- **Assets:** every asset (furniture, equipment, trees, rocks) is generated in this project; only textures and HDRIs are downloaded.
- **PDF:** no re-export unless he asks.
- **Never overwrite images:** renders auto-version to `construction/renders/*_vNNN.jpg`; anything else gets a new filename.
- **Replay discipline:** commit right after each change Roman asks for, including messages he sends mid-turn. The hook adds the `Prompt:` and `Also-Prompt:` trailers automatically. Push at milestones.
- **Blender files:** saved .blend files open with all foliage hidden in the viewport (renders still include it).
- **Render politely:** `nice -n 19`, `-t 12`, small Cycles tiles, no heavy EEVEE. The GPU that renders also drives his displays.
- **Built-ins flush (Roman 2026-10-18):** cells, cabinets, runs of anything built in sit flush with the walls they stand against, wall to wall, their fronts in the plane of the wall beside them; never a box set into a room after the fact.
- **Stage coverage:** nothing designed may be skipped by a stage, and nothing buried may show or float (`tools/stage_check.py`). Before showing a stage, look at wall bases, corners and inside the cores in a close camera; Roman once caught missing core corners himself.

## Replays
- **Drawings:** H in `blueprint/`.
- **3D renders:** `.capture/renders/replay.html`, rebuilt every turn by `tools/replay/render_history.py`. Any camera, every version, with its prompts.

## Known open items
- **Large .glb files:** GitHub rejects files over 100 MB. The PWR Play mega's .glb (386 MB per version) is kept on disk only and gitignored (dropped from history before the 2026-10-25 push). Check a new .glb's size before committing it. (The Remedy Place photos in b4e3807 were pushed as-is on 2026-10-25, Roman's call.)
- **F4 follow-ups offered, not decided:** the thermal suite reads dark and moody (offered: ink tile with black only round the plunges); the compression boots are fine at room scale but plain up close (offered: a multi-angle reference build as for the leg extensions).
- **The trail runs through Kulpen.** `site.features.trail` was routed before the sauna grew a berm: it passes the porch and under the west berm (keep_out is the old 6 x 9 m box). Re-route it west round the mound (bigger keep_out in `terrain/route_trail.py`, then the features raster in `terrain/ravine.py`) when stage 6 does the trail.
- **Entrance stone strip** inside the doors reads dark. With the vestibule now outside it could become oak plus a recessed mat; offered, not decided.
- **West-garden camera** sits inside the forest; there's a small ground dip at the foot of the W2 tower.
- **Forest species:** birch and grey alder aren't generated yet (the forest is spruce, pine and regrowth), and there are no shrubs.
- **3D stage replay:** the construction timelapse by `phase` / `seq` isn't built.
- **Drawings and code:** elevation A-203 draws no ground in front (an old issue). (The W1/W2 stairs' 1.0 m width vs TEK17: dropped, Roman 2026-10-17: don't worry about TEK17 for the stairs.)
- **Blender gotchas:**
  - Blender 4.1+ makes new faces smooth unless set flat (handled in bl_common).
  - In Blender 5.2's node API, Random Value has one "Value" output, and geometry nodes use FunctionNodeSeparateColor.

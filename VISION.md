# Vision (ground truth)

This is the source of truth for what we're building. It's compiled from Roman's notes (Oct 10, 2026), his floor sketch, the Gym V2 blockout, the feature list and the reference images. Where they conflict, **this file wins**. Anything marked *(proposed)* is Claude's suggestion and isn't confirmed yet.

## The one-liner

A **luxury 24/7 gym**, "the most optimal, nicest gym with the coolest design", with a **Scandinavian / Nordic** feel. It's built into a **deep forested ravine with a river** at the bottom. The building terraces down one wall of the ravine to below the waterline, and a glass **bridge** crosses to the other bank.

## Non-negotiables

1. **Real-world scale.** Everything is sized to true dimensions.
   - The ref people in Gym V2 are 6 ft (1.83 m), and Gym V2's proportions are what Roman intended, so we carry them over as the starting point. They can change later.
2. **Build it like a real finished structure.**
   - Model every material and assembly, even ones you can't see: framing, structure, slab build-ups, wall layers, and so on.
   - Design with load-bearing logic, so structure works the way it really would.
   - Plumbing and electrical don't need to be modeled inside the walls, but the design must respect their constraints: wet rooms stacked and grouped, shafts, risers, mechanical space.
   - *(proposed)* A routing script could lay out the main runs to check that they fit.
3. **No faked geometry.**
   - Things shouldn't be "printed textures" unless that's genuinely what the real material is.
   - Texturing comes later. Geometry and structure come first.
4. **Built into the environment.**
   - The building is designed around the site, and the site is designed around it.
   - Getting the ravine/valley right is a priority. The Gym V2 terrain is roughly 50% of the way there.
5. **Design intent beats the old drawings** wherever this file says something different.

## Site: the ravine

- **Main reference:** `reference/gym_v2_original/Gym Design.jpg`. This is Roman's single AI-generated exterior reference.
- It's a **deep ravine**, not a gentle river valley. The walls are steep and rocky, granite-gray and mossy. The banks have mixed pine/spruce forest, ferns and boulders.
- A **waterfall** sits upstream of the bridge.
- The river is narrow, fast and deep enough to stand waist-deep at floor 3's rim, with a visible riverbed at floor 4's windows.
- Outdoor elements (feature list):
  - A 2-mile **running trail** through the forest, lit by low bollards (see the mockup sheet).
  - **Stone paths** lit by lights.
  - A **covered bike area**, which is a timber-framed pavilion in the mockups.
  - A **rustic footbridge** over the river, **north of (behind) the building**. It should feel like it's been there since the 1930s, not futuristic. It exists so people can stroll to the sauna or the trail, which loops around both banks.
  - A **sub-terrain tunnel** to a small **parking garage** under the building, with an elevator to reception. The sketch calls it "Area for nice Cars", with a window.
  - An **outdoor sauna area**, mixed-gender. It's a separate outbuilding to the north by the trail.
  - An **outdoor garden terrace** and an outdoor training terrace with weatherproof equipment.

### What the reference image shows (architecture language)

- **Top:** a long timber volume with floor-to-ceiling glazing, a deep flat roof overhang with recessed downlights, timber soffit and fascia, and a cantilevered terrace with a glass balustrade. Gym equipment is visible inside. A stone-clad chimney/mass sits on the roof.
- **Below:** a second glazed timber level, set back.
- **Base:** heavy **dry-stacked stone** walls rising straight out of the river, with narrow vertical windows down at water level.
- **Bridge (in the image):** a fully glazed enclosed bridge with a timber frame and a flat roof. It spans the ravine and lands against a **stone retaining wall** on the far bank, which continues as a long stone wall into the forest.
- **Palette:** light/warm timber (spruce/pine), dark gray stone, glass, and green roof edges. The interior mockups add oak floors, stone feature walls, and warm linear/cove lighting.

## Program by floor

Floors are numbered **top-down**. Floor 1 is the entry level at the top of the ravine, and floor 4 is the lowest, at the riverbed.

### Floor 1: entry / social (spans both banks)

- **West bank (gym side):** Mens Locker, Womens Locker, Gallery, Stretching, Cardio, Calisthenics (strip along the river edge), Outdoor Garden Terrace.
- **Bridge / Lounge** across the river: the only link between the gym and reception/daycare. It's wide, with a seating area for meeting people, sliding glass walls that open fully, and **outdoor decks cantilevered over the river** on both sides.
- **East bank:** Reception, entry WC, Elevator (down to the garage), Bike Area. Also a water filling station.
- **NEW: Cafe in the middle area.** It replaces the "Kitchen" from the sketch, because that area felt too empty. Cafe themes on record are "fitness themed" and a smoothie/juice bar with nutrition consultation.
- **NEW: Daycare** on the east bank, north of the WC/Reception block. It's clearer in the Gym V2 .blend than in the sketch. It has **two floors**: the garage foundation extends out north, and the daycare sits on it over two levels. It must meet **full regulatory daycare requirements**: child-height restrooms, sinks, storage, and so on. Those need to be researched for real.
- **Sauna**: a separate outbuilding to the north, by the trail.

### Floor 2

- **West bank:** Free Weights (with mirrors, and possibly a lower step-down area of about 3 platforms), Machines, Cardio, Steps.
- **East bank:** Game Room, Elevator, Garage ("nice cars", with a window), and the daycare's second floor.
- **Garage:** small. A couple of cars is fine, because most members bike, so it doubles as an **indoor bike garage**. It's reached by the sub-terrain tunnel, with an elevator up to reception. The outdoor covered bike area stays too.

### Floor 3: river rim level

- Calisthenics / Functional, Free Weights, Machines / Strongman / "whatever else", Transition Area, **River Door**.
- **Signature feature:**
  - The river surface is at roughly **adult waist height** relative to this floor. From the waist down you'd be "underwater" if you stood outside.
  - **Glazing at the rim**, so the river visibly flows past the window.
  - An **opening that lets river water in** as a small **indoor stream**. The inspiration is Japanese *nagashi-sōmen* (flowing-noodle waterfall) channels.
  - The stream must **not overflow**. It has to be realistic and physically plausible, and also look really cool.

### Floor 4: recovery / pool (riverbed level)

- Recovery Area, **Pool**, "special stuff", Transition Area, River Door.
- **Signature feature:** windows looking **directly into the river below the surface and at the riverbed**.

### Vertical circulation

- **One open spiral staircase** runs from **floor 1 down to floor 3**. It replaces the sketch's "transition area" stairs and should feel **really open**.
- **Floor 3 to floor 4** uses **normal stairs**, placed toward the **north edge**. The spiral doesn't continue down because of the pool.
- There's an **elevator** on the east bank (garage to reception). The gym side presumably needs an elevator too, for accessibility. *(Open question.)*

## Gym zones (from the feature list)

Free Weight · Strength Machines · Functional / CrossFit · Cardio · Olympic Lifting Platforms · Calisthenics & Bodyweight · Stretching & Mobility · Small Group / Class Studio · Strongman · Recovery & Cooldown.

The full equipment list is in `reference/gym_v2_original/text_features_not_all_required.txt`. As the filename says, **not everything is required**. It's about 25 machines, a full free-weight setup, a CrossFit/strongman kit, Concept2/SkiErg/air bikes, and so on.

### Special features (wishlist, not all required)

> **Deferred.** Get the structure built first. The features get fitted into the structure's constraints later.


- Heated/cooled floors
- Posing room
- Robot cleaners
- Infrared sauna
- Cryo
- Hydrotherapy and hot/cold plunges
- Recovery lounge
- Altitude room
- 3D body scanning
- Virtual training walls
- Private training pods
- Smoothie bar
- Indoor turf track (sleds/sprints)
- Luxury lockers (towel service, rainfall showers, steam, grooming)
- Valet/concierge
- Sound-zoned areas
- Spa services
- Mobility/breathwork room
- Climbing/bouldering
- Outdoor training terrace
- Rooftop lounge

### Locker rooms (required detail)

- Washroom, locker and shower areas are kept separate.
- Floor-to-ceiling toilet stalls, urinals and sinks.
- Private showers.
- Modest locker space.
- Water bottle refill.

### Lighting

- Recessed into ceilings and floors, in natural tones.
- Optimal lighting for posing, plus lots of natural light.

### Stats (from the list)

- Open 24/7, autonomous.
- 50 to 75 active users.
- ~~1000 m²~~: Roman says this number was made up. **Size comes from the Gym V2 massing**, not from this stat.

## References in the repo

| File | What it is | How to use it |
|---|---|---|
| `Gym Design.jpg` | AI exterior concept of the ravine, building and bridge | **Main reference** for site and architecture |
| `Gym Design (1).jpg` | Grid of AI interior mockups per zone | Vibe only. Roman says these do **not** reflect the actual design |
| `00_floor_program_sketch.png` / `Gym_1_floor_program.psd` | 4-floor program sketch (Aug 2025) | Room adjacency, as updated by this file |
| `The_Gym_v2_snapshot_2026-09-18.blend` | Hand-made massing | **Scale and proportions** source |
| `text_features_not_all_required.txt` | Full features and equipment wishlist | Pick from it |
| `01..07_*.png` | Renders of the Gym V2 blockout | Quick visual of the massing |

## Engineering notes for the water features *(proposed, to discuss)*

- **Floor 3 river window:**
  - Use structural laminated glass or acrylic in a reinforced concrete frame, designed for hydrostatic load at that depth plus flood level.
  - The real constraint is the **flood level**. The design river level and the 100-year flood level must both be set, and the building's openings must sit above flood level or have closure provisions.
- **Indoor stream:**
  - Use a controlled intake: a screened inlet with a sluice gate and a fixed weir that limits flow.
  - The stream runs in a stone channel and returns to the river through an **overflow/return channel that sits lower than the intake**, so it physically can't flood the room.
  - A shut-off gate is needed for floods and maintenance.
- **Floor 4 underwater windows:**
  - Use thick acrylic aquarium-style panels set in a concrete tank wall.
  - The whole lower level is a waterproofed concrete box (tanked/"white tank"), designed for uplift and lateral water/earth pressure, and keyed into the ravine rock.
- **Structure strategy:**
  - Floors 3 and 4 (and the retaining side of floor 2): reinforced concrete clad in stone.
  - Upper floors: timber, either glulam frame + CLT or heavy timber, with steel where the spans and cantilevers need it.
  - Bridge: steel or glulam truss, possibly expressed.
  - This matches the reference image: stone base, timber top.

## Decisions (Oct 10, 2026)

- Floor area: the 1000 m² stat is meaningless. Gym V2's massing sets the size.
- Wishlist: deferred. Structure first, features later.
- Floor heights: keep Gym V2's tall ceilings (about 4.9 to 5.6 m floor to floor). They can change if structure demands it.
- Bridge: a rustic, 1930s-feeling footbridge north of the building, part of the trail loop to the sauna.
- Stairs: one open spiral from F1 to F3; normal stairs from F3 to F4 near the north edge.
- Garage: yes. Small (a couple of cars), and it doubles as indoor bike parking.
- Daycare: east bank, north of WC/Reception, two floors over an extension of the garage foundation, fully code-compliant.
- Lounge link: **yes, it stays.** It's the enclosed lounge over the river and the only way from reception/daycare to the main gym. It's now **wider**, with **decks extending outside over the river**. **Sliding glass walls** open fully on nice days, so people can relax in the open air above the water. The river runs under it, between the gym (west wing in Gym V2) and reception/daycare (east wing).
- Cafe: it's the round counter in Gym V2's east wing (about 7.5 m across), replacing the sketch's kitchen. Think of an **airport-style circular island bar, but a cafe**: staff inside the ring, seating all around it.
- Waterfall: **directly under the rustic footbridge**, north of the building (matching the reference image). The river flows from there south past the gym wing.
- Gym V2's river and terrain are a rough placeholder. The ravine gets designed for real (see the site approach in README / next steps).
- River flows **north to south**. The falls drop south, under the rustic footbridge, with the water lip **at least 1 to 2 m below the bridge deck**. The bridge sits right over the falls or slightly upstream of them.
- **Arrival road:** a narrow Nordic forest road (about 1.5 lanes), clean black asphalt, **no road lines, no clutter**, like the forest roads in Finland and Sweden. It arrives at reception (east bank) and the garage tunnel.
- **Landscape scale:** much bigger than Gym V2's plot. It needs room for the 2-mile (about 3.2 km) trail loop on both banks and for aerial shots.
- **Landscape terrain is generated procedurally outside Blender**, with real erosion, then imported into Blender.
- **Gate:** we don't move on to the building interiors until the ravine, river, waterfall, road and foundations look right **in 3D** and Roman is happy with them. Landscape and foundations drive everything else. The building itself is mostly simple boxes.
- **Site: Elverum, Norway** (around 60.957 N, 11.374 E). Kartverket 1 m terrain, CC BY 4.0. It's a forested plateau, not mega-hilly, so the horizon reads as forest rather than being walled in by hills.
- **Surroundings are real, the ravine is ours.** The real terrain is kept for everything around the site. The real gorge is erased and replaced by a **parametric ravine** (centerline, depths, falls, pools) that we reshape artistically. Its shape rules (depth to width, wall angles, step-pool rhythm, meander) are **measured from the real Elverum gorge**, so it stays believable.
- **Daycare lower floor = walk-out onto a sunken play garden** (option A). A sheltered courtyard is excavated on the north side of the east wing at E2 level (−6.0), with terraced planting stepping back up to the forest floor. It gives the lower daycare floor daylight, a direct exit and a safe enclosed outdoor play area. Roman: "amazing and magical".
- **Garage at E2 is reached by the sub-terrain tunnel ramp** from the road (about 45–50 m of ramp for the 6 m drop), designed together with the road.
- **Falls position confirmed:** lip just north of the rustic bridge, dropping south into the plunge pool along the gym.
- **Sauna (outdoor badstue):** replaces Gym V2's cube.
  - **Location:** moved **upstream to y ≈ 95 on the west bank**, by a new **calm, widened dipping pool** in the stream. It's about 55 m above the falls lip, with a rock weir between them. The walk from the gym's north side is about 85 m, roughly a minute.
  - **Small and integrated with nature:** under 15 people.
    - One hot room for 10–12, a small changing room and an outdoor shower. About 5 × 8 m.
    - **Sod roof (torvtak)** and dark tarred timber.
    - Set partly into the bank: a low mound from the trail, opening to the stream with a window and a small deck over the pool.
  - **Mixed, swimwear on** (the Norwegian norm).
- **Locker room back door:** a shared **sauna lobby** between the men's and women's locker rooms (F1, north side of the west wing), with robe hooks, a towel warmer, sandal racks and a key-card door.
- **Sauna path:** a lit stone path, about 2 m wide, with low bollards. The first stretch has **snow-melt heating**, so robes and sandals work in winter.
- **Indoor saunas too:** a men's and a women's sauna inside the locker rooms (plus the steam rooms). That's the quick everyday sauna; the badstue is the social, ritual one.
- **Garage looks out across the ravine** (as in the original sketch: "Garage (area for nice cars), Window"). The rock ledge between the east wing and the canyon is cut down along the garage stretch, so the garage's west wall stands on a rock shelf above the plunge pool. **Floor-to-ceiling glazing** looks straight across the water at the gym. The garage floor (E2) is about 2.8 m above the water.
- **Daycare lower floor:** glazed toward the sunken garden (walk-out). It stays solid toward the ravine for safety.
- **Trail:** a ~3.2 km (2-mile) loop around the upstream valley. It crosses the river at the rustic bridge and at a small timber footbridge far upstream, and passes the sauna. About 1.5 m wide, gentle, with low lights.
- **Trail is for running and walking** (not a winter ski lysløype). It stays about 1.5 m wide, as laid out (2.06 mi loop). A later polish pass can add drainage dips and culverts, plus dark-sky bollard lighting.
- **As column-free as possible:** no interior columns on any floor. Floors and roofs span wall to wall (23.1 m in the gym, 18.5 m in the east wing) on post-tensioned concrete beams (floors) and glulam beams (roofs). The tall floor-to-floor heights absorb the deeper beams.
- **Flood regulations are ignored for this build.**
- **Daycare = drop-in childcare** while parents train (not a full-day barnehage), but luxury: it must handle anything (babies to 12-year-olds) and everyone must be comfortable. It has age zones: a baby & toddler room, a kids' room, a parent & nursing room, a rest/sleep room, and active play opening onto the sunken garden. The current garden size is fine for drop-in.
- **Arrival is landscape, not a parking lot.** The road ends in a small drop-off loop around a planted island (one big old pine, boulders, moss), with 3 accessible spaces. The main entrance is an **entry meadow: soft grass and natural stepping stones**, with moss and boulder beds and no hard paving.
- **Parking is hidden:**
  - an **underground parking (~30 cars) under the entry meadow** (about 1 m of soil on its roof), drive-through to the east-wing garage, reached by the ramp tunnel off the road
  - plus a small **forest trailhead lot** (8 spaces, gravel, between kept trees) about 100 m east along the road, linked by a lit forest path
- **Bikes:**
  - A **covered bike shelter** (~30 bikes, e-bike charging, timber with a sod roof) at the south edge of the entry meadow, with stepping stones to the door.
  - **Underground bike + motorcycle parking** along the south wall of the east-wing garage (~40 bikes on two-tier racks, 6 motorcycle bays, bike wash + repair stand), a short walk to the core E lift/stairs up to reception.
- **Trailhead:** the 8-space gravel lot moved closer (x 99–120 along the road, ~50 m from the entrance). A **connector trail** runs north to the loop, and a **park-style trailhead sign** (log posts, small gable roof, illustrated map panel `terrain/assets/trail_map_v1.png`, made with gpt-image-2) stands at the trail start.
- **Outdoor garden terrace on the west side** (from Roman's sketch): a lawn garden between the two stair towers with moss/boulder beds and a big pine. It has a **timber training deck** off stretching & mobility with an **outdoor calisthenics rig** (pull-up bars at 3 heights, parallel bars), and a **path north along the back of the building into the sauna path and the trail**.
- **F2:** cardio halved (north half, river views); the south half is more machines (plate-loaded + cable).
- **Floor 3 is "the den"**: a darker, locked-in vibe with a black rubber floor, dark ceiling and low warm pools of light.
  - **Free weights take 3/4 of the west wall** (34.65 m), which is **floor-to-ceiling mirror**. The doors on that stretch are flush mirror-clad.
  - Rows of flat/incline/decline benches face the mirror, with dumbbell racks along it.
  - Strongman takes the north quarter; the sled lane moved east next to the river edge.
- **Extra rooms dug into the rock along the gym's south face** (6 m deep, below grade):
  - **F2:** posing room + 3 private training pods
  - **F3:** altitude training room
  - **F4:** breathwork & mobility room
- **Grip & hangboard wall** (hangboards, pinch blocks, rings, campus rungs; no bouldering) on the den's south wall.
- **Equipment: double up popular machines and plan islands** (freestanding dumbbell/cable racks with stations around them). Target normal gym density (~65–85 %), per `docs/FIT_STUDY.md`. That's 220 items, with every strength zone between 66 and 81 %.
- **Less spa (Roman: went overboard on the wishlist):** no massage or treatment rooms, no spa services, no cryo or infrared. What stays is the classic training recovery: a simple thermal setup on F4 (sauna, steam, hot/cold plunge), a recovery lounge (compression boots, loungers), and the outdoor sauna by the stream. Some of that could later move back into the locker rooms.
- **Game room (E2)** opens onto the ravine glass. It has **table tennis parallel to the river right on the glass** (the 'floating over the river' shot for clips), a classic 9-ft pool table, and a lounge corner with chairs and a coffee table. Only one table-tennis table fits comfortably, so there's one.
- **Public WCs** (reception): open, airport-style baffled entry with no door, full-height stalls inside, and an accessible WC with its own door.
- **Daycare toilets:** glass wall + open doorway, so staff have line of sight from the play space (safeguarding best practice rather than a strict code line); low stall screens for the kids.

## Exterior style: LOCKED (2026-10-11, stage 2)

**Direction B: dark tarred timber + sod roofs.** Roman picked it ("really clean").
- **Walls:** black-stained / tarred timber cladding (vertical boards), with a stone plinth at the base.
- **Roofs:** flat **sod / green roofs** on every roof (main wings, lounge bridge, annexes, bike shelter, W3 exit), thin dark roof edges, eaves kept.
- **Windows:** **divided glazing, not giant single panes.** Big openings broken into a rhythm of narrower panes with dark mullions, deep-set in the timber. Roman likes this explicitly.
- **Details:** weathered oak accents (soffits, doors, benches), dark metal.
- **Reference images:** `docs/style/bdarksod_gorge.jpg`, `bdarksod_aerial.jpg`, `bdarksod_arrival.jpg` (+ the full sheet `docs/style/style_options_v1.jpg`).
- Fits the sauna (already tarred timber + sod roof): the whole site reads as one family.

## Structure decisions (2026-10-11, stage 3)

Roman: "do whatever will look the best and sleekest for the design language", and keep the roof overhang.
- **2.5 m roof overhang is part of the real structure now:** CLT roofs run past the facades on tapered glulam beam tails; the wings and the lounge share one thin roof plane.
- **Lounge bridge floor = dark steel girders under the deck, not trusses**, so the sliding glass walls open fully with only slim posts in the glass lines.
- **Spiral = open helix, no centre post** (steel stringers, oak treads).

## Envelope decisions (2026-10-11, stage 4)

Read off the style-B references and built for real (`tools/envelope.py`):
- **Glass where it's open, black timber where it's private.** Changing rooms, wet zones, WCs, staff and nursing rooms get solid black board-on-board walls with a high obscured clerestory band; everything else is divided glass.
- Facade glulam posts are black-stained (dark posts in the references); the roof beams, their tails and the oak soffits stay warm.
- Stone plinth on every concrete face that shows above ground, incl. the river wall from the riverbed up.
- Sunken garden stays as designed: at the east end of the daycare's lower floor the terraced bank rises in front of the last glass bays (Roman: fine as is).

## Interior direction: LOCKED (2026-10-11, stage 5, reception first)

Roman: light floors, light ceilings, light walls, wooden slat walls; "only dark should be the walls by the windows, the frames". Liked the result: "super clean".
- **Floor:** white-oiled oak boards, 220 mm wide, 1.8 to 2.4 m long, on screed with underfloor heating; light honed stone at the entrance (2.5 m deep).
- **Ceiling:** pale oak acoustic slats (45 x 20 mm at 65 mm, on black felt) between the exposed pale spruce glulam beams.
- **Feature walls:** vertical oak slats on black battens (the core walls behind the reception desk and towards the cafe).
- **Other walls:** smooth warm-white lime plaster.
- **Dark only at the windows:** black window frames and the black facade band above the glass, inside as outside.
- Palette lives in `tools/interior.py` (`PALETTES["L"]`); renders `construction/renders/stage_5_rec_*`.
- **Ceiling (updated):** undulating pale ash baffle ceiling (30 mm fins at 110 mm, depth waving 60 to 320 mm) between the glulam beams, replacing the flat slats.
- **Furniture:** oiled walnut frames (contrast to the oak floor), oat wool, cognac leather, sheepskin; cushions rake back; minimal Nordic mid-century. All designed in `construction/furniture.py`.
- **Art:** the reception painting is a gpt-image-2 oil (`docs/art/artvalleyoil_0.png`) on a stretched canvas with a procedural linen weave, in an oak float frame. Green comes from art and the forest views.
- **Lighting:** no pendants in front of art; slim blackened-steel wall lights, downlights, soft wall-washers; every fitting is a real light source.
- **Entrance:** the vestibule (vindfang) stands outside under the eave; the facade doors are its inner doors.
- **Primary metal: blackened, waxed steel (option D)** for window frames, posts, girders, lift doors, hardware: uneven blue-black and smoky grey, mill-scale streaks, satin wax. **Brass only as small accents** (pulls, call plates, thin inlays); no whole component in brass or bronze (Roman, 2026-10-11).

### Wet rooms: WCs, locker rooms, showers (2026-10-12, Roman: "do whatever is best")
The reception language carried into the wet rooms. Wood stays where it doesn't get wet; stone and glazed tile take over where it does.
- **Floor:** the light honed stone, in 600 x 600 slabs laid in stack bond (slip-rated finish R10, and R11 in showers), falling to linear drains in the showers.
- **Walls:** handmade-look glazed tile in a warm chalk white, 65 x 260 laid vertically in stack bond (it echoes the oak slats), to 2.6 m on every wall. Warm-white lime plaster above.
- **Cubicles:** oak boxes standing in the tall room: floor to 2.6 m, closed to the floor, with a lid, faced in vertical oak staves (the slat language) and flush doors with shadow gaps. They are "full height" by having their own lid, so the 5.5 m room above stays open to the clerestory light. Each one has its own light.
- **Vanities:** a long honed-stone trough on the wall, wall-mounted blackened-steel spouts, a full-length mirror in a slim oak frame, and a linear light above it.
- **Ceramics** are white, and grab rails, flush plates and roll holders are blackened steel. Brass is used only for the small door pulls.
- **Every public WC room** has its own accessible WC (2.5 x 2.4 m, its own door, fold-down changing table) and a cleaner's cupboard.
- **Locker rooms (F1, later):** the same floor and tile in the wet zones. The changing rooms get oak slat walls, oak lockers and walnut benches, as in the reception.

### Daycare: playful, still Nordic (2026-10-12, Roman: "more playful and colorful decorations and vibes")
The light shell stays: oak floor, ash ceiling, plaster. Play and colour come from things at child height:
- **Colour:** a soft Nordic set (lingonberry, cloudberry yellow, moss, fjord blue, heather), in wool felt, linoleum tops, cushions, cubbies and art. It's never the walls, and never primary plastic colours.
- **Rounded oak furniture** at child height, a play loft or "tree house" built from oak (the rooms are 5.5 m tall), felt cloud acoustic panels, and generated forest-animal art at a child's eye level.
- **Wardrobe** with named cubbies and drying cabinets, in oak with coloured felt backs.
- **Toddler zone (0-3), the high-effort one (Roman):** references were Råå day care (Dorte Mandrup), Kočevje kindergarten's built-in nooks, Kéré's Kinderoase, and Montessori + Pikler practice.
  - **Kronen**, the structural piece: an oval oak sunburst canopy (6 x 4.6 m, 72 radial fins deepening to the rim) hung at 2.75 m from the roof, with a glowing linen oculus. It gives the toddlers their own low sky in the 5.5 m room.
  - **The nest** under it: a stepped oak amphitheatre with felt-topped tiers and a soft felt pit full of cushions, with a gentle ramp in for crawlers.
  - a cushioned **window nest** along the forest glass with a low rail, for watching birds
  - a Pikler arch with a ramp
  - a low Montessori mirror with a pull-up barre under the moose painting
  - sensory panels (bead maze, spinners, textures, peekaboo flaps)
  - a low oval snack table with toddler chairs
- **Sanitation everywhere (Roman: that level of detail):**
  - every WC cell: a sanitary pedal bin and a toilet brush
  - every basin: a wall soap dispenser, with a paper-towel dispenser and a 60 l waste bin beside every vanity
  - changing units: a sealed nappy bin, glove boxes, a disposable liner roll, a wipes shelf and soap
  - children's WCs: low roll holders, with brushes kept out of reach
  - hand sanitiser at the entrances, the daycare door, the toddler zone and the garden doors
  - kildesortering (waste sorting) in the cafe and the staff room
- **Baseline detail everywhere (Roman, 2026-10-12: the daycare's level of detail is the bare minimum before the final styling):**
  - **Reception:** the desk is fitted out: two staff monitors on the worktop behind the desk front, keyboards, a phone, drawer pedestals, a card terminal angled to the customer, a check-in tablet and a member-card tray. There's also a coat stand with an umbrella stand, a reading lamp and magazines in the waiting nook.
  - **Safety:** a safety point with an AED (hjertestarter), an extinguisher and a first-aid kit (one on each floor of the daycare), and lit exit signs over every exit.
  - **Wayfinding:** oak signs with burnt-in Norwegian + English text (toilets, gym, daycare, lift).
  - **Public WCs:** an emergency pull cord in the accessible WCs, floor drains, amenity trays on the vanities (period products in the women's), and baffles slatted on both faces.
  - **Cafe:**
    - on the tables: a tealight, a carafe with glasses and a menu card on every table
    - a water, glasses and cutlery station with waste sorting in its base
    - menu boards and cups on the bar, bag hooks under it, and a card terminal
    - two high chairs, and downlights over the tables
  - **Services:** sprinklers and smoke detectors in every ceiling (109 points across E1 and E2).
  - **Furniture joints:** stretchers and footrests are joined to the legs at their real height (the cafe chairs had floating stretchers).
- **Cafe rethink (Roman, 2026-10-12: less "IKEA cafe", more meeting people and watching the view):**
  - **Removed:** the 11 m window counter with its 15 stools, six of the eight dining tables, the communal table, and the bar stools on the side facing the lounge.
  - **Steinringen, the centrepiece:** a built-in curved oak banquette with wool cushions (open in two places) around a flyttblokk, a glacial granite boulder with a sawn, gridded granite top.
  - **Elva:** a suspended sculpture of the river overhead, about 230 fins standing across the current like ripples.
    - The water runs glacier teal, mist and fjord blue, with oak glints at the bank.
    - Every fin has a polished brass tip, and nine mirror-steel trout and grayling swim upstream.
  - **View lounge along the south glass:** pairs of low lounge chairs with side tables on round rugs.
  - **East glass:** two conversation groups (a sofa, two lounge chairs and a coffee table on a rug).
  - **Kept:** the north-west sofa corner, and two tables for four for people who want to eat at a table.
  - **WC wall:** oak slats like the core, blackened-steel portal frames, and pictograms (steel plates with brass figures) instead of text signs. The gym, daycare and lift signs are pictograms too.
- **Sunken garden: no fence along the top** (Roman, 2026-10-12). The terraces run straight out into the forest.
- **Lower floor (E2):** the active-play room opens onto the garden through a pair of glass doors. It has a bouldering wall with a crash mat, ribbevegg (wall bars), two felt nest swings hung from the beam, soft play and a balance beam. By the garden door there's a mudroom with a boot-wash trough, cubbies and drying cabinets.
- **Sleep room (Roman: no bunks):** a wall-to-wall wool carpet with sleeping mats and blankets, so children sleep where they like. Spare mats live on a low shelf, and a fibre-optic star canopy hangs overhead.
- **Also in the lower play room (Roman):**
  - a foam fortress of felt-covered foam blocks to build, knock down and throw
  - a wheels corner with balance bikes, caster boards (RipStik), tricycles and a rack for them and the helmets. There are two more tricycles out on the garden loop
  - my pick: a lekebakke, a rounded felt ridge in contour-stripe bands with an arched crawl tunnel running straight through it
  - floor games inlaid in linoleum (Roman: the floor was bleak): a fjord-blue race track looping round the fortress and the hill, with oat edge lines, a dashed centre line, a checkered start line and chevrons; and a numbered hopscotch
  - on the north wall beside the climbing wall: a music wall (oak xylophone, chimes, felt drums, rain stick) and a low safety mirror with a barre; in front of it a balance trail (zig-zag beams, stepping pods, wobble board)
  - the upper walls carry tall wool-felt banners (sun, mountains, spruce, waves, moon + star appliqué, swallowtail hems, oak rods), and two strings of felt pennant bunting swag across the room over the race track
  - foam blocks have soft rounded edges and sit slightly off, as if stacked by hand
  - the nest swings have a woven rope net (not a solid disc), and the lower floor's downlights are soft-edged, so there are no hard dark spots on the floor
- **Tube slide down the round stair (Roman):**
  - a 660 mm tube spiralling inside the stair's eye from the upper floor to the play room (about 2 turns at roughly 24°)
  - the lower half is brushed stainless and the upper half clear polycarbonate
  - steel flanges, and hangers up to the stair's inner stringer
  - three rescue hatches on the stair side, each opposite a lockable gate in the inner balustrade, placed where an adult on the treads stands level with the tube
  - an oak bridge with guards from the floor to the entry hood, and a run-out with a landing mat
  - the stair's eye is widened to 1.45 m radius for it; the treads stay 1.1 m wide
- **Polish pass (Roman: things need to make sense and be intentional):**
  - The round stair moved 1 m north-east and turned. Its top step used to land on the staff-room door, with the floor guard almost touching that wall. Now the top step lands facing north into the play room and the bottom step faces the open lower floor. There's 1.9 m clear in front of the staff door, and the tube slide starts from a bridge on the west side and runs out north on the lower floor.
  - The staff room is not a privacy room: it gets divided glass to the west forest. Its toilet is a real walled, tiled room with a door (not a freestanding booth), and the room also has a kitchenette on the south wall, oak staff lockers, and the table by the window.
  - Upstairs line between the age zones: the tree house moved east of the stair and the craft tables west. The forest painting faces the open floor, the tree-house slide comes down beside a low shelf, and the toddler gate is at the south end by the children's WC.
- **Stair opening framed properly (Roman caught it):** beam B-9 now stops at a trimmer beam beside the round opening, and the lower ceiling is cut round the stairwell and the trimmer.
- **Children's WC on both floors:** the lower one sits directly under the upper one, opening off the play room.
- **Pram store:** pram parking, an outdoor-gear wall with rain suits and boots, and drying cabinets.
- **Garden (barnehage practice):**
  - by the door, for the youngest: a sandbox with a sit-on oak edge, and a vognskur where toddlers nap outdoors in their prams
  - a mud kitchen and a lekehus (the building in miniature: tarred boards and a sod roof)
  - a tricycle loop around a picnic table for lunch outdoors
  - swings (a nest swing and a seat swing)
  - a gapahuk facing the bålplass (fire pit) with log seats
  - a freestanding slide off the terrace edge with a stair beside it
  - stepping stumps along the west terrace

## Open questions

(Resolved: river depth vs floors. The ravine design puts the plunge pool at −8.77, about 1 m above F3, with the bed at −16.2, just below F4.)

(Resolved: daycare garden size. Drop-in childcare, so ~190 m² is fine.)

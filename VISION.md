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

## Open questions

1. The cafe is in the "middle area". My read is the round counter in Gym V2's east wing, which replaces the sketch's kitchen. Confirm when we lay out floor 1.

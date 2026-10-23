# The equipment library

A side mission next to the architecture, and as big a job: **the most extensive open-source library of real, high-end gym equipment as 3D models**, every piece modelled by us from the real product, every iteration kept. It is a passion project, non-commercial (see `LICENSE.md`): that is why the pieces are real branded products. It furnishes The Gym, and it is a section of the YouTube video: how the equipment was curated, then how each piece was modelled.

It runs on its own, separate from the building pipeline, so a failure on one side never breaks the other.

## Roman's decisions (2026-10-17)

- **Every product Roman linked is a pick, and we model it.** Where he linked several for one list item, we want all of them: four leg extensions (Hammer Strength Select, Life Fitness Insignia, Hammer Strength Plate Loaded Iso-Lateral, Precor Resolute) and two standing calf raises (Hammer Strength Select, Atlantis incline M318) are four and two separate machines in the gym. Same for the two seated calf, the flat bench stations, the platforms.
- **Life Fitness (with Hammer Strength) is the default brand** for everything he didn't link ("the highest quality brand from all my experience"), unless something is clearly better.
- **Upper body = a maze of modular cable towers**, not rows of standalone machines: Life Fitness PWR Play style modules (cable towers, crossover, functional trainer stations, lat pulldown and row stations, pull-up bars on top) linked into one large interconnected structure, on one floor or several. Roman prefers the pulldown on these to standalone machines, and the bars on top let you superset pull-ups. Standalone upper-body machines only where the modules can't do it.
- **The CrossFit / calisthenics kit is mostly bars**: lots of iterations later, not first.
- **Order:** the most common machines first, to get the look of training on one right. **First: the four leg extensions**, dialled in until they're right, also seen in the rendered gym. Then the playbook below gets written from what worked, and the rest follows it.
- **Prices:** every piece gets a price for the video, the list price on the linked page where there is one, otherwise an estimate marked as one.
- **Don't get Roman's IP flagged:** fetching is one request per product page, ever (cached), 5-10 s apart. No scraping service needed at this volume; if a shop starts blocking, ask Roman before using an API (he offered Firecrawl).

## How it fits together

| What | Where |
|---|---|
| The master list (~200 types) | `list.json` |
| Roman's shopping page | `python3 equipment/serve.py` → http://localhost:5290 |
| Every click on it, timed (the curation replay) | `history/curation.jsonl` → folded into `picks.json` |
| One folder per real product picked | `pieces/<piece>/piece.json` (brand, model, link, list item, price, status, notes) |
| Its product photos (local only, they belong to the shops) | `pieces/<piece>/refs/` |
| Our model, every iteration | `pieces/<piece>/models/<piece>_<view>_vNNN.jpg` + `<piece>_vNNN.glb`, never overwritten (`tools/versions.py`) |
| Pieces from picks, then price + photos | `python3 equipment/tools/pieces.py sync` / `fetch` |
| The replay (curation, each piece's versions, overview, video mode V) | `python3 equipment/replay/build.py` → `replay/out/index.html` |

Each modelling pass is committed on its own, so the replay shows the prompt behind every version.

## Start here: the checklist for a new piece (the Hammer Strength method, 2026-10-18)

The Hammer Strength Iso-Lateral got to "looks amazing" in 11 versions by doing this, in this order. Follow it so the next
piece starts at that level instead of getting there by back and forth.

1. **References: real photos from many angles.** A true side view, a true front view, a three-quarter, and close-ups of
   the pivot, the pad mounts and the base. Dealer galleries (Shopify `/products/<handle>.js`) beat the maker's single hero
   render. Pick pieces that have them. No camera fitting, no generated drawings as truth.
2. **Read the structure before building anything.** For every assembly, answer from a close-up: what is it made of
   (member sizes: 3 x 3 in, 2 x 4 in, 3 x 2 in...), and **what holds it** (see the joint table below). Find the yokes,
   brackets and gussets first; the parts they carry come after.
2b. **Lay it out from the user before the frame** (the Atlantis M318, 2026-10-22: the foot plates came out as flat
   shelves wherever they fitted, "not proper at all, use your intuition of how a human would use it"). Write down the
   pose at the start and the end of the rep (standing, seated, lying, leaning, which way the face points), then place
   every contact point from the body: feet, hands, chest, back, shoulders, knees. Use the body lengths (rule 7 below)
   for a short, a middle and a tall user where the machine adjusts. Write the numbers into the constants'
   comments, then build the frame to carry those points. Before showing, check that a person fits: nothing in the
   way of the toes, the shins, the head or the moving limb over the whole rep, and the machine still inside its
   L x W x H. The photos show what the parts look like. The body decides where they go and which way they face.
   Prove it with the fit check: give model.py a `fit()` returning {label: pose} (see `blender/body.py`: a capsule
   figure at any height, posed by segment angles from the ball of the foot) and the run renders each user in the
   machine as `fit_<label>_<view>` (never in the piece or its .glb). The M318's fit() is the example.
3. **Build by eye from the side and front views**, held to the maker's L x W x H. Constants at the top of model.py with
   a comment on each, every joint built as what it is (cut + weld, bolted plate, hub on an axle, bracket + bolts).
4. **The finishing parts that make it read as real, from the first pass:**
   - every member end lands on a face (cut + weld) or has a **plastic end cap** (rails, posts, lever tops);
   - **rubber feet** under the rail ends (a block the rail sits on, a pad flanged out each side with anchor holes), so the
     frame stands off the floor; the rails run past the cross bars to them;
   - **bolts with washers**, through-bolts with nuts, rail bolts in round black bushings;
   - **cushioned upholstery** (`shaped_pad(cushion=)`) on a back plate on a bolted bracket;
   - satin powder coat, the maker's colourway; warning labels where the photos have them.
5. **`check` until clean** (about 2 s, no render): 0 floating, nothing hung on a rod, no unexplained gaps.
6. **Render, then close-ups of every joint** (`DETAILS` cameras: the pivot, the pad mounts, the feet, the seat frame),
   each set beside the matching photo crop. The check proves contact; the close-ups show whether each joint is the right
   kind. Fix what differs before showing Roman.
7. Every pass is a version, committed with its prompt. Stop when Roman says good enough.

**Gotchas (the benches, 2026-10-21):**
- A look role the kit doesn't have (`emboss`, `urethane`, `foam`, `hole`, ...) starts as a copy of the kit's `frame`, clear coat included: give every matte role `coat=0.0` or it renders glossy (the LF hooks, the Manta's rollers did).
- Check the section's orientation: `k.bar(mat, p0, p1, w, h, up=...)` puts `h` along `up`. A foot passed as (2 in, 3 in) with up = z stands 3 in tall (the Rogue flat bench's feet, v002).
- A piece whose photos are a site banner (Atlantis) has its real renders on the product page: the cached page lists them (`wp-content/uploads/...`), fetch them one at a time, 5-10 s apart.
- Pieces of one family share parts: the Atlantis P338 + P339 import P337's `model.py` and set its constants (heights, hooks, horns) before calling `tower()`.

**Attention to detail (the linear leg press, 2026-10-22: v001 "fucked and skinny", right at v007).** Roman asked that every agent
work this way. Each of these was a pass he had to send back:
1. **Take the geometry off the true side view, with numbers.** Before writing code, find the empty true-side photo,
   set its scale from the spec (px per m from the overall length or height), and read each member's two ends in px,
   converted to (y, z): where it starts, where it ends, its angle. The leg press rails start right at the seat near
   the floor and climb at 40 degrees for 2 m. Guessed, they came out 45 degrees, too short and starting too high, and
   the whole machine read wrong. Write the measured points into the constants' comments (`# y -0.03, z 1.07 (ref_13)`).
2. **Match the bulk, member by member.** Count what each assembly is made of in the photo, and build every one: the
   rails were a 4 x 6 in beam with two chrome rods and bearing housings round both, not one thin beam with one rod.
   A thin machine looks wrong even when the outline is right. Make the base as wide as the photo's feet.
3. **Open frames stay open.** If you can see through the real part (a sled built of tubes with a triangle of air in
   it), build the tubes. Never fill it with a plate or a wall to save time ("it doesn't have those side walls").
4. **Work out what each member belongs to before building it.** A member half hidden behind plates or a user is easy
   to misread. Check it in every photo, empty and loaded, from both sides. The leg press's big "top bar" was the sled's
   own top arm, not a fixed X frame. Building the misread version cost a pass.
5. **Every adjustment has its mechanism.** Seats, back pads, pads and stops adjust on something real: a hinge, a strut,
   a notched rack, a pin, a pop pin or a release handle. Find it in the close-ups and build it whole. A back pad just
   sitting at an angle is wrong ("the seat rest has no pivoting thing to lower it more or raise it").
6. **Check every assembly's side (handedness).** Machines are not symmetric. For the tower, the lever, the cam and the
   handles, decide which side each is on (the user's left or right, near or far from the tower) from which part hides
   which in the photos, and write it in the docstring. The HS Select leg extension went out with its lever mirrored
   ("the contraption on the wrong side"): the cam sits beside the tower, the roller reaching across to the open side.
7. **Size the parts the body touches from the body.** Seat, pads, pivots and handles sit where an average man's joints
   are: seated, his armpit ~0.45 m above the seat, upper arm ~0.33 m, forearm + hand ~0.33 m, thigh ~0.45 m, lower leg
   ~0.45 m; a pivot sits on the joint it moves (the elbow, the knee). Work these out first and put the numbers in the
   constants' comments. And count a lever's parts in the photos (the HS biceps curl's is three: a short U connector, an
   arm off it to the hands, the grips), never one guessed shape.
8. **Compare before showing.** Put each render next to the matching photo at the same angle on one sheet (PIL, 800 px
   each: ref | ours, side and three-quarter) and look for the differences above before reporting. The difference you
   find yourself is a version Roman doesn't have to send back.
9. **Shared parts get the most care, once.** A part many machines share (the weight-stack tower: `blender/stack_tower.py`)
   is built once per maker style and then every machine of that maker gets it. Measure it from a photo square on to
   it (the Insignia glute's ref_04): studio shots are turned about 40 degrees and read narrow, close phone shots read
   wide. Read how it is made (the Insignia tower: two uprights the full height and depth, a gloss cap with a crisp band
   and a rounded crown, two satin front panels with a narrow chrome channel and the badge block, a placard on each,
   an inset back panel), and check a close-up render of it beside a close-up photo. A plain box with a lid
   was Roman's "absolutely terrible" (2026-10-22).

## The playbook (learned on the Precor leg extension, 2026-10-17; superseded by the checklist above where they differ)

1. **Gather every angle first.** Makers often publish one hero render; dealer shops (Shopify: `/products/<handle>.js`) carry more angles, close-ups and colourways. Two or more views of the same machine are worth more than any amount of fitting on one.
2. **Read the machine with common sense before measuring anything** (Roman): which way the user sits, where the knees, the back pad and the stack are, what is built square and level. Machines are welded square: towers square to the frame, rollers level. Label every anchor by what it is on the real machine (which corner, which side); a mislabelled corner (the Precor's seat side read as its front) makes the solver invent tilts, turns and absurd sizes.
3. **Real dimensions**: the maker's overall L x W x H (spec sheet) go into `SPEC`; parts that are standard (seat ~0.45 wide, pads 65 mm) start from those.
4. **Camera match** (`tools/camsolve.py`): anchors + straight edges in each photo, solved together with only the genuinely uncertain dimensions (`FIT`), each held near its sensible value. Then `tools/model.py` renders through each photo's camera and composes a match sheet (the photo | ours | overlay with our outline). The overlay is for checking, not the goal by itself: where it fights common sense, common sense wins.
5. **Then detail, part by part**, against the overlays and the close-ups: real joints (nothing floating), the maker's materials and colours, our own artwork for placards.
6. Every pass is a version (renders + .glb), committed on its own.

### Learned the hard way on the Precor (v001-v039)

- **Positions and looks are separate problems.** The camera solve (`camsolve.py`) got every part where it belongs (Roman: "positionally perfect"), but a model can match the photo's outline and still look nothing like the machine. Once positions are right, stop fitting and restyle by eye, the photo beside ours.
- **What makes it read as the real machine** ("the sauce of the structure"): real member sizes (commercial frames are heavy: 80-120 mm tubes, 30-35 mm levers), satin powder coat not gloss, upholstery as cushions (bulging sides, rolled edges, a stitched panel: `kit.shaped_pad(cushion=)`), dense mechanisms (plates, bolts, guards packed round the pivot), parts squared to each other in plan.
- **Generated drawings (gpt-image-2) are guides, not measurements**: each view scales differently per axis, has some perspective, and invents what the photos don't show (the top view's tower, the rear view's single leg). Use them for layout and shapes; sizes come from the photos + the spec. They disagree with each other: when they do, the real photos decide.
- **Pick references with many real angles first.** One hero render forces guessing the hidden sides; a dealer gallery with side, front, rear and close-ups doesn't.
- **Sheets that helped**: `match` (photo | ours from its camera), `detail*` (close-ups per assembly from the same camera, match.json "details"), `drawover` (ours over each drawing), the orthographic top against the generated top.


## Connections: every part is held (learned on the Hammer Strength, v009)

Roman: "on the real thing it is welded or bolted, but on ours it is just floating there". A machine reads as fake when its parts sit near each other instead of joined. So before modelling a part, read from a close-up **what holds it**, and build that joint. Every part attaches in one of these ways:

| joint | what you see on the real one | kit |
|---|---|---|
| **welded** | a member's end cut to the face it meets (coped / mitred), a bead round it, powder-coated over | `k.bar(..., cut0=(point, normal), cut1=..., weld=True)` (also `k.tube`, `k.sweep`): the end is cut flush to the plane, a bead runs round it |
| **bolted** | a plate flat against a face, at least two bolts, washers, nuts on the far side when it goes through | `k.box(...)` touching the face + `k.bolt(c, "+x", size, nut=grip)` |
| **on an axle** | a hub (a short fat tube) round the axle, bearing against the frame each side, nuts at the axle's ends | `k.tube` hub + axle through the frame + `k.bolt(..., size=0.03)` as the nuts |
| **sleeved / pinned** | a tube sliding in a bigger tube, a pop-pin through both | an outer tube + the inner one inside it + the pin |
| **upholstered** | the pad on a board, the board bolted to a bracket welded to the frame | `k.shaped_pad` + a bracket box + `k.bolt` |

Rules:
- **No part hangs on a thin rod alone.** A rod, pin or axle (under 40 mm) can't hold a block: give it a hub, a plate bolted to the frame, or a weld. (The HS outer ROM block hung on the axle in air; the real one is bolted to the yoke's post.)
- **Members end on something.** Every end is cut to a face and welded, or capped (plastic caps on post tops, lever tops). No square end poking through another member, none stopping short in mid-air.
- **Find the yoke / bracket / gusset before the part it carries.** Pivots usually sit in a yoke (two posts on a bridge), not on one upright; A-frames meet at a gusset; bent rods end in a bracket.
- **Bolts are hardware, not glue.** A bolt head stuck on one plate holds nothing; bolts go where a plate meets a face.

**The check** (`kit.check()`, runs on every build, printed before the renders): every primitive is a part labelled with its line in model.py. Parts that touch are joined; anything not joined down to the floor is **floating**. Hardware (bolts, labels, holes, seams) must sit on a member but never joins two. It also reports parts **hung on a rod only**, and **gaps** (two members 6 mm or less apart without touching: reads as a near miss, close it or open it up). Check without rendering, in about 2 s:

    blender -b --factory-startup --python equipment/blender/studio.py -- <piece> 0 check     # exit 4 = something floats

Aim for `0 floating`, no "hung on a rod", and no gaps you can't explain. Then look at a `DETAILS` close-up of each joint beside the photo's close-up: the check proves contact, the eye judges whether the joint is the right kind.

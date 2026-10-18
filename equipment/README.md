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

## The playbook (learned on the Precor leg extension, 2026-10-17)

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

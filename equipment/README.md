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


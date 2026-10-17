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

## The playbook (filled in as we learn on the leg extensions)

1. Study the refs: every photo of the piece, the maker's spec sheet dimensions (footprint, height, weight stack, pad sizes), what moves and how.
2. Model at true scale from the real dimensions: frame tubes and their profiles, welds and end caps, pads and upholstery seams, the moving arm with its pivot and cam, weight stack with guide rods, pin and shroud, cables and pulleys, adjusters, labels as geometry where they're plates.
3. Render the studio views (front, side, three-quarter, detail) and compare side by side with the refs; iterate.
4. Then place it in the gym and render it there.
5. (to be written: what the leg extensions teach us)

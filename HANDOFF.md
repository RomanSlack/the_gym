# Handoff (read first in a new session)

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

**Then:**
1. the locker rooms (wet-room rules in VISION; the entries are fixed now), then the gym F1 hall: stretching, cardio, calisthenics (floor + ceiling done, equipment + lighting to do) (wet-room rules already in VISION)
2. E2: garage, bike/moto parking, game room, lift lobby
3. F2, then F3 (the darker "den", see VISION), then F4 (pool, thermal, recovery)

For each zone:
- First the shell: floors, ceilings and linings, in `tools/interior.py`.
- Then furniture, fixtures and doors: `tools/furnish.py` + `construction/furniture.py`.
- Then lighting.
- Show Roman a couple of cameras per zone before moving on.

Gym equipment comes from `docs/FIT_STUDY.md` and is hand-designed by us, like the furniture.

## Commands
- **Source of truth:** `model/building.json`. Rebuild everything derived with `terrain/.venv/bin/python tools/build_model.py`. It runs layout → structure → partitions → room numbers → foundations → stage-3 structure → stage-4 envelope → stage-5 interior → furnish → stage coverage check, and must end with `stage check ... OK`.
- **Downloaded inputs** (CC0 textures, HDRI): `python3 tools/assets.py`. Cached in `~/.cache/the_gym/`; manifest in `assets/manifest.json`. Nothing downloaded is committed (the repo is public).
- **Trees:**
  - tree library (generated, 13 variants × 3 LODs): `blender -b --factory-startup -t 12 --python construction/tree_lib.py` → `construction/out/tree_lib.blend`
  - forest points: `terrain/.venv/bin/python tools/forest_scatter.py`
  - real forest data: `tools/forest_data.py` (see `docs/ECOLOGY.md`)
- **Construction scenes:** `nice -n 19 blender -b --factory-startup -t 12 --python construction/scene.py -- <stage> render [only:cam1,cam2]`.
  - Stage 4+ renders in Cycles (GPU, small tiles).
  - Stage 5 adds the interior and furniture.
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
- **Stage coverage:** nothing designed may be skipped by a stage, and nothing buried may show or float (`tools/stage_check.py`). Before showing a stage, look at wall bases, corners and inside the cores in a close camera; Roman once caught missing core corners himself.

## Replays
- **Drawings:** H in `blueprint/`.
- **3D renders:** `.capture/renders/replay.html`, rebuilt every turn by `tools/replay/render_history.py`. Any camera, every version, with its prompts.

## Known open items
- **Entrance stone strip** inside the doors reads dark. With the vestibule now outside it could become oak plus a recessed mat; offered, not decided.
- **West-garden camera** sits inside the forest; there's a small ground dip at the foot of the W2 tower.
- **Forest species:** birch and grey alder aren't generated yet (the forest is spruce, pine and regrowth), and there are no shrubs.
- **3D stage replay:** the construction timelapse by `phase` / `seq` isn't built.
- **Drawings and code:** elevation A-203 draws no ground in front (an old issue); the W1/W2 stairs are only 1.0 m wide (check against TEK17).
- **Blender gotchas:**
  - Blender 4.1+ makes new faces smooth unless set flat (handled in bl_common).
  - In Blender 5.2's node API, Random Value has one "Value" output, and geometry nodes use FunctionNodeSeparateColor.

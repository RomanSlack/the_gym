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

**NEXT: the lounge bridge + its decks** (`model.spaces`):
- `lounge` (F1, x -6.45..12.0, y -9.5..6.8): the enclosed bridge over the river, the only link from reception/cafe to the gym. VISION wants it wide, with a seating area for meeting people and sliding glass walls that open fully.
- `deck-n` (y 6.8..11.3, the falls view) and `deck-s` (y -12.5..-9.5): outdoor decks cantilevered over the river.
- **Structure (stage 3/4, already built):**
  - `S-F1-link` slab and `S-RF-link` sod roof
  - four dark steel girders and the tapered deck outriggers (`ST3-link-*`)
  - glulam roof beams on slim posts
  - glass `EN-G-link-N-0` / `EN-G-link-S-0` with their headers, and the glass balustrades `EN-balustrade-*`
- **Floor levels (already solved):** the gym is at F1 = 0.00 and the cafe at E1 = 0.12, so the bridge's finished oak floor (`IN-F1-bridge-*` in interior.py, a sloped `pattern_floor` via `"slope"`) rises 120 mm over its 18.45 m (1:150, imperceptible). It's flush at both ends with no step. The black E2 facade band was lowered under the bridge so it no longer shows as a stripe at the join. Keep anything placed on the bridge floor at the floor's height there: `z = 0.12 * (x + 6.45) / 18.45`.
- **Shell to do:** ceiling and linings in `tools/interior.py` (the floor is done). The decks are still raw.
- **Furnish in `tools/furnish.py`:**
  - the meeting/seating area
  - the deck furniture (weatherproof: oiled oak / steel, sheepskins, blankets, heaters?)
  - lighting and services
  - the sliding-wall hardware made real
- **Open question to put to Roman:** card-reader gates into the gym where the cafe meets the bridge (members' gym; it changes the cafe's circulation).
- **The gallery** on the gym side (`gallery`, F1, x -11.6..-6.45) is where the bridge lands. Do it with the bridge or straight after.

**Then:**
1. the gym F1 hall: stretching, cardio, calisthenics, the gallery, the locker rooms (wet-room rules already in VISION)
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
- **Cameras:** every zone's cameras are in `CAMS` in `construction/scene.py` (prefixes `rec_`, `cafe_`, `wc_`, `dc_`, `garden_`). Interiors get +2.8 exposure by prefix: add yours (e.g. `br_`) to that tuple in scene.py.
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

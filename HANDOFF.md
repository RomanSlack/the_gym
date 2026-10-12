# Handoff (read first in a new session)

**State on 2026-10-11 (end of session c2657e98):** stages 0-4 are built (site, foundations, structure, envelope in the LOCKED exterior style B). The forest follows real forest data (NIBIO SR16), and the site has its ground, grass, rocks, water and HDRI sky. Stage 5 is under way: **the reception + cafe hall on E1 is the finished prototype** (interior shell, furniture, lighting, art). Its choices are LOCKED and recorded in VISION.md ("Interior direction" + "Primary metal").

**Next step:** apply the reception's design language to every other area, zone by zone, in this order:
1. ~~the rest of E1: public WCs, the daycare upper floor~~ (done 2026-10-12: see VISION "Wet rooms" + "Daycare"; renders `stage_5_wc_*`, `stage_5_dc_*`)
2. the lounge bridge (next)
3. the gym F1 hall: stretching, cardio, calisthenics, the gallery, the locker rooms
4. E2: garage, game room, daycare lower floor
5. F2, then F3 (the darker "den", see VISION), then F4 (pool, thermal, recovery)

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
- **Component catalogue** (every designed piece alone in a studio, 4 angles, one sheet each + an overview): `nice -n 19 blender -b --factory-startup -t 12 --python construction/catalog.py -- [zone:daycare,garden] [only:kind1,kind2]` → `construction/renders/catalog/<kind>_vNNN.jpg` (sheets composed by `tools/catalog_sheets.py`).
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

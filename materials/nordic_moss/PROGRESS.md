# Nordic moss: progress

Goal and done criteria: GOAL.md. Images: out/index.html.

- 2026-11-02 11:27 Started: goal set (GOAL.md), out/ page + replay hookup
- 2026-11-02 11:29 `out/refs_sheet_v001.jpg` Reference photos by kind. A is my read of 'fluffy green moss on grey rock' (cushion / mood moss); B is the pale decor lichen
- 2026-11-02 11:29 `out/scan_bases_v001.jpg` CC0 scans to build on: ambientCG Moss002-004 (cushion moss), Moss001 (forest floor), Rock046S (grey granite + lichen), Poly Haven mossy_rock
- 2026-11-02 11:31 `out/albedo_candidates_v001.jpg` First albedo candidates (Gemini, from the granite + moss scans and photos). Picked A: moss sits naturally in the hollows, rock reads granite (a touch warm: to be cooled). B's rock reads concrete, C is split in two
- 2026-11-02 11:37 `out/render_wall_v001.jpg` First Cycles render (2 x 2 m panel, displacement 6 cm, 128 samples, 16 s): moss reads fluffy and stands off the rock; overexposed (rock near white, moss lime), sheen too strong
- 2026-11-02 11:38 `out/render_wall_v002.jpg` Light and moss sheen fixed: grey granite, deep green cushions; reads right at 3 m
- 2026-11-02 11:38 `out/render_close_v001.jpg` 0.7 m, raking light: cushions terrace (the moss scan's bumps stretched on the slopes), rock soft (2K over 2 m = 1 mm/px)
- 2026-11-02 11:39 `out/render_close_v002.jpg` Moss height detail cut: terracing remains, so it's the scan's normal, not the height
- 2026-11-02 11:39 `out/render_close_v003.jpg` Fibre-only detail from the scan's normal: scallops gone, cushions plush. Rock still soft at 0.7 m (resolution)
- 2026-11-02 11:39 `out/maps_sheet_v001.jpg` The set: albedo, height (moss domes from the albedo's own moss outline), normal (height + scan fibres), roughness, AO (from the height), mask
- 2026-11-02 11:40 `out/render_boulder_v001.jpg` Boulder (box-projected): moss wraps the form and stays fluffy; but an egg shape, moss even all round (should favour top + shaded sides), rock too pale, a projection seam round the middle
- 2026-11-02 11:43 `out/render_boulder_v002.jpg` Moss as a layer over the bare granite (Gemini's moss-free edit underneath), dialled by orientation: a real boulder shape, rock reads granite; moss patches flat with cliff edges, too little
- 2026-11-02 11:43 `out/render_boulder_v003.jpg` Full coverage, thinning only on the down-facing sides; the top stays sparse (the texture has moss on ~half its area: a denser pass later)
- 2026-11-02 11:44 `out/render_wall_wet_v001.jpg` First wet pass: stone darker with a water film, moss soaked deeper green; but the film is even everywhere (silvery), streaks don't show, nothing to reflect
- 2026-11-02 11:45 `out/render_wall_wet_v002.jpg` Wet v2: damp everywhere, a full water film only where it runs or pools, the real sky to reflect; bug: the running-water streaks stripe the moss
- 2026-11-02 11:45 `out/render_close_wet_v001.jpg` Wet close-up (0.7 m): soaked dark granite with the film glinting, moss drenched deeper green, droplets catching the light
- 2026-11-02 11:46 `out/render_wall_wet_v003.jpg` Wet v3: streaks only on the stone, the moss soaked evenly
- 2026-11-02 11:46 `out/render_boulder_wet_v001.jpg` Wet boulder: dark soaked granite, the film catching the sky, moss deeper green
- 2026-11-02 11:46 `out/maps_sheet_v002.jpg` Two-layer set: the bare granite under the moss (Gemini's moss-free edit), the moss depth for the coverage dial

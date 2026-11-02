# Plants: progress

Goal and done criteria: GOAL.md. Images: out/index.html.

- 2026-11-02 11:53 Started: goal + plan (GOAL.md); first plant: Boston fern at hero detail
- 2026-11-02 11:54 `out/refs_boston_fern_v001.jpg` Boston fern references (Commons). Read off them: fronds 40-90 cm arching out, upright young ones + croziers in the centre, old outer ones droop and yellow; pinnae 2.5-4 cm, alternate, ~9 mm apart, oblong, blunt, slightly falcate, an auricle at the upper base, crenate wavy margins, twisted; brown-green rachis; paler underside with sori near the margins; wiry runners hanging over the pot
- 2026-11-02 11:57 `out/render_fern_hero_v001.jpg` Boston fern v1 (seed 1, 45 fronds, 300k faces): the structure is there (crown, arching fronds, croziers, runners) but the fronds read like bead strings (pinnae 18 mm apart a side, should be ~9), too few fronds, too pale, overexposed, splayed like a spider plant
- 2026-11-02 11:58 `out/render_fern_hero_v002.jpg` v2: density right (pinnae ~9 mm a side, 91 fronds, 1.07 M faces), colour closer; but bent flat from the base (a starfish), bare stipes in the centre
- 2026-11-02 11:59 `out/render_fern_hero_v003.jpg` v3: still flat: a bug (the rim guard pushed every stipe near the soil out to the rim)
- 2026-11-02 11:59 `out/render_fern_hero_v004.jpg` v4: rim bug fixed: reads as a Boston fern; a bit upright (a shuttlecock, the references fountain over the rim)
- 2026-11-02 12:01 `out/render_fern_trio_v001.jpg` Three seeds (91, 104, 103 fronds, ~1.1-1.3 M faces each): three clearly different plants of the same species
- 2026-11-02 12:01 `out/render_fern_close_v001.jpg` Close-up at the crown: veins read; but sori on the upper sides (half the pinnae wound upside down), stipes like pale plastic straws, pinnae a touch narrow, bark chips are square tiles
- 2026-11-02 12:03 `out/render_fern_close_v002.jpg` Pinnae wider, stipes matte, bark as flakes; the spore dots are right (the camera looks up at the fronds' undersides) but too orange and regular
- 2026-11-02 12:03 `out/render_fern_backlit_v001.jpg` Backlit: far too dark, the fronds don't glow
- 2026-11-02 12:04 `out/render_fern_hero_v005.jpg` v5 (seed 4): a full fountain over the rim, rich green, a few old fronds browning; the standard to tweak from
- 2026-11-02 12:05 `out/render_fern_backlit_v002.jpg` Backlit (the key in front of the wall now): the centre glows yellow-green through the pinnae; the waxy sheen too strong at grazing angles (outer pinnae go silvery): next round
- 2026-11-02 12:26 `out/refs_monstera_v001.jpg` Monstera references (Commons). Read off them: leaves 30-60 cm, about as wide as long, cordate base; mature ones slit from the margin 1/3-2/3 in between pale lateral veins, an inner row of oval holes by the midrib; very glossy deep green, the panels between the veins slightly puffed; young leaves lime and entire; long smooth pale-green petioles, a swollen kink (geniculum) under the blade, a winged sheath at the base; brown aerial roots, often on a coir pole
- 2026-11-02 12:29 `out/render_monstera_hero_v001.jpg` Monstera v1 (seed 1): structure works (petioles, sheaths, slit + holed leaves from per-leaf images) but lily pads on sticks: leaves too small and held flat (real ones hang out and down from the geniculum), petioles straight spokes, too pale, the stem an open pipe
- 2026-11-02 12:30 `out/render_monstera_hero_v002.jpg` v2: leaves hang out and down from the geniculum; but milky, and saw-tooth edges (the leaf images were stored upside down: geometry and cut-out disagreed)
- 2026-11-02 12:30 `out/render_monstera_hero_v003.jpg` v3: images the right way up: clean edges, deeper green; too squat, mature leaves read as palm fronds (too many, too deep slits), the relief lumpy
- 2026-11-02 12:31 `out/render_monstera_hero_v004.jpg` v4: taller, broader segments, fewer slits: reads as a monstera; leaves still rigid flat sheets, petioles thin sticks
- 2026-11-02 12:31 `out/render_monstera_trio_v001.jpg` Three seeds (13, 13, 12 leaves): different plants; not yet at the fern's level
- 2026-11-02 12:33 `out/render_monstera_hero_v005.jpg` v5 (seed 3): the leaves corrugated (panels bulge between the lateral veins, margins wave), petioles with body
- 2026-11-02 12:33 `out/render_monstera_close_v001.jpg` Close (square-on, 0.75 m): glossy corrugated blade, crisp slits + holes; the petiole's open end pokes through, a zipper on some vein folds (a sharp crease across the grid), the sheen a touch plastic
- 2026-11-02 12:35 `out/render_monstera_close_v002.jpg` Capped petioles, smooth vein valleys, micro-texture in the sheen; a faint ridge artefact left on one leaf
- 2026-11-02 12:35 `out/render_monstera_hero_v006.jpg` v6 (seed 5): recognisable monstera; still a little CG (even colour, every leaf hangs alike)
- 2026-11-02 12:35 `out/render_monstera_backlit_v001.jpg` Backlit (seed 3): the light through the leaves, the holes dappling it; the most convincing so far
- 2026-11-02 12:51 `out/monstera_leaf_atlas_v001.jpg` Roman: "this one doesn't look very photoreal". The leaves drawn in code read as CG, so real-looking ones instead (as with the moss): 8 flat-lay leaves generated from the reference photos (young to mature), cut out (colour mask, the white fringe repainted, the stubs removed), relief from each image
- 2026-11-02 12:51 `out/render_monstera_close_v003.jpg` Atlas leaves + satin wax (Roman: "the sheen is weird and plasticky": no clear coat, roughness from the leaf's own relief, soft specular): reads as a real leaf
- 2026-11-02 12:51 `out/render_monstera_hero_v007.jpg` v7 (seed 5): atlas leaves, mirrored + tinted per leaf, the real sky to reflect; dappled shadows through the holes
- 2026-11-02 13:02 `out/render_monstera_hero_v008.jpg` No clipping (Roman: "some of the leaves are clipping through each other, fix that first"): every leaf tries up to 30 placements and keeps one clear of every leaf, petiole, the pot and the floor by >= 1.5 cm; seed 5: 0 contacts
- 2026-11-02 13:02 `out/render_monstera_trio_v002.jpg` Seeds 2-4: 0 contacts each; the plants 1.7 m apart (at 1.3 m neighbours' leaves crossed)

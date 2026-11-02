# Nordic moss on grey rock: a material study

Roman (2026-11-02): "I just want to see what it looks like and then we can see where it fits in ... that kind of fluffy moss ...
used a lot for decorations ... put in /out folder so I can see as it progresses, make sure it works with the replay system."
Method: docs/reference/pbr_from_single_reference.md (real reference in, our own aligned PBR set out).

## Goal

A photoreal, Elverum-true material set of soft, fluffy moss on grey granite/gneiss rock (and on the ground), good enough to sit
in a Cycles render of the gym interior at 1-3 m without reading as a texture on a box. No placement decided yet.

## Done when

1. References: real photos of the moss kinds around Elverum (boreal spruce/pine forest on granite/gneiss) collected, with
   the decorative "fluffy" one identified for Roman to confirm (out/refs_sheet_vNNN.jpg).
2. Maps: albedo, height (16-bit), normal (OpenGL), roughness, AO and a moss mask, generated from the references, every map
   aligned to the albedo (median offset < 0.5 px, logged), tileable or used where tiling doesn't show.
3. Shader: Blender material, rock and moss as separate shaders through the mask (dry matte rock, soft fully matte moss with
   sheen, moss height), only the albedo sRGB.
4. Test renders (Cycles, GPU, polite): a 3 x 3 m wall panel, a boulder and a ground patch under soft daylight, close and
   at 2-3 m, plus a side by side with a plain CC0 scan. They look right next to the reference photos (moss reads fluffy,
   rock reads dry, nothing floats, no seams or repeats visible).
5. Every step's image is in out/ as *_vNNN.jpg (never overwritten), committed, and shows in the replay
   (.capture/renders/replay.html, cameras "material nordic_moss/...").

## Layout

- refs/   downloaded reference photos (local only: not ours), refs/sources.json has every URL + licence
- work/   candidates, scratch, 16-bit intermediates (local only)
- maps/   the final maps we made (committed)
- out/    progress images, *_vNNN.jpg, newest last; out/index.html shows them all (auto-refreshing)
- PROGRESS.md  the log, one line per step

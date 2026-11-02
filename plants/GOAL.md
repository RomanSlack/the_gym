# Plants: procedural, realistic, no two alike

Roman (2026-11-02): "make some plants now that would look really good and make the procedural building method so they can be
randomized ... no 2 plants is the same in each category as well as the materials for super realistic materials ... big small
medium ... around walls in pots or even on full walls"; "go for it"; "we can do mini trees almost like bonsais too";
"extremely high detail, let's do one or 2 first then we'll tweak those to lay the level of quality and standards".

## Plan (agreed list, built one family at a time)

| size | where | plants |
|---|---|---|
| large 1.5-3 m | corners, by the glass, reception | olive tree, fiddle-leaf fig, bird of paradise, multi-stem birch |
| medium 0.5-1.5 m | floor pots along walls / partitions | monstera, snake plant, ZZ plant, Boston fern, philodendron |
| small < 0.5 m | shelves, reception, changing rooms | pothos, bird's nest fern, peperomia, sedums; mini trees like bonsai |
| walls | the spiral void, recovery | trailing pothos / philodendron, ferns, preserved moss (materials/nordic_moss) |

First: **Boston fern** (Nephrolepis exaltata), the hardest family (hundreds of pinnae per frond), at hero detail. It sets the
standard every other plant has to meet.

## Done when (per plant)

1. References: real photos of the plant (habit, frond, pinna close-up, backlit), out/refs_<plant>_vNNN.jpg.
2. Generator: plants/gen_<plant>.py, one seed = one plant; every structural number from the references (frond count, length,
   pinna count / shape / spacing, arch, droop, age mix: new croziers in the centre, old fronds yellowing outside).
   Different seeds give visibly different plants of the same species.
3. Material: leaf colour from the references with per-frond / per-pinna variation, translucency when backlit, a slight
   waxy sheen, midrib + veins; browned tips on a few.
4. Pot: designed by us in the gym's palette (oak, blackened steel, stone), soil with bark bits.
5. Renders (Cycles GPU, polite): three seeds side by side, a close-up of the fronds, a backlit view; beside the references
   they read as the real plant. Roman sets the bar from these.
6. Every image in out/ (*_vNNN.jpg, never overwritten), committed, in the replay (cameras "material plants/...").

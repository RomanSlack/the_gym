"""Rogue Dip Belt (refs/: ref_01 laid flat: the black nylon belt, a wider back piece with ROGUE in white in the
middle, grey stitched end panels, a steel ring at each end, the chain arched between them; ref_02 the logo; ref_03 the
stitching; ref_04 a ring, the carabiner and the chain; ref_05 in use, a plate hung). The linked page: 30.5 in long,
3 in nylon with a 4 in back piece, a 30 in, 1/4 in steel chain, two locking D carabiners, black. Fetched 2026-10-25.
The chain's links (1/4 in wire) are an estimate, as the chain kits' lead chain. Built to the two gates and README
point 9 (the links: pieces/rogue-chain-kits).

DESIGN SPEC (gate 1)
1. Use. Weighted dips and pull-ups: the belt round the hips, the chain through a plate or a kettlebell's handle, its
   carabiner clipped back to the ring.
2. Each mass named (ref_01 / ref_04): the belt, 3 in black nylon, double stitched; the 4 in back piece with ROGUE; the
   end panels; a steel ring sewn into each end; the chain, 30 in of 1/4 in links; the carabiners.
3. Adjustments. The chain's length through the load (clipped at any link).
4. Load path. The plate on the chain, the carabiners, the rings, the belt round the hips.
5. Fit range. 30.5 in with the chain round the hips: every user (1.55 / 1.78 / 1.95 m). No figure.
6. Size. Laid flat, 0.95 x 0.45 m.
Axes: metres, floor z = 0; the belt along x, the chain arched toward +y.
"""
import importlib.util
import math
import os

IN = 0.0254
L, W, WB, T = 30.5 * IN, 3 * IN, 4 * IN, 0.004


def _chain():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rogue-chain-kits", "model.py")
    spec = importlib.util.spec_from_file_location("rck", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CH = _chain()
LOOK = {
    "nylon": dict(color=(0.010, 0.010, 0.011), rough=0.85, coat=0.0, spec=0.2, bump=(3000, 0.12)),
    "grey": dict(color=(0.025, 0.025, 0.027), rough=0.85, coat=0.0, bump=(3000, 0.12)),
    "white": dict(color=(0.8, 0.8, 0.8), rough=0.5, coat=0.0),
}
LOOK.update({r: v for r, v in CH.LOOK.items() if r not in LOOK})
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_end": ((0.55, -0.35, 0.30), (0.40, 0.0, 0.0), 30),          # a ring, its carabiner, the chain
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    k.box("nylon", (0, 0, T / 2), (L - 0.06, W, T), soft=0.0015)                                    # the belt
    k.box("nylon", (0, 0, T + 0.0015), (0.30, WB, 0.003), soft=0.0015)                              # the back piece
    k.text("white", "ROGUE", (0, 0, T + 0.0031), 0.042, rx=0.0, depth=0.0004)
    for sx in (1, -1):
        k.box("grey", (sx * (L / 2 - 0.10), 0, T + 0.0008), (0.10, W - 0.004, 0.0016), soft=0.0005)   # end panel
        xr = sx * (L / 2 - 0.005)                       # the ring sewn into the end
        ring = [(xr + sx * 0.035 + 0.035 * math.cos(t), 0.035 * math.sin(t), 0.006) for t in
                [2 * math.pi * i / 32 for i in range(33)]]
        k.sweep("zinc", ring, k.circle(0.006, 10), soft=0.0)
        CH.carabiner(k, (xr + sx * 0.085, 0.05, 0), (sx * 0.4, 1, 0), size=0.075)
    light = (1 / 4 * IN / 2, 0.85 * IN, 0.95 * IN)
    arc = [(0.43 * math.cos(t), 0.08 + 0.30 * math.sin(t), 0) for t in [math.pi * i / 40 for i in range(41)]]
    CH.chain(k, arc, 34, *light)

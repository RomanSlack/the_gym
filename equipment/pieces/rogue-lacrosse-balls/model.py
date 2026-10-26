"""Rogue Lacrosse Balls (refs/: ref_01 one: red rubber, the round Rogue R mark embossed with ROGUE FITNESS round it;
ref_02 / ref_03 in use against a rig and on the floor). The linked page was not fetched: a lacrosse ball is 2.5 in
(regulation); the brief's peanuts are not on this page (two balls side by side stand in for one). Built to the two
gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Trigger points: pinned between the body and a wall, a rig or the floor and rolled.
2. Each mass named (ref_01): a solid rubber ball, 2.5 in, red, the R mark embossed in a ring.
3. Adjustments. None.
4. Load path. The body's weight on the ball, the wall or floor.
5. Fit range. 2.5 in: every user (1.55 / 1.78 / 1.95 m). No figure.
6. Size. Three loose and a pair together, 64 mm each.
Axes: metres, floor z = 0.
"""
import balls

IN = 0.0254
R = 1.25 * IN

LOOK = {
    "rubber": dict(color=(0.55, 0.02, 0.015), rough=0.55, coat=0.0, spec=0.4),
    "emboss": dict(color=(0.48, 0.015, 0.012), rough=0.6, coat=0.0),
}
VIEWS = {"three_quarter": (-30, 30, 1.0), "front": (0, 15, 1.0), "side": (90, 15, 1.0), "back_three_quarter": (150, 30, 1.0)}
DETAILS = {
    "detail_ball": ((0.0, -0.30, 0.10), (0.0, 0.0, 0.03), 25),          # the R mark
}


def ball(k, x, y, mark=True):
    c = (x, y, R)
    k.sphere("rubber", c, R, seg=48, soft=0.002)
    if mark:
        balls.label(k, "emboss", "R", c, R, 0.018, lat=0.25, lon=0.0, depth=0.0006)
        balls.label(k, "emboss", "ROGUE", c, R, 0.006, lat=0.25 + 0.30, lon=0.0, depth=0.0005)


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    for x in (-0.12, 0.0, 0.12):
        ball(k, x, -0.06)
    ball(k, -R, 0.10, mark=False)                       # a pair side by side (the peanut)
    ball(k, R, 0.10, mark=False)

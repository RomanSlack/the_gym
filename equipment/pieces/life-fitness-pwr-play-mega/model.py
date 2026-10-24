"""Life Fitness PWR Play mega maze: Roman, 2026-10-23: "make one that's just completely insane, I want a viral post".
A 6 x 6 grid of Cores on the Long connector (36 Cores, every neighbour joined: 60 crossbars, 21 x 21 m with its
stations), generated from two rules:
- every outer face carries a big station (pulldowns, rows, Power Pivots, assisted dip / chins, dual cables, triceps,
  stall bars, adjustable pulleys), so the maze's rim reads as a ring of machines;
- every aisle (the faces either end of a crossbar) gets a pair of stations that work facing each other: crossover
  posts both ends, a dual cable high facing a low, a dip facing a step, a rope pull facing handle storage, stall bars
  facing an open face, a row facing handle storage, the crossbars' pull-up handles cycling through their three styles.
Three hero angles at 16:9 for the post: from high and far (the scale, still legible as machines), down an aisle at
eye height, low from outside the corner.
Built by equipment/blender/pwr_play.py (build_layout).
"""
import random

import pwr_play as pp

LOOK = dict(pp.LOOK)
N = 6
D = pp.spacing("long")
RES = (1920, 1080)
OUTER = ["pulldown", "row", "powerpivot", "dipchin", "pulldown", "dualhigh", "row", "triceps", "stallbars",
         "pulldown", "adjustable", "duallow"]
PAIRS = [("crossover", "crossover"), ("dualhigh", "duallow"), ("dip", "step"), ("ropepull", "handles"),
         ("crossover", "crossover"), ("stallbars", None), ("row", "handles"), ("crossover", "crossover")]
HANDLES = ["flat", "neutral", "angled"]


def layout():
    cores = {f"{i},{j}": (i * D, j * D) for i in range(N) for j in range(N)}
    faces, bars = {}, []
    rnd = random.Random(23)
    n = 0
    for j in range(N):                                  # the aisles: a crossbar and a facing pair each
        for i in range(N):
            for di, dj, fa, fb in ((1, 0, "E", "W"), (0, 1, "N", "S")):
                if i + di >= N or j + dj >= N:
                    continue
                a, b = f"{i},{j}", f"{i + di},{j + dj}"
                bars.append((a, b, HANDLES[n % 3]))
                pa, pb = PAIRS[n % len(PAIRS)]
                if rnd.random() < 0.5:
                    pa, pb = pb, pa
                faces[(a, fa)], faces[(b, fb)] = pa, pb
                n += 1
    m = 0                                               # the rim: round the outside, a big station each face
    rim = [(f"{i},0", "S") for i in range(N)] + [(f"{N - 1},{j}", "E") for j in range(N)] + \
          [(f"{i},{N - 1}", "N") for i in reversed(range(N))] + [(f"0,{j}", "W") for j in reversed(range(N))]
    for key in rim:
        faces[key] = OUTER[m % len(OUTER)]
        m += 1
    return dict(cores=cores, faces=faces, bars=bars)


LAYOUT = layout()
C = (N - 1) * D / 2                                     # the grid's centre
QUICK_CHECK = True                                      # its modules are checked in full in the maze piece
VIEWS = {"three_quarter": (-35, 24, 1.0), "hero_top": (-30, 52, 1.5),
         "hero_end": (-90, 10, 1.0)}                    # last: turns the backdrop's wall to face down the aisles
DETAILS = {
    "hero_aisle": ((-3.2, 2.5 * D, 1.62), (5 * D, 2.5 * D - 0.2, 1.25), 20),      # down an aisle at eye height
    "hero_corner": ((-3.6, -4.4, 1.15), (C, C, 1.25), 22),                        # low and close at the corner
}


def build(k):
    pp.build_layout(k, LAYOUT)

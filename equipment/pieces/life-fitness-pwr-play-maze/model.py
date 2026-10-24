"""Life Fitness PWR Play maze: the upper body's interconnected cable modules (Roman: "a maze of modular cable towers",
equipment/README.md), a first layout to grow from. Six Cores in a 3 x 2 grid, each pair of neighbours joined by a
crossbar on the Long connector (the manual's 248 cm clear between the Cores); the corners are L junctions, the middle
two T junctions (three crossbars on a Core). Every station the builder has is in it: lat pulldowns, rows, triceps,
dual cable high and low, a dip, adjustable pulleys and crossover posts, panels on faces left blank.

Built by equipment/blender/pwr_play.py (build_layout); the modules' shapes are the life-fitness-pwr-play piece's.
Axes: metres, floor z = 0; Core A at the origin, the grid along +x (A B C) and +y (D E F behind A B C).
"""
import pwr_play as pp

LOOK = dict(pp.LOOK)
D = pp.spacing("long")
LAYOUT = dict(
    cores={"A": (0.0, 0.0), "B": (D, 0.0), "C": (2 * D, 0.0),
           "D": (0.0, D), "E": (D, D), "F": (2 * D, D)},
    faces={("A", "S"): "pulldown", ("A", "W"): "row", ("A", "E"): "crossover", ("A", "N"): "panel",
           ("B", "S"): "triceps", ("B", "W"): "crossover", ("B", "N"): "dualhigh",
           ("C", "S"): "pulldown", ("C", "E"): "row", ("C", "N"): "crossover",
           ("D", "N"): "duallow", ("D", "W"): "adjustable", ("D", "E"): "crossover", ("D", "S"): "row",
           ("E", "N"): "pulldown", ("E", "W"): "crossover", ("E", "E"): "panel", ("E", "S"): "dip",
           ("F", "N"): "dualhigh", ("F", "E"): "triceps", ("F", "W"): "panel"},
    bars=[("A", "B", "flat"), ("B", "C", "neutral"), ("D", "E", "angled"), ("E", "F", "flat"),
          ("A", "D", "neutral"), ("B", "E", "flat"), ("C", "F", "angled")],
)
VIEWS = {"three_quarter": (-35, 22, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0),
         "back_three_quarter": (145, 24, 1.0), "top": (0, 80, 1.0), "aerial": (-30, 42, 1.0)}
DETAILS = {
    "detail_t_junction": ((D + 1.3, -1.2, 3.1), (D, 0.0, 2.25), 35),        # Core B's top: three crossbars on it
    "detail_l_junction": ((2 * D + 1.4, -1.3, 3.1), (2 * D, 0.0, 2.25), 35),    # Core C's top: two
    "detail_dual_high": ((D + 1.2, 1.8, 2.0), (D, 0.85, 1.6), 40),        # B's dual cable high arm
    "detail_dual_low": ((1.2, D + 1.9, 1.0), (0.0, D + 0.8, 0.55), 40),   # D's dual cable low arm
    "detail_dip": ((D + 1.0, D - 1.7, 1.6), (D, D - 0.8, 1.2), 40),       # E's dip
    "detail_panel": ((D + 1.6, D - 0.6, 1.4), (D + 0.4, D, 1.1), 40),     # E's blank face
}


def build(k):
    pp.build_layout(k, LAYOUT)

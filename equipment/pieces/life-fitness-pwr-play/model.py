"""Life Fitness PWR Play - 5 Stations, Charcoal frame / Black upholstery (the configuration Roman linked): the Core with
the Pulldown (LPP-PD), the Row (LPP-RW), the Triceps Pushdown (LPP-TP) and the attached Adjustable Cable Crossover
(LPP-CC: the carriage on the Core's fourth face, the crossbar with the pull-up handles, the crossover's own tower).

Built from the shared builder equipment/blender/pwr_play.py (read off the PWR Play assembly instructions' drawings and
Life Fitness's Multi-Jungle figures; see its docstring), the look off the dealer's photos (refs/: ref_01 the studio shot
of the 5 Stations, ref_02 / ref_03 / ref_06 the crossover's carriages and the pull-up handles in use, ref_04 / ref_05 the
pulldown in use). The layout: the Core at the origin, the pulldown on its -y face, the row on -x, the triceps on +y, the
crossover's carriage on +x, the crossbar out along +x to the tower (the short connector, 73.5 in between top mounts).
Axes: metres, floor z = 0.
"""
import math

import pwr_play as pp

LOOK = dict(pp.LOOK)
VIEWS = {"three_quarter": (-35, 16, 1.0), "front": (0, 6, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (145, 20, 1.0),
         "top": (0, 80, 1.0)}
DETAILS = {
    "detail_core_top": ((0.95, -1.15, 2.75), (0.0, 0.0, 2.05), 45),       # the hub, the legs' arms, the top mounts
    "detail_stack": ((0.35, -1.45, 1.05), (0.0, -0.20, 0.75), 40),        # the pulldown's stack, the seat, the knee pads
    "detail_carriage": ((1.2, -0.85, 1.55), (1.80, 0.0, 1.35), 45),       # the tower's carriage and track
}

TOWER = (2.10, 0.0)                 # the crossover's tower (x, y), facing the Core
ZB = 2.34                           # the crossbar's centre: on the hub's side, on the tower's top plate


def build(k):
    c = (0.0, 0.0)
    pp.core(k, c)
    global PD, RW
    PD = pp.pulldown(k, c, (0, -1))
    RW = pp.row(k, c, (-1, 0))
    pp.triceps(k, c, (0, 1))
    pp.crossover_core(k, c, (1, 0))
    top = pp.tower(k, TOWER, (-1, 0))
    pp.beam(k, (pp.HUB[0] - 0.01, 0.0), (top[0], top[1]), ZB)


FIT_VIEWS = ("three_quarter", "side")


def fit():
    """The pulldown at the start of a rep (seated facing the Core, the thighs under the knee pads, the arms up to the
    bar) for a short, a middle and a tall user; the row at its start (seated on the bench facing the Core, the feet on
    the foot plate, the arms forward to the handle) for the middle user."""
    vs, zs = PD["seat"]
    out = {}
    for label, H in (("pulldown_short", 1.60), ("pulldown_middle", 1.78), ("pulldown_tall", 1.95)):
        s = H / 1.78
        hip = (0.0, -vs + 0.02, zs + 0.035 + 0.075 * s)
        knee = (0.0, hip[1] + 0.245 * H, hip[2])
        ankle = (0.0, knee[1], knee[2] - 0.246 * H)
        ball = (0.0, ankle[1] + 0.48 * 0.152 * H, ankle[2] - 0.039 * H)
        out[label] = dict(H=H, ball=ball, face=(0, 1), sole=0, shank=0, thigh=-90, trunk=-6, neck=0, arm=8, forearm=2,
                          arm_out=14)
    vf, zf = RW["foot"]
    H = 1.78
    out["row_middle"] = dict(H=H, ball=(-vf + 0.02, 0.0, zf - 0.03), face=(1, 0), sole=55, shank=-62, thigh=-98, trunk=-4,
                             neck=0, arm=128, forearm=100, arm_out=6)
    return out

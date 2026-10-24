"""Life Fitness PWR Play, the modern two-Core configuration Roman picked (his render, 2026-10-23: "this is the modern
one, the one we want"; Life Fitness's PWR Play 4 Stations): two Cores joined at their tops by the crossbar, the
Pulldown (LPP-PD) on the front of the left Core, the Row (LPP-RW) on the outer side of the right Core, the cable
crossover (LPP-CX) between them: each Core's inner face drives a carriage on its own stainless post standing under the
crossbar, the pull-up handles at the bar's middle; added at Roman's ask: the Triceps Pushdown (LPP-TP, the pulldown's boom
half as long, no bench) on the left Core's outer face and an Adjustable Pulley (LPP-AC, the carriage on a post outside)
on the right Core's front. Charcoal frame, black upholstery.

Built from the shared builder equipment/blender/pwr_play.py (the PWR Play assembly instructions' drawings and Life
Fitness's figures for the frame; the details off the real photos ref_02-ref_06: the rounded legs, the stacks, the
pulleys, the round crossbar, the carriage posts; Roman's render for the configuration; ref_07 / ref_08 the maker's
renders of the Core +4 and a two-Core set). ref_01 is the older single-Core + tower configuration (kept in the builder
as tower()), ref_09 the old Multi-Jungle generation (silver, a shrouded tower): neither is this piece.
Axes: metres, floor z = 0; the left Core at the origin, the right one at +x, the pulldown's user facing +y.
"""
import math
import os

import pwr_play as pp

LOOK = dict(pp.LOOK)
VIEWS = {"three_quarter": (-20, 12, 1.0), "front": (0, 5, 1.0), "side": (90, 5, 1.0), "back_three_quarter": (150, 20, 1.0),
         "top": (0, 78, 1.0), "render": (10, 7, 1.45)}     # "render": Roman's render's / ref_08's angle, to compare
D = 3.22                            # the Cores' centres apart (Roman's render / ref_08: 2.4 m clear between them)
ZB = 2.34                           # the crossbar's centre: on the hubs' sides, just under the caps' tops
HANDLES = os.environ.get("PWRPLAY_HANDLES", "flat")   # the crossbar's pull-up handles: "flat", "neutral", "angled"
POST = pp.A + 0.14                  # each carriage post: right beside its Core (ref_08), on the centreline under the bar
DETAILS = {
    "detail_core_top": ((0.75, -1.05, 2.85), (0.0, 0.0, 2.10), 45),       # the hub, the legs' bends, the top mounts
    "detail_stack": ((0.30, -1.40, 1.05), (0.0, -0.20, 0.70), 40),        # the pulldown's stack, the seat, the knee pads
    "detail_carriage": ((0.60, -1.10, 1.55), (POST, 0.0, 1.30), 45),      # the post, the carriage, its pulley, the handle
    "detail_plates": ((-1.15, -0.10, 0.62), (-0.275, 0.0, 0.52), 45),     # a bare stack (the triceps'): numbers, pin
    "detail_heavy": ((0.42, -1.05, 0.55), (0.0, -0.28, 0.48), 45),       # the pulldown's heavy stack past its post
    "detail_post_top": ((POST + 0.45, -0.85, 2.05), (POST, 0.0, 2.22), 40),  # the post's saddle on the bar, its pulley
    "detail_knee": ((-0.80, -1.05, 1.05), (-0.03, -0.52, 0.66), 40),     # the knee pads' pivot, sector plate, pop pin
    "detail_bar": ((D / 2, -1.30, 2.55), (D / 2, 0.0, 2.25), 45),         # the crossbar, the handles, the post's clamp
    "detail_row": ((D + 1.6, -1.1, 1.0), (D + 0.7, 0.0, 0.45), 40),       # the row's bench, foot plate, low pulley
}


def build(k):
    a, b = (0.0, 0.0), (D, 0.0)
    pp.core(k, a)
    pp.core(k, b)
    global PD, RW
    PD = pp.pulldown(k, a, (0, -1))
    RW = pp.row(k, b, (1, 0))
    pp.triceps(k, a, (-1, 0))                           # the shorter boom, no bench, on the left Core's outer face
    pp.adjustable_station(k, b, (0, -1))                # the adjustable pulley on the right Core's front, outside
    pp.crossover_station(k, a, (1, 0), POST, ZB - 0.04)
    pp.crossover_station(k, b, (-1, 0), POST, ZB - 0.04)
    pp.beam(k, (pp.HUB[0] - 0.003, 0.0), (D - pp.HUB[0] + 0.003, 0.0), ZB, handles=HANDLES, caps=False)   # hub to hub


FIT_VIEWS = ("three_quarter", "front")


def fit():
    """The pulldown at the start (seated facing the left Core, the thighs under the knee pads, the arms up to the bar)
    for a short, a middle and a tall user; the crossover (standing between the posts facing -y, the arms out to the
    handles) and the row (on the bench facing the right Core, the feet on the foot plate) for the middle user."""
    vs, zs = PD["seat"]
    out = {}
    for label, H in (("pulldown_short", 1.60), ("pulldown_middle", 1.78), ("pulldown_tall", 1.95)):
        s = H / 1.78
        hip = (0.0, -vs + 0.02, zs + 0.045 + 0.075 * s)
        knee = (0.0, hip[1] + 0.245 * H, hip[2])
        ankle = (0.0, knee[1], knee[2] - 0.246 * H)
        ball = (0.0, ankle[1] + 0.48 * 0.152 * H, ankle[2] - 0.039 * H)
        out[label] = dict(H=H, ball=ball, face=(0, 1), sole=0, shank=0, thigh=-90, trunk=-6, neck=0, arm=8, forearm=2,
                          arm_out=14)
    H = 1.78
    out["crossover_middle"] = dict(H=H, ball=(D / 2, -0.10, 0.0), face=(0, -1), sole=0, shank=4, thigh=0, trunk=6, neck=0,
                                   arm=180, forearm=180, arm_out=72, stance=0.30)
    vf, zf = RW["foot"]
    out["row_middle"] = dict(H=H, ball=(D + vf - 0.04, 0.0, zf - 0.04), face=(-1, 0), sole=55, shank=-62, thigh=-98,
                             trunk=-4, neck=0, arm=128, forearm=100, arm_out=6)
    return out

"""Rogue Monster Lite Half Rack, 24 in inside depth, MG Black, as it ships (posts, J-cups, pull-up bar, band pegs).

Built by eye from Rogue's photos (refs/: ref_01 / ref_02 the whole rack from the front left, ref_06 a J-cup, ref_07 the
nameplate crossmember, ref_08 the numbered holes, ref_09 a plate post on its plate, ref_10 the angled feet), held to
Rogue's spec: four 90.375 in uprights of 3 x 3 in 11-gauge steel with 5/8 in numbered holes, 49 in across the uprights,
24 in inside depth, 30 in angled front feet, eight plate posts (12.5 in loadable), a skinny pull-up bar, black-on-black
ROGUE nameplate. Shared builder: equipment/blender/rack.py (axes there: the lifter at -y, the bar along x).
"""
import rack

IN = 0.0254
S = dict(
    W=49 * IN, D=24 * IN, TB=3 * IN, H_front=90.375 * IN, H_back=90.375 * IN,
    hole=(5 / 16 * IN, 2 * IN), low=6 * IN,
    foot=dict(flat=18 * IN, slope=8 * IN, tab=4 * IN),
    side_top=1.5 * IN, angled=False,
    plate=dict(h_end=12 * IN, h_mid=7 * IN, text="ROGUE", size=0.17, slots=True),
    pullup=dict(r=0.5 * IN, below=2 * IN),
    posts=dict(z=[11 * IN, 31 * IN, 51 * IN, 71 * IN], len=12.5 * IN, r=0.95 * IN),
    jcup=54 * IN,
)
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # MG black
    "nameplate": dict(color=(0.012, 0.012, 0.013), rough=0.4, coat=0.15),                       # black on black
    "cut": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.13, 0.13, 0.14), rough=0.5, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "peg": dict(color=(0.55, 0.56, 0.58), rough=0.3, metal=1.0, coat=0.0),
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_jcup": ((-0.30, -0.95, 1.50), (-0.58, -0.40, 1.36), 45),     # a J-cup on its upright, the numbers
    "detail_foot": ((-1.10, -1.35, 0.45), (-0.58, -0.75, 0.12), 45),     # the angled foot, its pegs, the base plate
    "detail_top": ((-0.95, 1.25, 2.55), (0.0, 0.42, 2.10), 45),          # the nameplate crossmember from behind
}


def build(k):
    rack.build(k, S)

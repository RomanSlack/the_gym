"""Rogue Monster Collegiate Half Rack (single), MG Black, as it ships (posts, J-cups, pull-up bar, band pegs, red
nameplate).

Built by eye from Rogue's photos (refs/: ref_01 the whole rack from the front left, ref_03 the numbered 1 in holes,
ref_04 the angled foot, ref_05 the red nameplate and its 1 in bolts, ref_06 a plate post), held to Rogue's spec: 3 x 3 in
11-gauge steel, 1 in holes and hardware, 100.375 in front uprights, 90 in back uprights, angled crossmembers between
them, 24 in inside depth, 49 in across, 30 in front feet with 8 numbered holes, 12 in plate posts with plastic covering,
the laser-cut nameplate in Rogue red. Shared builder: equipment/blender/rack.py (the lifter at -y, the bar along x).
"""
import rack

IN = 0.0254
S = dict(
    W=49 * IN, D=24 * IN, TB=3 * IN, H_front=100.375 * IN, H_back=90 * IN,
    hole=(0.5 * IN, 2 * IN), low=6 * IN,
    foot=dict(flat=18 * IN, slope=8 * IN, tab=4 * IN),
    side_top=1.5 * IN, angled=True, front_drop=2.5 * IN,
    plate=dict(h_end=13 * IN, h_mid=8 * IN, text="ROGUE", size=0.20),
    pullup=dict(r=0.625 * IN, below=2.5 * IN),
    posts=dict(z=[13 * IN, 34 * IN, 55 * IN, 75 * IN], len=12 * IN, r=0.95 * IN),
    jcup=54 * IN,
)
LOOK = {
    "frame": dict(color=(0.012, 0.012, 0.013), rough=0.32, coat=0.25, bump=(900, 0.05)),       # MG black
    "nameplate": dict(color=(0.55, 0.012, 0.010), rough=0.38, coat=0.2),                        # Rogue red
    "cut": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.13, 0.13, 0.14), rough=0.5, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "peg": dict(color=(0.55, 0.56, 0.58), rough=0.3, metal=1.0, coat=0.0),
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_top": ((-1.25, -0.55, 2.75), (-0.20, 0.30, 2.20), 45),      # the angled crossmember, the red nameplate
    "detail_foot": ((-1.10, -1.35, 0.45), (-0.58, -0.75, 0.12), 45),    # the angled foot, its pegs, the base plate
    "detail_jcup": ((-0.30, -0.95, 1.50), (-0.58, -0.40, 1.36), 45),    # a J-cup, the 1 in holes and their numbers
}


def build(k):
    rack.build(k, S)

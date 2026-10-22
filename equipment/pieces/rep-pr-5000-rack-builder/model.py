"""REP PR-5000 power rack (Matte Black), built as REP's photo shows it: a six-post cage with a rear storage extension.

The PR-5000 is a rack builder (height, depth, attachments are chosen per order); this is the build in REP's matte black
photo (refs/: ref_01), with the details read off the others (ref_03 the numbered 1 in holes and their hardware, ref_04
the nameplate, ref_02 / ref_05 the rack in use). 3 x 3 in 11-gauge steel, 1 in holes, 93 in uprights; the 52 in width,
30 in inside depth and 16 in extension are read off the photo, not from a spec.
Shared builder: equipment/blender/rack.py (the lifter at -y, the bar along x).
Structure: front, back and rear uprights on base plates, side crossmembers top and bottom the whole depth, the pull-up
bar at the front, the silver REP nameplate under the back top crossmember, strap safeties between the front and back
uprights, J-cups, six plate posts on each rear upright (three long below, three short above).
"""
import rack

IN = 0.0254
S = dict(
    W=52 * IN, D=30 * IN, TB=3 * IN, H_front=93 * IN, H_back=93 * IN, ext=16 * IN,
    hole=(0.5 * IN, 2 * IN), low=4 * IN, foot=None,
    side_top=1.5 * IN, angled=False,
    plate=dict(h_end=7 * IN, h_mid=10 * IN, chamfer=2.5 * IN, text="REP", size=0.17),
    pullup=dict(r=0.625 * IN, below=2 * IN),
    posts=dict(z=[12.5 * IN, 32 * IN, 51 * IN, 66 * IN, 75 * IN, 84 * IN],
               len=[13 * IN, 13 * IN, 13 * IN, 7 * IN, 7 * IN, 7 * IN], r=0.95 * IN),
    straps=dict(z=24 * IN, sag=4 * IN),
    jcup=42 * IN,
)
LOOK = {
    "frame": dict(color=(0.010, 0.010, 0.011), rough=0.55, coat=0.0, bump=(900, 0.05)),        # matte black
    "nameplate": dict(color=(0.36, 0.37, 0.38), rough=0.42, metal=1.0, coat=0.0, aniso=0.4),    # brushed steel
    "cut": dict(color=(0.006, 0.006, 0.007), rough=0.6, coat=0.0),
    "hole": dict(color=(0.0, 0.0, 0.0), rough=1.0, coat=0.0),
    "label": dict(color=(0.13, 0.13, 0.14), rough=0.5, coat=0.0),
    "bolt": dict(color=(0.62, 0.63, 0.65), rough=0.28, metal=1.0, coat=0.0),
    "peg": dict(color=(0.55, 0.56, 0.58), rough=0.3, metal=1.0, coat=0.0),
    "plastic": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.0),
    "strap": dict(color=(0.012, 0.012, 0.013), rough=0.75, coat=0.0, spec=0.2, bump=(2500, 0.1)),  # nylon webbing
}
VIEWS = {"three_quarter": (-35, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 16, 1.0)}
DETAILS = {
    "detail_top": ((-0.30, -1.10, 2.55), (0.0, 0.42, 2.20), 45),        # the REP nameplate from the front
    "detail_strap": ((0.05, -1.05, 0.95), (-0.55, -0.10, 0.55), 45),    # a strap safety, a J-cup above it
    "detail_posts": ((1.45, 1.75, 1.20), (0.75, 0.95, 1.00), 45),       # the plate posts on a rear upright
}


def build(k):
    rack.build(k, S)

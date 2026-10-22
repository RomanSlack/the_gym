"""Atlantis Olympic Flat / Decline Bench Press with Pivot (P339), black frame, red upholstery, set to decline.

Built by eye from Atlantis's six renders (refs/: ref_02 flat, ref_03 + ref_04 from behind the towers, ref_05 + ref_06
decline three-quarters, ref_07 decline side), held to Atlantis's 93 x 66 x 52 in (L with the rollers x W x H).
The towers are the flat bench's (P337's model.py, reused), at this bench's height.
Axes: metres, floor z = 0, the bench runs along x, the lifter's head at +x under the bar; y across.
Between the towers a low cross tube the main beam runs into; the beam runs forwards to a front cross foot on two disc
feet. The pad's frame turns on a pivot bracket on the beam near the towers; a telescoping strut with a pop pin (red
knob) holds it at flat or decline; past the pad's foot an arm carries two pairs of red leg rollers.
"""
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "p337", Path(__file__).resolve().parents[1] / "atlantis-olympic-flat-bench-press-with-pivot-p337" / "model.py")
p337 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(p337)
p337.RACK_TOP, p337.S_TOP = 52 * 0.0254, 1.05
p337.HOOKS = (0.80, 0.98)
p337.HORNS = (0.38, 0.74)
p337.CROSS_Z = 0.22

LOOK = dict(p337.LOOK, red=dict(color=(0.42, 0.012, 0.014), rough=0.45, coat=0.2))
VIEWS = {"three_quarter": (-40, 14, 1.0), "front": (-90, 6, 1.0), "side": (0, 4, 1.0), "back_three_quarter": (130, 16, 1.0)}
DETAILS = {
    "detail_pivot": ((0.35, -0.75, 0.55), (0.0, 0.0, 0.3), 38),         # the pad's pivot on the beam
    "detail_rollers": ((-1.6, -0.7, 0.9), (-1.05, 0.0, 0.55), 38),      # the strut, the roller arm, the rollers
}

XR, TY = p337.XR, p337.TY
DECLINE = 14.0                  # deg, the foot end up
PIV = (0.0, 0.31)               # the pad frame's pivot (x, z)
PAD_S = (-0.20, 0.95)           # the pad along its frame from the pivot (towards the foot end)
PAD_T, PAD_W = 0.075, 0.30
BEAM_Z, FRONT_X = 0.22, -0.95   # the main beam's centre, the front cross foot
STRUT_AT = (-0.55, 0.68)        # the strut: its foot on the beam (x), its top along the pad frame (s)
ROLL_R, ROLL_L = 0.06, 0.15


def build(k):
    Y = (0, 1, 0); Z = (0, 0, 1)
    for s in (1, -1):
        p337.tower(k, s)
    yi = TY - p337.STORE[1] / 2
    k.bar("frame", (XR, -yi, BEAM_Z), (XR, yi, BEAM_Z), 0.10, 0.07, up=Z, cut0=((0, -yi, 0), Y), cut1=((0, yi, 0), Y), weld=True)
    # the main beam to the front cross foot on its discs
    k.bar("frame", (FRONT_X, 0, BEAM_Z), (XR - 0.035, 0, BEAM_Z), 0.10, 0.06, up=Y, cut1=((XR - 0.035, 0, 0), (1, 0, 0)), weld=True)
    k.text("label", "ATLANTIS", (-0.30, -0.0305, BEAM_Z), 0.03, depth=0.0008)
    fz = 0.10
    k.bar("frame", (FRONT_X + 0.03, -0.36, fz), (FRONT_X + 0.03, 0.36, fz), 0.06, 0.07, up=Z)
    for s in (1, -1):
        k.box("plastic", (FRONT_X + 0.03, s * 0.364, fz), (0.064, 0.008, 0.074), soft=0.003)
        p337.disc(k, FRONT_X + 0.03, s * 0.30, fz - 0.035)
        k.bar("frame", (FRONT_X + 0.03, s * 0.03, fz + 0.035), (FRONT_X + 0.25, s * 0.03, BEAM_Z - 0.05), 0.05, 0.05, up=Y,
              cut0=((0, 0, fz + 0.035), Z), cut1=((0, 0, BEAM_Z - 0.05), Z), weld=True)
    k.bar("frame", (FRONT_X + 0.03, 0, fz + 0.035), (FRONT_X + 0.03, 0, BEAM_Z - 0.05), 0.06, 0.06, up=Y,
          cut0=((0, 0, fz + 0.035), Z), cut1=((0, 0, BEAM_Z - 0.05), Z), weld=True)
    # the pivot bracket: two plates welded on the beam, an axle, the pad frame's hub between them
    for s in (1, -1):
        k.box("frame", (PIV[0], s * 0.045, (BEAM_Z + 0.05 + PIV[1] + 0.04) / 2), (0.10, 0.01, PIV[1] + 0.04 - BEAM_Z - 0.05), soft=0.002)
        k.bolt((PIV[0], s * 0.05, PIV[1]), "+y" if s > 0 else "-y", size=0.02)
    k.tube("frame", (PIV[0], -0.04, PIV[1]), (PIV[0], 0.04, PIV[1]), 0.026, seg=28)
    A = math.radians(DECLINE)
    u = (-math.cos(A), 0, math.sin(A)); n = (math.sin(A), 0, math.cos(A))   # along the frame towards the foot, its up
    fh = 0.06

    def on(s_, off):
        return (PIV[0] + u[0] * s_ + n[0] * off, 0, PIV[1] + u[2] * s_ + n[2] * off)
    k.bar("frame", on(PAD_S[0] + 0.03, 0), on(PAD_S[1] + 0.02, 0), fh, 0.08, up=Y)
    k.box("plastic", on(PAD_S[0] + 0.026, 0), (0.008, 0.084, fh + 0.004), ry=A, soft=0.003)
    L = PAD_S[1] - PAD_S[0]
    k.shaped_pad("pad", [(-PAD_W / 2, -L / 2), (PAD_W / 2, -L / 2), (PAD_W / 2, L / 2), (-PAD_W / 2, L / 2)],
                 on((PAD_S[0] + PAD_S[1]) / 2, fh / 2 + PAD_T / 2), n, (0, 1, 0), PAD_T, r=0.05, cushion=0.028)
    # the strut: an outer tube welded on the beam, the inner one up to a clevis under the frame, the pin's red knob
    sx, ss = STRUT_AT
    top = on(ss, -fh / 2 - 0.03)
    b0 = (sx, 0, BEAM_Z + 0.05)
    d = tuple(top[i] - b0[i] for i in range(3)); ln = math.sqrt(sum(v * v for v in d)); d = tuple(v / ln for v in d)
    mid = tuple(b0[i] + d[i] * ln * 0.55 for i in range(3))
    k.bar("frame", b0, mid, 0.06, 0.06, up=Y, cut0=((0, 0, BEAM_Z + 0.05), Z), weld=True)
    k.bar("frame", tuple(b0[i] + d[i] * ln * 0.4 for i in range(3)), top, 0.045, 0.045, up=Y)
    k.box("frame", on(ss, -fh / 2 - 0.015), (0.07, 0.07, 0.03), ry=A, soft=0.002)                # the clevis block
    pk = tuple(mid[i] - d[i] * 0.03 for i in range(3))
    k.box("frame", (pk[0], -0.04, pk[2]), (0.04, 0.02, 0.04), soft=0.003)                      # the pin's boss
    k.tube("steel", (pk[0], -0.03, pk[2]), (pk[0], -0.07, pk[2]), 0.007)
    k.cyl("red", (pk[0], -0.06, pk[2]), 0.02, 0.025, axis="y", seg=28, soft=0.006)
    # the roller arm past the pad's foot: two pairs of red rollers on steel rods through the arm
    e0 = on(PAD_S[1] + 0.02, 0)
    e1 = (e0[0] - 0.34, 0, e0[2] - 0.16)
    k.bar("frame", e0, e1, 0.06, 0.06, up=Y)
    ad = math.hypot(0.34, 0.16)
    k.box("plastic", (e1[0] - 0.34 / ad * 0.004, 0, e1[2] - 0.16 / ad * 0.004), (0.008, 0.064, 0.064), ry=-math.atan2(0.16, 0.34), soft=0.003)
    for c in (on(PAD_S[1] - 0.02, fh / 2 + ROLL_R + 0.005), tuple(e0[i] + (e1[i] - e0[i]) * 0.86 for i in range(3))):
        if c[2] > e0[2]:
            k.bar("frame", on(PAD_S[1] - 0.02, 0), c, 0.04, 0.04, up=Y)                            # the upper pair's post
        k.tube("steel", (c[0], -(0.03 + ROLL_L + 0.01), c[2]), (c[0], 0.03 + ROLL_L + 0.01, c[2]), 0.0125)
        for s in (1, -1):
            k.cyl("pad", (c[0], s * (0.03 + ROLL_L / 2 + 0.004), c[2]), ROLL_R, ROLL_L, axis="y", seg=40, soft=0.012)
            k.cyl("plastic", (c[0], s * (0.03 + ROLL_L + 0.006), c[2]), 0.02, 0.008, axis="y", seg=24)

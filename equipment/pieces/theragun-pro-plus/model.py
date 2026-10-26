"""Therabody Theragun PRO Plus (refs/: ref_01 the gun: a black triangular handle loop, the motor head with its blue
disc on the side, the arm down to a round attachment, the screen on top; ref_02 the screen and dial; ref_03 the red
light; ref_04 / ref_05 in use). The linked page was not fetched: the size (about 25 x 17 x 7 cm) is an estimate off
ref_01 against the hands in ref_04. Laid on its side, the blue disc up. Built to the two gates and README point 9.

DESIGN SPEC (gate 1)
1. Use. Percussive massage: held by any side of the triangle handle, the attachment pressed into a muscle.
2. Each mass named (ref_01): the triangle handle (a thick loop, the battery in it); the head, a cylinder with the blue
   disc on its side; the arm down from the head to the attachment, a ball; the screen and dial on top; the light.
3. Adjustments. The speed (dial and screen), the attachment, the arm's angle.
4. Load path. The hand on the handle, the head, the arm, the attachment on the muscle.
5. Fit range. A handle in reach of every user's own back and legs (the triangle's sides). No figure.
6. Size. About 0.25 x 0.17 x 0.07 m lying.
Axes: metres, floor z = 0; lying in the x-y plane.
"""
import math

T = 0.07                              # its thickness lying

LOOK = {
    "body": dict(color=(0.02, 0.02, 0.022), rough=0.5, coat=0.1),
    "blue": dict(color=(0.01, 0.12, 0.45), rough=0.3, metal=0.5),
    "screen": dict(color=(0.01, 0.01, 0.012), rough=0.1, coat=0.6),
    "red": dict(color=(0.9, 0.05, 0.03), rough=0.4, coat=0.0, emit=1.0),
}
VIEWS = {"three_quarter": (-30, 40, 1.0), "front": (0, 30, 1.0), "side": (90, 30, 1.0), "back_three_quarter": (150, 40, 1.0)}
DETAILS = {
    "detail_head": ((-0.05, -0.30, 0.25), (-0.05, -0.02, 0.03), 30),    # the head, the blue disc
}


def build(k):
    k.look(**{r: v for r, v in LOOK.items() if r not in k.looks})
    hc = (-0.06, 0.0)                                   # the head's middle
    loop = [(hc[0], hc[1] + 0.035), (0.13, 0.055), (0.11, -0.065), (hc[0] + 0.03, -0.02), (hc[0], hc[1] + 0.035)]
    k.sweep("body", [(x, y, T / 2) for x, y in loop], k.rect(0.032, T * 0.85, 0.012), bend=0.03, up=(0, 0, 1), soft=0.0)
    k.cyl("body", (hc[0], hc[1], T / 2), 0.048, T, seg=48, soft=0.008)                              # the head
    k.cyl("blue", (hc[0], hc[1], T + 0.001), 0.040, 0.003, seg=48, soft=0.001)                      # the blue disc
    k.tube("body", (hc[0], hc[1] - 0.03, T / 2), (hc[0] - 0.02, hc[1] - 0.10, T / 2), 0.022, seg=24)  # the arm
    k.sphere("body", (hc[0] - 0.022, hc[1] - 0.115, T / 2), 0.026, seg=32, soft=0.002)               # the attachment
    k.box("screen", (0.0, 0.0575, T / 2), (0.06, 0.008, 0.035), rz=0.12, soft=0.002)                  # the screen
    k.box("red", (hc[0] + 0.040, hc[1] - 0.026, T / 2), (0.012, 0.006, 0.03), rz=-0.6, soft=0.002)     # the light, on the head

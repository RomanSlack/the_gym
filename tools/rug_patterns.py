"""Generate the woven patterns of the three bridge rugs (Roman, 2026-10-12: "patterned sort of geometric style carpets ... modern
nice colors that fit the vibe ... 3 of them, all tasteful").

Flatweave wool after the Norwegian åkle (the old woven coverlets with stepped lozenges, 'skillbragd'), drawn modern: few colours,
big calm fields, every shape stepped on the weave grid (2 cm picks), a thin charcoal border. The three tell one sequence down the
bridge towards the gym: a lattice of small lozenges (cafe end), one large concentric lozenge (the middle), stepped chevrons
pointing into the gym (gym end). Palette: oat ground, fjord blue, moss, glacier teal (Elva's water), a little lingon, charcoal.
Image x = along the bridge (east -> west reads left -> right is NOT assumed: x grows towards +x, east), y = across.
Writes docs/art/rug_<name>_v<N>.png at 5 mm per pixel (a changed pattern gets the next version, never overwritten).   terrain/.venv/bin/python tools/rug_patterns.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "art"
PX = 0.005          # 5 mm per pixel
PICK = 0.02         # the weave grid: every shape steps by 2 cm
C = {"oat": (205, 192, 168), "oat_d": (188, 174, 148), "fjord": (44, 66, 92), "moss": (88, 98, 60), "teal": (110, 148, 148),
     "lingon": (138, 44, 36), "char": (40, 40, 42)}
L, W = 2.6, 4.0     # rug size (m): along the bridge x across it


def canvas():
    nx, ny = int(L / PX), int(W / PX)
    x = (np.arange(nx) + 0.5) * PX - L / 2
    y = (np.arange(ny) + 0.5) * PX - W / 2
    X, Y = np.meshgrid(x, y)  # image rows = y, cols = x
    q = lambda v: np.round(v / PICK) * PICK  # snap to the weave grid -> stepped edges
    return q(X), q(Y), np.zeros(X.shape + (3,), np.uint8)


def paint(img, mask, col):
    img[mask] = C[col]


def border(img, X, Y):
    m_out = (np.abs(X) > L / 2 - 0.06) | (np.abs(Y) > W / 2 - 0.06)
    m_in = ((np.abs(X) > L / 2 - 0.12) | (np.abs(Y) > W / 2 - 0.12)) & ~m_out
    paint(img, m_out, "char"); paint(img, m_in, "oat")
    m_line = ((np.abs(X) > L / 2 - 0.14) | (np.abs(Y) > W / 2 - 0.14)) & ~m_in & ~m_out
    paint(img, m_line, "char")


def lattice():
    """Cafe end: a calm field of small stepped lozenges in fjord on oat, a lingon pip in every fourth, offset rows."""
    X, Y, img = canvas()
    img[:] = C["oat"]
    p = 0.46
    u, v = (X / p) % 1 - 0.5, (Y / p) % 1 - 0.5
    u2, v2 = ((X + p / 2) / p) % 1 - 0.5, ((Y + p / 2) / p) % 1 - 0.5
    for uu, vv, pip in ((u, v, True), (u2, v2, False)):
        d = np.abs(uu) + np.abs(vv)
        paint(img, (d < 0.27) & (d > 0.18), "fjord")
        if pip:
            sel = ((np.floor(X / p) + np.floor(Y / p)) % 4 == 0) & (d < 0.1)
            paint(img, sel, "lingon")
        else:
            paint(img, d < 0.07, "teal")
    border(img, X, Y)
    return img


def lozenge():
    """The middle: one large concentric stepped lozenge, bands of fjord, teal, oat, moss to a lingon heart; corners in quiet oat_d."""
    X, Y, img = canvas()
    img[:] = C["oat"]
    d = np.abs(X) / (L / 2 - 0.2) + np.abs(Y) / (W / 2 - 0.2)  # 1 at the inner border, along the diagonals
    bands = [(1.0, "oat_d"), (0.92, "fjord"), (0.84, "oat"), (0.78, "teal"), (0.70, "oat"), (0.64, "fjord"), (0.52, "oat"),
             (0.46, "moss"), (0.34, "oat"), (0.28, "fjord"), (0.16, "oat"), (0.1, "lingon")]
    for r, col in bands:
        paint(img, d < r, col)
    # a small stepped lozenge in each corner, as in the old åkle
    for sx in (-1, 1):
        for sy in (-1, 1):
            cd = np.abs(X - sx * (L / 2 - 0.42)) / 0.22 + np.abs(Y - sy * (W / 2 - 0.42)) / 0.22
            paint(img, (cd < 1.0) & (cd > 0.55), "fjord"); paint(img, cd < 0.3, "teal")
    border(img, X, Y)
    return img


def chevrons():
    """Gym end: stepped chevrons pointing west, into the gym (the salmon ladder's steps), moss + fjord + teal on oat."""
    X, Y, img = canvas()
    img[:] = C["oat"]
    t = X - np.abs(Y) * 0.55        # chevron coordinate: the point at Y = 0 is the westmost, so each V points west (-x), into the gym
    p = 0.5
    ph = (t / p) % 1
    k = np.floor(t / p)
    cols = ["fjord", "teal", "moss"]
    for i in range(3):
        sel = (ph > 0.12) & (ph < 0.4) & ((k % 3) == i)
        paint(img, sel, cols[i])
    paint(img, (ph > 0.46) & (ph < 0.5), "char")
    paint(img, (np.abs(Y) < 0.04) & (ph > 0.12) & (ph < 0.4), "lingon")  # a lingon stitch at every point
    border(img, X, Y)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn, ver in (("lattice", lattice, 2), ("lozenge", lozenge, 1), ("chevrons", chevrons, 2)):  # v2: lattice opened up, chevrons point west
        p = OUT / f"rug_{name}_v{ver}.png"
        if p.exists():
            print("kept (never overwritten):", p.name)
            continue
        Image.fromarray(fn()[::-1]).save(p)  # row 0 = +y edge (image top)
        print("wrote", p.name)

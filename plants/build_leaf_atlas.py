"""A leaf atlas: generated flat-lay leaf photos (work/<plant>_gen/*_0.webp: Gemini from the reference photos, the leaf tip up, its
base down, on white) -> clean cut-out leaves for the plant generators. Started for the monstera (Roman: "this one doesn't look
very photoreal": the leaves drawn in code read as CG; real-looking leaves in, like the moss); used by every plant since.

Per leaf: maps/<plant>/<name>_col.png (RGBA: the leaf, its slits and holes cut out, the white fringe at the edge replaced by
leaf colour, a petiole stub removed; the leaf's own proportions kept, 2048 px tall), <name>_bump.png (relief from the image:
veins in grooves, the panels between them puff), and atlas.json (maturity, aspect, where the petiole joins, the midrib's
column).

    python3 plants/build_leaf_atlas.py monstera | snake | ...
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
PLANT = sys.argv[1] if len(sys.argv) > 1 else "monstera"
SRC = HERE / "work" / ("mleaf_gen" if PLANT == "monstera" else f"{PLANT}_gen")
OUT = HERE / "maps" / PLANT
MATURITY = {"leafm1": 1.0, "leafm2": 0.95, "leafm3": 0.85, "leafm4": 0.9, "leafs1": 0.6, "leafs2": 0.5, "leafy1": 0.15, "leafy2": 0.25,
            "snaket1": 1.0, "snaket2": 0.95, "snaket3": 0.55, "snaket4": 0.9, "snakel1": 0.95, "snakel2": 0.8}
SQUARE = PLANT == "monstera"
SOLID = ("snake", "maple", "pothos")
KEEP_STEM = ("maple",)                           # the maple's petiole is part of the leaf (it attaches the card to its twig)                               # no holes in these leaves: pale bands must not read as background                    # (the monstera's maps were made square; the rest keep their proportions)
HPX = 2048

OUT.mkdir(parents=True, exist_ok=True)
atlas = {}
for f in sorted([g for pat in (("sprig*_0.webp", "tip*_0.webp") if PLANT == "bonsai" else ("leaf*_0.webp",) if PLANT in ("maple", "pothos") else ("*_0.webp",)) for g in SRC.glob(pat)]):   # (bonsai: the bark images aren't leaves)
    name = f.stem.replace("_0", "")
    img = cv2.cvtColor(cv2.imread(str(f)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    hsv = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32) / 255
    # the leaf by its colour (green / the yellowish midrib are saturated; the soft grey drop shadow under the lobes is not)
    m = (hsv[..., 1] > 0.2) | ((img[..., 1] - np.maximum(img[..., 0], img[..., 2]) > 0.05) & (img.min(-1) < 0.8)) | (img.max(-1) < 0.62)
    m = m.astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)   # the leaf only
    if PLANT in SOLID:                                                   # leaves with no holes: everything inside the outline
        ff = m.copy() * 255; mask_ = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
        cv2.floodFill(ff, mask_, (0, 0), 128)
        m = (ff != 128).astype(np.uint8)
    inv = 1 - m                                                          # specular glints read as background: fill the tiny ones
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < (40 if f.stem.startswith("tip") else 600):   # (lacy tips keep their gaps)
            m[lab == i] = 1
    H, W = m.shape
    ys, xs = np.nonzero(m)
    cx = int(np.median(xs[ys < ys.min() + (ys.max() - ys.min()) * 0.5]))    # the midrib's column (upper half)
    # a pale, near-white midrib reads as background by colour: keep its column by the looser not-white test
    loose = ((1 - img.min(-1)) > 0.1).astype(np.uint8)
    band = np.zeros_like(m); band[ys.min():ys.max() + 1, cx - 40:cx + 41] = 1
    m = np.maximum(m, loose * band)
    # the petiole stub: thin, below the sinus; opened away in the bottom-centre only
    low = np.zeros_like(m); low[int(ys.min() + 0.75 * (ys.max() - ys.min())):, cx - W // 8:cx + W // 8] = 1
    opened = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (131, 131)))
    m = np.where(low > 0, opened, m) if PLANT not in KEEP_STEM else m
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # the petiole joint: the sinus apex, scanning up the midrib column from the bottom
    col = m[:, cx]
    yj = y1
    while yj > y0 and col[yj] == 0:
        yj -= 1
    # the white fringe: re-colour a band at the edge from the leaf's inside
    band = (cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2) - cv2.erode(m, np.ones((3, 3), np.uint8), iterations=3)).astype(np.uint8)
    rgb8 = (img * 255).astype(np.uint8)
    fixed = cv2.inpaint(rgb8, band, 5, cv2.INPAINT_TELEA).astype(np.float32) / 255
    alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    # crop square-ish around the leaf with a small margin, the leaf base at the bottom
    pad = 12
    x0, x1, y0, y1 = max(x0 - pad, 0), min(x1 + pad, W - 1), max(y0 - pad, 0), min(y1 + pad, H - 1)
    rgba = np.dstack([fixed, alpha])[y0:y1 + 1, x0:x1 + 1]
    h, w = rgba.shape[:2]
    if SQUARE:
        rgba = cv2.resize(rgba, (1536, 1536), interpolation=cv2.INTER_AREA)
    else:
        rgba = cv2.resize(rgba, (max(int(round(HPX * w / h)), 64), HPX), interpolation=cv2.INTER_AREA)
    # relief: veins (lighter, thin) in grooves; panels puff; from the luminance's high-pass
    lum = cv2.cvtColor((rgba[..., :3] * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    hp = lum - cv2.GaussianBlur(lum, (0, 0), 6)
    puff = -cv2.GaussianBlur(hp, (0, 0), 14)
    bump = 0.5 - hp * 3.0 + puff * 4.0
    bump = (bump - np.percentile(bump, 1)) / (np.percentile(bump, 99) - np.percentile(bump, 1) + 1e-6)
    out = (np.clip(rgba, 0, 1) * 255).astype(np.uint8)
    cv2.imwrite(str(OUT / f"{name}_col.png"), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    cv2.imwrite(str(OUT / f"{name}_bump.png"), (np.clip(bump, 0, 1) * 255).astype(np.uint8))
    atlas[name] = {"maturity": MATURITY.get(name, 0.7), "aspect": round(w / h, 4),
                   "joint_v": round(1 - (yj - y0) / h, 4),          # from the bottom (UV v)
                   "midrib_u": round((cx - x0) / w, 4)}
    print(name, atlas[name])
(OUT / "atlas.json").write_text(json.dumps(atlas, indent=1))

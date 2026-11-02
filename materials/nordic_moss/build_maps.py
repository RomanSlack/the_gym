"""Nordic moss on grey granite: the generated candidates -> one consistent PBR set in maps/ (GOAL.md, PROGRESS.md).

Inputs (work/, local): albedo_src.png (Gemini candidate A), gen/height1, rough2; the
CC0 scans in ~/.cache/the_gym/textures (tools/assets.py) for real captured micro detail: ambientCG Moss002 (moss fibres),
Rock046S (granite grain). The patch is taken as 2 x 2 m.

    python3 materials/nordic_moss/build_maps.py      -> maps/*.png + work/preview_maps.jpg + work/align.txt
"""
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from pbr_align import align, load, lum, unit  # noqa: E402

W, M = HERE / "work", HERE / "maps"
SCAN = Path.home() / ".cache" / "the_gym" / "textures"
M.mkdir(exist_ok=True)
log = []

alb = load(W / "albedo_src.png")
S = alb.shape[0]
blur = lambda a, s: cv2.GaussianBlur(a, (0, 0), s)


def tiled(p, n, gray=False):
    """a CC0 scan map tiled n x n over the patch (its real scale: n tiles per 2 m)"""
    t = load(p)
    if gray and t.ndim == 3:
        t = lum(t)
    t = cv2.resize(t, (-(-S // n), -(-S // n)), interpolation=cv2.INTER_AREA)
    return np.tile(t, (n, n) + (1,) * (t.ndim - 2))[:S, :S]


# --- the moss mask, from the albedo's colour (moss = yellow-green, saturated); a sharp one for shading, a soft one for height
hsv = cv2.cvtColor((alb * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
raw = ((h > 55) & (h < 120) & (s > 0.28)).astype(np.uint8)
raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(np.float32)
mask = blur(raw, 2).clip(0, 1)
mask_h = blur(raw, 18).clip(0, 1)
log.append(f"moss cover {raw.mean() * 100:.0f} %")

# --- align every generated map to the albedo
maps = {}
# (checked 2026-11-02 by the overlap of the moss mask with each map's own moss shapes: aligning lifts height1 from 0.48 to
# 0.57 IoU but makes rough2 (0.90 -> 0.88) and ao1 worse; so only the height is warped, the AO is computed from the final height)
iou = lambda h, m_: max(((h > np.percentile(h, q)) & m_).sum() / ((h > np.percentile(h, q)) | m_).sum() for q in range(35, 70, 3))
src = lum(load(W / "gen" / "height1_0.webp"))
maps["height"], b, a = align(alb, src)
log.append(f"height1 aligned: median shift {b:.2f} -> {a:.2f} px; moss overlap (IoU) {iou(src, raw > 0):.2f} -> {iou(maps['height'], raw > 0):.2f}")
maps["rough"] = lum(load(W / "gen" / "rough2_0.webp"))
log.append(f"rough2 as generated: moss overlap (IoU) {iou(maps['rough'], raw > 0):.2f}")

# --- albedo: rock cooled to Elverum grey granite (the candidate was beige), baked shadows lifted (only spots darker than around)
L = lum(alb)[..., None]
rock = (1 - mask)[..., None]
cool = (L + (alb - L) * 0.35) * np.float32([0.97, 1.0, 1.035])
a2 = alb * (1 - rock) + cool * rock
l2 = lum(a2)
around = blur(l2, 25) * 0.75
dark = np.clip((around - blur(l2, 3)) / (around + 1e-6), 0, 1)
a2 = np.clip(a2 * (1 + blur(dark, 3) * 0.6)[..., None], 0, 1)

# --- height: the generated big forms, the dark rings it put round every cushion lifted to the rock's level (they read as
# trenches), then real captured detail from the scans: moss fibres on the moss, granite grain on the rock; steep slopes smoothed
ht = maps["height"]
rim = (cv2.dilate(raw, np.ones((41, 41), np.uint8)) - raw).clip(0, 1)
rock_lvl = np.median(ht[(raw == 0) & (rim == 0)])
ht = np.where(rim > 0, np.maximum(ht, rock_lvl * 0.97), ht)
ht = blur(ht, 1.2)
# the cushions' domes from the albedo's own moss outline (so colour and relief can't disagree): a rounded rise over ~6 cm in
# from the edge, blended with the generated forms for their irregularity
dist = cv2.distanceTransform(raw.astype(np.uint8), cv2.DIST_L2, 5)
dome = 1 - (1 - np.minimum(dist / 60.0, 1)) ** 2
ht = 0.45 * (ht - ht.min()) / (ht.max() - ht.min()) + 0.55 * (0.25 + 0.75 * blur(dome, 4)) * mask_h + 0.55 * 0.25 * (1 - mask_h)
# (v2: the moss scan's bumps at 0.10 terraced the cushions in close-ups; its fibres now live in the normal only, a light finer
# lumpiness from it stays)
moss_d = tiled(SCAN / "ambientcg" / "Moss002" / "disp.png", 5, True)
rock_d = tiled(SCAN / "ambientcg" / "Rock046S" / "disp.png", 2, True)
ht = ht + blur(moss_d - moss_d.mean(), 2) * 0.025 * mask_h + (rock_d - rock_d.mean()) * 0.05 * (1 - mask_h)
ht = (ht - ht.min()) / (ht.max() - ht.min())
gx, gy = cv2.Sobel(ht, cv2.CV_32F, 1, 0), cv2.Sobel(ht, cv2.CV_32F, 0, 1)
slope = np.sqrt(gx ** 2 + gy ** 2)
wst = blur((slope > np.percentile(slope, 88)).astype(np.float32), 6)
wst = np.clip(wst / (wst.max() + 1e-6) * 1.5, 0, 1)
ht = ht * (1 - wst) + blur(ht, 4) * wst

# --- normal: big shapes rebuilt from the height (so they can't disagree), fine detail from the scans' real normals
k = 6.0
nx, ny = -cv2.Sobel(ht, cv2.CV_32F, 1, 0, ksize=3) * k, cv2.Sobel(ht, cv2.CV_32F, 0, 1, ksize=3) * k
base = unit(np.dstack([nx, ny, np.ones_like(nx)]))
dm = tiled(SCAN / "ambientcg" / "Moss002" / "nor_gl.png", 5) * 2 - 1
dm = dm - np.dstack([blur(dm[..., i], 5) for i in range(3)]) + np.float32([0, 0, 1])   # fibres only: its clump shapes repeated as scallops
dr = tiled(SCAN / "ambientcg" / "Rock046S" / "nor_gl.png", 2) * 2 - 1
det = unit(dm * mask[..., None] + dr * (1 - mask[..., None]))
nrm = unit(np.dstack([base[..., 0] + det[..., 0], base[..., 1] + det[..., 1], base[..., 2] * det[..., 2]]))   # whiteout blend

# --- roughness: dry granite 0.62-0.92 from the generated map, moss fully matte; AO kept weak
r = maps["rough"]
r = (r - np.percentile(r, 2)) / (np.percentile(r, 98) - np.percentile(r, 2) + 1e-6)
rough = (0.62 + 0.30 * r.clip(0, 1)) * (1 - mask) + 1.0 * mask
cav = np.maximum(blur(ht, 10) - ht, 0) + 0.5 * np.maximum(blur(ht, 35) - ht, 0)   # cavities of the final height
ao = 1 - (cav / (np.percentile(cav, 99.5) + 1e-6)).clip(0, 1) * 0.45

w8 = lambda p, a: cv2.imwrite(str(p), (a.clip(0, 1) * 255).astype(np.uint8))
cv2.imwrite(str(M / "albedo.png"), cv2.cvtColor((a2 * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
cv2.imwrite(str(M / "height.png"), (ht.clip(0, 1) * 65535).astype(np.uint16))
cv2.imwrite(str(M / "normal.png"), cv2.cvtColor(((nrm * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
w8(M / "roughness.png", rough); w8(M / "ao.png", ao); w8(M / "mask_shade.png", mask); w8(M / "mask_height.png", mask_h)

# --- a contact sheet of the set
tiles = [a2, ht, nrm * 0.5 + 0.5, rough, ao, mask]
names = ["albedo (rock cooled, shadows lifted)", "height (16-bit)", "normal (from height + scan detail)", "roughness", "AO (from the height, weak)", "moss mask"]
T = 640
sheet = np.full((T * 2 + 60, T * 3, 3), 20, np.uint8)
for i, (t, n) in enumerate(zip(tiles, names)):
    t = cv2.resize(t if t.ndim == 3 else np.dstack([t] * 3), (T, T), interpolation=cv2.INTER_AREA)
    x, y = (i % 3) * T, (i // 3) * (T + 30) + 30
    sheet[y:y + T, x:x + T] = (t.clip(0, 1) * 255).astype(np.uint8)
    cv2.putText(sheet, n, (x + 8, y - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
cv2.imwrite(str(W / "preview_maps.jpg"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
(W / "align.txt").write_text("\n".join(log) + "\n")
print("\n".join(log))

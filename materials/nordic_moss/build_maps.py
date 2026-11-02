"""Nordic moss on grey granite: the generated candidates -> one consistent PBR set in maps/ (GOAL.md, PROGRESS.md).

Inputs (work/, local): albedo_src.png (Gemini candidate A), gen/height1, rough2, rockonly2 (the moss removed); the
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

# --- albedo, in two layers so the moss can be dialled (v3, the boulder: moss only on the tops / shaded sides): the bare granite
# under everything (the original rock exactly where there is no moss, Gemini's moss-free edit underneath it), the moss on top.
# The rock graded once: cooled to Elverum grey granite (the candidate was beige), baked shadows lifted, mid grey (v2 read white)
gen_rock, b_, a_ = align(alb, load(W / "gen" / "rockonly2_0.webp"))
log.append(f"rockonly2 aligned: {b_:.2f} -> {a_:.2f} px")
under = blur(cv2.dilate(raw, np.ones((9, 9), np.uint8)), 4).clip(0, 1)[..., None]
rk = alb * (1 - under) + gen_rock * under
L = lum(rk)[..., None]
rk = (L + (rk - L) * 0.35) * np.float32([0.97, 1.0, 1.035])
l2 = lum(rk)
around = blur(l2, 25) * 0.75
dark = np.clip((around - blur(l2, 3)) / (around + 1e-6), 0, 1)
rk = rk * (1 + blur(dark, 3) * 0.6)[..., None]
rk = np.clip(rk * (0.42 / lum(rk).mean()), 0, 1)
a2 = rk * (1 - mask[..., None]) + alb * mask[..., None]

# --- height, also in two layers on one scale: the rock (the generated forms where it's bare, the rock level under the moss,
# granite grain from the scan) and the moss cushions on it (domes from the albedo's own moss outline, rising over ~6 cm in from
# the edge, with the generated forms' irregularity). The dark rings the generator put round every cushion (they read as
# trenches) lifted to the rock's level. Steep slopes smoothed (the method's "curtains").
g = maps["height"]
rim = (cv2.dilate(raw, np.ones((41, 41), np.uint8)) - raw).clip(0, 1)
rock_lvl = np.median(g[(raw == 0) & (rim == 0)])
g = np.where(rim > 0, np.maximum(g, rock_lvl * 0.97), g)
g = blur(g, 1.2)
g = (g - g.min()) / (g.max() - g.min())
rock_lvl = np.median(g[(raw == 0) & (rim == 0)])
rock_d = tiled(SCAN / "ambientcg" / "Rock046S" / "disp.png", 2, True)
h_rock = 0.45 * (g * (1 - mask_h) + rock_lvl * mask_h) + 0.55 * 0.25 + (rock_d - rock_d.mean()) * 0.05
dist = cv2.distanceTransform(raw.astype(np.uint8), cv2.DIST_L2, 5)
dome = 1 - (1 - np.minimum(dist / 60.0, 1)) ** 2
# (v2: the moss scan's bumps at 0.10 terraced the cushions in close-ups; its fibres live in the normal, a light lumpiness stays)
moss_d = tiled(SCAN / "ambientcg" / "Moss002" / "disp.png", 5, True)
ht = 0.45 * g + 0.55 * (0.25 + 0.75 * blur(dome, 4)) * mask_h + 0.55 * 0.25 * (1 - mask_h)
ht = ht + blur(moss_d - moss_d.mean(), 2) * 0.025 * mask_h + (rock_d - rock_d.mean()) * 0.05 * (1 - mask_h)
lo, hi = min(ht.min(), h_rock.min()), max(ht.max(), h_rock.max())
ht, h_rock = (ht - lo) / (hi - lo), (h_rock - lo) / (hi - lo)


def soften(h):
    gx, gy = cv2.Sobel(h, cv2.CV_32F, 1, 0), cv2.Sobel(h, cv2.CV_32F, 0, 1)
    slope = np.sqrt(gx ** 2 + gy ** 2)
    w_ = blur((slope > np.percentile(slope, 88)).astype(np.float32), 6)
    w_ = np.clip(w_ / (w_.max() + 1e-6) * 1.5, 0, 1)
    return h * (1 - w_) + blur(h, 4) * w_


ht, h_rock = soften(ht), soften(h_rock)
ht = np.maximum(ht, h_rock)
moss_dist = blur(np.minimum(dist / 150.0, 1), 3)        # 0 at a cushion's edge -> 1 from 15 cm in: shrinking the moss eats it from the edges

# --- normals: big shapes rebuilt from each height (so they can't disagree), fine detail from the scans' real normals
dm = tiled(SCAN / "ambientcg" / "Moss002" / "nor_gl.png", 5) * 2 - 1
dm = dm - np.dstack([blur(dm[..., i], 5) for i in range(3)]) + np.float32([0, 0, 1])   # fibres only: its clump shapes repeated as scallops
dr = tiled(SCAN / "ambientcg" / "Rock046S" / "nor_gl.png", 2) * 2 - 1


def normal_of(h, det):
    k = 6.0
    nx, ny = -cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) * k, cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) * k
    base = unit(np.dstack([nx, ny, np.ones_like(nx)]))
    return unit(np.dstack([base[..., 0] + det[..., 0], base[..., 1] + det[..., 1], base[..., 2] * det[..., 2]]))   # whiteout blend


nrm = normal_of(ht, unit(dm * mask[..., None] + dr * (1 - mask[..., None])))
nrm_rock = normal_of(h_rock, unit(dr))

# --- roughness (the rock's: dry granite 0.62-0.92 from the generated map, the shader makes moss 1.0); AO from each height, weak
r = maps["rough"]
r = (r - np.percentile(r, 2)) / (np.percentile(r, 98) - np.percentile(r, 2) + 1e-6)
r = np.where(raw > 0, np.median(r[raw == 0]), r)
rough = 0.62 + 0.30 * blur(r, 1).clip(0, 1)


def ao_of(h):
    cav = np.maximum(blur(h, 10) - h, 0) + 0.5 * np.maximum(blur(h, 35) - h, 0)
    return 1 - (cav / (np.percentile(cav, 99.5) + 1e-6)).clip(0, 1) * 0.45


ao, ao_rock = ao_of(ht), ao_of(h_rock)

w8 = lambda p, a: cv2.imwrite(str(p), (a.clip(0, 1) * 255).astype(np.uint8))
w16 = lambda p, a: cv2.imwrite(str(p), (a.clip(0, 1) * 65535).astype(np.uint16))
wrgb = lambda p, a: cv2.imwrite(str(p), cv2.cvtColor((a.clip(0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
wrgb(M / "albedo.png", a2); wrgb(M / "rock_albedo.png", rk)
w16(M / "height.png", ht); w16(M / "rock_height.png", h_rock)
wrgb(M / "normal.png", nrm * 0.5 + 0.5); wrgb(M / "rock_normal.png", nrm_rock * 0.5 + 0.5)
w8(M / "roughness.png", rough); w8(M / "ao.png", ao); w8(M / "rock_ao.png", ao_rock)
w8(M / "mask_shade.png", mask); w8(M / "mask_height.png", mask_h); w8(M / "moss_dist.png", moss_dist)

# --- a contact sheet of the set
tiles = [a2, ht, nrm * 0.5 + 0.5, rk, h_rock, moss_dist]
names = ["albedo", "height (16-bit)", "normal (height + scan detail)", "bare rock under it (albedo)", "bare rock height", "moss depth (for the coverage dial)"]
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

"""Warp generated PBR maps onto their albedo with optical flow (docs/reference/pbr_from_single_reference.md, step 4).

Generated maps never line up pixel for pixel; this compares STRUCTURE (edge strength), not brightness, so a height map and a
colour map can be matched, and turns a normal map into shading first. Two passes, then renormalises normals.

    from pbr_align import align, load
    out, before, after = align(albedo_rgb, height, is_normal=False)    # float32 0-1 arrays; before/after = median px shift
"""
import cv2
import numpy as np


def load(p):
    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img.ndim == 3:
        img = cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2RGB)
    return img.astype(np.float32) / (65535 if img.dtype == np.uint16 else 255)


def lum(img):
    return img if img.ndim == 2 else img @ np.float32([0.299, 0.587, 0.114])


def unit(n):
    return n / np.linalg.norm(n, axis=-1, keepdims=True).clip(1e-6)


def probe(img, is_normal):
    if is_normal:                                   # a normal map compared as the shading it makes
        L = np.float32([-0.5, 0.5, 0.7]); L /= np.linalg.norm(L)
        return (unit(img * 2 - 1) * L).sum(-1).clip(0, 1).astype(np.float32)
    return lum(img)


def structure(g):
    b = cv2.GaussianBlur(g, (0, 0), 1.5)
    m = np.sqrt(cv2.Sobel(b, cv2.CV_32F, 1, 0) ** 2 + cv2.Sobel(b, cv2.CV_32F, 0, 1) ** 2)
    m = np.log1p(m / (m.mean() + 1e-6))
    return (255 * m / m.max()).astype(np.uint8)


_dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
_dis.setPatchSize(16); _dis.setPatchStride(4)


def flow(ref, mov, smooth, lim):
    f = _dis.calc(structure(ref), structure(mov), None)
    f = np.dstack([cv2.GaussianBlur(f[..., i], (0, 0), smooth) for i in range(2)])
    return np.clip(f, -lim, lim)


def warp(img, f):
    h, w = f.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx + f[..., 0], gy + f[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def shift(f):
    return float(np.median(np.linalg.norm(f, axis=-1)))


def align(albedo, src, is_normal=False):
    ref = lum(albedo)
    scale = max(ref.shape) / 2500
    smooth, lim = 24 * scale, 12 * scale
    if src.shape[:2] != ref.shape:
        src = cv2.resize(src, ref.shape[::-1], interpolation=cv2.INTER_CUBIC)
    before = shift(flow(ref, probe(src, is_normal), smooth, lim))
    total = np.zeros((*ref.shape, 2), np.float32)
    cur = src
    for _ in range(2):
        total += flow(ref, probe(cur, is_normal), smooth, lim)
        cur = warp(src, total)
    if is_normal:
        cur = unit(cur * 2 - 1) * 0.5 + 0.5
    return cur, before, shift(flow(ref, probe(cur, is_normal), smooth, lim))

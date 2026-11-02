"""Composite the bonsai post's passes (render_bonsai_post.py): the garden pass blurred like a 70 mm lens wide open (a smooth
float gaussian, no banding), the tree + stand over it. python3 plants/post_composite.py OUT.png [blur_px]"""
import sys

import cv2
import numpy as np

out = sys.argv[1]
blur = float(sys.argv[2]) if len(sys.argv) > 2 else 26
fg = cv2.imread(out.replace(".png", "_fg.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
bg = cv2.imread(out.replace(".png", "_bg.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
lift = float(sys.argv[3]) if len(sys.argv) > 3 else 1.9
bg = cv2.GaussianBlur(bg, (0, 0), blur * bg.shape[1] / 1600) * lift                  # (the shaded garden sat at 11-32 of 255: it banded)
a = fg[..., 3:4]
im = fg[..., :3] * a + bg * (1 - a)                              # (Blender PNGs store straight alpha)
im += np.random.default_rng(0).normal(0, 0.007, im.shape).astype(np.float32)   # a touch of grain, like a photo
im8 = (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)
cv2.imwrite(out, im8)
# the X upload: a high-quality JPEG (X re-encodes everything; it keeps 4:5 portraits at full feed width and wants < 5 MB)
q = 95
while True:
    ok, buf = cv2.imencode(".jpg", im8, [cv2.IMWRITE_JPEG_QUALITY, q, cv2.IMWRITE_JPEG_OPTIMIZE, 1])
    if len(buf) < 4.8e6 or q <= 80:
        break
    q -= 3
xj = out.rsplit(".", 1)[0] + "_x.jpg"
open(xj, "wb").write(buf.tobytes())
print("wrote", out, "and", xj, f"({im8.shape[1]} x {im8.shape[0]}, {len(buf) / 1e6:.1f} MB, q{q})")

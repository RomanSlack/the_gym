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
bg = cv2.GaussianBlur(bg, (0, 0), blur) * lift                  # (the shaded garden sat at 11-32 of 255: it banded)
a = fg[..., 3:4]
im = fg[..., :3] * a + bg * (1 - a)                              # (Blender PNGs store straight alpha)
im += np.random.default_rng(0).normal(0, 0.007, im.shape).astype(np.float32)   # a touch of grain, like a photo
cv2.imwrite(out, (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8))
print("wrote", out)

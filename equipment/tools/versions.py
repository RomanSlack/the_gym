"""Where a piece's model renders go: equipment/pieces/<piece>/models/<piece>_<view>_vNNN.jpg, never overwritten.

A piece = one real product Roman picked (equipment/pieces/<piece>/piece.json); four leg extensions = four pieces.

One modelling pass = one version number across all its views:
    v = next_version("hammer-strength-select-leg-extension")
    for view in ("front", "three_quarter", "side", "detail"):
        render_to(path("hammer-strength-select-leg-extension", view, v))
    export_glb(model_path("hammer-strength-select-leg-extension", v))   # the 3D geometry of that pass, kept too
next_path(item, view) is the shortcut for a single new view.
"""
import re
from pathlib import Path

PIECES = Path(__file__).resolve().parents[1] / "pieces"


def versions(item):
    d = PIECES / item / "models"
    pat = re.compile(rf"^{re.escape(item)}_(.+)_v(\d{{3}})$")
    out = []
    for f in sorted(d.glob("*.jpg")) if d.exists() else []:
        m = pat.match(f.stem)
        if m:
            out.append((int(m.group(2)), m.group(1), f))
    return out


def next_version(item):
    return max((v for v, _, _ in versions(item)), default=0) + 1


def path(item, view, v):
    p = PIECES / item / "models" / f"{item}_{view}_v{v:03d}.jpg"
    if p.exists():
        raise FileExistsError(f"{p} exists: renders are never overwritten")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def next_path(item, view):
    return path(item, view, max((v for v, w, _ in versions(item) if w == view), default=0) + 1)


def model_path(item, v):
    """The pass's geometry (equipment/pieces/<piece>/models/<piece>_vNNN.glb), never overwritten, so every iteration can be reopened."""
    p = PIECES / item / "models" / f"{item}_v{v:03d}.glb"
    if p.exists():
        raise FileExistsError(f"{p} exists: models are never overwritten")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

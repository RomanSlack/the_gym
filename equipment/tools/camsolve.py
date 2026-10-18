"""Solve the camera of a reference photo from anchor points, so our model can be rendered from exactly that view.

    python3 equipment/tools/camsolve.py <piece>

pieces/<piece>/match.json:  {"ref": "precor_official.png", "size": [2000, 2000],
                             "points": {"<anchor>": [u, v], ...},            # pixels in the photo (from the top-left)
                             "lines": {"z": [[u1, v1, u2, v2], ...], "x": [...], "y": [...]},  # edges known to run along an axis
                             "free_centre": true}                           # principal point free (photos are often cropped); "y" = only up/down (a level camera with rise, as product shots use)
The lines don't depend on the model at all: parallel edges must meet at their vanishing point, which pins the lens and
the camera's angle (otherwise a wrong model can pull the camera far away onto a long lens).
The 3D side comes from the piece's model.py: anchors() -> {"<anchor>": (x, y, z), ...}, so the anchors move with the model.
model.py may list FIT = {"NAME": sigma_m, ...}: module constants (numbers or tuples) solved together with the camera, each
held to its starting value with that sigma (one photo can't fix depth alone). The fitted values go to fit.json, which
model.py loads over its constants, so every render uses them.
Writes match.json "camera" (Blender: location, rotation matrix camera->world, lens mm on a 36 mm sensor, shift) and
prints each anchor's error in pixels: a big error = the model is wrong there (or the point was read wrong).
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

EQ = Path(__file__).resolve().parents[1]
piece = sys.argv[1]
mf = EQ / "pieces" / piece / "match.json"
M = json.loads(mf.read_text())
spec = importlib.util.spec_from_file_location("pm", EQ / "pieces" / piece / "model.py")
pm = importlib.util.module_from_spec(spec)
sys.modules["bpy"] = type(sys)("bpy")  # model.py only needs math at import; build() is never called here
import os
os.environ["EQ_NOFIT"] = "1"  # start from the model's own numbers, not the last fit
spec.loader.exec_module(pm)
W, H = M["size"]
S = max(W, H)
FIT = getattr(pm, "FIT", {})
fitf = EQ / "pieces" / piece / "fit.json"
start = {n: getattr(pm, n) for n in FIT}  # the model's current values (fit.json already applied by model.py)
flat, slots = [], []
for n, sig in FIT.items():
    v = start[n]
    if isinstance(v, (tuple, list)):
        for i, x in enumerate(v):
            flat.append(float(x)); slots.append((n, i, sig))
    else:
        flat.append(float(v)); slots.append((n, None, sig))
flat0 = np.array(flat)
names = [n for n in M["points"] if n in pm.anchors()]
U = np.array([M["points"][n] for n in names], float)
free = M.get("free_centre", True)
NC = 9 if free else 7
PRIOR_PX = float(M.get("prior_px", 25.0))  # a parameter one sigma off its start costs as much as 25 px of image error


def setp(q):
    vals = {}
    for (n, i, sig), x in zip(slots, q):
        if i is None:
            vals[n] = x
        else:
            vals.setdefault(n, list(start[n]))[i] = x
    for n, v in vals.items():
        setattr(pm, n, tuple(v) if isinstance(v, list) else v)


def anchors3d(q):
    setp(q)
    A = pm.anchors()
    return np.array([A[n] for n in names], float)


LENS = M.get("lens_mm")  # optional: hold the focal length (mm on 36 mm) instead of solving it


def project(p, X):
    rv, C, f = p[:3], p[3:6], (LENS / 36 * S if LENS else p[6])
    cx, cy = ((W / 2 if free == "y" else p[7]), p[8]) if free else (W / 2, H / 2)
    Rcw = Rotation.from_rotvec(rv).as_matrix()
    Pc = (X - C) @ Rcw  # world -> camera (rows)
    z = -Pc[:, 2]
    return np.stack([cx + f * Pc[:, 0] / z, cy - f * Pc[:, 1] / z], 1)


sigs = np.array([s_ for _, _, s_ in slots])
AXES = {"x": (1.0, 0, 0), "y": (0, 1.0, 0), "z": (0, 0, 1.0)}
LINES = [(np.array(AXES[a], float), np.array(seg, float)) for a, segs in M.get("lines", {}).items() for seg in segs]
LINE_PX = 400.0  # a segment pointing 1 rad off its vanishing point costs 400 px


def line_resid(c):
    """Each segment must point at the vanishing point of its axis: the error is the sine of the angle, in px."""
    if not LINES:
        return np.zeros(0)
    rv, f = c[:3], (LENS / 36 * S if LENS else c[6])
    cx, cy = ((W / 2 if free == "y" else c[7]), c[8]) if free else (W / 2, H / 2)
    Rcw = Rotation.from_rotvec(rv).as_matrix()
    out = []
    for d, (u1, v1, u2, v2) in LINES:
        dc = d @ Rcw                       # the axis in camera space
        m = np.array([(u1 + u2) / 2, (v1 + v2) / 2])
        # image direction of the axis at m: the projected tangent (vanishing direction) through m
        z_ = -dc[2]
        vp = np.array([cx * z_ + f * dc[0], cy * z_ - f * dc[1]])   # homogeneous vanishing point (x, y) with w = z_
        dirv = vp - m * z_
        s = np.array([u2 - u1, v2 - v1])
        n1, n2 = np.linalg.norm(dirv), np.linalg.norm(s)
        out.append(LINE_PX * (dirv[0] * s[1] - dirv[1] * s[0]) / max(n1 * n2, 1e-9))
    return np.array(out)


def resid(p, with_fit=True):
    q = p[NC:] if with_fit else flat0
    r = (project(p[:NC], anchors3d(q)) - U).ravel()
    r = np.r_[r, line_resid(p[:NC])]
    if with_fit and len(q):
        r = np.r_[r, PRIOR_PX * (q - flat0) / sigs]
        if hasattr(pm, "SPEC"):  # the maker's overall size: 1 cm off costs 10 px
            r = np.r_[r, 1000.0 * (np.array(pm.extents()) - np.array(pm.SPEC))]
    return r


X = anchors3d(flat0)
# start: looking at the anchors' centre from the front-left, 50 mm
ctr = X.mean(0)
best, cams = None, []
for az in range(-150, 181, 30):
    for el in (10, 20, 30):
        for dist in (3.5, 5.0, 8.0):
            a, e = math.radians(az), math.radians(el)
            C = ctr + dist * np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
            fwd = (ctr - C) / np.linalg.norm(ctr - C)
            right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
            Rcw = np.stack([right, up, -fwd], 1)
            p0 = np.r_[Rotation.from_matrix(Rcw).as_rotvec(), C, 50 / 36 * S, W / 2, H / 2][:NC]
            try:
                sol = least_squares(lambda c: resid(np.r_[c, flat0], False), p0, method="lm", max_nfev=4000)
            except Exception:
                continue
            if np.all(-((X - sol.x[3:6]) @ Rotation.from_rotvec(sol.x[:3]).as_matrix())[:, 2] > 0.2):
                cams.append(sol)
                if best is None or sol.cost < best.cost:
                    best = sol
if len(flat0):  # the joint fit from several camera starts (it has local minima), the best wins
    starts = sorted(cams, key=lambda s_: s_.cost)[:int(M.get('starts', 6))]
    best = min((least_squares(resid, np.r_[s_.x, flat0], method="trf", max_nfev=20000) for s_ in starts), key=lambda s_: s_.cost)
p = best.x
X = anchors3d(p[NC:]) if len(flat0) else X
err = np.linalg.norm(project(p[:NC], X) - U, axis=1)
if len(flat0):
    out = {}
    for (n, i, sig), x in zip(slots, p[NC:]):
        if i is None:
            out[n] = round(float(x), 4)
        else:
            out.setdefault(n, [round(float(v), 4) for v in start[n]])[i] = round(float(x), 4)
    fitf.write_text(json.dumps(out, indent=1) + "\n")
    print("fitted (start -> now):")
    for n in out:
        print(f"  {n}: {start[n]} -> {out[n]}")
Rcw = Rotation.from_rotvec(p[:3]).as_matrix()
cx, cy = ((W / 2 if free == "y" else p[7]), p[8]) if free else (W / 2, H / 2)
cam = {"location": p[3:6].tolist(), "rotation": Rcw.tolist(), "lens": float(LENS or p[6] * 36 / S), "sensor": 36.0,
       "shift_x": float((W / 2 - cx) / S), "shift_y": float((cy - H / 2) / S), "size": [W, H]}
M["camera"] = cam
M["errors_px"] = {n: round(float(e), 1) for n, e in zip(names, err)}
mf.write_text(json.dumps(M, indent=1) + "\n")
print(f"camera at {np.round(p[3:6], 3)}, lens {cam['lens']:.1f} mm, shift {cam['shift_x']:.3f}/{cam['shift_y']:.3f}, rms {math.sqrt((err ** 2).mean()):.1f} px")
for n, e in sorted(zip(names, err), key=lambda t: -t[1]):
    print(f"  {e:6.1f} px  {n}")

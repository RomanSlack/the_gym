"""Solve the cameras of a piece's reference photos together with the model's uncertain dimensions.

    python3 equipment/tools/camsolve.py <piece>

pieces/<piece>/match.json: {"views": [{"ref": "<file in refs/>", "size": [W, H],
                                       "points": {"<anchor>": [u, v], ...},          # pixels from the top-left
                                       "lines": {"x"|"y"|"z": [[u1, v1, u2, v2], ...]},   # edges running along an axis
                                       "free_centre": false | "y" | true}, ...],      # "y": a level camera with rise
                            "prior_px": 12}
model.py gives anchors() -> {"<anchor>": (x, y, z)} and FIT = {"NAME": sigma, ...} (module constants solved here, each
held to its own value in model.py with that sigma; physically certain things, like a tower built square, stay out of
FIT). SPEC + extents() hold the maker's overall size. With two or more photos of the same machine the depth is
triangulated instead of guessed. Writes each view's "camera" + "errors_px" and fit.json (model.py loads it).
Rule of thumb from the Precor: label every anchor by what it is on the real machine (which corner, which side) before
fitting; a mislabelled corner makes the solver invent tilts and turns to explain it.
"""
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

EQ = Path(__file__).resolve().parents[1]
piece = sys.argv[1]
mf = EQ / "pieces" / piece / "match.json"
M = json.loads(mf.read_text())
VIEWS = M.get("views") or [M]
spec = importlib.util.spec_from_file_location("pm", EQ / "pieces" / piece / "model.py")
pm = importlib.util.module_from_spec(spec)
sys.modules["bpy"] = type(sys)("bpy")
os.environ["EQ_NOFIT"] = "1"  # start from the model's own numbers, not the last fit
spec.loader.exec_module(pm)
PRIOR_PX = float(M.get("prior_px", 12.0))
LINE_PX = 400.0
AXES = {"x": (1.0, 0, 0), "y": (0, 1.0, 0), "z": (0, 0, 1.0)}

FIT = getattr(pm, "FIT", {})
start = {n: getattr(pm, n) for n in FIT}
slots, flat = [], []
for n, sig in FIT.items():
    v = start[n]
    for i, x in (enumerate(v) if isinstance(v, (tuple, list)) else [(None, v)]):
        flat.append(float(x)); slots.append((n, i, sig))
flat0, sigs = np.array(flat), np.array([s for _, _, s in slots])


def setp(q):
    vals = {}
    for (n, i, _), x in zip(slots, q):
        if i is None:
            vals[n] = x
        else:
            vals.setdefault(n, list(start[n]))[i] = x
    for n, v in vals.items():
        setattr(pm, n, tuple(v) if isinstance(v, list) else v)


class View:
    def __init__(self, d):
        self.d = d
        self.W, self.H = d["size"]
        self.S = max(self.W, self.H)
        self.free = d.get("free_centre", False)
        self.nc = 7 + (1 if self.free == "y" else 2 if self.free else 0)
        self.names = [n for n in d["points"] if n in pm.anchors()]
        self.U = np.array([d["points"][n] for n in self.names], float)
        self.lines = [(np.array(AXES[a]), np.array(s, float)) for a, segs in d.get("lines", {}).items() for s in segs]

    def centre(self, c):
        if self.free == "y":
            return self.W / 2, c[7]
        if self.free:
            return c[7], c[8]
        return self.W / 2, self.H / 2

    def project(self, c, X):
        Rcw = Rotation.from_rotvec(c[:3]).as_matrix()
        Pc = (X - c[3:6]) @ Rcw
        cx, cy = self.centre(c)
        z = -Pc[:, 2]
        return np.stack([cx + c[6] * Pc[:, 0] / z, cy - c[6] * Pc[:, 1] / z], 1)

    def resid(self, c, X):
        r = [(self.project(c, X) - self.U).ravel()]
        Rcw = Rotation.from_rotvec(c[:3]).as_matrix()
        cx, cy = self.centre(c)
        for d, (u1, v1, u2, v2) in self.lines:  # each edge must point at its axis' vanishing point
            dc = d @ Rcw
            z_ = -dc[2]
            m = np.array([(u1 + u2) / 2, (v1 + v2) / 2])
            dirv = np.array([cx * z_ + c[6] * dc[0], cy * z_ - c[6] * dc[1]]) - m * z_
            s = np.array([u2 - u1, v2 - v1])
            r.append([LINE_PX * (dirv[0] * s[1] - dirv[1] * s[0]) / max(np.linalg.norm(dirv) * np.linalg.norm(s), 1e-9)])
        return np.concatenate(r)

    def start_cam(self, X):
        """Best camera alone over a grid of starts (the model as it is)."""
        ctr, best = X.mean(0), None
        for az in range(-180, 180, 30):
            for el in (5, 15, 25):
                for dist in (3.0, 5.0, 8.0):
                    a, e = math.radians(az), math.radians(el)
                    C = ctr + dist * np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
                    fwd = (ctr - C) / np.linalg.norm(ctr - C)
                    right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right)
                    up = np.cross(right, fwd)
                    c0 = np.r_[Rotation.from_matrix(np.stack([right, up, -fwd], 1)).as_rotvec(), C, 50 / 36 * self.S,
                               ([self.H / 2] if self.free == "y" else [self.W / 2, self.H / 2] if self.free else [])]
                    try:
                        sol = least_squares(lambda c: self.resid(c, X), c0, method="lm", max_nfev=3000)
                    except Exception:
                        continue
                    if np.all(-((X - sol.x[3:6]) @ Rotation.from_rotvec(sol.x[:3]).as_matrix())[:, 2] > 0.2):
                        if best is None or sol.cost < best.cost:
                            best = sol
        return best.x


views = [View(d) for d in VIEWS]


def X_of(q, v):
    setp(q)
    A = pm.anchors()
    return np.array([A[n] for n in v.names], float)


def resid(p):
    q = p[sum(v.nc for v in views):]
    out, k = [], 0
    for v in views:
        out.append(v.resid(p[k:k + v.nc], X_of(q, v)))
        k += v.nc
    out.append(PRIOR_PX * (q - flat0) / sigs)
    if hasattr(pm, "SPEC"):
        setp(q)
        out.append(1000.0 * (np.array(pm.extents()) - np.array(pm.SPEC)))
    return np.concatenate(out)


cams = [v.start_cam(X_of(flat0, v)) for v in views]
sol = least_squares(resid, np.r_[np.concatenate(cams), flat0], method="trf", max_nfev=30000)
p = sol.x
q = p[sum(v.nc for v in views):]
out = {}
for (n, i, _), x in zip(slots, q):
    if i is None:
        out[n] = round(float(x), 4)
    else:
        out.setdefault(n, [round(float(v), 4) for v in start[n]])[i] = round(float(x), 4)
(EQ / "pieces" / piece / "fit.json").write_text(json.dumps(out, indent=1) + "\n")
print("fitted (model.py -> now):")
for n in out:
    print(f"  {n}: {start[n]} -> {out[n]}")
setp(q)
print("extents (L, W, H):", [round(e, 3) for e in pm.extents()], "spec", getattr(pm, "SPEC", None))
k = 0
for v in views:
    c = p[k:k + v.nc]; k += v.nc
    err = np.linalg.norm(v.project(c, X_of(q, v)) - v.U, axis=1)
    cx, cy = v.centre(c)
    v.d["camera"] = {"location": c[3:6].tolist(), "rotation": Rotation.from_rotvec(c[:3]).as_matrix().tolist(),
                     "lens": float(c[6] * 36 / v.S), "sensor": 36.0, "shift_x": float((v.W / 2 - cx) / v.S),
                     "shift_y": float((cy - v.H / 2) / v.S), "size": [v.W, v.H]}
    v.d["errors_px"] = {n: round(float(e), 1) for n, e in zip(v.names, err)}
    print(f"\n{v.d['ref']}: camera at {np.round(c[3:6], 2)}, lens {v.d['camera']['lens']:.0f} mm, rms {math.sqrt((err ** 2).mean()):.1f} px")
    for n, e in sorted(zip(v.names, err), key=lambda t: -t[1])[:8]:
        print(f"  {e:6.1f} px  {n}")
mf.write_text(json.dumps(M, indent=1) + "\n")

"""Solve the fit figure's arm onto a grip (body.py's chain, no Blender needed): given the legs and trunk, find the arm
angles that put the middle of the palm on a target, with the elbow as near a natural bend as the reach allows.

    from reach import shoulder, reach
    pose = dict(H=1.78, ball=(0, y, z), face=(0, 1), shank=8, thigh=4, trunk=8)
    arms = reach(pose, (x, y, z))          # -> dict(arm, forearm, arm_lat, fore_lat, elbow, err): update the pose with it

The target may be on either side (the figure is symmetric); arm_lat / fore_lat raise the segments out to that side.
"""
import math

import numpy as np

PALM = 0.04                                  # wrist to the middle of the palm, x H (body.py draws the hand 0.08 H)


def _frame(face):
    f = np.array([face[0], face[1], 0.0]); f /= np.linalg.norm(f)
    up = np.array([0.0, 0.0, 1.0])
    return f, up, np.cross(up, f)            # forward, up, the figure's left


def shoulder(pose, side=1):
    """The shoulder joint on one side (side 1 = the figure's left) for a pose dict as body.figure takes."""
    H = pose["H"]
    f, up, left = _frame(pose["face"])
    d = lambda a: up * math.cos(math.radians(a)) + f * math.sin(math.radians(a))
    sole = math.radians(pose.get("sole", 0.0))
    so = f * math.cos(sole) + up * math.sin(sole)
    su = up * math.cos(sole) - f * math.sin(sole)
    ankle = np.array(pose["ball"], float) - so * 0.48 * 0.152 * H + su * 0.039 * H
    hip = ankle + d(pose.get("shank", 0.0)) * 0.246 * H + d(pose.get("thigh", 0.0)) * 0.245 * H
    sh = hip + d(pose.get("trunk", 0.0)) * 0.288 * H
    return sh + left * side * 0.13 * H * 0.85


def reach(pose, target, elbow=150.0, step=2.0):
    """Arm angles (body.figure's arm, forearm, arm_lat, fore_lat) putting the palm on target, the elbow's inside angle
    nearest `elbow` (180 = straight). err is how far the best solution's palm misses (m): check it."""
    H = pose["H"]
    f, up, left = _frame(pose["face"])
    t = np.array(target, float)
    side = 1 if np.dot(t - np.array(pose["ball"], float), left) >= 0 else -1
    sh = shoulder(pose, side)
    L1, L2 = 0.186 * H, (0.146 + PALM) * H
    rel = t - sh
    fw, lat, z = np.dot(rel, f), np.dot(rel, left) * side, rel[2]       # in the figure's frame, lateral outward
    A = np.radians(np.arange(0.0, 200.0 + step, step))                 # sagittal angles from up toward the face
    Lt = np.radians(np.arange(-10.0, 70.0 + step, step))               # raises out to the side
    a, l = np.meshgrid(A, Lt, indexing="ij")
    seg = lambda a, l: (np.sin(a) * np.cos(l), np.sin(l), np.cos(a) * np.cos(l))   # (forward, out, up)
    u = seg(a, l)
    e = [L1 * c for c in u]                                             # the elbow, from the shoulder
    # for each upper-arm direction the forearm must point from the elbow to the target: solve it directly
    r = [np.array(fw) - e[0], np.array(lat) - e[1], np.array(z) - e[2]]
    n = np.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2)
    err = np.abs(n - L2)
    cosel = -(u[0] * r[0] + u[1] * r[1] + u[2] * r[2]) / np.maximum(n, 1e-9)   # the elbow's inside angle
    el = np.degrees(np.arccos(np.clip(cosel, -1, 1)))
    cost = err * 100.0 + np.abs(el - elbow) / 90.0 + np.abs(np.degrees(l)) / 400.0
    i = np.unravel_index(np.argmin(cost), cost.shape)
    v = [r[k][i] / n[i] for k in range(3)]
    fl = math.degrees(math.asin(max(-1.0, min(1.0, v[1]))))
    fa = math.degrees(math.atan2(v[0], v[2]))
    return dict(arm=math.degrees(a[i]), forearm=fa % 360 if fa < 0 else fa, arm_lat=math.degrees(l[i]), fore_lat=fl,
                elbow=float(el[i]), err=float(err[i]))

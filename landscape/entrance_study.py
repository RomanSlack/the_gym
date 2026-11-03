"""The entrance landscape, direction B "stone carpet" with A's planting (Roman 2026-11-03: "good very good, i like that plan";
research in docs/greenery/ENTRANCE_RESEARCH.md). A design study laid over the saved stage 5 scene, ONE shot per process:

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
        blender -b construction/out/stage_5.blend -t 12 --python landscape/entrance_study.py -- SHOT

SHOT: arrive (from the drop-off), corner (from the birch grove across the forecourt), door (out from the vestibule), aerial.
- the stone carpet: one forecourt of flamed light Iddefjord granite, 1200 x 600 slabs in running bond parallel to the facade,
  from the glass out 9.6 m, 14.5 m wide round the vestibule, falling 1:60 away from the building; a slot drain along the glass
  and across the vestibule threshold; flush blackened-steel edges where it meets the heath
- flag paths of the same granite: 2.5 m to the drop-off, 1.8 m to the accessible bays / trailhead path and to the bike shelter
- heath everywhere else (no lawn): lingonberry, heather, blueberry, hair grass on a generated heath ground (landscape/maps/heath)
- a multi-stem birch grove on a low mound north of the forecourt; granite boulders in the heath
- a planted swale south of the main path that takes the forecourt's water (and the plowed snow in winter), river stones in its bed
Renders kept as construction/renders/stage_5_ent_<shot>_vNNN.jpg.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "construction", ROOT / "plants", ROOT / "walls"):
    sys.path.insert(0, str(p))
import bl_common as bc  # noqa: E402
import ground  # noqa: E402
import shoot  # noqa: E402

SHOT = sys.argv[sys.argv.index("--") + 1:][0]
import time as _t
_T0 = _t.time()
def tick(what):
    print(f"[time] {what}: {_t.time() - _T0:.0f} s", flush=True)
scene = bpy.context.scene
bc.gpu_or_stop()
EXPO = scene.view_settings.exposure
rng = np.random.default_rng(11)
coll = bpy.data.collections.new("7 · entrance landscape"); scene.collection.children.link(coll)

# ---------------------------------------------------------------- the ground as it is (before anything is added)
X0, X1, Y0, Y1, STEP = 28.0, 66.0, -12.0, 30.0, 0.25
dg = bpy.context.evaluated_depsgraph_get()
xs, ys = np.arange(X0, X1 + 1e-6, STEP), np.arange(Y0, Y1 + 1e-6, STEP)
TER = np.zeros((len(ys), len(xs)))
for i, y in enumerate(ys):
    for j, x in enumerate(xs):
        hit, loc, *_ = scene.ray_cast(dg, Vector((x, y, 2.9)), Vector((0, 0, -1)))
        TER[i, j] = loc.z if hit else 0.12


def terrain(x, y):
    j = np.clip((np.asarray(x) - X0) / STEP, 0, len(xs) - 1.001); i = np.clip((np.asarray(y) - Y0) / STEP, 0, len(ys) - 1.001)
    j0, i0 = np.floor(j).astype(int), np.floor(i).astype(int); fj, fi = j - j0, i - i0
    return (TER[i0, j0] * (1 - fj) * (1 - fi) + TER[i0, j0 + 1] * fj * (1 - fi) + TER[i0 + 1, j0] * (1 - fj) * fi + TER[i0 + 1, j0 + 1] * fj * fi)


tick("ground sampled")
# the lawn's grass goes from the whole parking roof (the heath replaces it)
lg = bpy.data.objects.get("lawn_ground")
if lg:
    bm = bmesh.new(); bm.from_mesh(lg.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if 30.4 < f.calc_center_median().x < 60.5 and -9.8 < f.calc_center_median().y < 24.5], context="FACES")
    bm.to_mesh(lg.data); bm.free()

# ---------------------------------------------------------------- materials
granite = bc.pbr_material("granite_iddefjord_flamed", "granite_flamed_gridless", 1.2, box=True, tint=(1.0, 0.99, 0.97), sat=0.3, val=1.2,
                          rough_mul=0.9, rough_add=0.25, piece_var=0.07)
steel = bpy.data.materials.get("blackened_steel_d") or bc.material("blackened_steel", (0.03, 0.029, 0.028), 0.62, metal=0.7)
slot = bc.material("drain_slot", (0.004, 0.004, 0.004), 0.5)
boulder_m = bc.pbr_material("boulder_lichen", "lichen_rock", 1.6, box=True, piece_var=0.12)
cobble_m = bc.pbr_material("river_cobble", "granite_tile_03", 0.5, box=True, tint=(0.85, 0.85, 0.85), sat=0.5, val=0.9, rough_mul=0.8, rough_add=0.2, piece_var=0.2)


def heath_material():
    m = bpy.data.materials.new("heath_ground"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / 1.7,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    ci = N.new("ShaderNodeTexImage"); ci.image = bpy.data.images.load(str(ROOT / "landscape" / "maps" / "heath_col.jpg"))
    hi = N.new("ShaderNodeTexImage"); hi.image = bpy.data.images.load(str(ROOT / "landscape" / "maps" / "heath_h.png")); hi.image.colorspace_settings.name = "Non-Color"
    for t in (ci, hi):
        L.new(mp.outputs[0], t.inputs["Vector"])
    L.new(ci.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.02
    L.new(hi.outputs["Color"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def mesh_obj(name, V, F, mat, face_attrs=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F])
    for k, v in (face_attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", "FACE"); a.data.foreach_set("value", np.asarray(v, np.float32))
    me.polygons.foreach_set("use_smooth", np.full(len(F), smooth))
    o = bpy.data.objects.new(name, me); coll.objects.link(o); me.materials.append(mat)
    return o


class Boxes:
    """oriented boxes into one mesh, each with its own 'prand' (pbr_material shifts + tones every piece)"""
    def __init__(self):
        self.V, self.F, self.P = [], [], []

    def add(self, c, u, along, across, top, depth, pr=None):
        u = np.array([u[0], u[1], 0.0]); u /= np.linalg.norm(u); v = np.array([-u[1], u[0], 0.0])
        o = len(self.V)
        for dz in (top - depth, top):
            for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                self.V.append(np.array([c[0], c[1], dz]) + u * a * along / 2 + v * b * across / 2)
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.F.append([o + k for k in f])
        self.P += [rng.random() if pr is None else pr] * 6

    def obj(self, name, mat):
        return mesh_obj(name, self.V, self.F, mat, {"prand": self.P})


print("terrain over the forecourt: min %.3f  mean %.3f  max %.3f" % (TER[(ys[:, None] > 4) & (ys[:, None] < 18.5) & (xs[None] > 31) & (xs[None] < 52)].min(),
      TER[(ys[:, None] > 4) & (ys[:, None] < 18.5) & (xs[None] > 31) & (xs[None] < 52)].mean(), TER[(ys[:, None] > 4) & (ys[:, None] < 18.5) & (xs[None] > 31) & (xs[None] < 52)].max()))


TER = np.clip(TER, -0.3, None)                       # (a few rays fell through a hole onto the parking roof)


def fall(x, y=11.3):
    """the carpet's top: one plane, the floor level at the glass falling 1:60 away from the building"""
    return 0.125 - np.clip(np.asarray(x) - 30.9, 0, None) / 60.0 + 0 * np.asarray(y)


def path_top(pts):
    """a path's top along its length s: from the carpet's edge level down (or up) to the ground at its far end"""
    P = np.array(pts, float); L = np.hypot(*np.diff(P, axis=0).T).sum()
    z0 = float(fall(P[0][0])); z1 = float(terrain(*P[-1])) + 0.015
    return lambda sv: z0 + (z1 - z0) * np.clip(sv / L, 0, 1)


# ---------------------------------------------------------------- the stone carpet
CX0, CX1, CY0, CY1 = 30.9, 40.5, 4.0, 18.5            # glass face (granite plinth) -> 9.6 m out; 14.5 m wide
VEST = (30.5, 33.0, 9.3, 13.3)                       # the vestibule's porch floor (already built)
S = Boxes()
J = 0.006                                            # joint
for r in range(int(round((CX1 - CX0) / 0.6))):
    x = CX0 + 0.3 + r * 0.6
    edges = np.arange(CY0 - (0.6 if r % 2 else 0.0), CY1 + 1.2, 1.2)
    for a, b in zip(edges[:-1], edges[1:]):
        spans = [(max(a, CY0), min(b, CY1))]
        if x - 0.3 < VEST[1]:                                            # cut round the vestibule
            spans = [(s0, min(s1, VEST[2])) for s0, s1 in spans if s0 < VEST[2]] + [(max(s0, VEST[3]), s1) for s0, s1 in spans if s1 > VEST[3]]
        for s0, s1 in spans:
            if s1 - s0 > 0.05:
                S.add(((x, (s0 + s1) / 2)), (1, 0), 0.6 - J, s1 - s0 - J, float(fall(x, (s0 + s1) / 2)) + rng.normal(0, 0.0008), 0.25)


# ---------------------------------------------------------------- flag paths (courses of 0.6 across the path, split once at random)
def resample(pts, step):
    P = np.array(pts, float); seg = np.diff(P, axis=0); L = np.hypot(*seg.T); cum = np.r_[0, np.cumsum(L)]
    out = []
    for t in np.arange(step / 2, cum[-1], step):
        i = min(np.searchsorted(cum, t, side="right") - 1, len(seg) - 1); f = (t - cum[i]) / L[i]
        # tangent smoothed over the neighbouring segments so the courses turn gently at a bend
        tg = seg[i] / L[i]
        if 0 < i and f < 0.25:
            tg = tg + (seg[i - 1] / L[i - 1]) * (0.25 - f) * 2
        if i < len(seg) - 1 and f > 0.75:
            tg = tg + (seg[i + 1] / L[i + 1]) * (f - 0.75) * 2
        out.append((P[i] + seg[i] * f, tg / np.linalg.norm(tg)))
    return out


PATHS = {  # name: (polyline, width)
    "to_dropoff": ([(40.5, 11.3), (45.5, 11.7), (49.5, 12.6), (52.2, 13.1)], 2.5),
    "to_bays": ([(39.6, 18.5), (43.5, 19.4), (47.0, 20.6), (49.8, 22.2)], 1.8),
    "to_bikes": ([(36.4, 4.0), (37.2, 1.6), (38.6, -0.6)], 1.8),
}
PATH_Z = {}
for name, (pts, w) in PATHS.items():
    zf = PATH_Z[name] = path_top(pts)
    for k_, (c, t) in enumerate(resample(pts, 0.6)):
        n = np.array([-t[1], t[0]]); sp = rng.uniform(0.35, 0.65) * w
        for a, b in ((-w / 2, -w / 2 + sp), (-w / 2 + sp, w / 2)):
            cc = c + n * (a + b) / 2
            S.add(cc, t, 0.6 - J, b - a - J, float(zf(0.3 + 0.6 * k_)) + rng.normal(0, 0.001), 0.25)
S.obj("granite_forecourt", granite)

# slot drains: along the glass both sides of the vestibule, and across its threshold
D = Boxes()
for (x, y0, y1) in ((CX0 + 0.12, CY0, VEST[2]), (CX0 + 0.12, VEST[3], CY1)):
    D.add((x, (y0 + y1) / 2), (0, 1), y1 - y0, 0.03, float(fall(x, (y0 + y1) / 2)) + 0.0005, 0.05, 0.5)
D.add((VEST[1] + 0.15, (VEST[2] + VEST[3]) / 2), (0, 1), VEST[3] - VEST[2], 0.03, float(fall(VEST[1], 11.3)) + 0.0005, 0.05, 0.5)
D.obj("slot_drains", slot)
# flush steel edges where the carpet meets the heath (gaps where the paths leave)
E = Boxes()
for (p0, p1) in (((CX1, CY0), (CX1, 10.05)), ((CX1, 12.55), (CX1, 17.6)), ((CX0 + 0.3, CY1), (39.0, CY1)),
                 ((CX0 + 0.3, CY0), (35.5, CY0)), ((37.3, CY0), (CX1, CY0))):
    p0, p1 = np.array(p0), np.array(p1); d = p1 - p0
    E.add((p0 + p1) / 2, d, np.linalg.norm(d), 0.008, float(fall((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)) + 0.002, 0.15, 0.5)
E.obj("steel_edges", steel)


# ---------------------------------------------------------------- the heath (the ground), with the grove mound and the swale
def bump(x, y, cx, cy, rx, ry):
    q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return np.where(q < 1, (1 - q) ** 2, 0.0)


GROVE = (37.6, 21.6, 5.0, 3.0)                 # mound centre + radii
SWALE = (46.2, 6.4, 4.6, 2.3)


def paved(x, y):
    """inside the carpet or a path (+ a hair), as a boolean array"""
    inside = (x > CX0 - 0.5) & (x < CX1 + 0.02) & (y > CY0 - 0.02) & (y < CY1 + 0.02)
    for pts, w in PATHS.values():
        P = np.array(pts)
        for a, b in zip(P[:-1], P[1:]):
            d = b - a; t = np.clip(((x - a[0]) * d[0] + (y - a[1]) * d[1]) / (d @ d), 0, 1)
            inside |= np.hypot(x - a[0] - t * d[0], y - a[1] - t * d[1]) < w / 2 + 0.02
    return inside


def paved_top(x, y):
    """the paving's top under (x, y): the carpet plane, or the nearest path's graded level"""
    z = np.where((x < CX1 + 0.6), fall(x), np.nan)
    best = np.full(np.shape(x), 1e9)
    for name, (pts, w) in PATHS.items():
        P = np.array(pts); sacc = 0.0
        for a, b in zip(P[:-1], P[1:]):
            d = b - a; Ld = np.hypot(*d); t = np.clip(((x - a[0]) * d[0] + (y - a[1]) * d[1]) / (d @ d), 0, 1)
            dist = np.hypot(x - a[0] - t * d[0], y - a[1] - t * d[1])
            better = (dist < best) & (dist < w / 2 + 1.0) & ((x >= CX1) | (name == "to_bikes") | (name == "to_bays"))
            z = np.where(better, PATH_Z[name](sacc + t * Ld), z); best = np.where(better, dist, best); sacc += Ld
    return z


tb = bpy.data.objects.get("terrain_building")       # its base mesh: pushed down under the paving (+0.8 m round it)
if tb:
    co = np.array([v.co for v in tb.data.vertices]); wco = np.array([tb.matrix_world @ v.co for v in tb.data.vertices])
    near = np.zeros(len(co), bool)
    for dx in (-0.8, 0, 0.8):
        for dy in (-0.8, 0, 0.8):
            near |= paved(wco[:, 0] + dx, wco[:, 1] + dy)
    pt = paved_top(wco[:, 0], wco[:, 1])
    lower = near & ~np.isnan(pt) & (wco[:, 2] > pt - 0.06)
    co[lower, 2] -= (wco[lower, 2] - (pt[lower] - 0.06))
    tb.data.vertices.foreach_set("co", co.ravel().astype(np.float32)); tb.data.update()
    print("terrain_building: lowered", int(lower.sum()), "vertices under the paving")

HX0, HX1, HY0, HY1, HS = 30.6, 60.0, -9.6, 24.4, 0.25
gx, gy = np.meshgrid(np.arange(HX0, HX1 + 1e-6, HS), np.arange(HY0, HY1 + 1e-6, HS))
gz = terrain(gx, gy) + 0.02 + 0.45 * bump(gx, gy, *GROVE) - 0.38 * bump(gx, gy, *SWALE) + 0.03 * np.sin(gx * 1.3) * np.cos(gy * 1.7)
pv = paved(gx, gy)
ptop = paved_top(gx, gy)
gz = np.where(pv, np.minimum(gz, np.nan_to_num(ptop, nan=9) - 0.03), gz)              # tucked under the paving
edge = ~pv & ~np.isnan(ptop)                                                         # the heath meets the paving's level at its edge
gz = np.where(edge, np.minimum(gz, ptop + 0.04 + 0.25 * np.clip(gz - ptop - 0.04, 0, None)), gz)
ny, nx = gx.shape
V = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], 1)
idx = np.arange(nx * ny).reshape(ny, nx)
F = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
heath = mesh_obj("heath_ground", V, F, heath_material(), smooth=True)
# the planting lives on the faces clear of the paving (a copy 1 mm down carries the scatter)
cell_free = ~(pv[:-1, :-1] | pv[:-1, 1:] | pv[1:, 1:] | pv[1:, :-1]).ravel()
in_swale = (bump(gx, gy, *SWALE)[:-1, :-1] > 0.05).ravel()
V2 = V.copy(); V2[:, 2] -= 0.001


def proto_mat(name, rough, trans=0.25):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; ca = N.new("ShaderNodeVertexColor"); ca.layer_name = "col"
    oi = N.new("ShaderNodeObjectInfo"); hs = N.new("ShaderNodeHueSaturation")
    mr = N.new("ShaderNodeMapRange"); mr.inputs[3].default_value = 0.8; mr.inputs[4].default_value = 1.2
    L.new(oi.outputs["Random"], mr.inputs[0]); L.new(mr.outputs[0], hs.inputs["Value"]); L.new(ca.outputs["Color"], hs.inputs["Color"])
    L.new(hs.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(hs.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = trans
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def proto(name, kind, seed):
    """a dwarf-shrub clump along +Z: stems with leaves. heather: dense fine sprigs, mauve tips; lingonberry: low, small glossy
    dark leaves; blueberry: taller, bright green; fern: a few arching fronds (the swale)"""
    r = np.random.default_rng(seed)
    V, F, C = [], [], []
    spec = {"heather": (44, (0.14, 0.32), 0.005, 0, (0.12, 0.14, 0.07)), "lingonberry": (24, (0.06, 0.16), 0.0, 9, (0.025, 0.07, 0.018)),
            "blueberry": (16, (0.2, 0.36), 0.0, 11, (0.07, 0.15, 0.03)), "fern": (8, (0.35, 0.6), 0.0, 14, (0.06, 0.14, 0.03))}[kind]
    n, (h0, h1), sprig_w, leaves, col = spec
    col = np.array(col)
    for _ in range(n):
        az = r.uniform(0, 2 * math.pi); lean = r.uniform(0.1, 0.5) if kind != "fern" else r.uniform(0.6, 1.1); h = r.uniform(h0, h1)
        base = np.array([r.normal(0, 0.03), r.normal(0, 0.03), 0]); d = np.array([math.cos(az), math.sin(az), 0]); side = np.array([-d[1], d[0], 0])
        pts = [base + d * lean * h * t * t + np.array([0, 0, h * (t - (0.5 if kind == "fern" else 0.2) * lean * t * t)]) for t in np.linspace(0, 1, 5)]
        if kind == "heather":                                          # a fine sprig, green-grey, the top third flowering
            for k in range(4):
                o = len(V); w0, w1 = sprig_w * (1 - 0.2 * k), sprig_w * (1 - 0.2 * (k + 1))
                V += [pts[k] - side * w0, pts[k] + side * w0, pts[k + 1] + side * w1, pts[k + 1] - side * w1]; F.append([o, o + 1, o + 2, o + 3])
                c = col if (k < 3 or r.random() > 0.35) else col * 0.75 + np.array([0.3, 0.17, 0.26]) * 0.25 * r.uniform(0.6, 1.2)
                C += [c] * 4
            continue
        for k in range(4):                                             # the stem
            o = len(V); w = 0.0025 if kind != "fern" else 0.002
            V += [pts[k] - side * w, pts[k] + side * w, pts[k + 1] + side * w, pts[k + 1] - side * w]; F.append([o, o + 1, o + 2, o + 3]); C += [col * 0.6] * 4
        for k in range(leaves):                                        # the leaves (fern: pinnae both sides)
            t = (k + 1) / (leaves + 1) if kind == "fern" else r.uniform(0.25, 1)
            p = pts[0] + (pts[-1] - pts[0]) * t if kind != "fern" else pts[min(3, int(t * 4))] + (pts[min(4, int(t * 4) + 1)] - pts[min(3, int(t * 4))]) * (t * 4 % 1)
            for sgn in ((-1, 1) if kind == "fern" else (1,)):
                ld = side * sgn if kind == "fern" else np.array([math.cos(r.uniform(0, 6.3)), math.sin(r.uniform(0, 6.3)), r.uniform(-0.1, 0.5)])
                ld = ld / np.linalg.norm(ld)
                ll = {"lingonberry": 0.016, "blueberry": 0.024, "fern": 0.07 * (1 - 0.6 * t)}[kind]; lw = ll * (0.55 if kind != "fern" else 0.18)
                nrm = np.cross(ld, np.array([0, 0, 1.0])); nrm = nrm / (np.linalg.norm(nrm) + 1e-9)
                o = len(V)
                V += [p, p + ld * ll * 0.5 + nrm * lw, p + ld * ll, p + ld * ll * 0.5 - nrm * lw]; F.append([o, o + 1, o + 2, o + 3])
                C += [col * r.uniform(0.8, 1.25)] * 4
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], F)
    ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
    for i, c in enumerate(C):
        ca.data[i].color = (*np.clip(c, 0, 1), 1)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); o.location = (0, 0, -2000)
    me.materials.append(proto_mat(name + "_m", {"heather": 0.7, "lingonberry": 0.32, "blueberry": 0.5, "fern": 0.55}[kind]))
    return o


heath_protos = [proto(f"heather_{i}", "heather", i) for i in range(3)] + [proto(f"lingon_{i}", "lingonberry", 10 + i) for i in range(3)] + \
               [proto(f"blueb_{i}", "blueberry", 20 + i) for i in range(2)]
swale_protos = [proto(f"fern_{i}", "fern", 30 + i) for i in range(3)] + [ground.grass_proto("tuft_meadow_e", "meadow", coll), ground.grass_proto("tuft_dry_e2", "dry", coll)]
for nm, sel, protos, dens in (("heath_plants", cell_free & ~in_swale, heath_protos, 60), ("heath_grass", cell_free & ~in_swale, [ground.grass_proto("tuft_dry_e", "dry", coll)], 3),
                              ("swale_plants", cell_free & in_swale, swale_protos, 22)):
    o = mesh_obj(nm, V2, F[sel], heath.data.materials[0])
    md = o.modifiers.new("plants", "NODES"); md.node_group = ground.grass_nodes("GN_" + nm, protos, dens, seed=len(nm))

# river stones down the swale's bed
CB = []
for k in range(70):
    a = rng.uniform(0, 2 * math.pi); rr = math.sqrt(rng.uniform(0, 1)) * 0.6
    x = SWALE[0] + math.cos(a) * rr * SWALE[2] * 0.85; y = SWALE[1] + math.sin(a) * rr * SWALE[3] * 0.35
    CB.append((x, y, rng.uniform(0.07, 0.2)))


def rock(name, x, y, r, sq, mat, sink=0.3, seed=0):
    """a displaced icosphere built straight into a mesh (bpy.ops re-evaluated the whole building on every rock: minutes)"""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    rr = np.random.default_rng(seed); vs = np.array([v.co for v in bm.verts])
    k = rr.normal(0, 1, (6, 3))
    disp = sum(np.sin(vs @ k[i] * (1.2 + i) + rr.uniform(0, 6)) * 0.08 / (1 + i * 0.6) for i in range(6))
    vs = vs * (1 + disp)[:, None] * np.array([r, r * rr.uniform(0.7, 0.95), r * sq])
    for v, c in zip(bm.verts, vs):
        v.co = c
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); coll.objects.link(o); me.materials.append(mat)
    zb = float(terrain(x, y)) + 0.45 * float(bump(x, y, *GROVE)) - 0.38 * float(bump(x, y, *SWALE))
    o.location = (x, y, zb + r * sq * (1 - 2 * sink)); o.rotation_euler[2] = rr.uniform(0, 6.3)
    return o


for i, (x, y, r) in enumerate(CB):
    rock(f"cobble_{i}", x, y, r, 0.45, cobble_m, sink=0.35, seed=100 + i)
for i, (x, y, r, sq) in enumerate(((44.8, 16.4, 0.95, 0.55), (47.4, 18.3, 0.6, 0.6), (42.4, 7.9, 0.7, 0.5), (50.2, 4.6, 0.55, 0.6),
                                   (34.6, 1.6, 0.85, 0.5), (33.4, 21.9, 0.6, 0.55), (51.2, 8.8, 0.45, 0.6))):
    rock(f"boulder_{i}", x, y, r, sq, boulder_m, sink=0.3, seed=i)

tick("heath + rocks")
# ---------------------------------------------------------------- the birch grove (multi-stem silver birch on the mound)
import gen_birch  # noqa: E402
if SHOT != "aerial_fast":
    for k, (x, y, h) in enumerate(((36.0, 21.2, 7.2), (38.8, 22.7, 8.0), (40.2, 20.6, 6.4), (35.4, 23.4, 6.8))):
        zb = float(terrain(x, y)) + 0.45 * float(bump(x, y, *GROVE))
        objs = gen_birch.build(40 + k, (x, y, zb - 0.05), height=h, name=f"grove_birch_{k}")
        for o in objs:
            for c in o.users_collection:
                c.objects.unlink(o)
            coll.objects.link(o)

tick("birches")
# ---------------------------------------------------------------- the shots
CAMS = {
    "arrive": ((52.6, 13.4), 1.65, (31.0, 11.3, 2.2), 24),
    "corner": ((45.2, 22.6), 1.7, (33.0, 9.8, 1.0), 22),
    "door": ((33.7, 16.6), 1.62, (48.0, 8.5, 0.9), 20),
    "aerial": ((63.0, -7.0), 17.0, (39.0, 11.0, 0.0), 26),
}
(cx, cy), h, tgt, lens = CAMS[SHOT]
loc = (cx, cy, float(terrain(cx, cy)) + h)
name = f"ent_{SHOT}"
bc.camera(scene, f"cam_{name}", loc, tgt, lens)
lod = bpy.data.objects.get("lod_eye")
shoot.shoot(scene, name, name, EXPO, 5, lod)

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
DRAFT = "draft" in sys.argv[sys.argv.index("--") + 1:]                   # quick look: 32 samples, 60 % size
import time as _t
_T0 = _t.time()
def tick(what):
    print(f"[time] {what}: {_t.time() - _T0:.0f} s", flush=True)
scene = bpy.context.scene
if SHOT in ("stones", "build_only"):
    bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene; bc.world_and_render(scene)
    if SHOT == "build_only": bc.gpu_or_stop = lambda: None
    scene.render.engine = "CYCLES"; scene.cycles.device = "GPU"; scene.cycles.samples = 64; scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1600, 900, 100
bc.gpu_or_stop()
EXPO = scene.view_settings.exposure
rng = np.random.default_rng(11)
coll = bpy.data.collections.new("7 · entrance landscape"); scene.collection.children.link(coll)

# ---------------------------------------------------------------- the ground as it is (before anything is added)
X0, X1, Y0, Y1, STEP = 28.0, 78.0, -16.0, 32.0, 0.25
dg = bpy.context.evaluated_depsgraph_get()
xs, ys = np.arange(X0, X1 + 1e-6, STEP), np.arange(Y0, Y1 + 1e-6, STEP)
TER = np.full((len(ys), len(xs)), 0.12)
# rays against the ground meshes only (scene.ray_cast through the whole building took 3+ minutes)
from mathutils.bvhtree import BVHTree  # noqa: E402
def _bvh(o):
    try:
        return BVHTree.FromObject(o, dg)
    except ValueError:                                   # (lawn_ground carries the grass GN: use its base mesh)
        mw = o.matrix_world
        return BVHTree.FromPolygons([mw @ v.co for v in o.data.vertices], [tuple(p_.vertices) for p_ in o.data.polygons])


_trees = [_bvh(bpy.data.objects[n]) for n in ("terrain_building", "lawn_ground") if n in bpy.data.objects]
for i, y in enumerate(ys):
    for j, x in enumerate(xs):
        best = None
        for t_ in _trees:
            loc, *_ = t_.ray_cast(Vector((x, y, 2.9)), Vector((0, 0, -1)))
            if loc is not None and (best is None or loc.z > best):
                best = loc.z
        if best is not None:
            TER[i, j] = best


def terrain(x, y):
    j = np.clip((np.asarray(x) - X0) / STEP, 0, len(xs) - 1.001); i = np.clip((np.asarray(y) - Y0) / STEP, 0, len(ys) - 1.001)
    j0, i0 = np.floor(j).astype(int), np.floor(i).astype(int); fj, fi = j - j0, i - i0
    return (TER[i0, j0] * (1 - fj) * (1 - fi) + TER[i0, j0 + 1] * fj * (1 - fi) + TER[i0 + 1, j0] * (1 - fj) * fi + TER[i0 + 1, j0 + 1] * fj * fi)


tick("ground sampled")
# the lawn's grass goes from the whole parking roof (the heath replaces it)
lg = bpy.data.objects.get("lawn_ground")
if lg:
    bm = bmesh.new(); bm.from_mesh(lg.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if 30.4 < f.calc_center_median().x < 77.0 and -15.0 < f.calc_center_median().y < 31.0], context="FACES")
    bm.to_mesh(lg.data); bm.free()

# ---------------------------------------------------------------- materials
granite = bc.pbr_material("granite_iddefjord_flamed", "granite_flamed_gridless", 1.2, box=True, tint=(1.0, 0.99, 0.97), sat=0.3, val=1.2,
                          rough_mul=0.9, rough_add=0.25, piece_var=0.07)
steel = bpy.data.materials.get("blackened_steel_d") or bc.material("blackened_steel", (0.03, 0.029, 0.028), 0.62, metal=0.7)
slot = bc.material("drain_slot", (0.004, 0.004, 0.004), 0.5)


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

    def add(self, c, u, along, across, top, depth, pr=None, slope=0.0):
        u = np.array([u[0], u[1], 0.0]); u /= np.linalg.norm(u); v = np.array([-u[1], u[0], 0.0])
        o = len(self.V)
        for dz in (top - depth, top):
            for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                self.V.append(np.array([c[0], c[1], dz + slope * a * along / 2]) + u * a * along / 2 + v * b * across / 2)
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
            s_ = 0.3 + 0.6 * k_
            S.add(cc, t, 0.6 - J, b - a - J, float(zf(s_)) + rng.normal(0, 0.001), 0.25, slope=float(zf(s_ + 0.3) - zf(s_ - 0.3)) / 0.6)
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
GROVE_S = (35.6, -6.6, 4.2, 2.8)               # the smaller south group (Roman 2026-11-03: "the trees")
LOOP = (62.0, 13.0, 4.5, 10.5)                 # the drop-off loop: centre, island radius, outer radius (model site.surfaces)
BAYS = (49.5, 21.5, 57.5, 27.0)


def asphalt(x, y):
    r = np.hypot(x - LOOP[0], y - LOOP[1])
    return ((r > LOOP[2] - 0.06) & (r < LOOP[3] + 0.06)) | ((x > BAYS[0] - 0.05) & (x < BAYS[2] + 0.05) & (y > BAYS[1] - 0.05) & (y < BAYS[3] + 0.05))
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
    z = np.where((x > CX0 - 0.6) & (x < CX1 + 1.0) & (y > CY0 - 1.0) & (y < CY1 + 1.0), fall(x), np.nan)   # the carpet + 1 m round it only
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
    for dx in (-1.1, -0.55, 0, 0.55, 1.1):
        for dy in (-1.1, -0.55, 0, 0.55, 1.1):
            near |= paved(wco[:, 0] + dx, wco[:, 1] + dy) | asphalt(wco[:, 0] + dx, wco[:, 1] + dy)
    pt = paved_top(wco[:, 0], wco[:, 1])
    ga = np.mean([terrain(wco[:, 0] + dx, wco[:, 1] + dy) for dx in (-0.8, 0, 0.8) for dy in (-0.8, 0, 0.8)], axis=0)
    pt = np.where(np.isnan(pt) & asphalt(wco[:, 0], wco[:, 1]) | (np.isnan(pt) & near), ga, pt)
    lower = near & ~np.isnan(pt) & (wco[:, 2] > pt - 0.06)
    co[lower, 2] -= (wco[lower, 2] - (pt[lower] - 0.06))
    tb.data.vertices.foreach_set("co", co.ravel().astype(np.float32)); tb.data.update()
    print("terrain_building: lowered", int(lower.sum()), "vertices under the paving")

HX0, HX1, HY0, HY1, HS = 30.6, 76.0, -14.0, 30.0, 0.25
gx, gy = np.meshgrid(np.arange(HX0, HX1 + 1e-6, HS), np.arange(HY0, HY1 + 1e-6, HS))
gz = terrain(gx, gy) + 0.02 + 0.45 * bump(gx, gy, *GROVE) + 0.4 * bump(gx, gy, *GROVE_S) - 0.38 * bump(gx, gy, *SWALE) + 0.03 * np.sin(gx * 1.3) * np.cos(gy * 1.7)
pv = paved(gx, gy)
ptop = paved_top(gx, gy)
gz = np.where(pv, np.minimum(gz, np.nan_to_num(ptop, nan=9) - 0.03), gz)              # tucked under the paving
am = asphalt(gx, gy)
gz = np.where(am, np.minimum(gz, np.mean([terrain(gx + dx, gy + dy) for dx in (-0.8, 0, 0.8) for dy in (-0.8, 0, 0.8)], axis=0) + 0.0), gz)   # and just under the asphalt
edge = ~pv & ~np.isnan(ptop)                                                         # the heath meets the paving's level at its edge
gz = np.where(edge, np.minimum(gz, ptop + 0.04 + 0.25 * np.clip(gz - ptop - 0.04, 0, None)), gz)
ny, nx = gx.shape
V = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], 1)
idx = np.arange(nx * ny).reshape(ny, nx)
F = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
heath = mesh_obj("heath_ground", V, F, heath_material(), smooth=True)
# the asphalt: the loop + the bays, on the ground's own grade (smoothed), clean black, no markings
def ground_smooth(x, y):
    """the ground averaged over ~1.6 m: asphalt lies on the grade, not on every bump"""
    return np.mean([terrain(x + dx, y + dy) for dx in (-0.8, 0, 0.8) for dy in (-0.8, 0, 0.8)], axis=0)


RA, RB = [], []
NS, NR = 160, 8
for i in range(NS):
    a_ = 2 * math.pi * i / NS
    for j in range(NR + 1):
        r_ = LOOP[2] + (LOOP[3] - LOOP[2]) * j / NR
        RA.append((LOOP[0] + math.cos(a_) * r_, LOOP[1] + math.sin(a_) * r_))
RA = np.array(RA); VA = np.c_[RA, ground_smooth(RA[:, 0], RA[:, 1]) + 0.03]
FA = [[i * (NR + 1) + j, ((i + 1) % NS) * (NR + 1) + j, ((i + 1) % NS) * (NR + 1) + j + 1, i * (NR + 1) + j + 1] for i in range(NS) for j in range(NR)]
bx, by_ = np.meshgrid(np.linspace(BAYS[0], BAYS[2], 17), np.linspace(BAYS[1], BAYS[3], 12))
VB = np.c_[bx.ravel(), by_.ravel(), ground_smooth(bx.ravel(), by_.ravel()) + 0.03]
ib = np.arange(bx.size).reshape(bx.shape)
FB = np.stack([ib[:-1, :-1].ravel(), ib[:-1, 1:].ravel(), ib[1:, 1:].ravel(), ib[1:, :-1].ravel()], 1) + len(VA)
asph_m = bc.material("asphalt_black", (0.035, 0.035, 0.037), 0.82)
mesh_obj("dropoff_asphalt", np.vstack([VA, VB]), FA + FB.tolist(), asph_m, smooth=True)
# granite kerbs: round the island (a 12 cm upstand) and the loop's outer edge (flush)
K = Boxes()
for rad, up in ((LOOP[2], 0.12), (LOOP[3], 0.01)):
    n_ = int(2 * math.pi * rad / 1.0)
    for i in range(n_):
        a0 = 2 * math.pi * i / n_; a1 = 2 * math.pi * (i + 1) / n_; am_ = (a0 + a1) / 2
        c_ = np.array([LOOP[0] + math.cos(am_) * rad, LOOP[1] + math.sin(am_) * rad])
        if rad == LOOP[3] and np.hypot(c_[0] - 52.0, c_[1] - 13.1) < 1.4:
            continue                                                       # (the path meets the loop here: no kerb)
        top = float(ground_smooth(c_[0], c_[1])) + 0.03 + up
        K.add(c_, (-math.sin(am_), math.cos(am_)), 2 * math.pi * rad / n_ - 0.006, 0.15, top, 0.3)
K.obj("kerbs", granite)
# the planting lives on the faces clear of the paving (a copy 1 mm down carries the scatter)
cell_free = ~(pv[:-1, :-1] | pv[:-1, 1:] | pv[1:, 1:] | pv[1:, :-1]).ravel()


def bed_y(x):
    t = (np.asarray(x) - SWALE[0]) / (SWALE[2] * 0.82)
    return SWALE[1] + 0.35 * np.sin(t * 2.4), np.abs(t) < 1


cxs, cys = (gx[:-1, :-1] + HS / 2).ravel(), (gy[:-1, :-1] + HS / 2).ravel()
by, bin_ = bed_y(cxs)
in_bed = bin_ & (np.abs(cys - by) < 0.38 + 0.12 * np.cos(cxs * 1.7))
cell_free &= ~in_bed
cell_free &= ~(am[:-1, :-1] | am[:-1, 1:] | am[1:, 1:] | am[1:, :-1]).ravel()
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


import json  # noqa: E402
from gen_greenwall import pothos_material  # noqa: E402
ATLAS_DIR = {"lingonberry": "lingon", "blueberry": "blueberry"}
ATLAS = {k: json.loads((ROOT / "plants" / "maps" / d / "atlas.json").read_text()) for k, d in ATLAS_DIR.items()}


def proto(name, kind, seed):
    """a dwarf-shrub clump along +Z: stems with leaves. heather: dense fine sprigs, mauve tips; lingonberry: low, small glossy
    dark leaves; blueberry: taller, bright green; fern: a few arching fronds (the swale)"""
    r = np.random.default_rng(seed)
    V, F, C, LF, UVmap = [], [], [], [], {}
    leaf_img = "leaf1" if kind == "blueberry" else f"leaf{1 + seed % 2}"      # (the second blueberry leaf read yellow)
    spec = {"heather": (16, (0.12, 0.26), 0.005, 0, (0.07, 0.09, 0.04)), "lingonberry": (26, (0.06, 0.15), 0.0, 12, (0.025, 0.07, 0.018)),
            "blueberry": (16, (0.2, 0.36), 0.0, 11, (0.07, 0.15, 0.03)), "fern": (8, (0.35, 0.6), 0.0, 14, (0.06, 0.14, 0.03))}[kind]
    n, (h0, h1), sprig_w, leaves, col = spec
    col = np.array(col)
    for _ in range(n):
        az = r.uniform(0, 2 * math.pi); lean = r.uniform(0.1, 0.5) if kind != "fern" else r.uniform(0.6, 1.1); h = r.uniform(h0, h1)
        base = np.array([r.normal(0, 0.03), r.normal(0, 0.03), 0]); d = np.array([math.cos(az), math.sin(az), 0]); side = np.array([-d[1], d[0], 0])
        pts = [base + d * lean * h * t * t + np.array([0, 0, h * (t - (0.5 if kind == "fern" else 0.2) * lean * t * t)]) for t in np.linspace(0, 1, 5)]
        if kind == "heather":                                          # Calluna: a wiry twig + side shoots, clothed in tiny scale leaves
            twigs = [pts]
            for _ in range(int(r.integers(2, 4))):                     # side shoots from the lower half
                k0 = int(r.integers(1, 3)); a2 = az + r.normal(0, 0.9); d2 = np.array([math.cos(a2), math.sin(a2), 0]); h2 = h * r.uniform(0.4, 0.7)
                b0 = pts[k0]
                twigs.append([b0 + d2 * 0.35 * h2 * t * t + np.array([0, 0, h2 * t * 0.9]) for t in np.linspace(0, 1, 4)])
            flower = r.random() < 0.3
            for tw in twigs:
                tw = np.array(tw)
                for k in range(len(tw) - 1):                           # the wood
                    o = len(V); w = 0.0012
                    V += [tw[k] - side * w, tw[k] + side * w, tw[k + 1] + side * w, tw[k + 1] - side * w]; F.append([o, o + 1, o + 2, o + 3])
                    C += [np.array([0.07, 0.05, 0.035])] * 4
                for q in range(int(26 * len(tw) / 5)):                 # the scale leaves, thick along the upper 75 %
                    t = r.uniform(0.25, 1.0); seg_ = min(int(t * (len(tw) - 1)), len(tw) - 2); f_ = t * (len(tw) - 1) - seg_
                    pp = tw[seg_] + (tw[seg_ + 1] - tw[seg_]) * f_
                    a3 = r.uniform(0, 2 * math.pi); ld = np.array([math.cos(a3), math.sin(a3), 1.4]); ld /= np.linalg.norm(ld)
                    nr = np.cross(ld, np.array([0, 0, 1.0])); nr /= (np.linalg.norm(nr) + 1e-9)
                    ll_ = 0.006; lw_ = 0.0016
                    o = len(V); V += [pp, pp + ld * ll_ * 0.5 + nr * lw_, pp + ld * ll_, pp + ld * ll_ * 0.5 - nr * lw_]; F.append([o, o + 1, o + 2, o + 3])
                    c = col * r.uniform(0.75, 1.2)
                    if flower and t > 0.7:
                        c = np.array([0.36, 0.2, 0.32]) * r.uniform(0.7, 1.1)
                    C += [c] * 4
            continue
        for k in range(4):                                             # the stem
            o = len(V); w = 0.0025 if kind != "fern" else 0.002
            V += [pts[k] - side * w, pts[k] + side * w, pts[k + 1] + side * w, pts[k + 1] - side * w]; F.append([o, o + 1, o + 2, o + 3]); C += [col * 0.6] * 4
        for k in range(leaves):                                        # the leaves (fern: pinnae both sides)
            t = (k + 1) / (leaves + 1) if kind == "fern" else r.uniform(0.25, 1)
            p = pts[0] + (pts[-1] - pts[0]) * t if kind != "fern" else pts[min(3, int(t * 4))] + (pts[min(4, int(t * 4) + 1)] - pts[min(3, int(t * 4))]) * (t * 4 % 1)
            if kind in ATLAS:                                          # a photo leaf card (plants/maps/lingon|blueberry), cupped
                info = ATLAS[kind][leaf_img]
                a_ = r.uniform(0, 2 * math.pi)
                ld = np.array([math.cos(a_), math.sin(a_), r.uniform(0.35, 0.9)]); ld /= np.linalg.norm(ld)
                ll = {"lingonberry": r.uniform(0.016, 0.026), "blueberry": r.uniform(0.02, 0.032)}[kind]; lw = ll * info["aspect"]
                bb = np.cross(ld, np.array([0, 0, 1.0])); bb /= (np.linalg.norm(bb) + 1e-9)
                nn = np.cross(bb, ld)
                o = len(V); G = 3
                for jv in range(G):
                    for ju in range(G):
                        u_, v_ = ju / (G - 1), jv / (G - 1)
                        x_ = (u_ - info["midrib_u"]) * lw; y_ = v_ * ll
                        UVmap[len(V)] = (u_, v_)
                        V.append(p + ld * y_ + bb * x_ + nn * (0.18 * (2 * x_ / lw) ** 2 * lw - 0.1 * v_ * v_ * ll))
                        C.append(col)
                for jv in range(G - 1):
                    for ju in range(G - 1):
                        LF.append([o + jv * G + ju, o + jv * G + ju + 1, o + (jv + 1) * G + ju + 1, o + (jv + 1) * G + ju])
                continue
            for sgn in ((-1, 1) if kind == "fern" else (1,)):
                ld = side * sgn if kind == "fern" else np.array([math.cos(r.uniform(0, 6.3)), math.sin(r.uniform(0, 6.3)), r.uniform(-0.1, 0.5)])
                ld = ld / np.linalg.norm(ld)
                ll = {"lingonberry": 0.016, "blueberry": 0.024, "fern": 0.07 * (1 - 0.6 * t)}[kind]; lw = ll * (0.55 if kind != "fern" else 0.18)
                nrm = np.cross(ld, np.array([0, 0, 1.0])); nrm = nrm / (np.linalg.norm(nrm) + 1e-9)
                o = len(V)
                V += [p, p + ld * ll * 0.5 + nrm * lw, p + ld * ll, p + ld * ll * 0.5 - nrm * lw]; F.append([o, o + 1, o + 2, o + 3])
                C += [col * r.uniform(0.8, 1.25)] * 4
    nF = len(F)
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], F + LF)
    ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
    for i, c in enumerate(C):
        ca.data[i].color = (*np.clip(c, 0, 1), 1)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); o.location = (0, 0, -2000)
    me.materials.append(proto_mat(name + "_m", {"heather": 0.7, "lingonberry": 0.32, "blueberry": 0.5, "fern": 0.55}[kind]))
    if LF:
        uvl = me.uv_layers.new(name="UVMap"); uvv = np.zeros((len(me.loops), 2), np.float32)
        lv = np.array([l.vertex_index for l in me.loops])
        UVa = np.zeros((len(V), 2), np.float32)
        for vi, uvp in UVmap.items():
            UVa[vi] = uvp
        uvl.data.foreach_set("uv", UVa[lv].ravel())
        va = me.attributes.new("var", "FLOAT", "POINT"); va.data.foreach_set("value", r.uniform(-0.8, 0.8, len(V)).astype(np.float32))
        me.materials.append(pothos_material(leaf_img, ROOT / "plants" / "maps" / ATLAS_DIR[kind], rough=0.3 if kind == "lingonberry" else 0.45, val=0.85 if kind == "lingonberry" else 0.7, bump=0.0004))
        mi = np.zeros(len(me.polygons), np.int32); mi[nF:] = 1; me.polygons.foreach_set("material_index", mi)
    return o


heath_protos = [proto(f"heather_{i}", "heather", i) for i in range(3)] + [proto(f"lingon_{i}", "lingonberry", 10 + i) for i in range(3)] + \
               [proto(f"blueb_{i}", "blueberry", 20 + i) for i in range(2)]
swale_protos = [ground.grass_proto("tuft_meadow_e", "meadow", coll)] + heath_protos[3:8]     # sedge + lingonberry + blueberry (the dry hair grass read as straw)
bedg = mesh_obj("stream_bed", V + np.array([0, 0, 0.004]), F[in_bed], bc.pbr_material("river_gravel", "river_small_rocks", 1.0, piece_var=0.0, val=0.5, sat=0.7))
for nm, sel, protos, dens in (("heath_plants", cell_free & ~in_swale, heath_protos, 60), ("heath_grass", cell_free & ~in_swale, [ground.grass_proto("tuft_dry_e", "dry", coll)], 3),
                              ("swale_plants", cell_free & in_swale, swale_protos, 75)):
    o = mesh_obj(nm, V2, F[sel], heath.data.materials[0])
    md = o.modifiers.new("plants", "NODES"); md.node_group = ground.grass_nodes("GN_" + nm, protos, dens, seed=len(nm))

if SHOT == "build_only":
    print("protos", [(o.name, len(o.data.polygons), len(o.data.materials)) for o in heath_protos]); raise SystemExit
# ---------------------------------------------------------------- stones (Roman: "the stones look way too weird and bad": they were smooth eggs)
def stone_material(name, mapname, tile, tone=(0.85, 1.15), moss=0.0):
    """a generated close-up photo (landscape/maps/<mapname>_col/_h), box-projected at its real size; every stone its own tone;
    a darker, earthier band where it goes into the ground; moss on the up-facing tops if moss > 0"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.88
    tc = N.new("ShaderNodeTexCoord"); oi = N.new("ShaderNodeObjectInfo")
    off = N.new("ShaderNodeVectorMath"); off.operation = "SCALE"; L.new(oi.outputs["Random"], off.inputs["Scale"]); off.inputs[0].default_value = (13.7, 7.3, 5.1)
    ad = N.new("ShaderNodeVectorMath"); ad.operation = "ADD"; L.new(tc.outputs["Object"], ad.inputs[0]); L.new(off.outputs[0], ad.inputs[1])
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tile,) * 3; L.new(ad.outputs[0], mp.inputs["Vector"])
    ci = N.new("ShaderNodeTexImage"); ci.image = bpy.data.images.load(str(ROOT / "landscape" / "maps" / f"{mapname}_col.jpg")); ci.projection = "BOX"; ci.projection_blend = 0.3
    hi = N.new("ShaderNodeTexImage"); hi.image = bpy.data.images.load(str(ROOT / "landscape" / "maps" / f"{mapname}_h.png")); hi.projection = "BOX"; hi.projection_blend = 0.3
    hi.image.colorspace_settings.name = "Non-Color"
    for t in (ci, hi):
        L.new(mp.outputs[0], t.inputs["Vector"])
    tn = N.new("ShaderNodeMapRange"); tn.inputs[3].default_value, tn.inputs[4].default_value = tone; L.new(oi.outputs["Random"], tn.inputs[0])
    bc_ = N.new("ShaderNodeBrightContrast"); bc_.inputs["Contrast"].default_value = 0.35; L.new(ci.outputs["Color"], bc_.inputs["Color"])
    hs = N.new("ShaderNodeHueSaturation"); L.new(tn.outputs[0], hs.inputs["Value"]); L.new(bc_.outputs[0], hs.inputs["Color"])
    hu = N.new("ShaderNodeMapRange"); hu.inputs[3].default_value = 0.47; hu.inputs[4].default_value = 0.53; L.new(oi.outputs["Random"], hu.inputs[0]); L.new(hu.outputs[0], hs.inputs["Hue"])
    # weathering: big soft darker patches and streaks down the sides
    wn = N.new("ShaderNodeTexNoise"); wn.inputs["Scale"].default_value = 1.6; wn.inputs["Detail"].default_value = 6; wn.inputs["Roughness"].default_value = 0.6
    L.new(ad.outputs[0], wn.inputs["Vector"])
    wr = N.new("ShaderNodeMapRange"); wr.inputs[1].default_value = 0.35; wr.inputs[2].default_value = 0.65; wr.inputs[3].default_value = 0.55; wr.inputs[4].default_value = 1.0
    L.new(wn.outputs["Fac"], wr.inputs[0])
    wm = N.new("ShaderNodeMix"); wm.data_type = "RGBA"; wm.blend_type = "MULTIPLY"; wm.inputs["Factor"].default_value = 1.0
    L.new(hs.outputs[0], wm.inputs["A"]); L.new(wr.outputs[0], wm.inputs["B"])
    # the foot: earthier and darker over the bottom 12 cm above the ground line (object z: 0 = ground)
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    ft = N.new("ShaderNodeMapRange"); ft.inputs[1].default_value = -0.02; ft.inputs[2].default_value = 0.12; ft.inputs[3].default_value = 1; ft.inputs[4].default_value = 0
    L.new(sep.outputs["Z"], ft.inputs[0])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; L.new(ft.outputs[0], mx.inputs["Factor"])
    L.new(wm.outputs["Result"], mx.inputs["A"]); mx.inputs["B"].default_value = (0.45, 0.38, 0.3, 1)
    col = mx.outputs["Result"]
    if moss:
        gm = N.new("ShaderNodeNewGeometry"); sn = N.new("ShaderNodeSeparateXYZ"); L.new(gm.outputs["Normal"], sn.inputs[0])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 8; L.new(tc.outputs["Object"], nz.inputs["Vector"])
        up = N.new("ShaderNodeMath"); up.operation = "MULTIPLY"; L.new(sn.outputs["Z"], up.inputs[0]); L.new(nz.outputs["Fac"], up.inputs[1])
        mf = N.new("ShaderNodeMapRange"); mf.inputs[1].default_value = 0.42; mf.inputs[2].default_value = 0.52; mf.inputs[4].default_value = moss
        L.new(up.outputs[0], mf.inputs[0])
        mm = N.new("ShaderNodeMix"); mm.data_type = "RGBA"; L.new(mf.outputs[0], mm.inputs["Factor"]); L.new(col, mm.inputs["A"])
        mm.inputs["B"].default_value = (0.07, 0.11, 0.03, 1); col = mm.outputs["Result"]
    L.new(col, b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.01
    L.new(hi.outputs["Color"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


boulder_m = stone_material("boulder_granite", "boulder", 1.1, (0.42, 0.66), moss=0.7)
cobble_m = stone_material("river_cobble", "cobble", 0.35, (0.38, 0.9))


def stone_mesh(name, r, aspect, seed, cuts, smooth_it=3, noise=0.035, sub=5):
    """a glacial stone: an ellipsoid sheared by random planes (the flat, chipped faces of split granite), the edges worn round,
    a little lumpy; origin at the ground line"""
    rr = np.random.default_rng(seed)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    vs = np.array([v.co for v in bm.verts]) * np.array(aspect)
    for _ in range(cuts):
        n = rr.normal(0, 1, 3); n[2] = abs(n[2]) * 0.6 if rr.random() < 0.7 else n[2]; n /= np.linalg.norm(n)
        sup = (vs @ n).max(); d = sup * rr.uniform(0.5, 0.8)
        over = np.clip(vs @ n - d, 0, None)
        vs -= np.outer(over * rr.uniform(0.92, 1.0), n)
    for v, c in zip(bm.verts, vs):
        v.co = c
    for _ in range(smooth_it):                                         # worn edges, not rounded lumps
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.35, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    k = rr.normal(0, 1, (4, 3)); P = np.array([v.co for v in bm.verts])
    P = P * (1 + sum(np.sin(P @ k[i] * (2.5 + 1.5 * i) + i) * noise / (1 + i) for i in range(4)))[:, None]
    for v, c in zip(bm.verts, P):
        v.co = c
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.transform(__import__("mathutils").Matrix.Diagonal((r, r, r, 1)))
    return me


def place_stone(name, me, x, y, sink, mat, yaw):
    zs = me.vertices; zmin = min(v.co.z for v in zs); zmax = max(v.co.z for v in zs)
    zb = float(terrain(x, y)) + 0.45 * float(bump(x, y, *GROVE)) + 0.4 * float(bump(x, y, *GROVE_S)) - 0.38 * float(bump(x, y, *SWALE)) + 0.02
    me.transform(__import__("mathutils").Matrix.Translation((0, 0, -(zmin + (zmax - zmin) * sink))))
    o = bpy.data.objects.new(name, me); coll.objects.link(o); me.materials.append(mat)
    o.location = (x, y, zb); o.rotation_euler[2] = yaw
    return o


# boulders: glacial erratics in small clusters (one big one with smaller ones leaning on it), half buried in the heath
CLUSTERS = [((44.9, 16.4), 1.15, 3), ((42.3, 7.6), 0.8, 2), ((34.8, 1.4), 0.95, 2), ((50.4, 4.7), 0.55, 1), ((33.6, 22.0), 0.6, 1), ((51.4, 9.2), 0.45, 1)]
k_ = 0
for (cx, cy), R, n in CLUSTERS:
    for j in range(n):
        r = R if j == 0 else R * rng.uniform(0.3, 0.5)
        a = rng.uniform(0, 2 * math.pi); dd = 0 if j == 0 else R * rng.uniform(0.95, 1.3)
        me = stone_mesh(f"boulder_{k_}", r, (1.0, rng.uniform(0.7, 0.9), rng.uniform(0.5, 0.68)), 200 + k_, cuts=int(rng.integers(9, 14)), smooth_it=1, noise=0.045)
        place_stone(f"boulder_{k_}", me, cx + math.cos(a) * dd, cy + math.sin(a) * dd, rng.uniform(0.3, 0.42), boulder_m, rng.uniform(0, 6.3)); k_ += 1
# river stones: a dry stream bed down the middle of the swale, packed, bigger ones at the bends, smaller ones in between
for i in range(420):
    t = rng.uniform(-1, 1); x = SWALE[0] + t * SWALE[2] * 0.82; y = SWALE[1] + 0.35 * math.sin(t * 2.4) + float(np.clip(rng.normal(0, 0.17), -0.36, 0.36))
    r = float(rng.choice([rng.uniform(0.03, 0.08), rng.uniform(0.08, 0.16), rng.uniform(0.16, 0.3)], p=[0.6, 0.3, 0.1]))
    me = stone_mesh(f"cobble_{i}", r, (1.0, rng.uniform(0.55, 0.85), rng.uniform(0.3, 0.5)), 500 + i, cuts=int(rng.integers(1, 5)), smooth_it=3, noise=0.04, sub=3)
    place_stone(f"cobble_{i}", me, x, y, rng.uniform(0.25, 0.4), cobble_m, rng.uniform(0, 6.3))
tick("heath + rocks")
# ---------------------------------------------------------------- the birch grove (multi-stem silver birch on the mound)
import gen_birch  # noqa: E402
if SHOT != "stones":
    GROVE_LIB = ROOT / "landscape" / "out" / "grove_v4.blend"     # grown once, then appended (3 minutes of birch growing per shot)
    if GROVE_LIB.exists():
        with bpy.data.libraries.load(str(GROVE_LIB), link=False) as (src, dst):
            dst.objects = [n for n in src.objects if n.startswith("grove_birch_")]
        for o in dst.objects:
            coll.objects.link(o)
        print("grove: appended", len(dst.objects), "objects")
    else:
        grove = []
        for k, (x, y, h) in enumerate(((36.0, 21.2, 7.2), (38.8, 22.7, 8.0), (40.2, 20.6, 6.4), (35.4, 23.4, 6.8),
                                        (34.6, -6.0, 6.6), (37.4, -7.4, 7.6), (35.8, -8.6, 5.8))):   # north grove + south group
            zb = float(terrain(x, y)) + 0.45 * float(bump(x, y, *GROVE)) + 0.4 * float(bump(x, y, *GROVE_S))
            objs = gen_birch.build(40 + k, (x, y, zb - 0.05), height=h, name=f"grove_birch_{k}", leaf_scale=1.5)   # (real leaves on a 7 m birch: 4-6 cm)
            for o in objs:
                for c in o.users_collection:
                    c.objects.unlink(o)
                coll.objects.link(o); grove.append(o)
        if SHOT not in ("stones", "build_only"):                   # (the cache must sit on the real ground)
            GROVE_LIB.parent.mkdir(exist_ok=True)
            bpy.data.libraries.write(str(GROVE_LIB), set(grove), compress=True)
            print("grove: cached to", GROVE_LIB)

# ---------------------------------------------------------------- the shots
CAMS = {
    "arrive": ((52.6, 13.4), 1.65, (31.0, 11.3, 2.2), 24),
    "corner": ((45.2, 22.6), 1.7, (33.0, 9.8, 1.0), 22),
    "door": ((33.7, 16.6), 1.62, (48.0, 8.5, 0.9), 20),
    "aerial": ((63.5, -5.0), 21.0, (46.0, 11.0, 0.0), 22),
    "loop": ((66.5, 2.8), 1.65, (36.0, 13.5, 1.8), 22),
}
if SHOT == "stones":
    out = ROOT / "landscape" / "work"; out.mkdir(exist_ok=True)
    for i_, (c_, t_, l_) in enumerate((((47.6, 13.6, 1.3), (44.6, 16.6, 0.3), 30), ((47.0, 3.4, 1.4), (44.8, 6.6, 0.0), 30))):
        bc.camera(scene, f"cam_st{i_}", c_, t_, l_); scene.camera = bpy.data.objects[f"cam_st{i_}"]
        scene.render.filepath = str(out / f"stones_{i_}.png"); bpy.ops.render.render(write_still=True); print("wrote", scene.render.filepath)
    raise SystemExit
(cx, cy), h, tgt, lens = CAMS[SHOT]
loc = (cx, cy, float(terrain(cx, cy)) + h)
if DRAFT:
    scene.cycles.samples = 32; scene.render.resolution_percentage = 60
# ---------------------------------------------------------------- pines (the forest's own trees from construction/out/tree_lib.blend)
# Scots pines close the forecourt to the south and north, off the parking roof (x 30.5-60, y -9.5..24: 1.2 m of soil);
# young pines stand in the heath on low mounds, the way pines seed into a heath at a forest edge.
PINES = [  # (x, y, library variant, height m)
    (52.6, -11.6, 6, 15.5), (58.8, -10.4, 8, 13.0), (46.0, -12.2, 7, 12.0),        # south: the bike shelter side
    (45.4, 26.8, 9, 13.5), (56.8, 27.6, 6, 16.0), (34.2, 27.0, 8, 12.5),          # north: behind the grove + the bays
    (67.4, -6.0, 7, 14.0)]                                                          # south-east of the loop
YOUNG = []                                                                       # (the library's young trees are spruces: wrong in an open heath)
VH = {6: 14, 7: 13, 8: 15, 9: 12, 10: 3.0, 11: 2.2, 12: 3.8}                    # tools/forest_scatter.py VAR heights
for k, (x, y, v, h) in enumerate(PINES + YOUNG):
    near_ = math.hypot(x - loc[0], y - loc[1]) < 18 if SHOT != "stones" else True
    cname = f"v{v:02d}_L{0 if near_ else 1}"                       # full needles only near the camera (the GPU ran out with 7 at L0)
    if cname not in bpy.data.collections:
        with bpy.data.libraries.load(str(ROOT / "construction" / "out" / "tree_lib.blend"), link=False) as (src, dst):
            dst.collections = [cname]
    e = bpy.data.objects.new(f"pine_{k}", None); e.instance_type = "COLLECTION"; e.instance_collection = bpy.data.collections[cname]
    zb = float(terrain(x, y)) - 0.15 + (0.25 * float(bump(x, y, x, y, 1.6, 1.6)) if v >= 10 else 0)
    e.location = (x, y, zb); s_ = h / VH[v]; e.scale = (s_, s_, s_); e.rotation_euler[2] = rng.uniform(0, 6.3)
    coll.objects.link(e)
print("pines:", len(PINES), "+", len(YOUNG), "young")

name = f"ent_{SHOT}"
bc.camera(scene, f"cam_{name}", loc, tgt, lens)
lod = bpy.data.objects.get("lod_eye")
if SHOT == "aerial" and lod:      # from the air the forest needs no needles: its LOD eye 60 m up (the GPU ran out with 7 birches)
    lod.location = (loc[0], loc[1], loc[2] + 60); bpy.context.view_layer.update(); lod = None
shoot.shoot(scene, name, name, EXPO, 5, lod)

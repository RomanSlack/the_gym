"""Assemble the site in Blender: terrain (detail + real context), water + falls,
Gym V2 massing, placeholder forest, sun/sky, cameras. Renders previews.

blender -b --factory-startup --python terrain/blender_scene.py -- <out_dir> [render]
Heights are relative to ±0.00 (F1 = model datum masl). x east, y north, metres.
"""
import sys, json, math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "terrain" / "out" / "ravine"
SITE = ROOT / "terrain" / "out" / "site"
args = sys.argv[sys.argv.index("--") + 1:]
OUT = Path(args[0]); OUT.mkdir(parents=True, exist_ok=True)
RENDER = len(args) > 1 and args[1] == "render"
model = json.loads((ROOT / "model" / "building.json").read_text())
DATUM = model["project"]["datum"]["masl"]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
rng = np.random.default_rng(3)


def grid_mesh(name, H, x0, y0, res, attrs=None):
    ny, nx = H.shape
    xs = x0 + np.arange(nx, dtype=np.float32) * res
    ys = y0 + np.arange(ny, dtype=np.float32) * res
    X, Y = np.meshgrid(xs, ys)
    verts = np.stack([X, Y, H.astype(np.float32)], -1).reshape(-1, 3)
    i = np.arange(nx * ny).reshape(ny, nx)
    quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1).reshape(-1, 4)
    return mesh_from(name, verts, quads, attrs)


def mesh_from(name, verts, faces, attrs=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", np.asarray(verts, np.float32).ravel())
    faces = np.asarray(faces)
    me.loops.add(faces.size); me.loops.foreach_set("vertex_index", faces.ravel())
    me.polygons.add(len(faces))
    me.polygons.foreach_set("loop_start", np.arange(0, faces.size, faces.shape[1]))
    me.polygons.foreach_set("loop_total", np.full(len(faces), faces.shape[1]))
    me.update()
    if smooth:
        me.polygons.foreach_set("use_smooth", np.ones(len(faces), bool))
    for k, v in (attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", "POINT")
        a.data.foreach_set("value", np.asarray(v, np.float32).ravel())
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def material(name, build):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    build(nt, bsdf)
    return m


# ---------------- terrain ----------------
H = np.load(RV / "eroded_1m.npy")          # 2000 x 2000, x,y in [-1000, 1000)
rock = np.load(RV / "rock_1m.npy")
D = 320                                     # detail half-size at 1 m
c = slice(1000 - D, 1000 + D)
FEAT = np.load(RV / "features_1m.npy")
detail = grid_mesh("terrain_detail", H[c, c], -D + 0.5, -D + 0.5, 1.0, {"rock": rock[c, c], "feat": FEAT[c, c].astype(np.float32)})

ctx = np.load(SITE / "context_4m.npy") - DATUM   # 2000 x 2000 at 4 m over [-4000, 4000)
core4 = H.reshape(500, 4, 500, 4).mean((1, 3))
ctx[750:1250, 750:1250] = core4
ctx[750 + 80 - 2:1250 - 80 + 2, 750 + 80 - 2:1250 - 80 + 2] -= 0.6   # tuck under the detail mesh
far = grid_mesh("terrain_context", ctx[::2, ::2], -4000 + 2, -4000 + 2, 8.0,
                {"rock": np.zeros(ctx[::2, ::2].shape)})


def terrain_mat(nt, bsdf):
    N = nt.nodes; L = nt.links
    attr = N.new("ShaderNodeAttribute"); attr.attribute_name = "rock"
    geo = N.new("ShaderNodeNewGeometry")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    slope = N.new("ShaderNodeMapRange"); slope.inputs[1].default_value = 0.9; slope.inputs[2].default_value = 0.7  # ravine sides read as rock
    L.new(sep.outputs["Z"], slope.inputs[0])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(attr.outputs["Fac"], mx.inputs[0]); L.new(slope.outputs[0], mx.inputs[1])
    noise = N.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.08
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.05, 0.02, 1)   # forest floor / moss
    ramp.color_ramp.elements[1].color = (0.075, 0.065, 0.035, 1)  # dry needles
    L.new(noise.outputs["Fac"], ramp.inputs[0])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (0.085, 0.085, 0.08, 1)      # granite / gneiss
    L.new(mx.outputs[0], mix.inputs["Factor"]); L.new(ramp.outputs["Color"], mix.inputs["A"])
    feat = N.new("ShaderNodeAttribute"); feat.attribute_name = "feat"
    col = mix.outputs["Result"]
    # bit flags from terrain/ravine.py MASK: asphalt 1, shoulder 2, court 4, ramp 8, garden 16, path 32
    for bit, rgb in ((16, (0.05, 0.09, 0.03)), (2, (0.16, 0.15, 0.13)), (32, (0.20, 0.19, 0.17)), (8, (0.03, 0.03, 0.03)), (1, (0.018, 0.018, 0.02))):
        div = N.new("ShaderNodeMath"); div.operation = "DIVIDE"; div.inputs[1].default_value = bit
        L.new(feat.outputs["Fac"], div.inputs[0])
        fl = N.new("ShaderNodeMath"); fl.operation = "FLOOR"; L.new(div.outputs[0], fl.inputs[0])
        md = N.new("ShaderNodeMath"); md.operation = "MODULO"; md.inputs[1].default_value = 2; L.new(fl.outputs[0], md.inputs[0])
        gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5; L.new(md.outputs[0], gt.inputs[0])
        mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"; mx2.inputs["B"].default_value = (*rgb, 1)
        L.new(gt.outputs[0], mx2.inputs["Factor"]); L.new(col, mx2.inputs["A"])
        col = mx2.outputs["Result"]
    L.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95


tm = material("terrain", terrain_mat)
detail.data.materials.append(tm)


def canopy_mat(nt, bsdf):
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.02
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.018, 0.035, 0.018, 1)
    ramp.color_ramp.elements[1].color = (0.04, 0.06, 0.03, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 1.0


far.data.materials.append(material("canopy_far", canopy_mat))

# ---------------- water ----------------
W = np.load(RV / "water_1m.npy")[c, c]
wet = ~np.isnan(W)
ny, nx = W.shape
i = np.arange(nx * ny).reshape(ny, nx)
q = wet[:-1, :-1] & wet[:-1, 1:] & wet[1:, 1:] & wet[1:, :-1]
quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1)[q]
xs = np.arange(nx) - D + 0.5
X, Y = np.meshgrid(xs, xs)
Wz = np.nan_to_num(W, nan=-50) + 0.02
used = np.unique(quads)
remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used))
wverts = np.stack([X.ravel()[used], Y.ravel()[used], Wz.ravel()[used]], 1)
water = mesh_from("water", wverts, remap[quads])


def water_mat(nt, bsdf):
    bsdf.inputs["Base Color"].default_value = (0.02, 0.05, 0.05, 1)
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["Transmission Weight"].default_value = 0.6
    bsdf.inputs["IOR"].default_value = 1.33


water.data.materials.append(material("water", water_mat))

# falls: a curtain wherever the water level drops > 2 m between stations a few metres apart
st = sorted(model["site"]["ravine"]["stations"], key=lambda s: -s["y"])
foam = material("falls", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.85, 0.9, 0.9, 1)),
                                         b.inputs["Roughness"].__setattr__("default_value", 0.5)))
for a, b in zip(st, st[1:]):
    if a["water"] - b["water"] > 2 and a["y"] - b["y"] < 6:
        ym = (a["y"] + b["y"]) / 2
        hw = a["half_bed"] + 0.5
        xc = (a["x"] + b["x"]) / 2
        n = 24
        vs, fs = [], []
        for k in range(n + 1):
            x = xc - hw + 2 * hw * k / n
            jitter = 0.4 * math.sin(k * 1.7)
            vs += [(x, ym + 0.6 + jitter * 0.3, a["water"]), (x, ym - 0.8 + jitter, b["water"] + 0.3)]
            if k:
                fs.append((2 * k - 2, 2 * k, 2 * k + 1, 2 * k - 1))
        f = mesh_from(f"falls_{a['id']}", vs, fs)
        f.data.materials.append(foam)

# ---------------- Gym V2 massing ----------------
ext = json.loads((ROOT / "reference" / "gym_v2_original" / "gymv2_extract.json").read_text())
dz = -model["project"]["datum"]["blender_z_gymv2"]
clay = material("clay", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.78, 0.76, 0.72, 1)),
                                        b.inputs["Roughness"].__setattr__("default_value", 0.8)))
mv, mf = [], []
for e in ext["elements"]:
    if e["kind"] not in ("slab", "column", "wall", "beam", "panel", "block") or e["hidden"] or e["name"] == "Cube.033":  # Cube.033 = old sauna cube
        continue
    z0, z1 = e["z"][0] + dz, e["z"][1] + dz
    base = len(mv)
    for (x, y) in e["plan"]:
        mv.append((x, y, z0))
    for (x, y) in e["plan"]:
        mv.append((x, y, z1))
    mf += [(base, base + 3, base + 2, base + 1), (base + 4, base + 5, base + 6, base + 7)]
    mf += [(base + k, base + (k + 1) % 4, base + 4 + (k + 1) % 4, base + 4 + k) for k in range(4)]
mass = mesh_from("gymv2_massing", mv, mf, smooth=False)
mass.data.materials.append(clay)

# scale figures (6 ft) from Gym V2
fig_m = material("figure", lambda nt, b: b.inputs["Base Color"].__setattr__("default_value", (0.55, 0.2, 0.1, 1)))
for e in ext["elements"]:
    if e["kind"] == "person":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.83, location=(e["at"][0], e["at"][1], e["at"][2] + dz + 0.915), vertices=8)
        bpy.context.object.data.materials.append(fig_m)

# ---------------- placeholder forest ----------------
def tree_proto(name, kind, h):
    vs, fs = [], []
    def cone(z0, z1, r, n=8):
        b = len(vs)
        for k in range(n):
            a = 2 * math.pi * k / n
            vs.append((r * math.cos(a), r * math.sin(a), z0))
        vs.append((0, 0, z1))
        fs.extend([(b + k, b + (k + 1) % n, b + n) for k in range(n)])
    cone(0, h * 0.3, h * 0.03, 5)  # trunk
    if kind == "spruce":
        for k in range(4):
            cone(h * (0.18 + 0.2 * k), h * (0.45 + 0.18 * k), h * 0.2 * (1 - 0.2 * k))
    else:  # pine: tall trunk, rounded crown
        cone(0, h * 0.7, h * 0.035, 5)
        for k in range(3):
            cone(h * (0.6 + 0.1 * k), h * (0.8 + 0.07 * k), h * 0.17 * (1 - 0.25 * k))
    ob = mesh_from(name, vs, [f + (f[-1],) if len(f) == 3 else f for f in fs], smooth=False)
    ob.data.materials.append(material(name + "_m", lambda nt, b: (
        b.inputs["Base Color"].__setattr__("default_value", (0.03, 0.07, 0.03, 1) if kind == "spruce" else (0.05, 0.09, 0.03, 1)),
        b.inputs["Roughness"].__setattr__("default_value", 0.9))))
    ob.hide_render = False
    ob.location = (0, 0, -500)
    return ob


Hd = H[c, c]
gy, gx = np.gradient(Hd)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
clear = np.zeros(Hd.shape, bool)
pads = model["site"]["pads"]
for p in pads:
    poly = np.array(p["poly"])
    lo, hi = poly.min(0) - 12, poly.max(0) + 12
    clear |= (X > lo[0]) & (X < hi[0]) & (Y > lo[1]) & (Y < hi[1])
works = FEAT[c, c] > 0
for _ in range(9):  # keep trees ~9 m off roads, paths, garden, sauna (crowns are ~4 m wide)
    works = works | np.roll(works, 1, 0) | np.roll(works, -1, 0) | np.roll(works, 1, 1) | np.roll(works, -1, 1)
ok = (slope < 32) & np.isnan(np.load(RV / "water_1m.npy")[c, c]) & ~clear & (rock[c, c] < 0.3) & ~works
cand = np.argwhere(ok)
pick = cand[rng.random(len(cand)) < 1 / 28]
pick = pick + rng.random(pick.shape) - 0.5
protos = [tree_proto("spruce_a", "spruce", 22), tree_proto("spruce_b", "spruce", 16), tree_proto("pine_a", "pine", 24)]
for k, proto in enumerate(protos):
    sel = pick[k::3]
    zz = Hd[sel[:, 0].astype(int), sel[:, 1].astype(int)]
    pv = np.stack([sel[:, 1] - D + 0.5, sel[:, 0] - D + 0.5, zz], 1)
    holder = mesh_from(f"forest_{proto.name}", pv, np.zeros((0, 4), int))
    proto.parent = holder
    proto.location = (0, 0, 0)
    holder.instance_type = "VERTS"
ring = rng.random((95000, 2)) * 2400 - 1200
ring = ring[(np.abs(ring).max(1) > D)]
road_xy = np.array([p[:2] for p in model["site"]["features"]["road"]["points"]])
dmin = np.min(np.hypot(ring[:, None, 1] - road_xy[None, :, 0], ring[:, None, 0] - road_xy[None, :, 1]), axis=1)
ring = ring[dmin > 12]  # keep the road corridor open beyond the detail area
cz = ctx[((ring[:, 0] + 4000) / 4).astype(int), ((ring[:, 1] + 4000) / 4).astype(int)]
ring_v = np.stack([ring[:, 1], ring[:, 0], cz - 0.6], 1)
for k, proto in enumerate(protos):
    holder = mesh_from(f"forest_far_{proto.name}", ring_v[k::3], np.zeros((0, 4), int))
    inst = proto.copy(); inst.data = proto.data
    scene.collection.objects.link(inst)
    inst.parent = holder; inst.location = (0, 0, 0)
    holder.instance_type = "VERTS"
print("trees", len(pick), "far", len(ring_v))

# ---------------- rock: blocks on cliff walls + boulders ----------------
def rock_variant(seed):
    r = np.random.default_rng(seed)
    v = np.array([(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)], float)
    v = v[np.abs(v).sum(1) > 0] * (1 + r.normal(0, 0.18, (26, 1)))
    v[:, 2] *= r.uniform(0.45, 0.75)  # granite breaks in slabs
    # convex hull of jittered box corners/edges -> faceted chunk
    import bmesh
    bm = bmesh.new()
    for p in v:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    return bm


import bmesh  # noqa: E402
variants = [rock_variant(k) for k in range(6)]
rock_bm = bmesh.new()
Hfull = H[c, c]
gyd, gxd = np.gradient(Hfull)
built = FEAT[c, c] > 0
for _ in range(4):  # no natural rock on or right next to built works (terraces, ramp walls, paths)
    built = built | np.roll(built, 1, 0) | np.roll(built, -1, 0) | np.roll(built, 1, 1) | np.roll(built, -1, 1)
steep = (np.degrees(np.arctan(np.hypot(gxd, gyd))) > 48) & (rock[c, c] > 0.25) & ~built
pad_box = np.zeros(steep.shape, bool)
for p in model["site"]["pads"]:
    poly = np.array(p["poly"]); lo, hi = poly.min(0) - 1.5, poly.max(0) + 1.5
    pad_box |= (X > lo[0]) & (X < hi[0]) & (Y > lo[1]) & (Y < hi[1])
steep &= ~pad_box
cells = np.argwhere(steep)
cells = cells[rng.random(len(cells)) < 0.45]
nb_max = np.maximum.reduce([np.roll(np.roll(Hfull, a, 0), b, 1) for a in (-1, 0, 1) for b in (-1, 0, 1)])
nb_min = np.minimum.reduce([np.roll(np.roll(Hfull, a, 0), b, 1) for a in (-1, 0, 1) for b in (-1, 0, 1)])
blocks = 0
for (j, i) in cells:
    z0, z1 = nb_min[j, i], nb_max[j, i]
    nx_, ny_ = -gxd[j, i], -gyd[j, i]
    nl = math.hypot(nx_, ny_) + 1e-6
    out = (nx_ / nl, ny_ / nl)
    for zc in np.arange(z0 + 0.8, z1 + 0.4, rng.uniform(1.6, 2.6)):
        bm_src = variants[rng.integers(6)]
        sc = rng.uniform(1.0, 2.2)
        ang = math.atan2(out[1], out[0]) + rng.normal(0, 0.3)
        ca, sa = math.cos(ang), math.sin(ang)
        px = i - D + 0.5 - out[0] * 0.6 * sc + rng.normal(0, 0.3)
        py = j - D + 0.5 - out[1] * 0.6 * sc + rng.normal(0, 0.3)
        base_i = len(rock_bm.verts)
        new = []
        for v in bm_src.verts:
            x, y, z = v.co.x * sc * 1.3, v.co.y * sc, v.co.z * sc
            new.append(rock_bm.verts.new((px + ca * x - sa * y, py + sa * x + ca * y, zc + z)))
        for f in bm_src.faces:
            rock_bm.faces.new([new[v.index] for v in f.verts])
        blocks += 1
# boulders at wall feet and along the water's edge
wet = ~np.isnan(np.load(RV / "water_1m.npy")[c, c])
edge = wet & ~(np.roll(wet, 1, 0) & np.roll(wet, -1, 0) & np.roll(wet, 1, 1) & np.roll(wet, -1, 1))
for (j, i) in np.argwhere(edge)[rng.random(int(edge.sum())) < 0.12]:
    bm_src = variants[rng.integers(6)]
    sc = rng.uniform(0.4, 1.4)
    new = [rock_bm.verts.new((i - D + 0.5 + v.co.x * sc, j - D + 0.5 + v.co.y * sc, Hfull[j, i] + v.co.z * sc * 0.6)) for v in bm_src.verts]
    for f in bm_src.faces:
        rock_bm.faces.new([new[v.index] for v in f.verts])
rock_me = bpy.data.meshes.new("rocks")
rock_bm.to_mesh(rock_me)
rocks = bpy.data.objects.new("rocks_cliffs", rock_me)
scene.collection.objects.link(rocks)


def rock_mat(nt, bsdf):
    N = nt.nodes; L = nt.links
    noise = N.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.6
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.048, 1)
    ramp.color_ramp.elements[1].color = (0.13, 0.13, 0.12, 1)
    lic = ramp.color_ramp.elements.new(0.72); lic.color = (0.10, 0.11, 0.07, 1)  # lichen
    L.new(noise.outputs["Fac"], ramp.inputs[0]); L.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85


rocks.data.materials.append(material("granite", rock_mat))
print("rock blocks", blocks)

# ---------------- sauna (sod-roof badstue) ----------------
sa_ = model["site"]["features"]["sauna"]
(scx, scy), (sw_, sh_) = sa_["center"], sa_["size"]
fl = sa_["floor"]
tar = material("tarred_timber", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.022, 0.018, 0.014, 1)), b.inputs["Roughness"].__setattr__("default_value", 0.75)))
sod = material("sod_roof", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.06, 0.09, 0.03, 1)), b.inputs["Roughness"].__setattr__("default_value", 1.0)))
deck_m = material("deck", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.12, 0.08, 0.05, 1)), b.inputs["Roughness"].__setattr__("default_value", 0.8)))
glass = material("glass", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.4, 0.3, 0.15, 1)), b.inputs["Emission Color"].__setattr__("default_value", (1.0, 0.55, 0.2, 1)), b.inputs["Emission Strength"].__setattr__("default_value", 3.0)))
eave, ridge = fl + 2.3, fl + 3.9
x0_, x1_, y0_, y1_ = scx - sw_ / 2, scx + sw_ / 2, scy - sh_ / 2, scy + sh_ / 2
walls = mesh_from("sauna_walls", [(x0_, y0_, fl - 0.4), (x1_, y0_, fl - 0.4), (x1_, y1_, fl - 0.4), (x0_, y1_, fl - 0.4),
                                  (x0_, y0_, eave), (x1_, y0_, eave), (x1_, y1_, eave), (x0_, y1_, eave), (scx, y0_, ridge), (scx, y1_, ridge)],
                  [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 8, 8), (7, 6, 9, 9)], smooth=False)
walls.data.materials.append(tar)
ov = 0.5
roof = mesh_from("sauna_sod_roof", [(x0_ - ov, y0_ - ov, eave - 0.25), (scx, y0_ - ov, ridge + 0.25), (scx, y1_ + ov, ridge + 0.25), (x0_ - ov, y1_ + ov, eave - 0.25),
                                    (x1_ + ov, y0_ - ov, eave - 0.25), (x1_ + ov, y1_ + ov, eave - 0.25)], [(0, 1, 2, 3), (1, 4, 5, 2)], smooth=False)
roof.modifiers.new("thick", "SOLIDIFY").thickness = 0.35
roof.data.materials.append(sod)
win = mesh_from("sauna_window", [(x1_ + 0.02, scy - 2.2, fl + 0.5), (x1_ + 0.02, scy + 2.2, fl + 0.5), (x1_ + 0.02, scy + 2.2, fl + 2.0), (x1_ + 0.02, scy - 2.2, fl + 2.0)], [(0, 1, 2, 3)], smooth=False)
win.data.materials.append(glass)
dx0, dy0, dx1, dy1 = sa_["deck"]["rect"]
dz_ = sa_["deck"]["z"]
deck = mesh_from("sauna_deck", [(dx0, dy0, dz_), (dx1, dy0, dz_), (dx1, dy1, dz_), (dx0, dy1, dz_)], [(0, 1, 2, 3)], smooth=False)
deck.modifiers.new("thick", "SOLIDIFY").thickness = 0.12
deck.data.materials.append(deck_m)
step = mesh_from("sauna_steps", [(x1_, scy - 0.8, fl), (dx0 + 1.6, scy - 0.8, dz_), (dx0 + 1.6, scy + 0.8, dz_), (x1_, scy + 0.8, fl)], [(0, 1, 2, 3)], smooth=False)
step.data.materials.append(deck_m)

# ---------------- east wing lower level: placeholder envelope, glazing, cars ----------------
env = model["site"]["envelope_placeholders"]["east_wing_E2"]
ex0, ey0, ex1, ey1 = env["rect"]
ez0, ez1 = env["floor"], env["top"]
concrete = material("concrete", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.42, 0.41, 0.39, 1)), b.inputs["Roughness"].__setattr__("default_value", 0.85)))
mullion = material("mullion", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.02, 0.02, 0.022, 1)), b.inputs["Roughness"].__setattr__("default_value", 0.4)))


def glass_mat(nt, b):
    b.inputs["Base Color"].default_value = (0.03, 0.045, 0.05, 1)
    b.inputs["Roughness"].default_value = 0.03
    b.inputs["Alpha"].default_value = 0.22


glass_e = material("glass_facade", glass_mat)
for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
    try:
        setattr(glass_e, attr, val)
        break
    except (AttributeError, TypeError):
        continue


def box(name, x0, y0, z0, x1, y1, z1, mat):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_from(name, v, f, smooth=False)
    ob.data.materials.append(mat)
    return ob


T = 0.35  # wall thickness
sides = {"W": ("y", ex0, ey0, ey1), "E": ("y", ex1, ey0, ey1), "S": ("x", ey0, ex0, ex1), "N": ("x", ey1, ex0, ex1)}
for side, (run, fixed, a0, a1) in sides.items():
    cuts = sorted([(g["from"], g["to"], "glass") for g in env["glazed"] if g["side"] == side] +
                  [(o["from"], o["to"], "open") for o in env["openings"] if o["side"] == side])
    spans, cur = [], a0
    for f0, f1, kind in cuts:
        if f0 > cur:
            spans.append((cur, f0, "wall"))
        spans.append((f0, f1, kind)); cur = f1
    if cur < a1:
        spans.append((cur, a1, "wall"))
    for k, (s0, s1, kind) in enumerate(spans):
        if kind == "open":
            continue
        if run == "y":
            bx = (fixed - T / 2, s0, fixed + T / 2, s1)
        else:
            bx = (s0, fixed - T / 2, s1, fixed + T / 2)
        if kind == "wall":
            box(f"e2_wall_{side}{k}", bx[0], bx[1], ez0 - 0.6, bx[2], bx[3], ez1 - 0.3, concrete)
        else:
            box(f"e2_glass_{side}{k}", bx[0] + 0.1 * (run == "y"), bx[1] + 0.1 * (run == "x"), ez0, bx[2] - 0.1 * (run == "y"), bx[3] - 0.1 * (run == "x"), ez1 - 0.35, glass_e)
            n = max(1, int((s1 - s0) / 2.4))
            for i in range(n + 1):  # slim vertical mullions every ~2.4 m
                t_ = s0 + (s1 - s0) * i / n
                if run == "y":
                    box(f"e2_mull_{side}{k}_{i}", fixed - 0.08, t_ - 0.04, ez0, fixed + 0.08, t_ + 0.04, ez1 - 0.35, mullion)
                else:
                    box(f"e2_mull_{side}{k}_{i}", t_ - 0.04, fixed - 0.08, ez0, t_ + 0.04, fixed + 0.08, ez1 - 0.35, mullion)
box("e2_floor", ex0, ey0, ez0 - 0.3, ex1, ey1, ez0, concrete)

car_paint = [material("car_silver", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.5, 0.52, 0.55, 1)), b.inputs["Metallic"].__setattr__("default_value", 0.9), b.inputs["Roughness"].__setattr__("default_value", 0.25))),
             material("car_green", lambda nt, b: (b.inputs["Base Color"].__setattr__("default_value", (0.02, 0.08, 0.05, 1)), b.inputs["Metallic"].__setattr__("default_value", 0.8), b.inputs["Roughness"].__setattr__("default_value", 0.3)))]
for k, cy_ in enumerate((3.2, 7.4)):
    box(f"car_{k}_body", 13.6, cy_ - 0.95, ez0 + 0.25, 18.4, cy_ + 0.95, ez0 + 0.85, car_paint[k])
    box(f"car_{k}_cabin", 14.9, cy_ - 0.8, ez0 + 0.85, 17.4, cy_ + 0.8, ez0 + 1.3, car_paint[k])

glow = bpy.data.objects.new("e2_ceiling_light", bpy.data.lights.new("e2_light", "AREA"))
glow.data.size = 16; glow.data.energy = 3500; glow.data.color = (1.0, 0.85, 0.7)
glow.location = ((ex0 + ex1) / 2, (ey0 + ey1) / 2, ez1 - 0.6)
scene.collection.objects.link(glow)

# ---------------- light, world, cameras ----------------
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4.0
sun.data.angle = math.radians(2)
sun.rotation_euler = (math.radians(55), 0, math.radians(-140))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("sky"); scene.world = world
world.use_nodes = True
try:
    sky = world.node_tree.nodes.new("ShaderNodeTexSky")
    for t in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "PREETHAM"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            continue
    sky.sun_elevation = math.radians(28)
    sky.sun_rotation = math.radians(220)
    world.node_tree.links.new(sky.outputs["Color"], world.node_tree.nodes["Background"].inputs["Color"])
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
except Exception as ex:  # older/newer API: plain sky colour
    print("sky fallback", ex)
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.65, 0.8, 1)

for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = eng
        break
    except TypeError:
        continue
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
try:
    scene.eevee.taa_render_samples = 32
except AttributeError:
    pass
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.7

cam_data = bpy.data.cameras.new("cam"); cam_data.clip_end = 12000
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
VIEWS = {
    "reference_upstream": ((4, -95, -3.5), (-2, 25, -2), 20),   # like Gym Design.jpg: in the gorge, looking at building + falls
    "aerial_se": ((160, -170, 95), (0, 0, -6), 30),
    "horizon_drone": ((-60, -420, 140), (0, 150, -10), 24),
    "east_rim": ((45, 10, 1.7), (-15, 20, -6), 18),
    "sauna_from_stream": ((-1, 120, 2.5), (-21, 95, 0.5), 22),
    "arrival_drone": ((170, 70, 60), (40, 8, -2), 26),
    "garden_drone": ((62, 100, 48), (24, 40, -5), 26),
}
for name, (loc, tgt, lens) in VIEWS.items():
    vc = bpy.data.objects.new(f"cam_{name}", cam_data.copy()); scene.collection.objects.link(vc)
    vc.location = loc
    vc.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    vc.data.lens = lens

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "site.blend"))
if RENDER:
    for name in VIEWS:
        scene.camera = bpy.data.objects[f"cam_{name}"]
        scene.render.filepath = str(OUT / f"{name}.png")
        bpy.ops.render.render(write_still=True)
print("done")

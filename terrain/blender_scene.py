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
detail = grid_mesh("terrain_detail", H[c, c], -D + 0.5, -D + 0.5, 1.0, {"rock": rock[c, c]})

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
    L.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
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
    if e["kind"] not in ("slab", "column", "wall", "beam", "panel", "block") or e["hidden"]:
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
ok = (slope < 32) & np.isnan(np.load(RV / "water_1m.npy")[c, c]) & ~clear & (rock[c, c] < 0.3)
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
ring = np.argwhere(np.ones((300, 300), bool)).astype(float) * 8 - 1200 + rng.random((90000, 2)) * 8
ring = ring[(np.abs(ring).max(1) > D)]
cz = ctx[((ring[:, 0] + 4000) / 4).astype(int), ((ring[:, 1] + 4000) / 4).astype(int)]
ring_v = np.stack([ring[:, 1], ring[:, 0], cz - 0.6], 1)
for k, proto in enumerate(protos):
    holder = mesh_from(f"forest_far_{proto.name}", ring_v[k::3], np.zeros((0, 4), int))
    inst = proto.copy(); inst.data = proto.data
    scene.collection.objects.link(inst)
    inst.parent = holder; inst.location = (0, 0, 0)
    holder.instance_type = "VERTS"
print("trees", len(pick), "far", len(ring_v))

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

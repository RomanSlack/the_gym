"""The bonsai as a social post (Roman: "need more interesting background ... for an X post ... what you'd see on actual bonsai
influencer posts"): the dome-style juniper on a weathered plank stand in a Chinese garden (Poly Haven chinese_garden, CC0),
shot like a photo: a 70 mm lens at f/2, focused on the trunk, the pond + pavilion soft behind; portrait 4:5. One shot per process.

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_bonsai_post.py -- OUT.png [--seed 3] [--samples 384] [--yaw 0] [--style dome]
"""
import math
import os
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
OUT = a[0]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES, YAW = opt("--seed", 3), opt("--samples", 512), opt("--yaw", 0.0)
os.environ["BONSAI_STYLE"] = opt("--style", "dome")
import gen_bonsai  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = 1600, 2000
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = -0.3
sc.render.film_transparent = False

objs = gen_bonsai.build(SEED, (0, 0, 0))
names = {o.name for o in objs if o.name.startswith("Cube")}
for o in list(sc.objects):                                           # the studio table out: a weathered plank stand instead
    if o.name in names:
        bpy.data.objects.remove(o)
objs = [o for o in sc.objects if o.type == "MESH"]
T = gen_bonsai.TABLE


def deadwood_mat(name, scale=2.5, tint=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.8
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(gen_bonsai.MAPS / "deadwood.jpg"), check_existing=True)
    t.projection = "BOX"; t.projection_blend = 0.2; L.new(mp.outputs[0], t.inputs["Vector"])
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Value"].default_value = tint
    L.new(t.outputs[0], hs.inputs["Color"]); L.new(hs.outputs[0], b.inputs["Base Color"])
    g = N.new("ShaderNodeRGBToBW"); L.new(t.outputs[0], g.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.003
    L.new(g.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


plank = deadwood_mat("plank", 2.0, 0.5)
for (sx, sy, sz, z) in ((0.74, 0.52, 0.06, T - 0.03), (0.16, 0.16, T - 0.06, (T - 0.06) / 2)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
    o = bpy.context.object; o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bv = o.modifiers.new("bv", "BEVEL"); bv.width = 0.006; bv.segments = 3
    o.data.materials.append(plank)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
catcher = bpy.context.object; catcher.is_shadow_catcher = True

# the garden: the pond, lantern and pavilion behind the tree (u ~0.58 of the panorama), the sun behind it: a rim light
w = bpy.data.worlds.new("garden"); sc.world = w; w.use_nodes = True
N, L = w.node_tree.nodes, w.node_tree.links
tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping")
mp.inputs["Rotation"].default_value = (0, 0, math.radians(-118.8 + YAW))
env = N.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(str(Path.home() / ".cache/the_gym/hdris/polyhaven/chinese_garden_4k.hdr"))
L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs[0], env.inputs["Vector"])
L.new(env.outputs["Color"], N["Background"].inputs["Color"]); N["Background"].inputs["Strength"].default_value = 0.9
# a soft key from the front left (a bounce card's worth), so the tree isn't a silhouette against the sun
ld = bpy.data.lights.new("key", "AREA"); ld.size = 1.4; ld.energy = 140; ld.color = (1.0, 0.96, 0.9)
k = bpy.data.objects.new("key", ld); sc.collection.objects.link(k); k.location = (-1.3, -1.6, 1.6)
k.rotation_euler = (mathutils.Vector((0, 0, T + 0.25)) - k.location).to_track_quat("-Z", "Y").to_euler()

# the camera: frame the tree + pot, focus on the trunk
tree = [o for o in objs if o.get("tree")]
pts = [o.matrix_world @ mathutils.Vector(c) for o in tree for c in o.bound_box]
lo = mathutils.Vector([min(p[i] for p in pts) for i in range(3)]); hi = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
c = (lo + hi) / 2 + mathutils.Vector((0, 0, -0.06))
lens = 70
d = mathutils.Vector((0.12, -1.0, 0.035)).normalized()      # (near level: the garden behind, not the pond edge)
half_w = math.atan(18 * 0.8 / lens)
dist = max(hi.x - lo.x, hi.y - lo.y) * 0.56 / math.tan(half_w)
cd = bpy.data.cameras.new("cam"); cd.lens = lens
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam)
cam.location = c + d * dist
cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
wood = [o for o in objs if o.name.endswith("_wood")][0]
focus = bpy.data.objects.new("focus", None); sc.collection.objects.link(focus)
focus.location = wood.matrix_world @ mathutils.Vector(wood.bound_box[0]).lerp(mathutils.Vector(wood.bound_box[6]), 0.5)
cd.dof.use_dof = True;  # (light: the stand's front edge just soft)
cd.dof.aperture_fstop = 5.6; cd.dof.focus_object = focus; pass
# two passes, composited outside (a lens blur of the panorama through the denoiser banded into contours): the stand + tree
# on a transparent film, then the garden alone, sharp and noise-free; tools: plants/post_composite.py
sc.render.image_settings.color_depth = "16"
sc.render.film_transparent = True
sc.render.filepath = OUT.replace(".png", "_fg.png")
bpy.ops.render.render(write_still=True)
for o in list(sc.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o)
sc.render.film_transparent = False
sc.cycles.samples = 16; sc.cycles.use_denoising = False; cd.dof.use_dof = False
sc.render.image_settings.color_mode = "RGB"
sc.render.filepath = OUT.replace(".png", "_bg.png")
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

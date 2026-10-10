"""Render a heightfield (.npy, row 0 = south, metres) as a quick 3D preview in Blender.

blender -b --factory-startup --python terrain/blender_preview.py -- <in.npy> <res_m> <out_prefix> [cams.json]
Writes <out_prefix>_oblique.png (low view along the site) and <out_prefix>_aerial.png.
cams.json (optional): [{"name", "loc": [x,y,z], "target": [x,y,z], "lens"}] in metres from the
grid centre with absolute heights; replaces the default views.
"""
import sys, math, json
import numpy as np
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
npy, res, out = args[:3]
cams = json.load(open(args[3])) if len(args) > 3 else None
res = float(res)
H = np.load(npy).astype(np.float32)
H = np.where(np.isnan(H), np.nanmin(H), H)
if cams is None:  # default views are relative to the centre height
    H -= np.median(H[H.shape[0] // 2 - 20:H.shape[0] // 2 + 20, H.shape[1] // 2 - 20:H.shape[1] // 2 + 20])
ny, nx = H.shape
w, h = (nx - 1) * res, (ny - 1) * res

bpy.ops.wm.read_factory_settings(use_empty=True)
mesh = bpy.data.meshes.new("terrain")
xs = np.linspace(-w / 2, w / 2, nx, dtype=np.float32)
ys = np.linspace(-h / 2, h / 2, ny, dtype=np.float32)
X, Y = np.meshgrid(xs, ys)
verts = np.stack([X, Y, H], -1).reshape(-1, 3)
i = np.arange(nx * ny).reshape(ny, nx)
quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1).reshape(-1, 4)
mesh.vertices.add(len(verts))
mesh.vertices.foreach_set("co", verts.ravel())
mesh.loops.add(quads.size)
mesh.loops.foreach_set("vertex_index", quads.ravel())
mesh.polygons.add(len(quads))
mesh.polygons.foreach_set("loop_start", np.arange(0, quads.size, 4))
mesh.polygons.foreach_set("loop_total", np.full(len(quads), 4))
mesh.update()
mesh.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
obj = bpy.data.objects.new("terrain", mesh)
scene = bpy.context.scene
scene.collection.objects.link(obj)

scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "SINGLE"
sh.single_color = (0.55, 0.6, 0.5)
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_shadows = True
scene.display.shadow_focus = 0.9
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.75, 0.8, 0.85)

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 20000


def look(loc, target, lens):
    from mathutils import Vector
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = lens


if cams is None:
    cams = [{"name": "oblique", "loc": (w * 0.05, -h * 0.42, 60), "target": (0, 0, -5), "lens": 28},
            {"name": "aerial", "loc": (w * 0.3, -h * 0.75, h * 0.55), "target": (0, 0, 0), "lens": 35}]
for c in cams:
    look(c["loc"], c["target"], c["lens"])
    scene.render.filepath = f"{out}_{c['name']}.png"
    bpy.ops.render.render(write_still=True)

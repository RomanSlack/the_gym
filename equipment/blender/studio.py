"""Render one equipment piece in the studio and keep the pass: its views + its geometry, never overwritten.

Run through the runner (it picks the version number and composes the comparison sheet):
    python3 equipment/tools/model.py <piece> [draft]
Directly: nice -n 19 blender -b --factory-startup -t 12 --python equipment/blender/studio.py -- <piece> <version> [draft]
Joints only (build + the floating-part check, nothing rendered or saved):
    blender -b --factory-startup --python equipment/blender/studio.py -- <piece> 0 check

Builds equipment/pieces/<piece>/model.py (def build(k)), exports pieces/<piece>/models/<piece>_vNNN.glb, then renders
the studio views to pieces/<piece>/models/<piece>_<view>_vNNN.jpg. A model.py may define VIEWS (extra or replaced
views: name -> (azimuth deg, 0 = from the front, +90 = from the user's right; elevation deg; zoom)) and
DETAILS (name -> (eye, target, lens mm)). Cycles on the GPU or not at all.
"""
import importlib.util
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

EQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EQ / "blender"))
sys.path.insert(0, str(EQ / "tools"))
import kit  # noqa: E402
import versions  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
PIECE, V = args[0], int(args[1])
DRAFT = "draft" in args
CHECK = "check" in args


def gpu_or_stop():
    """Same rule as the building's renders (construction/bl_common.py): GPU or quit with code 3, never the CPU."""
    pr = bpy.context.preferences.addons["cycles"].preferences
    for dev in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = dev; pr.get_devices()
        except Exception:
            continue
        if [d for d in pr.devices if d.type == dev]:
            for d in pr.devices:
                d.use = d.type == dev
            return
    print("\n!! NO GPU: Cycles cannot reach the NVIDIA GPU, stopping instead of rendering on the CPU.\n"
          "!! Usual cause: a driver update without a reboot (`nvidia-smi` says Driver/library version mismatch). Reboot, then rerun.\n", flush=True)
    os._exit(3)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "GPU"; scene.cycles.tile_size = 256
if not CHECK:
    gpu_or_stop()
scene.cycles.samples = 48 if DRAFT else 160; scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = (1200, 900)
scene.render.resolution_percentage = 70 if DRAFT else 100
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "JPEG"; scene.render.image_settings.quality = 92

# ---- the piece
spec = importlib.util.spec_from_file_location("piece_model", EQ / "pieces" / PIECE / "model.py")
pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
RES = getattr(pm, "RES", (1200, 900))   # a piece may ask for its own frame (a 16:9 hero for a post)
scene.render.resolution_x, scene.render.resolution_y = RES
coll = bpy.data.collections.new(PIECE); scene.collection.children.link(coll)
k = kit.Kit(PIECE, coll, getattr(pm, "LOOK", None))
pm.build(k)
obs = k.finish()
bpy.context.view_layer.update()
if CHECK:
    os._exit(4 if k.floating else 0)

glb = versions.model_path(PIECE, V)
for o in bpy.data.objects:
    o.select_set(o.name in coll.all_objects)
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True, export_apply=True)
print("geometry:", glb)

lo = Vector((min(c[i] for o in obs for c in (o.matrix_world @ Vector(b) for b in o.bound_box)) for i in range(3)))
hi = Vector((max(c[i] for o in obs for c in (o.matrix_world @ Vector(b) for b in o.bound_box)) for i in range(3)))
centre, size = (lo + hi) / 2, hi - lo
sc = max(1.0, size.length / 6.0)    # a big assembly (a maze of modules): the backdrop and lights grow with it
print(f"bounding box: {size.x:.3f} x {size.y:.3f} x {size.z:.3f} m (w x d x h)")

# ---- the studio: a seamless mid-grey sweep, big soft lights
w = bpy.data.worlds.new("studio"); scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.6, 0.62, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12
floor = bpy.data.materials.new("sweep"); floor.use_nodes = True
fb = floor.node_tree.nodes["Principled BSDF"]; fb.inputs["Base Color"].default_value = (0.32, 0.32, 0.33, 1); fb.inputs["Roughness"].default_value = 0.6
import bmesh  # noqa: E402
bm = bmesh.new()
R, back = 2.0 * sc, 6.0 * sc  # floor runs to a curved wall behind the piece (cyclorama)
prof = [(-12.0 * sc, 0.0)] + [(back - R + R * math.sin(a * math.pi / 2 / 12), R - R * math.cos(a * math.pi / 2 / 12)) for a in range(13)] + [(back, 8.0 * sc)]
rows = []
for x in (-14 * sc, 14 * sc):
    rows.append([bm.verts.new((x, y, z)) for y, z in prof])
for i in range(len(prof) - 1):
    bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
me = bpy.data.meshes.new("sweep"); bm.to_mesh(me); bm.free()
sw = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sw); me.materials.append(floor)
for p in me.polygons:
    p.use_smooth = True


def area(name, loc, energy, size, target):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
    L.data.energy = energy; L.data.size = size; L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(L)


c = centre
area("key", c + Vector((-2.6, -3.0, 2.8)) * sc, 420 * sc * sc, 2.5 * sc, c)
area("fill", c + Vector((3.2, -2.2, 1.4)) * sc, 110 * sc * sc, 3.0 * sc, c)
area("rim", c + Vector((1.5, 3.2, 3.0)) * sc, 320 * sc * sc, 2.0 * sc, c)
area("top", c + Vector((0, 0, 3.5)) * sc, 110 * sc * sc, 3.0 * sc, c)

# ---- views
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 50; cam.data.sensor_width = 36
VIEWS = {"three_quarter": (-38, 14, 1.0), "front": (0, 6, 1.0), "side": (90, 6, 1.0), "back_three_quarter": (150, 18, 1.0)}
VIEWS.update(getattr(pm, "VIEWS", {}))
rad = 0.5 * size.length
fov = 2 * math.atan(18 / cam.data.lens) * (RES[1] / RES[0])  # the narrower (vertical) angle
for name, (az, el, zoom) in VIEWS.items():
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    dist = rad / math.sin(fov / 2) * 1.02 / zoom
    cam.location = c + d * dist
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sw.location = (c.x, c.y, 0); sw.rotation_euler = (0, 0, a)  # the sweep's curved wall always behind the piece
    sw.data.transform(__import__("mathutils").Matrix.Translation((-c.x, -c.y, 0))) if not sw.get("centred") else None
    sw["centred"] = True
    scene.render.filepath = str(versions.path(PIECE, name, V))
    bpy.ops.render.render(write_still=True)
    print("view:", scene.render.filepath, flush=True)
# orthographic views (to set beside orthographic reference drawings): name -> azimuth (0 = from the front, +90 = from the
# user's left) or "top"; one metre is the same number of pixels in all of them
for name, az in getattr(pm, "ORTHO", {}).items():
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 2.0
    sw.location = (c.x, c.y, 0)
    if az == "top":
        cam.location = Vector((c.x, c.y, 6.0)); cam.rotation_euler = (0, 0, 0)
        sw.hide_render = True
    else:
        a = math.radians(az)
        d = Vector((math.sin(a), -math.cos(a), 0))
        cam.location = Vector((c.x, c.y, 0.80)) + d * 6.0
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sw.rotation_euler = (0, 0, a); sw.hide_render = False
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.filepath = str(versions.path(PIECE, name, V))
    bpy.ops.render.render(write_still=True)
    print("view:", scene.render.filepath, flush=True)
    # the same view cut out (transparent, no sweep) for the overlay on the generated drawing (tools/model.py)
    hid, sw.hide_render = sw.hide_render, True
    scene.render.film_transparent = True; scene.cycles.samples = 16
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGBA"
    (EQ / ".cache").mkdir(exist_ok=True)
    scene.render.filepath = str(EQ / ".cache" / f"ortho_{PIECE}_{name}.png")
    bpy.ops.render.render(write_still=True)
    scene.render.film_transparent = False; scene.cycles.samples = 48 if DRAFT else 160; sw.hide_render = hid
    scene.render.image_settings.file_format = "JPEG"; scene.render.image_settings.color_mode = "RGB"
cam.data.type = "PERSP"; sw.hide_render = False
scene.render.resolution_x, scene.render.resolution_y = RES
for name, (eye, target, lens) in getattr(pm, "DETAILS", {}).items():
    cam.location = Vector(eye); cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    scene.render.filepath = str(versions.path(PIECE, name, V))
    bpy.ops.render.render(write_still=True)
    print("view:", scene.render.filepath, flush=True)
    cam.data.lens = 50

# ---- the fit check: stand-in users (blender/body.py) posed in the machine by the piece's fit() -> {label: figure
# kwargs}, each rendered on its own as fit_<label>_<view> (FIT_VIEWS, default the side and the three-quarter); never in
# the piece, its .glb or its joint check
if hasattr(pm, "fit"):
    import body  # noqa: E402
    for label, kw in pm.fit().items():
        fc = bpy.data.collections.new(f"fit_{label}"); scene.collection.children.link(fc)
        fk = kit.Kit(f"fit_{label}", fc, body.LOOK); fk.is_sub = True
        pts = body.figure(fk, **kw)
        print(f"fit {label}: " + ", ".join(f"{n} ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})" for n, p in pts.items()), flush=True)
        fobs = fk.finish()
        for name in getattr(pm, "FIT_VIEWS", ("side", "three_quarter")):
            az, el, zoom = VIEWS[name]
            a, e = math.radians(az), math.radians(el)
            d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
            cam.location = c + d * (rad / math.sin(fov / 2) * 1.02 / zoom)
            cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
            sw.rotation_euler = (0, 0, a)
            scene.render.filepath = str(versions.path(PIECE, f"fit_{label}_{name}", V))
            bpy.ops.render.render(write_still=True)
            print("view:", scene.render.filepath, flush=True)
        for o in fobs:
            bpy.data.objects.remove(o)

# ---- the reference cameras (equipment/tools/camsolve.py): our model seen exactly as each photo, for the overlays
mfile = EQ / "pieces" / PIECE / "match.json"
if mfile.exists():
    import json
    from mathutils import Matrix
    MJ = json.loads(mfile.read_text())
    for vi, vw in enumerate(MJ.get("views") or [MJ]):
        mc = vw.get("camera")
        if not mc:
            continue
        R = Matrix(mc["rotation"]).to_4x4(); R.translation = Vector(mc["location"])
        cam.matrix_world = R
        cam.data.lens, cam.data.sensor_width, cam.data.sensor_fit = mc["lens"], mc["sensor"], "AUTO"
        cam.data.shift_x, cam.data.shift_y = mc["shift_x"], mc["shift_y"]
        scene.render.resolution_x, scene.render.resolution_y = mc["size"]
        scene.render.resolution_percentage = 100 if MJ.get("details") else 50   # full size when close-ups are cut from it
        scene.render.film_transparent = True
        sw.hide_render = True
        scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGBA"
        (EQ / ".cache").mkdir(exist_ok=True)
        scene.render.filepath = str(EQ / ".cache" / f"match_{PIECE}_{vi}.png")
        bpy.ops.render.render(write_still=True)
        print("match:", scene.render.filepath, flush=True)

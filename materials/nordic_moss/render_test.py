"""Test renders of the nordic moss set (maps/): one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python materials/nordic_moss/render_test.py -- SHOT OUT.png [--scale 0.06] [--samples 256]

SHOT: wall (a 2 x 2 m panel of it, seen from 2.4 m, soft interior light), close (the same panel from 0.7 m, raking light),
boulder (a rounded granite boulder ~1.4 m wide, box-projected), compare (ours beside the plain CC0 scans).
"""
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "construction"))
import bl_common as bc  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
SCALE, SAMPLES = opt("--scale", 0.06), int(opt("--samples", 256))
MAPS = HERE / "maps"
SCAN = Path.home() / ".cache" / "the_gym" / "textures"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
bc.gpu_or_stop()
sc.cycles.device = "GPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.tile_size = 256
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Base Contrast"
try:
    sc.cycles.feature_set = "EXPERIMENTAL"
except Exception:
    pass


def img(path, color=False):
    im = bpy.data.images.load(str(path), check_existing=True)
    if not color:
        im.colorspace_settings.name = "Non-Color"
    return im


def moss_material(name="nordic_moss", d=MAPS, box=False, scale=SCALE, files=None):
    """The method's shader: albedo x weak AO; dry matte rock (rough 0.62-0.92 from the map, specular 0.2) and soft fully matte
    moss (sheen, a little subsurface) mixed by the sharp mask; displacement from the height (+ the soft mask: moss stands up)."""
    f = files or {"albedo": "albedo.png", "height": "height.png", "normal": "normal.png", "rough": "roughness.png",
                  "ao": "ao.png", "mask": "mask_shade.png", "mask_h": "mask_height.png"}
    m = bpy.data.materials.new(name); m.use_nodes = True
    for attr in ("displacement_method",):
        try:
            setattr(m, attr, "BOTH")
        except Exception:
            m.cycles.displacement_method = "BOTH"
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")

    def tex(key, color=False):
        t = N.new("ShaderNodeTexImage"); t.image = img(d / f[key], color)
        if box:
            t.projection = "BOX"; t.projection_blend = 0.35
            L.new(tc.outputs["Object"], t.inputs["Vector"])
        else:
            L.new(tc.outputs["UV"], t.inputs["Vector"])
        return t

    dif, ao, rgh, nrm, hgt = tex("albedo", True), tex("ao"), tex("rough"), tex("normal"), tex("height")
    col = N.new("ShaderNodeMix"); col.data_type = "RGBA"; col.blend_type = "MULTIPLY"; col.inputs[0].default_value = 0.55
    L.new(dif.outputs[0], col.inputs[6]); L.new(ao.outputs[0], col.inputs[7])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.2
    L.new(nrm.outputs[0], nm.inputs["Color"])
    rock = N.new("ShaderNodeBsdfPrincipled")
    L.new(col.outputs[2], rock.inputs["Base Color"]); L.new(rgh.outputs[0], rock.inputs["Roughness"])
    rock.inputs["Specular IOR Level"].default_value = 0.2
    L.new(nm.outputs[0], rock.inputs["Normal"])
    mo = N.new("ShaderNodeBsdfPrincipled")
    L.new(col.outputs[2], mo.inputs["Base Color"])
    mo.inputs["Roughness"].default_value = 1.0
    mo.inputs["Specular IOR Level"].default_value = 0.1
    mo.inputs["Sheen Weight"].default_value = 0.25
    mo.inputs["Sheen Tint"].default_value = (0.35, 0.5, 0.15, 1)
    mo.inputs["Subsurface Weight"].default_value = 0.15
    L.new(nm.outputs[0], mo.inputs["Normal"])
    mix = N.new("ShaderNodeMixShader")
    if "mask" in f:
        ms = tex("mask"); L.new(ms.outputs[0], mix.inputs[0])
    else:
        mix.inputs[0].default_value = 0.0
    L.new(rock.outputs[0], mix.inputs[1]); L.new(mo.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    dp = N.new("ShaderNodeDisplacement"); dp.inputs["Midlevel"].default_value = 0.15; dp.inputs["Scale"].default_value = scale
    L.new(hgt.outputs[0], dp.inputs["Height"]); L.new(dp.outputs[0], out.inputs["Displacement"])
    return m


def panel(name, size, mat, loc=(0, 0, 0), rot=(math.radians(90), 0, 0), cuts=1024):
    """a vertical size x size panel (UV 0-1 over it), dense enough for the displacement (~2 mm)"""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=cuts, y_subdivisions=cuts, size=size, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.data.materials.append(mat)
    return o


def look(loc, tgt, lens):
    c = bc.camera(sc, "cam", loc, tgt, lens)
    sc.camera = c
    return c


def lights(key_loc, key_size=2.5, key_e=900, fill=0.2):
    """an interior-like setup: one big soft area key (a window / skylight), a weak sky fill"""
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.78, 0.82, 0.86, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = fill
    ld = bpy.data.lights.new("key", "AREA"); ld.size = key_size; ld.energy = key_e; ld.color = (1.0, 0.97, 0.92)
    k = bpy.data.objects.new("key", ld); sc.collection.objects.link(k); k.location = key_loc
    d = -k.location
    k.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


import mathutils  # noqa: E402

if SHOT in ("wall", "close"):
    m = moss_material()
    panel("panel", 2.0, m, loc=(0, 0, 1.0))
    # a pale floor + side walls so the light reads like a room
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -2, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.55, 0.53, 0.5), 0.8))
    if SHOT == "wall":
        lights(mathutils.Vector((-1.8, -2.2, 3.0)), 2.5, 260)
        look((0.0, -3.0, 1.1), (0.0, 0.0, 1.0), 35)
    else:
        lights(mathutils.Vector((-2.4, -0.9, 1.6)), 1.2, 170)        # raking from the left: the relief shows
        look((0.25, -0.75, 1.15), (0.05, 0.0, 0.95), 50)
elif SHOT == "boulder":
    m = moss_material(box=True, scale=SCALE * 0.8)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=7, radius=0.7, location=(0, 0, 0.35))
    o = bpy.context.object; o.scale = (1.0, 0.8, 0.62)
    tx = bpy.data.textures.new("lump", "VORONOI"); tx.noise_scale = 0.55
    dm = o.modifiers.new("lump", "DISPLACE"); dm.texture = tx; dm.strength = 0.12; dm.texture_coords = "GLOBAL"
    o.modifiers.new("sub", "SUBSURF").levels = 1
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.5, 0.48, 0.45), 0.85))
    lights(mathutils.Vector((-2.2, -2.0, 2.8)), 2.0, 260)
    look((0.4, -2.3, 1.2), (0.0, 0.0, 0.42), 45)
elif SHOT == "compare":
    ours = moss_material()
    scan = moss_material("scan", SCAN / "ambientcg" / "Rock046S", files={"albedo": "diff.png", "height": "disp.png", "normal": "nor_gl.png",
                                                                       "rough": "rough.png", "ao": "ao.png"}, scale=SCALE * 0.4)
    panel("ours", 1.6, ours, loc=(-0.9, 0, 0.9), cuts=800)
    panel("scan", 1.6, scan, loc=(0.9, 0, 0.9), cuts=800)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -2, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.55, 0.53, 0.5), 0.8))
    lights(mathutils.Vector((-1.5, -2.4, 3.0)), 3.0, 340)
    look((0.0, -3.2, 1.0), (0.0, 0.0, 0.9), 40)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

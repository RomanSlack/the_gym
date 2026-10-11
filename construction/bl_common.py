"""Shared Blender helpers for the construction scenes (meshes, materials, terrain, water, rock, world)."""
import math
import numpy as np
import bpy
import bmesh
from mathutils import Vector


def mesh_from(name, verts, faces, attrs=None, smooth=True, coll=None):
    me = bpy.data.meshes.new(name)
    verts = np.asarray(verts, np.float32).reshape(-1, 3)
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    faces = np.asarray(faces, np.int64)
    if faces.size:
        me.loops.add(faces.size); me.loops.foreach_set("vertex_index", faces.ravel())
        me.polygons.add(len(faces))
        me.polygons.foreach_set("loop_start", np.arange(0, faces.size, faces.shape[1]))
        me.polygons.foreach_set("loop_total", np.full(len(faces), faces.shape[1]))
    me.update()
    if faces.size:  # Blender 4.1+: faces are smooth unless explicitly marked flat
        me.polygons.foreach_set("use_smooth", np.full(len(faces), bool(smooth)))
    for k, v in (attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", "POINT"); a.data.foreach_set("value", np.asarray(v, np.float32).ravel())
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def grid_mesh(name, H, x0, y0, res, attrs=None, coll=None):
    ny, nx = H.shape
    X, Y = np.meshgrid(x0 + np.arange(nx, dtype=np.float32) * res, y0 + np.arange(ny, dtype=np.float32) * res)
    i = np.arange(nx * ny).reshape(ny, nx)
    quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1).reshape(-1, 4)
    return mesh_from(name, np.stack([X, Y, H.astype(np.float32)], -1), quads, attrs, coll=coll)


def material(name, rgb, rough=0.8, metal=0.0, alpha=None, emit=None):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val); break
            except (AttributeError, TypeError):
                continue
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1); b.inputs["Emission Strength"].default_value = emit[1]
    return m


def box(name, x0, y0, z0, x1, y1, z1, mat, coll=None):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    ob = mesh_from(name, v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], smooth=False, coll=coll)
    ob.data.materials.append(mat)
    return ob


def oriented_box(name, a, b, width, z0, z1, mat, coll=None):
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0); nx, ny = -(y1 - y0) / L * width / 2, (x1 - x0) / L * width / 2
    v = [(x0 + nx, y0 + ny, z0), (x1 + nx, y1 + ny, z0), (x1 - nx, y1 - ny, z0), (x0 - nx, y0 - ny, z0)]
    if (v[1][0] - v[0][0]) * (v[3][1] - v[0][1]) - (v[1][1] - v[0][1]) * (v[3][0] - v[0][0]) < 0:
        v = [v[0], v[3], v[2], v[1]]
    v += [(x, y, z1) for x, y, _ in v]
    ob = mesh_from(name, v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], smooth=False, coll=coll)
    ob.data.materials.append(mat)
    return ob


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in (parent or bpy.context.scene.collection).children:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def terrain_material():
    """Forest floor / soil, rock where steep or flagged ('rock' attribute), raw excavated rock where 'cut' > 0."""
    m = bpy.data.materials.new("terrain"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = N["Principled BSDF"]
    rock = N.new("ShaderNodeAttribute"); rock.attribute_name = "rock"
    cut = N.new("ShaderNodeAttribute"); cut.attribute_name = "cut"
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    sl = N.new("ShaderNodeMapRange"); sl.inputs[1].default_value = 0.9; sl.inputs[2].default_value = 0.7; L.new(sep.outputs["Z"], sl.inputs[0])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; L.new(rock.outputs["Fac"], mx.inputs[0]); L.new(sl.outputs[0], mx.inputs[1])
    noise = N.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.08
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.05, 0.02, 1); ramp.color_ramp.elements[1].color = (0.075, 0.065, 0.035, 1)
    L.new(noise.outputs["Fac"], ramp.inputs[0])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = (0.085, 0.085, 0.08, 1)
    L.new(mx.outputs[0], mix.inputs["Factor"]); L.new(ramp.outputs["Color"], mix.inputs["A"])
    mix2 = N.new("ShaderNodeMix"); mix2.data_type = "RGBA"; mix2.inputs["B"].default_value = (0.20, 0.19, 0.17, 1)  # fresh-cut granite / gravel
    L.new(cut.outputs["Fac"], mix2.inputs["Factor"]); L.new(mix.outputs["Result"], mix2.inputs["A"])
    L.new(mix2.outputs["Result"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.95
    return m


def water_mesh(name, W, x0, y0, res, coll=None):
    wet = ~np.isnan(W); ny, nx = W.shape
    i = np.arange(nx * ny).reshape(ny, nx)
    q = wet[:-1, :-1] & wet[:-1, 1:] & wet[1:, 1:] & wet[1:, :-1]
    quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1)[q]
    X, Y = np.meshgrid(x0 + np.arange(nx) * res, y0 + np.arange(ny) * res)
    used = np.unique(quads); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used))
    v = np.stack([X.ravel()[used], Y.ravel()[used], np.nan_to_num(W, nan=-50).ravel()[used] + 0.02], 1)
    ob = mesh_from(name, v, remap[quads], coll=coll)
    ob.data.materials.append(material("water", (0.02, 0.05, 0.05), rough=0.04))
    return ob


def rock_variants(n=6):
    out = []
    for k in range(n):
        r = np.random.default_rng(k)
        v = np.array([(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)], float)
        v = v[np.abs(v).sum(1) > 0] * (1 + r.normal(0, 0.18, (26, 1))); v[:, 2] *= r.uniform(0.45, 0.75)
        bm = bmesh.new()
        for p in v:
            bm.verts.new(p)
        bmesh.ops.convex_hull(bm, input=bm.verts); bm.verts.ensure_lookup_table(); bm.verts.index_update()
        out.append(bm)
    return out


def cliff_rocks(H, rock, x0, y0, exclude, rng, coll=None):
    """Faceted granite blocks stacked up steep, rock-flagged cliff faces (H at 1 m, origin x0,y0)."""
    variants = rock_variants()
    gy, gx = np.gradient(H)
    steep = (np.degrees(np.arctan(np.hypot(gx, gy))) > 48) & (rock > 0.25) & ~exclude
    cells = np.argwhere(steep); cells = cells[rng.random(len(cells)) < 0.45]
    nbmax = np.maximum.reduce([np.roll(np.roll(H, a, 0), b, 1) for a in (-1, 0, 1) for b in (-1, 0, 1)])
    nbmin = np.minimum.reduce([np.roll(np.roll(H, a, 0), b, 1) for a in (-1, 0, 1) for b in (-1, 0, 1)])
    bm = bmesh.new()
    for (j, i) in cells:
        o = (-gx[j, i], -gy[j, i]); ol = math.hypot(*o) + 1e-6; o = (o[0] / ol, o[1] / ol)
        for zc in np.arange(nbmin[j, i] + 0.8, nbmax[j, i] + 0.4, rng.uniform(1.6, 2.6)):
            src = variants[rng.integers(6)]; sc = rng.uniform(1.0, 2.2)
            ang = math.atan2(o[1], o[0]) + rng.normal(0, 0.3); ca, sa = math.cos(ang), math.sin(ang)
            px = i + x0 + 0.5 - o[0] * 0.6 * sc + rng.normal(0, 0.3); py = j + y0 + 0.5 - o[1] * 0.6 * sc + rng.normal(0, 0.3)
            nv = [bm.verts.new((px + ca * v.co.x * sc * 1.3 - sa * v.co.y * sc, py + sa * v.co.x * sc * 1.3 + ca * v.co.y * sc, zc + v.co.z * sc)) for v in src.verts]
            for f in src.faces:
                bm.faces.new([nv[v.index] for v in f.verts])
    me = bpy.data.meshes.new("cliff_rocks"); bm.to_mesh(me)
    me.polygons.foreach_set("use_smooth", np.zeros(len(me.polygons), bool))
    ob = bpy.data.objects.new("cliff_rocks", me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.data.materials.append(material("granite", (0.09, 0.09, 0.085), rough=0.85))
    return ob


def world_and_render(scene):
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 4.0; sun.data.angle = math.radians(2); sun.rotation_euler = (math.radians(55), 0, math.radians(-140))
    scene.collection.objects.link(sun)
    w = bpy.data.worlds.new("sky"); scene.world = w; w.use_nodes = True
    try:
        sky = w.node_tree.nodes.new("ShaderNodeTexSky")
        for t in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "PREETHAM"):
            try:
                sky.sky_type = t; break
            except TypeError:
                continue
        sky.sun_elevation = math.radians(28); sky.sun_rotation = math.radians(220)
        w.node_tree.links.new(sky.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
        w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    except Exception:
        w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.65, 0.8, 1)
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = eng; break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.view_settings.view_transform = "AgX"; scene.view_settings.exposure = -0.7


def camera(scene, name, loc, tgt, lens):
    cd = bpy.data.cameras.new(name); cd.clip_end = 12000
    if isinstance(lens, tuple):
        cd.type = "ORTHO"; cd.ortho_scale = lens[1]
    else:
        cd.lens = lens
    c = bpy.data.objects.new(name, cd); scene.collection.objects.link(c)
    c.location = loc; c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return c

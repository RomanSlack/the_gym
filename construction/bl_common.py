"""Shared Blender helpers for the construction scenes (meshes, materials, terrain, water, rock, world)."""
import math
import numpy as np
import bpy
import bmesh
from mathutils import Matrix, Vector


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


def grid_mesh(name, H, x0, y0, res, attrs=None, coll=None, keep=None):
    """Heightfield mesh; `keep` (shape (ny-1, nx-1)) drops the quads where it is False."""
    ny, nx = H.shape
    X, Y = np.meshgrid(x0 + np.arange(nx, dtype=np.float32) * res, y0 + np.arange(ny, dtype=np.float32) * res)
    i = np.arange(nx * ny).reshape(ny, nx)
    quads = np.stack([i[:-1, :-1], i[:-1, 1:], i[1:, 1:], i[1:, :-1]], -1)
    quads = (quads[keep] if keep is not None else quads).reshape(-1, 4)
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
    ob.data.materials.append(water_material())
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
    ob.data.materials.append(rock_material())
    # jointed granite: keep the crisp block edges, roughen the faces (simple subdivision + small displacement, flat shading)
    sub = ob.modifiers.new("weather", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = 1; sub.render_levels = 2
    dtx = bpy.data.textures.get("rock_weather") or bpy.data.textures.new("rock_weather", "CLOUDS")
    dtx.noise_scale = 0.35; dtx.noise_depth = 3
    dsp = ob.modifiers.new("weather_disp", "DISPLACE"); dsp.texture = dtx; dsp.strength = 0.14; dsp.mid_level = 0.5; dsp.texture_coords = "GLOBAL"
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


def extrude_profile(name, a, b, width, profile, mat, coll=None):
    """Closed (s, z) profile in the vertical plane along a -> b (s = metres from a), extruded `width` across. Tapered beams, stair flights."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy * width / 2, ux * width / 2
    profile = [p for i, p in enumerate(profile) if math.dist(p, profile[i - 1]) > 1e-6]  # drop repeated points (zero-length tails)
    bm = bmesh.new()
    side = lambda k: [bm.verts.new((x0 + ux * s + k * nx, y0 + uy * s + k * ny, z)) for s, z in profile]
    va, vb = side(1), side(-1)
    bm.faces.new(va); bm.faces.new(vb[::-1])
    n = len(profile)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((va[j], va[i], vb[i], vb[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.polygons.foreach_set("use_smooth", np.zeros(len(me.polygons), bool))
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def poly_slab(name, pts, z0, z1, mat, coll=None):
    """Vertical prism over a 2D polygon (spiral treads)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]; hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.polygons.foreach_set("use_smooth", np.zeros(len(me.polygons), bool))
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def helix_plate(name, c, r, thick, depth, a0, a1, z0, z1, mat, coll=None, n=96):
    """Helical stringer plate: radius r, z of its top edge rising linearly from z0 (angle a0) to z1 (a1), degrees."""
    vs, fs = [], []
    for k in range(n + 1):
        t = k / n; a = math.radians(a0 + (a1 - a0) * t); zt = z0 + (z1 - z0) * t
        ca, sa = math.cos(a), math.sin(a)
        for rr, zz in ((r - thick / 2, zt - depth), (r + thick / 2, zt - depth), (r + thick / 2, zt), (r - thick / 2, zt)):
            vs.append((c[0] + rr * ca, c[1] + rr * sa, zz))
        if k:
            b0, b1 = 4 * (k - 1), 4 * k
            fs += [(b0 + i, b0 + (i + 1) % 4, b1 + (i + 1) % 4, b1 + i) for i in range(4)]
    fs += [(3, 2, 1, 0), (4 * n, 4 * n + 1, 4 * n + 2, 4 * n + 3)]
    ob = mesh_from(name, vs, fs, smooth=False, coll=coll)
    ob.data.materials.append(mat)
    return ob


TEXDIR = None


def _tex(N, L, tid, fn, vec, non_color=False, box=False):
    from pathlib import Path
    t = N.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(Path.home() / ".cache" / "the_gym" / "textures" / "polyhaven" / tid / fn), check_existing=True)
    if non_color:
        t.image.colorspace_settings.name = "Non-Color"
    if box:
        t.projection = "BOX"; t.projection_blend = 0.35
    L.new(vec, t.inputs["Vector"])
    return t


def rock_material():
    """Granite blocks: three scanned rock textures box-projected at real scale and mixed by large noise, moss on the ledges
    (up-facing), a touch of lichen; height maps as bump so the facets get real surface relief."""
    m = bpy.data.materials.get("rock_scanned")
    if m:
        return m
    m = bpy.data.materials.new("rock_scanned"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    def vec(size):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / size,) * 3
        L.new(tc.outputs["Object"], mp.inputs["Vector"]); return mp.outputs[0]
    layers = [("dark_rock", 2.4), ("lichen_rock", 2.0), ("quarry_wall", 1.8), ("mossy_rock", 3.0)]
    cols, roughs, heights = [], [], []
    for tid, size in layers:
        v = vec(size)
        cols.append(_tex(N, L, tid, "diff.jpg", v, box=True).outputs["Color"])
        roughs.append(_tex(N, L, tid, "rough.jpg", v, True, box=True).outputs["Color"])
        heights.append(_tex(N, L, tid, "disp.jpg", v, True, box=True).outputs["Color"])
    def mixer(fac, a, b_):
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(fac, mx.inputs["Factor"]); L.new(a, mx.inputs["A"]); L.new(b_, mx.inputs["B"])
        return mx.outputs["Result"]
    def noise_fac(scale, lo, hi, seed_off):
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 3
        mo = N.new("ShaderNodeMapping"); mo.inputs["Location"].default_value = (seed_off, seed_off * 1.7, 0)
        L.new(tc.outputs["Object"], mo.inputs["Vector"]); L.new(mo.outputs[0], nz.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange"); mr.interpolation_type = "SMOOTHSTEP"; mr.inputs[1].default_value = lo; mr.inputs[2].default_value = hi
        L.new(nz.outputs["Fac"], mr.inputs[0]); return mr.outputs[0]
    f1, f2 = noise_fac(0.06, 0.42, 0.58, 0.0), noise_fac(0.11, 0.45, 0.62, 13.0)
    # moss: faces looking up, broken by noise
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    up = N.new("ShaderNodeMapRange"); up.inputs[1].default_value = 0.45; up.inputs[2].default_value = 0.8; L.new(sep.outputs["Z"], up.inputs[0])
    mn = N.new("ShaderNodeMath"); mn.operation = "MULTIPLY"; mn.use_clamp = True; L.new(up.outputs[0], mn.inputs[0]); L.new(noise_fac(0.5, 0.35, 0.6, 5.0), mn.inputs[1])
    col = mixer(mn.outputs[0], mixer(f2, mixer(f1, cols[0], cols[1]), cols[2]), cols[3])
    rough = mixer(mn.outputs[0], mixer(f2, mixer(f1, roughs[0], roughs[1]), roughs[2]), roughs[3])
    hgt = mixer(mn.outputs[0], mixer(f2, mixer(f1, heights[0], heights[1]), heights[2]), heights[3])
    cool = N.new("ShaderNodeMix"); cool.data_type = "RGBA"; cool.blend_type = "MULTIPLY"; cool.inputs["Factor"].default_value = 1.0
    cool.inputs["B"].default_value = (0.82, 0.86, 0.9, 1)  # grey gneiss / granite of the Glomma valley, not warm sandstone
    L.new(col, cool.inputs["A"]); col = cool.outputs["Result"]
    L.new(col, b.inputs["Base Color"]); L.new(rough, b.inputs["Roughness"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.8; bump.inputs["Distance"].default_value = 0.04
    L.new(hgt, bump.inputs["Height"]); L.new(bump.outputs[0], b.inputs["Normal"])
    return m


def water_material():
    """River water: near-glass surface (IOR 1.333) with the tea-brown tint of a Norwegian forest river, ripples stretched
    along the flow (north -> south, so along y), fine chop on top. You see the bed through it in the shallows."""
    m = bpy.data.materials.get("river_water")
    if m:
        return m
    m = bpy.data.materials.new("river_water"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.42, 0.40, 0.26, 1)  # tea-brown humic water
    b.inputs["Roughness"].default_value = 0.02; b.inputs["IOR"].default_value = 1.333
    for nm in ("Transmission Weight", "Transmission"):
        if nm in b.inputs:
            b.inputs[nm].default_value = 0.92
            break
    tc = N.new("ShaderNodeTexCoord")
    def ripple(scale, stretch, strength, dist):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale * stretch, scale)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.55
        L.new(mp.outputs[0], nz.inputs["Vector"])
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength; bp.inputs["Distance"].default_value = dist
        L.new(nz.outputs["Fac"], bp.inputs["Height"])
        return bp
    big = ripple(0.9, 0.25, 0.35, 0.08)   # long flow streaks
    fine = ripple(7.0, 0.6, 0.15, 0.01)   # chop
    L.new(big.outputs[0], fine.inputs["Normal"]); L.new(fine.outputs[0], b.inputs["Normal"])
    return m


def cliff_face(H, rock, x0, y0, exclude, coll=None, sheet=0.7, joint=2.0):
    """Jointed granite cliff skin over the steep rock cells (the way procedural cliffs are built: a rock skin that follows the
    wall, broken into blocks by a Voronoi pattern stretched into horizontal sheets, each block stepped in/out by its own
    depth, so ledges and joints get sharp breaks). H at 1 m, origin x0,y0. sheet = layer thickness, joint = joint spacing (m)."""
    gy, gx = np.gradient(H)
    steep = (np.degrees(np.arctan(np.hypot(gx, gy))) > 40) & (rock > 0.25) & ~exclude
    steep = steep | np.roll(steep, 1, 0) | np.roll(steep, -1, 0) | np.roll(steep, 1, 1) | np.roll(steep, -1, 1)  # a 1-cell skirt
    q = steep[:-1, :-1] & steep[1:, :-1] & steep[:-1, 1:] & steep[1:, 1:]
    ny, nx = H.shape
    idx = np.arange(nx * ny).reshape(ny, nx)
    quads = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1)[q]
    used = np.unique(quads); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used))
    Xg, Yg = np.meshgrid(x0 + 0.5 + np.arange(nx), y0 + 0.5 + np.arange(ny))
    v = np.stack([Xg.ravel()[used], Yg.ravel()[used], H.ravel()[used] + 0.05], 1)
    ob = mesh_from("cliff_face", v, remap[quads], smooth=False, coll=coll)
    ob.data.materials.append(rock_material())
    ng = bpy.data.node_groups.new("GN_cliff", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    sd = N.new("GeometryNodeSubdivideMesh"); sd.inputs["Level"].default_value = 3  # 1 m -> 12.5 cm: joints read as sharp steps
    L.new(gi.outputs[0], sd.inputs["Mesh"])
    pos = N.new("GeometryNodeInputPosition"); nrm = N.new("GeometryNodeInputNormal")
    sc = N.new("ShaderNodeVectorMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = (1 / joint, 1 / joint, 1 / sheet)
    L.new(pos.outputs[0], sc.inputs[0])
    vor = N.new("ShaderNodeTexVoronoi"); vor.voronoi_dimensions = "3D"; vor.feature = "F1"; vor.inputs["Scale"].default_value = 1.0
    vor.inputs["Randomness"].default_value = 0.85; L.new(sc.outputs[0], vor.inputs["Vector"])
    cell = N.new("FunctionNodeSeparateColor"); L.new(vor.outputs["Color"], cell.inputs[0])  # random per block
    depth = N.new("ShaderNodeMath"); depth.operation = "MULTIPLY_ADD"; L.new(cell.outputs[0], depth.inputs[0])
    depth.inputs[1].default_value = 0.9; depth.inputs[2].default_value = -0.2           # each block stands 0.2 m in .. 0.7 m out
    edge = N.new("ShaderNodeTexVoronoi"); edge.voronoi_dimensions = "3D"; edge.feature = "DISTANCE_TO_EDGE"
    L.new(sc.outputs[0], edge.inputs["Vector"])
    chip = N.new("ShaderNodeMapRange"); chip.inputs[1].default_value = 0.0; chip.inputs[2].default_value = 0.08
    chip.inputs[3].default_value = -0.12; chip.inputs[4].default_value = 0.0; L.new(edge.outputs["Distance"], chip.inputs[0])  # chipped, open joints
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6; L.new(pos.outputs[0], nz.inputs["Vector"])
    nzc = N.new("ShaderNodeMapRange"); nzc.inputs[3].default_value = -0.08; nzc.inputs[4].default_value = 0.08; L.new(nz.outputs["Fac"], nzc.inputs[0])
    s1 = N.new("ShaderNodeMath"); s1.operation = "ADD"; L.new(depth.outputs[0], s1.inputs[0]); L.new(chip.outputs[0], s1.inputs[1])
    s2 = N.new("ShaderNodeMath"); s2.operation = "ADD"; L.new(s1.outputs[0], s2.inputs[0]); L.new(nzc.outputs[0], s2.inputs[1])
    off = N.new("ShaderNodeVectorMath"); off.operation = "SCALE"; L.new(nrm.outputs[0], off.inputs[0]); L.new(s2.outputs[0], off.inputs["Scale"])
    sp = N.new("GeometryNodeSetPosition"); L.new(sd.outputs[0], sp.inputs["Geometry"]); L.new(off.outputs[0], sp.inputs["Offset"])
    flat = N.new("GeometryNodeSetShadeSmooth"); flat.inputs["Shade Smooth"].default_value = False; L.new(sp.outputs[0], flat.inputs["Geometry"])
    L.new(flat.outputs[0], go.inputs[0])
    md = ob.modifiers.new("cliff", "NODES"); md.node_group = ng
    return ob


def fallen_blocks(H, rock, x0, y0, exclude, rng, coll=None, n=140):
    """A few large angular blocks at the cliff toes: cuboid slabs with corners sliced off at random angles (jointed granite)."""
    gy, gx = np.gradient(H)
    toe = (np.degrees(np.arctan(np.hypot(gx, gy))) < 30) & (rock > 0.2) & ~exclude
    cells = np.argwhere(toe)
    if not len(cells):
        return None
    cells = cells[rng.choice(len(cells), min(n, len(cells)), replace=False)]
    bm = bmesh.new()
    for (j, i) in cells:
        w, d, h = rng.uniform(0.8, 2.6), rng.uniform(0.6, 1.8), rng.uniform(0.35, 1.0)
        tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0)
        bmesh.ops.scale(tmp, vec=(w, d, h), verts=tmp.verts)
        for _ in range(3):  # slice corners off: sharp joint planes
            nv = Vector((rng.normal(), rng.normal(), rng.normal() * 0.6)).normalized()
            bmesh.ops.bisect_plane(tmp, geom=tmp.verts[:] + tmp.edges[:] + tmp.faces[:], plane_co=nv * rng.uniform(0.25, 0.45) * min(w, d, h) * 1.6,
                                   plane_no=nv, clear_outer=True)
            bmesh.ops.contextual_create(tmp, geom=[e for e in tmp.edges if e.is_boundary])
        ang = rng.uniform(0, 2 * math.pi); tilt = rng.normal(0, 0.12)
        bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(ang, 3, "Z") @ Matrix.Rotation(tilt, 3, "X"))
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(i + x0 + 0.5, j + y0 + 0.5, H[j, i] + h * 0.25))
        me = bpy.data.meshes.new("tmp"); tmp.to_mesh(me); bm.from_mesh(me); bpy.data.meshes.remove(me); tmp.free()
    me = bpy.data.meshes.new("fallen_blocks"); bm.to_mesh(me); bm.free()
    me.polygons.foreach_set("use_smooth", np.zeros(len(me.polygons), bool))
    ob = bpy.data.objects.new("fallen_blocks", me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.data.materials.append(rock_material())
    return ob

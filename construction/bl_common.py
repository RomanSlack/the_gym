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


HDRI_DEFAULT = "kloofendal_48d_partly_cloudy_puresky_4k.hdr"  # assets/manifest.json: partly cloudy, sunny midday (CC0)


def hdri_world(scene, fname=HDRI_DEFAULT, sun_azimuth_deg=220.0, strength=1.0):
    """World = the HDRI (its own sun lights the scene: no lamp). The sky is rotated so its sun comes from `sun_azimuth_deg`
    (compass degrees, 220 = south-west, the design's light). Returns False if the HDRI isn't cached (run tools/assets.py)."""
    from pathlib import Path
    path = Path.home() / ".cache" / "the_gym" / "hdris" / "polyhaven" / fname
    if not path.exists():
        return False
    img = bpy.data.images.load(str(path), check_existing=True)
    w_, h_ = img.size
    px = np.empty(w_ * h_ * 4, np.float32); img.pixels.foreach_get(px)
    lum = px.reshape(h_, w_, 4)[..., :3].sum(-1)
    vrow, ucol = np.unravel_index(int(np.argmax(lum)), lum.shape)
    u, v = (ucol + 0.5) / w_, (vrow + 0.5) / h_
    have = (0.5 - u) * 2 * math.pi  # Cycles equirect: u = 0.5 - atan2(dy, dx) / 2pi
    az = math.radians(sun_azimuth_deg)
    want = math.atan2(math.cos(az), math.sin(az))  # compass -> math angle (x east, y north)
    w = bpy.data.worlds.new("hdri_sky"); scene.world = w; w.use_nodes = True
    N, L = w.node_tree.nodes, w.node_tree.links
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, have - want)
    env = N.new("ShaderNodeTexEnvironment"); env.image = img
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs[0], env.inputs["Vector"])
    L.new(env.outputs["Color"], N["Background"].inputs["Color"]); N["Background"].inputs["Strength"].default_value = strength
    scene["sun_elevation_deg"] = round(math.degrees((v - 0.5) * math.pi), 1)
    return True


def world_and_render(scene):
    if hdri_world(scene):
        for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            try:
                scene.render.engine = eng; break
            except TypeError:
                continue
        scene.render.resolution_x, scene.render.resolution_y = 1600, 900
        scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Base Contrast"
        scene.view_settings.exposure = 1.3  # real midday HDRI: a bright Nordic summer day
        return
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


# ------------------------------------------------------------------ interior finishes (stage 5): real pieces, real sizes
def _pieces_mesh(name, boxes, mat, coll):
    """boxes: list of (8 corner verts) ; every piece gets a random 'prand' (texture offset / tint per board, slat, slab)."""
    vs, fs, pr = [], [], []
    rng_ = np.random.default_rng(abs(hash(name)) % 2**32)
    for corners in boxes:
        b = len(vs); vs += corners; r = float(rng_.random())
        fs += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]
        pr += [r] * 8
    ob = mesh_from(name, vs, fs, {"prand": np.array(pr)}, smooth=False, coll=coll)
    ob.data.materials.append(mat)
    return ob


def _box(x0, y0, z0, x1, y1, z1):
    return [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]


def pattern_floor(e, mat, coll, rng):
    x0, y0, x1, y1 = e["rect"]; z0, z1 = e["z"]; p = e["pattern"]
    boxes = []
    if p["kind"] in ("boards", "slabs"):
        w, gap = p["w"], p["gap"]
        along_y = p.get("dir", "y") == "y"
        a0, a1, c0, c1 = (y0, y1, x0, x1) if along_y else (x0, x1, y0, y1)
        c = c0; row = 0
        while c < c1 - 1e-6:
            cw = min(w, c1 - c)
            a = a0 - (rng.uniform(0, max(p["L"])) if p["kind"] == "boards" else (p["L"][0] / 2 if row % 2 and p.get("bond") != "stack" else 0))  # staggered / running / stack bond
            while a < a1 - 1e-6:
                L = float(rng.choice(p["L"])) if p["kind"] == "boards" else p["L"][0]
                s0, s1 = max(a, a0), min(a + L, a1)
                if s1 - s0 > 0.05:
                    q = (c + gap / 2, s0 + gap / 2, c + cw - gap / 2, s1 - gap / 2)
                    q = (q[0], q[1], q[2], q[3]) if along_y else (q[1], q[0], q[3], q[2])
                    for r_ in _minus_holes(q, e.get("holes", [])):  # recesses (e.g. the entrance mat well): pieces cut round them
                        boxes.append(_box(r_[0], r_[1], z0, r_[2], r_[3], z1))
                a += L
            c += w; row += 1
    else:  # poured: panels between saw cuts
        J = p["joint"]
        nx_, ny_ = max(1, round((x1 - x0) / J)), max(1, round((y1 - y0) / J))
        for i in range(nx_):
            for j in range(ny_):
                boxes.append(_box(x0 + (x1 - x0) * i / nx_ + 0.0015, y0 + (y1 - y0) * j / ny_ + 0.0015, z0,
                                  x0 + (x1 - x0) * (i + 1) / nx_ - 0.0015, y0 + (y1 - y0) * (j + 1) / ny_ - 0.0015, z1))
    return _pieces_mesh(e["id"], boxes, mat, coll)


def _minus_holes(q, holes):
    """Axis-aligned rect q (x0, y0, x1, y1) minus rect holes ({"rect": [x0, y0, x1, y1]}): the pieces left over."""
    out = [q]
    for h in holes:
        if "rect" not in h or not isinstance(h["rect"][0], (int, float)):
            continue
        hx0, hy0, hx1, hy1 = h["rect"]; nxt = []
        for (x0, y0, x1, y1) in out:
            if hx0 >= x1 or hx1 <= x0 or hy0 >= y1 or hy1 <= y0:
                nxt.append((x0, y0, x1, y1)); continue
            for r_ in ((x0, y0, hx0, y1), (hx1, y0, x1, y1), (max(x0, hx0), y0, min(x1, hx1), hy0), (max(x0, hx0), hy1, min(x1, hx1), y1)):
                if r_[2] - r_[0] > 0.01 and r_[3] - r_[1] > 0.01:
                    nxt.append(r_)
        out = nxt
    return out


def pattern_ceiling(e, mat, coll, beam_lines):
    x0, y0, x1, y1 = e["rect"]; z0, z1 = e["z"]; p = e["pattern"]
    half = e.get("between_beams", 0.25) / 2 + 0.02
    boxes = []
    y = y0 + p["pitch"] / 2
    while y < y1:
        if all(abs(y - yb) > half + p["w"] / 2 for yb in beam_lines):
            boxes.append(_box(x0, y - p["w"] / 2, z0, x1, y + p["w"] / 2, z1))
        y += p["pitch"]
    return _pieces_mesh(e["id"], boxes, mat, coll)


def pattern_lining(e, mat, coll, rng, backing_mat=None):
    """Wall linings: vertical slats on black battens, stone courses, or a plain skin; openings left open."""
    (ax, ay), (bx, by) = e["from"], e["to"]; z0, z1 = e["z"]; p = e["pattern"]
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    fnx, fny = e.get("face_normal", (-uy, ux)); d = e["size"][0]
    ops = e.get("openings", [])
    def blocked(s0, s1, za, zb):
        return any(o["s"][0] < s1 and o["s"][1] > s0 and o["z"][0] < zb and o["z"][1] > za for o in ops)
    def quad(s0, s1, za, zb, t0, t1):  # piece from s0..s1 along, za..zb up, t0..t1 out from the wall face (t measured along the face normal)
        pts = []
        for zz in (za, zb):
            for (s, t) in ((s0, t0), (s1, t0), (s1, t1), (s0, t1)):
                pts.append((ax + ux * s + fnx * t, ay + uy * s + fny * t, zz))
        return [pts[0], pts[1], pts[2], pts[3], pts[4], pts[5], pts[6], pts[7]]
    boxes, back = [], []
    base_t = -d / 2  # e from/to sit at the lining centre; t is relative to that
    if p["kind"] == "slats":
        s = p["pitch"] / 2
        while s < L - p["w"] / 2:
            segs = [(z0, z1)]
            for o in ops:
                if o["s"][0] < s + p["w"] and o["s"][1] > s - p["w"]:
                    segs = [q for sg in segs for q in ((sg[0], min(sg[1], o["z"][0])), (max(sg[0], o["z"][1]), sg[1])) if q[1] - q[0] > 0.05]
            for za, zb in segs:
                boxes.append(quad(s - p["w"] / 2, s + p["w"] / 2, za, zb, base_t + d - p["d"], base_t + d))
            s += p["pitch"]
        back.append((0.0, L))
    elif p["kind"] == "tiles":  # glazed wall tiles in stack bond on a grout bed; tiles cut at the ends, none across an opening
        t_d = p["d"]; g = p["gap"]
        z = z0
        while z < z1 - 0.02:
            h = min(p["h"], z1 - z); s = 0.0
            while s < L - 0.01:
                w_ = min(p["w"], L - s)
                if not blocked(s, s + w_, z, z + h):
                    boxes.append(quad(s + g / 2, s + w_ - g / 2, z + g / 2, z + h - g / 2, base_t + d - t_d, base_t + d))
                s += p["w"]
            z += h
        cuts = sorted({0.0, L, *[v for o in ops for v in o["s"]]})
        for s0, s1 in zip(cuts, cuts[1:]):
            mid = (s0 + s1) / 2; segs = [(z0, z1)]
            for o in ops:
                if o["s"][0] <= mid <= o["s"][1]:
                    segs = [q for sg in segs for q in ((sg[0], min(sg[1], o["z"][0])), (max(sg[0], o["z"][1]), sg[1])) if q[1] - q[0] > 0.02]
            back += [quad(s0, s1, za, zb, base_t, base_t + d - t_d + 0.001) for za, zb in segs]
        _pieces_mesh(e["id"] + "_grout", back, material("grout_warm", (0.6, 0.58, 0.54), 0.9), coll)
        back = []
    elif p["kind"] == "courses":
        z = z0
        while z < z1 - 1e-6:
            h = min(float(rng.choice(p["h"])), z1 - z); s = -rng.uniform(0, max(p["L"]))
            while s < L:
                ln = float(rng.choice(p["L"])); s0, s1 = max(s, 0), min(s + ln, L)
                if s1 - s0 > 0.05 and not blocked(s0, s1, z, z + h):
                    boxes.append(quad(s0 + p["gap"] / 2, s1 - p["gap"] / 2, z + p["gap"] / 2, z + h - p["gap"] / 2, base_t, base_t + d))
                s += ln
            z += h
    else:  # plain skin, cut round openings
        cuts = sorted({0.0, L, *[v for o in ops for v in o["s"]]})
        for s0, s1 in zip(cuts, cuts[1:]):
            mid = (s0 + s1) / 2; segs = [(z0, z1)]
            for o in ops:
                if o["s"][0] <= mid <= o["s"][1]:
                    segs = [q for sg in segs for q in ((sg[0], min(sg[1], o["z"][0])), (max(sg[0], o["z"][1]), sg[1])) if q[1] - q[0] > 0.02]
            boxes += [quad(s0, s1, za, zb, base_t, base_t + d) for za, zb in segs]
    ob = _pieces_mesh(e["id"], boxes, mat, coll)
    if back and backing_mat is not None:  # black battens / felt behind the slats
        bk = []
        for s0, s1 in back:
            cuts = sorted({s0, s1, *[v for o in ops for v in o["s"] if s0 < v < s1]})
            for a_, b_ in zip(cuts, cuts[1:]):
                mid = (a_ + b_) / 2; segs = [(z0, z1)]
                for o in ops:
                    if o["s"][0] <= mid <= o["s"][1]:
                        segs = [q for sg in segs for q in ((sg[0], min(sg[1], o["z"][0])), (max(sg[0], o["z"][1]), sg[1])) if q[1] - q[0] > 0.02]
                bk += [quad(a_, b_, za, zb, base_t, base_t + d - p["d"]) for za, zb in segs]
        _pieces_mesh(e["id"] + "_backing", bk, backing_mat, coll)
    return ob


def pbr_material(name, tid, size, tint=(1, 1, 1), rough_add=0.0, box=False, rotate=0.0, piece_var=0.12, rough_mul=1.0, sat=1.0, val=1.0):
    """Scanned CC0 PBR at real scale (size = metres per texture tile). Per-piece 'prand' shifts the texture + varies the tone,
    so no two boards / slats / slabs are the same."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); pr = N.new("ShaderNodeAttribute"); pr.attribute_name = "prand"
    off = N.new("ShaderNodeCombineXYZ")
    for i, k in enumerate((7.31, 3.17, 5.03)):
        mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = k * size; L.new(pr.outputs["Fac"], mm.inputs[0]); L.new(mm.outputs[0], off.inputs[i])
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"; L.new(tc.outputs["Object"], add.inputs[0]); L.new(off.outputs[0], add.inputs[1])
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / size,) * 3; mp.inputs["Rotation"].default_value = (0, 0, rotate)
    L.new(add.outputs[0], mp.inputs["Vector"])
    col = _tex(N, L, tid, "diff.jpg", mp.outputs[0], box=box).outputs["Color"]
    tone = N.new("ShaderNodeMapRange"); tone.inputs[3].default_value = 1 - piece_var; tone.inputs[4].default_value = 1 + piece_var
    L.new(pr.outputs["Fac"], tone.inputs[0])
    tcol = N.new("ShaderNodeCombineColor"); tcol.inputs[0].default_value = tint[0]; tcol.inputs[1].default_value = tint[1]; tcol.inputs[2].default_value = tint[2]
    tsc = N.new("ShaderNodeVectorMath"); tsc.operation = "SCALE"; L.new(tcol.outputs[0], tsc.inputs[0]); L.new(tone.outputs[0], tsc.inputs["Scale"])
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
    L.new(col, mul.inputs["A"]); L.new(tsc.outputs[0], mul.inputs["B"])
    hsv = N.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = sat; hsv.inputs["Value"].default_value = val  # e.g. white-oiled oak: paler, less orange
    L.new(mul.outputs["Result"], hsv.inputs["Color"]); L.new(hsv.outputs["Color"], b.inputs["Base Color"])
    rg = _tex(N, L, tid, "rough.jpg", mp.outputs[0], True, box=box).outputs["Color"]
    rm = N.new("ShaderNodeMath"); rm.operation = "MULTIPLY_ADD"; rm.use_clamp = True; rm.inputs[1].default_value = rough_mul; rm.inputs[2].default_value = rough_add
    L.new(rg, rm.inputs[0]); L.new(rm.outputs[0], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.6
    L.new(_tex(N, L, tid, "nor_gl.jpg", mp.outputs[0], True, box=box).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    return m


def interior_materials():
    return {
        "oak_floor": pbr_material("oak_floor", "oak_veneer_01", 1.83, tint=(1.05, 1.0, 0.9), rough_mul=0.8, rough_add=0.1, piece_var=0.07, sat=0.6, val=1.75),   # white-oiled oak
        "oak_slat": pbr_material("oak_slat", "oak_veneer_01", 1.83, box=True, rough_mul=0.9, rough_add=0.15, piece_var=0.07, tint=(1.05, 1.0, 0.9), sat=0.65, val=1.7),
        "stone_honed": pbr_material("stone_honed", "dark_rock", 2.4, tint=(0.62, 0.64, 0.66), box=True, rough_mul=0.55, rough_add=0.2, piece_var=0.08),
        "concrete_ground": pbr_material("concrete_ground", "smooth_concrete_floor", 2.0, tint=(0.95, 0.92, 0.86), rough_mul=0.7, rough_add=0.15, piece_var=0.04),
        "clt_white": pbr_material("clt_white", "coated_pine_02", 1.05, tint=(1.25, 1.22, 1.15), box=True, piece_var=0.03),
        "clt_natural": pbr_material("clt_natural", "coated_pine_02", 1.05, tint=(1.05, 0.98, 0.85), box=True, piece_var=0.03),
        "lime_plaster": material("lime_plaster", (0.80, 0.77, 0.71), 0.9),   # smooth warm-white lime plaster
        "stone_light": pbr_material("stone_light", "smooth_concrete_floor", 2.0, tint=(1.0, 0.98, 0.95), box=True, rough_mul=0.6, rough_add=0.15, piece_var=0.05, sat=0.2, val=2.0),
        "felt_black": material("felt_black", (0.012, 0.012, 0.013), 0.95),
        "ash_fin": pbr_material("ash_fin", "ash_veneer", 1.0, box=True, tint=(1.05, 1.02, 0.95), sat=0.45, val=1.75, piece_var=0.06),
        "impact_mat": material("impact_mat", (0.05, 0.05, 0.05), 0.9),
        "screed": material("screed", (0.4, 0.39, 0.37), 0.9),
        "timber_stud": material("painted_gypsum", (0.82, 0.8, 0.76), 0.85),
        "glass_partition": material("glass", (0.05, 0.07, 0.08), 0.05, alpha=0.28),
        "tile_glazed": glazed_tile(),
    }


def glazed_tile(name="tile_chalk", tones=((0.80, 0.78, 0.72), (0.76, 0.74, 0.68), (0.83, 0.81, 0.76), (0.73, 0.71, 0.66))):
    """Handmade-look glazed tile: every tile ('prand') picks its own glaze tone, the glaze pools and waves a little
    (noise bump), glossy with a thin clear coat, slightly rougher where the glaze thins."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    pr = N.new("ShaderNodeAttribute"); pr.attribute_name = "prand"
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    els = ramp.color_ramp.elements
    for k, t in enumerate(tones):
        e_ = els[k] if k < len(els) else els.new(k / len(tones))
        e_.position = k / len(tones); e_.color = (*t, 1)
    L.new(pr.outputs["Fac"], ramp.inputs["Fac"])
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 0.08
    L.new(ramp.outputs["Color"], mix.inputs["A"]); L.new(nz.outputs["Color"], mix.inputs["B"])
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs[3].default_value = 0.05; rr.inputs[4].default_value = 0.2
    L.new(nz.outputs["Fac"], rr.inputs[0]); L.new(rr.outputs[0], b.inputs["Roughness"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12; bump.inputs["Distance"].default_value = 0.002
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    for k_, v_ in (("Coat Weight", 0.4), ("Coat Roughness", 0.03)):
        if k_ in b.inputs:
            b.inputs[k_].default_value = v_
    return m


def arch_glass(name, tint=(0.92, 0.95, 0.94), rough=0.0, frosted=False):
    """Architectural glass for Cycles: glass BSDF to the camera (reflection + see-through), fully transparent to shadow rays,
    so daylight and sun actually come into the rooms (a thin box of real glass would block / caustic most of it)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    gl = N.new("ShaderNodeBsdfGlass"); gl.inputs["Color"].default_value = (*tint, 1); gl.inputs["Roughness"].default_value = rough; gl.inputs["IOR"].default_value = 1.5
    tr = N.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (*tint, 1)
    lp = N.new("ShaderNodeLightPath")
    mx = N.new("ShaderNodeMixShader")
    fac = N.new("ShaderNodeMath"); fac.operation = "MAXIMUM"; L.new(lp.outputs["Is Shadow Ray"], fac.inputs[0]); L.new(lp.outputs["Is Diffuse Ray"], fac.inputs[1])
    L.new(fac.outputs[0], mx.inputs[0]); L.new(gl.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    if frosted:
        dif = N.new("ShaderNodeBsdfTranslucent"); dif.inputs["Color"].default_value = (0.85, 0.87, 0.88, 1)
        mf = N.new("ShaderNodeMixShader"); mf.inputs[0].default_value = 0.6; L.new(mx.outputs[0], mf.inputs[1]); L.new(dif.outputs[0], mf.inputs[2]); mx = mf
    L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def metal_material(name, rgb, rough=(0.22, 0.42), brushed=True, wear=0.0):
    """Believable metal: roughness varies across the surface (noise), fine directional brushing (anisotropy + stretched noise
    in the bump), a slight tone drift; optional edge wear (pointiness) for blackened steel. Real metals are never uniform."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Metallic"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord")
    big = N.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 3.0; big.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], big.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs[3].default_value = rough[0]; rr.inputs[4].default_value = rough[1]; L.new(big.outputs["Fac"], rr.inputs[0])
    L.new(rr.outputs[0], b.inputs["Roughness"])
    tone = N.new("ShaderNodeMapRange"); tone.inputs[3].default_value = 0.88; tone.inputs[4].default_value = 1.08; L.new(big.outputs["Fac"], tone.inputs[0])
    col = N.new("ShaderNodeCombineColor"); col.inputs[0].default_value, col.inputs[1].default_value, col.inputs[2].default_value = rgb
    cs = N.new("ShaderNodeVectorMath"); cs.operation = "SCALE"; L.new(col.outputs[0], cs.inputs[0]); L.new(tone.outputs[0], cs.inputs["Scale"])
    base = cs.outputs[0]
    if wear > 0:  # worn, slightly brighter edges
        geo = N.new("ShaderNodeNewGeometry")
        we = N.new("ShaderNodeMapRange"); we.inputs[1].default_value = 0.52; we.inputs[2].default_value = 0.6; L.new(geo.outputs["Pointiness"], we.inputs[0])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["B"].default_value = (min(1, rgb[0] * 4 + 0.15), min(1, rgb[1] * 4 + 0.15), min(1, rgb[2] * 4 + 0.15), 1)
        fm = N.new("ShaderNodeMath"); fm.operation = "MULTIPLY"; fm.inputs[1].default_value = wear; L.new(we.outputs[0], fm.inputs[0])
        L.new(fm.outputs[0], mx.inputs["Factor"]); L.new(base, mx.inputs["A"]); base = mx.outputs["Result"]
    L.new(base, b.inputs["Base Color"])
    if brushed:
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (400.0, 4.0, 400.0); L.new(tc.outputs["Object"], mp.inputs["Vector"])
        sc = N.new("ShaderNodeTexNoise"); sc.inputs["Detail"].default_value = 2; L.new(mp.outputs[0], sc.inputs["Vector"])
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.06; bp.inputs["Distance"].default_value = 0.0005; L.new(sc.outputs["Fac"], bp.inputs["Height"])
        L.new(bp.outputs[0], b.inputs["Normal"])
        for nm in ("Anisotropic", "Anisotropy"):
            if nm in b.inputs:
                b.inputs[nm].default_value = 0.5
    return m


def pattern_wave_ceiling(e, mat, coll, beam_lines):
    """Undulating baffle ceiling: pale ash fins (30 mm wide) every 110 mm running across each bay (along x), each fin's depth
    following a slow wave (60 -> 320 mm) whose phase drifts from fin to fin, so the ceiling reads as a gentle landscape of ridges."""
    x0, y0, x1, y1 = e["rect"]; ztop = e["z"][1]; p = e["pattern"]
    half = e.get("between_beams", 0.25) / 2 + 0.03
    vs, fs, pr = [], [], []
    rng_ = np.random.default_rng(7)
    y = y0 + p["pitch"] / 2
    nseg = max(8, int((x1 - x0) / 0.25))
    while y < y1:
        if all(abs(y - yb) > half + p["w"] / 2 for yb in beam_lines):
            r = float(rng_.random())
            ph = y / p.get("drift", 4.0) * 2 * math.pi
            for k in range(nseg):
                xa, xb = x0 + (x1 - x0) * k / nseg, x0 + (x1 - x0) * (k + 1) / nseg
                da = p["dmin"] + (p["dmax"] - p["dmin"]) * (0.5 + 0.5 * math.sin(2 * math.pi * xa / p["wave"] + ph))
                db = p["dmin"] + (p["dmax"] - p["dmin"]) * (0.5 + 0.5 * math.sin(2 * math.pi * xb / p["wave"] + ph))
                ya, yb_ = y - p["w"] / 2, y + p["w"] / 2
                b = len(vs)
                vs += [(xa, ya, ztop - da), (xb, ya, ztop - db), (xb, yb_, ztop - db), (xa, yb_, ztop - da),
                       (xa, ya, ztop), (xb, ya, ztop), (xb, yb_, ztop), (xa, yb_, ztop)]
                fs += [(b, b + 3, b + 2, b + 1), (b, b + 1, b + 5, b + 4), (b + 2, b + 3, b + 7, b + 6)]
                if k == 0:
                    fs.append((b + 3, b, b + 4, b + 7))
                if k == nseg - 1:
                    fs.append((b + 1, b + 2, b + 6, b + 5))
                pr += [r] * 8
        y += p["pitch"]
    ob = mesh_from(e["id"], vs, fs, {"prand": np.array(pr)}, smooth=False, coll=coll)
    ob.data.materials.append(mat)
    return ob


def powder_coat(name, rgb=(0.028, 0.028, 0.03)):
    """Powder-coated / painted steel and aluminium (frames, posts, girders): a dielectric paint, not bare metal. Reads real through
    (1) orange-peel micro texture in the bump, (2) roughness that drifts across a member (0.28-0.5), (3) a faint lighter cast on
    edges where the coat thins (pointiness), (4) a very fine dust layer on upward faces. Pair with small bevels so edges catch light."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Metallic"].default_value = 0.0
    for nm in ("Coat Weight", "Clearcoat"):
        if nm in b.inputs:
            b.inputs[nm].default_value = 0.1; break
    tc = N.new("ShaderNodeTexCoord"); geo = N.new("ShaderNodeNewGeometry")
    drift = N.new("ShaderNodeTexNoise"); drift.inputs["Scale"].default_value = 2.5; drift.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], drift.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs[3].default_value = 0.28; rr.inputs[4].default_value = 0.5; L.new(drift.outputs["Fac"], rr.inputs[0]); L.new(rr.outputs[0], b.inputs["Roughness"])
    col = N.new("ShaderNodeCombineColor"); col.inputs[0].default_value, col.inputs[1].default_value, col.inputs[2].default_value = rgb
    edge = N.new("ShaderNodeMapRange"); edge.inputs[1].default_value = 0.5; edge.inputs[2].default_value = 0.56; L.new(geo.outputs["Pointiness"], edge.inputs[0])
    em = N.new("ShaderNodeMix"); em.data_type = "RGBA"; em.inputs["B"].default_value = (rgb[0] * 2.6 + 0.02, rgb[1] * 2.6 + 0.02, rgb[2] * 2.6 + 0.02, 1)
    ef = N.new("ShaderNodeMath"); ef.operation = "MULTIPLY"; ef.inputs[1].default_value = 0.0; L.new(edge.outputs[0], ef.inputs[0])  # pointiness is unreliable on box profiles: off
    L.new(ef.outputs[0], em.inputs["Factor"]); L.new(col.outputs[0], em.inputs["A"])
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    up = N.new("ShaderNodeMapRange"); up.inputs[1].default_value = 0.7; up.inputs[2].default_value = 1.0; up.inputs[4].default_value = 0.08; L.new(sep.outputs["Z"], up.inputs[0])
    dust = N.new("ShaderNodeMix"); dust.data_type = "RGBA"; dust.inputs["B"].default_value = (0.18, 0.17, 0.16, 1)
    L.new(up.outputs[0], dust.inputs["Factor"]); L.new(em.outputs["Result"], dust.inputs["A"]); L.new(dust.outputs["Result"], b.inputs["Base Color"])
    peel = N.new("ShaderNodeTexNoise"); peel.inputs["Scale"].default_value = 900.0; peel.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], peel.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.0004
    L.new(peel.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def stained_timber(name="tarred_timber"):
    """Black-stained / tarred timber with its grain showing through (scanned CC0 black painted planks)."""
    return pbr_material(name, "black_painted_planks", 1.6, box=True, tint=(0.9, 0.88, 0.85), sat=0.6, val=0.85, piece_var=0.08, rough_mul=0.9, rough_add=0.05)


def blackened_steel(name="blackened_steel_d"):
    """Option D, Roman's primary metal: hot-rolled steel, chemically blackened and waxed. Uneven blue-black and smoky grey
    tones in soft clouds, mill-scale streaks along the rolling direction, darker pooling, satin wax sheen that varies
    (roughness 0.28-0.55), fine pitting in the bump. Every member reads a little different, like the real thing."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Metallic"].default_value = 0.85
    tc = N.new("ShaderNodeTexCoord"); oi = N.new("ShaderNodeObjectInfo")
    seed = N.new("ShaderNodeVectorMath"); seed.operation = "ADD"; L.new(tc.outputs["Object"], seed.inputs[0])
    rs = N.new("ShaderNodeCombineXYZ"); L.new(oi.outputs["Random"], rs.inputs[0]); L.new(oi.outputs["Random"], rs.inputs[1]); L.new(rs.outputs[0], seed.inputs[1])
    def noise(scale, stretch=(1, 1, 1), detail=4):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = stretch; L.new(seed.outputs[0], mp.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail; nz.inputs["Roughness"].default_value = 0.6
        L.new(mp.outputs[0], nz.inputs["Vector"]); return nz.outputs["Fac"]
    clouds = noise(1.8)
    scale_ = noise(6.0, stretch=(1.0, 1.0, 9.0))  # mill-scale streaks run along the member (z for posts and mullions)
    ramp = N.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.3; els[0].color = (0.018, 0.02, 0.025, 1)      # blue-black
    els[1].position = 0.75; els[1].color = (0.075, 0.072, 0.07, 1)     # smoky grey patches
    e = els.new(0.52); e.color = (0.035, 0.036, 0.042, 1)
    mx = N.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; mx.inputs[1].default_value = 0.35; L.new(scale_, mx.inputs[0]); L.new(clouds, mx.inputs[2])
    mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.35; mr.inputs[2].default_value = 1.05; L.new(mx.outputs[0], mr.inputs[0])
    L.new(mr.outputs[0], ramp.inputs[0]); L.new(ramp.outputs[0], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs[3].default_value = 0.28; rr.inputs[4].default_value = 0.55; L.new(clouds, rr.inputs[0]); L.new(rr.outputs[0], b.inputs["Roughness"])
    pit = noise(700.0, detail=2)
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08; bp.inputs["Distance"].default_value = 0.0003; L.new(pit, bp.inputs["Height"])
    bp2 = N.new("ShaderNodeBump"); bp2.inputs["Strength"].default_value = 0.15; bp2.inputs["Distance"].default_value = 0.001; L.new(scale_, bp2.inputs["Height"]); L.new(bp.outputs[0], bp2.inputs["Normal"])
    L.new(bp2.outputs[0], b.inputs["Normal"])
    return m


def brass_accent(name="brass_accent"):
    """Brushed, lightly aged brass for small accents only (pulls, call plates, inlays)."""
    return metal_material(name, (0.78, 0.58, 0.3), rough=(0.2, 0.38))

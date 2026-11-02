"""Test renders of the nordic moss set (maps/): one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python materials/nordic_moss/render_test.py -- SHOT OUT.png [--scale 0.06] [--samples 256]

--wet 1: after rain, water running down over it (0-1).
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
SCALE, SAMPLES, WET = opt("--scale", 0.06), int(opt("--samples", 256)), opt("--wet", 0.0)
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


def moss_material(name="nordic_moss", d=MAPS, box=False, scale=SCALE, files=None, coverage=1.0, by_slope=0.0, wet=None):
    """The method's shader, two layers: the bare granite (rock_* maps) and the moss cushions on it (albedo/height/normal/ao),
    switched by vis = how much of each cushion is kept: moss_dist (0 at a cushion's edge -> 1 deep inside) above 1 - coverage,
    so less coverage shrinks the cushions from their edges and drops the small ones. by_slope > 0: coverage falls on
    down-facing surfaces and gets a little noise (moss on a boulder's top and shaded sides, not underneath).
    Rock: dry matte (rough 0.62-0.92 from the map, specular 0.2). Moss: rough 1.0, a little sheen and subsurface.
    `files` (a plain scan set, no layers) for the comparison panel."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    try:
        m.displacement_method = "BOTH"
    except Exception:
        m.cycles.displacement_method = "BOTH"
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")

    def tex(fname, color=False):
        t = N.new("ShaderNodeTexImage"); t.image = img(d / fname, color)
        if box:
            t.projection = "BOX"; t.projection_blend = 0.5
            L.new(tc.outputs["Object"], t.inputs["Vector"])
        else:
            L.new(tc.outputs["UV"], t.inputs["Vector"])
        return t

    def mix(fac, a_, b_, rgb=False):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA" if rgb else "FLOAT"
        L.new(fac, n.inputs[0])
        L.new(a_, n.inputs[6] if rgb else n.inputs[2]); L.new(b_, n.inputs[7] if rgb else n.inputs[3])
        return n.outputs[2] if rgb else n.outputs[0]

    def math(op, a_, b_=None, c_=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a_, b_, c_)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    if files:                                                      # a plain scan: one layer
        col, hgt, nrm, ao, rgh = (tex(files[k], k == "albedo").outputs[0] for k in ("albedo", "height", "normal", "ao", "rough"))
        vis = None
    else:
        cov = coverage
        if by_slope:
            geo = N.new("ShaderNodeNewGeometry")
            sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
            noise = N.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 1.6
            L.new(tc.outputs["Object"], noise.inputs["Vector"])
            # coverage = coverage + by_slope * (normal z) + noise: full on top, thinning down the sides, none underneath
            cov = math("ADD", math("MULTIPLY_ADD", sep.outputs["Z"], by_slope, coverage), math("MULTIPLY", math("SUBTRACT", noise.outputs[0], 0.5), 0.7))
        dist = tex("moss_dist.png").outputs[0]
        mask = tex("mask_shade.png").outputs[0]
        t_ = math("SUBTRACT", 1.0, cov) if not isinstance(cov, float) else 1.0 - cov
        mr = N.new("ShaderNodeMapRange"); mr.clamp = True
        L.new(dist, mr.inputs["Value"])
        if isinstance(t_, float):
            mr.inputs["From Min"].default_value = t_ - 0.02; mr.inputs["From Max"].default_value = t_ + 0.06
        else:
            L.new(math("SUBTRACT", t_, 0.02), mr.inputs["From Min"]); L.new(math("ADD", t_, 0.06), mr.inputs["From Max"])
        vis = math("MULTIPLY", mr.outputs["Result"], mask)
        col = mix(vis, tex("rock_albedo.png", True).outputs[0], tex("albedo.png", True).outputs[0], rgb=True)
        # the cushions taper down to the rock at whatever edge the dial leaves (a cut cushion stood as a cliff)
        mr2 = N.new("ShaderNodeMapRange"); mr2.clamp = True; mr2.interpolation_type = "SMOOTHSTEP"
        L.new(dist, mr2.inputs["Value"])
        if isinstance(t_, float):
            mr2.inputs["From Min"].default_value = t_ - 0.02; mr2.inputs["From Max"].default_value = t_ + 0.3
        else:
            L.new(math("SUBTRACT", t_, 0.02), mr2.inputs["From Min"]); L.new(math("ADD", t_, 0.3), mr2.inputs["From Max"])
        rh = tex("rock_height.png").outputs[0]
        thick = math("MAXIMUM", math("SUBTRACT", tex("height.png").outputs[0], rh), 0.0)
        hgt = math("MULTIPLY_ADD", thick, math("MULTIPLY", mr2.outputs["Result"], mask), rh)
        nrm = mix(vis, tex("rock_normal.png").outputs[0], tex("normal.png").outputs[0], rgb=True)
        ao = mix(vis, tex("rock_ao.png").outputs[0], tex("ao.png").outputs[0])
        rgh = tex("roughness.png").outputs[0]
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.blend_type = "MULTIPLY"; c2.inputs[0].default_value = 0.55
    L.new(col, c2.inputs[6]); L.new(ao, c2.inputs[7])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.2
    L.new(nrm, nm.inputs["Color"])
    rock = N.new("ShaderNodeBsdfPrincipled")
    L.new(c2.outputs[2], rock.inputs["Base Color"]); L.new(rgh, rock.inputs["Roughness"])
    rock.inputs["Specular IOR Level"].default_value = 0.2
    L.new(nm.outputs[0], rock.inputs["Normal"])
    mo = N.new("ShaderNodeBsdfPrincipled")
    L.new(c2.outputs[2], mo.inputs["Base Color"])
    mo.inputs["Roughness"].default_value = 1.0
    mo.inputs["Specular IOR Level"].default_value = 0.1
    mo.inputs["Sheen Weight"].default_value = 0.25
    mo.inputs["Sheen Tint"].default_value = (0.35, 0.5, 0.15, 1)
    mo.inputs["Subsurface Weight"].default_value = 0.15
    L.new(nm.outputs[0], mo.inputs["Normal"])
    wet = WET if wet is None else wet
    if wet > 0:
        # wet (Roman: "like it was raining or had water flowing over it"): the stone darker and more saturated (water fills its
        # pores), a thin water film on it (a clear coat, IOR 1.33) that fills the fine grain, glassy pools in the hollows and
        # streaks of running water down the fall line; the moss soaks it up: deeper green, matte underneath, a light glisten
        # and droplets on its tips
        g_ = N.new("ShaderNodeGamma"); g_.inputs[1].default_value = 2.1; L.new(c2.outputs[2], g_.inputs[0])
        hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 1.25; hs.inputs["Value"].default_value = 0.92
        L.new(g_.outputs[0], hs.inputs["Color"])
        geo2 = N.new("ShaderNodeNewGeometry")
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (9, 9, 0.35)   # streaks: long down the fall line (world z)
        L.new(geo2.outputs["Position"], mp.inputs["Vector"])
        sn = N.new("ShaderNodeTexNoise"); sn.inputs["Scale"].default_value = 2.2; sn.inputs["Detail"].default_value = 6
        L.new(mp.outputs[0], sn.inputs["Vector"])
        st_ = N.new("ShaderNodeMapRange"); st_.inputs["From Min"].default_value = 0.5; st_.inputs["From Max"].default_value = 0.58
        L.new(sn.outputs[0], st_.inputs["Value"]); streak = st_.outputs["Result"]
        pl = N.new("ShaderNodeMapRange"); pl.inputs["From Min"].default_value = 0.93; pl.inputs["From Max"].default_value = 0.72
        L.new(ao, pl.inputs["Value"]); pool = pl.outputs["Result"]
        water = math("MULTIPLY", math("ADD", 0.22, math("MULTIPLY", math("MAXIMUM", pool, streak), 0.78)), wet)   # damp everywhere, a full film only where it runs or pools
        dark = math("MULTIPLY", math("ADD", 0.8, math("MULTIPLY", math("MAXIMUM", pool, streak), 0.2)), wet)
        wc = N.new("ShaderNodeMix"); wc.data_type = "RGBA"; L.new(dark, wc.inputs[0]); L.new(c2.outputs[2], wc.inputs[6]); L.new(hs.outputs[0], wc.inputs[7])
        L.new(wc.outputs[2], rock.inputs["Base Color"])            # the streaks darken the stone; the moss is soaked evenly
        # (the wet references: soaked moss goes MORE vivid, its leaves unfurl and glow when backlit, so saturation up, not darker)
        hm = N.new("ShaderNodeHueSaturation"); hm.inputs["Hue"].default_value = 0.5 + 0.035 * wet; hm.inputs["Saturation"].default_value = 1.0 + 0.3 * wet; hm.inputs["Value"].default_value = 1.0 - 0.12 * wet
        L.new(c2.outputs[2], hm.inputs["Color"]); L.new(hm.outputs[0], mo.inputs["Base Color"])
        # rock: the film
        fn = N.new("ShaderNodeNormalMap"); fn.inputs["Strength"].default_value = 0.3; L.new(nrm, fn.inputs["Color"])
        rb = N.new("ShaderNodeBump"); rb.inputs["Strength"].default_value = 0.15; rb.inputs["Distance"].default_value = 0.002
        L.new(sn.outputs[0], rb.inputs["Height"]); L.new(fn.outputs[0], rb.inputs["Normal"])
        L.new(water, rock.inputs["Coat Weight"]); rock.inputs["Coat IOR"].default_value = 1.33
        L.new(math("SUBTRACT", 0.16, math("MULTIPLY", math("MAXIMUM", pool, streak), 0.14)), rock.inputs["Coat Roughness"])
        L.new(rb.outputs[0], rock.inputs["Coat Normal"])
        L.new(math("MULTIPLY", rgh, 1 - 0.55 * wet), rock.inputs["Roughness"])
        rock.inputs["Specular IOR Level"].default_value = 0.2 + 0.3 * wet
        # moss: droplets on the tips (~4 mm cells, about a third of them carry a drop)
        vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 230
        L.new(geo2.outputs["Position"], vo.inputs["Vector"])
        dr_ = N.new("ShaderNodeMapRange"); dr_.inputs["From Min"].default_value = 0.42; dr_.inputs["From Max"].default_value = 0.0
        dr_.interpolation_type = "SMOOTHSTEP"; L.new(vo.outputs["Distance"], dr_.inputs["Value"])
        sepc = N.new("ShaderNodeSeparateColor"); L.new(vo.outputs["Color"], sepc.inputs[0])
        keep = N.new("ShaderNodeMapRange"); keep.inputs["From Min"].default_value = 0.64; keep.inputs["From Max"].default_value = 0.66
        L.new(sepc.outputs[0], keep.inputs["Value"])
        drop = math("MULTIPLY", dr_.outputs["Result"], keep.outputs["Result"])
        db = N.new("ShaderNodeBump"); db.inputs["Strength"].default_value = 0.9; db.inputs["Distance"].default_value = 0.002
        L.new(drop, db.inputs["Height"]); L.new(nm.outputs[0], db.inputs["Normal"])
        L.new(math("MULTIPLY", math("ADD", 0.25, math("MULTIPLY", drop, 0.75)), wet), mo.inputs["Coat Weight"])
        mo.inputs["Coat IOR"].default_value = 1.33; mo.inputs["Coat Roughness"].default_value = 0.06
        L.new(db.outputs[0], mo.inputs["Coat Normal"])
        mo.inputs["Roughness"].default_value = 1.0 - 0.2 * wet
        mo.inputs["Sheen Weight"].default_value = 0.25 * (1 - wet)
        mo.inputs["Subsurface Weight"].default_value = 0.15 + 0.25 * wet
    sh = N.new("ShaderNodeMixShader")
    if vis is not None:
        L.new(vis, sh.inputs[0])
    L.new(rock.outputs[0], sh.inputs[1]); L.new(mo.outputs[0], sh.inputs[2])
    L.new(sh.outputs[0], out.inputs["Surface"])
    dp = N.new("ShaderNodeDisplacement"); dp.inputs["Midlevel"].default_value = 0.15; dp.inputs["Scale"].default_value = scale
    L.new(hgt, dp.inputs["Height"]); L.new(dp.outputs[0], out.inputs["Displacement"])
    return m


def droplets(size, loc, n=30000, seed=7, scale=SCALE):
    """Real water drops on a vertical panel (panel(): UV u -> world x, v -> world z, facing -y), sat on the displaced surface:
    round beads 0.8-3 mm on the moss tips (the wet references: each a little lens), fewer, flatter, smaller ones on the stone."""
    import numpy as np
    rng = np.random.default_rng(seed)
    def px(f):
        im = bpy.data.images.load(str(MAPS / f), check_existing=True); im.colorspace_settings.name = "Non-Color"
        a_ = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a_)
        return a_.reshape(im.size[1], im.size[0], 4)[..., 0]
    mask, h, md = px("mask_shade.png"), px("height.png"), px("moss_dist.png")
    S = mask.shape[0]
    u, v = rng.random(n * 3), rng.random(n * 3)
    iu, iv = (u * (S - 1)).astype(int), (v * (S - 1)).astype(int)
    moss = (mask[iv, iu] > 0.6) & (md[iv, iu] > 0.03)
    keep = moss | (rng.random(n * 3) < 0.10)
    u, v, iu, iv, moss = u[keep][:n], v[keep][:n], iu[keep][:n], iv[keep][:n], moss[keep][:n]
    r = np.where(moss, np.clip(rng.lognormal(np.log(0.0009), 0.6, len(u)), 0.0004, 0.0038),   # many tiny, a few big
                 np.clip(rng.lognormal(np.log(0.0008), 0.3, len(u)), 0.0004, 0.0016))
    off = (h[iv, iu] - 0.15) * scale + np.where(moss, r * 0.5, r * 0.15)       # out of the surface (toward -y), resting on it
    cx, cy, cz = loc[0] + (u - 0.5) * size, loc[1] - off, loc[2] + (v - 0.5) * size
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
    t = bpy.context.object; tv = np.array([vv.co[:] for vv in t.data.vertices]); tf = [list(f.vertices) for f in t.data.polygons]
    bpy.data.objects.remove(t)
    sy = np.where(moss, 0.85, 0.45)                                            # beads on stone sit flatter (they wet it)
    V = (tv[None] * np.stack([r, r * sy, r], 1)[:, None] + np.stack([cx, cy, cz], 1)[:, None]).reshape(-1, 3)
    F = (np.array(tf)[None] + (np.arange(len(u)) * len(tv))[:, None, None]).reshape(-1, 3)
    me = bpy.data.meshes.new("drops"); me.from_pydata(V.tolist(), [], F.tolist()); me.update()
    for poly in me.polygons:
        poly.use_smooth = True
    o = bpy.data.objects.new("drops", me); sc.collection.objects.link(o)
    w = bpy.data.materials.new("water"); w.use_nodes = True
    b = w.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Roughness"].default_value = 0.0
    b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["IOR"].default_value = 1.33
    o.data.materials.append(w)
    print(f"droplets: {len(u)} ({int(moss.sum())} on moss)")
    return o


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
    """an interior-like setup: one big soft area key (a window / skylight), a weak sky fill (wet: the real sky, so the water
    has something to reflect)"""
    if WET > 0 and bc.hdri_world(sc, strength=0.35):
        pass
    else:
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
    if WET > 0:
        droplets(2.0, (0, 0, 1.0), n=int(opt("--drops", 45000)))
        sc.cycles.transmission_bounces = 8; sc.cycles.max_bounces = 12
    # a pale floor + side walls so the light reads like a room
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -2, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.55, 0.53, 0.5), 0.8))
    if SHOT == "wall":
        lights(mathutils.Vector((-1.8, -2.2, 3.0)), 2.5, 260)
        look((0.0, -3.0, 1.1), (0.0, 0.0, 1.0), 35)
    else:
        lights(mathutils.Vector((-2.4, -0.9, 1.6)), 1.2, 170)        # raking from the left: the relief shows
        look((0.25, -0.75, 1.15), (0.05, 0.0, 0.95), 50)
elif SHOT == "boulder":
    # a glacial granite boulder: lumpy, asymmetric, flat-ish where it sits in the ground; moss on the top and shaded sides
    m = moss_material(box=True, scale=SCALE * 0.9, coverage=1.0, by_slope=0.7)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=7, radius=0.7, location=(0, 0, 0))
    o = bpy.context.object; o.scale = (1.2, 0.85, 0.7); o.rotation_euler = (0.08, -0.05, 0.5)
    for nm_, typ, sc_, st in (("big", "CLOUDS", 0.9, 0.30), ("mid", "VORONOI", 0.45, 0.10), ("small", "CLOUDS", 0.18, 0.025)):
        tx = bpy.data.textures.new(nm_, typ); tx.noise_scale = sc_
        dm = o.modifiers.new(nm_, "DISPLACE"); dm.texture = tx; dm.strength = st; dm.texture_coords = "GLOBAL"; dm.mid_level = 0.5
    bpy.ops.object.convert(target="MESH")
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data)
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts); floor_z = zs[int(len(zs) * 0.18)]   # sunk: the lowest 18 % below the ground
    for v in bm.verts:
        w = mw @ v.co
        if w.z < floor_z:
            v.co = mw.inverted() @ mathutils.Vector((w.x, w.y, floor_z))
    bm.to_mesh(o.data); bm.free()
    o.location.z -= floor_z
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.5, 0.48, 0.45), 0.85))
    lights(mathutils.Vector((-2.2, -2.0, 2.8)), 2.0, 260)
    look((0.5, -2.6, 1.3), (0.0, 0.0, 0.42), 42)
elif SHOT == "compare":
    ours = moss_material()
    scan = moss_material("scan", SCAN / "polyhaven" / "mossy_rock", files={"albedo": "diff.jpg", "height": "disp.jpg", "normal": "nor_gl.jpg",
                                                                         "rough": "rough.jpg", "ao": "ao.jpg"}, scale=SCALE * 0.5)
    panel("ours", 1.6, ours, loc=(-0.9, 0, 0.9), cuts=800)
    panel("scan", 1.6, scan, loc=(0.9, 0, 0.9), cuts=800)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -2, 0)); bpy.context.object.data.materials.append(bc.material("floor", (0.55, 0.53, 0.5), 0.8))
    lights(mathutils.Vector((-1.5, -2.4, 3.0)), 3.0, 340)
    look((0.0, -3.2, 1.0), (0.0, 0.0, 0.9), 40)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

"""Ground for the finished site (stage 4+): terrain material by stand type + generated grass on sod roofs, lawns and the meadow.

Terrain layers (scanned CC0, real scale, blended by masks on the terrain mesh, docs/ECOLOGY.md):
  spruce stands  -> forest_floor (needles + feather moss, bilberry-dark)
  pine stands    -> forest_leaves_04 with a pale lichen/heather tint (the driest, poorest ground)
  clear-cuts     -> withered_grass (wavy hair-grass, dry)
  lawns / meadow / garden -> sparse_grass, greener
  rock (flagged + steep) -> mossy_rock;  paths / trail -> gravel_ground_01 (fetched by tools/assets.py)
Grass: tufts of curved blades (real geometry), three kinds; GN-scattered on sod roofs and as points over lawns and the meadow.
"""
import math
import random
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

TEX = Path.home() / ".cache" / "the_gym" / "textures" / "polyhaven"


def _img(N, L, tid, fn, vec, non_color=False):
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(TEX / tid / fn), check_existing=True)
    if non_color:
        t.image.colorspace_settings.name = "Non-Color"
    t.projection = "FLAT"; L.new(vec, t.inputs["Vector"])
    return t


def terrain_material_v2():
    """Masks come from point attributes: 'spruce', 'pine', 'clear', 'lawn', 'path', 'rock' (0..1)."""
    m = bpy.data.materials.new("terrain_finished"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord")
    def vec(size, rot=0.0):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / size, 1 / size, 1 / size); mp.inputs["Rotation"].default_value = (0, 0, rot)
        L.new(tc.outputs["Object"], mp.inputs["Vector"]); return mp.outputs[0]
    layers = {  # name: (texture id, size in m, tint)
        "base": ("forest_floor", 2.14, (0.45, 0.55, 0.32)),     # darkened + greened: feather moss and old needles under spruce
        "pine": ("forest_leaves_04", 1.5, (0.75, 0.72, 0.55)),  # pine heath: browner, a little paler (lichen, heather)
        "clear": ("withered_grass", 2.0, (0.7, 0.68, 0.5)),
        "lawn": ("sparse_grass", 2.0, (0.75, 1.0, 0.6)),
        "path": ("gravel_ground_01", 3.0, (1, 1, 1)),
        "rock": ("dark_rock", 2.4, (0.9, 0.9, 0.9)),
        "bed": ("river_small_rocks", 2.9, (0.7, 0.68, 0.6)),     # riverbed, seen through the water
    }
    col = rough = nrm = None
    breakup = N.new("ShaderNodeTexNoise"); breakup.inputs["Scale"].default_value = 0.08; L.new(tc.outputs["Object"], breakup.inputs["Vector"])
    for name, (tid, size, tint) in layers.items():
        v = vec(size, rot=0.37 * len(name))
        c = _img(N, L, tid, "diff.jpg", v).outputs["Color"]
        if tint != (1, 1, 1):
            mt = N.new("ShaderNodeMix"); mt.data_type = "RGBA"; mt.blend_type = "MULTIPLY"; mt.inputs["Factor"].default_value = 1
            mt.inputs["B"].default_value = (*tint, 1); L.new(c, mt.inputs["A"]); c = mt.outputs["Result"]
        r = _img(N, L, tid, "rough.jpg", v, True).outputs["Color"]
        n_ = _img(N, L, tid, "nor_gl.jpg", v, True).outputs["Color"]
        if col is None:
            col, rough, nrm = c, r, n_
            continue
        at = N.new("ShaderNodeAttribute"); at.attribute_name = name
        # soft, noisy edges between layers
        ns = N.new("ShaderNodeMath"); ns.operation = "MULTIPLY_ADD"; L.new(breakup.outputs["Fac"], ns.inputs[0]); ns.inputs[1].default_value = 0.6; ns.inputs[2].default_value = -0.3
        fac = N.new("ShaderNodeMath"); fac.operation = "ADD"; fac.use_clamp = True; L.new(at.outputs["Fac"], fac.inputs[0]); L.new(ns.outputs[0], fac.inputs[1])
        sm = N.new("ShaderNodeMapRange"); sm.interpolation_type = "SMOOTHSTEP"; sm.inputs[1].default_value = 0.35; sm.inputs[2].default_value = 0.65
        L.new(fac.outputs[0], sm.inputs[0])
        for kind, cur, new_ in (("RGBA", col, c), ("RGBA", rough, r), ("RGBA", nrm, n_)):
            mx = N.new("ShaderNodeMix"); mx.data_type = kind; L.new(sm.outputs[0], mx.inputs["Factor"]); L.new(cur, mx.inputs["A"]); L.new(new_, mx.inputs["B"])
            if cur is col:
                col = mx.outputs["Result"]
            elif cur is rough:
                rough = mx.outputs["Result"]
            else:
                nrm = mx.outputs["Result"]
    L.new(col, b.inputs["Base Color"]); L.new(rough, b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); L.new(nrm, nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    return m


def ground_masks(H_shape_crop, crop, forest_npz, fm, rock, water=None):
    """Per-vertex masks on the cropped 1 m terrain grid (crop = (rows slice, cols slice) into the 2000 x 2000 site grid)."""
    F = np.load(forest_npz)
    sp, dh = F["species"], F["dom_height_m"]
    step, o = float(F["step"]), float(F["origin"])
    rs, cs = crop
    yy = np.arange(rs.start, rs.stop) - 1000 + 0.5; xx = np.arange(cs.start, cs.stop) - 1000 + 0.5
    i = np.clip(((yy - o) / step).astype(int), 0, sp.shape[0] - 1)[:, None]; j = np.clip(((xx - o) / step).astype(int), 0, sp.shape[1] - 1)[None, :]
    s, h = sp[i, j], dh[i, j]
    f = fm[rs, cs]
    lawn = ((f & (4096 | 16 | 512 | 8192)) > 0).astype(np.float32)
    path = ((f & (32 | 256 | 2048 | 1024)) > 0).astype(np.float32)
    clear = ((h < 4) & (s > 0)).astype(np.float32)
    return {"pine": ((s == 2) & (clear == 0)).astype(np.float32), "clear": clear, "lawn": lawn, "path": path,
            "rock": np.clip(rock[rs, cs] * 1.5, 0, 1).astype(np.float32),
            "bed": (np.zeros(s.shape, np.float32) if water is None else (~np.isnan(water[rs, cs])).astype(np.float32))}


# ------------------------------------------------------------------ grass
def grass_proto(name, kind, coll):
    """A tuft of curved blades along +Z. kinds: 'lawn' short and fine, 'meadow' long sod-roof / meadow grass, 'dry' hair-grass."""
    rng = random.Random({"lawn": 1, "meadow": 2, "dry": 3}[kind])
    n, hmin, hmax, w = {"lawn": (28, 0.06, 0.12, 0.003), "meadow": (24, 0.18, 0.42, 0.004), "dry": (30, 0.15, 0.32, 0.0015)}[kind]
    vs, fs = [], []
    for _ in range(n):
        az = rng.random() * 2 * math.pi; lean = rng.uniform(0.15, 0.6); h = rng.uniform(hmin, hmax)
        base = Vector((rng.gauss(0, 0.02), rng.gauss(0, 0.02), 0))
        d = Vector((math.cos(az), math.sin(az), 0)); side = Vector((-d.y, d.x, 0))
        seg = 4; b0 = len(vs)
        for k in range(seg + 1):
            t = k / seg
            p = base + d * (lean * h * t * t) + Vector((0, 0, h * (t - 0.25 * lean * t * t)))
            ww = w * (1 - 0.85 * t)
            vs += [tuple(p - side * ww), tuple(p + side * ww)]
        for k in range(seg):
            a = b0 + 2 * k; fs.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs)
    me.polygons.foreach_set("use_smooth", np.ones(len(fs), bool))
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.location = (0, 0, -2000)
    col = {"lawn": (0.10, 0.20, 0.04), "meadow": (0.12, 0.19, 0.05), "dry": (0.35, 0.30, 0.16)}[kind]
    mat = bpy.data.materials.new(name + "_m"); mat.use_nodes = True
    N, L = mat.node_tree.nodes, mat.node_tree.links
    bs = N["Principled BSDF"]; oi = N.new("ShaderNodeObjectInfo")
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (*[c * 0.7 for c in col], 1); ramp.color_ramp.elements[1].color = (*[min(1, c * 1.4) for c in col], 1)
    L.new(oi.outputs["Random"], ramp.inputs[0]); L.new(ramp.outputs[0], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.6
    tl = N.new("ShaderNodeBsdfTranslucent"); L.new(ramp.outputs[0], tl.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.35
    L.new(bs.outputs[0], mx.inputs[1]); L.new(tl.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    me.materials.append(mat)
    return ob


def grass_nodes(name, protos, density, seed=0, up_only=True):
    """GN: distribute tufts over the faces of the object it sits on (density per m2), random yaw + size."""
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Density"].default_value = density; dp.inputs["Seed"].default_value = seed
    L.new(gi.outputs[0], dp.inputs["Mesh"])
    if up_only:  # only faces looking up (the top of the sod, not its edges)
        nrm = N.new("GeometryNodeInputNormal"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(nrm.outputs[0], sep.inputs[0])
        cmp = N.new("FunctionNodeCompare"); cmp.data_type = "FLOAT"; cmp.operation = "GREATER_THAN"; cmp.inputs["B"].default_value = 0.6
        L.new(sep.outputs["Z"], cmp.inputs["A"]); L.new(cmp.outputs[0], dp.inputs["Selection"])
    jn = N.new("GeometryNodeGeometryToInstance")
    for p in protos:
        oi = N.new("GeometryNodeObjectInfo"); oi.inputs[0].default_value = p; oi.transform_space = "ORIGINAL"; L.new(oi.outputs["Geometry"], jn.inputs[0])
    ip = N.new("GeometryNodeInstanceOnPoints"); ip.inputs["Pick Instance"].default_value = True
    rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "INT"; rnd.inputs["Max"].default_value = len(protos) - 1; rnd.inputs["Seed"].default_value = seed + 3
    L.new(rnd.outputs["Value"], ip.inputs["Instance Index"])
    yaw = N.new("FunctionNodeRandomValue"); yaw.data_type = "FLOAT_VECTOR"; yaw.inputs["Max"].default_value = (0, 0, 6.283); yaw.inputs["Min"].default_value = (0, 0, 0)
    sc = N.new("FunctionNodeRandomValue"); sc.data_type = "FLOAT"; sc.inputs["Min"].default_value = 0.7; sc.inputs["Max"].default_value = 1.3
    e2r = N.new("FunctionNodeEulerToRotation"); L.new(yaw.outputs["Value"], e2r.inputs[0]); L.new(e2r.outputs[0], ip.inputs["Rotation"])
    L.new(sc.outputs["Value"], ip.inputs["Scale"])
    L.new(dp.outputs["Points"], ip.inputs["Points"]); L.new(jn.outputs[0], ip.inputs["Instance"])
    jo = N.new("GeometryNodeJoinGeometry"); L.new(gi.outputs[0], jo.inputs[0]); L.new(ip.outputs[0], jo.inputs[0])
    L.new(jo.outputs[0], go.inputs[0])
    return ng

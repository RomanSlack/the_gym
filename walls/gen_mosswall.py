"""Preserved moss wall panel, parametric (Roman 2026-11-02: "let's make some like moss walls ... that would look good in the
gym, with the same vibe ... very parametric procedural"). One seed + a few numbers = one panel, never the same twice.

Built like the bonsai (plants/HOW_WE_BUILT_IT.md): the surfaces are 4K photo textures generated from the references
(walls/maps: flat sheet moss, cushion moss, Norwegian reindeer lichen), the structure is code:
- a relief on the wall plane (3 mm grid): sheet moss as the low carpet, cushion-moss domes, lichen hummocks heaped higher,
  a few half-buried Elverum granite stones; the zones flow in drifts (domain-warped noise), not random dots
- per-vertex weights pick the layer; each texture sampled twice at different scale / rotation and blended by noise so
  the 20 cm tiles never repeat visibly; relief from each texture's own height
- a flush oak frame; a linear grazing light along the top (the gym's way of lighting a texture wall)

Parameters (build kwargs): width, height (m), mix = (sheet, cushion, lichen, stone) shares, flow (drift scale),
relief (dome height, m), frame (m).

    import gen_mosswall; objs = gen_mosswall.build(seed, (x, y, z), width=2.4, height=1.6)
"""
import math
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
MAPS = HERE / "maps"
ROCK = HERE.parent / "materials" / "nordic_moss" / "maps"


def _img(p, color=True):
    im = bpy.data.images.load(str(p), check_existing=True)
    if not color:
        im.colorspace_settings.name = "Non-Color"
    return im


def _noise2(x, y, rng, freq, n=16):
    k = rng.normal(0, 1, (n, 2)) * freq
    ph = rng.uniform(0, 2 * math.pi, n)
    return sum(np.sin(x * k[i, 0] + y * k[i, 1] + ph[i]) for i in range(n)) / math.sqrt(n)


def material():
    """three photo layers by the vertex weights (w_sheet, w_cush, w_lich), each de-tiled (two samplings, noise-blended)"""
    m = bpy.data.materials.new("moss_wall"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    uv = N.new("ShaderNodeUVMap")                                         # UV = metres on the wall
    det = N.new("ShaderNodeTexNoise"); det.inputs["Scale"].default_value = 3.0; det.inputs["Detail"].default_value = 3
    L.new(uv.outputs[0], det.inputs["Vector"])
    dm = N.new("ShaderNodeMapRange"); dm.inputs["From Min"].default_value = 0.42; dm.inputs["From Max"].default_value = 0.58
    L.new(det.outputs[0], dm.inputs["Value"])

    def layer(name, tile, tint=1.0):
        outs = []
        for k, (s_, rot, off) in enumerate(((1.0, 0.0, 0.0), (0.83, 1.1, 0.37))):
            mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (s_ / tile, s_ / tile, 1)
            mp.inputs["Rotation"].default_value = (0, 0, rot); mp.inputs["Location"].default_value = (off, off * 0.6, 0)
            L.new(uv.outputs[0], mp.inputs["Vector"])
            c = N.new("ShaderNodeTexImage"); c.image = _img(MAPS / f"{name}_col.jpg"); L.new(mp.outputs[0], c.inputs["Vector"])
            h = N.new("ShaderNodeTexImage"); h.image = _img(MAPS / f"{name}_h.png", False); L.new(mp.outputs[0], h.inputs["Vector"])
            outs.append((c.outputs[0], h.outputs[0]))
        mc = N.new("ShaderNodeMix"); mc.data_type = "RGBA"; L.new(dm.outputs[0], mc.inputs[0])
        L.new(outs[0][0], mc.inputs[6]); L.new(outs[1][0], mc.inputs[7])
        mh = N.new("ShaderNodeMix"); mh.data_type = "FLOAT"; L.new(dm.outputs[0], mh.inputs[0])
        L.new(outs[0][1], mh.inputs[2]); L.new(outs[1][1], mh.inputs[3])
        return mc.outputs[2], mh.outputs[0]

    sheet, cush, lich = layer("sheet4k", 0.2), layer("cushion4k", 0.22), layer("lichen4k", 0.2)
    wc = N.new("ShaderNodeAttribute"); wc.attribute_name = "w_cush"
    wl = N.new("ShaderNodeAttribute"); wl.attribute_name = "w_lich"
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"; L.new(wc.outputs["Fac"], c1.inputs[0]); L.new(sheet[0], c1.inputs[6]); L.new(cush[0], c1.inputs[7])
    sl = N.new("ShaderNodeMapRange"); sl.inputs["From Min"].default_value = 0.15; sl.inputs["From Max"].default_value = 0.45
    L.new(wl.outputs["Fac"], sl.inputs["Value"]); wl_s = sl.outputs["Result"]                       # (a soft weight read as green lichen)
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; L.new(wl_s, c2.inputs[0]); L.new(c1.outputs[2], c2.inputs[6]); L.new(lich[0], c2.inputs[7])
    h1 = N.new("ShaderNodeMix"); h1.data_type = "FLOAT"; L.new(wc.outputs["Fac"], h1.inputs[0]); L.new(sheet[1], h1.inputs[2]); L.new(cush[1], h1.inputs[3])
    h2 = N.new("ShaderNodeMix"); h2.data_type = "FLOAT"; L.new(wl_s, h2.inputs[0]); L.new(h1.outputs[0], h2.inputs[2]); L.new(lich[1], h2.inputs[3])
    # crevices darker (the light is ours): colour x (0.45 + 0.55 h) x the ambient occlusion baked per vertex
    ao = N.new("ShaderNodeAttribute"); ao.attribute_name = "ao"
    cv = N.new("ShaderNodeMath"); cv.operation = "MULTIPLY_ADD"; cv.inputs[1].default_value = 0.55; cv.inputs[2].default_value = 0.45
    L.new(h2.outputs[0], cv.inputs[0])
    cv2 = N.new("ShaderNodeMath"); cv2.operation = "MULTIPLY"; L.new(cv.outputs[0], cv2.inputs[0]); L.new(ao.outputs["Fac"], cv2.inputs[1])
    dk = N.new("ShaderNodeMix"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"; dk.inputs[0].default_value = 1.0
    L.new(c2.outputs[2], dk.inputs[6]); L.new(cv2.outputs[0], dk.inputs[7])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9; bp.inputs["Distance"].default_value = 0.004
    L.new(h2.outputs[0], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(dk.outputs[2], pb.inputs["Base Color"]); L.new(bp.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = 0.9; pb.inputs["Specular IOR Level"].default_value = 0.2
    pb.inputs["Sheen Weight"].default_value = 0.3; pb.inputs["Sheen Tint"].default_value = (0.6, 0.7, 0.4, 1)
    L.new(pb.outputs[0], out.inputs["Surface"])
    return m


def stone_material():
    m = bpy.data.materials.new("wall_granite"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.5, 2.5, 2.5)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    c = N.new("ShaderNodeTexImage"); c.image = _img(ROCK / "rock_albedo.png"); c.projection = "BOX"; c.projection_blend = 0.3
    L.new(mp.outputs[0], c.inputs["Vector"])
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Value"].default_value = 0.42; hs.inputs["Saturation"].default_value = 0.8
    L.new(c.outputs[0], hs.inputs["Color"]); L.new(hs.outputs[0], b.inputs["Base Color"])          # (read as white chalk)
    h = N.new("ShaderNodeTexImage"); h.image = _img(ROCK / "rock_height.png", False); h.projection = "BOX"; h.projection_blend = 0.3
    L.new(mp.outputs[0], h.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.004
    L.new(h.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.75
    return m


def oak_material():
    m = bpy.data.materials.new("wall_oak"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.45
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (60, 3, 60)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.inputs["Distortion"].default_value = 5; w.inputs["Scale"].default_value = 0.6
    w.inputs["Detail"].default_value = 4
    L.new(mp.outputs[0], w.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); L.new(w.outputs[1], cr.inputs[0])
    cr.color_ramp.elements[0].color = (0.28, 0.18, 0.1, 1); cr.color_ramp.elements[1].color = (0.45, 0.31, 0.18, 1)
    L.new(cr.outputs[0], b.inputs["Base Color"])
    return m


def build(seed, loc=(0, 0, 0), width=2.4, height=1.6, mix=(0.34, 0.36, 0.28, 0.03), flow=2.2, relief=0.07, frame=0.06, res=0.003):
    """the panel stands in the x-z plane facing -y, its back at y = loc.y, its bottom at loc.z"""
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    nx, nz = int(width / res) + 1, int(height / res) + 1
    xs, zs = np.linspace(0, width, nx), np.linspace(0, height, nz)
    X, Z = np.meshgrid(xs, zs)
    # drifts: domain-warped noise fields, one per layer; the shares set by thresholds (quantiles)
    wx = X + 0.12 * _noise2(X, Z, rng, flow * 1.3); wz = Z + 0.12 * _noise2(X, Z, rng, flow * 1.3)
    f_c = _noise2(wx, wz, rng, flow); f_l = _noise2(wx * 1.1 + 3, wz * 0.9 - 2, rng, flow * 0.9)
    sh, cu, li, st = mix
    t_l = np.quantile(f_l, 1 - li); t_c = np.quantile(f_c, 1 - cu)
    soft = lambda f, t, w: np.clip((f - t) / w, 0, 1) ** 1.5
    w_l = soft(f_l, t_l, 0.35)
    w_c = soft(f_c, t_c, 0.35) * (1 - w_l)
    # relief: sheet a low carpet with a little undulation; cushions as domes, lichen as heaped hummocks
    base = 0.006 + 0.004 * _noise2(X, Z, rng, 9)
    bumps = np.zeros_like(X)
    for w_, n_, rr in ((w_c, int(400 * cu * width * height), (0.03, 0.075)), (w_l, int(260 * li * width * height), (0.04, 0.1))):
        cand = rng.random((n_ * 6, 2)) * [width, height]
        ix = np.clip((cand[:, 0] / res).astype(int), 0, nx - 1); iz = np.clip((cand[:, 1] / res).astype(int), 0, nz - 1)
        keep = cand[rng.random(len(cand)) < w_[iz, ix]][:n_]
        for cx, cz in keep:
            r_ = rng.uniform(*rr)
            x0, x1 = max(int((cx - r_) / res), 0), min(int((cx + r_) / res) + 1, nx)
            z0, z1 = max(int((cz - r_) / res), 0), min(int((cz + r_) / res) + 1, nz)
            d2 = ((X[z0:z1, x0:x1] - cx) ** 2 + (Z[z0:z1, x0:x1] - cz) ** 2) / r_ ** 2
            lump = 1 + 0.18 * np.sin((X[z0:z1, x0:x1] - cx) / r_ * rng.uniform(4, 7) + rng.uniform(0, 6)) * np.sin((Z[z0:z1, x0:x1] - cz) / r_ * rng.uniform(4, 7))
            dome = np.sqrt(np.clip(1 - d2 * lump, 0, 1)) * r_ * rng.uniform(0.45, 0.75) * (relief / 0.07)   # lumpy, not balls
            bumps[z0:z1, x0:x1] = np.maximum(bumps[z0:z1, x0:x1], dome * w_[z0:z1, x0:x1] ** 0.5)
    D = base + bumps
    # ambient occlusion from the relief: deep between mounds
    import numpy.fft as fft  # noqa: F401
    def blur(a, s):
        r = int(3 * s); k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum()
        a = np.apply_along_axis(lambda m_: np.convolve(np.pad(m_, r, mode="edge"), k, "valid"), 0, a)
        return np.apply_along_axis(lambda m_: np.convolve(np.pad(m_, r, mode="edge"), k, "valid"), 1, a)
    cav = np.clip(blur(D, 6) - D, 0, None) + 0.5 * np.clip(blur(D, 18) - D, 0, None)
    AO = 1 - np.clip(cav / (np.percentile(cav, 99.5) + 1e-6), 0, 1) * 0.7
    # the mesh
    V = np.stack([X + loc[0] - width / 2, loc[1] - D, Z + loc[2]], -1).reshape(-1, 3)
    ii = np.arange(nx * nz).reshape(nz, nx)
    F = np.stack([ii[:-1, :-1], ii[:-1, 1:], ii[1:, 1:], ii[1:, :-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(f"mosswall_{seed}")
    me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    me.loops.add(F.size); me.loops.foreach_set("vertex_index", F.ravel().astype(np.int32))
    me.polygons.add(len(F)); me.polygons.foreach_set("loop_start", np.arange(0, F.size, 4, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(len(F), 4, np.int32))
    me.update(); me.validate()
    ul = me.uv_layers.new(name="UVMap")
    UVv = np.stack([X.ravel(), Z.ravel()], 1)
    ul.data.foreach_set("uv", UVv[F.ravel()].astype(np.float32).ravel())
    for k, a in (("w_cush", w_c), ("w_lich", w_l), ("ao", AO)):
        at = me.attributes.new(k, "FLOAT", "POINT"); at.data.foreach_set("value", a.astype(np.float32).ravel())
    me.polygons.foreach_set("use_smooth", [True] * len(F)); me.update()
    o = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(material())
    objs = [o]
    # granite stones, half sunk, on the drifts' edges
    sm = stone_material()
    n_st = int(st * 40 * width * height) + 2
    for _ in range(n_st):
        cx, cz = rng.uniform(0.15, width - 0.15), rng.uniform(0.12, height - 0.12)
        r_ = rng.uniform(0.04, 0.11)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1, location=(loc[0] - width / 2 + cx, loc[1] - 0.01, loc[2] + cz))
        s_ = bpy.context.object
        co = np.array([v.co[:] for v in s_.data.vertices])
        co = co * (1 + 0.12 * _noise2(co[:, 0] * 3, co[:, 2] * 3 + co[:, 1], rng, 1.0)[:, None])
        for v, c in zip(s_.data.vertices, co):
            v.co = c
        s_.scale = (r_ * rng.uniform(1, 1.5), r_ * 0.55, r_ * rng.uniform(0.7, 1.0)); s_.rotation_euler = (0, rng.uniform(0, 6.3), 0)
        bpy.ops.object.shade_smooth(); s_.data.materials.append(sm); objs.append(s_)
    # the oak frame, flush: its face 1 cm proud of the moss's deepest point
    oak = oak_material()
    fd = relief + 0.03
    for (sx, sz, x, z) in ((width + 2 * frame, frame, 0, -frame / 2), (width + 2 * frame, frame, 0, height + frame / 2),
                           (frame, height, -width / 2 - frame / 2, height / 2), (frame, height, width / 2 + frame / 2, height / 2)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0] + x, loc[1] - fd / 2, loc[2] + z))
        b = bpy.context.object; b.scale = (sx, fd, sz)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = b.modifiers.new("bv", "BEVEL"); bv.width = 0.003; bv.segments = 2
        b.data.materials.append(oak); objs.append(b)
    print(f"moss wall {seed}: {width} x {height} m, {len(F)} faces, cushion {w_c.mean():.0%}, lichen {w_l.mean():.0%}, {n_st} stones")
    return objs

"""Juniper bonsai (Juniperus chinensis 'Shimpaku') generator, v2: one seed = one tree (plants/GOAL.md).

v1 (a bent pipe with a bark image, flat pad discs on sticks, box tray, box plinth) was rejected: "nah looks weird af",
"make good". A bonsai's character is its wood, so v2 sculpts it (references: out/refs_bonsai_v001.jpg):
- trunk, surface roots and main branches as one fused body: overlapping tubes voxel-remeshed together, so every join grows
  out of the next (no pipe joints), then carved per vertex: long twisting fibre ridges, knots and lumps, the shari (the
  deadwood band spiralling up) sunk into a hollow with raised live-vein lips at its edges, its own tighter grain; a jin
  (dead apex) and dead branch stubs tapering to points
- ramification: each main branch forks twice into thin twigs (separate fine tubes); a foliage cluster sits on every twig tip
  (open branchlet-tip cards + dense sprigs inside, near-horizontal, the top lit, the underside shadowed), so the pads
  form from the clusters and the branches show beneath them; clusters of different branches kept apart
- an oval unglazed clay pot with a rolled lip and feet; the soil under the Nordic cushion moss (materials/nordic_moss,
  real scale, displaced); a dark oak display table
Bark and deadwood: the generated images (maps/bonsai), mapped round each nearest spine and twisted with the ridges.

    import gen_bonsai; objs = gen_bonsai.build(seed, (x, y, z_floor))
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
MAPS = HERE / "maps" / "bonsai"
MOSSMAPS = HERE.parent / "materials" / "nordic_moss" / "maps"
TABLE = 0.62
FRAME = {"pot_scale": 0, "auto": True, "hero": ((0.5, -1.55, 1.12), (0, 0, 0.96), 42), "close": ((0.2, -0.55, 0.98), (0.0, 0, 0.86), 45),
         "trio": ((0, -4.3, 1.3), (0, 0, 0.92), 36), "spacing": 1.2}


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _obj(name, V, F, mat, uv=None, attrs=None, smooth=True, colors=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.asarray(V).tolist(), [], F)
    if colors is not None:
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
        ca.data.foreach_set("color", np.concatenate([colors, np.ones((len(colors), 1))], 1).astype(np.float32).ravel())
    if uv is not None:
        ul = me.uv_layers.new(name="UVMap")
        ul.data.foreach_set("uv", np.array([uv[i] for f in F for i in f], np.float32).ravel())
    for k, a in (attrs or {}).items():
        at = me.attributes.new(k, "FLOAT", "POINT"); at.data.foreach_set("value", np.asarray(a, np.float32))
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons)); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o


def _img(path, color=True):
    im = bpy.data.images.load(str(path), check_existing=True)
    if not color:
        im.colorspace_settings.name = "Non-Color"
    return im


def _pixels(path):
    im = _img(path, False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a)
    return a.reshape(h, w, 4)


# ------------------------------------------------------------------------------------------------------------ materials
_M = {}


def wood_material():
    """bark on the live veins, deadwood on the shari (the 'dead' attribute), both images on the UVs that follow the twist"""
    if "wood" in _M:
        return _M["wood"]
    m = bpy.data.materials.new("bonsai_wood"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    uv = N.new("ShaderNodeUVMap")
    bark = N.new("ShaderNodeTexImage"); bark.image = _img(MAPS / "bark.jpg"); bark.extension = "REPEAT"   # (MIRROR made chevrons)
    dead = N.new("ShaderNodeTexImage"); dead.image = _img(MAPS / "deadwood.jpg"); dead.extension = "REPEAT"
    for t in (bark, dead):
        L.new(uv.outputs[0], t.inputs["Vector"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "dead"
    bk = N.new("ShaderNodeHueSaturation"); bk.inputs["Value"].default_value = 0.75     # live bark a touch deeper
    L.new(bark.outputs[0], bk.inputs["Color"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(at.outputs["Fac"], mx.inputs[0]); L.new(bk.outputs[0], mx.inputs[6]); L.new(dead.outputs[0], mx.inputs[7])
    g = N.new("ShaderNodeRGBToBW"); L.new(mx.outputs[2], g.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.7; bp.inputs["Distance"].default_value = 0.0015
    L.new(g.outputs[0], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(mx.outputs[2], pb.inputs["Base Color"])
    r = N.new("ShaderNodeMath"); r.operation = "MULTIPLY_ADD"; r.inputs[1].default_value = -0.2; r.inputs[2].default_value = 0.88
    L.new(at.outputs["Fac"], r.inputs[0]); L.new(r.outputs[0], pb.inputs["Roughness"])
    pb.inputs["Specular IOR Level"].default_value = 0.3
    L.new(bp.outputs[0], pb.inputs["Normal"])
    L.new(pb.outputs[0], out.inputs["Surface"])
    _M["wood"] = m
    return m


def sprig_material(name):
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    col = N.new("ShaderNodeTexImage"); col.image = _img(MAPS / f"{name}_col.png")
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "shade"
    hs = N.new("ShaderNodeHueSaturation"); L.new(col.outputs["Color"], hs.inputs["Color"])
    L.new(at.outputs["Fac"], hs.inputs["Value"])
    at2 = N.new("ShaderNodeAttribute"); at2.attribute_name = "hue"
    L.new(at2.outputs["Fac"], hs.inputs["Hue"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(hs.outputs[0], pb.inputs["Base Color"])
    pb.inputs["Roughness"].default_value = 0.55; pb.inputs["Specular IOR Level"].default_value = 0.3
    tr = N.new("ShaderNodeBsdfTranslucent")
    tc = N.new("ShaderNodeHueSaturation"); tc.inputs["Value"].default_value = 1.3
    L.new(hs.outputs[0], tc.inputs["Color"]); L.new(tc.outputs[0], tr.inputs["Color"])
    sm = N.new("ShaderNodeMixShader"); sm.inputs[0].default_value = 0.18
    L.new(pb.outputs[0], sm.inputs[1]); L.new(tr.outputs[0], sm.inputs[2])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(col.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(sm.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    _M[name] = m
    return m


def clay():
    """unglazed bonsai clay: dark red-brown, mottled, matte, sandy grain"""
    m = bpy.data.materials.new("pot_clay"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.86; b.inputs["Specular IOR Level"].default_value = 0.25
    tc = N.new("ShaderNodeTexCoord")
    mo = N.new("ShaderNodeTexNoise"); mo.inputs["Scale"].default_value = 14; mo.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], mo.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); L.new(mo.outputs[0], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0.075, 0.04, 0.03, 1)
    cr.color_ramp.elements[1].position = 0.72; cr.color_ramp.elements[1].color = (0.13, 0.07, 0.048, 1)
    L.new(cr.outputs[0], b.inputs["Base Color"])
    gr = N.new("ShaderNodeTexNoise"); gr.inputs["Scale"].default_value = 1200; gr.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], gr.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; bp.inputs["Distance"].default_value = 0.0003
    L.new(gr.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def dark_oak(vertical=False):
    """the display table: dark oiled oak, grain along x (the legs: along z)"""
    m = bpy.data.materials.new("table_oak_v" if vertical else "table_oak"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.42
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (60, 60, 3) if vertical else (3, 60, 60)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "X" if vertical else "Y"; w.inputs["Distortion"].default_value = 6
    w.inputs["Detail"].default_value = 4; w.inputs["Scale"].default_value = 0.4
    L.new(mp.outputs[0], w.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); L.new(w.outputs[1], cr.inputs[0])
    cr.color_ramp.elements[0].color = (0.035, 0.022, 0.014, 1); cr.color_ramp.elements[1].color = (0.075, 0.048, 0.03, 1)
    L.new(cr.outputs[0], b.inputs["Base Color"])
    return m


def moss_material(k):
    """bonsai pot moss (v2, Roman: "the base texture sucks ... like the grass in the pot": the Nordic study's 2 m patch spread
    over 0.5 m read as a blurry lawn): a 4K top-down photo texture of tight cushion moss with akadama grit, generated from the
    moss scan + the references (work/potmoss), one image across the whole pot (0.12 mm a pixel); relief from its height"""
    m = bpy.data.materials.new(f"bonsai_moss{k}"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    uv = N.new("ShaderNodeUVMap")
    a = N.new("ShaderNodeTexImage"); a.image = _img(MAPS / f"potmoss{k}_col.jpg"); L.new(uv.outputs[0], a.inputs["Vector"])
    h = N.new("ShaderNodeTexImage"); h.image = _img(MAPS / f"potmoss{k}_h.png", False); L.new(uv.outputs[0], h.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; bp.inputs["Distance"].default_value = 0.003
    L.new(h.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Value"].default_value = 0.82
    L.new(a.outputs[0], hs.inputs["Color"]); L.new(hs.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.92; b.inputs["Sheen Weight"].default_value = 0.35
    b.inputs["Sheen Tint"].default_value = (0.45, 0.6, 0.2, 1)
    b.inputs["Subsurface Weight"].default_value = 0.08
    return m


# ------------------------------------------------------------------------------------------------------------ geometry
def spine(p0, d0, length, n, rng, bends=2.0, amp=0.25, droop=0.0, up=0.0, horiz=False):
    pts = [np.array(p0, float)]
    d = _unit(np.array(d0, float))
    ph = rng.uniform(0, 2 * math.pi, 2)
    side = _unit(np.cross(d, [0.3, 0.2, 1.0]))
    other = np.cross(d, side)
    for k in range(n):
        t = (k + 1) / n
        bend = amp * (side * math.sin(ph[0] + bends * math.pi * t) + 0.6 * other * math.cos(ph[1] + bends * math.pi * t))
        if horiz:
            bend = bend * [1, 1, 0.25]
        d = _unit(d + bend * (2.0 / n) + np.array([0, 0, -droop + up * t]) * (1.0 / n))
        pts.append(pts[-1] + d * length / n)
    return np.array(pts)


def frames(pts):
    """parallel-transported frames along a curve: tangent, a1, a2"""
    n = len(pts)
    T = _unit(np.gradient(pts, axis=0))
    a1 = np.zeros_like(pts); a1[0] = _unit(np.cross(T[0], [0.3, 1.0, 0.1]))
    for k in range(1, n):
        v = a1[k - 1] - T[k] * (a1[k - 1] @ T[k])
        a1[k] = v / (np.linalg.norm(v) + 1e-12)
    return T, a1, np.cross(T, a1)


def tube(pts, radii, sides=16, uscale=0.06, cap=True):
    V, F, UV = [], [], []
    n = len(pts)
    T, A1, A2 = frames(pts)
    vlen = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    for k in range(n):
        for j in range(sides + 1):
            t = 2 * math.pi * j / sides
            V.append(pts[k] + (A1[k] * math.cos(t) + A2[k] * math.sin(t)) * radii[k])
            UV.append((j / sides * 2 * math.pi * max(radii[k], 0.003) / uscale, vlen[k] / uscale))
    R = sides + 1
    for k in range(n - 1):
        for j in range(sides):
            F.append([k * R + j, k * R + j + 1, (k + 1) * R + j + 1, (k + 1) * R + j])
    if cap:                                                           # both ends closed (open starts read as hollow pipes)
        F.append([(n - 1) * R + j for j in range(sides)]); F.append([j for j in range(sides)][::-1])
    return np.array(V), F, UV


def closed_tube(pts, radii, sides=20):
    """a watertight tube (no seam duplicates, both ends capped): what the voxel fuse needs (v2's first try had an open seam
    and the remesh hollowed the trunk away)"""
    n = len(pts)
    T, A1, A2 = frames(pts)
    t = np.linspace(0, 2 * math.pi, sides, endpoint=False)
    ring = np.cos(t)[None, :, None] * A1[:, None] + np.sin(t)[None, :, None] * A2[:, None]
    V = (pts[:, None] + ring * np.asarray(radii)[:, None, None]).reshape(-1, 3)
    F = [[k * sides + j, k * sides + (j + 1) % sides, (k + 1) * sides + (j + 1) % sides, (k + 1) * sides + j]
         for k in range(n - 1) for j in range(sides)]
    F.append(list(range(sides))[::-1]); F.append([(n - 1) * sides + j for j in range(sides)])
    return V, F


def wavenoise(P, rng, freq, n=20):
    """smooth 3D noise: a sum of random plane waves (numpy, no scipy in Blender)"""
    k = _unit(rng.normal(0, 1, (n, 3))) * freq * rng.uniform(0.6, 1.4, (n, 1))
    ph = rng.uniform(0, 2 * math.pi, n)
    return (np.sin(P @ k.T + ph) * rng.uniform(0.5, 1.0, n)).sum(1) / math.sqrt(n)


def foliage_material():
    """the scale shoots: the per-vertex colour (sage cords, paler tips, brown stems, shaded inside the pads), tiny overlapping
    scales as a bump (Voronoi on the cord's mm-scaled UVs), satin, a little light through"""
    if "fol" in _M:
        return _M["fol"]
    m = bpy.data.materials.new("juniper_foliage"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    ca = N.new("ShaderNodeVertexColor"); ca.layer_name = "col"
    L.new(ca.outputs["Color"], b.inputs["Base Color"])
    uv = N.new("ShaderNodeUVMap"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.3, 0.9, 1)
    L.new(uv.outputs[0], mp.inputs["Vector"])
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 1.0; vo.feature = "F1"
    L.new(mp.outputs[0], vo.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.55; bp.inputs["Distance"].default_value = 0.00025
    L.new(vo.outputs["Distance"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.5; b.inputs["Specular IOR Level"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.12; b.inputs["Subsurface Radius"].default_value = (0.002, 0.004, 0.001)
    _M["fol"] = m
    return m


def foliage_3d(clusters, trunk, rng, S=6):
    """grow the scale shoots: returns V, F, UV (per vertex), shade, colours"""
    DARK, MID, TIP, WOOD = np.array([0.055, 0.085, 0.05]), np.array([0.1, 0.145, 0.085]), np.array([0.19, 0.25, 0.15]), np.array([0.075, 0.04, 0.022])
    segs = []                                                            # p0, p1, r0, r1, colour0, colour1, cluster (c, rc)
    for cpos, rc in clusters:
        k = np.argmin(np.linalg.norm(trunk - cpos, axis=1))
        out = cpos - trunk[k]; out[2] = 0
        out = _unit(out) if np.linalg.norm(out) > 1e-4 else _unit(rng.normal(0, 1, 3) * [1, 1, 0])
        az0 = math.atan2(out[1], out[0])
        tint = rng.normal(0, 0.06, 3) * [0.6, 1, 1.2]
        for _ in range(int(10 + 26000 * rc * rc)):                         # (11000: airy next to the real dense pads)
            az = az0 + rng.normal(0, 1.1)
            el = rng.uniform(-0.3, 0.7)
            d = np.array([math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)])
            base = cpos + rng.normal(0, rc * 0.18, 3) * [1, 1, 0.5]
            Ls = rng.uniform(0.016, 0.034) * (rc / 0.034) ** 0.6
            # the shoot's axis: 5 segments curving up a little
            pts = [base]; dd = d.copy()
            for i in range(5):
                dd = _unit(dd + np.array([0, 0, 0.12]) + rng.normal(0, 0.12, 3))
                pts.append(pts[-1] + dd * Ls / 5)
            rads = np.linspace(0.0011, 0.0005, 6)
            for i in range(5):
                t0, t1 = i / 5, (i + 1) / 5
                c0 = WOOD if t0 < 0.35 else MID * (1 + tint); c1 = WOOD if t1 < 0.45 else (MID if t1 < 0.95 else TIP) * (1 + tint)
                segs.append((pts[i], pts[i + 1], rads[i], rads[i + 1], c0, c1, cpos, rc))
            # side cords all round the axis (137.5 deg), from 30 % up, shorter toward the tip
            phi = rng.uniform(0, 2 * math.pi)
            n_side = int(Ls / 0.0017)
            for j in range(n_side):
                tt = 0.3 + 0.68 * j / max(n_side - 1, 1)
                i = min(int(tt * 5), 4); f = tt * 5 - i
                p0 = pts[i] + (pts[i + 1] - pts[i]) * f
                ax_ = _unit(pts[i + 1] - pts[i])
                a1 = _unit(np.cross(ax_, [0, 0, 1.0]) if abs(ax_[2]) < 0.95 else np.cross(ax_, [1.0, 0, 0])); a2 = np.cross(ax_, a1)
                phi += math.radians(137.5)
                rad_dir = a1 * math.cos(phi) + a2 * math.sin(phi)
                rad_dir = _unit(rad_dir + np.array([0, 0, 0.35]))             # (the cords lean up into the light)
                off = math.radians(rng.uniform(32, 55))
                sd = _unit(ax_ * math.cos(off) + rad_dir * math.sin(off))
                ln = rng.uniform(0.004, 0.008) * (1.15 - 0.55 * tt)
                m1 = p0 + sd * ln * 0.55
                sd2 = _unit(sd + ax_ * 0.35 + rng.normal(0, 0.1, 3))          # curving forward, like the real whipcords
                p2 = m1 + sd2 * ln * 0.45
                segs.append((p0, m1, 0.0008, 0.0007, MID * (1 + tint), MID * (1 + tint), cpos, rc))      # stubby whipcords
                segs.append((m1, p2, 0.0007, 0.00045, MID * (1 + tint), TIP * (1 + tint) * rng.uniform(0.85, 1.1), cpos, rc))
                if ln > 0.006 and rng.random() < 0.5:                         # a few cords fork once more
                    sd3 = _unit(sd2 + rad_dir * 0.6 + rng.normal(0, 0.2, 3))
                    segs.append((m1, m1 + sd3 * ln * 0.4, 0.00045, 0.00028, MID * (1 + tint), TIP * (1 + tint), cpos, rc))
            segs.append((pts[-1], pts[-1] + dd * 0.004, 0.0005, 0.0003, MID * (1 + tint), TIP * (1 + tint), cpos, rc))
    P0 = np.array([s_[0] for s_ in segs]); P1 = np.array([s_[1] for s_ in segs])
    R0 = np.array([s_[2] for s_ in segs]); R1 = np.array([s_[3] for s_ in segs])
    C0 = np.array([s_[4] for s_ in segs]); C1 = np.array([s_[5] for s_ in segs])
    CC = np.array([s_[6] for s_ in segs]); RC = np.array([s_[7] for s_ in segs])
    n = len(segs)
    D = _unit(P1 - P0)
    ref = np.where(np.abs(D[:, 2:3]) < 0.95, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    A1 = _unit(np.cross(D, ref)); A2 = np.cross(D, A1)
    th = 2 * math.pi * np.arange(S) / S
    ring = np.cos(th)[None, :, None] * A1[:, None] + np.sin(th)[None, :, None] * A2[:, None]       # n, S, 3
    V0 = P0[:, None] + ring * R0[:, None, None]; V1 = P1[:, None] + ring * R1[:, None, None]
    apex = P1 + D * R1[:, None] * 0.9
    V = np.concatenate([V0, V1, apex[:, None]], 1)                                                    # n, 2S+1, 3
    seglen = np.linalg.norm(P1 - P0, axis=1)
    UVu = np.tile(th / (2 * math.pi), (n, 1)) * (2 * math.pi * np.maximum(R0, 0.0003) / 0.0004)[:, None]
    UV = np.concatenate([np.stack([UVu, np.zeros((n, S))], 2), np.stack([UVu, np.repeat((seglen / 0.0004)[:, None], S, 1)], 2),
                         np.stack([UVu[:, :1], (seglen / 0.0004 + 1)[:, None]], 2)], 1)
    col = np.concatenate([np.repeat(C0[:, None], S, 1), np.repeat(C1[:, None], S, 1), C1[:, None]], 1)
    # shading inside the pad: the top and the outside lit, the core and the underside dark
    rel = (V - CC[:, None]) / RC[:, None, None]
    hz = np.clip(0.5 + 0.9 * rel[..., 2], 0, 1); rr = np.clip(np.linalg.norm(rel[..., :2], axis=-1), 0, 1.3)
    shade = 0.35 + 0.65 * hz ** 1.1 * (0.55 + 0.45 * np.minimum(rr, 1))
    base = np.arange(n)[:, None] * (2 * S + 1)
    j = np.arange(S); jn = (j + 1) % S
    Q = np.stack([j, jn, S + jn, S + j], 1)[None] + base[:, :, None]                                  # n, S, 4
    T = np.stack([S + j, S + jn, np.full(S, 2 * S)], 1)[None] + base[:, :, None]                     # n, S, 3
    F = [list(f) for f in Q.reshape(-1, 4)] + [list(f) for f in T.reshape(-1, 3)]
    return (V.reshape(-1, 3), F, [tuple(u) for u in UV.reshape(-1, 2)], shade.reshape(-1),
            (col * shade[..., None]).reshape(-1, 3))


# ------------------------------------------------------------------------------------------------------------ the scene
def table_and_pot(loc, rng):
    objs = []
    oak, oak_v = dark_oak(), dark_oak(True)
    tw, td = 0.66, 0.46
    for (sx, sy, sz, x, y, z) in [(tw, td, 0.035, 0, 0, TABLE - 0.0175)] + \
            [(0.045, 0.045, TABLE - 0.035, sx_ * (tw / 2 - 0.05), sy_ * (td / 2 - 0.05), (TABLE - 0.035) / 2)
             for sx_ in (-1, 1) for sy_ in (-1, 1)] + \
            [(tw - 0.1, 0.02, 0.05, 0, sy_ * (td / 2 - 0.05), TABLE - 0.06) for sy_ in (-1, 1)] + \
            [(0.02, td - 0.1, 0.05, sx_ * (tw / 2 - 0.05), 0, TABLE - 0.06) for sx_ in (-1, 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(loc + [x, y, z]))
        o = bpy.context.object; o.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = o.modifiers.new("bv", "BEVEL"); bv.width = 0.003; bv.segments = 2
        o.data.materials.append(oak_v if sz > 0.3 else oak); objs.append(o)
    # the oval pot: a lathe on an ellipse (outer foot -> wall -> rolled lip -> inner wall -> floor)
    a, b = rng.uniform(0.22, 0.26), rng.uniform(0.16, 0.18)
    H = rng.uniform(0.065, 0.08)
    prof = [(0.88, 0.012), (0.93, 0.012), (0.95, 0.02), (0.985, H - 0.012), (1.0, H - 0.005), (1.0, H), (0.985, H + 0.003),
            (0.955, H + 0.002), (0.94, H - 0.004), (0.93, H - 0.015), (0.9, 0.022), (0.0, 0.022)]
    seg = 160
    V, F = [], []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        for r, z in prof:
            V.append((loc[0] + a * r * math.cos(t), loc[1] + b * r * math.sin(t), loc[2] + TABLE + z))
    P = len(prof)
    for i in range(seg):
        for j in range(P - 1):
            a_, b_ = i * P + j, ((i + 1) % seg) * P + j
            F.append((a_, b_, b_ + 1, a_ + 1))
    F.append(tuple(i * P for i in range(seg))[::-1])
    potm = clay()
    objs.append(_obj("bonsai_pot", V, F, potm)); objs[-1]["tree"] = 1          # (framed with the tree: the hero cut the pot off)
    for t in (0.6, 2.55, 3.7, 5.65):                                    # four cloud feet
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=tuple(loc + [a * 0.84 * math.cos(t), b * 0.84 * math.sin(t), TABLE + 0.008]))
        f_ = bpy.context.object; f_.scale = (0.03, 0.022, 0.012); f_.data.materials.append(potm); objs.append(f_)
    # the soil: the pot moss texture across the whole pot, displaced by its own height (cushions up, grit gaps down)
    zs = TABLE + H - 0.008
    burn = rng.uniform(0.05, 0.75, 120)                                  # (the draws the old moss placement used: seeds keep their trees)
    k_ = int(burn[0] * 100) % 2
    hmap = _pixels(MAPS / f"potmoss{k_}_h.png")[..., 0]
    S_ = hmap.shape[0]
    span = 2 * a * 1.04
    nr, nt = 150, 460
    V, UV, F = [], [], []
    for i in range(nr + 1):
        rr = 0.955 * i / nr
        for j in range(nt):
            t = 2 * math.pi * j / nt
            x, y = a * rr * math.cos(t), b * rr * math.sin(t)
            u, v = 0.5 + x / span, 0.5 + y / span
            hgt = hmap[int(v * (S_ - 1)), int(u * (S_ - 1))]
            dome = 0.012 * (1 - rr ** 2)
            V.append((loc[0] + x, loc[1] + y, zs + dome + (hgt - 0.5) * 0.007 * min(1, (0.955 - rr) / 0.06) - 0.004 * (rr > 0.94)))
            UV.append((u, v))
    for i in range(nr):
        for j in range(nt):
            F.append([i * nt + j, i * nt + (j + 1) % nt, (i + 1) * nt + (j + 1) % nt, (i + 1) * nt + j])
    objs.append(_obj("bonsai_moss", V, F, moss_material(k_), UV))
    stone = bpy.data.materials.new("pebble"); stone.use_nodes = True     # speckled granite (v1 was smooth grey clay)
    sn, sl = stone.node_tree.nodes, stone.node_tree.links
    sb = sn["Principled BSDF"]; sb.inputs["Roughness"].default_value = 0.62
    tc_ = sn.new("ShaderNodeTexCoord")
    vo = sn.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 14; sl.new(tc_.outputs["Object"], vo.inputs["Vector"])
    sep = sn.new("ShaderNodeSeparateColor"); sl.new(vo.outputs["Color"], sep.inputs[0])
    cr = sn.new("ShaderNodeValToRGB"); sl.new(sep.outputs[0], cr.inputs[0])
    cr.color_ramp.interpolation = "CONSTANT"
    cr.color_ramp.elements[0].color = (0.02, 0.02, 0.02, 1)                       # mica / hornblende
    cr.color_ramp.elements[1].position = 0.25; cr.color_ramp.elements[1].color = (0.2, 0.19, 0.18, 1)   # quartz-grey
    e = cr.color_ramp.elements.new(0.75); e.color = (0.34, 0.3, 0.27, 1)          # feldspar
    mo = sn.new("ShaderNodeTexNoise"); mo.inputs["Scale"].default_value = 1.5; sl.new(tc_.outputs["Object"], mo.inputs["Vector"])
    mx = sn.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.5
    sl.new(cr.outputs[0], mx.inputs[6]); sl.new(mo.outputs[0], mx.inputs[7]); sl.new(mx.outputs[2], sb.inputs["Base Color"])
    nz = sn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6; nz.inputs["Detail"].default_value = 10
    sl.new(tc_.outputs["Object"], nz.inputs["Vector"])
    bp = sn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.0004
    sl.new(nz.outputs[0], bp.inputs["Height"]); sl.new(bp.outputs[0], sb.inputs["Normal"])
    for _ in range(int(rng.integers(3, 7))):                            # granite pebbles half sunk in the moss
        t = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0.35, 0.8)
        x, y = a * rr * math.cos(t), b * rr * math.sin(t)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=tuple(loc + [x, y, zs + 0.012 * (1 - rr ** 2)]))
        st = bpy.context.object
        for vtx in st.data.vertices:
            vtx.co *= rng.uniform(0.85, 1.12)
        sz = rng.uniform(0.007, 0.016)
        st.scale = (sz * rng.uniform(1, 1.6), sz, sz * rng.uniform(0.5, 0.8)); st.rotation_euler = (0, 0, rng.uniform(0, 6.3))
        bpy.ops.object.shade_smooth()
        st.data.materials.append(stone); objs.append(st)
    return objs, zs


def build(seed, loc=(0, 0, 0), pot_r=None, pot_h=None):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    objs, zs = table_and_pot(loc, rng)
    zs -= loc[2]
    # ---- the wood skeleton (local coordinates; loc added at the end)
    H = rng.uniform(0.36, 0.5)
    base = np.array([rng.uniform(-0.05, 0.05), rng.uniform(-0.02, 0.02), zs - 0.03])   # the foot sunk in the soil
    lean = _unit(np.array([rng.normal(0, 0.45), rng.normal(0, 0.2), 1.0]))
    trunk = spine(base, lean, H, 70, rng, bends=rng.uniform(2.0, 3.2), amp=rng.uniform(1.0, 1.6))
    R0 = rng.uniform(0.04, 0.055)
    tt = np.linspace(0, 1, len(trunk))
    trad = R0 * (1 - 0.8 * tt ** 0.7) * (1 + 0.18 * np.exp(-tt / 0.05))  # (a steep flare read as a stepped skirt: the roots make the base)
    jin = rng.random() < 0.6
    spines = [("trunk", trunk, trad, False)]
    n_rt = int(rng.integers(5, 8))
    for j in range(n_rt):                                                # nebari: buttress roots from up the trunk, spreading into the soil
        az = 2 * math.pi * j / n_rt + rng.normal(0, 0.3)
        k0 = int(rng.uniform(0.03, 0.07) * (len(trunk) - 1))
        rp = spine(trunk[k0], [math.cos(az), math.sin(az), -0.3], rng.uniform(0.1, 0.17), 18, rng, amp=0.4, droop=0.5)
        rr_ = R0 * rng.uniform(0.6, 0.8) * np.linspace(1, 0.12, len(rp)) ** 0.8          # (thin + fast taper read as fins)
        surf = zs + 0.012 * (1 - (rp[:, 0] / 0.24) ** 2 - (rp[:, 1] / 0.17) ** 2).clip(0, 1)   # the moss surface (its dome)
        rp[:, 2] = np.minimum(rp[:, 2], np.maximum(surf - 0.45 * rr_, rp[:, 2] - 0.0))     # half buried: running over the surface
        rp[:, 2] = np.maximum(rp[:, 2], surf - 0.45 * rr_)
        spines.append(("root", rp, rr_, False))
    # main branches: level, alternating, longer low down; forks -> twigs -> foliage clusters on the tips
    twig_tubes, clusters = [], []
    n_br = int(rng.integers(6, 10))
    hs = np.sort(rng.uniform(0.38, 0.86, n_br))
    az = rng.uniform(0, 2 * math.pi)
    placed_tips = np.zeros((0, 3))
    for i, h in enumerate(hs):
        k = int(h * (len(trunk) - 1))
        for attempt in range(30):
            az_i = az + i * math.radians(rng.uniform(115, 165)) + rng.normal(0, 0.2 + 0.05 * attempt)
            out = np.array([math.cos(az_i), math.sin(az_i), 0.0])
            blen = (0.08 + 0.2 * (1 - h)) * rng.uniform(0.85, 1.15)
            dead = rng.random() < 0.12
            bp_ = spine(trunk[k], out + [0, 0, rng.uniform(-0.25, 0.05)], blen * (0.5 if dead else 1), 18, rng, amp=0.7,
                        droop=0.25, up=0.35, horiz=True)
            if dead:
                break
            # ramification: secondaries off the outer 55 %, tertiaries off those; the tips fan out in the horizontal plane
            tips, tw_ = [], []
            for s_ in np.linspace(0.45, 1.0, int(rng.integers(3, 5))):
                p0 = bp_[int(s_ * (len(bp_) - 1))]
                d0 = _unit(bp_[-1] - bp_[0])
                for _ in range(int(rng.integers(1, 3))):
                    ang = rng.uniform(-1.0, 1.0)
                    d2 = _unit(np.array([d0[0] * math.cos(ang) - d0[1] * math.sin(ang), d0[0] * math.sin(ang) + d0[1] * math.cos(ang), 0.05]))
                    sp2 = spine(p0, d2, rng.uniform(0.03, 0.06), 6, rng, amp=0.6, up=0.4, horiz=True)
                    tw_.append((sp2, np.linspace(0.0035, 0.0018, len(sp2))))
                    for _ in range(int(rng.integers(2, 4))):
                        ang3 = ang + rng.uniform(-0.9, 0.9)
                        d3 = _unit(np.array([d0[0] * math.cos(ang3) - d0[1] * math.sin(ang3), d0[0] * math.sin(ang3) + d0[1] * math.cos(ang3), 0.15]))
                        sp3 = spine(sp2[-1], d3, rng.uniform(0.02, 0.04), 5, rng, amp=0.6, up=0.5, horiz=True)
                        tw_.append((sp3, np.linspace(0.0018, 0.0009, len(sp3))))
                        tips.append(sp3[-1])
            tips = np.array(tips)
            # apart from other branches' foliage (pads don't merge into a blob) and off the trunk
            dd = np.linalg.norm((tips[:, None] - placed_tips[None]) * [1, 1, 2.6], axis=2).min() if len(placed_tips) else 1
            dt = np.linalg.norm((tips[:, None] - trunk[None])[..., :2], axis=2)
            near = np.abs(tips[:, None, 2] - trunk[None, :, 2]) < 0.05
            dtr = np.where(near, dt, 1).min() if near.any() else 1
            if dd > 0.06 and dtr > 0.03:
                break
        rb = np.linspace(trad[k] * 0.5, 0.0045 if not dead else 0.0008, len(bp_))
        spines.append(("dead" if dead else "branch", bp_, rb, dead))
        if dead:
            continue
        twig_tubes += tw_
        placed_tips = np.concatenate([placed_tips, tips])
        clusters += [(t_, rng.uniform(0.036, 0.052)) for t_ in tips]           # (0.026-0.04 left the pads gappy with real shoots)
    # the crown: the trunk's top splits into short twigs (a jin carries on above them on some trees)
    top_k = int((0.88 if jin else 0.97) * (len(trunk) - 1))
    for _ in range(int(rng.integers(7, 12))):
        a3 = rng.uniform(0, 2 * math.pi)
        sp3 = spine(trunk[top_k], [math.cos(a3), math.sin(a3), rng.uniform(0.2, 0.9)], rng.uniform(0.03, 0.07), 6, rng, amp=0.5, up=0.3)
        twig_tubes.append((sp3, np.linspace(0.004, 0.001, len(sp3))))
        rc_ = rng.uniform(0.04, 0.054)
        dtk = np.linalg.norm(trunk[:top_k] - sp3[-1], axis=1) - trad[:top_k]
        if dtk.min() < rc_ * 0.8:                                    # (crown clusters brushed the trunk)
            continue
        clusters.append((sp3[-1], rc_))
    # ---- fuse the thick wood: tubes -> one voxel-remeshed body
    allV, allF = [], []
    off = 0
    for name, sp, rr, dead in spines:
        V_, F_ = closed_tube(sp, np.maximum(rr, 0.0022), sides=20)
        allV.append(V_); allF += [[i + off for i in f] for f in F_]; off += len(V_)
    raw = _obj("wood_raw", np.concatenate(allV), allF, None)
    rm = raw.modifiers.new("fuse", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0016; rm.adaptivity = 0.0
    sm = raw.modifiers.new("sm", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(raw.evaluated_get(dg))
    bpy.data.objects.remove(raw)
    # ---- carve: per vertex, its nearest spine sample -> the angle round it, the height along it
    nV = len(me.vertices)
    P = np.empty(nV * 3, np.float32); me.vertices.foreach_get("co", P); P = P.reshape(-1, 3).astype(np.float64)
    Nn = np.empty(nV * 3, np.float32); me.vertices.foreach_get("normal", Nn); Nn = Nn.reshape(-1, 3).astype(np.float64)
    SP, SA1, SA2, SR, SS, SI, SD, SL = [], [], [], [], [], [], [], []
    for si, (name, sp, rr, dead) in enumerate(spines):
        T_, A1_, A2_ = frames(sp)
        ln = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(sp, axis=0), axis=1))])
        SP.append(sp); SA1.append(A1_); SA2.append(A2_); SR.append(rr); SS.append(np.linspace(0, 1, len(sp)))
        SI.append(np.full(len(sp), si)); SD.append(np.full(len(sp), 1.0 if dead else 0.0)); SL.append(ln)
    SP, SA1, SA2, SR, SS, SI, SD, SL = map(np.concatenate, (SP, SA1, SA2, SR, SS, SI, SD, SL))
    near = np.empty(nV, int)
    for c0 in range(0, nV, 20000):
        d = np.linalg.norm(P[c0:c0 + 20000, None] - SP[None], axis=2) / (SR[None] + 0.004)
        near[c0:c0 + 20000] = d.argmin(1)
    # the roots take their frame from the trunk's base (one continuous bark mapping: a ring seam where they met)
    is_root = np.isin(SI[near], [i for i, sp_ in enumerate(spines) if sp_[0] == "root"])
    nt_ = len(spines[0][1])
    if is_root.any():
        dtr = np.linalg.norm(P[is_root, None] - SP[None, :nt_], axis=2)
        near[is_root] = dtr.argmin(1)
    rel = P - SP[near]
    ang = np.arctan2((rel * SA2[near]).sum(1), (rel * SA1[near]).sum(1))
    s = SS[near]; r = SR[near]; idx = SI[near]; ln = SL[near]
    # the nearest spine *sample* steps along a branch (zig-zag bands in the bark): smooth the fields over the surface first
    E = np.empty(len(me.edges) * 2, int); me.edges.foreach_get("vertices", E); E = E.reshape(-1, 2)
    deg = np.bincount(E.ravel(), minlength=nV).astype(float) + 1e-9

    def lap(x, it):
        for _ in range(it):
            acc = np.zeros(nV); np.add.at(acc, E[:, 0], x[E[:, 1]]); np.add.at(acc, E[:, 1], x[E[:, 0]])
            x = 0.5 * x + 0.5 * acc / deg
        return x
    s, ln, r = lap(s, 12), lap(ln, 12), lap(r, 6)
    ang = np.arctan2(lap(np.sin(ang), 4), lap(np.cos(ang), 4))
    is_trunk = idx == 0
    sh_w = rng.uniform(0.36, 0.5); sh_turn = rng.uniform(0.7, 1.5) * rng.choice([-1, 1]); sh0 = rng.uniform(0, 2 * math.pi)
    twist = sh_turn * 2 * math.pi
    c = sh0 + twist * s
    band = (np.cos(ang - c) + 1) / 2
    w = sh_w * (0.75 + 0.5 * s)
    dead = np.where(is_trunk, 1 / (1 + np.exp(-(band - (1 - w)) * 30)) * (s > 0.03), 0.0)
    if jin:
        dead = np.where(is_trunk & (s > 0.88), np.maximum(dead, np.clip((s - 0.88) / 0.03, 0, 1)), dead)
    dead = np.maximum(dead, SD[near])
    lip = np.exp(-((band - (1 - w)) / 0.05) ** 2) * is_trunk * (s > 0.03)   # the live vein's swollen edge along the shari
    nr_ = np.clip(np.round(2 * math.pi * r / 0.014), 3, 11)
    twist = np.where(is_trunk, twist, twist * 0.15)                    # the spiral is the trunk's (branches spiralled: stripes across)
    ridges = np.sin(nr_ * ang + twist * s * 0.9 + 0.8 * wavenoise(P, rng, 40)) * 0.5 + 0.5
    grain = np.sin(2 * nr_ * ang + twist * s + 1.5 * wavenoise(P, rng, 60))
    knots = wavenoise(P, rng, 28)
    disp = r * (0.13 * ridges + 0.1 * knots - 0.26 * dead + 0.07 * grain * dead + 0.16 * lip)      # (0.07/0.06/0.16 read smooth)
    disp *= np.where(is_trunk, 1.0, np.where(is_root, 0.8, 0.3))       # (branches at 0.55 read corrugated)
    disp, dead = lap(disp, 6), lap(dead, 3)                            # (where neighbours took different spines it stepped)
    P2 = P + Nn * disp[:, None]
    me.vertices.foreach_set("co", P2.astype(np.float32).ravel())
    # UVs: round the nearest spine, twisted with the ridges (the bark strips follow the fibres)
    uscale, vscale = 0.13, 0.3                                       # the bark image's strips are long: one tile ~22 cm along (6 cm read as bricks)
    U = ((ang + twist * s * 0.9) % (2 * math.pi)) * np.maximum(r, 0.004) / uscale
    Vv = ln / vscale
    if is_root.any():                                                 # the roots: strips running out along them (not stretched round)
        hd = np.linalg.norm(rel[is_root][:, :2], axis=1)
        Vv[is_root] = -np.maximum(hd - trad[0] * 0.9, 0) / vscale * 1.5      # 0 where the root leaves the flare: no ring
    Vv = lap(Vv, 6)
    me.uv_layers.new(name="UVMap")
    lv = np.empty(len(me.loops), int); me.loops.foreach_get("vertex_index", lv)
    lu, lvv = U[lv].copy(), Vv[lv]
    period = (2 * math.pi) * np.maximum(r, 0.004)[lv] / uscale
    starts = np.empty(len(me.polygons), int); me.polygons.foreach_get("loop_start", starts)
    first = np.repeat(lu[starts], np.diff(np.append(starts, len(lu))))           # each loop's face's first corner
    lu = np.where(lu - first > period / 2, lu - period, np.where(first - lu > period / 2, lu + period, lu))   # no seam smear
    me.uv_layers[0].data.foreach_set("uv", np.stack([lu, lvv], 1).astype(np.float32).ravel())
    at = me.attributes.new("dead", "FLOAT", "POINT"); at.data.foreach_set("value", dead.astype(np.float32))
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
    wood = bpy.data.objects.new(f"bonsai_{seed}_wood", me); bpy.context.scene.collection.objects.link(wood)
    wood.data.materials.append(wood_material()); wood.location = loc
    objs.append(wood)
    # ---- the fine twigs (too thin for the voxels)
    tv, tf, tu = [], [], []
    off = 0
    for sp, rr in twig_tubes:
        V_, F_, UV_ = tube(sp, rr, sides=6, uscale=0.03)
        tv.append(V_); tf += [[i + off for i in f] for f in F_]; tu += UV_; off += len(V_)
    if tv:
        objs.append(_obj(f"bonsai_{seed}_twigs", np.concatenate(tv) + loc, tf, wood_material(), tu, {"dead": np.zeros(off)}))
    # ---- foliage, v4 (Roman: "the leaves look like a classic particle scatter", "way too just 2D cards"): real 3D geometry
    # grown like the plant, from the real close-up (out/compare_bonsai_foliage): every twig tip sends out shoots fanning outward;
    # each shoot is a brown stem whose upper part is clothed in round, cord-like scale shoots branching off it all round
    # (phyllotaxis 137.5 deg: a 3D tuft, not a flat spray), each cord tapering to a rounded paler tip. Colours measured on the
    # generated Shimpaku shoot photos (work/bonsai_gen/shoot*): sage / grey-blue green, paler fresh tips.
    fol = foliage_3d(clusters, trunk, rng)
    objs.append(_obj(f"bonsai_{seed}_foliage", fol[0] + loc, fol[1], foliage_material(), fol[2], {"shade": fol[3]}, colors=fol[4]))
    objs[-1]["tree"] = 1
    for o in objs:
        if o.name.startswith((f"bonsai_{seed}_wood", f"bonsai_{seed}_twigs")):
            o["tree"] = 1
    n_cards = len(fol[1])
    print(f"bonsai {seed}: trunk {H:.2f} m (base r {R0 * 100:.1f} cm), {len(spines)} wood spines fused into {len(me.polygons)} faces, "
          f"{len(twig_tubes)} twigs, {len(clusters)} foliage clusters, {n_cards} foliage faces, jin {jin}")
    return objs

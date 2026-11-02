"""Juniper bonsai (Juniperus chinensis 'Shimpaku') generator: one seed = one tree (plants/GOAL.md; Roman: "we can do mini trees
almost like bonsais too"). From the references (out/refs_bonsai_v001.jpg):
- an informal upright trunk 0.35-0.55 m, two or three S-bends, a flared base (nebari) with surface roots, tapering hard
- live veins of reddish fibrous bark spiralling round bleached silver deadwood (shari) that twists up the trunk; a dead
  apex (jin) on some trees, a few dead branch stubs
- 5-9 branches, roughly level, alternating, each ending in a dense rounded foliage pad (a cloud), plus the apex pad
- foliage: cards of real-looking sprig images (maps/bonsai, build_leaf_atlas.py bonsai), 60-140 per pad on the pad's dome;
  pads never overlap each other or the trunk
- a shallow unglazed brown tray, the soil covered in cushion moss (the ambientCG moss scan), on an oak display plinth

    import gen_bonsai; objs = gen_bonsai.build(seed, (x, y, z_floor))
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
MAPS = HERE / "maps" / "bonsai"
MOSS = Path.home() / ".cache" / "the_gym" / "textures" / "ambientcg" / "Moss004"
PLINTH = 0.62
FRAME = {"pot_scale": 0, "hero": ((0.45, -1.25, 1.05), (0, 0, 0.9), 45), "close": ((0.25, -0.75, 1.05), (0.0, 0, 0.95), 45),
         "trio": ((0, -4.2, 1.25), (0, 0, 0.9), 36), "spacing": 1.15}


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


def _obj(name, V, F, mat, uv=None, attrs=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.asarray(V).tolist(), [], F)
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


# ------------------------------------------------------------------------------------------------------------ materials
_M = {}


def _img(path, color=True):
    im = bpy.data.images.load(str(path), check_existing=True)
    if not color:
        im.colorspace_settings.name = "Non-Color"
    return im


def wood_material():
    """bark (live vein) and deadwood mixed by the 'dead' attribute; both from the generated images, box-free UVs on the
    tubes (u around, v along); the deadwood smoother and paler, the bark fibrous (relief from the image)"""
    if "wood" in _M:
        return _M["wood"]
    m = bpy.data.materials.new("bonsai_wood"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    uv = N.new("ShaderNodeUVMap")
    bark = N.new("ShaderNodeTexImage"); bark.image = _img(MAPS / "bark.jpg"); bark.extension = "MIRROR"
    dead = N.new("ShaderNodeTexImage"); dead.image = _img(MAPS / "deadwood.jpg"); dead.extension = "MIRROR"
    for t in (bark, dead):
        L.new(uv.outputs[0], t.inputs["Vector"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "dead"
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(at.outputs["Fac"], mx.inputs[0]); L.new(bark.outputs[0], mx.inputs[6]); L.new(dead.outputs[0], mx.inputs[7])
    g = N.new("ShaderNodeRGBToBW"); L.new(mx.outputs[2], g.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9; bp.inputs["Distance"].default_value = 0.0025
    L.new(g.outputs[0], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(mx.outputs[2], pb.inputs["Base Color"])
    r = N.new("ShaderNodeMath"); r.operation = "MULTIPLY_ADD"; r.inputs[1].default_value = -0.15; r.inputs[2].default_value = 0.85
    L.new(at.outputs["Fac"], r.inputs[0]); L.new(r.outputs[0], pb.inputs["Roughness"])
    pb.inputs["Specular IOR Level"].default_value = 0.3
    L.new(bp.outputs[0], pb.inputs["Normal"])
    L.new(pb.outputs[0], out.inputs["Surface"])
    _M["wood"] = m
    return m


def sprig_material(name):
    """a sprig card: the image, cut out; matte-satin scales, light through them, a little colour drift per pad"""
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    col = N.new("ShaderNodeTexImage"); col.image = _img(MAPS / f"{name}_col.png")
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "shade"
    hs = N.new("ShaderNodeHueSaturation"); L.new(col.outputs["Color"], hs.inputs["Color"])
    L.new(at.outputs["Fac"], hs.inputs["Value"])                     # inner cards darker (self-shadowed pad)
    at2 = N.new("ShaderNodeAttribute"); at2.attribute_name = "hue"
    L.new(at2.outputs["Fac"], hs.inputs["Hue"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(hs.outputs[0], pb.inputs["Base Color"])
    pb.inputs["Roughness"].default_value = 0.55; pb.inputs["Specular IOR Level"].default_value = 0.3
    tr = N.new("ShaderNodeBsdfTranslucent")
    tc = N.new("ShaderNodeHueSaturation"); tc.inputs["Value"].default_value = 1.4
    L.new(hs.outputs[0], tc.inputs["Color"]); L.new(tc.outputs[0], tr.inputs["Color"])
    sm = N.new("ShaderNodeMixShader"); sm.inputs[0].default_value = 0.2
    L.new(pb.outputs[0], sm.inputs[1]); L.new(tr.outputs[0], sm.inputs[2])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(col.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(sm.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    _M[name] = m
    return m


def simple(name, rgb, rough, tex=None, scale=1.0, bump=0.0, val=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    if tex:
        tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        t = N.new("ShaderNodeTexImage"); t.image = _img(tex["diff"]); L.new(mp.outputs[0], t.inputs["Vector"])
        hv = N.new("ShaderNodeHueSaturation"); hv.inputs["Value"].default_value = val
        L.new(t.outputs[0], hv.inputs["Color"]); L.new(hv.outputs[0], b.inputs["Base Color"])
        if "nor" in tex:
            n_ = N.new("ShaderNodeTexImage"); n_.image = _img(tex["nor"], False); L.new(mp.outputs[0], n_.inputs["Vector"])
            nm = N.new("ShaderNodeNormalMap"); L.new(n_.outputs[0], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    else:
        b.inputs["Base Color"].default_value = (*rgb, 1)
        if bump:
            nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 160; nz.inputs["Detail"].default_value = 8
            bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.0008
            L.new(nz.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def clay():
    """unglazed bonsai tray clay: dark red-brown, mottled, matte, a fine sandy grain"""
    m = bpy.data.materials.new("tray_clay"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.88; b.inputs["Specular IOR Level"].default_value = 0.25
    tc = N.new("ShaderNodeTexCoord")
    mo = N.new("ShaderNodeTexNoise"); mo.inputs["Scale"].default_value = 18; mo.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], mo.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); L.new(mo.outputs[0], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (0.09, 0.045, 0.032, 1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (0.16, 0.085, 0.055, 1)
    L.new(cr.outputs[0], b.inputs["Base Color"])
    gr = N.new("ShaderNodeTexNoise"); gr.inputs["Scale"].default_value = 900; gr.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], gr.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.0004
    L.new(gr.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------------------------------------------------ geometry
def tube(pts, radii, dead=None, sides=18, twist0=0.0, uscale=0.07, fl=0.0):
    """a wood tube: u around (scaled to ~real texture size), v along; per-vertex 'dead' from dead(t, angle)"""
    V, F, UV, D = [], [], [], []
    n = len(pts)
    ref = np.array([0, 0, 1.0])
    a1 = None
    vlen = 0.0
    for k in range(n):
        d = _unit(pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)])
        if a1 is None:
            a1 = _unit(np.cross(d, [1.0, 0.3, 0]))
        a1 = _unit(a1 - d * (a1 @ d))                                    # parallel transport: no flips
        a2 = np.cross(d, a1)
        if k:
            vlen += np.linalg.norm(pts[k] - pts[k - 1])
        for j in range(sides + 1):
            t = 2 * math.pi * j / sides
            dd = dead(k / (n - 1), t) if dead else 0.0
            flute = 1 + fl * (0.6 * math.sin(7 * t + 9 * k / n) + 0.4 * math.sin(13 * t - 5 * k / n + 1.3))
            r = radii[k] * (1 - 0.07 * dd) * flute                       # deadwood sunk below the live vein; fibrous ridges
            V.append(pts[k] + (a1 * math.cos(t) + a2 * math.sin(t)) * r)
            UV.append((j / sides * 2 * math.pi * max(radii[k], 0.004) / uscale, vlen / uscale))
            D.append(dd)
    R = sides + 1
    for k in range(n - 1):
        for j in range(sides):
            F.append([k * R + j, k * R + j + 1, (k + 1) * R + j + 1, (k + 1) * R + j])
    F.append([(n - 1) * R + j for j in range(sides)])
    return np.array(V), F, UV, D


def spine(p0, d0, length, n, rng, bends=2.0, amp=0.25, droop=0.0, up=0.0):
    """a gently S-bending curve"""
    pts = [np.array(p0, float)]
    d = _unit(np.array(d0, float))
    ph = rng.uniform(0, 2 * math.pi, 2)
    side = _unit(np.cross(d, [0.3, 0.2, 1.0]))
    other = np.cross(d, side)
    for k in range(n):
        t = (k + 1) / n
        bend = amp * (side * math.sin(ph[0] + bends * math.pi * t) + 0.6 * other * math.cos(ph[1] + bends * math.pi * t))
        d = _unit(d + bend * (2.0 / n) + np.array([0, 0, -droop + up * t]) * (1.0 / n))
        pts.append(pts[-1] + d * length / n)
    return np.array(pts)


def build(seed, loc=(0, 0, 0), pot_r=None, pot_h=None):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    objs = []
    # --- the plinth, the tray, the moss
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(loc + [0, 0, PLINTH / 2]))
    pl = bpy.context.object; pl.scale = (0.62, 0.46, PLINTH)
    bv = pl.modifiers.new("bv", "BEVEL"); bv.width = 0.004; bv.segments = 2
    pl.data.materials.append(simple("oak_plinth", (0.30, 0.20, 0.12), 0.5, bump=0.05)); objs.append(pl)
    tw, td, th = rng.uniform(0.42, 0.5), rng.uniform(0.3, 0.34), rng.uniform(0.065, 0.085)
    z0 = loc[2] + PLINTH
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(loc + [0, 0, PLINTH + 0.008 + th / 2]))
    tray = bpy.context.object; tray.scale = (tw, td, th)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # (scaled object coords stretched the clay into wood grain)
    bv = tray.modifiers.new("bv", "BEVEL"); bv.width = 0.012; bv.segments = 4
    sol = bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(loc + [0, 0, PLINTH + 0.008 + th - 0.006]))
    inner = bpy.context.object; inner.scale = (tw - 0.024, td - 0.024, 0.04)
    bo = tray.modifiers.new("hollow", "BOOLEAN"); bo.object = inner; bo.operation = "DIFFERENCE"
    bpy.context.view_layer.objects.active = tray
    for md in list(tray.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(inner)
    tray.data.materials.clear()                                          # (the boolean left an empty slot: it rendered white)
    tray.data.materials.append(clay()); objs.append(tray)
    for sx in (-1, 1):                                                   # the feet
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(loc + [sx * (tw / 2 - 0.04), sy * (td / 2 - 0.035), PLINTH + 0.004]))
            f_ = bpy.context.object; f_.scale = (0.045, 0.03, 0.008); f_.data.materials.append(tray.data.materials[0]); objs.append(f_)
    zs = PLINTH + 0.008 + th - 0.012                                     # the soil surface
    moss = simple("moss_soil", None, 1.0, tex={"diff": MOSS / "diff.png", "nor": MOSS / "nor_gl.png"}, scale=8.0, val=0.8)
    g = np.linspace(-1, 1, 70)
    gx, gy = np.meshgrid(g, g)
    hx, hy = gx * (tw / 2 - 0.016), gy * (td / 2 - 0.016)
    cush = sum(rng.uniform(0.004, 0.009) * np.exp(-((hx - cx_) ** 2 + (hy - cy_) ** 2) / rng.uniform(0.02, 0.05) ** 2)
               for cx_, cy_ in rng.uniform([-tw / 2, -td / 2], [tw / 2, td / 2], (40, 2)))               # moss cushions
    edge = np.clip(np.minimum(1 - np.abs(gx), 1 - np.abs(gy)) / 0.15, 0, 1)            # down to the rim at the walls
    mound = (0.018 * np.exp(-(hx ** 2 / (tw * 0.3) ** 2 + hy ** 2 / (td * 0.35) ** 2)) + cush) * edge
    MV = np.stack([hx.ravel(), hy.ravel(), (zs + mound).ravel()], 1) + [loc[0], loc[1], loc[2]]
    MF = [[j * 70 + i, j * 70 + i + 1, (j + 1) * 70 + i + 1, (j + 1) * 70 + i] for j in range(69) for i in range(69)]
    objs.append(_obj("moss_bed", MV, MF, moss))
    for _ in range(int(rng.integers(2, 5))):                              # a few small stones in the moss
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1,
                                              location=tuple(loc + [rng.uniform(-tw / 3, tw / 3), rng.uniform(-td / 3, td / 3), zs + 0.008]))
        st = bpy.context.object; st.scale = (rng.uniform(0.012, 0.03), rng.uniform(0.01, 0.022), rng.uniform(0.006, 0.012))
        st.data.materials.append(simple("stone", (0.32, 0.31, 0.3), 0.7, bump=0.3)); objs.append(st)
    # --- the trunk: informal upright, S-bends, nebari, shari spiralling up
    H = rng.uniform(0.32, 0.5)
    base = np.array([rng.uniform(-0.04, 0.04), rng.uniform(-0.03, 0.03), zs - 0.01])
    lean = _unit(np.array([rng.normal(0, 0.35), rng.normal(0, 0.2), 1.0]))
    tr = spine(base, lean, H, 60, rng, bends=rng.uniform(1.5, 3.0), amp=rng.uniform(0.6, 1.2))
    R0 = rng.uniform(0.032, 0.045)
    t = np.linspace(0, 1, len(tr))
    rad = R0 * (1 - 0.72 * t ** 0.8) * (1 + 0.6 * np.exp(-t / 0.04))     # hard taper; the flare at the base
    sh_w = rng.uniform(0.25, 0.45); sh_turn = rng.uniform(0.6, 1.4) * rng.choice([-1, 1]); sh0 = rng.uniform(0, 2 * math.pi)
    jin = rng.random() < 0.55

    def trunk_dead(tt, ang):
        c = sh0 + sh_turn * 2 * math.pi * tt
        dd = (math.cos(ang - c) + 1) / 2
        w = sh_w * (0.7 + 0.6 * tt)
        v = 1 / (1 + math.exp(-(dd - (1 - w)) * 40))
        if jin and tt > 0.88:
            v = 1.0
        return v * (tt > 0.04)
    V, F, UV, D = tube(tr, rad, trunk_dead, sides=48, fl=0.07)
    wood = wood_material()
    parts = [(V, F, UV, D)]
    for _ in range(int(rng.integers(3, 6))):                              # surface roots
        az = rng.uniform(0, 2 * math.pi)
        rp = spine(base + [0, 0, 0.012], [math.cos(az), math.sin(az), -0.15], rng.uniform(0.06, 0.12), 14, rng, amp=0.4, droop=0.3)
        rp[:, 2] = np.maximum(rp[:, 2], zs - 0.004)
        parts.append(tube(rp, np.linspace(R0 * 0.55, R0 * 0.12, len(rp)), None, sides=10))
    # --- branches + pads (pads kept apart: spheres of their half-width, retries)
    pads = []
    trunk_pts = tr
    n_br = int(rng.integers(7, 12))
    hs = np.sort(rng.uniform(0.35, 0.9, n_br))
    az = rng.uniform(0, 2 * math.pi)
    for i, h in enumerate(hs):
        k = int(h * (len(tr) - 1))
        for attempt in range(25):
            az_i = az + i * math.radians(rng.uniform(110, 160)) + rng.normal(0, 0.25 + 0.06 * attempt)
            out = np.array([math.cos(az_i), math.sin(az_i), 0.0])
            blen = (0.09 + 0.17 * (1 - h)) * rng.uniform(0.8, 1.2)
            bp_ = spine(tr[k], out + [0, 0, rng.uniform(-0.15, 0.15)], blen, 16, rng, amp=0.5, droop=0.15, up=0.4)
            c = bp_[-1] + np.array([0, 0, 0.012])
            pw = (0.065 + 0.09 * (1 - h)) * rng.uniform(0.85, 1.15)
            ok = all(np.linalg.norm((c - q[0]) * [1, 1, 3.0]) > (pw + q[1]) * 0.62 for q in pads)
            ok &= np.min(np.linalg.norm((trunk_pts - c)[:, :2], axis=1) + 10 * (np.abs(trunk_pts[:, 2] - c[2]) > pw * 0.4)) > pw * 0.55
            if ok:
                break
        if not ok:
            continue
        rb = np.linspace(rad[k] * 0.45, 0.003, len(bp_))
        dead_br = rng.random() < 0.1
        if dead_br:                                                     # a jin: short, bleached, reaching up a little
            bp_ = bp_[: len(bp_) // 2] + np.linspace(0, 1, len(bp_) // 2)[:, None] * [0, 0, 0.03]
            rb = np.linspace(rad[k] * 0.4, 0.0006, len(bp_)) ** 1.0           # tapering to a point, not a pipe
        parts.append(tube(bp_, rb, (lambda tt, a, dd=dead_br: 1.0 if dd else 0.0), sides=10))
        if dead_br:                                                      # a jin: a dead stub, no pad
            continue
        pads.append((c, pw))
    apex = tr[-1] if not jin else tr[int(0.9 * (len(tr) - 1))]
    pads.append((apex + np.array([0, 0, 0.02]), 0.09 * rng.uniform(0.9, 1.2)))
    allV, allF, allUV, allD = [], [], [], []
    off = 0
    for V_, F_, UV_, D_ in parts:
        allV.append(V_); allF += [[i + off for i in f] for f in F_]; allUV += UV_; allD += list(D_) if len(D_) else [0.0] * len(V_)
        off += len(V_)
    objs.append(_obj(f"bonsai_{seed}_wood", np.concatenate(allV) + [loc[0], loc[1], loc[2]], allF, wood, allUV, {"dead": allD}))
    # --- the foliage pads: sprig cards on a flattened dome, facing out + up
    atlas = json.loads((MAPS / "atlas.json").read_text())
    tips = [n for n in atlas if n.startswith("tip") and n != "tip2"] if rng.random() < 0.7 else ["tip2", "tip2", "tip4"]
    fill = [n for n in atlas if n.startswith("sprig") and n != "sprig2"]
    names = tips + fill
    by = {n: ([], [], [], [], []) for n in names}
    hue0 = rng.uniform(-0.01, 0.01)
    for c, pw in pads:
        # a pad: a wide flat cloud (refs: flat-topped, layered, feathery edges): sprays lying near-horizontal in 4-6 layers
        # inside a flattened ellipsoid, fanning outward; the lower layers darker (self-shadowed)
        ph_ = pw * rng.uniform(0.28, 0.4)
        sq = rng.uniform(0.75, 1.0)
        hue = 0.5 + hue0 + rng.normal(0, 0.008)
        n_cards = int(600 + 46000 * pw * pw)
        # (v5 pads were perfect discs, "flying saucers"): each pad 2-4 overlapping sub-clouds, a wobbly outline
        subs = [(np.zeros(3), 1.0)] + [(np.array([*(rng.normal(0, 0.42, 2) * pw), rng.normal(0, 0.15) * ph_]), rng.uniform(0.5, 0.78))
                                     for _ in range(int(rng.integers(1, 4)))]
        wob = rng.uniform(0, 2 * math.pi, 3)
        for _ in range(n_cards):
            so, sr = subs[int(rng.integers(len(subs)))]
            r_ = math.sqrt(rng.uniform(0, 1)) ** 0.8
            th_ = rng.uniform(0, 2 * math.pi)
            r_ *= 1 + 0.18 * math.sin(2 * th_ + wob[0]) + 0.1 * math.sin(3 * th_ + wob[1]) + 0.06 * math.sin(5 * th_ + wob[2])
            zc = rng.uniform(-1, 1)
            zmax = math.sqrt(max(1 - min(r_, 1) ** 2, 0.0)) ** 0.7       # the dome: flat top, rounded edge
            p = c + so + np.array([r_ * pw * sr * math.cos(th_), r_ * pw * sr * sq * math.sin(th_), zc * zmax * ph_ * (0.7 + 0.3 * sr)])
            outw = np.array([math.cos(th_), math.sin(th_), 0.0])
            tilt = rng.normal(0, 0.18) + 0.35 * r_ * (zc < 0)              # near-horizontal; edge sprays droop a little
            facing = _unit(np.array([0, 0, 1.0]) + outw * (0.25 * r_ - tilt) + rng.normal(0, 0.12, 3))
            inner = r_ < 0.75 and abs(zc) < 0.6 and rng.random() < 0.35      # dense clusters deep inside: no see-through pad
            name = fill[int(rng.integers(len(fill)))] if inner else tips[int(rng.integers(len(tips)))]
            sz = rng.uniform(0.03, 0.05) if inner else rng.uniform(0.022, 0.04)
            asp = atlas[name]["aspect"]
            ay = _unit(outw + rng.normal(0, 0.45, 3)); ay = _unit(ay - facing * (ay @ facing))   # the spray points outward
            ax = np.cross(ay, facing)
            hw, hh = sz * asp / 2, sz / 2
            q = [p - ax * hw - ay * hh * 0.2, p + ax * hw - ay * hh * 0.2, p + ax * hw + ay * hh * 1.8, p - ax * hw + ay * hh * 1.8]
            V_, F_, UV_, S_, Hh = by[name]
            o_ = len(V_); V_ += q; F_.append([o_, o_ + 1, o_ + 2, o_ + 3]); UV_ += [(0, 0), (1, 0), (1, 1), (0, 1)]
            sh = 0.45 + 0.55 * ((zc * zmax + 1) / 2) ** 1.3 * (0.75 + 0.25 * r_)   # top + outside bright, under + inside dark
            S_ += [sh] * 4; Hh += [hue] * 4
    for name, (V_, F_, UV_, S_, Hh) in by.items():
        if F_:
            objs.append(_obj(f"bonsai_{seed}_{name}", np.array(V_) + loc, F_, sprig_material(name), UV_, {"shade": S_, "hue": Hh}, smooth=False))
    print(f"bonsai {seed}: trunk {H:.2f} m, {len(pads)} pads, {sum(len(v[1]) for v in by.values())} sprig cards, jin {jin}")
    return objs

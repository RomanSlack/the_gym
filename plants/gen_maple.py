"""Red Japanese maple bonsai (Acer palmatum) generator: one seed = one tree (Roman: "one more variation of a different type of
bonsai"). The opposite of the juniper (references: out/refs_maple_v001.jpg, maple_06 the red one, maple_01 the blue pot):
- a thick smooth grey trunk with a strong nebari (buttress roots spreading into the moss), splitting low into 3-4 leaders that
  fan up and out (the broom / informal upright of maple_05/06); trunk, roots, leaders and main branches voxel-fused into
  one body; the fine twigs as tubes
- a broad dome canopy: a real branch network out to ~600 twig tips on its shell, a cluster of 5-9 red palmate leaves on each
  (leaf photos generated from the references, cut out with their petioles: maps/maple), facing up and out, translucent
  (they glow against the sun)
- the bark: a 4K smooth grey maple bark photo texture (lenticels, silvery patches), box-projected at real scale
- an oval pot in a deep blue nami-namako glaze (4K glaze photo texture), the soil under cushion moss

    import gen_maple; objs = gen_maple.build(seed, (x, y, z_floor))
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np

import gen_bonsai as gb

HERE = Path(__file__).resolve().parent
MAPS = HERE / "maps" / "maple"
FRAME = {"pot_scale": 0, "auto": True, "hero": ((0.42, -1.2, 1.08), (0, 0, 0.93), 46), "close": ((0.2, -0.55, 0.98), (0, 0, 0.86), 45),
         "trio": ((0, -4.4, 1.35), (0, 0, 0.95), 36), "spacing": 1.25}
_unit = gb._unit
TABLE = gb.TABLE


def _tex(N, L, vec, name, color=True, blend=0.3):
    t = N.new("ShaderNodeTexImage"); t.image = gb._img(MAPS / name, color); t.projection = "BOX"; t.projection_blend = blend
    L.new(vec, t.inputs["Vector"]); return t


def bark_material():
    m = bpy.data.materials.new("maple_bark"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (10, 10, 10)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    c = _tex(N, L, mp.outputs[0], "bark4k_col.jpg"); h = _tex(N, L, mp.outputs[0], "bark4k_h.png", False)
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Value"].default_value = 0.8
    L.new(c.outputs[0], hs.inputs["Color"]); L.new(hs.outputs[0], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.0008
    L.new(h.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.78; b.inputs["Specular IOR Level"].default_value = 0.25
    return m


def glaze_material():
    """the glazed pot: the glaze photo box-projected (one image per face), glossy with a little variation in the gloss"""
    m = bpy.data.materials.new("pot_glaze"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.8, 1.8, 1.8)
    mp.inputs["Location"].default_value = (0.5, 0.5, 0.0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    c = _tex(N, L, mp.outputs[0], "glaze4k_col.jpg"); h = _tex(N, L, mp.outputs[0], "glaze4k_h.png", False)
    L.new(c.outputs[0], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.08; rr.inputs["To Max"].default_value = 0.22
    L.new(h.outputs[0], rr.inputs["Value"]); L.new(rr.outputs[0], b.inputs["Roughness"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.0003
    L.new(h.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    return m


def leaf_material(name):
    """a leaf: its image (cut out), a per-leaf hue / value drift, satin on top, light through it (the glow when backlit)"""
    m = bpy.data.materials.new(f"maple_{name}"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    uv = N.new("ShaderNodeUVMap")
    c = N.new("ShaderNodeTexImage"); c.image = gb._img(MAPS / f"{name}_col.png"); L.new(uv.outputs[0], c.inputs["Vector"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "var"
    hs = N.new("ShaderNodeHueSaturation"); L.new(c.outputs["Color"], hs.inputs["Color"])
    mh = N.new("ShaderNodeMath"); mh.operation = "MULTIPLY_ADD"; mh.inputs[1].default_value = 0.03; mh.inputs[2].default_value = 0.485
    L.new(at.outputs["Fac"], mh.inputs[0]); L.new(mh.outputs[0], hs.inputs["Hue"])
    mv = N.new("ShaderNodeMath"); mv.operation = "MULTIPLY_ADD"; mv.inputs[1].default_value = 0.3; mv.inputs[2].default_value = 0.8
    L.new(at.outputs["Fac"], mv.inputs[0]); L.new(mv.outputs[0], hs.inputs["Value"])
    sh = N.new("ShaderNodeAttribute"); sh.attribute_name = "shade"
    dk = N.new("ShaderNodeMix"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"; dk.inputs[0].default_value = 1.0
    L.new(hs.outputs[0], dk.inputs[6]); L.new(sh.outputs["Fac"], dk.inputs[7])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(dk.outputs[2], pb.inputs["Base Color"])
    pb.inputs["Roughness"].default_value = 0.45; pb.inputs["Specular IOR Level"].default_value = 0.35
    tr = N.new("ShaderNodeBsdfTranslucent")
    tc = N.new("ShaderNodeHueSaturation"); tc.inputs["Saturation"].default_value = 1.2; tc.inputs["Value"].default_value = 1.6
    L.new(hs.outputs[0], tc.inputs["Color"]); L.new(tc.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.35
    L.new(pb.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(c.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(mx.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    return m


def build(seed, loc=(0, 0, 0), pot_r=None, pot_h=None):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    objs, zs = gb.table_and_pot(loc, rng, rect=False)
    for o in objs:
        if o.name.startswith("bonsai_pot") or (o.data.materials and o.data.materials[0].name.startswith("pot_clay")):
            o.data.materials.clear(); o.data.materials.append(glaze_material())
    zs -= loc[2]
    # ---- the wood: a thick trunk splitting into leaders, nebari, main branches
    H0 = rng.uniform(0.11, 0.15)                                       # to the split
    base = np.array([rng.uniform(-0.03, 0.03), rng.uniform(-0.02, 0.02), zs - 0.03])
    lean = _unit(np.array([rng.normal(0, 0.18), rng.normal(0, 0.12), 1.0]))
    trunk = gb.spine(base, lean, H0, 30, rng, bends=1.2, amp=0.5)
    R0 = rng.uniform(0.045, 0.06)
    tt = np.linspace(0, 1, len(trunk))
    trad = R0 * (1 - 0.3 * tt) * (1 + 0.35 * np.exp(-tt / 0.08))
    spines = [("trunk", trunk, trad)]
    n_rt = int(rng.integers(6, 10))
    for j in range(n_rt):                                               # nebari: thick buttress roots, half buried
        az = 2 * math.pi * j / n_rt + rng.normal(0, 0.25)
        rp = gb.spine(trunk[3], [math.cos(az), math.sin(az), -0.35], rng.uniform(0.09, 0.15), 16, rng, amp=0.3, droop=0.4)
        rr_ = R0 * rng.uniform(0.55, 0.7) * np.linspace(1, 0.12, len(rp)) ** 0.8
        surf = zs + 0.012 * (1 - (rp[:, 0] / 0.24) ** 2 - (rp[:, 1] / 0.17) ** 2).clip(0, 1)
        rp[:, 2] = np.maximum(np.minimum(rp[:, 2], surf - 0.4 * rr_ + 0.004), surf - 0.5 * rr_)
        spines.append(("root", rp, rr_))
    # the canopy: a broad dome, a touch wider one way, its top ~0.45-0.55 m above the soil
    Hc = rng.uniform(0.42, 0.52)
    cc = np.array([trunk[-1][0] + rng.normal(0, 0.03), trunk[-1][1], zs + Hc * 0.62])
    AX, AY, AZ = rng.uniform(0.27, 0.33), rng.uniform(0.22, 0.27), Hc * 0.42
    n_lead = int(rng.integers(3, 5))
    net, ntan = [], []
    az0 = rng.uniform(0, 2 * math.pi)
    for i in range(n_lead):                                             # leaders fanning up and out from the split
        a_ = az0 + 2 * math.pi * i / n_lead + rng.normal(0, 0.3)
        tgt = cc + np.array([math.cos(a_) * AX * 0.45, math.sin(a_) * AY * 0.45, AZ * rng.uniform(0.0, 0.5)])
        sp_ = gb.grow(trunk[-1], trunk[-1] - trunk[-4], tgt, 22, rng, wob=0.08)
        spines.append(("lead", sp_, np.linspace(trad[-1] * rng.uniform(0.5, 0.65), 0.009, len(sp_))))
        net.append(sp_); ntan.append(np.gradient(sp_, axis=0))
        for _ in range(int(rng.integers(3, 6))):                        # main branches off each leader, out to the shell
            k = int(rng.uniform(0.3, 0.95) * (len(sp_) - 1))
            b_ = rng.uniform(0, 2 * math.pi)
            tb = cc + np.array([math.cos(b_) * AX * 0.85, math.sin(b_) * AY * 0.85, AZ * rng.uniform(-0.45, 0.35)])
            bp_ = gb.grow(sp_[k], np.gradient(sp_, axis=0)[k], tb, 16, rng, sag=0.06, wob=0.1)
            spines.append(("branch", bp_, np.linspace(0.0075, 0.0035, len(bp_))))
            net.append(bp_); ntan.append(np.gradient(bp_, axis=0))
    net, ntan = np.concatenate(net), np.concatenate(ntan)
    # ---- fuse + bark
    allV, allF, off = [], [], 0
    for _, sp, rr in spines:
        V_, F_ = gb.closed_tube(sp, np.maximum(rr, 0.0024), sides=18)
        allV.append(V_); allF += [[i + off for i in f] for f in F_]; off += len(V_)
    raw = gb._obj("maple_raw", np.concatenate(allV), allF, None)
    rm = raw.modifiers.new("fuse", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0016
    sm = raw.modifiers.new("sm", "SMOOTH"); sm.factor = 0.6; sm.iterations = 6
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(raw.evaluated_get(dg)); bpy.data.objects.remove(raw)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
    bark = bark_material()
    wood = bpy.data.objects.new(f"maple_{seed}_wood", me); bpy.context.scene.collection.objects.link(wood)
    wood.data.materials.append(bark); wood.location = loc; wood["tree"] = 1
    objs.append(wood)
    # ---- twigs to the shell, a leaf cluster on each
    tips = []
    for _ in range(20000):
        if len(tips) >= 620:
            break
        dv = _unit(rng.normal(0, 1, 3))
        if dv[2] < -0.5:
            continue
        if dv[2] < 0:
            dv[2] *= 0.55                                                # a flatter underside
        r_ = rng.uniform(0.8, 1.0) * (1 + 0.07 * math.sin(4 * math.atan2(dv[1], dv[0]) + seed))
        p = cc + dv * [AX, AY, AZ] * r_
        if tips and np.min(np.linalg.norm(np.array(tips) - p, axis=1)) < 0.024:
            continue
        tips.append(p)
    TV, TF, off = [], [], 0
    atlas = json.loads((MAPS / "atlas.json").read_text())
    names = sorted(atlas)
    LV = {n: ([], [], [], [], []) for n in names}                       # verts, faces, uvs, var, shade
    for p in tips:
        d_ = np.linalg.norm(net - p, axis=1)
        ahead = ((p - net) * ntan).sum(1) > 0
        k = int(np.argmin(np.where(ahead, d_, d_ + 1)))
        tw = gb.grow(net[k], ntan[k], p, 7, rng, sag=0.05)
        V_, F_ = gb.closed_tube(tw, np.linspace(0.0028, 0.0012, len(tw)), sides=6)
        TV.append(V_); TF += [[i + off for i in f] for f in F_]; off += len(V_)
        out = _unit(p - cc) * [1, 1, 0.6]; out = _unit(out)
        sh = float(np.clip(0.55 + 0.45 * ((p - cc)[2] / AZ + 0.6) / 1.6, 0.45, 1.0))
        for _ in range(int(rng.integers(5, 10))):                       # the leaf cluster: petioles fanning from the tip
            nm = names[int(rng.integers(len(names)))]
            info = atlas[nm]
            Ls = rng.uniform(0.034, 0.05)
            fan = _unit(out + rng.normal(0, 0.55, 3) + [0, 0, 0.25])
            nrm = _unit(np.array([0, 0, 1.0]) + out * 0.5 + rng.normal(0, 0.3, 3))
            nrm = _unit(nrm - fan * (nrm @ fan))
            side = np.cross(fan, nrm)
            w = Ls * info["aspect"]
            j0 = p + rng.normal(0, 0.004, 3)
            V_l, U_l = [], []
            for jv in range(4):                                         # a 3 x 3 sheet, cupped a little, the tip drooping
                v = jv / 3
                for ju in range(4):
                    u = ju / 3
                    x = (u - info["midrib_u"]) * w
                    y = (v - info["joint_v"]) * Ls
                    z = 0.12 * (x / w * 2) ** 2 * w - 0.08 * v * v * Ls
                    V_l.append(j0 + fan * y + side * x + nrm * z); U_l.append((u, v))
            Vv, Ff, Uu, Va, Sa = LV[nm]
            o_ = len(Vv)
            Vv += V_l; Uu += U_l
            Ff += [[o_ + jv * 4 + ju, o_ + jv * 4 + ju + 1, o_ + (jv + 1) * 4 + ju + 1, o_ + (jv + 1) * 4 + ju] for jv in range(3) for ju in range(3)]
            va = rng.uniform(-1, 1); Va += [va] * 16; Sa += [sh * rng.uniform(0.85, 1.05)] * 16
    tw_o = gb._obj(f"maple_{seed}_twigs", np.concatenate(TV) + loc, TF, bark); tw_o["tree"] = 1; objs.append(tw_o)
    n_leaves = 0
    for nm, (Vv, Ff, Uu, Va, Sa) in LV.items():
        if not Ff:
            continue
        n_leaves += len(Ff) // 9
        o = gb._obj(f"maple_{seed}_foliage_{nm}", np.array(Vv) + loc, Ff, leaf_material(nm), Uu, {"var": Va, "shade": Sa}, smooth=True)
        o["tree"] = 1; objs.append(o)
    print(f"maple {seed}: {n_lead} leaders, {len(spines)} wood spines fused into {len(me.polygons)} faces, {len(tips)} twigs, {n_leaves} leaves")
    return objs

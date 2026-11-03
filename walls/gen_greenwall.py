"""Living green wall, parametric (Roman 2026-11-02: "not a painting ... living green wall"): a floor-to-ceiling planted
wall, every plant generated:
- planting pockets on a jittered grid (spacing ~22 cm), each gets a plant by a species mix that drifts across the wall
  (domain-warped noise, so the planting reads in sweeps like a designed living wall, not confetti)
- Boston ferns (plants/gen_fern.py, the photoreal one) tilted out of the wall, 5 seeded variants instanced with their own
  rotation / scale, so 60+ ferns cost 5 meshes
- golden pothos vines (leaves from the generated leaf atlas, plants/maps/pothos): each from a pocket, out a little, then
  hanging down the wall with a wander, heart leaves alternating every 4-6 cm on petioles, bigger near the pocket, small
  and lime at the growing tip, facing out
- the backing: sheet + cushion moss (walls/gen_mosswall.py's relief and photo textures) so no felt ever shows

Parameters (build kwargs): width, height, spacing, mix = (fern, pothos, moss-only, bird's nest fern, spider plant,
philodendron) shares (3 values = the first three), vine (max length, m).
- more species (Roman: "make even better"; real living walls mix many): bird's nest fern, spider plant, philodendron,
  strap leaves from generated photo atlases (plants/maps/nest, spider; the young monstera leaves)

    import gen_greenwall; objs = gen_greenwall.build(seed, (x, y, z), width=3.2, height=3.0)
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
PLANTS = HERE.parent / "plants"
sys.path.insert(0, str(PLANTS))
import fern_mat  # noqa: E402
import gen_fern  # noqa: E402
import gen_mosswall  # noqa: E402

POTHOS = PLANTS / "maps" / "pothos"


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _img(p, color=True):
    im = bpy.data.images.load(str(p), check_existing=True)
    if not color:
        im.colorspace_settings.name = "Non-Color"
    return im


def pothos_material(name, folder=POTHOS, rough=0.38, val=0.92):
    m = bpy.data.materials.new(f"{folder.name}_{name}"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    uv = N.new("ShaderNodeUVMap")
    c = N.new("ShaderNodeTexImage"); c.image = _img(folder / f"{name}_col.png"); L.new(uv.outputs[0], c.inputs["Vector"])
    bh = N.new("ShaderNodeTexImage"); bh.image = _img(folder / f"{name}_bump.png", False); L.new(uv.outputs[0], bh.inputs["Vector"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "var"
    hs = N.new("ShaderNodeHueSaturation"); L.new(c.outputs["Color"], hs.inputs["Color"])
    mv = N.new("ShaderNodeMath"); mv.operation = "MULTIPLY_ADD"; mv.inputs[1].default_value = 0.12; mv.inputs[2].default_value = val
    L.new(at.outputs["Fac"], mv.inputs[0]); L.new(mv.outputs[0], hs.inputs["Value"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; bp.inputs["Distance"].default_value = 0.001
    L.new(bh.outputs["Color"], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(hs.outputs[0], pb.inputs["Base Color"]); L.new(bp.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = rough; pb.inputs["Specular IOR Level"].default_value = 0.4
    tr = N.new("ShaderNodeBsdfTranslucent"); tc = N.new("ShaderNodeHueSaturation"); tc.inputs["Value"].default_value = 1.5
    L.new(hs.outputs[0], tc.inputs["Color"]); L.new(tc.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.15
    L.new(pb.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(c.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(mx.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    return m


def _noise2(x, y, rng, freq, n=12):
    k = rng.normal(0, 1, (n, 2)) * freq; ph = rng.uniform(0, 2 * math.pi, n)
    return sum(np.sin(x * k[i, 0] + y * k[i, 1] + ph[i]) for i in range(n)) / math.sqrt(n)


def build(seed, loc=(0, 0, 0), width=3.2, height=3.0, spacing=0.22, mix=(0.3, 0.3, 0.02, 0.12, 0.14, 0.12), vine=1.3, fern_scale=0.42):
    """the wall in the x-z plane facing -y; its moss face at y = loc.y - ~0.01; bottom at loc.z"""
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    sc = bpy.context.scene
    objs = gen_mosswall.build(seed + 1000, loc, width=width, height=height, mix=(0.6, 0.38, 0.0, 0.02), relief=0.05, frame=0.0, res=0.005)
    # pockets
    xs = np.arange(spacing / 2, width, spacing); zs = np.arange(spacing * 0.35, height, spacing * 0.85)   # (to the top: the ceiling line was bare)
    P = np.array([(x + rng.normal(0, spacing * 0.22), z + rng.normal(0, spacing * 0.2)) for z in zs for x in xs])
    # species in drifts: one warped noise field per species, each pocket takes the strongest; the biases are tuned until
    # every species holds its share (kinds: 0 fern, 1 pothos, 2 moss only, 3 bird's nest fern, 4 spider plant, 5 philodendron)
    if len(mix) == 3:
        mix = (mix[0], mix[1], mix[2], 0, 0, 0)
    share = np.array([mix[0], mix[1], mix[2], mix[3], mix[4], mix[5]], float); share /= share.sum()
    fields = np.array([_noise2(P[:, 0], P[:, 1], rng, 1.6) for _ in range(6)])
    fields[2] = rng.normal(0, 1, len(P))                                  # bare moss: scattered gaps, not a drift
    bias = np.zeros(6)
    for _ in range(200):
        kind = np.argmax(fields + bias[:, None] - np.where(share[:, None] > 0, 0, 1e9), axis=0)
        got = np.bincount(kind, minlength=6) / len(P)
        bias += 0.5 * (share - got)
    # ---- ferns: 5 variants, instanced
    fmat = fern_mat.leaf_material()
    variants = []
    for v in range(5):
        o = gen_fern.build(seed * 10 + v, (0, 0, 0), pot_r=0.0, mat=fmat, name=f"gw_fern_v{v}")
        o.hide_render = True; o.hide_viewport = True
        variants.append(o)
    n_f = 0
    for (x, z), k in zip(P, kind):
        if k != 0:
            continue
        v = variants[int(rng.integers(len(variants)))]
        inst = v.copy(); sc.collection.objects.link(inst); inst.hide_render = False; inst.hide_viewport = False
        s_ = fern_scale * rng.uniform(0.75, 1.2)
        inst.scale = (s_, s_, s_)
        # the crown out of the wall: the plant's up turned toward -y, tilted up 25-45 deg; spun about its own axis
        inst.rotation_mode = "XYZ"
        tilt = math.radians(rng.uniform(45, 70))
        inst.rotation_euler = (tilt, rng.normal(0, 0.15), rng.uniform(-0.4, 0.4))
        inst.location = (loc[0] - width / 2 + x, loc[1] - 0.02, loc[2] + z)
        objs.append(inst); n_f += 1
    # ---- pothos vines
    atlas = json.loads((POTHOS / "atlas.json").read_text())
    names = sorted(atlas)
    LV = {n: ([], [], [], []) for n in names}
    SV, SF, off = [], [], 0
    n_v = 0
    for (x, z), k in zip(P, kind):
        if k != 1:
            continue
        for _ in range(int(rng.integers(1, 4))):
            n_v += 1
            p = np.array([loc[0] - width / 2 + x + rng.normal(0, 0.03), loc[1] - 0.03, loc[2] + z])
            d = _unit(np.array([rng.normal(0, 0.4), -1.0, rng.uniform(-0.2, 0.4)]))
            L = rng.uniform(0.25, vine) * min(1.0, (z + 0.2) / 1.2)
            pts = [p.copy()]; step = 0.01
            for i in range(int(L / step)):
                out_ = pts[-1][1] - (loc[1] - 0.02)                          # how far out from the wall
                d = _unit(d + np.array([0, 0, -0.07]) + np.array([0, 0.03 if out_ < -0.12 else -0.01, 0]) + rng.normal(0, 0.05, 3))
                q = pts[-1] + d * step
                q[1] = min(q[1], loc[1] - 0.025)                             # never into the wall
                q[0] = np.clip(q[0], loc[0] - width / 2 + 0.03, loc[0] + width / 2 - 0.03)   # never past the wall's edge
                if q[2] < loc[2] + 0.05:
                    break
                pts.append(q)
            pts = np.array(pts)
            if len(pts) < 6:
                continue
            # the stem
            r = np.linspace(0.0022, 0.0012, len(pts))
            Vt, Ft = gen_fern_tube(pts, r)
            SV.append(Vt); SF += [[i + off for i in f] for f in Ft]; off += len(Vt)
            # leaves: every 4-6 cm, alternating sides, petiole out, blade facing out and down
            s = rng.uniform(0.0, 0.03); side = 1
            seg = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
            while s < seg[-1]:
                j = int(np.searchsorted(seg, s)); j = min(j, len(pts) - 2)
                t_ = s / seg[-1]
                tang = _unit(pts[j + 1] - pts[j])
                nm = names[int(rng.integers(len(names)))] if t_ < 0.8 else "leaf4"
                info = atlas[nm]
                Ls = rng.uniform(0.06, 0.1) * (1.15 - 0.6 * t_)
                sidev = _unit(np.cross(tang, [0, -1.0, 0])) * side
                pet = _unit(sidev * 0.7 + np.array([0, -0.8, 0.0]) + rng.normal(0, 0.15, 3))
                j0 = pts[j] + pet * rng.uniform(0.02, 0.045)
                fan = _unit(np.array([0, -0.35, -1.0]) + sidev * 0.5 + rng.normal(0, 0.25, 3))   # tip down and out
                nrm = _unit(np.array([0, -1.0, 0.2]) - fan * (np.array([0, -1.0, 0.2]) @ fan))
                sv = np.cross(fan, nrm); w = Ls * info["aspect"]
                Vv, Ff, Uu, Va = LV[nm]; o_ = len(Vv)
                for jv in range(4):
                    v_ = jv / 3
                    for ju in range(4):
                        u_ = ju / 3
                        xx = (u_ - info["midrib_u"]) * w; yy = (v_ - info["joint_v"]) * Ls
                        zz = -0.1 * (xx / w * 2) ** 2 * w - 0.06 * v_ * v_ * Ls
                        Vv.append(j0 + fan * yy + sv * xx + nrm * zz); Uu.append((u_, v_))
                Ff += [[o_ + jv * 4 + ju, o_ + jv * 4 + ju + 1, o_ + (jv + 1) * 4 + ju + 1, o_ + (jv + 1) * 4 + ju] for jv in range(3) for ju in range(3)]
                Va += [rng.uniform(-1, 1)] * 16
                # the petiole
                pp = np.array([pts[j] + (j0 - pts[j]) * t for t in np.linspace(0, 1, 4)])
                Vt, Ft = gen_fern_tube(pp, np.full(4, 0.0012))
                SV.append(Vt); SF += [[i + off for i in f] for f in Ft]; off += len(Vt)
                s += rng.uniform(0.04, 0.06); side = -side
    n_r = _rosettes(rng, P, kind, loc, width, objs)
    stem_m = bpy.data.materials.new("pothos_stem"); stem_m.use_nodes = True
    stem_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.2, 0.05, 1)
    stem_m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
    objs.append(gen_mosswall_obj("pothos_stems", np.concatenate(SV), SF, stem_m))
    n_l = 0
    for nm, (Vv, Ff, Uu, Va) in LV.items():
        if Ff:
            n_l += len(Ff) // 9
            objs.append(gen_mosswall_obj(f"pothos_{nm}", np.array(Vv), Ff, pothos_material(nm), Uu, {"var": Va}))
    print(f"green wall {seed}: {width} x {height} m, {len(P)} pockets: {n_f} ferns (5 meshes), {n_v} pothos vines, {n_l} leaves, {n_r}")
    return objs


NEST, SPIDER, PHILO = PLANTS / "maps" / "nest", PLANTS / "maps" / "spider", PLANTS / "maps" / "monstera"


def _strap(acc, nm, info, base, d0, L, bend, rng, wscale=1.0, fold=0.18, rows=10):
    """one strap leaf from the atlas: its midrib follows an arc (out along d0, curving down by bend), a V-fold along the
    midrib, a little twist; the blade faces out of the wall / up"""
    V, F, U, A = acc; o_ = len(V)
    pts = [np.array(base, float)]; d = _unit(np.array(d0, float)); step = L / rows
    for i in range(rows):
        d = _unit(d + np.array([0, 0, -bend / rows]) + rng.normal(0, 0.03, 3))
        pts.append(pts[-1] + d * step)
    w = L * info["aspect"] * wscale
    tw = rng.normal(0, 0.25)
    for i, q in enumerate(pts):
        v_ = i / rows
        t = _unit(pts[min(i + 1, rows)] - pts[max(i - 1, 0)])
        face = np.array([0, -0.8, 0.6])
        sd = np.cross(t, face); sd = _unit(sd if np.linalg.norm(sd) > 1e-3 else np.array([1.0, 0, 0]))
        nm_ = np.cross(sd, t)
        a = tw * v_; sd, nm_ = sd * math.cos(a) + nm_ * math.sin(a), nm_ * math.cos(a) - sd * math.sin(a)
        for ju, u_ in enumerate((0.0, info["midrib_u"], 1.0)):
            x = (u_ - info["midrib_u"]) * w
            V.append(q + sd * x + nm_ * abs(x) * fold); U.append((u_, v_))
    for i in range(rows):
        for ju in range(2):
            F.append([o_ + i * 3 + ju, o_ + i * 3 + ju + 1, o_ + (i + 1) * 3 + ju + 1, o_ + (i + 1) * 3 + ju])
    A += [rng.uniform(-1, 1)] * (3 * (rows + 1))


def _rosettes(rng, P, kind, loc, width, objs):
    """bird's nest fern (a cup of broad glossy fronds), spider plant (a fountain of striped blades arching over),
    philodendron (young split leaves on long petioles, a dark glossy clump)"""
    banks = {}
    def acc(folder, nm):
        return banks.setdefault((folder, nm), ([], [], [], []))
    cnt = [0, 0, 0]
    for (x, z), k in zip(P, kind):
        base = np.array([loc[0] - width / 2 + x, loc[1] - 0.03, loc[2] + z])
        if k == 3:
            cnt[0] += 1
            atlas = json.loads((NEST / "atlas.json").read_text()); names = sorted(atlas)
            n = int(rng.integers(9, 15)); L0 = rng.uniform(0.26, 0.42)
            for i in range(n):
                a = 2 * math.pi * i / n + rng.normal(0, 0.15)
                d0 = np.array([math.cos(a) * 0.55, -0.9, 0.35 + math.sin(a) * 0.55])     # a cup opening out and up
                nm = names[int(rng.integers(len(names)))]
                _strap(acc(NEST, nm), nm, atlas[nm], base + rng.normal(0, 0.01, 3), d0, L0 * rng.uniform(0.6, 1.1),
                       rng.uniform(0.5, 1.1), rng, fold=0.12)
        elif k == 4:
            cnt[1] += 1
            atlas = json.loads((SPIDER / "atlas.json").read_text()); names = sorted(atlas)
            n = int(rng.integers(22, 36))
            for i in range(n):
                a = rng.uniform(0, 2 * math.pi)
                d0 = np.array([math.cos(a) * 0.6, -0.7, 0.5 + 0.5 * abs(math.sin(a))])     # up and out, then arching over
                nm = names[int(rng.integers(len(names)))]
                _strap(acc(SPIDER, nm), nm, atlas[nm], base + rng.normal(0, 0.008, 3), d0, rng.uniform(0.14, 0.3),
                       rng.uniform(1.4, 2.6), rng, wscale=0.6, fold=0.3)
        elif k == 5:
            cnt[2] += 1
            atlas = json.loads((PHILO / "atlas.json").read_text())
            names = [k_ for k_ in sorted(atlas) if k_.startswith(("leafs", "leafy"))]
            for i in range(int(rng.integers(6, 11))):
                a = rng.uniform(0, 2 * math.pi)
                pet = _unit(np.array([math.cos(a) * 0.7, -1.0, math.sin(a) * 0.5 + 0.2]))
                j0 = base + pet * rng.uniform(0.06, 0.16)
                nm = names[int(rng.integers(len(names)))]
                # a heart leaf: short and broad, drooping from the petiole tip, facing out
                _strap(acc(PHILO, nm), nm, atlas[nm], j0, _unit(pet * 0.4 + np.array([0, -0.2, -0.6]) + rng.normal(0, 0.2, 3)),
                       rng.uniform(0.11, 0.19), 0.3, rng, fold=0.1, rows=6)
                pp = np.array([base + (j0 - base) * t for t in np.linspace(0, 1, 4)])
                Vt, Ft = gen_fern_tube(pp, np.full(4, 0.0025))
                Vs, Fs, Us, As = acc(PHILO, "_stem"); o_ = len(Vs); Vs += list(Vt); Fs += [[i_ + o_ for i_ in f] for f in Ft]
    stem = bpy.data.materials.new("philo_stem"); stem.use_nodes = True
    stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.16, 0.04, 1)
    for (folder, nm), (V, F, U, A) in banks.items():
        if not F:
            continue
        if nm == "_stem":
            objs.append(gen_mosswall_obj(f"{folder.name}_stems", np.array(V), F, stem)); continue
        mat = pothos_material(nm, folder, rough={"nest": 0.5, "spider": 0.55, "monstera": 0.42}[folder.name],
                              val={"nest": 0.72, "spider": 0.85, "monstera": 0.8}[folder.name])   # (the nest fronds read pale + papery at 0.92)
        objs.append(gen_mosswall_obj(f"{folder.name}_{nm}", np.array(V), F, mat, U, {"var": A}))
    return f"{cnt[0]} bird's nest ferns, {cnt[1]} spider plants, {cnt[2]} philodendrons"


def gen_fern_tube(pts, radii, sides=6):
    n = len(pts); V, F = [], []
    for k in range(n):
        d = _unit(pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)])
        a1 = _unit(np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.95 else np.cross(d, [1.0, 0, 0])); a2 = np.cross(d, a1)
        for j in range(sides):
            t = 2 * math.pi * j / sides
            V.append(pts[k] + (a1 * math.cos(t) + a2 * math.sin(t)) * radii[k])
    for k in range(n - 1):
        for j in range(sides):
            a_, b_ = k * sides + j, k * sides + (j + 1) % sides
            F.append([a_, a_ + sides, b_ + sides, b_])
    return np.array(V), F


def gen_mosswall_obj(name, V, F, mat, uv=None, attrs=None):
    me = bpy.data.meshes.new(name); me.from_pydata(np.asarray(V).tolist(), [], F)
    if uv is not None:
        ul = me.uv_layers.new(name="UVMap"); ul.data.foreach_set("uv", np.array([uv[i] for f in F for i in f], np.float32).ravel())
    for k, a in (attrs or {}).items():
        at = me.attributes.new(k, "FLOAT", "POINT"); at.data.foreach_set("value", np.asarray(a, np.float32))
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat)
    return o

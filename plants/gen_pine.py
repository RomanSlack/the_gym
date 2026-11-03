"""A sculptural cloud-pruned Scots pine (niwaki), full size, for the gym (Roman 2026-11-02: "pine trees ... sort of
tailored"). The bonsai's method at 1:1:
- the wood: a trunk with a couple of slow sculptural bends, 5-7 main branches leaving it along its direction and curving
  out level onto their pads (grow(): no right-angle joints), all fused into one body (voxel remesh); the bark two generated
  4K photo textures (plants/maps/pine): grey-brown plated bark low down, turning to the Scots pine's thin orange flaking
  bark up the trunk and on the branches, box-projected at real scale (20 / 10 cm tiles)
- the pads: wide flat clipped clouds at the branch ends + a crown pad, each a mass of real shoots: a stem whose needle pairs
  spiral round it angled forward (bottle brush), 4-6 cm blue-green needles, a brown bud at the tip; shoots point out and
  up over the dome; twigs fan into each pad from its branch; a dark core so the pads never read see-through; the pads'
  undersides and insides darker
- seeded: every tree its own trunk line, branch layout and pads

    import gen_pine; objs = gen_pine.build(seed, (x, y, z), height=2.0)
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gen_bonsai import _obj, _img, closed_tube, grow, tube  # noqa: E402

MAPS = HERE / "maps" / "pine"
_M = {}


def _unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bark_material():
    if "bark" in _M:
        return _M["bark"]
    m = bpy.data.materials.new("pine_bark"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")

    def img(name, scale, color=True):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale * 0.6)   # (plates run long)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        t = N.new("ShaderNodeTexImage"); t.image = _img(MAPS / name, color); t.projection = "BOX"; t.projection_blend = 0.3
        L.new(mp.outputs[0], t.inputs["Vector"]); return t
    pc, ph = img("barkplate4k_col.jpg", 5), img("barkplate4k_h.png", 5, False)
    fc, fh = img("barkflake4k_col.jpg", 10), img("barkflake4k_h.png", 10, False)
    # the plate bark a touch warmer + greyer (the generated one leaned lilac), the flake bark a little less saturated
    pt = N.new("ShaderNodeHueSaturation"); pt.inputs["Hue"].default_value = 0.53; pt.inputs["Saturation"].default_value = 0.8
    pt.inputs["Value"].default_value = 0.8; L.new(pc.outputs[0], pt.inputs["Color"])
    ft = N.new("ShaderNodeHueSaturation"); ft.inputs["Saturation"].default_value = 0.82; ft.inputs["Value"].default_value = 0.85
    L.new(fc.outputs[0], ft.inputs["Color"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "flake"
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(at.outputs["Fac"], mx.inputs[0]); L.new(pt.outputs[0], mx.inputs[6]); L.new(ft.outputs[0], mx.inputs[7])
    hm = N.new("ShaderNodeMix"); hm.data_type = "FLOAT"
    L.new(at.outputs["Fac"], hm.inputs[0]); L.new(ph.outputs[0], hm.inputs[2]); L.new(fh.outputs[0], hm.inputs[3])
    cv = N.new("ShaderNodeMath"); cv.operation = "MULTIPLY_ADD"; cv.inputs[1].default_value = 0.55; cv.inputs[2].default_value = 0.45
    L.new(hm.outputs[0], cv.inputs[0])
    dk = N.new("ShaderNodeMix"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"; dk.inputs[0].default_value = 1.0
    L.new(mx.outputs[2], dk.inputs[6]); L.new(cv.outputs[0], dk.inputs[7])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 1.0; bp.inputs["Distance"].default_value = 0.004
    L.new(hm.outputs[0], bp.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(dk.outputs[2], pb.inputs["Base Color"]); L.new(bp.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = 0.92; pb.inputs["Specular IOR Level"].default_value = 0.2
    L.new(pb.outputs[0], out.inputs["Surface"])
    _M["bark"] = m
    return m


def needle_material():
    if "needle" in _M:
        return _M["needle"]
    m = bpy.data.materials.new("pine_needles"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    ca = N.new("ShaderNodeVertexColor"); ca.layer_name = "col"
    L.new(ca.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.42; b.inputs["Specular IOR Level"].default_value = 0.45   # waxy needles
    b.inputs["Subsurface Weight"].default_value = 0.1; b.inputs["Subsurface Radius"].default_value = (0.002, 0.004, 0.001)
    _M["needle"] = m
    return m


def _needles(shoots, rng):
    """shoots: (base, dir, length, tint, shade) -> ribbon needles in pairs spiralling round each stem, a bud at the tip;
    returns V, F, colours"""
    V, F, C = [], [], []
    off = 0
    GLAU, OLD, BUD, STEM = np.array([0.07, 0.14, 0.075]), np.array([0.09, 0.12, 0.05]), np.array([0.13, 0.075, 0.04]), np.array([0.06, 0.08, 0.04])
    for base, d, Ls, tint, shade in shoots:
        a1 = _unit(np.cross(d, [0.3, 0.1, 1.0])); a2 = np.cross(d, a1)
        n_f = int(Ls / 0.0028)                                           # a fascicle every ~3 mm of stem
        t = np.linspace(0.03, 0.96, n_f)                                 # (from 0.12: bare stems hung below the pads)
        phi = np.arange(n_f) * math.radians(137.5) + rng.uniform(0, 6.3)
        P0 = base + d * (Ls * t)[:, None]                                 # fascicle points
        out = np.cos(phi)[:, None] * a1 + np.sin(phi)[:, None] * a2
        # the pair: two needles diverging a little from one sheath, both angled forward 35-60 deg off the stem
        ND = []
        for sg in (-1, 1):
            ang = np.radians(rng.uniform(40, 62, n_f) + 30 * (1 - t) ** 2) * (1 - 0.35 * t)   # flaring at the base (it clothes the stem: bare stubs showed below the pads), tighter at the tip
            spread = sg * np.radians(rng.uniform(6, 14, n_f))
            o2 = _unit(out * np.cos(spread)[:, None] + np.cross(d, out) * np.sin(spread)[:, None])
            ND.append(_unit(d * np.cos(ang)[:, None] + o2 * np.sin(ang)[:, None] + rng.normal(0, 0.06, (n_f, 3))))
        ND = np.concatenate(ND); P = np.concatenate([P0, P0]); tt = np.concatenate([t, t])
        nn = len(ND)
        ln = rng.uniform(0.04, 0.06, nn) * (1 - 0.35 * tt ** 2)
        side = _unit(np.cross(ND, d[None]) + 1e-6)
        # 4 points along, curving gently toward the stem's direction (the needles sweep forward)
        seg = []
        for k in range(4):
            s = k / 3
            pk = P + ND * (ln * s)[:, None] + d[None] * (ln * 0.12 * s * s)[:, None]
            w = 0.0007 * (1 - 0.85 * s)                                   # 1.4 mm wide, to a point
            seg.append((pk - side * w, pk + side * w))
        for k in range(4):
            V.append(seg[k][0]); V.append(seg[k][1])
        # vertex order: [k][0/1] blocks of nn: index = (2k + j) * nn + i
        idx = np.arange(nn)
        for k in range(3):
            a, b_, c, e = (2 * k) * nn + idx, (2 * k + 1) * nn + idx, (2 * k + 3) * nn + idx, (2 * k + 2) * nn + idx
            F += (np.stack([a, b_, c, e], 1) + off).tolist()
        col_n = (GLAU * (1 + tint))[None] * np.ones((nn, 1))
        old = (tt < 0.35)[:, None]
        col_n = np.where(old, OLD * (1 + tint), col_n)
        for k in range(4):
            s = k / 3
            cc = col_n * (0.82 + 0.3 * s) * shade
            C.append(cc); C.append(cc)
        off += 8 * nn
        # the stem + the bud
        Vt, Ft, _ = tube(np.array([base, base + d * Ls * 0.5, base + d * Ls]), np.array([0.0022, 0.0018, 0.0014]), sides=5, cap=False)
        V.append(Vt); F += [[i + off for i in f] for f in Ft]; C.append(np.repeat((STEM * shade)[None], len(Vt), 0)); off += len(Vt)
        Vb, Fb, _ = tube(np.array([base + d * Ls, base + d * (Ls + 0.006), base + d * (Ls + 0.009)]), np.array([0.0019, 0.0017, 0.0003]), sides=6)
        V.append(Vb); F += [[i + off for i in f] for f in Fb]; C.append(np.repeat((BUD * shade)[None], len(Vb), 0)); off += len(Vb)
    return np.concatenate(V), F, np.concatenate(C)


def build(seed, loc=(0, 0, 0), height=2.0, density=2600, name="pine"):
    rng = np.random.default_rng(seed)
    loc = np.array(loc, float)
    H = height * rng.uniform(0.62, 0.7)                                  # the wood's height; the crown pad tops it
    # ---- the trunk: a lean one way low, a slow counter-bend, settling upright (the niwaki line)
    sd = rng.choice([-1, 1]); az = rng.uniform(0, 2 * math.pi)
    lean = np.array([math.cos(az), math.sin(az), 0.0])
    pts = [np.zeros(3)]
    for i in range(60):
        t = (i + 1) / 60
        d = _unit(np.array([0, 0, 1.0]) + lean * (0.55 * math.sin(math.pi * t * 1.1) * sd - 0.25 * t)
                  + np.cross([0, 0, 1.0], lean) * 0.18 * math.sin(2.3 * math.pi * t + seed))
        pts.append(pts[-1] + d * H / 60)
    trunk = np.array(pts)
    tt = np.linspace(0, 1, len(trunk))
    R0 = rng.uniform(0.065, 0.085) * height / 2
    trad = R0 * (1 - 0.62 * tt) * (1 + 0.35 * np.exp(-tt / 0.04))
    spines = [(trunk, trad)]
    # ---- the branches + pads: alternating round the trunk, longer low down, each ends in a pad
    n_br = int(rng.integers(5, 8))
    hs = np.sort(rng.uniform(0.32, 0.88, n_br))
    pads = []
    a0 = rng.uniform(0, 2 * math.pi)
    for i, h in enumerate(hs):
        k = int(h * (len(trunk) - 1))
        for attempt in range(40):
            a = a0 + i * math.radians(rng.uniform(120, 160)) + rng.normal(0, 0.25)
            reach = (0.75 - 0.5 * h) * height * 0.42 * rng.uniform(0.85, 1.15)
            c = trunk[k] + np.array([math.cos(a) * reach, math.sin(a) * reach, rng.uniform(0.0, 0.12) * height / 2])
            rp = (0.36 - 0.18 * h) * height / 2 * rng.uniform(0.9, 1.1)
            # pads apart from each other (separate clouds with air between, the niwaki look) and clear of the trunk
            ok = all(np.linalg.norm((c - q[0]) * [1, 1, 2.2]) > (rp + q[1]) * 1.05 for q in pads)
            dtr = np.linalg.norm((trunk - c)[:, :2], axis=1)[np.abs(trunk[:, 2] - c[2]) < rp * 0.5]
            if ok and (len(dtr) == 0 or dtr.min() > rp * 0.85):
                break
        tk = _unit(trunk[min(k + 1, len(trunk) - 1)] - trunk[max(k - 1, 0)])
        bp = grow(trunk[k], tk * 0.6 + _unit(c - trunk[k]) * 0.4, c - np.array([0, 0, rp * 0.15]), 24, rng, sag=0.06, wob=0.06)
        spines.append((bp, np.linspace(trad[k] * 0.55, 0.012 * height / 2, len(bp))))
        pads.append((c, rp, _unit(c - trunk[k])))
    # the crown pad on the leader
    top = trunk[-1]
    pads.append((top + np.array([0, 0, 0.05]), 0.2 * height / 2 * rng.uniform(0.9, 1.1), np.array([0, 0, 1.0])))
    # ---- the wood: fused
    allV, allF, off = [], [], 0
    for sp, rr in spines:
        V_, F_ = closed_tube(sp, np.maximum(rr, 0.006), sides=20)
        allV.append(V_); allF += [[i + off for i in f] for f in F_]; off += len(V_)
    raw = _obj(f"{name}_wood_raw", np.concatenate(allV), allF, None)
    rm = raw.modifiers.new("fuse", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.004 * height / 2; rm.adaptivity = 0.0
    sm = raw.modifiers.new("sm", "SMOOTH"); sm.factor = 0.5; sm.iterations = 3
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(raw.evaluated_get(dg))
    bpy.data.objects.remove(raw)
    nV = len(me.vertices)
    P = np.empty(nV * 3, np.float32); me.vertices.foreach_get("co", P); P = P.reshape(-1, 3)
    flake = np.clip((P[:, 2] - 0.4 * H) / (0.3 * H), 0, 1)
    flake = flake * flake * (3 - 2 * flake)
    at = me.attributes.new("flake", "FLOAT", "POINT"); at.data.foreach_set("value", flake.astype(np.float32))
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()
    wood = bpy.data.objects.new(f"{name}_wood", me); bpy.context.scene.collection.objects.link(wood)
    wood.data.materials.append(bark_material()); wood.location = loc
    objs = [wood]
    # ---- each pad: twigs fanning in from its branch, shoots over its dome, a dark core
    shoots, twigs = [], []
    core_m = bpy.data.materials.get("pine_core") or bpy.data.materials.new("pine_core"); core_m.use_nodes = True
    cb = core_m.node_tree.nodes["Principled BSDF"]; cb.inputs["Base Color"].default_value = (0.012, 0.022, 0.012, 1); cb.inputs["Roughness"].default_value = 0.9
    for c, rp, din in pads:
        rx, ry, rz = rp, rp * rng.uniform(0.8, 1.0), rp * rng.uniform(0.5, 0.62)   # (0.4 read as flat plates)
        R3 = np.array([rx, ry, rz])
        area = 2 * math.pi * rx * ry * 0.75
        n_s = int(area * density)
        root = c - np.array([0, 0, rz * 0.5]) - din * rx * 0.3
        hubs = [c + np.array([*rng.normal(0, 0.45, 2) * [rx, ry], rng.uniform(-0.2, 0.3) * rz]) for _ in range(int(rng.integers(6, 11)))]
        for hb in hubs:
            twigs.append((grow(root, din + np.array([0, 0, 0.3]), hb, 8, rng, wob=0.1), np.linspace(0.009, 0.004, 8) * height / 2))
        for _ in range(n_s):
            u = _unit(rng.normal(0, 1, 3))
            if u[2] < -0.25:
                u[2] = -0.25 + 0.15 * u[2]
            nrm = _unit(u / R3)                                          # the ellipsoid's normal there
            surf = c + u * R3
            d = _unit(nrm + np.array([0, 0, 1.3]) + rng.normal(0, 0.25, 3))   # shoots (candles) point up: radial ones read as a hedgehog
            Ls = rng.uniform(0.07, 0.13)
            base = surf - d * Ls * rng.uniform(0.5, 1.1)                 # tips scattered round the clip line: depth, not a shell
            shade = float(np.clip(0.42 + 0.6 * (0.5 + 0.5 * u[2]), 0.35, 1.0))   # undersides + insides darker
            shoots.append((base, d, Ls, rng.normal(0, 0.07, 3) * [0.8, 1, 1.2], shade))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=tuple(c + loc), radius=1)
        co = bpy.context.object; co.scale = tuple(R3 * [0.62, 0.62, 0.5]); co.name = f"{name}_core"; co.data.materials.append(core_m)
        objs.append(co)
    tv, tf, off = [], [], 0
    for sp, rr in twigs:
        V_, F_, _ = tube(sp, rr, sides=6)
        tv.append(V_); tf += [[i + off for i in f] for f in F_]; off += len(V_)
    tw = _obj(f"{name}_twigs", np.concatenate(tv) + loc, tf, bark_material(), attrs={"flake": np.ones(off)})
    objs.append(tw)
    V, F, C = _needles(shoots, rng)
    objs.append(_obj(f"{name}_needles", V + loc, F, needle_material(), colors=C))
    for o in objs:
        o["tree"] = True
    print(f"pine {name} {seed}: wood {H:.2f} m, {len(spines) - 1} branches, {len(pads)} pads, {len(shoots)} shoots, {len(F)} needle faces")
    return objs

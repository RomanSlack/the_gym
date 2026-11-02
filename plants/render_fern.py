"""Boston fern test renders: one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_fern.py -- SHOT OUT.png [--seed 1] [--samples 256]

SHOT: trio (three seeds side by side: no two alike), hero (one plant, eye level), close (the fronds at 0.45 m),
backlit (the light behind it: the translucency).
"""
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402
import gen_fern  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES = int(opt("--seed", 1)), int(opt("--samples", 256))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"


def leaf_material():
    """Nephrolepis leaf: colour by age (yellow-green new -> mid green -> yellowing old) varied per frond and per pinna, browned
    tips, paler + rougher underside with sori on mature fronds, midrib + forked lateral veins from the pinna UVs, a waxy upper
    sheen, translucent when backlit; the rachis and runners brown-green."""
    m = bpy.data.materials.new("nephrolepis"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")

    def math_(op, x, y=None, z=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((x, y, z)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def mixc(f, c1, c2):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"
        if isinstance(f, (int, float)):
            n.inputs[0].default_value = f
        else:
            L.new(f, n.inputs[0])
        for i, c in ((6, c1), (7, c2)):
            if isinstance(c, tuple):
                n.inputs[i].default_value = c
            else:
                L.new(c, n.inputs[i])
        return n.outputs[2]

    age, fr, pr, brown = _attr(N, "age"), _attr(N, "fr"), _attr(N, "pr"), _attr(N, "brown")
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.11, 0.28, 0.025, 1)      # new: fresh yellow-green
    cr.elements[1].position = 0.45; cr.elements[1].color = (0.035, 0.13, 0.014, 1)     # mature: mid green
    e = cr.elements.new(0.8); e.color = (0.045, 0.13, 0.016, 1)
    e = cr.elements.new(1.0); e.color = (0.15, 0.17, 0.035, 1)                          # old: yellowing
    L.new(age, ramp.inputs[0])
    hsv = N.new("ShaderNodeHueSaturation")
    L.new(ramp.outputs[0], hsv.inputs["Color"])
    L.new(math_("MULTIPLY_ADD", fr, 0.04, 0.48), hsv.inputs["Hue"])                    # per frond: +-0.02 hue
    L.new(math_("MULTIPLY_ADD", pr, 0.16, 0.92), hsv.inputs["Value"])                  # per pinna: +-8 % value
    L.new(math_("MULTIPLY_ADD", fr, 0.25, 1.05), hsv.inputs["Saturation"])
    col = hsv.outputs[0]
    # veins from the pinna UVs: the midrib (v = 0.5) and lateral veins forking out toward the tip
    uv = N.new("ShaderNodeUVMap"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(uv.outputs[0], sep.inputs[0])
    u_, v_ = sep.outputs[0], sep.outputs[1]
    dv = math_("ABSOLUTE", math_("SUBTRACT", v_, 0.5))
    midrib = _band(N, L, dv, 0.0, 0.028)
    lat = math_("FRACT", math_("SUBTRACT", math_("MULTIPLY", u_, 16.0), math_("MULTIPLY", dv, 9.0)))
    lat = _band(N, L, math_("ABSOLUTE", math_("SUBTRACT", lat, 0.5)), 0.42, 0.5, invert=False)
    veins = math_("MAXIMUM", midrib, math_("MULTIPLY", lat, math_("LESS_THAN", dv, 0.44)))
    col = mixc(math_("MULTIPLY", veins, 0.22), col, (0.30, 0.48, 0.10, 1))
    # browned tips / damage
    col = mixc(math_("MAXIMUM", brown, 0.0), col, (0.23, 0.12, 0.04, 1))
    # the rachis (brown = -1) and the runners (-2)
    isr = math_("LESS_THAN", brown, -0.5)
    isst = math_("LESS_THAN", brown, -1.5)
    col = mixc(isr, col, (0.022, 0.03, 0.009, 1))
    col = mixc(isst, col, (0.09, 0.065, 0.03, 1))
    # underside: paler, rougher; sori (brown dots near the margins) on mature fronds
    geo = N.new("ShaderNodeNewGeometry")
    back = geo.outputs["Backfacing"]
    under = mixc(0.35, col, (0.36, 0.48, 0.2, 1))
    sx = math_("SUBTRACT", math_("FRACT", math_("MULTIPLY", u_, 11.0)), 0.5)
    sy = math_("SUBTRACT", dv, 0.31)
    sor = math_("LESS_THAN", math_("ADD", math_("MULTIPLY", sx, sx), math_("MULTIPLY", math_("MULTIPLY", sy, sy), 9.0)), 0.018)
    sor = math_("MULTIPLY", math_("MULTIPLY", math_("MULTIPLY", sor, math_("GREATER_THAN", age, 0.55)), math_("GREATER_THAN", fr, 0.35)), math_("MULTIPLY", math_("GREATER_THAN", u_, 0.15), math_("LESS_THAN", u_, 0.92)))
    under = mixc(math_("MULTIPLY", math_("MULTIPLY", sor, math_("SUBTRACT", 1, isr)), 0.8), under, (0.07, 0.04, 0.015, 1))
    base = mixc(back, col, under)
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.0004
    L.new(math_("SUBTRACT", 1.0, veins), bump.inputs["Height"])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(base, pb.inputs["Base Color"])
    L.new(math_("MAXIMUM", math_("MULTIPLY_ADD", back, 0.25, math_("MULTIPLY_ADD", age, 0.12, 0.33)), math_("MULTIPLY", isr, 0.62)), pb.inputs["Roughness"])   # the stipes matte
    pb.inputs["Specular IOR Level"].default_value = 0.45
    L.new(bump.outputs[0], pb.inputs["Normal"])
    tr = N.new("ShaderNodeBsdfTranslucent")
    tcol = N.new("ShaderNodeHueSaturation"); tcol.inputs["Hue"].default_value = 0.47; tcol.inputs["Saturation"].default_value = 1.35; tcol.inputs["Value"].default_value = 2.2   # backlit leaves glow yellow-green
    L.new(base, tcol.inputs["Color"]); L.new(tcol.outputs[0], tr.inputs["Color"])
    L.new(bump.outputs[0], tr.inputs["Normal"])
    mx = N.new("ShaderNodeMixShader")
    L.new(math_("MULTIPLY", math_("SUBTRACT", 1, isr), 0.2), mx.inputs[0])
    L.new(pb.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    return m


def _attr(N, name):
    n = N.new("ShaderNodeAttribute"); n.attribute_name = name; n.attribute_type = "GEOMETRY"
    return n.outputs["Fac"]


def _band(N, L, x, lo, hi, invert=True):
    """1 inside [lo, hi] with soft edges (x a socket)"""
    n = N.new("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
    L.new(x, n.inputs["Value"])
    if invert:                                    # 1 at lo falling to 0 at hi
        n.inputs["From Min"].default_value = hi; n.inputs["From Max"].default_value = lo
    else:
        n.inputs["From Min"].default_value = lo; n.inputs["From Max"].default_value = hi
    return n.outputs["Result"]


def pot(loc, rng_seed=0):
    """our pot: a tapered stone-grey ceramic planter, a rolled rim, soil with bark chips; returns the soil height"""
    import numpy as np
    rng = np.random.default_rng(rng_seed)
    prof = [(0.0, 0.0), (0.128, 0.0), (0.132, 0.01), (0.165, 0.29), (0.172, 0.295), (0.174, 0.305), (0.168, 0.31),
            (0.155, 0.305), (0.150, 0.29), (0.118, 0.02), (0.0, 0.02)]
    seg = 96
    V, F = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for r, z in prof:
            V.append((loc[0] + r * math.cos(a), loc[1] + r * math.sin(a), loc[2] + z))
    P = len(prof)
    for i in range(seg):
        for j in range(P - 1):
            a_, b_ = i * P + j, ((i + 1) % seg) * P + j
            F.append((a_, b_, b_ + 1, a_ + 1))
    me = bpy.data.meshes.new("pot"); me.from_pydata(V, [], F); me.update()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    o = bpy.data.objects.new("pot", me); sc.collection.objects.link(o)
    o.modifiers.new("ws", "WEIGHTED_NORMAL")
    pm = bpy.data.materials.new("pot_stone"); pm.use_nodes = True
    Nn, Ll = pm.node_tree.nodes, pm.node_tree.links
    b = Nn["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.17, 0.165, 0.155, 1); b.inputs["Roughness"].default_value = 0.72
    nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 8
    bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.0006
    Ll.new(nz.outputs[0], bp.inputs["Height"]); Ll.new(bp.outputs[0], b.inputs["Normal"])
    o.data.materials.append(pm)
    zs = loc[2] + 0.272
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=0.152, fill_type="NGON", location=(loc[0], loc[1], zs))
    soil = bpy.context.object
    sm = bpy.data.materials.new("soil"); sm.use_nodes = True
    Nn, Ll = sm.node_tree.nodes, sm.node_tree.links
    b = Nn["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.035, 0.025, 0.018, 1); b.inputs["Roughness"].default_value = 0.95
    nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90; nz.inputs["Detail"].default_value = 10
    bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; bp.inputs["Distance"].default_value = 0.004
    Ll.new(nz.outputs[0], bp.inputs["Height"]); Ll.new(bp.outputs[0], b.inputs["Normal"])
    soil.data.materials.append(sm)
    cm = bpy.data.materials.new("bark"); cm.use_nodes = True
    cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.028, 0.016, 1)
    cm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
    for i in range(45):                                           # bark chips: irregular flakes, not tiles
        r = 0.14 * math.sqrt(rng.random()); a = rng.uniform(0, 2 * math.pi)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(loc[0] + r * math.cos(a), loc[1] + r * math.sin(a), zs + 0.001))
        c = bpy.context.object
        for vtx in c.data.vertices:
            vtx.co *= rng.uniform(0.7, 1.3)
        c.scale = (rng.uniform(0.006, 0.016), rng.uniform(0.004, 0.011), rng.uniform(0.0012, 0.0025))
        c.rotation_euler = (rng.normal(0, 0.25), rng.normal(0, 0.25), rng.uniform(0, 6.3))
        c.data.materials.append(cm)
    return zs


def room(key_loc, key_e=320, rim=True):
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.83, 0.86, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
    bpy.context.object.data.materials.append(bc.material("floor_oak", (0.42, 0.33, 0.24), 0.55))
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 1.6, 3), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(bc.material("wall", (0.72, 0.71, 0.68), 0.9))
    ld = bpy.data.lights.new("key", "AREA"); ld.size = 2.2; ld.energy = key_e; ld.color = (1.0, 0.97, 0.92)
    k = bpy.data.objects.new("key", ld); sc.collection.objects.link(k); k.location = key_loc
    k.rotation_euler = (mathutils.Vector((0, 0, 0.6)) - k.location).to_track_quat("-Z", "Y").to_euler()
    if rim:
        lr = bpy.data.lights.new("rim", "AREA"); lr.size = 1.2; lr.energy = key_e * 0.45; lr.color = (1.0, 0.98, 0.9)
        r_ = bpy.data.objects.new("rim", lr); sc.collection.objects.link(r_); r_.location = (1.6, 1.3, 1.9)
        r_.rotation_euler = (mathutils.Vector((0, 0, 0.6)) - r_.location).to_track_quat("-Z", "Y").to_euler()


def look(loc, tgt, lens):
    c = bc.camera(sc, "cam", loc, tgt, lens); sc.camera = c


mat = leaf_material()
if SHOT == "trio":
    for i, x in enumerate((-1.25, 0.0, 1.25)):
        zs = pot((x, 0, 0), i)
        gen_fern.build(SEED + i, (x, 0, zs), mat=mat)
    room(mathutils.Vector((-2.2, -2.4, 2.8)), 250)
    look((0, -4.4, 1.5), (0, 0, 0.42), 36)
elif SHOT in ("hero", "close", "backlit"):
    zs = pot((0, 0, 0), SEED)
    gen_fern.build(SEED, (0, 0, zs), mat=mat)
    if SHOT == "hero":
        room(mathutils.Vector((-2.0, -2.2, 2.6)), 190)
        look((0.45, -2.5, 1.35), (0, 0, 0.4), 38)
    elif SHOT == "close":
        room(mathutils.Vector((-2.0, -2.2, 2.6)), 190)
        look((0.18, -0.62, 0.62), (0.0, -0.12, 0.42), 50)
    else:
        room(mathutils.Vector((0.3, 1.25, 1.5)), 700, rim=False)      # the light from behind, through the fronds (in front of the wall)
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
        look((0.2, -1.7, 0.95), (0, 0, 0.45), 45)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

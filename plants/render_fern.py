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
    pb.inputs["Specular IOR Level"].default_value = 0.3   # (0.45 went silvery at grazing angles, backlit)
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


from stage import look, pot, room  # noqa: E402  (the shared scene: plants/stage.py)


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

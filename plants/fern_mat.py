"""The Boston fern leaf material (from render_fern.py), importable without rendering: used by walls/gen_greenwall.py."""
import bpy


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

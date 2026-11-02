"""Monstera test renders: one shot per Blender process (render politeness).

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
      blender -b -t 12 --python plants/render_monstera.py -- SHOT OUT.png [--seed 1] [--samples 256]

SHOT: hero (one plant, eye level), trio (three seeds), close (a mature leaf at 0.6 m), backlit.
"""
import math
import sys
from pathlib import Path

import bpy
import mathutils

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "construction"))
import bl_common as bc  # noqa: E402
import gen_monstera  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT = a[0], a[1]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
SEED, SAMPLES = int(opt("--seed", 1)), int(opt("--samples", 256))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
bc.gpu_or_stop()
sc.cycles.device = "GPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.tile_size = 256
sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"
from stage import look, pot, room  # noqa: E402


def leaf_material(path):
    """one leaf: its own colour + cut-out and relief images; the glossy waxy upper side (a thin clear coat), the paler,
    matte underside, a little light through it, cut where the alpha is 0"""
    m = bpy.data.materials.new(path.name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    col = N.new("ShaderNodeTexImage"); col.image = bpy.data.images.load(str(path.with_name(path.name + "_col.png")))
    col.interpolation = "Cubic"
    bmp = N.new("ShaderNodeTexImage"); bmp.image = bpy.data.images.load(str(path.with_name(path.name + "_bump.png")))
    bmp.image.colorspace_settings.name = "Non-Color"
    geo = N.new("ShaderNodeNewGeometry")
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.002
    mic = N.new("ShaderNodeTexNoise"); mic.inputs["Scale"].default_value = 900; mic.inputs["Detail"].default_value = 3
    hb = N.new("ShaderNodeMath"); hb.operation = "MULTIPLY_ADD"; hb.inputs[1].default_value = 0.04
    L.new(mic.outputs[0], hb.inputs[0]); L.new(bmp.outputs["Color"], hb.inputs[2])          # micro-texture breaks the sheen
    L.new(hb.outputs[0], bump.inputs["Height"])
    under = N.new("ShaderNodeHueSaturation"); under.inputs["Saturation"].default_value = 0.8; under.inputs["Value"].default_value = 1.2
    L.new(col.outputs["Color"], under.inputs["Color"])
    base = N.new("ShaderNodeMix"); base.data_type = "RGBA"
    L.new(geo.outputs["Backfacing"], base.inputs[0]); L.new(col.outputs["Color"], base.inputs[6]); L.new(under.outputs[0], base.inputs[7])
    pb = N.new("ShaderNodeBsdfPrincipled")
    L.new(base.outputs[2], pb.inputs["Base Color"])
    rmix = N.new("ShaderNodeMath"); rmix.operation = "MULTIPLY_ADD"; rmix.inputs[1].default_value = 0.25; rmix.inputs[2].default_value = 0.3
    L.new(geo.outputs["Backfacing"], rmix.inputs[0]); L.new(rmix.outputs[0], pb.inputs["Roughness"])
    pb.inputs["Specular IOR Level"].default_value = 0.5
    cw = N.new("ShaderNodeMath"); cw.operation = "MULTIPLY_ADD"; cw.inputs[1].default_value = -0.2; cw.inputs[2].default_value = 0.2
    L.new(geo.outputs["Backfacing"], cw.inputs[0]); L.new(cw.outputs[0], pb.inputs["Coat Weight"])     # the cuticle, on top only
    pb.inputs["Coat Roughness"].default_value = 0.2
    L.new(bump.outputs[0], pb.inputs["Normal"]); L.new(bump.outputs[0], pb.inputs["Coat Normal"])
    tr = N.new("ShaderNodeBsdfTranslucent")
    tc = N.new("ShaderNodeHueSaturation"); tc.inputs["Hue"].default_value = 0.47; tc.inputs["Value"].default_value = 1.8
    L.new(col.outputs["Color"], tc.inputs["Color"]); L.new(tc.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.12
    L.new(pb.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    cut = N.new("ShaderNodeMixShader"); tp = N.new("ShaderNodeBsdfTransparent")
    L.new(col.outputs["Alpha"], cut.inputs[0]); L.new(tp.outputs[0], cut.inputs[1]); L.new(mx.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    return m


def stem_material():
    m = bpy.data.materials.new("monstera_petiole"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.10, 0.22, 0.045, 1); b.inputs["Roughness"].default_value = 0.32
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (90, 90, 6)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], nz.inputs["Vector"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[0].default_value = 0.25
    mx.inputs[6].default_value = (0.10, 0.22, 0.045, 1); mx.inputs[7].default_value = (0.16, 0.30, 0.07, 1)
    L.new(nz.outputs[0], mx.inputs[0]); L.new(mx.outputs[2], b.inputs["Base Color"])
    return m


def root_material():
    return bc.material("monstera_root", (0.09, 0.055, 0.03), 0.75)


def plant(seed, x):
    zs = pot((x, 0, 0), seed, scale=1.3)
    return gen_monstera.build(seed, (x, 0, zs), 0.2, leaf_mat=leaf_material, stem_mat=stem_material(), root_mat=root_material())


if SHOT == "trio":
    for i, x in enumerate((-1.3, 0.0, 1.3)):
        plant(SEED + i, x)
    room(mathutils.Vector((-2.2, -2.4, 2.8)), 260)
    look((0, -5.2, 1.7), (0, 0, 0.8), 36)
else:
    objs = plant(SEED, 0.0)
    if SHOT == "hero":
        room(mathutils.Vector((-2.0, -2.2, 2.6)), 200)
        look((0.6, -3.0, 1.55), (0, 0, 0.8), 38)
    elif SHOT == "close":
        room(mathutils.Vector((-2.0, -2.2, 2.6)), 200)
        # the biggest leaf facing the camera side, seen square-on from 0.75 m along its own normal
        leaves = [o for o in objs if "leaf" in o.name]
        def facing(o):
            n_ = sum((pl.normal * pl.area for pl in o.data.polygons), mathutils.Vector()).normalized()
            return n_
        lv = max(leaves, key=lambda o: o.dimensions.length * (0.3 + max(0.0, -facing(o).y)))
        c = sum((lv.matrix_world @ v.co for v in lv.data.vertices), mathutils.Vector()) / len(lv.data.vertices)
        n_ = facing(lv)
        if n_.z < -0.2:
            n_ = -n_
        look(tuple(c + n_ * 0.75 + mathutils.Vector((0, -0.1, 0.05))), tuple(c), 40)
    else:
        room(mathutils.Vector((0.3, 1.25, 1.6)), 700, rim=False)
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
        look((0.3, -2.3, 1.15), (0, 0, 0.65), 40)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)

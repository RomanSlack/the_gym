"""The shared stage for the plant renders: our pot, a plain room (oak floor, pale wall, a soft window key, a rim light), the
camera. Used by render_fern.py and render_monstera.py."""
import math

import bpy
import mathutils

import bl_common as bc

def pot(loc, rng_seed=0, scale=1.0):
    """our pot: a tapered stone-grey ceramic planter, a rolled rim, soil with bark chips; returns the soil height.
    scale: 1 = 0.35 m across, 0.31 m tall"""
    import numpy as np
    rng = np.random.default_rng(rng_seed)
    prof = [(0.0, 0.0), (0.128, 0.0), (0.132, 0.01), (0.165, 0.29), (0.172, 0.295), (0.174, 0.305), (0.168, 0.31),
            (0.155, 0.305), (0.150, 0.29), (0.118, 0.02), (0.0, 0.02)]
    seg = 96
    V, F = [], []
    prof = [(r * scale, z * scale) for r, z in prof]
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
    sc = bpy.context.scene
    o = bpy.data.objects.new("pot", me); sc.collection.objects.link(o)
    o.modifiers.new("ws", "WEIGHTED_NORMAL")
    pm = bpy.data.materials.new("pot_stone"); pm.use_nodes = True
    Nn, Ll = pm.node_tree.nodes, pm.node_tree.links
    b = Nn["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.17, 0.165, 0.155, 1); b.inputs["Roughness"].default_value = 0.72
    nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 8
    bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.0006
    Ll.new(nz.outputs[0], bp.inputs["Height"]); Ll.new(bp.outputs[0], b.inputs["Normal"])
    o.data.materials.append(pm)
    zs = loc[2] + 0.272 * scale
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=0.152 * scale, fill_type="NGON", location=(loc[0], loc[1], zs))
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
    for i in range(int(45 * scale * scale)):                       # bark chips: irregular flakes, not tiles
        r = 0.14 * scale * math.sqrt(rng.random()); a = rng.uniform(0, 2 * math.pi)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(loc[0] + r * math.cos(a), loc[1] + r * math.sin(a), zs + 0.001))
        c = bpy.context.object
        for vtx in c.data.vertices:
            vtx.co *= rng.uniform(0.7, 1.3)
        c.scale = (rng.uniform(0.006, 0.016), rng.uniform(0.004, 0.011), rng.uniform(0.0012, 0.0025))
        c.rotation_euler = (rng.normal(0, 0.25), rng.normal(0, 0.25), rng.uniform(0, 6.3))
        c.data.materials.append(cm)
    return zs


def room(key_loc, key_e=320, rim=True):
    sc = bpy.context.scene
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
    sc = bpy.context.scene
    c = bc.camera(sc, "cam", loc, tgt, lens); sc.camera = c

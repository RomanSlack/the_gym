"""The towel over Kulpen's badestamp rim, draped by a real cloth simulation (Roman: "just do a cloth sim").

A 0.5 x 0.9 m cotton towel is dropped across the tub's rim (more of it outside than in) and left to settle against the staves;
the settled mesh is saved to construction/data/towel_badestamp.npz, which furniture.badestamp() loads (tub-local coordinates:
tub centre at the origin, its base at z = 0, the towel on the rim at -y, towards the steps).

nice -n 19 blender -b --factory-startup -t 12 --python construction/towel_sim.py
"""
import math
from pathlib import Path

import bmesh
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "construction" / "data" / "towel_badestamp.npz"
R, Z0, H = 1.0, 0.08, 1.0            # the tub (furniture.badestamp defaults): radius, base, stave height
TOP = Z0 + H

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 90

# the collider: the staves' wall as a ring (inside face, rim, outside face) + the water surface inside
b = bmesh.new()
n = 96
rings = [(R - 0.045, Z0), (R - 0.045, TOP), (R, TOP), (R, Z0)]   # a closed ring section: the stave wall as a solid
vs = [[b.verts.new((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z)) for (r, z) in rings] for k in range(n)]
for k in range(n):
    A, B = vs[k], vs[(k + 1) % n]
    for i in range(len(rings)):
        j = (i + 1) % len(rings)
        b.faces.new((A[i], B[i], B[j], A[j]))
bmesh.ops.recalc_face_normals(b, faces=b.faces)
me = bpy.data.meshes.new("tub_wall"); b.to_mesh(me); b.free()
wall = bpy.data.objects.new("tub_wall", me); sc.collection.objects.link(wall)
bpy.context.view_layer.objects.active = wall; bpy.ops.object.modifier_add(type="COLLISION")
wall.collision.thickness_outer = 0.012; wall.collision.thickness_inner = 0.01; wall.collision.cloth_friction = 80.0
bpy.ops.mesh.primitive_circle_add(vertices=96, radius=R - 0.03, fill_type="NGON", location=(0, 0, TOP - 0.15))  # runs into the wall: no gap to slip down
water = bpy.context.object; bpy.ops.object.modifier_add(type="COLLISION"); water.collision.thickness_outer = 0.003

# the towel: 0.5 along the rim, 0.9 across it (0.42 inside, 0.48 outside: terry grips the wood), 3 cm above the rim, a little crumple to start
W, Lr, inside = 0.5, 0.9, 0.42
bpy.ops.mesh.primitive_grid_add(x_subdivisions=26, y_subdivisions=46, size=1.0, location=(0, 0, 0))
tw = bpy.context.object
rng = np.random.default_rng(3)
for v in tw.data.vertices:
    u, w = v.co.x, v.co.y                         # -0.5..0.5
    v.co.x = u * W
    v.co.y = -(R - inside) - (w + 0.5) * Lr       # radial: from 0.42 inside the rim to 0.48 outside, along -y
    v.co.z = TOP + 0.02 + float(rng.uniform(0, 0.003))
cl = tw.modifiers.new("cloth", "CLOTH").settings
cl.quality = 16; cl.mass = 0.35; cl.air_damping = 2.0
cl.tension_stiffness = cl.compression_stiffness = 15.0; cl.shear_stiffness = 8.0; cl.bending_stiffness = 0.6   # heavy cotton terry
cl.tension_damping = cl.compression_damping = 5.0; cl.bending_damping = 0.5
coll = tw.modifiers["cloth"].collision_settings
coll.friction = 80.0; coll.distance_min = 0.004; coll.use_self_collision = True; coll.self_distance_min = 0.003; coll.collision_quality = 8
tw.modifiers["cloth"].point_cache.frame_end = sc.frame_end

bpy.context.view_layer.update()
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f)
dg = bpy.context.evaluated_depsgraph_get()
me2 = tw.evaluated_get(dg).to_mesh()
V = np.array([v.co[:] for v in me2.vertices], np.float32)
F = np.array([p.vertices[:] for p in me2.polygons], np.int32)
OUT.parent.mkdir(parents=True, exist_ok=True)
np.savez(OUT, verts=V, faces=F)
print("towel settled:", len(V), "verts; z", float(V[:, 2].min()), "..", float(V[:, 2].max()), "->", OUT.relative_to(ROOT))

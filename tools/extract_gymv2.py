"""Extract Roman's hand-made Gym V2 blockout into plain JSON (the "existing survey").

Run:  blender -b reference/gym_v2_original/The_Gym_v2_snapshot_2026-09-18.blend \
        --python tools/extract_gymv2.py -- reference/gym_v2_original/gymv2_extract.json

Every object is classified by shape (slab / column / wall / beam / panel / block / void /
person / label / terrain) and stored with its world-space plan footprint and z range.
The two sculpted terrain planes are resampled into one 1 m heightfield by raycasting.
"""
import bpy, json, math, sys
from mathutils import Vector

out_path = sys.argv[sys.argv.index("--") + 1]
deps = bpy.context.evaluated_depsgraph_get()
r2 = lambda v: round(v, 3)


def classify(o):
    d = o.dimensions
    if o.type == "FONT":
        return "label"
    if o.name.startswith("blender_"):
        return "person"
    if o.name in ("Plane", "Plane.003"):
        return "terrain"
    if o.name == "Plane.002":
        return "flat_plane"
    if o.name.startswith("Cylinder"):
        return "void" if o.hide_get() else "round_block"
    if o.name.startswith("Plane."):
        return "beam"
    thin_plan = min(d.x, d.y)
    if d.z <= 0.3 and min(d.x, d.y) > 2:
        return "slab"
    if d.z >= 2 and thin_plan <= 0.12:
        return "panel"  # 0.09 m thick: glazing / door panels
    if d.z >= 2 and max(d.x, d.y) <= 0.7:
        return "column"
    if d.z >= 2 and thin_plan <= 0.36:
        return "wall"
    return "block"


def footprint(o):
    """World-space plan corners of the object's bounding box (handles z rotation)."""
    m = o.matrix_world
    pts = [m @ Vector(c) for c in o.bound_box]
    zs = [p.z for p in pts]
    # bound_box indices 0,4,7,3 are the local -z face, in ring order (safe for flat planes)
    bottom = [pts[i] for i in (0, 4, 7, 3)]
    return [[r2(p.x), r2(p.y)] for p in bottom], r2(min(zs)), r2(max(zs))


elements = []
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    kind = classify(o)
    if kind == "terrain":
        continue
    poly, z0, z1 = footprint(o)
    e = {"name": o.name, "kind": kind, "plan": poly, "z": [z0, z1],
         "hidden": o.hide_get(), "collection": o.users_collection[0].name}
    if kind == "label":
        e["text"] = o.data.body.strip()
        e["at"] = [r2(o.location.x), r2(o.location.y), r2(o.location.z)]
        e["rot_z"] = r2(o.rotation_euler.z)
    if kind == "person":
        e["at"] = [r2(o.location.x), r2(o.location.y), r2(z0)]
        e["height"] = r2(o.dimensions.y)  # cutouts stand on their local Y axis
    if kind in ("void", "round_block"):
        e["center"] = [r2(o.location.x), r2(o.location.y)]
        e["radius"] = r2(o.dimensions.x / 2)
    cutters = [md.object.name for md in o.modifiers if md.type == "BOOLEAN" and md.object]
    if cutters:
        e["cut_by"] = cutters
    elements.append(e)

# --- terrain heightfield: topmost hit on either terrain plane, 1 m grid ---
terrain = [bpy.data.objects[n] for n in ("Plane", "Plane.003")]
for t in terrain:
    t.hide_set(False)
xs, ys = [], []
for t in terrain:
    for c in t.bound_box:
        w = t.matrix_world @ Vector(c)
        xs.append(w.x); ys.append(w.y)
step = 1.0
x0, y0 = math.floor(min(xs)), math.floor(min(ys))
nx, ny = int(math.ceil(max(xs)) - x0) + 1, int(math.ceil(max(ys)) - y0) + 1
heights = []  # row-major, y outer; centimetres, None = no terrain
for j in range(ny):
    for i in range(nx):
        origin = Vector((x0 + i * step, y0 + j * step, 500.0))
        best = None
        for t in terrain:
            inv = t.matrix_world.inverted()
            ok, loc, *_ = t.ray_cast(inv @ origin, (inv.to_3x3() @ Vector((0, 0, -1))).normalized(), depsgraph=deps)
            if ok:
                z = (t.matrix_world @ loc).z
                best = z if best is None else max(best, z)
        heights.append(None if best is None else int(round(best * 100)))

data = {
    "source": "The_Gym_v2_snapshot_2026-09-18.blend",
    "units": "m",
    "axes": "x east, y north, z up (Blender world)",
    "elements": elements,
    "terrain": {"origin": [x0, y0], "step": step, "nx": nx, "ny": ny,
                "unit": "cm", "heights": heights},
}
with open(out_path, "w") as f:
    json.dump(data, f, separators=(",", ":"))
counts = {}
for e in elements:
    counts[e["kind"]] = counts.get(e["kind"], 0) + 1
print("EXTRACT", out_path, len(elements), counts, "terrain", nx, "x", ny)

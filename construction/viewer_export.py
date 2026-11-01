"""Export the saved stage scene for scenewalk (~/tools/scenewalk, Roman 2026-11-01: "we can quickly iterate on these things without
the full rebuild and render"): the gym's building shell as one glTF, every equipment prototype as its own glTF, and an index the
layout adapter (tools/viewer_manifest.py) places them from. Layout changes then need no Blender at all; run this again only when
the building, the furnishings or a piece's model changes.

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \\
        blender -b construction/out/stage_5.blend -t 12 --python construction/viewer_export.py [-- shell|eq]

-> construction/out/viewer/shell.glb, eq/<prototype>.glb, index.json
"""
import json
import re
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "construction" / "out" / "viewer"
(OUT / "eq").mkdir(parents=True, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DO = set(args) or {"shell", "eq"}
T0 = time.time()
BOX = ((-33.0, -44.5, -11.0), (-3.0, 16.0, 7.5))            # the gym wing: F1-F3, its walls, the spiral, the river side
SHELL = ("1 · foundations", "3 · structure", "4 · envelope", "5 · interior shell", "5b · furniture + fixtures")
LAYOUT_FURN = ("wipe_station",)                             # furnishings the layouts place: in the manifest, not the shell
vl = bpy.context.view_layer


def in_box(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box] if o.type == "MESH" else [o.matrix_world.translation]
    lo, hi = BOX
    return all(min(p[i] for p in pts) <= hi[i] and max(p[i] for p in pts) >= lo[i] for i in range(3))


def lean(objs):
    """Viewer geometry: bevels off (render detail, ~40 % of the triangles), dense meshes decimated to ~30k faces."""
    for o in objs:
        if o.type != "MESH":
            continue
        for m in o.modifiers:
            if m.type == "BEVEL":
                m.show_viewport = m.show_render = False
        n = len(o.data.polygons)
        if n > 30000 and not any(m.type == "DECIMATE" for m in o.modifiers):
            d = o.modifiers.new("viewer_decimate", "DECIMATE"); d.ratio = max(0.05, 30000 / n)


def export(path, objs):
    bpy.ops.object.select_all(action="DESELECT")
    n = 0
    for o in objs:
        try:
            o.select_set(True); n += 1
        except RuntimeError:
            pass
    if not n:
        return 0
    bpy.ops.export_scene.gltf(filepath=str(path), use_selection=True, export_apply=True, export_lights=False, export_cameras=False,
                              export_extras=False, export_yup=True, export_image_format="JPEG", export_jpeg_quality=80)
    return n


model = json.loads((ROOT / "model" / "building.json").read_text())
layout_furn = {f["id"] for f in model.get("furnishings", []) if f["kind"] in LAYOUT_FURN}
index = {"protos": {}, "attach": {}, "furn": {}}

if "eq" in DO:
    # every prototype an equipment instance uses, exported in its own (unplaced) axes
    for lc in vl.layer_collection.children:
        if lc.name.startswith("eq_prototypes"):
            lc.exclude = False
    inst = [o for o in bpy.data.collections["5b · gym equipment"].all_objects if o.instance_type == "COLLECTION" and o.instance_collection]
    used = {o.instance_collection for o in inst}
    for c in sorted(used, key=lambda c: c.name):
        objs = [o for o in c.all_objects if o.type in ("MESH", "CURVE", "FONT")]
        lean(objs)
        fn = re.sub(r"[^A-Za-z0-9_.-]", "_", c.name) + ".glb"
        export(OUT / "eq" / fn, objs)
        index["protos"][c.name] = {"file": f"eq/{fn}", "centre": list(c.get("centre", (0.0, 0.0))), "sig": c.get("sig")}
    # what rides on a placed piece (a bench's bar, a hanger's kit, a rig's parallel bars): its matrix relative to its carrier
    by = {o.name: o for o in inst}
    for o in inst:
        base = re.sub(r"-(bar|kit)$", "", o.name)
        if base != o.name and base in by:
            rel = by[base].matrix_world.inverted() @ o.matrix_world
            index["attach"].setdefault(by[base].instance_collection.name, []).append(
                {"proto": o.instance_collection.name, "m": [list(r) for r in rel]})
    # one wipes station, as the layouts place them (their furnishing ids are in building.json)
    for f in model.get("furnishings", []):
        if f["kind"] in LAYOUT_FURN and f["kind"] not in index["furn"]:
            o = bpy.data.objects.get(f["id"])
            if o and o.instance_collection:
                c = o.instance_collection
                objs = [q for q in c.all_objects if q.type in ("MESH", "CURVE", "FONT")]
                lean(objs)
                export(OUT / "eq" / f"furn_{f['kind']}.glb", objs)
                index["furn"][f["kind"]] = {"file": f"eq/furn_{f['kind']}.glb", "proto_origin": "placed at (x, y, level) turned by rot"}
    for k_, v in index["attach"].items():                     # one per carrier kind is enough (they're all the same)
        seen, out = set(), []
        for a in v:
            if a["proto"] not in seen:
                seen.add(a["proto"]); out.append(a)
        index["attach"][k_] = out
    print(f"viewer: {len(used)} prototypes, {len(index['attach'])} carriers ({time.time() - T0:.0f} s)")

if "shell" in DO:
    for lc in vl.layer_collection.children:
        if lc.name.startswith("eq_prototypes"):
            lc.exclude = True
    objs = []
    for nm in SHELL:
        c = bpy.data.collections.get(nm)
        if not c:
            continue
        for o in c.all_objects:
            if o.type in ("LIGHT", "CAMERA") or o.name in layout_furn or (o.name.endswith("_light")):
                continue
            if o.type == "EMPTY" and not o.instance_collection:
                continue
            if in_box(o):
                objs.append(o)
    lean(objs)
    for o in objs:                                              # what instanced furnishings draw
        if o.instance_collection:
            lean(list(o.instance_collection.all_objects))
    n = export(OUT / "shell.glb", objs)
    print(f"viewer: shell {n} objects ({time.time() - T0:.0f} s)")

idx = OUT / "index.json"
if idx.exists() and DO != {"shell", "eq"}:                     # a partial run keeps the other half's entries
    old = json.loads(idx.read_text())
    for k_ in ("protos", "attach", "furn"):
        index[k_] = index[k_] or old.get(k_, {})
idx.write_text(json.dumps(index, indent=1))
print(f"viewer: wrote {OUT} ({time.time() - T0:.0f} s)")

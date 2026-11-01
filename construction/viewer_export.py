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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gltf_fix  # noqa: E402  (Blender writes texCoord -1 on box-mapped textures; strict readers refuse it)

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


def _guess(sock, depth=0):
    """A flat colour for a procedural colour input: the ramp's mean, an RGB node, a box-mapped image's mean, a mix of its
    inputs (through vector maths and hue / saturation / value), else None; "image" for a UV-mapped image (glTF keeps it)."""
    if depth > 8:
        return None
    if not sock.is_linked:
        v = getattr(sock, "default_value", None)
        return tuple(v[:3]) if v is not None and hasattr(v, "__len__") and len(v) >= 3 and sock.type == "RGBA" else None
    n = sock.links[0].from_node
    if n.type == "TEX_IMAGE":
        return _img_mean(n.image) if n.image and _uvless(n) else "image"
    if n.type == "VALTORGB":
        els = n.color_ramp.elements
        return tuple(sum(e.color[i] for e in els) / len(els) for i in range(3))
    if n.type == "RGB":
        return tuple(n.outputs[0].default_value[:3])
    if n.type == "HUE_SAT":
        c = _guess(n.inputs["Color"], depth + 1)
        if c in (None, "image"):
            return c
        val, sat = n.inputs["Value"].default_value, n.inputs["Saturation"].default_value
        g = sum(c) / 3
        return tuple(max(0.0, (g + (ch - g) * sat) * val) for ch in c)
    if n.type in ("TEX_COORD", "ATTRIBUTE", "TEX_NOISE", "TEX_VORONOI", "TEX_WAVE", "MAPPING"):
        return None
    cols = [c for c in (_guess(i, depth + 1) for i in n.inputs if i.type in ("RGBA", "VECTOR") and (i.is_linked or i.type == "RGBA")) if c]
    if "image" in cols:
        return "image"
    return tuple(sum(c[i] for c in cols) / len(cols) for i in range(3)) if cols else None


def _uvless(img_node, depth=0):
    """An image texture placed without UVs (box projection, object / generated coordinates): glTF can't carry it."""
    if img_node.projection == "BOX":
        return True
    v = img_node.inputs["Vector"]
    while v.is_linked and depth < 6:
        n = v.links[0].from_node
        if n.type == "TEX_COORD":
            return v.links[0].from_socket.name != "UV"
        v = n.inputs[0] if n.inputs else v; depth += 1
        if not v.is_linked:
            break
    return False


def _img_mean(img):
    import numpy as np
    px = np.empty(len(img.pixels), dtype=np.float32); img.pixels.foreach_get(px)
    return tuple(float(c) for c in px.reshape(-1, 4)[::7, :3].mean(axis=0))


def flatten_materials():
    """glTF keeps only image textures: a base colour driven by procedural nodes would export white. Give it its flat mean
    (in memory only; the .blend isn't saved)."""
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        nm = m.name.lower()
        nt = m.node_tree
        if not any(nd.type == "BSDF_PRINCIPLED" for nd in nt.nodes) and any(nd.type in ("BSDF_GLASS", "BSDF_TRANSPARENT") for nd in nt.nodes):
            out = next((nd for nd in nt.nodes if nd.type == "OUTPUT_MATERIAL"), None)
            src = next(nd for nd in nt.nodes if nd.type in ("BSDF_GLASS", "BSDF_TRANSPARENT"))
            if out:
                pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
                pr.inputs["Base Color"].default_value = tuple(src.inputs["Color"].default_value)
                pr.inputs["Roughness"].default_value = 0.05; pr.inputs["Alpha"].default_value = 0.15
                nt.links.new(pr.outputs[0], out.inputs["Surface"])
                if hasattr(m, "surface_render_method"):
                    m.surface_render_method = "BLENDED"
                else:
                    m.blend_method = "BLEND"
                n += 1
            continue
        for nd in m.node_tree.nodes:
            if nd.type != "BSDF_PRINCIPLED":
                continue
            if "mirror" in nm:                                  # no reflections in the viewer: a dark polished metal reads as mirror
                for k_, v in (("Base Color", (0.42, 0.45, 0.48, 1.0)), ("Metallic", 1.0), ("Roughness", 0.08)):
                    if nd.inputs[k_].is_linked:
                        m.node_tree.links.remove(nd.inputs[k_].links[0])
                    nd.inputs[k_].default_value = v
                continue
            tw = nd.inputs.get("Transmission Weight") or nd.inputs.get("Transmission")
            if "glass" in nm or "acrylic" in nm or (tw is not None and not tw.is_linked and tw.default_value > 0.5):
                nd.inputs["Alpha"].default_value = 0.18          # see-through (the exporter writes alpha blend)
                if hasattr(m, "surface_render_method"):
                    m.surface_render_method = "BLENDED"
                else:
                    m.blend_method = "BLEND"
                continue
            for k_ in ("Base Color", "Normal"):                 # box-mapped images: no UVs in glTF
                sk = nd.inputs[k_]
                if not sk.is_linked:
                    continue
                img = next((l_.from_node for l_ in sk.links if l_.from_node.type == "TEX_IMAGE"), None)
                if img is None and k_ == "Normal":
                    src = sk.links[0].from_node
                    img = next((i.links[0].from_node for i in src.inputs if i.is_linked and i.links[0].from_node.type == "TEX_IMAGE"), None)
                if img is not None and img.image and _uvless(img):
                    c = _img_mean(img.image) if k_ == "Base Color" else None
                    m.node_tree.links.remove(sk.links[0])
                    if c:
                        nd.inputs["Base Color"].default_value = (*c, 1.0); n += 1
            if nd.inputs["Base Color"].is_linked:
                c = _guess(nd.inputs["Base Color"])
                if c == "image":
                    continue
                c = c or tuple(m.diffuse_color[:3])
                m.node_tree.links.remove(nd.inputs["Base Color"].links[0])
                nd.inputs["Base Color"].default_value = (*c, 1.0); n += 1
    print(f"viewer: {n} procedural base colours flattened")


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
    gltf_fix.fix(str(path))
    return n


model = json.loads((ROOT / "model" / "building.json").read_text())
layout_furn = {f["id"] for f in model.get("furnishings", []) if f["kind"] in LAYOUT_FURN}
index = {"protos": {}, "attach": {}, "furn": {}, "on": {}}
flatten_materials()

if "eq" in DO:
    # every prototype an equipment instance uses, exported in its own (unplaced) axes
    def unexclude(lc):
        lc.exclude = False; lc.hide_viewport = False
        for ch in lc.children:
            unexclude(ch)
    for lc in vl.layer_collection.children:
        if lc.name.startswith("eq_prototypes"):
            unexclude(lc)
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
    # pieces mounted on another (the parallel bars in a rig's bay): their matrix relative to the carrier's, the nearest rig (item ids
    # repeat across floors, so not by name)
    index["on"] = {}
    rigs = [o for o in inst if "-rig-2-0" in o.instance_collection.name and "rig-mount" not in o.instance_collection.name]
    for o in inst:
        if "rig-mount" in o.instance_collection.name and rigs:
            r = min(rigs, key=lambda q: (q.matrix_world.translation - o.matrix_world.translation).length)
            rel = r.matrix_world.inverted() @ o.matrix_world
            index["on"][o.instance_collection.name] = {"carrier": r.instance_collection.name, "m": [list(x) for x in rel]}
    # one wipes station, as the layouts place them (their furnishing ids are in building.json)
    for f in model.get("furnishings", []):
        if f["kind"] in LAYOUT_FURN and f["kind"] not in index["furn"]:
            o = bpy.data.objects.get(f["id"])
            if o and o.instance_collection:
                c = o.instance_collection
                linked = c.name not in bpy.context.scene.collection.children
                if linked:                                    # (furniture prototypes live outside the view layer)
                    bpy.context.scene.collection.children.link(c)
                objs = [q for q in c.all_objects if q.type in ("MESH", "CURVE", "FONT")]
                lean(objs)
                if export(OUT / "eq" / f"furn_{f['kind']}.glb", objs):
                    index["furn"][f["kind"]] = {"file": f"eq/furn_{f['kind']}.glb", "proto_origin": "placed at (x, y, level) turned by rot"}
                if linked:
                    bpy.context.scene.collection.children.unlink(c)
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
    for k_ in ("protos", "attach", "furn", "on"):
        index[k_] = index[k_] or old.get(k_, {})
idx.write_text(json.dumps(index, indent=1))
print(f"viewer: wrote {OUT} ({time.time() - T0:.0f} s)")

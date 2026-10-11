"""Tree library for the site scatter: generated variants x 3 LODs, cached in construction/out/tree_lib.blend.

blender -b --factory-startup -t 12 --python construction/tree_lib.py
Collection "tree_lib" holds one child collection per variant + LOD, named so that alphabetical order = scatter index:
  v{index:02d}_L{lod}   (index = position in VARIANTS, lod 0 every needle / 1 reduced / 2 baked impostor)
Each tree sits at the origin, base at z = 0, at its variant height; the scatter scales it to the target height.
The blend stores the hash of trees.py + this file; scene.py rebuilds the library when either changes.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402
import trees  # noqa: E402

OUT = ROOT / "construction" / "out"; IMP = OUT / "trees" / "imp"; IMP.mkdir(parents=True, exist_ok=True)
# (species, seed, generated height). Heights near the local top heights (docs/ECOLOGY.md); the scatter scales 0.6-1.4x.
VARIANTS = [("spruce", 201, 16), ("spruce", 202, 15), ("spruce", 203, 17), ("spruce", 204, 14), ("spruce", 205, 18), ("spruce", 206, 13),
            ("pine", 301, 14), ("pine", 302, 13), ("pine", 303, 15), ("pine", 304, 12),
            ("young_spruce", 401, 3.0), ("young_spruce", 402, 2.2), ("young_spruce", 403, 3.8)]
SRC_HASH = hashlib.sha1((ROOT / "construction" / "trees.py").read_bytes() + Path(__file__).read_bytes()).hexdigest()[:12]


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.tile_size = 256
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dev; prefs.get_devices()
            for d in prefs.devices:
                d.use = True
            break
        except Exception:
            continue
    lib = bc.collection("tree_lib")
    work = bc.collection("work")
    meta = []
    for i, (kind, seed, H) in enumerate(VARIANTS):
        base_kind = "spruce" if kind.startswith("young_spruce") else kind
        for lod in (0, 1):
            c = bc.collection(f"v{i:02d}_L{lod}", lib)
            root, Hr, n = trees.make_tree(base_kind, seed, c, H=H, lod=lod)
        # LOD 2: impostor baked from LOD 0
        c0 = bpy.data.collections[f"v{i:02d}_L0"]
        root0 = next(o for o in c0.objects if o.type == "EMPTY")
        files, w, h = trees.bake_impostor(root0, H, str(IMP / f"v{i:02d}"))
        c2 = bc.collection(f"v{i:02d}_L2", lib)
        trees.impostor_object(f"v{i:02d}_imp", files, w, h, c2)
        meta.append({"index": i, "kind": kind, "seed": seed, "height": H})
        print("variant", i, kind, H, "shoots", n)
    bpy.data.collections.remove(work)
    lib["src_hash"] = SRC_HASH
    lib["variants"] = json.dumps(meta)
    lib.use_fake_user = True  # kept in the file although no scene uses it directly
    sc.collection.children.unlink(lib)  # not rendered directly: instanced by the scatter
    bpy.data.use_autopack = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "tree_lib.blend"))
    print("tree library", len(VARIANTS), "variants ->", OUT / "tree_lib.blend", SRC_HASH)


if __name__ == "__main__":
    build()

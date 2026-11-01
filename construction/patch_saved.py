"""Bring the saved stage scene up to the current model without rebuilding it (Roman 2026-10-30: "aren't the 3d geometries already
saved in the file so it is just putting them into position?"). The saved .blend keeps every built piece; this moves what moved:

  - the gym equipment: the instances re-placed from model/layouts/gym_f*.json, the built prototypes reused (a new piece builds)
  - the building elements: the ones that changed since the scene's model are rebuilt (linings, plain walls, slabs + patterned floors with their holes)
  - the furnishings (lights, wipes, ...): matched by content; the ones that moved or changed are re-placed, their prototypes reused

    systemd-run --user --scope -p MemoryMax=12G -p MemorySwapMax=0 nice -n 19 \
        blender -b construction/out/stage_5.blend -t 12 --python construction/patch_saved.py -- 5 [base git rev] [--rebuild=kind,kind]

The scene's model is the "model_base.json" text the full build saves (scene.py), else model/building.json at the given git rev.
A changed element of a kind this can't rebuild (stairs, glazing, walls with openings) exits 2: run the full build then.
"""
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "construction"))
import bl_common as bc  # noqa: E402
import equipment_place  # noqa: E402
import furniture  # noqa: E402

T0 = time.time()
args = sys.argv[sys.argv.index("--") + 1:]
STAGE = int(args[0])
REBUILD = {k for a_ in args[1:] if a_.startswith("--rebuild=") for k in a_.split("=", 1)[1].split(",")}   # kinds whose builder code
# changed (same parameters, so they'd otherwise keep their saved prototype): dropped and built again
model = json.loads((ROOT / "model" / "building.json").read_text())
if "model_base.json" in bpy.data.texts:
    base = json.loads(bpy.data.texts["model_base.json"].as_string())
else:
    base = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{[a_ for a_ in args[1:] if not a_.startswith('--')][0]}:model/building.json"]))


def objs_of(id_):
    return [o for o in bpy.data.objects if o.name == id_ or o.name.startswith(id_ + "_")]


def drop(obs):
    for o in obs:
        bpy.data.objects.remove(o, do_unlink=True)


# ---- building elements: rebuild the changed ones
PHASES = {1: "1 · foundations", 3: "3 · structure", 4: "4 · envelope", 5: "5 · interior shell"}
old_e = {e["id"]: e for e in base["elements"] if e.get("phase", 0) <= STAGE}
new_e = {e["id"]: e for e in model["elements"] if e.get("phase", 0) <= STAGE}
mat_of = {}                                                    # an element material key -> the scene's material
for i, e in old_e.items():
    o = bpy.data.objects.get(i)
    if o and o.type == "MESH" and o.data.materials and e["material"] not in mat_of:
        mat_of[e["material"]] = o.data.materials[0]
felt = next((o.data.materials[0] for o in bpy.data.objects if o.name.endswith("_backing") and o.type == "MESH" and o.data.materials), None)
def norm(e):                                                   # the same opening twice is the same wall (a re-run can append one)
    return {**e, "openings": sorted({json.dumps(o, sort_keys=True) for o in e.get("openings", [])})}
changed = [i for i in new_e if i not in old_e or norm(new_e[i]) != norm(old_e[i])]
gone = [i for i in old_e if i not in new_e]
plain = lambda e: (e["type"] == "wall" and e.get("kind") == "lining") or \
    (e["type"] == "wall" and not e.get("openings") and "mullions" not in e and e.get("kind") != "clad") or \
    (e["type"] == "slab" and "rect" in e and "pattern" not in e) or \
    (e["type"] == "slab" and e.get("pattern", {}).get("kind") in ("boards", "slabs", "poured"))   # (floors with holes: bc.floor_slab / rect_slab, as scene.py)
bad = [i for i in changed if not plain(new_e[i]) or new_e[i]["material"] not in mat_of]
if bad:
    print("patch: can't rebuild these here, run the full build:", bad[:8]); sys.exit(2)
prng = np.random.default_rng(55)
for i in gone + changed:
    drop(objs_of(i))
for i in changed:
    e = new_e[i]; mat = mat_of[e["material"]]; coll = bpy.data.collections[PHASES[e["phase"]]]; z0, z1 = e["z"]
    if e["type"] == "wall" and e.get("kind") == "lining":
        bc.pattern_lining(e, mat, coll, prng, backing_mat=felt)
    elif e["type"] == "wall":
        bc.oriented_box(e["id"], e["from"], e["to"], e["size"][0], z0, z1, mat, coll)
    elif "pattern" in e:
        bc.floor_slab(e, mat, coll, prng)
    else:
        bc.rect_slab(e, mat, coll)
print(f"patch: elements {len(changed)} rebuilt, {len(gone)} removed ({time.time() - T0:.0f} s)")

# ---- furnishings: match by content (their ids are sequence numbers, so they shift); re-place the rest
sig = lambda f: json.dumps({k: v for k, v in f.items() if k != "id"}, sort_keys=True)
old_f = [f for f in base.get("furnishings", []) if f.get("phase", 5) <= STAGE]
new_f = [f for f in model.get("furnishings", []) if f.get("phase", 5) <= STAGE]
pool = {}
for f in old_f:
    if f["kind"] not in REBUILD:
        pool.setdefault(sig(f), []).append(f["id"])
stale_rb = [f["id"] for f in old_f if f["kind"] in REBUILD]
keep, add = {}, []                                             # new id -> old id
for f in new_f:
    s = sig(f)
    if pool.get(s):
        keep[f["id"]] = pool[s].pop()
    else:
        add.append(f)
stale = [i for ids in pool.values() for i in ids] + stale_rb
for f in old_f:                                                # the scene's prototypes, by the key furniture.build_all uses
    o = bpy.data.objects.get(f["id"])
    if o and o.instance_collection and f["kind"] not in REBUILD:
        furniture.PROTO.setdefault(furniture.proto_key(f)[1], o.instance_collection)
fcoll = bpy.data.collections["5b · furniture + fixtures"]
for i in stale:
    drop([o for o in (bpy.data.objects.get(i), bpy.data.objects.get(i + "_light")) if o])
moved = {}
for new_id, old_id in keep.items():                            # free the names first: two-step rename
    for suf in ("", "_light"):
        o = bpy.data.objects.get(old_id + suf)
        if o:
            o.name = f"__patch_{new_id}{suf}"; moved[new_id + suf] = o
for nm, o in moved.items():
    o.name = nm
mats = {m.name: m for m in bpy.data.materials}
n_add = furniture.build_all({**model, "furnishings": add}, mats, fcoll) if add else 0
print(f"patch: furnishings {len(keep)} kept, {len(stale)} removed, {n_add} placed ({time.time() - T0:.0f} s)")

# ---- the gym equipment: every instance re-placed from the layouts, the prototypes reused
ecoll = bpy.data.collections["5b · gym equipment"]
drop(list(ecoll.objects))
n_eq = equipment_place.build(model, ecoll, floors=("gym_f1", "gym_f2", "gym_f3"))
for lc in bpy.context.view_layer.layer_collection.children:
    if lc.name.startswith("eq_prototypes"):
        lc.exclude = True
used = {o.instance_collection for o in bpy.data.objects if o.instance_collection}
for c in [c for c in bpy.data.collections if c.name.startswith("eq_maze-") and c not in used]:   # replaced PWR Play modules
    drop(list(c.all_objects)); bpy.data.collections.remove(c)
for c in [c for c in bpy.data.collections if c.name.startswith("eq_prototypes") and not c.children and not c.objects]:
    bpy.data.collections.remove(c)
print(f"patch: equipment {n_eq} placed ({time.time() - T0:.0f} s)")

# ---- cameras defined since the scene was built (scene.py CAMS)
import ast  # noqa: E402
src = (ROOT / "construction" / "scene.py").read_text()
CAMS = ast.literal_eval(next(n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CAMS"))
new_cams = [n for n in CAMS if f"cam_{n}" not in bpy.data.objects]
for n in new_cams:
    bc.camera(bpy.context.scene, f"cam_{n}", *CAMS[n])
print(f"patch: cameras added {new_cams}")

if "model_base.json" in bpy.data.texts:
    bpy.data.texts.remove(bpy.data.texts["model_base.json"])
bpy.data.texts.new("model_base.json").write(json.dumps(model))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(f"patch: saved {bpy.data.filepath} ({time.time() - T0:.0f} s)")

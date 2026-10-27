"""The wall-mounted pieces' own sizes, without their display wall (for the gym plans: tools/gym_layout.py).

    blender -b --factory-startup --python equipment/tools/wall_survey.py

Builds each piece that hangs on a display wall section with k.display = False and measures it: the wall's face is the
model's y = 0, the piece stands out to -y. Writes equipment/lineups/wall_sizes.json {piece: {w, d, z0, z1}}. No render.
"""
import importlib.util
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

EQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EQ / "blender"))
import kit  # noqa: E402

out = {}
for d in sorted((EQ / "pieces").iterdir()):
    f = d / "model.py"
    if not f.exists() or 'getattr(k, "display", True)' not in f.read_text():
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    spec = importlib.util.spec_from_file_location(f"pm_{d.name}", f)
    pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
    coll = bpy.data.collections.new(d.name); sc.collection.children.link(coll)
    k = kit.Kit(d.name, coll, getattr(pm, "LOOK", None))
    k.check = lambda: None
    k.display = False
    pm.build(k)
    obs = k.finish()
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(b) for o in obs if o.type == "MESH" for b in o.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    out[d.name] = dict(w=round(x1 - x0, 3), d=round(max(0.0, y1) - y0, 3), z0=round(min(p.z for p in pts), 3), z1=round(max(p.z for p in pts), 3))
    print(d.name, out[d.name], flush=True)
(EQ / "lineups" / "wall_sizes.json").write_text(json.dumps(out, indent=1))

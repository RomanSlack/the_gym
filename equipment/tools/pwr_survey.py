"""The PWR Play stations' plan footprints, for laying the maze out in 2D (tools/gym_layout.py).

    blender -b --factory-startup --python equipment/tools/pwr_survey.py

Builds a bare Core, then one Core per station with that station on its S face, and measures how far the station
reaches past the Core (out of the face, and across it). Writes equipment/lineups/pwr_play_stations.json:
{"core": [w, d], "spacing": {connector: m}, "stations": {name: {"out": m from the Core's centre, "half": m either side}}}.
No render.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

EQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EQ / "blender"))
import kit  # noqa: E402
import pwr_play as pp  # noqa: E402

STATIONS = ["pulldown", "row", "triceps", "adjustable", "crossover", "dualhigh", "duallow", "dip", "panel", "step",
            "handles", "stallbars", "ropepull", "powerpivot", "dipchin"]


def bounds(layout, name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    coll = bpy.data.collections.new(name); sc.collection.children.link(coll)
    k = kit.Kit(name, coll, pp.LOOK)
    k.check = lambda: None
    pp.build_layout(k, layout)
    obs = k.finish()
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(b) for o in obs if o.type == "MESH" for b in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts))


core = bounds(dict(cores={"A": (0.0, 0.0)}, faces={}, bars=[]), "core")
out = {"core": [round(core[1] - core[0], 3), round(core[3] - core[2], 3)],
       "spacing": {c: round(pp.spacing(c), 3) for c in pp.CONNECTORS}, "stations": {}}
for st in STATIONS:
    x0, x1, y0, y1 = bounds(dict(cores={"A": (0.0, 0.0)}, faces={("A", "S"): st}, bars=[]), st)
    out["stations"][st] = {"out": round(max(-y0, -core[2]), 3), "half": round(max(-x0, x1, core[1]), 3)}
    print(st, out["stations"][st], flush=True)
(EQ / "lineups" / "pwr_play_stations.json").write_text(json.dumps(out, indent=1))
print("wrote", EQ / "lineups" / "pwr_play_stations.json")

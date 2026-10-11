"""Generate the structural grid and columns from model.structure (design parameters)
into model.grids and model.elements. Re-run after changing model.structure.

python3 tools/structure.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
S = m["structure"]
lv = {l["id"]: l["elevation"] for l in m["levels"]}
grids, elements = [], [e for e in m.get("elements", []) if e.get("type") != "column"]

for wing in S["wings"]:
    xs, ys = wing["x_lines"], wing["y_lines"]
    ext = 4.0  # grid lines run a little past the building, with bubbles at the ends
    for name, x in zip(wing["x_names"], xs):
        grids.append({"id": name, "from": [x, ys[-1] - ext], "to": [x, ys[0] + ext]})
    for name, y in zip(wing["y_names"], ys):
        grids.append({"id": name, "from": [xs[0] - ext, y], "to": [xs[-1] + ext, y]})
    for tier in wing["column_tiers"]:
        z0, z1 = lv[tier["from"]], lv[tier["to"]] if tier["to"] in lv else tier["to"]
        for xn, x in zip(wing["x_names"], xs):
            if xn not in tier["x_names"]:
                continue
            for yn, y in zip(wing["y_names"], ys):
                elements.append({"id": f"C-{xn}{yn}-{tier['from']}", "type": "column", "material": tier["material"],
                                 "at": [x, y], "size": tier["size"], "z": [round(z0, 2), round(z1 - tier.get("top_gap", 0), 2)]})

m["grids"] = grids
m["elements"] = elements
modelio.save(m)
print(len(grids), "grid lines,", sum(e["type"] == "column" for e in elements), "columns")

"""Room numbers: <level>.<nn>, numbered north-to-south then west-to-east within each level
(cores/shafts are numbered last). Writes space["number"].

python3 tools/annotate.py   (last step of tools/build_model.py)
"""
import sys
from pathlib import Path
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "terrain"))
import modelio  # noqa: E402

m = modelio.load()
for L in sorted({s["level"] for s in m["spaces"]}):
    S = [s for s in m["spaces"] if s["level"] == L]
    key = lambda s: (s["kind"] == "core", -round(Polygon(s["poly"]).centroid.y / 4), Polygon(s["poly"]).centroid.x)
    for i, s in enumerate(sorted(S, key=key), 1):
        s["number"] = f"{L}.{i:02d}"
modelio.save(m)
print("numbered", len(m["spaces"]), "rooms")

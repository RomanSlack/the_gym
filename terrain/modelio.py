"""Read/write model/building.json with compact, diff-friendly formatting:
objects and arrays that hold only scalars (or short coordinate pairs) stay on one line."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "model" / "building.json"


def _flat(v):
    if isinstance(v, list):
        return all(not isinstance(x, (dict, list)) or (isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x)) for x in v)
    if isinstance(v, dict):
        return all(not isinstance(x, (dict, list)) or (isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x)) for x in v.values())
    return True


def _dump(v, ind=0):
    pad, pad1 = "  " * ind, "  " * (ind + 1)
    if _flat(v) and len(json.dumps(v, ensure_ascii=False)) < 230:
        return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))
    if isinstance(v, dict):
        return "{\n" + ",\n".join(f"{pad1}{json.dumps(k)}: {_dump(x, ind + 1)}" for k, x in v.items()) + f"\n{pad}}}"
    if isinstance(v, list):
        return "[\n" + ",\n".join(pad1 + _dump(x, ind + 1) for x in v) + f"\n{pad}]"
    return json.dumps(v, ensure_ascii=False)


def load():
    return json.loads(PATH.read_text())


def save(m):
    PATH.write_text(_dump(m) + "\n")

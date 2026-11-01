"""Make Blender's glTF exports load in strict readers (scenewalk / Bevy): Blender writes "texCoord": -1 on textures it projects
without UVs (box-mapped PBR materials), which the spec doesn't allow; drop it (the default, UV 0). Rewrites the .glb's JSON chunk.

    python3 tools/gltf_fix.py file.glb [...]
"""
import json
import struct
import sys


def _clean(o):
    if isinstance(o, dict):
        if isinstance(o.get("texCoord"), int) and o["texCoord"] < 0:
            del o["texCoord"]
        for v in o.values():
            _clean(v)
    elif isinstance(o, list):
        for v in o:
            _clean(v)


def fix(path):
    b = open(path, "rb").read()
    magic, ver, _ = struct.unpack("<III", b[:12])
    ln, typ = struct.unpack("<II", b[12:20])
    j = json.loads(b[20:20 + ln])
    _clean(j)
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    rest = b[20 + ln:]
    out = struct.pack("<III", magic, ver, 12 + 8 + len(js) + len(rest)) + struct.pack("<II", len(js), typ) + js + rest
    open(path, "wb").write(out)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix(p)

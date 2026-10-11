"""Fetch the downloaded inputs listed in assets/manifest.json (textures, HDRIs; all CC0) into ~/.cache/the_gym/.
Nothing downloaded is committed: the repo is public and every model is generated in this project.

python3 tools/assets.py            fetch whatever is missing
Textures land in ~/.cache/the_gym/textures/<source>/<id>/<map>.<ext>  (map = diff, nor_gl, rough, disp, ao, arm)
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".cache" / "the_gym"
MAPS = {"Diffuse": "diff", "nor_gl": "nor_gl", "Rough": "rough", "Displacement": "disp", "AO": "ao", "arm": "arm"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "the_gym-assets/1.0"}), timeout=60) as r:
        return r.read()


def polyhaven(tid, res):
    out = CACHE / "textures" / "polyhaven" / tid
    files = json.loads(get(f"https://api.polyhaven.com/files/{tid}"))
    got = []
    for key, name in MAPS.items():
        if key not in files or res not in files[key]:
            continue
        fmt = "jpg" if "jpg" in files[key][res] else "png"
        dst = out / f"{name}.{fmt}"
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(get(files[key][res][fmt]["url"]))
        got.append(name)
    return got


def texture_dir(tid, source="polyhaven"):
    return CACHE / "textures" / source / tid


if __name__ == "__main__":
    man = json.loads((ROOT / "assets" / "manifest.json").read_text())
    for t in man["textures"]:
        if t["source"] == "polyhaven":
            print(t["id"], polyhaven(t["id"], t["res"]))
    sys.exit(0)

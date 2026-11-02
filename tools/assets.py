"""Fetch the downloaded inputs listed in assets/manifest.json (textures, HDRIs; all CC0) into ~/.cache/the_gym/.
Nothing downloaded is committed: the repo is public and every model is generated in this project.

python3 tools/assets.py            fetch whatever is missing
Textures land in ~/.cache/the_gym/textures/<source>/<id>/<map>.<ext>  (map = diff, nor_gl, rough, disp, ao, arm)
HDRIs land in ~/.cache/the_gym/hdris/<source>/<id>_<res>.hdr
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


def polyhaven_hdri(hid, res):
    dst = CACHE / "hdris" / "polyhaven" / f"{hid}_{res}.hdr"
    if not dst.exists():
        files = json.loads(get(f"https://api.polyhaven.com/files/{hid}"))
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(get(files["hdri"][res]["hdr"]["url"]))
    return dst


def derive_gridless(src, dst, box):
    """A texture with a tile grid baked in (e.g. granite_tile_03), made gridless: one clean tile cut out (box = l, t, r, b in px)
    and mirror-tiled 2 x 2, seamless in every direction; the normal map's x / y flipped where the copy is mirrored."""
    from PIL import Image, ImageOps
    s_, d_ = CACHE / "textures" / "polyhaven" / src, CACHE / "textures" / "polyhaven" / dst
    if (d_ / "diff.jpg").exists():
        return
    d_.mkdir(parents=True, exist_ok=True)
    for name in ("diff", "rough", "nor_gl"):
        c = Image.open(s_ / f"{name}.jpg").convert("RGB").crop(box)
        fx, fy = ImageOps.mirror(c), ImageOps.flip(c)
        fxy = ImageOps.flip(fx)
        if name == "nor_gl":
            inv = lambda im, ch: Image.merge("RGB", [ImageOps.invert(b) if i in ch else b for i, b in enumerate(im.split())])
            fx, fy, fxy = inv(fx, (0,)), inv(fy, (1,)), inv(fxy, (0, 1))
        w, h = c.size
        out = Image.new("RGB", (2 * w, 2 * h))
        out.paste(c, (0, 0)); out.paste(fx, (w, 0)); out.paste(fy, (0, h)); out.paste(fxy, (w, h))
        out.resize((2048, 2048), Image.LANCZOS).save(d_ / f"{name}.jpg", quality=95)


def ambientcg(tid, res):
    """ambientCG's zip (PNG maps) -> the same map names as Poly Haven's (diff, nor_gl, rough, disp, ao)."""
    import io, zipfile
    out = CACHE / "textures" / "ambientcg" / tid
    names = {"Color": "diff", "NormalGL": "nor_gl", "Roughness": "rough", "Displacement": "disp", "AmbientOcclusion": "ao"}
    if all(any(out.glob(f"{n}.*")) for n in ("diff", "nor_gl", "rough", "disp")):
        return sorted(p_.stem for p_ in out.iterdir())
    z = zipfile.ZipFile(io.BytesIO(get(f"https://ambientcg.com/get?file={tid}_{res}-PNG.zip")))
    out.mkdir(parents=True, exist_ok=True)
    for f in z.namelist():
        for key, name in names.items():
            if f.endswith(f"_{key}.png"):
                (out / f"{name}.png").write_bytes(z.read(f))
    return sorted(p_.stem for p_ in out.iterdir())


def texture_dir(tid, source="polyhaven"):
    return CACHE / "textures" / source / tid


if __name__ == "__main__":
    man = json.loads((ROOT / "assets" / "manifest.json").read_text())
    for t in man["textures"]:
        if t["source"] == "polyhaven":
            print(t["id"], polyhaven(t["id"], t["res"]))
        elif t["source"] == "ambientcg":
            print(t["id"], ambientcg(t["id"], t["res"]))
    derive_gridless("granite_tile_03", "granite_flamed_gridless", (24, 24, 660, 1000))   # the F4 deck: one clean slab of it
    for h in man.get("hdris", []):
        if h["source"] == "polyhaven":
            print(h["id"], polyhaven_hdri(h["id"], h["res"]))
    sys.exit(0)

"""Put a piece's reference photos beside our latest renders, pair by pair, on one sheet (the 'compare before showing'
step of the README's attention to detail).

    python3 equipment/tools/compare.py <piece> <ref>:<view> [<ref>:<view> ...] [--v NNN] [--out path]

e.g. compare.py hammer-strength-plate-loaded-hack-squat 02:side 01:three_quarter: each row is refs/ref_02 | our side.
Writes /tmp/compare_<piece>.jpg by default (a working sheet, not a deliverable) and prints its path.
"""
import glob
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

EQ = Path(__file__).resolve().parent.parent
W = 800


def fit(im):
    im = ImageOps.exif_transpose(im)          # phone photos are stored sideways with an orientation tag
    return im.convert("RGB").resize((W, int(im.height * W / im.width)))


def main():
    args = sys.argv[1:]
    piece = args.pop(0)
    v = out = None
    if "--v" in args:
        i = args.index("--v"); v = args[i + 1]; del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    d = EQ / "pieces" / piece
    if v is None:
        vs = sorted({re.search(r"_v(\d{3})\.jpg$", f).group(1) for f in glob.glob(str(d / "models" / "*_v[0-9][0-9][0-9].jpg"))})
        v = vs[-1]
    rows = []
    for pair in args:
        ref, view = pair.split(":")
        rf = glob.glob(str(d / "refs" / f"ref_{ref}.*"))[0]
        ours = d / "models" / f"{piece}_{view}_v{v}.jpg"
        rows.append((fit(Image.open(rf)), fit(Image.open(ours))))
    H = sum(max(a.height, b.height) for a, b in rows)
    sheet = Image.new("RGB", (2 * W, H), "white")
    y = 0
    for a, b in rows:
        sheet.paste(a, (0, y)); sheet.paste(b, (W, y)); y += max(a.height, b.height)
    out = out or f"/tmp/compare_{piece}.jpg"
    sheet.save(out, quality=88)
    print(out, f"(v{v})")


if __name__ == "__main__":
    main()

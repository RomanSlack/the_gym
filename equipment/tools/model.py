"""Model one piece: one new version (views + .glb) in the studio, then a comparison sheet (the real product above, ours below).

    python3 equipment/tools/model.py <piece> [draft]

-> equipment/pieces/<piece>/models/<piece>_<view>_vNNN.jpg, <piece>_vNNN.glb, <piece>_sheet_vNNN.jpg (never overwritten).
The sheet's photos are piece.json "sheet_refs" (file names in refs/) or the first three. Exit code 3 = no GPU: stop
and tell Roman (usually a driver update without a reboot); never render on the CPU.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EQ / "tools"))
import versions  # noqa: E402

piece, rest = sys.argv[1], sys.argv[2:]
v = versions.next_version(piece)
r = subprocess.run(["nice", "-n", "19", "blender", "-b", "--factory-startup", "-t", "12", "--python-exit-code", "1", "--python",
                    str(EQ / "blender" / "studio.py"), "--", piece, str(v), *rest])
if r.returncode == 3:
    sys.exit("!! NO GPU: tell Roman (driver update without a reboot?); nothing rendered")
if r.returncode or not [1 for vv, _, _ in versions.versions(piece) if vv == v]:
    sys.exit(f"blender failed ({r.returncode}): no sheet")

pc = json.loads((EQ / "pieces" / piece / "piece.json").read_text())
refs_dir = EQ / "pieces" / piece / "refs"
names = pc.get("sheet_refs") or [Path(x["file"]).name for x in pc.get("refs", [])][:3]
refs = [refs_dir / n for n in names if (refs_dir / n).exists()]
order = ["three_quarter", "front", "side", "back_three_quarter"]
ours = sorted(versions.versions(piece), key=lambda t: (order.index(t[1]) if t[1] in order else 9, t[1]))
ours = [f for vv, view, f in ours if vv == v and view != "sheet"][:4]

W, cell = 2400, 600
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
fontb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 40)
rows = [refs, ours] if refs else [ours]
H = 110 + len(rows) * (cell + 50)
sheet = Image.new("RGB", (W, H), (20, 19, 18))
d = ImageDraw.Draw(sheet)
price = pc.get("price")
d.text((40, 30), f"{pc['model']}  ·  v{v:03d}", font=fontb, fill=(233, 228, 220))
d.text((W - 40, 42), (f"{price['currency']} {price['amount']:,.0f}  ·  " if price else "") + pc["brand"], font=font, fill=(201, 164, 106), anchor="ra")
y = 110
for label, row in (("the real one", refs), ("ours", ours)):
    if not row:
        continue
    d.text((40, y), label, font=font, fill=(141, 134, 124))
    n = max(len(row), 3 if label == "the real one" else 4)
    cw = (W - 80 - (n - 1) * 20) // n
    for i, f in enumerate(row):
        im = Image.open(f)
        if im.mode in ("RGBA", "LA", "P"):  # transparent product shots go on white, like the shop shows them
            im = im.convert("RGBA"); w_ = Image.new("RGBA", im.size, (255, 255, 255, 255)); w_.alpha_composite(im); im = w_
        im = im.convert("RGB")
        im.thumbnail((cw, cell))
        bg = Image.new("RGB", (cw, cell), (244, 242, 238) if label == "the real one" else (20, 19, 18))
        bg.paste(im, ((cw - im.width) // 2, (cell - im.height) // 2))
        sheet.paste(bg, (40 + i * (cw + 20), y + 40))
    y += cell + 50
out = versions.path(piece, "sheet", v)
sheet.save(out, quality=90)
print("sheet:", out)

# the overlays, one per reference photo: the photo | ours from its camera | both, ours at half with its outline in red
mfile = EQ / "pieces" / piece / "match.json"
if mfile.exists():
    from PIL import ImageFilter, ImageChops
    MJ = json.loads(mfile.read_text())
    for vi, vw in enumerate(MJ.get("views") or [MJ]):
        raw = EQ / ".cache" / f"match_{piece}_{vi}.png"
        if not raw.exists() or raw.stat().st_mtime < out.stat().st_mtime - 600:
            continue
        ref = Image.open(refs_dir / vw["ref"]).convert("RGBA")
        w_ = Image.new("RGBA", ref.size, (255, 255, 255, 255)); w_.alpha_composite(ref); ref = w_
        ours_ = Image.open(raw).convert("RGBA").resize(ref.size)
        alone = Image.new("RGBA", ref.size, (255, 255, 255, 255)); alone.alpha_composite(ours_)
        a = ours_.getchannel("A").point(lambda x: 255 if x > 40 else 0)
        edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(5)), a)
        ov = ref.copy(); half = ours_.copy(); half.putalpha(ours_.getchannel("A").point(lambda x: x // 2)); ov.alpha_composite(half)
        ov.paste((230, 20, 20, 255), (0, 0), edge)
        side = 1000
        sheet2 = Image.new("RGB", (3 * side + 80, side + 90), (20, 19, 18)); d2 = ImageDraw.Draw(sheet2)
        for i, (lab, im) in enumerate((("the real one", ref), ("ours, same camera", alone), ("overlay: ours at half, outline red", ov))):
            sheet2.paste(im.convert("RGB").resize((side, side)), (20 + i * (side + 20), 70))
            d2.text((20 + i * (side + 20), 25), lab, font=font, fill=(141, 134, 124))
        errs = vw.get("errors_px", {})
        if errs:
            d2.text((3 * side + 60, 25), f"anchors off by {(sum(e * e for e in errs.values()) / len(errs)) ** 0.5:.0f} px rms", font=font, fill=(201, 164, 106), anchor="ra")
        mo = versions.path(piece, "match" if vi == 0 else f"match{vi + 1}", v)
        sheet2.save(mo, quality=90)
        print("match:", mo)

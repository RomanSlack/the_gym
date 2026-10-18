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

# the drawings sheet: the orthographic reference views we generated (refs/gen/ortho*.png) above, ours from the same sides below
gen = {"ortho_side": "orthosideleft_0.png", "ortho_front": "orthofront_0.png", "ortho_rear": "orthorear_0.png", "ortho_top": "orthotop_0.png"}
mine = {view: f for vv, view, f in versions.versions(piece) if vv == v and view in gen}
if mine:
    cell = 640
    sheet3 = Image.new("RGB", (len(mine) * (cell + 20) + 20, 2 * cell + 140), (20, 19, 18)); d3 = ImageDraw.Draw(sheet3)
    d3.text((20, 20), "generated reference drawings (from the real photos)", font=font, fill=(141, 134, 124))
    d3.text((20, cell + 80), f"ours, orthographic, v{v:03d}", font=font, fill=(141, 134, 124))
    for i, view in enumerate(k_ for k_ in gen if k_ in mine):
        for row, f in enumerate((refs_dir / "gen" / gen[view], mine[view])):
            if not f.exists():
                continue
            im = Image.open(f).convert("RGB"); im.thumbnail((cell, cell))
            bg = Image.new("RGB", (cell, cell), (255, 255, 255)); bg.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2))
            sheet3.paste(bg, (20 + i * (cell + 20), 60 + row * (cell + 60)))
    do = versions.path(piece, "drawings", v)
    sheet3.save(do, quality=90)
    print("drawings:", do)

# the drawing overlays: each generated drawing with ours on top, ours stretched to the drawing's own extent on each axis
# (a generated view is not to scale and stretches differently across and up), outline red: shapes, not sizes
if mine:
    from PIL import ImageFilter, ImageChops
    cut = []
    for view in (k_ for k_ in gen if k_ in mine):
        raw, gf = EQ / ".cache" / f"ortho_{piece}_{view}.png", refs_dir / "gen" / gen[view]
        if not raw.exists() or not gf.exists():
            continue
        ref = Image.open(gf).convert("RGB")
        rb = ImageChops.invert(ref.convert("L")).point(lambda x: 255 if x > 25 else 0).getbbox()
        ou = Image.open(raw).convert("RGBA")
        ob = ou.getchannel("A").point(lambda x: 255 if x > 40 else 0).getbbox()
        ou = ou.crop(ob).resize((rb[2] - rb[0], rb[3] - rb[1]))
        lay = Image.new("RGBA", ref.size, (0, 0, 0, 0)); lay.paste(ou, rb[:2])
        a = lay.getchannel("A").point(lambda x: 255 if x > 40 else 0)
        edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(5)), a)
        ov = ref.convert("RGBA"); half = lay.copy(); half.putalpha(lay.getchannel("A").point(lambda x: x // 2)); ov.alpha_composite(half)
        ov.paste((230, 20, 20, 255), (0, 0), edge)
        cut.append((view, ov.convert("RGB")))
    if cut:
        cell = 900
        sheet4 = Image.new("RGB", (len(cut) * (cell + 20) + 20, cell + 90), (20, 19, 18)); d4 = ImageDraw.Draw(sheet4)
        d4.text((20, 20), f"generated drawings with ours over them (each stretched to the drawing's extent), outline red, v{v:03d}", font=font, fill=(141, 134, 124))
        for i, (view, im) in enumerate(cut):
            im.thumbnail((cell, cell)); bg = Image.new("RGB", (cell, cell), (255, 255, 255))
            bg.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2)); sheet4.paste(bg, (20 + i * (cell + 20), 70))
        oo = versions.path(piece, "drawover", v)
        sheet4.save(oo, quality=90)
        print("drawing overlays:", oo)

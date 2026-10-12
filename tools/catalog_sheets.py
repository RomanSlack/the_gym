"""Compose the component-catalogue sheets from the views rendered by construction/catalog.py (one 2 x 2 sheet per piece, labelled,
plus an overview of every piece). Never overwrites: construction/renders/catalog/<kind>_vNNN.jpg, _overview_vNNN.jpg.

terrain/.venv/bin/python tools/catalog_sheets.py construction/out/catalog_tmp/shots.json
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "construction" / "renders" / "catalog"; OUT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font, fontb = ImageFont.truetype(FONT, 22), ImageFont.truetype(FONTB, 30)


def next_name(stem):
    v = 1 + max([int(p.stem.rsplit("_v", 1)[1]) for p in OUT.glob(f"{stem}_v*.jpg") if p.stem.rsplit("_v", 1)[1].isdigit()] or [0])
    return OUT / f"{stem}_v{v:03d}.jpg"


pieces = json.loads(Path(sys.argv[1]).read_text())
# Roman: the catalogue is treasured, nothing temporary. Every single view is also kept as its own versioned file
# (construction/renders/catalog/views/<kind>_<angle>_vNNN.jpg), next to the sheets; the Blender frames folder is only scratch.
VIEWS = OUT / "views"; VIEWS.mkdir(exist_ok=True)
for pc in pieces:
    for label, p in pc["shots"]:
        stem = f"{pc['kind']}_{label.replace('/', '').replace(' ', '')}"
        v = 1 + max([int(q.stem.rsplit("_v", 1)[1]) for q in VIEWS.glob(f"{stem}_v*.jpg") if q.stem.rsplit("_v", 1)[1].isdigit()] or [0])
        Image.open(p).convert("RGB").save(VIEWS / f"{stem}_v{v:03d}.jpg", quality=92)
if "--views-only" in sys.argv:
    sys.exit(0)
sheets = []
for pc in pieces:
    W_, H_ = Image.open(pc["shots"][0][1]).size
    sheet = Image.new("RGB", (2 * W_, 2 * H_ + 90), (246, 243, 238)); dr = ImageDraw.Draw(sheet)
    dr.text((24, 18), pc["kind"].replace("_", " "), fill=(30, 28, 26), font=fontb)
    dr.text((24, 56), pc["note"][:150], fill=(90, 86, 80), font=font)
    for i, (label, p) in enumerate(pc["shots"]):
        x, y = (i % 2) * W_, 90 + (i // 2) * H_
        sheet.paste(Image.open(p).convert("RGB"), (x, y)); dr.text((x + 16, y + 12), label, fill=(40, 38, 36), font=font)
    dst = next_name(pc["kind"]); sheet.save(dst, quality=90); sheets.append((pc["kind"], pc["shots"][0][1])); print("sheet", dst.name)
if len(sheets) > 1:
    cols = 6; rows = math.ceil(len(sheets) / cols); tw, th = 450, 350
    ov = Image.new("RGB", (cols * tw, rows * (th + 34) + 70), (246, 243, 238)); dr = ImageDraw.Draw(ov)
    dr.text((20, 18), "The Gym: component catalogue (every piece designed in this project)", fill=(30, 28, 26), font=fontb)
    for i, (k, p) in enumerate(sheets):
        x, y = (i % cols) * tw, 70 + (i // cols) * (th + 34)
        ov.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y)); dr.text((x + 10, y + th + 4), k.replace("_", " "), fill=(40, 38, 36), font=font)
    dst = next_name("_overview"); ov.save(dst, quality=88); print("overview", dst.name)

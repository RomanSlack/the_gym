"""Progress images for a material study (materials/<name>/): never overwritten, in the replay, viewable as one page.

    python3 tools/material_out.py add nordic_moss refs_sheet img.png "what this shows"   # -> out/refs_sheet_vNNN.jpg
    python3 tools/material_out.py log nordic_moss "a step with no image"
    python3 tools/material_out.py page nordic_moss                                        # rebuild out/index.html
    (name "plants": the plants/ study instead of materials/<name>/)

Every image goes to out/<cam>_vNNN.jpg (the next free version) with a line in PROGRESS.md; out/index.html is static (works
from file://, refreshes itself), newest first. tools/replay/render_history.py picks the committed out/*.jpg up as cameras
"material <name>/<cam>".
"""
import html
import re
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def study(name):
    """materials/<name>/, or a top-level study folder (plants/)"""
    return ROOT / name if name in ("plants",) else ROOT / "materials" / name


def page(name):
    d = study(name)
    out = d / "out"
    imgs = sorted(out.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
    log = (d / "PROGRESS.md").read_text() if (d / "PROGRESS.md").exists() else ""
    notes = dict(re.findall(r"`out/([^`]+)`\s*(?:[:-]\s*)?(.*)", log))
    figs = "\n".join(f'<figure><a href="{p.name}"><img src="{p.name}" loading=lazy></a><figcaption><b>{p.name}</b> {html.escape(notes.get(p.name, ""))}</figcaption></figure>'
                     for p in imgs)
    (out / "index.html").write_text(f"""<!doctype html><meta charset=utf-8><meta http-equiv=refresh content=20><title>{name} · progress</title>
<style>body{{margin:0;background:#141614;color:#d8dcd4;font:14px/1.45 system-ui,sans-serif}}
header{{background:#1c1f1b;padding:10px 16px}}h1{{font-size:16px;margin:0}}
details{{padding:8px 16px;color:#9aa594}}pre{{white-space:pre-wrap;font-size:13px;max-width:1100px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,560px),1fr));gap:14px;padding:14px}}
figure{{margin:0;background:#1c1f1b;border-radius:6px;overflow:hidden}}img{{width:100%;display:block}}
figcaption{{padding:6px 10px;font-size:12.5px;color:#aab3a4}}figcaption b{{color:#d8dcd4;font-weight:600}}</style>
<header><h1>{name.replace('_', ' ')}: {len(imgs)} images, newest first (refreshes every 20 s; click an image for full size)</h1></header>
<details open><summary>Progress log</summary><pre>{html.escape(log)}</pre></details>
<main>{figs}</main>""")


def add(name, cam, src, note=""):
    d = study(name)
    out = d / "out"
    out.mkdir(parents=True, exist_ok=True)
    n = max([int(m.group(1)) for p in out.glob(f"{cam}_v*.jpg") if (m := re.search(r"_v(\d{3})\.jpg$", p.name))] or [0]) + 1
    dst = out / f"{cam}_v{n:03d}.jpg"
    im = Image.open(src).convert("RGB")
    im.thumbnail((2400, 2400))
    im.save(dst, quality=88)
    log(name, f"`out/{dst.name}` {note}".strip())
    return dst


def log(name, text):
    d = study(name)
    with open(d / "PROGRESS.md", "a") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} {text}\n")
    page(name)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["add"] and len(a) >= 4:
        print(add(a[1], a[2], a[3], " ".join(a[4:])))
    elif a[:1] == ["log"] and len(a) >= 3:
        log(a[1], " ".join(a[2:]))
    elif a[:1] == ["page"] and len(a) == 2:
        page(a[1])
    else:
        sys.exit(__doc__)

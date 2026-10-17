"""The equipment replay: how the equipment was curated, then how each piece was modelled. Separate from the building.

    python3 equipment/replay/build.py [equipment_dir]    then open equipment/replay/out/index.html

Reads list.json + picks.json, the curation log (history/curation.jsonl: every click on the shopping page, timed),
the product photos fetched into refs/, and the model renders in models/<item>/<item>_<view>_vNNN.jpg with the
prompt behind each version from git (Prompt / Also-Prompt trailers, like tools/replay/render_history.py).
One static page, three views: Curation (the list filling up over time), Piece (one item: its finds, then every model
version), Overview (product beside model). V = video mode for screen recording.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EQ = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = EQ / "replay" / "out"
OUT.mkdir(parents=True, exist_ok=True)
rel = lambda p: os.path.relpath(p, OUT)


def jload(p, default):
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


lst = jload(EQ / "list.json", {"categories": []})
picks = jload(EQ / "picks.json", {"items": {}, "custom": []})
events = []
log = EQ / "history" / "curation.jsonl"
for line in (log.read_text().splitlines() if log.exists() else []):
    try:
        events.append(json.loads(line))
    except Exception:
        pass  # a half-written last line never breaks the replay

# items: the master list + anything Roman added (custom items appear in the curation at the moment he added them)
cats = []
for c in lst["categories"]:
    cats.append({"id": c["id"], "name": c["name"], "items": [{k: i.get(k) for k in ("id", "name", "qty", "zone", "maybe")} for i in c["items"]]})
byid = {c["id"]: c for c in cats}
for x in picks.get("custom", []) + [e for e in events if e.get("action") == "add_item"]:
    c = byid.get(x.get("cat"))
    if c and x["id"] not in [i["id"] for i in c["items"]]:
        c["items"].append({"id": x["id"], "name": x["name"], "qty": x.get("qty", 1), "zone": x.get("zone", ""), "custom": True})

# a ref image only counts if the file is on disk (refs/ is git-ignored, so a fresh clone has none)
for e in events:
    if e.get("ref"):
        e["ref"] = rel(EQ / e["ref"]) if (EQ / e["ref"]).exists() else None

# play time: real gaps squeezed so the replay keeps moving (a pause of hours plays as ~1.2 s, a burst stays a burst)
def ts(e):
    try:
        return datetime.fromisoformat(e["t"]).timestamp()
    except Exception:
        return 0.0
play, last = 0.0, None
for e in events:
    t = ts(e)
    if last is not None:
        play += min(1.2, max(0.12, (t - last) / 20))
    e["p"], last = round(play, 3), t

# model versions from git (prompt per version) + whatever is on disk but not committed yet
def git(*a):
    try:
        return subprocess.run(["git", "-C", str(EQ), *a], capture_output=True, timeout=60).stdout.decode(errors="ignore")
    except Exception:
        return ""
models = {}
pat = re.compile(r"^(.+?)_(.+)_v(\d{3})$")
def add_render(f, meta):
    item = f.parent.name
    m = pat.match(f.stem)
    if not m or m.group(1) != item:
        return
    vs = models.setdefault(item, {})
    v = vs.setdefault(int(m.group(3)), {"v": int(m.group(3)), "views": {}, **meta})
    v["views"].setdefault(m.group(2), rel(f))
    for k, val in meta.items():
        if val and not v.get(k):
            v[k] = val
top = git("rev-parse", "--show-toplevel").strip()
if top:
    recs = git("log", "--reverse", "--format=%H%x1f%ad%x1f%s%x1f%(trailers:key=Prompt,valueonly)%x1f%(trailers:key=Also-Prompt,valueonly)%x1e",
               "--date=format:%Y-%m-%d %H:%M", "--", "models/")
    for rec in recs.split("\x1e"):
        if not rec.strip():
            continue
        h, date, subj, prompt, also = (rec.strip("\n").split("\x1f") + [""] * 5)[:5]
        for n in git("diff-tree", "--no-commit-id", "--name-only", "-r", "--diff-filter=A", h).split():
            f = Path(top) / n
            if f.suffix == ".jpg" and f.exists() and EQ / "models" in f.parents:
                add_render(f, {"date": date, "commit": h[:8], "subject": subj, "prompt": prompt.strip(),
                               "also": [a.strip() for a in also.splitlines() if a.strip()]})
for f in sorted((EQ / "models").glob("*/*.jpg")) if (EQ / "models").exists() else []:
    add_render(f, {"date": "", "commit": "", "subject": "(not committed yet)", "prompt": "", "also": []})
models = {k: [vs[v] for v in sorted(vs)] for k, vs in models.items()}

data = json.dumps({"cats": cats, "events": events, "models": models}, ensure_ascii=False).replace("</", "<\\/")
html = (Path(__file__).with_name("template.html")).read_text().replace("/*DATA*/null", data)
(OUT / "index.html").write_text(html)
n = sum(len(c["items"]) for c in cats)
print(f"equipment replay: {n} items, {len(events)} curation events, {sum(len(v) for v in models.values())} model versions -> {OUT / 'index.html'}")

"""Render replay: every version of every construction render, from git history, with the prompt(s) behind it.

Walks the commits that added or changed construction/renders/*.jpg, extracts each version (old ones were overwritten
before the never-overwrite rule, so they only live in git) into .capture/renders/, groups them by camera
(name without the _vNNN suffix) and writes .capture/renders/replay.html: pick a camera, scrub or play through its
versions, the prompt (and any mid-turn messages) under each frame.
python3 tools/replay/render_history.py    then open .capture/renders/replay.html
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".capture" / "renders"; OUT.mkdir(parents=True, exist_ok=True)
git = lambda *a: subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True).stdout

log = git("log", "--reverse", "--format=%H%x1f%ad%x1f%s%x1f%(trailers:key=Prompt,valueonly)%x1f%(trailers:key=Also-Prompt,valueonly)%x1e",
          "--date=format:%Y-%m-%d %H:%M", "--", "construction/renders/").decode(errors="ignore")
frames = {}
for rec in log.split("\x1e"):
    if not rec.strip():
        continue
    h, date, subj, prompt, also = (rec.strip("\n").split("\x1f") + [""] * 5)[:5]
    names = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--diff-filter=AM", h, "--", "construction/renders/").decode().split()
    for n in names:
        if not n.endswith(".jpg"):
            continue
        cam = re.sub(r"_v\d{3}$", "", Path(n).stem)
        dst = OUT / h[:8] / Path(n).name
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(git("show", f"{h}:{n}"))
        frames.setdefault(cam, []).append({"src": str(dst.relative_to(OUT)), "commit": h[:8], "date": date, "subject": subj,
                                           "prompt": prompt.strip(), "also": [a.strip() for a in also.strip().splitlines() if a.strip()]})
# drop exact repeats (same image committed twice)
for cam, fs in frames.items():
    keep, last = [], None
    for f in fs:
        b = (OUT / f["src"]).read_bytes()
        if b != last:
            keep.append(f)
        last = b
    frames[cam] = keep
data = json.dumps(dict(sorted(frames.items())))
(OUT / "replay.html").write_text(f"""<!doctype html><meta charset=utf-8><title>The Gym · render replay</title>
<style>body{{margin:0;background:#111;color:#ddd;font:14px system-ui}}header{{display:flex;gap:12px;align-items:center;padding:10px 14px;background:#1b1b1b}}
img{{display:block;max-width:100%;max-height:78vh;margin:0 auto}}#cap{{padding:10px 18px;max-width:1100px;margin:auto}}#cap b{{color:#fff}}.also{{color:#9a9;font-size:13px}}
input[type=range]{{flex:1}}select,button{{background:#2a2a2a;color:#ddd;border:1px solid #444;padding:4px 8px}}</style>
<header><select id=cam></select><button id=prev>◀</button><button id=play>▶</button><button id=next>▶|</button><input type=range id=t min=0 value=0><span id=n></span></header>
<img id=im><div id=cap></div>
<script>const D={data};const cam=document.getElementById('cam'),t=document.getElementById('t'),im=document.getElementById('im'),cap=document.getElementById('cap'),n=document.getElementById('n');
for(const k of Object.keys(D)){{const o=document.createElement('option');o.value=k;o.textContent=k+' ('+D[k].length+')';cam.appendChild(o)}}
const pick=new URLSearchParams(location.search).get('cam');if(pick&&D[pick])cam.value=pick;
function show(){{const fs=D[cam.value];t.max=fs.length-1;const f=fs[+t.value];im.src=f.src;n.textContent=(+t.value+1)+' / '+fs.length;
cap.innerHTML='<b>'+f.date+'</b> · '+f.commit+' · '+f.subject.replace(/</g,'&lt;')+'<br><b>Prompt:</b> '+f.prompt.replace(/</g,'&lt;')+(f.also.length?'<div class=also>also: '+f.also.map(a=>a.replace(/</g,'&lt;')).join('<br>also: ')+'</div>':'')}}
cam.onchange=()=>{{t.value=0;show()}};t.oninput=show;document.getElementById('prev').onclick=()=>{{t.value=Math.max(0,+t.value-1);show()}};
document.getElementById('next').onclick=()=>{{t.value=Math.min(+t.max,+t.value+1);show()}};let iv=null;
document.getElementById('play').onclick=()=>{{if(iv){{clearInterval(iv);iv=null;return}}iv=setInterval(()=>{{if(+t.value>=+t.max){{clearInterval(iv);iv=null;return}}t.value=+t.value+1;show()}},900)}};
document.onkeydown=e=>{{if(e.key=='ArrowLeft')document.getElementById('prev').click();if(e.key=='ArrowRight')document.getElementById('next').click()}};show();</script>""")
print(f"render replay: {sum(len(v) for v in frames.values())} frames over {len(frames)} cameras -> {OUT / 'replay.html'}")

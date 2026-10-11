"""Build the replay data for the blueprint viewer from git history + the archived transcripts.

For every commit that touched the model: the building model and site terrain at that
commit (deduplicated by blob), the commit subject, and the prompt that led to it
(the Prompt: trailer, or, for older commits, the latest user prompt before the commit
time in .capture/sessions/*.jsonl).

python3 tools/replay/build_history.py   -> blueprint/public/history/ (git-ignored, regenerable)
"""
import glob
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "blueprint" / "public" / "history"
sys.path.insert(0, str(ROOT / "tools" / "capture"))
from checkpoint import first_line  # noqa: E402

TRACK = ["model/building.json", "model/site_terrain.json"]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout


def user_prompts():
    """(epoch seconds, first line) for every real user prompt in the archived transcripts."""
    out = []
    for f in glob.glob(str(ROOT / ".capture" / "sessions" / "*.jsonl")):
        for line in open(f, errors="ignore"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") != "user" or e.get("isMeta"):
                continue
            c = e.get("message", {}).get("content")
            if isinstance(c, list):
                if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                    continue
                c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            t = first_line(c) if isinstance(c, str) else ""
            if t and e.get("timestamp"):
                out.append((datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp(), t))
    return sorted(out)


def main():
    (OUT / "blobs").mkdir(parents=True, exist_ok=True)
    prompts = user_prompts()
    log = git("log", "--reverse", "--format=%H%x1f%ct%x1f%s%x1f%b%x1e", "--", *TRACK)
    commits = []
    for rec in log.split("\x1e"):
        if not rec.strip():
            continue
        h, ct, subj, body = rec.strip("\n").split("\x1f")
        ct = int(ct)
        prompt = next((l[len("Prompt: "):] for l in body.splitlines() if l.startswith("Prompt: ")), "")
        source = "trailer"
        if not prompt:  # older commits: latest user prompt before the commit
            before = [p for p in prompts if p[0] <= ct + 5]
            prompt, source = (before[-1][1], "transcript") if before else ("", "none")
        blobs = {}
        for path in TRACK:
            sha = git("rev-parse", f"{h}:{path}").strip()
            if not sha or "fatal" in sha or len(sha) != 40:
                continue
            f = OUT / "blobs" / f"{sha}.json"
            if not f.exists():
                f.write_text(git("show", f"{h}:{path}"))
            blobs["model" if path.endswith("building.json") else "terrain"] = sha
        if "model" not in blobs:
            continue
        if commits and commits[-1]["blobs"] == blobs:
            continue  # nothing the drawings can show changed
        commits.append({"hash": h[:7], "time": ct, "subject": subj, "prompt": prompt, "prompt_source": source, "blobs": blobs})
    (OUT / "index.json").write_text(json.dumps({"built": int(datetime.now().timestamp()), "commits": commits}, indent=1))
    size = sum(os.path.getsize(p) for p in (OUT / "blobs").glob("*.json")) // 1024
    print(f"{len(commits)} versions, {len(list((OUT / 'blobs').glob('*.json')))} blobs, {size} KB -> {OUT}")


if __name__ == "__main__":
    main()

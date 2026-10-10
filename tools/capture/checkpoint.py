#!/usr/bin/env python3
"""Stop-hook checkpoint for the replay history.

After every Claude turn:
  1. Archive the session transcript to .capture/sessions/ (gitignored, local only),
     so prompts survive Claude Code's transcript cleanup.
  2. If the repo has changes, make a local commit whose message carries the
     prompt that caused them plus the session id, so a replay tool can join
     git history back to the conversation. Never pushes.
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def last_prompt(transcript):
    prompt, ts = "", ""
    for line in transcript.read_text(errors="ignore").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        content = e.get("message", {}).get("content")
        if isinstance(content, list):  # tool results come back as user entries; skip those
            if any(c.get("type") == "tool_result" for c in content if isinstance(c, dict)):
                continue
            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        if isinstance(content, str) and content.strip():
            prompt, ts = content.strip(), e.get("timestamp", "")
    return prompt, ts


def main():
    data = json.load(sys.stdin)
    session = data.get("session_id", "unknown")
    transcript = Path(data.get("transcript_path", ""))

    prompt, ts = "", ""
    if transcript.is_file():
        archive = ROOT / ".capture" / "sessions"
        archive.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(transcript, archive / f"{session}.jsonl")
        prompt, ts = last_prompt(transcript)

    if not git("status", "--porcelain").stdout.strip():
        return
    # skip wrapper tags (pasted content, system notes) and use the first real line of text
    lines = [l.strip() for l in prompt.splitlines()]
    first = next((l for l in lines if l and not l.startswith("<")), "(no prompt)")
    subject = "checkpoint: " + (first[:69] + "..." if len(first) > 72 else first)
    body = f"Session-Id: {session}\nPrompt-Time: {ts}"
    git("add", "-A")
    git("commit", "-q", "-m", subject, "-m", body)


if __name__ == "__main__":
    main()

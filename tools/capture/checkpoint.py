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
        if isinstance(content, str) and first_line(content):  # skips system notifications
            prompt, ts = content.strip(), e.get("timestamp", "")
    return prompt, ts


def first_line(text):
    """First line of real text, skipping wrapper tags (pasted content, system notes)."""
    return next((l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("<")), "")


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
    first = first_line(prompt) or "(no prompt)"
    subject = "checkpoint: " + (first[:69] + "..." if len(first) > 72 else first)
    body = f"Prompt: {first[:200]}\nPrompt-Time: {ts}\nSession-Id: {session}"
    git("add", "-A")
    git("commit", "-q", "-m", subject, "-m", body)


def rebuild_history():
    """Refresh the blueprint's replay data (git-ignored) so the viewer always has the latest versions."""
    subprocess.run([sys.executable, str(ROOT / "tools" / "replay" / "build_history.py")], capture_output=True, timeout=120)


if __name__ == "__main__":
    main()
    rebuild_history()

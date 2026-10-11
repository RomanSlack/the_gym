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


def all_prompts(transcript):
    """Every human prompt in order: normal turns AND messages sent mid-turn (queued_command attachments). [(text, ts), ...]"""
    out, seen = [], set()
    for line in transcript.read_text(errors="ignore").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        text, ts = "", e.get("timestamp", "")
        att = e.get("attachment") if isinstance(e.get("attachment"), dict) else None
        if e.get("type") == "attachment" and att and att.get("type") == "queued_command" and (att.get("origin") or {}).get("kind", "human") == "human":
            text = att.get("prompt", "")
        elif e.get("type") == "user" and not e.get("isMeta"):
            content = e.get("message", {}).get("content")
            if isinstance(content, list):
                if any(c.get("type") == "tool_result" for c in content if isinstance(c, dict)):
                    continue
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            text = content if isinstance(content, str) else ""
        line1 = first_line(text or "")
        if line1 and (line1, ts[:16]) not in seen:
            seen.add((line1, ts[:16])); out.append((text.strip(), ts))
    return out


def prompts_since_last_commit(transcript):
    """Prompts newer than the Prompt-Time of the previous commit (so a commit lists every message it answers)."""
    last = git("log", "-1", "--format=%(trailers:key=Prompt-Time,valueonly)").stdout.strip()
    ps = all_prompts(transcript)
    new = [p for p in ps if not last or p[1] > last]
    return new or ps[-1:]


def trailers(transcript, session):
    ps = prompts_since_last_commit(transcript)
    if not ps:
        return ""
    text, ts = ps[-1]
    lines = [f"Prompt: {first_line(text)[:200]}", f"Prompt-Time: {ts}"]
    lines += [f"Also-Prompt: {first_line(t)[:200]} @ {t_}" for t, t_ in ps[:-1]]  # earlier messages answered by the same commit
    lines.append(f"Session-Id: {session}")
    return "\n".join(lines)


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
    ps = prompts_since_last_commit(transcript) if transcript.is_file() else []
    first = first_line(ps[-1][0]) if ps else (first_line(prompt) or "(no prompt)")
    subject = "checkpoint: " + (first[:69] + "..." if len(first) > 72 else first)
    body = trailers(transcript, session) if ps else f"Prompt: {first[:200]}\nPrompt-Time: {ts}\nSession-Id: {session}"
    git("add", "-A")
    git("commit", "-q", "-m", subject, "-m", body)


def rebuild_history():
    """Refresh the blueprint's replay data (git-ignored) so the viewer always has the latest versions."""
    subprocess.run([sys.executable, str(ROOT / "tools" / "replay" / "build_history.py")], capture_output=True, timeout=120)
    subprocess.run([sys.executable, str(ROOT / "tools" / "replay" / "render_history.py")], capture_output=True, timeout=300)  # 3D render replay


if __name__ == "__main__":
    main()
    rebuild_history()

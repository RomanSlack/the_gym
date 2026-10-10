"""Version every terrain run so the landscape's evolution can be replayed.

Each run gets terrain/runs/<UTC time>_<stage>/ with:
  manifest.json  inputs (params), code commit, output hashes  (committed to git)
  *.png          small previews                                (committed to git)
Large arrays are NOT committed: any run is reproducible from its manifest
(+ the cached Kartverket tiles). Optional animation frames go to the local-only
.capture/terrain/<run>/ folder for the video.
"""
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "terrain" / "runs"


def _commit():
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "terrain"], capture_output=True, text=True).stdout.strip()
    return r.stdout.strip() + ("+dirty" if dirty else "")


class Run:
    def __init__(self, stage: str, params: dict):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.id = f"{stamp}_{stage}"
        self.dir = RUNS / self.id
        self.dir.mkdir(parents=True)
        self.frames = ROOT / ".capture" / "terrain" / self.id
        self.manifest = {"id": self.id, "stage": stage, "started": stamp, "code": _commit(),
                         "params": params, "outputs": {}}

    def output(self, name: str, data: bytes | None = None, **meta):
        """Record an output (hash of its bytes, plus any metadata)."""
        entry = dict(meta)
        if data is not None:
            entry["sha256"] = hashlib.sha256(data).hexdigest()[:16]
        self.manifest["outputs"][name] = entry

    def preview(self, fig_or_path, name="preview.png", dpi=80):
        p = self.dir / name
        fig_or_path.savefig(p, dpi=dpi)
        return p

    def frame(self, k: int, fig, dpi=60):
        self.frames.mkdir(parents=True, exist_ok=True)
        fig.savefig(self.frames / f"{k:05d}.png", dpi=dpi)

    def close(self):
        (self.dir / "manifest.json").write_text(json.dumps(self.manifest, indent=1))
        with open(RUNS / "runs.jsonl", "a") as f:
            f.write(json.dumps({"id": self.id, "stage": self.manifest["stage"], "code": self.manifest["code"]}) + "\n")
        return self.dir

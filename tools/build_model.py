"""Regenerate everything derived in model/building.json, in order: layout -> structure -> partitions -> room numbers -> foundations -> stage-3 structure -> stage-4 envelope -> stage-5 interior shell -> stage coverage check."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / "terrain" / ".venv" / "bin" / "python")
for step in ("layout_v1.py", "structure.py", "partitions.py", "annotate.py", "foundations.py", "structure_stage.py", "envelope.py", "interior.py", "stage_check.py"):
    r = subprocess.run([PY, str(ROOT / "tools" / step)], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        sys.exit(r.returncode)

---
description: Pick The Gym project back up after a context reset
---

You've lost context on The Gym (a luxury Nordic gym in an Elverum ravine, designed through conversation with Roman and built stage by stage). Get back up to speed:

1. Read `HANDOFF.md` first, then `README.md` and `CONSTRUCTION_PLAN.md` (which stage we're on and what's next).
2. Read the decision sheets we keep updated, and treat them as the rules:
   - `VISION.md`: ground truth, including the LOCKED exterior style
   - `STRUCTURE.md`
   - `DECISIONS_PENDING.md`
   - `docs/AUDIT.md`
   - `docs/FIT_STUDY.md`
3. Note Roman's standing rules from those files and your memory:
   - open plan, no door unless needed
   - column-free
   - Gym V2 is his intent reference
   - no PDF re-export unless asked
4. Check the replay/recording is intact:
   - every commit carries a `Prompt:` trailer (`tools/capture/`)
   - `.capture/sessions/` archives the transcripts
   - the drawings replay (H in `blueprint/`) builds from `tools/replay/build_history.py`
5. Read `git log --oneline -20` for the latest work.

Report back briefly: current stage, what was last done, what's next, and any open questions. Then wait for Roman.

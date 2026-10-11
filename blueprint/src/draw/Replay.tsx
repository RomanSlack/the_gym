// Replay: scrub through the design's history. Each version is a commit that changed the model
// or the site terrain, with the prompt that led to it. Data comes from tools/replay/build_history.py.
import { useEffect, useRef, useState } from "react";
import type { Model, Underlay } from "../model";
import { loadSite, loadV2Terrain, loadWide, normalizeModel } from "../model";

export interface Version {
  hash: string;
  time: number;
  subject: string;
  prompt: string;
  prompt_source: string;
  blobs: { model: string; terrain?: string };
}

const cache = new Map<string, unknown>();
async function blob(sha: string) {
  if (!cache.has(sha)) cache.set(sha, await (await fetch(`/history/blobs/${sha}.json`)).json());
  return cache.get(sha);
}

/** Load a version: its model, and its terrain (Gym V2's own terrain before the site existed). */
export async function loadVersion(v: Version, base: Underlay): Promise<{ model: Model; underlay: Underlay }> {
  const model = normalizeModel(await blob(v.blobs.model));
  if (!v.blobs.terrain) {
    return { model, underlay: { ...base, terrain: loadV2Terrain(model.project.datum.blender_z_gymv2), wide: null } };
  }
  const raw = (await blob(v.blobs.terrain)) as Parameters<typeof loadSite>[0];
  return { model, underlay: { ...base, terrain: loadSite(raw), wide: loadWide(raw) } };
}

const fmt = (t: number) =>
  new Date(t * 1000).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

export function ReplayBar({
  versions, index, setIndex, onClose,
}: { versions: Version[]; index: number; setIndex: (i: number) => void; onClose: () => void }) {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(2.5);
  const timer = useRef<number | null>(null);
  useEffect(() => {
    if (!playing) return;
    timer.current = window.setTimeout(() => {
      if (index < versions.length - 1) setIndex(index + 1);
      else setPlaying(false);
    }, speed * 1000);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [playing, index, speed, versions.length, setIndex]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") setIndex(Math.min(versions.length - 1, index + 1));
      if (e.key === "ArrowLeft") setIndex(Math.max(0, index - 1));
      if (e.key === " ") { e.preventDefault(); setPlaying((p) => !p); }
    };
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [index, versions.length, setIndex]);
  const v = versions[index];
  if (!v) return null;
  const t0 = versions[0].time, t1 = versions[versions.length - 1].time;
  return (
    <div className="replay">
      <div className="replay-top">
        <button onClick={() => setIndex(Math.max(0, index - 1))}>◀</button>
        <button className="play" onClick={() => setPlaying((p) => !p)}>{playing ? "❚❚" : "▶"}</button>
        <button onClick={() => setIndex(Math.min(versions.length - 1, index + 1))}>▶︎▏</button>
        <span className="mono replay-count">{index + 1} / {versions.length}</span>
        <div className="replay-track">
          {versions.map((x, i) => (
            <button key={x.hash} className={i === index ? "tick on" : i < index ? "tick past" : "tick"}
              style={{ left: `${((x.time - t0) / Math.max(1, t1 - t0)) * 100}%` }}
              title={`${fmt(x.time)} · ${x.subject}`} onClick={() => setIndex(i)} />
          ))}
        </div>
        <select value={speed} onChange={(e) => setSpeed(+e.target.value)} title="seconds per version">
          {[1, 2.5, 5].map((s) => <option key={s} value={s}>{s}s</option>)}
        </select>
        <button onClick={onClose} title="back to the current design">✕</button>
      </div>
      <div className="replay-caption">
        <div className="replay-meta mono">{fmt(v.time)} · {v.hash}</div>
        <div className="replay-prompt">“{v.prompt.length > 260 ? v.prompt.slice(0, 260) + "…" : v.prompt}”</div>
        <div className="replay-subject">→ {v.subject.length > 200 ? v.subject.slice(0, 200) + "…" : v.subject}</div>
      </div>
    </div>
  );
}

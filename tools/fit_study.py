"""Equipment fit study: does the wishlist fit the zones at normal commercial-gym density?

Each item = footprint + its use/walk clearance (an "allocation" in m²), from common gym
planning rules of thumb:
  selectorized machine ~4.5-6 m² (incl. ~0.6-0.9 m walkway), plate-loaded 5-7, cable station 7-9,
  cardio 3.5-4.5 (treadmill ~5), power rack + platform ~10-12, bench station ~5,
  Olympic platform 2.4 x 3.0 + 1 m clearance ~ 15-17.
Utilisation = allocated / zone area. ~65-85 % = normal gym density; >90 % crowded; <50 % sparse.
These are planning estimates, not manufacturer footprints.

python3 tools/fit_study.py  -> printed table + docs/FIT_STUDY.md
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
m = json.loads((ROOT / "model" / "building.json").read_text())


def area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


A = {s["id"]: area(s["poly"]) for s in m["spaces"]}

# zone -> [(item, count, m² each incl. clearance)]
# Roman: double up popular machines + plan "islands" (freestanding racks with stations all round)
# so each strength floor lands at normal gym density (~65-85 %).
PLAN = {
    "machines": [  # F2 legs
        ("Leg press 45°", 3, 7.0), ("Hack squat", 2, 6.5), ("Pendulum squat", 1, 6.5), ("V-squat", 1, 6.5), ("Leg extension", 3, 4.5),
        ("Seated leg curl", 2, 4.5), ("Lying leg curl", 2, 4.5), ("Standing calf raise", 2, 4.0), ("Seated calf raise", 1, 3.5),
        ("Hip abduction", 2, 4.0), ("Hip adduction", 2, 4.0), ("Glute drive / hip thrust", 2, 5.5), ("Belt squat", 2, 6.0),
        ("Smith machine", 2, 8.0), ("Reverse hyper", 1, 4.0), ("ISLAND: dumbbell rack + lunge/RDL floor", 1, 12.0)],
    "machines-2": [  # F2 upper body + cable
        ("Lat pulldown", 3, 4.5), ("Seated row (low row)", 2, 4.5), ("Chest press (flat + incline)", 3, 4.5),
        ("Pec deck / rear delt", 2, 4.5), ("Shoulder press", 2, 4.5), ("Bicep curl", 1, 3.5), ("Tricep pushdown / extension", 1, 3.5),
        ("Assisted pull-up / dip", 1, 4.0), ("Cable crossover (dual pulley)", 1, 9.0), ("Functional trainer", 2, 7.0),
        ("Plate-loaded iso-lateral (chest/back/row)", 4, 5.5)],
    "free-weights": [  # F2 mirror wall
        ("Power rack + bench", 6, 11.0), ("Half rack / squat stand", 2, 9.0), ("Flat bench press station", 3, 6.0),
        ("Incline bench press station", 3, 6.0), ("Decline bench station", 1, 6.0), ("Plate trees + bar storage", 4, 1.5),
        ("Fixed barbell / EZ rack", 2, 2.5), ("ISLAND: dumbbell rack 2.5-50 kg + 4 benches round it", 1, 30.0)],
    "olympic": [
        ("Weightlifting platform (2.4 x 3 m)", 8, 15.0), ("Bumper plate storage + chalk", 3, 1.5),
        ("Specialty bar rack (trap, SSB, cambered, swiss)", 1, 3.0), ("GHD / back extension", 2, 3.5), ("Warm-up / mobility floor", 1, 25.0)],
    "free-weights-F3": [  # the den
        ("Adjustable bench (flat/incline/decline) station", 18, 5.0), ("Dumbbell rack 2.5-75 kg (run)", 3, 6.0),
        ("Kettlebell rack", 1, 3.0), ("Landmine stations", 2, 4.5), ("Multi-grip pull-up bars", 1, 4.0),
        ("ISLAND: 4-stack cable tower", 1, 24.0), ("ISLAND: dumbbell rack + benches", 1, 30.0), ("Grip & hangboard wall", 1, 12.0)],
    "functional": [
        ("Rig (pull-up / squat / dip bays)", 1, 60.0), ("Wall-ball targets", 1, 8.0), ("Plyo boxes, slam/med balls, ropes, rings storage", 1, 10.0),
        ("Rowers (Concept2)", 4, 4.0), ("SkiErg", 3, 2.5), ("Air bike", 4, 3.0), ("GHD", 2, 3.5), ("Pegboard + climbing rope", 1, 6.0),
        ("Battle ropes anchor", 1, 6.0), ("Open floor for classes", 1, 40.0)],
    "strongman": [("Yoke", 1, 12.0), ("Atlas stones + platform", 1, 12.0), ("Farmer's handles, sandbags, log", 1, 8.0), ("Open carry lane", 1, 30.0)],
    "sled-track": [("Turf sprint / sled lane (46 m)", 1, 105.0), ("Sleds + harness storage", 1, 4.0)],
    "cardio-F1": [("Treadmill", 8, 5.0), ("Curved / non-motor treadmill", 2, 5.0), ("Stair climber", 3, 4.0), ("Elliptical", 4, 4.0), ("Upright / recumbent bike", 6, 3.5)],
    "cardio-F2": [("Treadmill", 6, 5.0), ("Rower", 3, 4.0), ("Bike", 5, 3.5), ("Elliptical", 3, 4.0)],
    "calisthenics": [("Bar station + rings", 1, 20.0), ("Parallettes / dip bars", 1, 6.0), ("Open floor", 1, 30.0)],
    "stretching": [("Mats / mobility area", 1, 120.0), ("Foam rollers, bands, massage guns storage", 1, 6.0),
                   ("3D body scanner", 1, 6.0), ("Small group class studio (open)", 1, 70.0)],
    "recovery": [("Compression boots chairs", 8, 4.0), ("Zero-gravity loungers", 10, 4.5), ("Stretch / foam-roll corner", 1, 25.0)],
    "posing": [("Posing stage + light rig + 3-way mirror", 1, 25.0)],
    "pod-1": [("Pod: rack, bench, dumbbells, AV", 1, 22.0)], "pod-2": [("Pod: rack, bench, dumbbells, AV", 1, 22.0)],
    "pod-3": [("Pod: rack, bench, dumbbells, AV", 1, 22.0)],
    "altitude": [("Bike", 4, 3.5), ("Rower", 2, 4.0), ("Treadmill", 2, 5.0), ("Open floor", 1, 20.0)],
    "breathwork": [("Mats / mobility floor", 1, 45.0)],
}

rows, out = [], ["# Equipment fit study", "", "Generated by `tools/fit_study.py` from the model's zone areas.",
                 "Allocations include use + walking clearance (planning rules of thumb, not manufacturer data).",
                 "~65–85 % = normal gym density, >90 % crowded, <50 % sparse.", "",
                 "| Zone | Area m² | Items | Allocated m² | Use | Verdict |", "|---|---|---|---|---|---|"]
for zone, items in PLAN.items():
    alloc = sum(n * a for _, n, a in items)
    n = sum(n for _, n, _ in items)
    u = alloc / A[zone]
    verdict = "crowded" if u > 0.9 else "normal" if u >= 0.65 else "roomy" if u >= 0.5 else "sparse"
    rows.append((zone, A[zone], n, alloc, u, verdict))
    out.append(f"| {zone} | {A[zone]:.0f} | {n} | {alloc:.0f} | {u:.0%} | {verdict} |")
out += ["", "## Item lists", ""]
for zone, items in PLAN.items():
    out.append(f"**{zone}**: " + "; ".join(f"{name} ×{n}" for name, n, _ in items))
    out.append("")
(ROOT / "docs" / "FIT_STUDY.md").write_text("\n".join(out) + "\n")
for r in rows:
    print(f"{r[0]:18} {r[1]:5.0f} m²  {r[2]:3d} items  {r[3]:5.0f} m²  {r[4]:4.0%}  {r[5]}")
print("total equipment items:", sum(r[2] for r in rows))

"""Studio check of the island's grand tree against its reference (Roman: "need to dial that separately then render").
    /snap/blender/current/blender -b --factory-startup -t 12 --python landscape/test_grand_tree.py -- HEIGHT SEED LOD
writes landscape/work/gammelfuru_<seed>_full.png + _crown.png"""
import sys
from pathlib import Path
import bpy
ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "construction", ROOT / "plants", ROOT / "walls"):
    sys.path.insert(0, str(p))
import bl_common as bc  # noqa: E402
import gen_pine  # noqa: E402
a = sys.argv[sys.argv.index("--") + 1:]; H = float(a[0]); SEED = int(a[1]); LOD = float(a[2])
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; bc.world_and_render(sc)
sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; bc.gpu_or_stop(); sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 1500
bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(bc.material("g", (0.11, 0.12, 0.07), 0.9))
gen_pine.build_natural(SEED, (0, 0, 0), height=H, density=2600, lod=LOD, name="grand")
for nm, loc, tgt, lens in (("full", (0, -H * 1.5, 1.7), (0, 0, H * 0.52), 22), ("crown", (H * 0.25, -H * 0.55, H * 0.55), (0, 0, H * 0.72), 30)):
    bc.camera(sc, nm, loc, tgt, lens); sc.camera = bpy.data.objects[nm]
    sc.render.filepath = str(ROOT / "landscape" / "work" / f"gammelfuru_{SEED}_{nm}.png"); bpy.ops.render.render(write_still=True)

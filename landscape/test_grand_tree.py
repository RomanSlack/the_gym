"""Studio check of the island's grand tree (Roman: "the tree in the middle make way thicker or better a big grand tree").
    blender -b --factory-startup -t 12 --python landscape/test_grand_tree.py -- HEIGHT SEED"""
import sys
from pathlib import Path
import bpy
ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "construction", ROOT / "plants", ROOT / "walls"):
    sys.path.insert(0, str(p))
import bl_common as bc  # noqa: E402
import gen_birch  # noqa: E402
import gen_pine  # noqa: E402
a = sys.argv[sys.argv.index("--") + 1:]; H = float(a[0]); SEED = int(a[1])
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; bc.world_and_render(sc)
sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; bc.gpu_or_stop(); sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 1500
bpy.ops.mesh.primitive_plane_add(size=60); bpy.context.object.data.materials.append(bc.material("g", (0.12, 0.14, 0.08), 0.9))
gen_pine.build_natural(SEED, (0, 0, 0), height=H, density=2600, lod=float(a[2]) if len(a) > 2 else 3.0, name="grand")
bc.camera(sc, "cam", (0, -H * 1.45, 1.7), (0, 0, H * 0.5), 22); sc.camera = bpy.data.objects["cam"]
sc.render.filepath = str(ROOT / "landscape" / "work" / f"gammelfuru_{SEED}.png"); bpy.ops.render.render(write_still=True)

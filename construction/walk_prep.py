"""A walk-through copy of the stage 5 scene (Roman 2026-10-27: "walk through it myself in Blender ... EEVEE so it doesn't crash").

    blender -b construction/out/stage_5.blend --python construction/walk_prep.py

-> construction/out/gym_walk.blend: EEVEE with light settings, the forest + grass excluded from the view layer (tick them
back on in the outliner), the viewports in Solid, and a camera at eye level in from the gallery on F1. In the viewport:
View > Navigation > Walk Navigation (Shift + `): WASD, the mouse to look, Tab toggles gravity, Q / E down / up.
"""
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent / "out"
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE"
ee = sc.eevee
for attr, val in (("taa_samples", 8), ("taa_render_samples", 32), ("use_raytracing", False), ("use_shadows", True),
                  ("shadow_ray_count", 1), ("shadow_step_count", 2), ("use_gtao", False), ("use_volumetric_shadows", False)):
    if hasattr(ee, attr):
        setattr(ee, attr, val)
for lc in bpy.context.view_layer.layer_collection.children:
    if lc.name in ("6 · forest", "6 · grass"):
        lc.exclude = True
cam = bpy.data.objects.get("cam_eq1_gallery")
if cam:
    sc.camera = cam
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == "VIEW_3D":
            for sp in area.spaces:
                if sp.type == "VIEW_3D":
                    sp.shading.type = "SOLID"
                    sp.clip_start, sp.clip_end = 0.05, 500.0
                    sp.lens = 24
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "gym_walk.blend"))
print("wrote", OUT / "gym_walk.blend")

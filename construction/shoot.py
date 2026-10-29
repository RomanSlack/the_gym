"""One shot from a built stage scene: the camera's exposure + clipping, the render, and the kept _vNNN copy (Roman's rule: never
overwrite a render). Shared by construction/scene.py (build + render) and construction/render_saved.py (render from the saved
.blend, Roman 2026-10-28: "how do we optimize it like crazy": build once, render each camera in its own short process)."""
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "construction" / "out"


def shoot(scene, cam_n, n, EXPO, STAGE, LOD_EYE):
    """cam_n = the camera's name, n = the shot's file name (cam_n, + _night)."""
    scene.camera = bpy.data.objects[f"cam_{cam_n}"]
    if LOD_EYE is not None:  # LOD switches by distance from this camera
        LOD_EYE.location = scene.camera.location; bpy.context.view_layer.update()
    if cam_n.startswith("eq") and cam_n.endswith("_top"):
        scene.camera.data.clip_start = 15.75 if cam_n == "eq1_top" else 16.9   # cut 4.25 m up (F2 + F3: 3.1 m, under the pods' ceilings)
    scene.view_settings.exposure = EXPO + (1.0 if cam_n == "eq2_pod" else 2.2 if cam_n[:2] == "eq" and cam_n[3:4] == "_" else 0.6 if "_cab_" in cam_n else 1.6 if cam_n in ("ku_hot", "ku_hot_view", "ku_changing") else 0.8 if n.startswith("lk_") else 1.0 if n.startswith(("gwc_", "ann_")) else 2.2 if n.startswith(("br_", "gal_", "gym_", "pool_")) else 2.8 if n.startswith(("rec_", "cafe_", "wc_", "dc_")) else 0.0)  # the bridge + gallery have glass on three sides: less  # interiors exposed for the room, like a photographer would
    scene.render.filepath = str(OUT / f"stage_{STAGE}_{n}.png")
    bpy.ops.render.render(write_still=True)
    # Roman's rule: never overwrite a render. Every render is also kept as the next version in construction/renders/.
    RND = ROOT / "construction" / "renders"; RND.mkdir(exist_ok=True)
    v = 1 + max([int(p_.stem.rsplit("_v", 1)[1]) for p_ in RND.glob(f"stage_{STAGE}_{n}_v*.jpg") if p_.stem.rsplit("_v", 1)[1].isdigit()] or [0])
    img_ = bpy.data.images.load(scene.render.filepath)
    sc_ = bpy.context.scene; ff = sc_.render.image_settings.file_format; q_ = sc_.render.image_settings.quality
    vs_ = sc_.view_settings; keep_ = (vs_.view_transform, vs_.look, vs_.exposure)
    vs_.view_transform = "Standard"; vs_.look = "None"; vs_.exposure = 0.0  # the PNG is already graded: store it as is
    sc_.render.image_settings.file_format = "JPEG"; sc_.render.image_settings.quality = 90
    img_.save_render(str(RND / f"stage_{STAGE}_{n}_v{v:03d}.jpg"), scene=sc_)
    sc_.render.image_settings.file_format = ff; sc_.render.image_settings.quality = q_
    vs_.view_transform, vs_.look, vs_.exposure = keep_
    bpy.data.images.remove(img_)
    print("kept", f"stage_{STAGE}_{n}_v{v:03d}.jpg")

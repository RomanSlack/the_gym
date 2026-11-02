# How to make pro-level PBR textures from a single reference (Blender + Claude)

Source: https://x.com/mukadeshinigami/status/2115580095511617850 (saved by Roman 2026-11-02, "save this for later"; text as pasted).

Here's how I make pro-level PBR materials with Claude Opus 5.5, step by step, with code.

The core idea in one line: you don't make textures from nothing. You take real textures as a reference and generate your own set on top of them. Then you fix that set until every map agrees with every other map.

Not procedural noise. Not a random AI picture slapped on a sphere. Real forms in, your own clean material out.

## Why start from real textures?

Because nature is hard to fake. If you try to make rock with procedural noise (Voronoi, Perlin and friends), next to a real scan it reads as a collage: hard outlines, the same speckle everywhere, a fake emboss look. Your eye catches it instantly.

A real texture (a scan or a good photo of the surface) already has the right shapes: how cracks branch, where moss grows, how stones sit in the ground. You use that as the base and build your own version of it.

## Step 1. Pick your reference

Find a real texture of the surface you want. Rock, bark, brick, sand, concrete, anything. What makes a good reference:

- top-down, no perspective
- soft, even light, no hard sun shadows
- sharp, no motion blur
- ideally it's already a PBR set (color + height + normal), but a single good photo works too

This is the "truth" of your material. Everything after this step tries to stay close to it.

## Step 2. Generate your own maps from the reference

Feed the reference to an image generator and make your own maps. One map at a time, and several candidates per map. You'll pick the best later.

- Albedo (color): the color with no lighting in it
- Height: real height, it moves the actual geometry
- Normal (OpenGL): small surface detail for the light
- Roughness: how matte each spot is (white = matte, black = shiny)
- AO: soft darkness in the cracks

Prompt templates (attach your reference image to each):

```
ALBEDO: Top-down albedo texture of [SURFACE], same shapes and layout as
the reference. Flat, even, shadowless light. No highlights, no cast
shadows, no ambient occlusion. Pure surface color. High resolution.

HEIGHT: Grayscale height map of [SURFACE] matching the reference layout.
White = highest, black = lowest. Only real relief: stones, cracks,
bumps. No color patterns, no lighting. Smooth gradients.

NORMAL: OpenGL tangent-space normal map of [SURFACE] matching the
reference layout. Flat areas are (128,128,255) blue. No color cast.

ROUGHNESS: Grayscale roughness map of [SURFACE] matching the reference.
Dry rock and moss are light (matte), wet spots are darker.
No shadows, no lighting.

AO: Ambient occlusion map of [SURFACE] matching the reference.
White everywhere except soft darkening in cracks and contact areas.
```

Make 2-4 of each. They will NOT match each other pixel to pixel. That's normal, step 4 fixes it.

## Step 3. Pick the best candidate per map

Most people take the first image that looks cool. Use these rules instead:

- Albedo: the one with the LEAST baked light. No cast shadows, no shiny highlights. Pick the flatter, less dramatic one. Drama = baked shadows, and those will fight your real light in Blender.
- Height: shows real forms (big shapes, cracks) without the color pattern leaking in. If a dark color patch became a hole, reject it.
- Normal: on average the flat blue (128,128,255). A pink or green tint over the whole map means it's tilted.
- AO: dark only in the cracks, soft falloff.
- Roughness: no shadows in it. Shadows are lighting, not a material property.

I gave all candidates to Claude, numbered, and asked it to pick the winner per map with a reason. It's surprisingly good at spotting baked light.

## Step 4. Align every map to the albedo

THE step that turns "AI pictures" into a real material. Generated maps never line up: the height is a few pixels off from the color, so cracks in the relief sit next to cracks in the color, and in the render the rocks "float".

The fix: the albedo is the reference, every other map gets gently warped onto it with optical flow. Compare structure (edges), not brightness, because a height map and a color map have totally different brightness. A normal map is turned into a shaded image first so it can be compared too.

```python
# pip install opencv-python numpy
# python align_maps.py albedo.png height.png normal.png roughness.png ao.png
# writes *_aligned.png next to each map
import sys, cv2, numpy as np

def load(p):
    img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if img.ndim == 3: img = cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2RGB)
    return img.astype(np.float32) / (65535 if img.dtype == np.uint16 else 255)

def lum(img):
    return img if img.ndim == 2 else img @ np.float32([0.299, 0.587, 0.114])

def unit(n):
    return n / np.linalg.norm(n, axis=-1, keepdims=True).clip(1e-6)

def probe(img, is_normal):
    # compare STRUCTURE, not brightness. a normal map is turned into shading first
    if is_normal:
        L = np.float32([-0.5, 0.5, 0.7]); L /= np.linalg.norm(L)
        return (unit(img * 2 - 1) * L).sum(-1).clip(0, 1).astype(np.float32)
    return lum(img)

def structure(g):
    b = cv2.GaussianBlur(g, (0, 0), 1.5)
    m = np.sqrt(cv2.Sobel(b, cv2.CV_32F, 1, 0) ** 2 + cv2.Sobel(b, cv2.CV_32F, 0, 1) ** 2)
    m = np.log1p(m / (m.mean() + 1e-6))
    return (255 * m / m.max()).astype(np.uint8)

dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
dis.setPatchSize(16); dis.setPatchStride(4)

def flow(ref, mov, smooth, lim):
    f = dis.calc(structure(ref), structure(mov), None)
    f = np.dstack([cv2.GaussianBlur(f[..., i], (0, 0), smooth) for i in range(2)])
    return np.clip(f, -lim, lim)

def warp(img, f):
    h, w = f.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx + f[..., 0], gy + f[..., 1], cv2.INTER_CUBIC,
                     borderMode=cv2.BORDER_REFLECT)

def shift_px(f):
    m = np.linalg.norm(f, axis=-1)
    return f"median {np.median(m):.2f}px, p90 {np.percentile(m, 90):.2f}px"

albedo = lum(load(sys.argv[1]))
scale = max(albedo.shape) / 2500          # defaults are tuned for ~2.5K images
smooth, lim = 24 * scale, 12 * scale

for path in sys.argv[2:]:
    src = load(path)
    if src.shape[:2] != albedo.shape:
        src = cv2.resize(src, albedo.shape[::-1], interpolation=cv2.INTER_CUBIC)
    is_normal = src.ndim == 3 and "nor" in path.lower()
    total = np.zeros((*albedo.shape, 2), np.float32)
    cur = src
    print(path, "before:", shift_px(flow(albedo, probe(cur, is_normal), smooth, lim)))
    for _ in range(2):
        total += flow(albedo, probe(cur, is_normal), smooth, lim)
        cur = warp(src, total)
    if is_normal:
        cur = unit(cur * 2 - 1) * 0.5 + 0.5      # renormalize after warping
    print(path, "after: ", shift_px(flow(albedo, probe(cur, is_normal), smooth, lim)))
    out = path.rsplit(".", 1)[0] + "_aligned.png"
    if cur.ndim == 2 and "height" in path.lower():
        cv2.imwrite(out, (cur.clip(0, 1) * 65535).astype(np.uint16))   # 16-bit height
    elif cur.ndim == 2:
        cv2.imwrite(out, (cur.clip(0, 1) * 255).astype(np.uint8))
    else:
        cv2.imwrite(out, cv2.cvtColor((cur.clip(0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
```

It prints how far off each map was before and after. On a test with maps shifted 3-4 px it went down to 0.1-0.3 px. Anything under ~0.5 px is invisible.

## Step 5. Fix and soften

- Height specks: tiny black dots and pits. Patch only the small isolated ones. Don't threshold the dark areas, you'll kill real cracks.
- Rebuild the normal from the aligned height: big shapes from the height, fine detail from the generated normal. Now normal and height can't disagree.
- Soften baked shadows in the albedo: lift only the spots darker than their surroundings. Don't flatten the whole image.

```python
# lift baked shadows in the albedo, keep natural contrast
import cv2, numpy as np
img = cv2.imread("albedo_aligned.png").astype(np.float32) / 255
lum = img.mean(-1)
around = cv2.GaussianBlur(lum, (0, 0), 25) * 0.75
dark = np.clip((around - cv2.GaussianBlur(lum, (0, 0), 3)) / (around + 1e-6), 0, 1)
gain = 1 + cv2.GaussianBlur(dark, (0, 0), 3) * 0.6
cv2.imwrite("albedo_soft.png", (np.clip(img * gain[..., None], 0, 1) * 255).astype(np.uint8))
```

- AO: soften it too. A harsh AO looks dirty. Keep it weak.
- Roughness: clamp to a sane range (0.35-1 for natural matte stuff).

## Step 6. 8K, honestly

The aligned set was 2752×1536, the final 8192×4572. That's an upscale, not "true 8K". Measure how much real detail you have first (shrink a bit and scale back; if it barely changes, the detail wasn't there).

- Plain resample: fast, clean, soft up close. Normal maps must be upscaled as vectors and renormalized, never like a normal picture.
- AI re-detailing (Real-ESRGAN): only the albedo goes through the network; the new fine detail is transferred to height, normal, AO and roughness so the set stays consistent. Looks great, but the detail is plausible and invented. Say so.

## Step 7. Masks: moss is not rock

Real surfaces are mixed. Moss is soft and fully matte, rock is hard. Make a mask from the albedo color (moss = yellow-green, saturated, dark) to switch between two shaders. Two masks: a sharp one for the look, a blurred one for height (one sharp mask turned the moss height into thousands of needles).

```python
# pip install pillow numpy
from PIL import Image, ImageFilter
import numpy as np

src = Image.open("albedo.png").convert("RGB")
hsv = np.asarray(src.convert("HSV")).astype(float) / 255
h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
mask = (h > 50) & (h < 110) & (s > 0.25) & (v < 0.7)
m = Image.fromarray((mask * 255).astype(np.uint8))
m.filter(ImageFilter.GaussianBlur(2)).save("mask_shade.png")    # sharp: shading
m.filter(ImageFilter.GaussianBlur(25)).save("mask_height.png")  # soft: height
```

## Step 8. Blender: the material in one script

Select your object, Scripting tab, paste, set D to your maps folder, Run. Files: diffuse.png, height.png, normal.png, roughness.png, ao.png, mask_shade.png, mask_height.png.

```python
import bpy
D = "/path/to/maps/"
obj = bpy.context.object
mat = bpy.data.materials.new("PBR_Material"); mat.use_nodes = True
mat.displacement_method = 'DISPLACEMENT'
nt = mat.node_tree; N, L = nt.nodes, nt.links
N.clear()
out = N.new("ShaderNodeOutputMaterial")

def tex(name, color=False):
    t = N.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(D + name)
    if not color: t.image.colorspace_settings.name = "Non-Color"
    return t

dif = tex("diffuse.png", True)
rgh, ao, nrm = tex("roughness.png"), tex("ao.png"), tex("normal.png")
hgt = tex("height.png")
m_shade, m_height = tex("mask_shade.png"), tex("mask_height.png")

# diffuse x AO at 55%
col = N.new("ShaderNodeMix"); col.data_type = 'RGBA'
col.blend_type = 'MULTIPLY'; col.inputs[0].default_value = 0.55
L.new(dif.outputs[0], col.inputs[6]); L.new(ao.outputs[0], col.inputs[7])

nmap = N.new("ShaderNodeNormalMap")
nmap.inputs["Strength"].default_value = 1.4
L.new(nrm.outputs[0], nmap.inputs["Color"])

# dry matte rock: roughness map squeezed into 0.62-1.0
rr = N.new("ShaderNodeMath"); rr.operation = 'MULTIPLY_ADD'
rr.inputs[1].default_value = 0.45; rr.inputs[2].default_value = 0.62
rr.use_clamp = True
L.new(rgh.outputs[0], rr.inputs[0])

# material A: the base (rock)
a = N.new("ShaderNodeBsdfPrincipled")
L.new(col.outputs[2], a.inputs["Base Color"])
L.new(rr.outputs[0], a.inputs["Roughness"])
a.inputs["Specular IOR Level"].default_value = 0.2
L.new(nmap.outputs[0], a.inputs["Normal"])

# material B: the masked one (moss)
b = N.new("ShaderNodeBsdfPrincipled")
L.new(col.outputs[2], b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 1.0
b.inputs["Specular IOR Level"].default_value = 0.1
b.inputs["Sheen Weight"].default_value = 0.6
b.inputs["Sheen Tint"].default_value = (0.45, 0.6, 0.2, 1)
b.inputs["Subsurface Weight"].default_value = 0.15
L.new(nmap.outputs[0], b.inputs["Normal"])

mix = N.new("ShaderNodeMixShader")
L.new(m_shade.outputs[0], mix.inputs[0])
L.new(a.outputs[0], mix.inputs[1]); L.new(b.outputs[0], mix.inputs[2])
L.new(mix.outputs[0], out.inputs["Surface"])

# height = base height + soft mask * 0.15
add = N.new("ShaderNodeMath"); add.operation = 'MULTIPLY_ADD'
add.inputs[1].default_value = 0.15
L.new(m_height.outputs[0], add.inputs[0]); L.new(hgt.outputs[0], add.inputs[2])

disp = N.new("ShaderNodeDisplacement")
disp.inputs["Midlevel"].default_value = 0.5
disp.inputs["Scale"].default_value = 0.045   # higher = spikes
L.new(add.outputs[0], disp.inputs["Height"])
L.new(disp.outputs[0], out.inputs["Displacement"])

obj.data.materials.clear(); obj.data.materials.append(mat)
sub = obj.modifiers.new("Subdiv", 'SUBSURF')
sub.subdivision_type = 'SIMPLE'; sub.levels = 6; sub.render_levels = 6
bpy.context.scene.render.engine = 'CYCLES'
```

What matters: only the albedo is sRGB, everything else Non-Color (or you get plastic). Blender uses OpenGL normals, Unreal DirectX (green flipped). Moss shader: roughness 1.0, soft sheen, a little subsurface, its own height.

## Step 9. Dry rock, not soap

First renders looked wet. What fixed it:

- rock roughness 0.62-1.0: the map squeezed into the matte range (rough * 0.45 + 0.62). A raw generated roughness is often too dark, and dark = shiny
- specular 0.2 on the rock, no plastic highlights
- normal strength 1.4
- AO at 55%, not 100%. Full AO looks dirty

## Step 10. Displacement: from plastic to real

- mesh too light: displacement only moves vertices that exist. Needs a very dense mesh (Subdivision, Simple)
- strength too high: 0.40 gave needles, 0.12 still spiky. Sweet spot 0.045
- vertical "curtains" on the steepest slopes; blurring the whole height map makes it soapy
- the fix: slope-adaptive smoothing, blur only the steepest ~12%

```python
# smooth the height only on the steepest slopes
import cv2, numpy as np
h = cv2.imread("height.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
gx = cv2.Sobel(h, cv2.CV_32F, 1, 0); gy = cv2.Sobel(h, cv2.CV_32F, 0, 1)
slope = np.sqrt(gx ** 2 + gy ** 2)
steep = (slope > np.percentile(slope, 88)).astype(np.float32)   # top ~12%
w = cv2.GaussianBlur(steep, (0, 0), 6)                          # soft transition
w = np.clip(w / (w.max() + 1e-6) * 1.5, 0, 1)
smooth = cv2.GaussianBlur(h, (0, 0), 4)
out = h * (1 - w) + smooth * w
cv2.imwrite("height_smooth.png", (np.clip(out, 0, 1) * 65535).astype(np.uint16))
```

## Step 11. Putting a flat texture on a ball

- UV sphere (equirect): seam + pinched poles
- mirror around the pole: mirror line
- triplanar: seamless but each side gets a small crop, blurry
- what worked: two hemispheres. Left half of the texture to the front hemisphere, right half to the back, azimuthal from each pole, soft cross-fade band at the equator, into one atlas

## Step 12. Bake, export, show it off

Bake to plain maps (color, roughness, normal), export GLB, render a 240-frame 24 fps turntable (ball fills 80-90% of frame, strong side light). Baking loses the moss sheen and subsurface: live shader for stills, GLB for portability.

## Honest limits

- One reference is usually not tileable: fine for hero shots, needs work for big terrain
- AI upscale detail is invented, not captured
- Real displacement is heavy: great for renders, too much for games
- Baking to GLB loses sheen and subsurface

## Cheat sheet

- Real texture as reference, never procedural for realism
- Generate each map separately, several candidates
- Pick the albedo with the least baked light
- Align everything to the albedo (the step that matters most)
- Rebuild the normal from the aligned height
- Albedo = sRGB, everything else = Non-Color
- Sharp mask for the look, blurred mask for height
- Dry rock: roughness 0.62-1.0, specular 0.2
- Displacement lower than you think (~0.045), smooth only the steep slopes
- Flat texture on a ball: two hemispheres, not a UV sphere
- 8K from 2.7K = upscale. Say it

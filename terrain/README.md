# Terrain

Real Norwegian terrain (Kartverket DTM, © Kartverket, CC BY 4.0, via the Geonorge WCS), with our ravine carved in and GPU erosion on top, exported to Blender.

- `dtm.py`: tiled, cached fetch of any area at any resolution (EPSG:25833, row 0 = south).
- `scout.py`: scans regions for a narrow gorge (12-35 m deep) in mellow ground with hills around.
- `blender_preview.py`: quick 3D preview render of a heightfield.
- `runlog.py`: **versioning**. Every run writes `runs/<time>_<stage>/manifest.json` (inputs, code commit, output hashes) and preview images, which are committed. Big arrays aren't committed; they're reproducible from the manifest. Animation frames go to the local-only `.capture/terrain/`.

Setup: `uv venv .venv && uv pip install --python .venv/bin/python numpy scipy tifffile imagecodecs matplotlib requests pyproj torch`

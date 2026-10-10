"""Fetch real Norwegian terrain (Kartverket DTM, CC BY 4.0) from the Geonorge WCS.

Data: © Kartverket, høydedata.no, licensed CC BY 4.0.
CRS: ETRS89 / UTM 33N (EPSG:25833), heights in metres (NN2000).
Requests are tiled and cached on disk so re-runs are free.
"""
from pathlib import Path
import io
import numpy as np
import requests
import tifffile

WCS = "https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833"
CACHE = Path(__file__).parent / "cache"
TILE = 500  # pixels per request side


def _tile(x0, y0, res):
    """One TILE×TILE tile with lower-left corner (x0, y0). Returns array, north row first."""
    f = CACHE / f"dtm_{res:g}m_{x0}_{y0}.npy"
    if f.exists():
        return np.load(f)
    x1, y1 = x0 + TILE * res, y0 + TILE * res
    r = requests.get(WCS, timeout=120, params={
        "service": "WCS", "request": "GetCoverage", "version": "1.0.0",
        "coverage": "nhm_dtm_topo_25833", "crs": "EPSG:25833",
        "bbox": f"{x0},{y0},{x1},{y1}", "width": TILE, "height": TILE, "format": "GeoTIFF",
    })
    r.raise_for_status()
    a = tifffile.imread(io.BytesIO(r.content)).astype(np.float32)
    a[(a < -500) | (a > 3000)] = np.nan  # nodata (sea / outside coverage)
    CACHE.mkdir(exist_ok=True)
    np.save(f, a)
    return a


def fetch(x0, y0, x1, y1, res):
    """Heights over [x0,x1]×[y0,y1] at `res` m. Row 0 = south edge (y up, like Blender)."""
    span = TILE * res
    tx = range(int(x0 // span * span), int(x1), int(span))
    ty = range(int(y0 // span * span), int(y1), int(span))
    rows = []
    for ty0 in ty:
        rows.append(np.hstack([_tile(tx0, ty0, res)[::-1] for tx0 in tx]))  # flip to south-first
    full = np.vstack(rows)
    ox, oy = tx[0], ty[0]
    i0, j0 = int((x0 - ox) / res), int((y0 - oy) / res)
    return full[j0:j0 + int((y1 - y0) / res), i0:i0 + int((x1 - x0) / res)]

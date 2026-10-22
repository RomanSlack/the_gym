"""Fetch a used unit's photos off Fitness Equipment Empire (WooCommerce store API) into a piece's refs/, politely:
one API request, then the images 5-9 s apart, each recorded in piece.json.

    python3 equipment/tools/fee_fetch.py <piece> <fee-product-slug>
"""
import json
import random
import sys
import time
import urllib.request
from pathlib import Path

EQ = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def main():
    piece, slug = sys.argv[1:3]
    cache = EQ / ".cache" / f"{piece}.fee.json"
    if cache.exists():
        data = json.loads(cache.read_text())
    else:
        data = json.loads(get(f"https://www.fitnessequipmentempire.com/wp-json/wc/store/v1/products?slug={slug}"))
        cache.write_text(json.dumps(data))
        time.sleep(random.uniform(5, 9))
    srcs = []
    for im in data[0]["images"]:
        if im["src"] not in srcs:
            srcs.append(im["src"])
    pj = EQ / "pieces" / piece / "piece.json"
    d = json.loads(pj.read_text())
    refs = d.get("refs", [])
    print(piece, data[0]["name"], len(srcs), "images", flush=True)
    for url in srcs:
        if any(r["url"] == url for r in refs):
            continue
        b = get(url)
        ext = "png" if b[:4] == b"\x89PNG" else ("webp" if b[8:12] == b"WEBP" else "jpg")
        f = f"refs/ref_{len(refs) + 1:02d}.{ext}"
        (EQ / "pieces" / piece / f).write_bytes(b)
        refs.append({"file": f, "url": url, "source": "Fitness Equipment Empire (a used unit)"})
        print(" ", f, flush=True)
        time.sleep(random.uniform(5, 9))
    d["refs"] = refs
    pj.write_text(json.dumps(d, indent=1))


if __name__ == "__main__":
    main()

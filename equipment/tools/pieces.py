"""One folder per real product Roman picked: equipment/pieces/<piece>/ with piece.json, refs/ (photos), models/ (our 3D).

    python3 equipment/tools/pieces.py sync     picks.json -> a folder + piece.json per linked product (merges, never clobbers)
    python3 equipment/tools/pieces.py fetch    price + the full photo gallery for every piece not fetched yet

The same product linked on several list items (PWR Play on the cable rows) is one piece with several `items`.
Fetching is polite on purpose (Roman: don't get my IP flagged): one page request per product, ever (cached in
equipment/.cache/), 5-10 s apart, a normal browser UA; photos come off the shops' CDNs. Shopify shops answer
/products/<handle>.js with the price + every image, the rest are read from the page's JSON-LD / og tags.
refs/ stays out of git: the photos belong to the shops.
"""
import html
import json
import random
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

EQ = Path(__file__).resolve().parents[1]
PIECES, CACHE = EQ / "pieces", EQ / ".cache"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
BRANDS = {"shop.lifefitness.com": "Life Fitness", "www.roguefitness.com": "Rogue", "atlantisstrength.com": "Atlantis",
          "titan.fitness": "Titan", "repfitness.com": "REP", "eleiko.com": "Eleiko", "gymleco.com": "Gymleco",
          "giantlifting.com": "GIANT", "strencor.com": "Strencor", "gmwdfitness.com": "GMWD"}
# brands named in the product title win over the shop (Hammer Strength is sold by Life Fitness, Precor by dealers)
TITLE_BRANDS = ["Hammer Strength", "Life Fitness", "Precor", "StairMaster", "VersaClimber", "Woodway", "Body-Solid",
                "Concept2", "Eleiko", "Rogue", "Titan", "Atlantis", "The abs Company", "AbMat", "TITAN"]
now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def model_name(title):
    t = re.split(r"\s+\|\s+", title)[0]
    t = re.split(r"\s+-\s+|\s+w/\s+", t)[0]  # shop taglines: "Monster Half Rack - Space-Saving Rack"
    t = re.sub(r"\s*\b(ModelBlack|The Ultimate Commercial Fitness Treadmill)\b.*$", "", t)
    return t.strip()


def brand_of(title, url):
    for b in TITLE_BRANDS:
        if title.lower().startswith(b.lower()) or f" {b.lower()} " in f" {title.lower()} ":
            return {"TITAN": "Titan"}.get(b, b)
    if title.startswith(("Insignia Series", "Axiom Series", "Signature Series")):
        return "Life Fitness"
    return BRANDS.get(urlparse(url).hostname, urlparse(url).hostname.replace("www.", ""))


def clean_url(u):
    p = urlparse(u)
    keep = [q for q in p.query.split("&") if q.startswith(("variant=", "sku=", "attribute_"))]
    return p._replace(path=re.sub(r"/{2,}", "/", p.path), query="&".join(keep)).geturl()


def sync():
    picks = json.loads((EQ / "picks.json").read_text())
    names = {i["id"]: i["name"] for c in json.loads((EQ / "list.json").read_text())["categories"] for i in c["items"]}
    names.update({c["id"]: c["name"] for c in picks.get("custom", [])})
    found = {}
    for item, st in picks["items"].items():
        for l in st["links"]:
            url = clean_url(l["url"])
            key = urlparse(url)._replace(query="", fragment="").geturl().rstrip("/")
            title = l.get("title") or urlparse(url).path.rstrip("/").split("/")[-1].replace("-", " ")
            p = found.setdefault(key, {"title": title, "url": url, "items": [], "picked": l["added"], "by": l.get("by")})
            if item not in p["items"]:
                p["items"].append(item)
    ids = {}
    for key, p in found.items():
        brand, model = brand_of(p["title"], p["url"]), model_name(p["title"])
        base = slug(model if model.lower().startswith(brand.lower()) else f"{brand} {model}")[:64].strip("-")
        pid = base if base not in ids.values() else f"{base}-{len(ids)}"
        ids[key] = pid
        f = PIECES / pid / "piece.json"
        old = json.loads(f.read_text()) if f.exists() else {}
        new = {"id": pid, "brand": brand, "model": model, "title": p["title"], "url": p["url"],
               "items": p["items"], "item_names": [names.get(i, i) for i in p["items"]], "picked": p["picked"],
               "source": "Claude's pick (Roman, 2026-10-23: a free hand, Life Fitness preferred)" if p["by"] == "claude"
               else "Roman's pick", "price": None, "refs": [], "status": "picked", "notes": ""}
        new.update({k: v for k, v in old.items() if k not in ("items", "item_names")})  # manual + fetched fields survive
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(found)} pieces in {PIECES}")


def get(url, accept="text/html"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "en-US,en"})
    return urllib.request.urlopen(req, timeout=20).read(4_000_000)


def page_data(pid, url):
    """(price, currency, [image urls]) from one cached request."""
    CACHE.mkdir(exist_ok=True)
    u = urlparse(url)
    m = re.search(r"/products/([^/?#]+)", u.path)
    if m:  # Shopify: the product's own JSON
        c = CACHE / f"{pid}.js.json"
        try:
            if not c.exists():
                c.write_bytes(get(f"{u.scheme}://{u.netloc}/products/{m.group(1)}.js", "application/json")); time.sleep(random.uniform(5, 10))
            j = json.loads(c.read_text())
            var = re.search(r"variant=(\d+)", u.query)
            v = next((v for v in j.get("variants", []) if var and str(v["id"]) == var.group(1)), None)
            price = (v or j).get("price")
            imgs = [urljoin(url, i if i.startswith("http") or i.startswith("//") else i) for i in j.get("images", [])]
            imgs = ["https:" + i if i.startswith("//") else i for i in imgs]
            return (price / 100 if isinstance(price, int) else None), "USD", imgs, "shopify json"
        except Exception:
            c.unlink(missing_ok=True)
    c = CACHE / f"{pid}.html"
    if not c.exists():
        c.write_bytes(get(url)); time.sleep(random.uniform(5, 10))
    page = c.read_text(errors="ignore")
    price, cur, imgs = None, None, []
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page, re.S | re.I):
        try:
            d = json.loads(blk.strip())
        except Exception:
            continue
        for o in (d if isinstance(d, list) else d.get("@graph", [d])):
            if not isinstance(o, dict) or "Product" not in str(o.get("@type")):
                continue
            im = o.get("image") or []
            imgs += [x if isinstance(x, str) else x.get("url", "") for x in (im if isinstance(im, list) else [im])]
            offs = o.get("offers") or {}
            offs = offs if isinstance(offs, list) else [offs]
            for of in offs:
                pr = of.get("price") or of.get("lowPrice")
                if pr and price is None:
                    price, cur = float(str(pr).replace(",", "")), of.get("priceCurrency")
    for mm in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:image|og:price:amount|product:price:amount|og:price:currency|product:price:currency)["\'][^>]*>', page, re.I):
        tag = mm.group(0)
        val = re.search(r'content=["\']([^"\']+)', tag)
        if not val:
            continue
        val = html.unescape(val.group(1))
        if "og:image" in tag:
            imgs.append(val)
        elif "amount" in tag and price is None:
            try:
                price = float(val.replace(",", ""))
            except ValueError:
                pass
        elif "currency" in tag and not cur:
            cur = val
    return price, cur, [urljoin(url, i) for i in imgs if i], "page"


def fetch():
    for f in sorted(PIECES.glob("*/piece.json")):
        p = json.loads(f.read_text())
        if p.get("fetched") or p.get("refs"):          # photos already there (some added by hand): never refetched
            continue
        try:
            price, cur, imgs, how = page_data(p["id"], p["url"])
        except Exception as e:
            print(f"  {p['id']}: page not reachable ({e.__class__.__name__}); stays a plain link")
            p["fetched"] = {"at": now(), "error": str(e)[:120]}
            f.write_text(json.dumps(p, indent=1, ensure_ascii=False) + "\n")
            continue
        refs, seen = [], set()
        for u in imgs:
            u = re.sub(r"_\d+x\d+(?=\.\w+)", "", u)  # Shopify size suffix -> the original
            if u in seen or len(refs) >= 14:
                continue
            seen.add(u)
            try:
                data = get(u, "image/*")
            except Exception:
                continue
            ext = (Path(urlparse(u).path).suffix or ".jpg").lower()[:5]
            dst = PIECES / p["id"] / "refs" / f"ref_{len(refs) + 1:02d}{ext}"
            dst.parent.mkdir(exist_ok=True)
            dst.write_bytes(data)
            refs.append({"file": str(dst.relative_to(f.parent)), "url": u})
            time.sleep(random.uniform(0.8, 1.6))
        if price is not None and not p.get("price"):
            p["price"] = {"amount": price, "currency": cur or "USD", "kind": "list price on the linked page", "at": now()}
        p["refs"], p["fetched"] = refs, {"at": now(), "how": how}
        f.write_text(json.dumps(p, indent=1, ensure_ascii=False) + "\n")
        print(f"  {p['id']}: {len(refs)} photos, price {p['price']['amount'] if p.get('price') else 'none on page'}", flush=True)


if __name__ == "__main__":
    {"sync": sync, "fetch": fetch}[sys.argv[1] if len(sys.argv) > 1 else "sync"]()

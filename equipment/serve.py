"""The equipment shopping list: a tiny local server, separate from the building pipeline.

    python3 equipment/serve.py      then open http://localhost:5290

list.json is the master list (what we need). Every click on the page is posted as one action, appended to
history/curation.jsonl (the curation replay: who picked what, when) and folded into picks.json (the current state).
Each pasted link gets its page title + preview image fetched in the background (refs/, kept out of git: product
photos belong to the shops).
"""
import html
import json
import re
import threading
import urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
PICKS, LOG, REFS = HERE / "picks.json", HERE / "history" / "curation.jsonl", HERE / "refs"
LOCK = threading.Lock()
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def load():
    return json.loads(PICKS.read_text()) if PICKS.exists() else {"items": {}, "custom": []}


def save(state):
    tmp = PICKS.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False))
    tmp.replace(PICKS)  # atomic: a crash never leaves a half-written file


def apply(state, a):
    it = state["items"].setdefault(a["id"], {"links": [], "skipped": False}) if "id" in a else None
    if a["action"] == "add_link" and a["url"] not in [l["url"] for l in it["links"]]:
        it["links"].append({"url": a["url"], "added": a["t"]})
    elif a["action"] == "remove_link":
        it["links"] = [l for l in it["links"] if l["url"] != a["url"]]
    elif a["action"] == "skip":
        it["skipped"] = bool(a["value"])
    elif a["action"] == "note":
        it["note"] = a["value"]
    elif a["action"] == "add_item":
        state["custom"].append({"id": a["id"], "cat": a["cat"], "name": a["name"], "qty": a.get("qty", 1), "zone": a.get("zone", "")})
    elif a["action"] == "remove_item":
        state["custom"] = [c for c in state["custom"] if c["id"] != a["id"]]
        state["items"].pop(a["id"], None)
    elif a["action"] == "link_meta":
        for l in it["links"]:
            if l["url"] == a["url"]:
                l.update({k: a[k] for k in ("title", "image", "ref") if a.get(k)})


def act(a):
    a["t"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LOCK:
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a") as f:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
        state = load()
        apply(state, a)
        save(state)
    if a["action"] == "add_link":
        threading.Thread(target=fetch_meta, args=(a["id"], a["url"]), daemon=True).start()
    return state


def fetch_meta(item, url):
    """Best effort: many shops block bots, then the link just stays a plain link."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
        page = urllib.request.urlopen(req, timeout=12).read(800_000).decode("utf-8", "ignore")
    except Exception:
        return
    def meta(*names):
        for n in names:
            m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]*content=["\']([^"\']+)' % re.escape(n), page, re.I) or \
                re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']%s["\']' % re.escape(n), page, re.I)
            if m:
                return html.unescape(m.group(1)).strip()
    title = meta("og:title", "twitter:title")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
        title = html.unescape(m.group(1)).strip() if m else None
    image, ref = meta("og:image", "og:image:url", "twitter:image"), None
    if image:
        image = urljoin(url, image)
        try:
            req = urllib.request.Request(image, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=12).read(8_000_000)
            ext = (Path(urlparse(image).path).suffix or ".jpg")[:5]
            n = len(list((REFS / item).glob("*"))) if (REFS / item).exists() else 0
            dst = REFS / item / f"ref_{n + 1:02d}{ext}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            ref = str(dst.relative_to(HERE))
        except Exception:
            pass
    if title or image:
        act({"action": "link_meta", "id": item, "url": url, "title": title and title[:200], "image": image, "ref": ref})


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def send(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/shop.html"
        if self.path == "/api/state":
            with LOCK:
                return self.send({"list": json.loads((HERE / "list.json").read_text()), "picks": load()})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/act":
            return self.send({"error": "not found"}, 404)
        try:
            a = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            return self.send({"picks": act(a)})
        except Exception as e:
            return self.send({"error": str(e)}, 400)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("equipment list on http://localhost:5290")
    ThreadingHTTPServer(("127.0.0.1", 5290), H).serve_forever()

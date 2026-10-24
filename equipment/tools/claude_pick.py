"""Claude's picks for list items Roman left open (Roman, 2026-10-23: "for those other ones you have liberty to go find
the right ones and get the reference images, preference is on Life Fitness"). Logged to history/curation.jsonl like
Roman's clicks but marked by: claude, folded into picks.json the same way (serve.apply), so the replay and the pieces
say who chose what. Titles and photos come from the shop's cached catalogue (.cache/lf_catalog_p*.json, fetched once),
so no product page is requested again; pieces.py fetch then reads the seeded cache instead of the shop.

    python3 equipment/tools/claude_pick.py <list item> <shop handle> [<list item> <shop handle> ...]
    python3 equipment/tools/claude_pick.py --note <list item> "<note>"
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EQ))
import serve  # noqa: E402

SHOP = "https://shop.lifefitness.com/products/"


def catalogue():
    out = {}
    for f in sorted((EQ / ".cache").glob("lf_catalog_p*.json")):
        for p in json.loads(f.read_text())["products"]:
            out[p["handle"]] = p
    return out


def log(a):
    a["t"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with serve.LOCK:
        with serve.LOG.open("a") as f:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
        state = serve.load()
        serve.apply(state, a)
        serve.save(state)


def seed(handle, p):
    """The shop's own product JSON (/products/<handle>.js) in the shape pieces.py reads, from the catalogue entry."""
    js = {"handle": handle, "title": p["title"], "images": [i["src"] for i in p.get("images", [])],
          "variants": [{"id": v["id"], "price": round(float(v["price"]) * 100)} for v in p.get("variants", [])]}
    js["price"] = js["variants"][0]["price"] if js["variants"] else None
    return js


def main(args):
    if args[:1] == ["--note"]:
        log({"action": "note", "id": args[1], "value": args[2], "by": "claude"})
        return
    cat = catalogue()
    seeds = json.loads((EQ / ".cache" / "claude_seeds.json").read_text()) if (EQ / ".cache" / "claude_seeds.json").exists() else {}
    for item, handle in zip(args[::2], args[1::2]):
        p = cat[handle]
        url = SHOP + handle
        log({"action": "add_link", "id": item, "url": url, "by": "claude"})
        img = p["images"][0]["src"] if p.get("images") else None
        log({"action": "link_meta", "id": item, "url": url, "title": p["title"], "image": img, "by": "claude"})
        seeds[handle] = seed(handle, p)
        print(f"{item}: {p['title']} ({len(p.get('images', []))} photos)")
    (EQ / ".cache" / "claude_seeds.json").write_text(json.dumps(seeds))


if __name__ == "__main__":
    main(sys.argv[1:])

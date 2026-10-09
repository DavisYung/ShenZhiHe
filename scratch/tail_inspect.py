# -*- coding: utf-8 -*-
"""Inspect tail state of 2b.json / 4b.json / 8.json before appending."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

meta = json.load(open(os.path.join(ROOT, "pages", "meta.json"), encoding="utf-8"))
print("meta pages:", {k: v["pages"] for k, v in meta.items()})

for tid in ("2b", "4b", "8"):
    p = os.path.join(DATA, tid + ".json")
    if not os.path.exists(p):
        print(tid, "MISSING")
        continue
    t = json.load(open(p, encoding="utf-8"))
    secs = t["sections"]
    np = sum(len(s["points"]) for s in secs)
    used = sorted({pt["page"] for s in secs for pt in s["points"]})
    print("\n=== %s === title=%r sections=%d points=%d" % (tid, t.get("title"), len(secs), np))
    print("top-level keys:", list(t.keys()))
    print("used pages:", used)
    print("last 5 sections:")
    for s in secs[-5:]:
        print("  ", s["id"], "|", s["title"], "| keys:", list(s.keys()), "| pts:", len(s["points"]))
    print("sample point:")
    print(json.dumps(secs[-1]["points"][0], ensure_ascii=False, indent=2))
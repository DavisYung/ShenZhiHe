# -*- coding: utf-8 -*-
import json, os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TIDS = ["1a", "1b", "1c", "2a", "2b", "3a", "3b", "4a", "4b", "6", "8"]

total = 0
all_ids = {}
for tid in TIDS:
    path = os.path.join(BASE, tid + ".json")
    if not os.path.exists(path):
        print("MISSING", path)
        continue
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    print("=" * 70)
    print("### %s | top keys: %s" % (tid, list(data.keys()) if isinstance(data, dict) else type(data)))
    title = data.get("title") if isinstance(data, dict) else ""
    print("TITLE: %s" % title)
    secs = data.get("sections", []) if isinstance(data, dict) else []
    n = 0
    for sec in secs:
        print("  [%s] %s" % (sec.get("id"), sec.get("title")))
        for p in sec.get("points", []):
            n += 1
            all_ids[p.get("id")] = (tid, sec.get("id"), p.get("title"))
            print("    %-14s %s" % (p.get("id"), p.get("title")))
    total += n
    print("  -> %s points: %d" % (tid, n))

print("=" * 70)
print("TOTAL POINTS: %d" % total)
print("UNIQUE IDS: %d" % len(all_ids))
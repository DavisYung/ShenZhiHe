# -*- coding: utf-8 -*-
"""Confirm sections 2b-s1..s8 are untouched: compare against git/backup if available."""
import json, os, hashlib

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)
with open(DATA, "r", encoding="utf-8") as f:
    doc = json.load(f)

old = [s for s in doc["sections"] if s["id"] in {"2b-s%d" % i for i in range(1, 9)}]
assert len(old) == 8
for s in old:
    print("%s  pts=%d  pages=%s" % (
        s["id"], len(s["points"]),
        sorted({pt["page"] for pt in s["points"]})))
blob = json.dumps(old, ensure_ascii=False, sort_keys=True).encode("utf-8")
print("sha256(s1..s8 payload) =", hashlib.sha256(blob).hexdigest())
print("total points in s1..s8 =", sum(len(s["points"]) for s in old), "(expected 22)")
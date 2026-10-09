# -*- coding: utf-8 -*-
"""Final verification of f6chem/data/2b.json."""
import json, os

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)
with open(DATA, "r", encoding="utf-8") as f:
    doc = json.load(f)  # raises on invalid JSON

secs = doc["sections"]
ids = [s["id"] for s in secs]
pids = [pt["id"] for s in secs for pt in s["points"]]

assert len(ids) == len(set(ids)), "duplicate section id"
assert len(pids) == len(set(pids)), "duplicate point id"
new = [s for s in secs if s["id"] not in ("2b-s%d" % i for i in range(1, 9))]

bad = []
for s in new:
    n = len(s["points"])
    if not (3 <= n <= 6):
        bad.append("%s has %d points" % (s["id"], n))
        continue
    for pt in s["points"]:
        assert isinstance(pt["page"], int), "%s page not int" % pt["id"]
        assert 21 <= pt["page"] <= 39, "%s page out of input range" % pt["id"]
        for k in ("title", "body", "tags"):
            assert k in pt and pt[k], "%s missing %s" % (pt["id"], k)
if bad:
    raise SystemExit("POINTS-RANGE VIOLATIONS:\n  " + "\n  ".join(bad))
np = sum(len(s["points"]) for s in new)
pages = sorted({pt["page"] for s in new for pt in s["points"]})

print("json.load: OK")
print("total sections=%d, total points=%d" % (len(secs), len(pids)))
print("new sections=%d, new points=%d" % (len(new), np))
print("new section ids: %s" % ", ".join(s["id"] for s in new))
print("page coverage: %d-%d  (pages: %s)" % (min(pages), max(pages), ",".join(map(str, pages))))
print("original 2b-s1..s8 preserved: %d sections, %d points"
      % (len(secs) - len(new), len(pids) - np))
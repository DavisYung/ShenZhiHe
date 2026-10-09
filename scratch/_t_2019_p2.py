# -*- coding: utf-8 -*-
import json, io, re, sys

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2019_p2.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = io.open(MAP, "r", encoding="utf-8").read()
errs = []
if "\ufffd" in raw:
    errs.append("output contains U+FFFD")

data = json.loads(raw)
assert data["year"] == 2019

cat_ids = set()
for line in io.open(CAT, "r", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cat_ids.add(line.split("\t")[0])

points_seen = []
for m in data["mappings"]:
    ref = m["ref"]
    if not re.match(r"^2019-P2[ABC]-Q\d+(\([a-z0-9]+\))*$", ref):
        errs.append("bad ref format: " + ref)
    if not m["focus"] or len(m["focus"]) > 40:
        errs.append("focus len out of range (%d): %s" % (len(m["focus"]), ref))
    for p in m["points"]:
        if p not in cat_ids:
            errs.append("point not in catalog: %s (%s)" % (p, ref))
    points_seen.extend(m["points"])

refs = [m["ref"] for m in data["mappings"]]
if len(refs) != len(set(refs)):
    errs.append("duplicate refs")

map_points = set(points_seen)
for k in data["kw"]:
    if k not in map_points:
        errs.append("kw key not in mappings: " + k)
    for w in data["kw"][k]:
        if not (2 <= len(w) <= 8):
            errs.append("kw len %d: %s/%s" % (len(w), k, w))
        if "\ufffd" in w:
            errs.append("kw U+FFFD: " + k)

# 覆盖题号（去掉小问，看大题）
big = sorted(set(re.match(r"^(2019-P2[ABC]-Q\d+)", r).group(1) for r in refs))
kw_pts = len(data["kw"])
kw_words = sum(len(v) for v in data["kw"].values())

print("units:", len(data["mappings"]))
print("big-questions:", ",".join(big))
print("kw points:", kw_pts, "kw words:", kw_words)
print("distinct points:", len(map_points))
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)
print("OK")

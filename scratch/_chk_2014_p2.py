# -*- coding: utf-8 -*-
import json, sys, io

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
out_path = BASE + r"\map\2014_p2.json"
cat_path = BASE + r"\pp\catalog.tsv"

raw = open(out_path, encoding="utf-8").read()
errors = []

if "\ufffd" in raw:
    errors.append("JSON file contains U+FFFD replacement chars")

data = json.loads(raw)

cat_ids = set()
with open(cat_path, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if parts and parts[0]:
            cat_ids.add(parts[0])

refs = [m["ref"] for m in data["mappings"]]
if len(refs) != len(set(refs)):
    errors.append("duplicate refs: " + str([r for r in refs if refs.count(r) > 1]))

mpts = set()
for m in data["mappings"]:
    if not m.get("points"):
        errors.append("empty points: " + m["ref"])
    for p in m.get("points", []):
        mpts.add(p)
        if p not in cat_ids:
            errors.append("point not in catalog: %s (%s)" % (p, m["ref"]))
    fu = m.get("focus", "")
    if len(fu) > 40:
        errors.append("focus >40 chars (%d): %s" % (len(fu), m["ref"]))
    if any(ch == "\ufffd" for ch in fu):
        errors.append("focus has U+FFFD: " + m["ref"])

for k in data["kw"]:
    if k not in mpts:
        errors.append("kw key not in mappings: " + k)
    for w in data["kw"][k]:
        if not (2 <= len(w) <= 8):
            errors.append("kw word len %d: %s/%s" % (len(w), k, w))

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

sections = sorted({r.split("-")[1] for r in refs})
questions = sorted({r.split("-")[2] for r in refs})
print("PASS")
print("units:", len(data["mappings"]))
print("sections:", sections)
print("questions:", questions)
print("kw points:", len(data["kw"]))
print("distinct points:", len(mpts))

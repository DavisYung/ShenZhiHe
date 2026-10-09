# -*- coding: utf-8 -*-
import json, sys, io

MAP = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch\map\2016_p1b.json"
CAT = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = io.open(MAP, encoding="utf-8").read()
if "\ufffd" in raw:
    print("FAIL: U+FFFD present in output")
    sys.exit(1)

data = json.loads(raw)
assert data["year"] == 2016

cat_ids = set()
for line in io.open(CAT, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cat_ids.add(line.split("\t")[0])

errs = []
used = set()
empty_units = 0
refs = []
for m in data["mappings"]:
    refs.append(m["ref"])
    if not m["points"]:
        empty_units += 1
    for p in m["points"]:
        used.add(p)
        if p not in cat_ids:
            errs.append("unknown point %s in %s" % (p, m["ref"]))
    if len(m["focus"]) > 40:
        errs.append("focus too long in %s (%d)" % (m["ref"], len(m["focus"])))

kw = data["kw"]
for k in kw:
    if k not in used:
        errs.append("kw key not in mappings: %s" % k)
    if "\ufffd" in k:
        errs.append("ufffd in kw key %s" % k)

kw_pts = sum(len(v) for v in kw.values())

qs = sorted({r.split("-Q")[1].split("(")[0] for r in refs})
dup = [r for r in set(refs) if refs.count(r) > 1]
if dup:
    errs.append("duplicate refs: %s" % dup)

if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)

print("OK units=%d questions=%s kw_points=%d empty_points=%d unique_points=%d" % (
    len(data["mappings"]), ",".join(qs), kw_pts, empty_units, len(used)))

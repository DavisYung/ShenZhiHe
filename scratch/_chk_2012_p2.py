# -*- coding: utf-8 -*-
import json, re, sys, io

MAP = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2012_p2.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = open(MAP, "rb").read()
errs = []
if b"\xef\xbf\xbd" in raw:
    errs.append("file contains U+FFFD bytes")
text = raw.decode("utf-8")
if "\ufffd" in text:
    errs.append("file contains \\ufffd char")

data = json.loads(text)  # json.load check
assert data["year"] == 2012

cat_ids = set()
for line in open(CAT, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0]:
        cat_ids.add(parts[0])

pat = re.compile(r"^2012-P2[ABC]-Q\d+(\([A-Za-z]+\))+$")
refs = set()
used_pts = set()
for m in data["mappings"]:
    ref = m["ref"]
    if not pat.match(ref):
        errs.append("bad ref format: %s" % ref)
    if ref in refs:
        errs.append("dup ref: %s" % ref)
    refs.add(ref)
    pts = m["points"]
    if not (1 <= len(pts) <= 3):
        errs.append("%s has %d points" % (ref, len(pts)))
    for p in pts:
        if p not in cat_ids:
            errs.append("%s: point not in catalog: %s" % (ref, p))
        used_pts.add(p)
    if len(m["focus"]) > 40:
        errs.append("%s focus %d chars > 40" % (ref, len(m["focus"])))

for k, arr in data["kw"].items():
    if k not in used_pts:
        errs.append("kw key not in mappings: %s" % k)
    if not isinstance(arr, list) or not (1 <= len(arr) <= 8):
        errs.append("kw %s list len bad" % k)
    for w in arr:
        if not (2 <= len(w) <= 8):
            errs.append("kw %s word len bad (%d): %s" % (k, len(w), w))
        if any(ch == "\ufffd" for ch in w):
            errs.append("kw %s has ufffd" % k)

missing = used_pts - set(data["kw"].keys())
for p in sorted(missing):
    print("note: no kw for point", p)

print("units:", len(data["mappings"]))
print("refs:", ", ".join(sorted(refs)))
print("points used:", len(used_pts), "| kw keys:", len(data["kw"]),
      "| kw words:", sum(len(v) for v in data["kw"].values()))
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)
print("PASS: json ok, no ufffd, all point ids valid, formats ok")

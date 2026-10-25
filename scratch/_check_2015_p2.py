# -*- coding: utf-8 -*-
import json, io, sys

MAP = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2015_p2.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = io.open(MAP, "rb").read()
assert b"\xef\xbf\xbd" not in raw, "JSON 文件含 U+FFFD"
data = json.loads(raw.decode("utf-8"))
assert data["year"] == 2015

cat_ids = set()
for line in io.open(CAT, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    cat_ids.add(line.split("\t")[0])

errors = []
used = set()
refs = []
for m in data["mappings"]:
    ref, pts, focus = m["ref"], m["points"], m["focus"]
    refs.append(ref)
    if not ref.startswith("2015-P2") or ref[7] not in "ABC":
        errors.append("bad ref: " + ref)
    if not (1 <= len(pts) <= 3):
        errors.append("points count out of range: " + ref)
    for p in pts:
        used.add(p)
        if p not in cat_ids:
            errors.append("unknown point id: %s (%s)" % (p, ref))
    if len(focus) > 40:
        errors.append("focus too long (%d): %s" % (len(focus), ref))
    if "\ufffd" in json.dumps(m, ensure_ascii=False):
        errors.append("fffd in mapping: " + ref)

kw = data["kw"]
for k, words in kw.items():
    if k not in used:
        errors.append("kw key not in mappings: " + k)
    if k not in cat_ids:
        errors.append("kw key not in catalog: " + k)
    for w in words:
        if not (2 <= len(w) <= 8):
            errors.append("kw length %d: %s / %s" % (len(w), k, w))
        if "\ufffd" in w:
            errors.append("fffd in kw: " + k)

missing = used - set(kw.keys())
print("units=%d refs=%d kw_keys=%d kw_total=%d" % (
    len(data["mappings"]), len(refs), len(kw), sum(len(v) for v in kw.values())))
print("refs:", " ".join(refs))
print("points_without_kw:", sorted(missing))
if errors:
    print("ERRORS:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK")

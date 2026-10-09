# -*- coding: utf-8 -*-
import json, io, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
OUT = BASE + r"\map\2015_p1b.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = io.open(OUT, "r", encoding="utf-8").read()
errors = []
if "\ufffd" in raw:
    errors.append("output contains U+FFFD replacement char")

data = json.loads(raw)

cat_ids = set()
for line in io.open(CAT, "r", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cat_ids.add(line.split("\t")[0])

mappings = data["mappings"]
kw = data["kw"]

refs = [m["ref"] for m in mappings]
if len(refs) != len(set(refs)):
    errors.append("duplicate refs: " + str([r for r in refs if refs.count(r) > 1]))

used_points = set()
for m in mappings:
    if "ref" not in m or "points" not in m or "focus" not in m:
        errors.append("missing field in " + str(m))
        continue
    if len(m["focus"]) > 40:
        errors.append("focus too long (%d): %s" % (len(m["focus"]), m["ref"]))
    if not isinstance(m["points"], list):
        errors.append("points not list: " + m["ref"])
        continue
    if len(m["points"]) > 3:
        errors.append("too many points: " + m["ref"])
    for p in m["points"]:
        used_points.add(p)
        if p not in cat_ids:
            errors.append("point not in catalog: %s (from %s)" % (p, m["ref"]))

kw_points = set(kw.keys())
for p in kw_points:
    if p not in cat_ids:
        errors.append("kw point not in catalog: " + p)
    if p not in used_points:
        errors.append("kw point not used in mappings: " + p)
    if not isinstance(kw[p], list) or not kw[p]:
        errors.append("kw empty: " + p)
    for w in kw[p]:
        if "\ufffd" in w:
            errors.append("kw has U+FFFD: " + p)
        if len(w) > 8:
            errors.append("kw word too long (%d): %s / %s" % (len(w), p, w))

covered = sorted({m["ref"].split("-Q")[1].split("(")[0] for m in mappings}, key=lambda x: int(x))
print("units=%d kw_points=%d covered_questions=%s" % (len(mappings), len(kw_points), ",".join(covered)))
print("units_with_no_points=%d" % sum(1 for m in mappings if not m["points"]))

if errors:
    print("FAIL")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS")

# -*- coding: utf-8 -*-
import json, io, sys, re

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2020_p1b_b.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = io.open(MAP, encoding="utf-8").read()
assert "\ufffd" not in raw, "FOUND U+FFFD in map json"
d = json.loads(raw)

cat = {}
for line in io.open(CAT, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2:
        cat[p[0]] = p[1]

ids = set()
bad = []
for m in d["mappings"]:
    for pid in m["points"]:
        ids.add(pid)
        if pid not in cat:
            bad.append((m["ref"], pid))

kwbad = [k for k in d["kw"] if k not in cat]
kworphan = [k for k in d["kw"] if k not in ids]

refs = [m["ref"] for m in d["mappings"]]
dup = [r for r in set(refs) if refs.count(r) > 1]
q = sorted({re.search(r"Q(\d+)", r).group(1) for r in refs}, key=int)
focus_bad = [m["ref"] for m in d["mappings"] if not m["focus"] or len(m["focus"]) > 40]
kwlen_bad = [(k, w) for k, ws in d["kw"].items() for w in ws if not (2 <= len(w) <= 8)]
empty_pts = [m["ref"] for m in d["mappings"] if not m["points"]]

print("units =", len(d["mappings"]))
print("refs_dup =", dup)
print("points_not_in_catalog =", bad)
print("kw_keys_not_in_catalog =", kwbad)
print("kw_keys_orphan(not in any points) =", kworphan)
print("focus_bad =", focus_bad)
print("kw_len_bad =", kwlen_bad)
print("empty_points =", empty_pts)
print("kw_point_count =", len(d["kw"]))
print("questions =", q)
ok = not (bad or kwbad or kworphan or dup or focus_bad or kwlen_bad)
print("RESULT =", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

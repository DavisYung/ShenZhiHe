# -*- coding: utf-8 -*-
import json, io, sys, os

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
JP = os.path.join(BASE, "map", "2023_p1b_a.json")
CAT = os.path.join(BASE, "pp", "catalog.tsv")

raw = io.open(JP, "rb").read()
bad = raw.count(b"\xef\xbf\xbd")
txt = raw.decode("utf-8")
d = json.loads(txt)

ids = set()
for line in io.open(CAT, encoding="utf-8"):
    p = line.split("\t")
    if p and p[0].strip():
        ids.add(p[0].strip())

errs = []
if bad:
    errs.append("U+FFFD count=%d" % bad)

maps = d["mappings"]
refs = [m["ref"] for m in maps]
if len(refs) != len(set(refs)):
    errs.append("duplicate ref")

used = set()
for m in maps:
    if not m["ref"].startswith("2023-P1B-Q"):
        errs.append("bad ref prefix: " + m["ref"])
    if not (0 <= len(m["points"]) <= 3):
        errs.append("points count out of range: %s -> %d" % (m["ref"], len(m["points"])))
    for pid in m["points"]:
        used.add(pid)
        if pid not in ids:
            errs.append("point not in catalog: %s (%s)" % (pid, m["ref"]))
    f = m["focus"]
    if not f or len(f) > 40:
        errs.append("focus length %d: %s" % (len(f), m["ref"]))

kw = d["kw"]
for k, v in kw.items():
    if k not in ids:
        errs.append("kw key not in catalog: " + k)
    if k not in used:
        errs.append("kw key not referenced by any mapping: " + k)
    if not (1 <= len(v) <= 8):
        errs.append("kw size out of range: %s -> %d" % (k, len(v)))
    for w in v:
        if len(w) < 2 or (len(w) > 8 and not any(c.isdigit() for c in w)):
            errs.append("kw term length %d (%s): %s" % (len(w), k, w))

qs = sorted(set(r.split("-Q")[1].split("(")[0] for r in refs))
print("units=%d questions=%s kw_points=%d kw_terms=%d" % (
    len(maps), ",".join(qs), len(kw), sum(len(v) for v in kw.values())))
print("fffd=%d" % bad)
if errs:
    print("FAIL")
    for e in errs:
        print(" - " + e)
    sys.exit(1)
print("OK")

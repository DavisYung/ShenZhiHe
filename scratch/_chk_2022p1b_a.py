import json, io, sys, os

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = os.path.join(BASE, "map", "2022_p1b_a.json")
CAT = os.path.join(BASE, "pp", "catalog.tsv")

with io.open(MAP, encoding="utf-8") as f:
    raw = f.read()

errs = []
if "\ufffd" in raw:
    errs.append("found U+FFFD replacement char")

data = json.loads(raw)
ids = set()
with io.open(CAT, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if p and p[0]:
            ids.add(p[0])

maps = data["mappings"]
kw = data["kw"]
refs = [m["ref"] for m in maps]

bad_ids = []
for m in maps:
    for pid in m["points"]:
        if pid not in ids:
            bad_ids.append((m["ref"], pid))
if bad_ids:
    errs.append("unknown point ids: %s" % bad_ids)

# kw keys must be point ids that appear in some mapping
for k in kw:
    if k not in ids:
        errs.append("kw key not in catalog: %s" % k)

# focus length check
for m in maps:
    if len(m["focus"]) > 40:
        errs.append("focus too long (%d): %s" % (len(m["focus"]), m["ref"]))

# kw term length 2-8 chars (skip formula-like entries containing spaces/long formulas)
for k, terms in kw.items():
    for t in terms:
        if len(t) < 2:
            errs.append("kw term too short: %s -> %s" % (k, t))

qnums = sorted(set(r.split("-Q")[1].split("(")[0] for r in refs))
print("units:", len(maps))
print("questions:", qnums)
print("kw points:", len(kw), "terms:", sum(len(v) for v in kw.values()))
print("empty-points units:", [m["ref"] for m in maps if not m["points"]])
print("ERRORS:", errs if errs else "none")

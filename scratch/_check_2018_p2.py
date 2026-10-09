import json, sys
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
jp = BASE + r"\map\2018_p2.json"
raw = open(jp, encoding="utf-8").read()
assert "\ufffd" not in raw, "U+FFFD found in json"
data = json.loads(raw)
cat_ids = set()
for ln in open(BASE + r"\pp\catalog.tsv", encoding="utf-8"):
    ln = ln.rstrip("\n")
    if ln:
        cat_ids.add(ln.split("\t")[0])
errs = []
used = set()
for m in data["mappings"]:
    for p in m["points"]:
        used.add(p)
        if p not in cat_ids:
            errs.append("missing point: " + p + " @ " + m["ref"])
for k in data["kw"]:
    if k not in used:
        errs.append("kw key not in mappings: " + k)
refs = [m["ref"] for m in data["mappings"]]
if len(refs) != len(set(refs)):
    errs.append("duplicate refs")
print("units:", len(data["mappings"]))
print("refs:", sorted(set(r.split("-Q")[1][:1] for r in refs)))
print("kw points:", len(data["kw"]))
print("errors:", errs if errs else "NONE")
sys.exit(1 if errs else 0)

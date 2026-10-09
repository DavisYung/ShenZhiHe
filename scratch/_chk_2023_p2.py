import json, re, io, sys

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
OUT = BASE + r"\map\2023_p2.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = open(OUT, "rb").read()
txt = raw.decode("utf-8")  # raises if not valid utf-8
errs = []
if "\ufffd" in txt:
    errs.append("file contains U+FFFD")

data = json.loads(txt)  # json.load passes
assert data["year"] == 2023

cat_ids = set()
for line in open(CAT, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cat_ids.add(line.split("\t")[0])

used = set()
refs = []
for m in data["mappings"]:
    ref = m["ref"]
    refs.append(ref)
    if not re.match(r"^2023-P2[ABC]-Q\d(\([a-z]+\))+(\(\d+\))?$", ref):
        errs.append("bad ref format: " + ref)
    if not m["points"]:
        errs.append("empty points: " + ref)
    if len(m["focus"]) > 40:
        errs.append("focus >40: %s (%d)" % (ref, len(m["focus"])))
    for p in m["points"]:
        if p not in cat_ids:
            errs.append("point not in catalog: %s (%s)" % (p, ref))
        used.add(p)

if len(refs) != len(set(refs)):
    errs.append("duplicate refs")

for p in data["kw"]:
    if p not in used:
        errs.append("kw key not in mappings: " + p)

sections = sorted(set(re.match(r"^2023-P2([ABC])-Q(\d+)", r).groups() for r in refs))
print("units:", len(data["mappings"]))
print("sections/questions:", sections)
print("kw points:", len(data["kw"]))
print("unique points:", len(used))
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)
print("PASS")

import json, re, sys

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
JP = BASE + r"\map\2020_p1b_a.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = open(JP, encoding="utf-8").read()
errs = []

if "\ufffd" in raw:
    errs.append("U+FFFD found in json text")

data = json.loads(raw)

ids = set()
for line in open(CAT, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0]:
        ids.add(parts[0])

refs = []
for m in data["mappings"]:
    refs.append(m["ref"])
    for p in m["points"]:
        if p not in ids:
            errs.append("bad point_id: %s (ref %s)" % (p, m["ref"]))
    f = m["focus"]
    if not f or len(f) > 40:
        errs.append("focus length bad (%d): %s" % (len(f), m["ref"]))
    if not re.fullmatch(r"2020-P1B-Q\d(\([a-z]\)|\(i+\))*", m["ref"]):
        errs.append("ref format bad: %s" % m["ref"])

if len(refs) != len(set(refs)):
    errs.append("duplicate refs")

used = set()
for m in data["mappings"]:
    used.update(m["points"])
for k in data["kw"]:
    if k not in ids:
        errs.append("kw key not in catalog: %s" % k)
    if k not in used:
        errs.append("kw key not used by any unit: %s" % k)
    for w in data["kw"][k]:
        if not (2 <= len(w) <= 8):
            errs.append("kw len bad: %s / %s" % (k, w))

for k in used:
    if k not in data["kw"]:
        errs.append("point without kw entry: %s" % k)

print("units:", len(data["mappings"]))
print("kw points:", len(data["kw"]))
print("Q covered:", sorted(set(r.split("Q")[1][0] for r in refs)))
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)
print("OK")

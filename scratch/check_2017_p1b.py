import json, io, sys

MAP = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2017_p1b.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = open(MAP, encoding="utf-8").read()
assert "\ufffd" not in raw, "U+FFFD found in output"
data = json.loads(raw)

cat_ids = set()
with io.open(CAT, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if parts and parts[0]:
            cat_ids.add(parts[0])

errs = []
used = set()
for m in data["mappings"]:
    for p in m["points"]:
        used.add(p)
        if p not in cat_ids:
            errs.append("unknown point %s in %s" % (p, m["ref"]))
    if len(m["points"]) > 3:
        errs.append("too many points in %s" % m["ref"])
    if len(m["focus"]) > 40:
        errs.append("focus too long in %s" % m["ref"])

for k in data["kw"]:
    if k not in used:
        errs.append("kw key not in mappings: %s" % k)
    if not data["kw"][k]:
        errs.append("kw empty for %s" % k)
    for item in data["kw"][k]:
        if len(item) < 2:
            errs.append("kw item too short for %s: %r" % (k, item))
        if "\ufffd" in item:
            errs.append("kw item has replacement char: %r" % item)

refs = [m["ref"] for m in data["mappings"]]
if len(refs) != len(set(refs)):
    errs.append("duplicate refs")

if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)

qnums = sorted({r.split("-Q")[1].split("(")[0] for r in refs})
nkw = sum(len(v) for v in data["kw"].values())
print("OK units=%d coverage=Q%s kw_points=%d" % (len(refs), ",".join(qnums), len(data["kw"])))

import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2023_p1b_b.json"
CAT = BASE + r"\pp\catalog.tsv"

errs = []

raw = io.open(MAP, "r", encoding="utf-8").read()
if "\ufffd" in raw:
    errs.append("found U+FFFD in json file")

data = json.loads(raw)

ids = set()
for line in io.open(CAT, "r", encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0].strip():
        ids.add(parts[0].strip())

mappings = data.get("mappings", [])
kw = data.get("kw", {})

refs = [m["ref"] for m in mappings]
if len(refs) != len(set(refs)):
    errs.append("duplicate refs: %s" % [r for r in refs if refs.count(r) > 1])

used = set()
for m in mappings:
    r = m["ref"]
    if not re.fullmatch(r"2023-P1B-Q\d+(\([a-z0-9]+\))*", r):
        errs.append("bad ref format: %s" % r)
    f = m.get("focus")
    if not isinstance(f, str) or not f:
        errs.append("missing focus: %s" % r)
    elif len(f) > 40:
        errs.append("focus too long (%d): %s" % (len(f), r))
    pts = m.get("points")
    if not isinstance(pts, list) or len(pts) > 3:
        errs.append("points not a list<=3: %s" % r)
    for p in pts or []:
        used.add(p)
        if p not in ids:
            errs.append("point id not in catalog: %s (%s)" % (p, r))

for k, v in kw.items():
    if k not in ids:
        errs.append("kw key not in catalog: %s" % k)
    if k not in used:
        errs.append("kw key not referenced by any mapping: %s" % k)
    if not isinstance(v, list):
        errs.append("kw value not a list: %s" % k)
        continue
    for w in v:
        if not (2 <= len(w) <= 8):
            errs.append("kw term length out of 2-8: %s -> %s (%d)" % (k, w, len(w)))

qnums = sorted({int(re.search(r"Q(\d+)", r).group(1)) for r in refs})
print("units:", len(mappings))
print("questions:", qnums)
print("kw points:", len(kw))
print("ERRORS:", len(errs))
for e in errs:
    print("  -", e)
sys.exit(1 if errs else 0)

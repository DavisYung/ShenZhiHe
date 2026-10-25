import json, io, sys, os, re

MAP = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2022_p1b_b.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

errs = []

with io.open(MAP, encoding="utf-8") as f:
    raw = f.read()
if "\ufffd" in raw:
    errs.append("U+FFFD found in json raw text")
data = json.loads(raw)

ids = set()
with io.open(CAT, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if parts and parts[0].strip():
            ids.add(parts[0].strip())

mappings = data.get("mappings", [])
kw = data.get("kw", {})

used = set()
refs = []
qs = set()
for m in mappings:
    refs.append(m["ref"])
    mt = re.match(r"2022-P1B-Q(\d+)", m["ref"])
    if not mt:
        errs.append("bad ref format: " + m["ref"])
    else:
        qs.add(int(mt.group(1)))
    for p in m["points"]:
        used.add(p)
        if p not in ids:
            errs.append("point id not in catalog: " + p)
    if not m.get("focus") or len(m["focus"]) > 40:
        errs.append("focus missing or >40 chars: " + m["ref"])
    if len(m["points"]) > 3:
        errs.append("too many points: " + m["ref"])

for k in kw:
    if k not in ids:
        errs.append("kw key not in catalog: " + k)
    if k not in used:
        errs.append("kw key not referenced by any mapping: " + k)
    if not isinstance(kw[k], list) or not (0 <= len(kw[k]) <= 8):
        errs.append("kw bad list: " + k)
    for w in kw[k]:
        if not (2 <= len(w) <= 8):
            errs.append("kw word length out of 2-8: " + k + " / " + w)

if data.get("year") != 2022:
    errs.append("year != 2022")

sys.stdout.write("units=%d\n" % len(mappings))
sys.stdout.write("questions=%s\n" % ",".join(str(q) for q in sorted(qs)))
sys.stdout.write("kw_points=%d\n" % len(kw))
sys.stdout.write("kw_words=%d\n" % sum(len(v) for v in kw.values()))
sys.stdout.write("used_ids=%d\n" % len(used))
if errs:
    sys.stdout.write("ERRORS(%d):\n" % len(errs))
    for e in errs:
        sys.stdout.write("  - " + e + "\n")
else:
    sys.stdout.write("OK\n")

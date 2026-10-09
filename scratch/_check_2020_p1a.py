import json, io, sys

MAP = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch\map\2020_p1a.json"
CAT = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = open(MAP, "rb").read()
text = raw.decode("utf-8")
assert "\\ufffd" not in text and "�" not in text, "U+FFFD found in output"

data = json.loads(text)
ids = set()
for line in open(CAT, encoding="utf-8"):
    line = line.rstrip("\n")
    if line:
        ids.add(line.split("\t")[0])

refs = []
bad = []
empty = 0
for m in data["mappings"]:
    refs.append(m["ref"])
    if not m["points"]:
        empty += 1
    for p in m["points"]:
        if p not in ids:
            bad.append((m["ref"], p))
    if len(m["focus"]) > 30:
        print("focus too long:", m["ref"], len(m["focus"]))
    if any("�" in s for s in [m["focus"]] + m["points"]):
        print("FFFD in entry:", m["ref"])

ns = [int(r.split("-Q")[1]) for r in refs]
print("json.load OK")
print("units:", len(refs))
print("empty mappings:", empty)
print("range: Q%d-Q%d" % (min(ns), max(ns)))
print("missing ids:", bad if bad else "none")

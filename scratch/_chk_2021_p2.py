import json, io

OUT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2021_p2.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = open(OUT, "rb").read()
assert b"\xef\xbf\xbd" not in raw, "file contains U+FFFD"
data = json.loads(raw.decode("utf-8"))
assert data["year"] == 2021

ids = set()
for ln in open(CAT, encoding="utf-8"):
    ln = ln.rstrip("\n")
    if ln:
        ids.add(ln.split("\t")[0])

mapped = set()
for m in data["mappings"]:
    assert m["points"], m["ref"]
    for p in m["points"]:
        assert p in ids, f"unknown point {p} in {m['ref']}"
        mapped.add(p)
    assert len(m["focus"]) <= 40, (m["ref"], len(m["focus"]))
    ref = m["ref"]
    assert ref.startswith("2021-P2") and ref[7] in "ABC", ref

for p in data["kw"]:
    assert p in mapped, f"kw key {p} not in mappings"
    for w in data["kw"][p]:
        assert 2 <= len(w) <= 8, (p, w)

print("OK units=%d kw_points=%d refs=%s" % (
    len(data["mappings"]), len(data["kw"]),
    ",".join(sorted({m["ref"].split("-")[1] for m in data["mappings"]}))))
q = sorted({m["ref"].split("-Q")[1].split("(")[0] for m in data["mappings"]})
print("questions:", q)

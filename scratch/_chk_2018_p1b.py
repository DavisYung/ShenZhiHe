import json, io, sys
MAP = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2018_p1b.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"
raw = open(MAP, "rb").read()
bad = raw.count(b"\xef\xbf\xbd")
print("replacement-char count:", bad)
d = json.loads(raw.decode("utf-8"))
cat_ids = set()
for line in io.open(CAT, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0]:
        cat_ids.add(parts[0])
missing = []
used = set()
for m in d["mappings"]:
    assert m["ref"].startswith("2018-P1B-Q"), m["ref"]
    for p in m["points"]:
        used.add(p)
        if p not in cat_ids:
            missing.append((m["ref"], p))
print("units:", len(d["mappings"]))
print("units with empty points:", sum(1 for m in d["mappings"] if not m["points"]))
print("missing point ids:", missing)
print("kw keys not in mappings:", [k for k in d["kw"] if k not in used])
print("points with kw:", len(d["kw"]), "total kw items:", sum(len(v) for v in d["kw"].values()))
long_focus = [m["ref"] for m in d["mappings"] if len(m["focus"]) > 40]
print("focus >40 chars:", long_focus)
print("focus max len:", max(len(m["focus"]) for m in d["mappings"]))
refs = [m["ref"] for m in d["mappings"]]
print("dup refs:", len(refs) - len(set(refs)))
qs = sorted({r.split("-Q")[1].split("(")[0] for r in refs}, key=int)
print("questions covered:", qs)

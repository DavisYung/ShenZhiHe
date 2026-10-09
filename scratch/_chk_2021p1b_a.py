import json, io, os, re

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = os.path.join(BASE, "map", "2021_p1b_a.json")
CAT = os.path.join(BASE, "pp", "catalog.tsv")

raw = open(MAP, "rb").read()
txt = raw.decode("utf-8")
errs = []

# 1) json.load
data = json.loads(txt)
print("[OK] json.load passed")

# 2) U+FFFD
if "\ufffd" in txt:
    for i, line in enumerate(txt.splitlines(), 1):
        if "\ufffd" in line:
            errs.append("U+FFFD at line %d" % i)
else:
    print("[OK] no U+FFFD")

# 3) point ids in catalog
cat_ids = set()
for line in io.open(CAT, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0]:
        cat_ids.add(parts[0].strip())

used = set()
for m in data["mappings"]:
    for p in m["points"]:
        used.add(p)
        if p not in cat_ids:
            errs.append("unknown point_id: %s (ref %s)" % (p, m["ref"]))

# kw keys must be point ids too
for k in data["kw"]:
    if k not in cat_ids:
        errs.append("kw key not in catalog: %s" % k)
    if k not in used:
        errs.append("kw key not used by any mapping: %s" % k)

# 4) ref format + focus length
seen = set()
for m in data["mappings"]:
    r = m["ref"]
    if r in seen:
        errs.append("duplicate ref: %s" % r)
    seen.add(r)
    if not re.match(r"^2021-P1B-Q\d+\([a-z0-9)(i v]+\)$", r):
        errs.append("odd ref format: %s" % r)
    if len(m["focus"]) > 40:
        errs.append("focus too long (%d): %s" % (len(m["focus"]), r))
    if not (0 <= len(m["points"]) <= 3):
        errs.append("points count %d at %s" % (len(m["points"]), r))
    for kw in m["points"]:
        pass

for k, v in data["kw"].items():
    if not (2 <= len(v) <= 8):
        errs.append("kw length %d for %s" % (len(v), k))
    for w in v:
        if len(w) < 2 or len(w) > 8:
            errs.append("kw word len %d: %r in %s" % (len(w), w, k))

# summary
qs = sorted(set(re.match(r"^2021-P1B-(Q\d+)", m["ref"]).group(1) for m in data["mappings"]),
            key=lambda s: int(s[1:]))
print("[INFO] units=%d  questions=%s  kw_points=%d  points_used=%d"
      % (len(data["mappings"]), ",".join(qs), len(data["kw"]), len(used)))
empty = [m["ref"] for m in data["mappings"] if not m["points"]]
print("[INFO] empty-points units: %s" % (", ".join(empty) if empty else "none"))

if errs:
    print("[FAIL]")
    for e in errs:
        print("  -", e)
    raise SystemExit(1)
print("[PASS] all checks")

# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"D:\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2022_p2.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = open(MAP, "rb").read()
text = raw.decode("utf-8")
errs = []
if "\ufffd" in text:
    errs.append("JSON 文件含 U+FFFD 乱码")

data = json.loads(text)
assert data["year"] == 2022, "year 错误"

cat_ids = set()
for line in io.open(CAT, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cat_ids.add(line.split("\t")[0])

maps = data["mappings"]
all_pts = set()
refs = set()
for m in maps:
    ref = m["ref"]
    if ref in refs:
        errs.append("重复 ref: " + ref)
    refs.add(ref)
    if not ref.startswith("2022-P2") or ref[7] not in "ABC":
        errs.append("ref 格式异常: " + ref)
    if len(m["focus"]) > 40:
        errs.append("focus 超40字(%d): %s" % (len(m["focus"]), ref))
    if not (1 <= len(m["points"]) <= 3):
        errs.append("points 数量越界: " + ref)
    for p in m["points"]:
        if p not in cat_ids:
            errs.append("point 不在 catalog: %s (%s)" % (p, ref))
        all_pts.add(p)

for p in data["kw"]:
    if p not in all_pts:
        errs.append("kw key 未在 mappings 出现: " + p)
    for w in data["kw"][p]:
        if not (2 <= len(w) <= 8):
            errs.append("kw 长度越界 %d: %s -> %s" % (len(w), p, w))

kw_pts = len(data["kw"])
kw_total = sum(len(v) for v in data["kw"].values())
print("单元数:", len(maps))
for sec in "ABC":
    refs_s = sorted(r for r in refs if r[7] == sec)
    print("  P2%s:" % sec, len(refs_s), "|", refs_s[0], "..", refs_s[-1])
print("kw 点数:", kw_pts, "| kw 词组:", kw_total)
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)
print("OK: json.load 通过, 无乱码, points 全部命中 catalog, kw key 合法")

# -*- coding: utf-8 -*-
import io, collections, re, sys
OUT = io.open(r"D:\deepseek-harness\default-workspace\f6chem\scratch\_q2015_scan.out.txt", "w", encoding="utf-8")
sys.stdout = OUT
p = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"
rows = []
with io.open(p, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4:
            rows.append(parts)
print("total rows:", len(rows))
c = collections.Counter(r[1] for r in rows)
print("topics:", sorted(c.items()))
kws = ["晶胞", "晶格", "液晶", "成型", "選址", "廠", "奈米", "納米", "納米", "粒子大小", "偏振", "分層", "有序", "注塑", "隔熱", "熱傳", "绝缘", "絕熱"]
for k in kws:
    hits = [r for r in rows if any(k in x for x in r[2:])]
    if hits:
        print("== %s ==" % k)
        for r in hits[:6]:
            print("   ", r[0], "|", r[2], "|", r[3])
    else:
        print("== %s == (none)" % k)

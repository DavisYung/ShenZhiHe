# -*- coding: utf-8 -*-
"""獨立驗證 links.json：重新讀檔、重新比對所有課題 JSON。"""
import json, os, sys, io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TIDS = ["1a", "1b", "1c", "2a", "2b", "3a", "3b", "4a", "4b", "6", "8"]

owner = {}   # point id -> tid
title = {}   # point id -> title
for tid in TIDS:
    with io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8") as f:
        d = json.load(f)
    for sec in d["sections"]:
        for p in sec.get("points", []):
            owner[p["id"]] = tid
            title[p["id"]] = p.get("title", "")

with io.open(os.path.join(DATA, "links.json"), encoding="utf-8") as f:
    links = json.load(f)

bad = []
edges = set()
pairs = Counter()
for i, e in enumerate(links):
    if set(e.keys()) != {"from", "to", "label"}:
        bad.append("#%d 欄位錯誤: %s" % (i, list(e.keys())))
        continue
    a, b, lab = e["from"], e["to"], e["label"]
    if a not in owner:
        bad.append("#%d from 不存在: %s" % (i, a))
    if b not in owner:
        bad.append("#%d to 不存在: %s" % (i, b))
    if (a, b) in edges:
        bad.append("#%d 重複邊: %s -> %s" % (i, a, b))
    edges.add((a, b))
    if owner.get(a) == owner.get(b):
        bad.append("#%d 同課題內部連結(本批不含): %s" % (i, a))
    if not (4 <= len(lab) <= 12):
        bad.append("#%d label %d 字: %s" % (i, len(lab), lab))
    if not any("\u4e00" <= ch <= "\u9fff" for ch in lab):
        bad.append("#%d label 非中文: %s" % (i, lab))
    pairs[tuple(sorted((owner.get(a, "?"), owner.get(b, "?"))))] += 1

for p, c in pairs.items():
    if c < 3 or c > 8:
        bad.append("課題對 %s = %d 條，超出 3-8" % (p, c))
if not (60 <= len(links) <= 90):
    bad.append("總數 %d 超出 60-90" % len(links))

print("讀入連結數: %d / 唯一邊: %d" % (len(links), len(edges)))
print("課題對數: %d" % len(pairs))
print("被引用的 point 數: %d（from %d / to %d）"
      % (len({e['from'] for e in links} | {e['to'] for e in links}),
         len({e['from'] for e in links}), len({e['to'] for e in links})))
print("課題分佈: %s" % dict(sorted(Counter(
    [owner.get(e["from"]) for e in links] + [owner.get(e["to"]) for e in links]).items())))
if bad:
    print("\n❌ 發現 %d 個問題：" % len(bad))
    for x in bad:
        print("  - " + x)
    sys.exit(1)
print("\n✅ 全部檢查通過：id 全部存在、無重複邊、每課題對 3-8 條、總數 60-90、label 4-12 字")
print("\n抽樣 8 條：")
for e in links[:4] + links[-4:]:
    print("  %-10s %-16s → %-10s %-16s [%s]"
          % (e["from"], title[e["from"]][:16], e["to"], title[e["to"]][:16], e["label"]))
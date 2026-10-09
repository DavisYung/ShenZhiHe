# -*- coding: utf-8 -*-
"""把化學區所有 fill（填充題）抽出來，寫成一份待改寫的工作檔。

不改動原始 quiz 檔，只讀。輸出 _fill_work.json：
  { "1a": [ {id, point, q, answer, explanation, options?}, ... ], ... }
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
CHEM = os.path.join(BASE, "chem")
OUT = os.path.join(BASE, "_fill_work.json")

work = {}
n = 0
for p in sorted(glob.glob(os.path.join(CHEM, "*.json"))):
    tid = os.path.basename(p)[:-5]
    data = json.load(io.open(p, encoding="utf-8"))
    items = []
    for q in data.get("questions", []):
        if q.get("type") != "fill":
            continue
        items.append({
            "id": q.get("id"),
            "point": q.get("point"),
            "q": q.get("q"),
            "answer": q.get("answer"),
            "explanation": q.get("explanation", ""),
            "options": q.get("options"),
        })
    if items:
        work[tid] = items
        n += len(items)

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(work, f, ensure_ascii=False, indent=1)

print("填充題共 %d 道，分布：" % n)
for tid in sorted(work):
    print("  %-4s %d" % (tid, len(work[tid])))
print("written:", OUT)
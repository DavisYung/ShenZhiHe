# -*- coding: utf-8 -*-
"""导出知识点目录 + 既有考频标注，供逐题映射子代理使用。

输出（f6chem/scratch/pp/）：
  catalog.tsv   每行：point_id \t 课题 \t 章节标题 \t 知识点标题 \t 标签(逗号)
  existing.json 既有 exam 标注（point_id -> {years, refs}），避免重复映射
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
OUT = os.path.join(BASE, "scratch", "pp")
DATA = os.path.join(BASE, "data", "chem")

rows = []
existing = {}
topic_names = {}
for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
    stem = os.path.basename(f)[:-5]
    if stem in ("subject", "links", "index"):
        continue
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    topic_names[stem] = t.get("title") or stem
    for s in t.get("sections") or []:
        for p in s.get("points") or []:
            rows.append((p["id"], stem, s.get("title", ""), p.get("title", ""),
                         ",".join(p.get("tags") or [])))
            e = p.get("exam")
            if e:
                existing[p["id"]] = {
                    "years": e.get("years") or [],
                    "samples": [{"y": sm.get("y"), "ref": sm.get("ref")}
                                for sm in (e.get("samples") or [])],
                }

os.makedirs(OUT, exist_ok=True)
with io.open(os.path.join(OUT, "catalog.tsv"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write("\t".join(r) + "\n")
with io.open(os.path.join(OUT, "existing.json"), "w", encoding="utf-8") as f:
    json.dump({"topic_names": topic_names, "points": existing}, f,
              ensure_ascii=False, indent=1)
print("catalog rows:", len(rows), "existing annotated:", len(existing))
print("topics:", topic_names)

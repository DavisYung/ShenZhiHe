# -*- coding: utf-8 -*-
"""预计算既有标注按年份的题号集合 → scratch/pp/existing_qnums.json。

旧 ref 风格混杂（'卷一 甲部 Q1' / '2014-P1-甲部-23' / '2021 P1 Q1' / '2020-P1-A-14'），
统一解析：去前导年份 → 去 P1/P2 标记 → 取第一个数字。
既有口径全部是卷一甲部（source 注明），所以题号即甲部 MC 题号。
"""
import glob
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
OUT = os.path.join(BASE, "scratch", "pp", "existing_qnums.json")

per_year = defaultdict(set)
bad = []
for f in glob.glob(os.path.join(BASE, "data", "chem", "*.json")):
    stem = os.path.basename(f)[:-5]
    if stem in ("subject", "links", "index"):
        continue
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    for s in t.get("sections") or []:
        for p in s.get("points") or []:
            e = p.get("exam") or {}
            for sm in e.get("samples") or []:
                y, ref = sm.get("y"), str(sm.get("ref") or "")
                s2 = re.sub(r"^20\d{2}", "", ref.strip())
                s2 = re.sub(r"[Pp]\d", "", s2)
                m = re.search(r"(\d+)", s2)
                if y is None or not m:
                    bad.append((y, ref))
                    continue
                per_year[int(y)].add(int(m.group(1)))

res = {str(y): sorted(qs) for y, qs in sorted(per_year.items())}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
for y, qs in res.items():
    print(y, "qnums:", qs)
if bad:
    print("UNPARSED:", bad)
print("written:", OUT)

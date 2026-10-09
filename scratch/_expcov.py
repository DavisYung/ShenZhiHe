# -*- coding: utf-8 -*-
"""统计既有标注按年份覆盖了哪些题号（判断卷一甲部是否已全、乙部缺多少）。"""
import glob
import io
import json
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
per_year = defaultdict(list)
for f in glob.glob(BASE + r"\data\chem\*.json"):
    stem = f.rsplit("\\", 1)[-1][:-5]
    if stem in ("subject", "links", "index"):
        continue
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    for s in t.get("sections") or []:
        for p in s.get("points") or []:
            e = p.get("exam") or {}
            for sm in e.get("samples") or []:
                y, ref = sm.get("y"), sm.get("ref", "")
                m = re.search(r"(\d+)", ref)
                per_year[y].append((int(m.group(1)) if m else None, ref))

for y in sorted(per_year):
    nums = sorted({n for n, _ in per_year[y] if n is not None})
    refs = [r for _, r in per_year[y]]
    print(y, "samples=%d" % len(refs), "qnums=%s" % nums[:60])
    # ref 风格样例
    print("   e.g.", refs[:3])

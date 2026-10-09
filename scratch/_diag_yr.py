# -*- coding: utf-8 -*-
"""检查：是否存在 years 里的年份没有对应 sample（决定 dedup 时 years 该取交集还是并集）。"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)

for label, d in (("premerge", os.path.join(HERE, "backup_data_premerge")),
                 ("current", os.path.join(BASE, "data", "chem"))):
    bad = []
    n = 0
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        stem = os.path.basename(f)[:-5]
        if stem in ("subject", "links", "index"):
            continue
        obj = json.load(io.open(f, encoding="utf-8"))
        if not isinstance(obj, dict):
            continue
        for s in obj.get("sections") or []:
            for p in s.get("points") or []:
                e = p.get("exam")
                if not e:
                    continue
                n += 1
                yrs = set(e.get("years") or [])
                syrs = {sm.get("y") for sm in (e.get("samples") or []) if sm.get("y")}
                if yrs - syrs:
                    bad.append((p["id"], sorted(yrs - syrs), sorted(syrs)))
    print("%s: exam 点 %d 个，years 有但 samples 无的 %d 个" % (label, n, len(bad)))
    for b in bad[:8]:
        print("   ", b)

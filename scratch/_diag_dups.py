# -*- coding: utf-8 -*-
"""诊断：列出同一知识点内归一化 key 重复的 sample，看清重复来源（旧档双风格 vs 新档）。"""
import glob
import io
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from merge_exam import norm_key  # noqa: E402

BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data", "chem")

n_dup_points = 0
n_dup_samples = 0
for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
    stem = os.path.basename(f)[:-5]
    if stem in ("subject", "links", "index"):
        continue
    obj = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(obj, dict):
        continue
    for s in obj.get("sections") or []:
        for p in s.get("points") or []:
            e = p.get("exam") or {}
            sms = e.get("samples") or []
            cnt = Counter(norm_key(sm.get("y"), sm.get("ref")) for sm in sms)
            bad = {k: c for k, c in cnt.items() if c > 1}
            if bad:
                n_dup_points += 1
                n_dup_samples += sum(c - 1 for c in bad.values())
                print("[%s] %s" % (p["id"], p.get("title", "")[:28]))
                for k in bad:
                    for sm in sms:
                        if norm_key(sm.get("y"), sm.get("ref")) == k:
                            print("    y=%s ref=%r focus=%r" % (sm.get("y"), sm.get("ref"), (sm.get("focus") or "")[:40]))
print("\n重复知识点数: %d，多余 sample 数: %d" % (n_dup_points, n_dup_samples))

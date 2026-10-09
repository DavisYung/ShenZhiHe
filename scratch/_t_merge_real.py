# -*- coding: utf-8 -*-
"""沙盒预演：用 scratch/map/ 里已有的真实产出跑一遍 merge + audit，不碰真 data。

复制 data/chem → scratch/_t_data_real，merge_exam 指向沙盒，跑完输出统计。
真合并时重跑本脚本确认无误后再执行真 merge_exam。
用法：python f6chem/scratch/_t_merge_real.py
"""
import glob
import io
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import merge_exam  # noqa: E402

BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data", "chem")
SANDBOX = os.path.join(HERE, "_t_data_real")
BAK = os.path.join(HERE, "_t_bak_real")

if os.path.isdir(SANDBOX):
    shutil.rmtree(SANDBOX)
os.makedirs(SANDBOX)
for f in glob.glob(os.path.join(DATA, "*.json")):
    shutil.copy2(f, SANDBOX)
if os.path.isdir(BAK):
    shutil.rmtree(BAK)

merge_exam.DATA = SANDBOX
merge_exam.BAK = BAK
# MAPD 保持默认 = scratch/map（真实产出）
sys.argv = ["merge_exam.py"]
merge_exam.main()

# 沙盒级复核：与备份对比新增量（按年/课题/等级）
import glob as _g
import json as _json
from collections import Counter

def _pts(d):
    out = {}
    for f in _g.glob(os.path.join(d, "*.json")):
        obj = _json.load(io.open(f, encoding="utf-8"))
        if not isinstance(obj, dict):
            continue
        for s in obj.get("sections") or []:
            for p in s.get("points") or []:
                out[p["id"]] = (obj.get("title") or "", p)
    return out

old = _pts(BAK)
new = _pts(SANDBOX)
add_year = Counter()
add_samp = Counter()
lv = Counter()
for pid, (ttitle, p) in new.items():
    e = p.get("exam") or {}
    oe = (old.get(pid, ("", {}))[1].get("exam")) or {}
    oy = set(oe.get("years") or [])
    for y in e.get("years") or []:
        if y not in oy:
            add_year[y] += 1
    orefs = set()
    for sm in oe.get("samples") or []:
        orefs.add((sm.get("y"), sm.get("ref")))
    for sm in e.get("samples") or []:
        if (sm.get("y"), sm.get("ref")) not in orefs:
            add_samp[sm.get("y")] += 1
    if e:
        n = len(e.get("years") or [])
        lv[3 if n >= 5 else (2 if n >= 2 else 1)] += 1

print("\n== 沙盒新增点-年（按年）==", dict(sorted(add_year.items())))
print("== 沙盒新增 sample（按年）==", dict(sorted(add_samp.items())))
print("== 沙盒 level 分布 ==", "lv3=%d lv2=%d lv1=%d" % (lv[3], lv[2], lv[1]))
print("== 有标注点总数 ==", sum(lv.values()))

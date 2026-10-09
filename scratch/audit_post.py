# -*- coding: utf-8 -*-
"""合并后审计：与 scratch/backup_exam/ 对照，输出变更统计、重复检测、抽样人查。

用法：python f6chem/scratch/audit_post.py
"""
import glob
import io
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_exam import norm_key, level_of  # noqa: E402

DATA = os.path.join(BASE, "data", "chem")
BAK = os.path.join(BASE, "scratch", "backup_exam")


def load_dir(d):
    out = {}
    for f in glob.glob(os.path.join(d, "*.json")):
        out[os.path.basename(f)] = json.load(io.open(f, encoding="utf-8"))
    return out


def points_of(objs):
    pts = {}
    for name, obj in objs.items():
        if not isinstance(obj, dict):
            continue
        for s in obj.get("sections") or []:
            for p in s.get("points") or []:
                pts[p["id"]] = (name, p, obj.get("title") or name[:-5])
    return pts


old = points_of(load_dir(BAK)) if os.path.isdir(BAK) else {}
new = points_of(load_dir(DATA))

new_years = Counter()
new_samples = Counter()
new_pts_by_topic = Counter()
dups = []
for pid, (name, p, ttitle) in new.items():
    e = p.get("exam") or {}
    oe = (old.get(pid, (None, {}, ""))[1].get("exam")) or {}
    old_years = set(oe.get("years") or [])
    for y in e.get("years") or []:
        if y not in old_years:
            new_years[y] += 1
            new_pts_by_topic[ttitle] += 0  # 占位，稍后按点计
    old_refs = {norm_key(sm.get("y"), sm.get("ref")) for sm in (oe.get("samples") or [])}
    for sm in e.get("samples") or []:
        if norm_key(sm.get("y"), sm.get("ref")) not in old_refs:
            new_samples[sm.get("y")] += 1
    # 同一点内重复：同 (year, qnum) 不同 section 或完全相同 key 出现两次
    keys = [norm_key(sm.get("y"), sm.get("ref")) for sm in (e.get("samples") or [])]
    cnt = Counter(keys)
    for k, c in cnt.items():
        if c > 1:
            dups.append((pid, k, c))
    # 同年同题号跨节（疑似同题两标）
    byq = defaultdict(set)
    for sm in (e.get("samples") or []):
        k = norm_key(sm.get("y"), sm.get("ref"))
        byq[(k[0], k[3])].add(k[2])
    for (y, q), secs in byq.items():
        if len(secs) > 1:
            dups.append((pid, ("cross-sec", y, q, sorted(secs)), 0))

print("== 新增点-年对（按年） ==")
for y in sorted(new_years):
    print("  %d: %d 個知識點新帶該年" % (y, new_years[y]))
print("== 新增 sample（按年） ==")
for y in sorted(new_samples):
    print("  %d: +%d" % (y, new_samples[y]))

lv = Counter()
topics_with = Counter()
for pid, (name, p, ttitle) in new.items():
    e = p.get("exam")
    if not e:
        continue
    lv[level_of(len(e.get("years") or []))] += 1
    topics_with[ttitle] += 1
print("== level 分布 ==", "lv3=%d lv2=%d lv1=%d" % (lv[3], lv[2], lv[1]))
print("== 帶標注的點（按課題）==", dict(topics_with))

if dups:
    print("== 疑似重複 %d 虛 ==")
    for d in dups[:20]:
        print("  ", d)
else:
    print("== 重複檢測：無 ==")

random.seed(42)
allsm = []
for pid, (name, p, ttitle) in new.items():
    e = p.get("exam") or {}
    for sm in e.get("samples") or []:
        allsm.append((pid, p.get("title"), sm))
print("== 隨機抽 8 條人查 ==")
for pid, title, sm in random.sample(allsm, min(8, len(allsm))):
    print("  [%s] %s | %s | %s | %s" % (pid, title, sm.get("y"), sm.get("ref"),
                                        (sm.get("focus") or "")[:50]))

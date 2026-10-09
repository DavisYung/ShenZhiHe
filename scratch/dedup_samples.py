# -*- coding: utf-8 -*-
"""清理同知识点内的重复 sample（归一化 key 相同），保留信息最完整的一条。

重复来源：旧数据里同一道题存在两种 ref 风格（'2020-P1-A-20' 与 '2020-p1-Q20'），
合并时被当成两条。规则：
- 同 (年,卷,节,题号,小问) 只留一条
- 保留优先级：focus 更长者 > 先出现者（旧条目通常在前）
- **years 保持不动**：实测旧数据存在「年份有、例题无」的情况（题被考过但没记具体题号），
  拿 samples 反推 years 会误删真实考频，所以只清 samples 里的重复，hits/level 按 years 重算。
用法：python f6chem/scratch/dedup_samples.py [--apply]
"""
import glob
import io
import json
import os
import shutil
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from merge_exam import norm_key, level_of, write_back  # noqa: E402

BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data", "chem")
BAK = os.path.join(HERE, "backup_dedup")

APPLY = "--apply" in sys.argv
if APPLY:
    os.makedirs(BAK, exist_ok=True)

total_removed = 0
files_changed = 0
for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
    stem = os.path.basename(f)[:-5]
    if stem in ("subject", "links", "index"):
        continue
    obj = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(obj, dict):
        continue
    changed = False
    for s in obj.get("sections") or []:
        for p in s.get("points") or []:
            e = p.get("exam")
            if not e:
                continue
            sms = e.get("samples") or []
            best = OrderedDict()
            for idx, sm in enumerate(sms):
                k = norm_key(sm.get("y"), sm.get("ref"))
                cur = best.get(k)
                if cur is None:
                    best[k] = (idx, sm)
                else:
                    # 比较：focus 更长者胜；长度相同则保留先出现者（旧条目在前）
                    old_len = len(cur[1].get("focus") or "")
                    new_len = len(sm.get("focus") or "")
                    if new_len > old_len:
                        best[k] = (idx, sm)
            if len(best) != len(sms):
                removed = len(sms) - len(best)
                total_removed += removed
                changed = True
                e["samples"] = [v[1] for v in best.values()]
                # years 不动（旧数据可能「有年份、无例题」）；hits/level 仍按 years 重算
                e["hits"] = len(e.get("years") or [])
                e["level"] = level_of(e["hits"])
                print("%s %s: -%d sample (now %d)" % (stem, p["id"], removed, len(e["samples"])))
    if changed:
        files_changed += 1
        if APPLY:
            shutil.copy2(f, os.path.join(BAK, os.path.basename(f)))
            write_back(f, obj)

print("\n%s：%d 个档、移除 %d 条重复 sample"
      % ("已写回" if APPLY else "预览（未写回，加 --apply 执行）", files_changed, total_removed))

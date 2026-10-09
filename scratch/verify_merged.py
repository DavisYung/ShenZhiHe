# -*- coding: utf-8 -*-
"""最终一致性核对：map 产出的每一个 point_id + ref 是否都进了 data/chem。

检查：把 map/*.json 里所有 (point_id, ref) 归一化后与 data 里的 sample 对比，
列出「map 有但 data 没有」的条目（= 漏合并）。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from merge_exam import norm_key  # noqa: E402

BASE = os.path.dirname(HERE)
MAPD = os.path.join(HERE, "map")
DATA = os.path.join(BASE, "data", "chem")

# 1) map 侧：point_id -> {(y, ref)}
want = {}
for f in sorted(glob.glob(os.path.join(MAPD, "*.json"))):
    d = json.load(io.open(f, encoding="utf-8"))
    y = int(d["year"])
    for m in d.get("mappings") or []:
        ref = m.get("ref", "")
        for pid in m.get("points") or []:
            want.setdefault(pid, set()).add((y, ref))

# 2) data 侧
have = {}
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
            for sm in e.get("samples") or []:
                have.setdefault(p["id"], set()).add((sm.get("y"), sm.get("ref")))

missing_total = 0
for pid, pairs in sorted(want.items()):
    hp = have.get(pid, set())
    hk = {norm_key(y, r) for (y, r) in hp}
    miss = [(y, r) for (y, r) in pairs if norm_key(y, r) not in hk]
    if miss:
        missing_total += len(miss)
        print("%s 漏 %d 条：%s" % (pid, len(miss), miss[:3]))

print("\nmap 侧涉及 %d 个知识点；漏合并条目共 %d 条" % (len(want), missing_total))
print("结果：", "全部已合并 ✅" if missing_total == 0 else "有漏 ❌")

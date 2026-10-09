# -*- coding: utf-8 -*-
"""检查合并后是否有 map 档被延迟重写（map 的 mtime 晚于 data/chem 或 hot.json），
这类档需要补合并。用法：python f6chem/scratch/check_stale_maps.py [--since <hot.json 路径>]"""
import glob
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
MAPD = os.path.join(HERE, "map")
MARK = os.path.join(BASE, "extras", "chem", "hot.json")

mark_t = os.path.getmtime(MARK)
print("基准（hot.json 重生时间）：%s" % __import__("datetime").datetime.fromtimestamp(mark_t))
stale = []
for f in sorted(glob.glob(os.path.join(MAPD, "*.json"))):
    t = os.path.getmtime(f)
    if t > mark_t:
        stale.append((os.path.basename(f), t))
if stale:
    print("\n需要补合并的 map 档：")
    for n, t in stale:
        print("  %s  (%s)" % (n, __import__("datetime").datetime.fromtimestamp(t)))
else:
    print("\n没有延迟重写的档，全部已合并 ✅")

# -*- coding: utf-8 -*-
"""诊断每年卷一 OCR 的页级结构：总页数、甲部完/乙部标记所在页、题号分布页。"""
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")

for f in sorted(glob.glob(os.path.join(PP, "*_p1.txt"))):
    name = os.path.basename(f)
    if "_p1_" in name:
        continue
    y = name[:4]
    text = io.open(f, encoding="utf-8").read()
    pages = re.split(r"=== page (\d+) ===", text)
    blocks = [(int(pages[i]), pages[i + 1]) for i in range(1, len(pages), 2)]
    jbw = [n for n, b in blocks if "甲部完" in b]
    ybw = [n for n, b in blocks if "乙部" in b]
    # 每页第一个「行首题号」样本，用于看编号走势
    first_q = []
    for n, b in blocks:
        m = None
        for ln in b.splitlines():
            mm = re.match(r"\s*(\d{1,2})\.\s", ln)
            if mm:
                m = int(mm.group(1))
                break
        first_q.append("%d:%s" % (n, m if m is not None else "-"))
    print("%s pages=%d 甲部完@%s 乙部@%s" % (y, len(blocks), jbw, ybw))
    print("   first-q per page:", " ".join(first_q))

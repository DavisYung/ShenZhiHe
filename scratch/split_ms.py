# -*- coding: utf-8 -*-
"""把参考答案 OCR 按「卷一 / 卷二」切开，减小子代理上下文压力。

切法：找含『卷二』的页，从该页起为 ms_p2；找不到的年份（OCR 稀疏）整份给两边。
输出：pp/<年>_ms_p1.txt、pp/<年>_ms_p2.txt
用法：python f6chem/scratch/split_ms.py
"""
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")

for f in sorted(glob.glob(os.path.join(PP, "*_ms.txt"))):
    y = os.path.basename(f)[:4]
    text = io.open(f, encoding="utf-8").read()
    pages = re.split(r"=== page (\d+) ===", text)
    # pages[0] 空串，之后 (页码, 内容) 成对
    blocks = [(int(pages[i]), pages[i + 1]) for i in range(1, len(pages), 2)]
    cut = None
    for idx, (n, body) in enumerate(blocks):
        if "卷二" in body:
            cut = idx
            break
    if cut is None:
        p1 = p2 = text
        note = "no-marker(整份给两边)"
    else:
        p1 = "\n".join("=== page %d ===%s" % b for b in blocks[:cut])
        p2 = "\n".join("=== page %d ===%s" % b for b in blocks[cut:])
        note = "cut at page %d" % blocks[cut][0]
    io.open(os.path.join(PP, "%s_ms_p1.txt" % y), "w", encoding="utf-8").write(p1)
    io.open(os.path.join(PP, "%s_ms_p2.txt" % y), "w", encoding="utf-8").write(p2)
    print("%s: %s | p1=%dB p2=%dB" % (y, note, len(p1), len(p2)))
print("done")

# -*- coding: utf-8 -*-
"""把卷一 OCR 按「甲部选择 / 乙部长题」切开。

切法：甲部 = 到最后一个含『甲部完』的页为止；乙部 = 从最后一个含『乙部』且在甲部完之后的页开始，
兜底从甲部完下一页开始。输出 pp/<年>_p1_mc.txt、pp/<年>_p1_b.txt。
用法：python f6chem/scratch/split_p1.py
"""
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
    if "_ms_" in name:
        continue                      # 参考答案切片不参与本切分
    y = name[:4]
    text = io.open(f, encoding="utf-8").read()
    pages = re.split(r"=== page (\d+) ===", text)
    blocks = [(int(pages[i]), pages[i + 1]) for i in range(1, len(pages), 2)]
    # 甲部 = 到最后一个含『甲部完』的页（页1 是考生须知里的引用，真标记在 MC 末页）
    mc_end = max((i for i, (n, b) in enumerate(blocks) if "甲部完" in b), default=0)
    # 乙部 = 紧接其后的页开始（不能用『乙部』字样定位——页眉会反复出现，实测会切丢正文）
    b_start = min(mc_end + 1, len(blocks) - 1)
    mc = "\n".join("=== page %d ===%s" % b for b in blocks[:mc_end + 1])
    bb = "\n".join("=== page %d ===%s" % b for b in blocks[b_start:])
    io.open(os.path.join(PP, "%s_p1_mc.txt" % y), "w", encoding="utf-8").write(mc)
    io.open(os.path.join(PP, "%s_p1_b.txt" % y), "w", encoding="utf-8").write(bb)
    print("%s: mc=%dB(%dp) b=%dB(%dp)" % (y, len(mc), mc_end + 1,
                                          len(bb), len(blocks) - b_start))
print("done")

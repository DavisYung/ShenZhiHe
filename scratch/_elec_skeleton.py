# -*- coding: utf-8 -*-
"""把电学工作纸抽取文本压成「骨架」：每页只保留含中文的行，滤掉散落的符号行。

输出 scratch/elec_extract/elec_skeleton.txt，供逐课精读与「工作纸↔答案」对齐。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elec_extract")
CJK = re.compile(r"[\u4e00-\u9fff]")
SKIP = re.compile(r"^(新高中生活與物理|課堂工作紙|牛津大學出版社|\d+$)")

src = os.path.join(BASE, "Book_4_Electric_notes.txt")
lines = io.open(src, encoding="utf-8").read().split("\n")

out = []
page = 0
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    m = re.match(r"<<<PAGE (\d+)>>>", s)
    if m:
        page = int(m.group(1))
        out.append("")
        out.append("##### PAGE %d #####" % page)
        continue
    if not s:
        continue
    if SKIP.match(s):
        continue
    if not CJK.search(s):
        continue
    out.append("  %s" % s)

dst = os.path.join(BASE, "elec_skeleton.txt")
with io.open(dst, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("骨架已写出: %s" % dst)
print("原 %d 行 → 骨架 %d 行" % (len(lines), len(out)))

# -*- coding: utf-8 -*-
"""为电学两份 PDF 的抽取文本建立「页码 → 行号」索引，方便按课分段精读。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elec_extract")

for fn in ["Book_4_Electric_notes.txt", "ws_4_ans_ce.txt"]:
    p = os.path.join(BASE, fn)
    lines = io.open(p, encoding="utf-8").read().split("\n")
    print("=" * 60)
    print(fn, " 共", len(lines), "行")
    print("=" * 60)
    # 每行输出：页码 起始行 结束行
    marks = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"<<<PAGE (\d+)>>>", ln.strip())
        if m:
            marks.append((int(m.group(1)), i))
    for k, (pg, start) in enumerate(marks):
        end = marks[k + 1][1] - 1 if k + 1 < len(marks) else len(lines)
        print("p%02d  L%d-L%d" % (pg, start, end))

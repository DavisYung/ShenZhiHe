# -*- coding: utf-8 -*-
import io, os, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\核物理学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuclear_extract")
os.makedirs(OUT, exist_ok=True)

FILES = [
    (r"Book 5 notes.pdf", "nuclear"),
    (r"Atomic note's solution.pdf", "nuclear_ans"),
]

HEAD_LESSON = re.compile(r"^第\s*\d+\s*課")
HEAD_SEC = re.compile(r"^\d+\.\d+\s+\S")
HEAD_SUB = re.compile(r"^[A-D]\s+\S")
HEAD_EVAL = re.compile(r"^進度評估\s*\d+")
CJK = re.compile(r"[\u4e00-\u9fff]")


def headings(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or len(s) > 46:
            continue
        if HEAD_LESSON.match(s) or HEAD_SEC.match(s) or HEAD_SUB.match(s) or HEAD_EVAL.match(s):
            if CJK.search(s):
                out.append(s)
    return out


for name, tag in FILES:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失:", p)
        continue
    doc = pymupdf.open(p)
    print("=" * 60)
    print(name, "共", doc.page_count, "页")
    print("=" * 60)
    lines = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        hs = headings(t)
        nimg = len(page.get_images(full=True))
        lines.append("p%02d | 字%4d | %s" % (i + 1, len(t), " / ".join(hs[:4])))
    doc.close()
    out = os.path.join(OUT, "nuclear_pagemap.txt")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("页面分析已写出:", out)
    print()
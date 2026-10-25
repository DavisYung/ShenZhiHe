# -*- coding: utf-8 -*-
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

src = r"D:\物理相关\核物理学"
for name in [r"Book 5 notes.pdf", r"Atomic note's solution.pdf"]:
    p = os.path.join(src, name)
    if not os.path.exists(p):
        print("缺失:", p)
        continue
    doc = pymupdf.open(p)
    print(name, "共", doc.page_count, "页")
    doc.close()
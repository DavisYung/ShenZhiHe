# -*- coding: utf-8 -*-
"""把物理 PDF 指定页渲染成图片，检查版式、公式、图的呈现质量。

产出到 f6chem/scratch/phys_preview/，供人工核对后再决定转录策略。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phys_preview")
os.makedirs(OUT, exist_ok=True)

# 每份文件取若干代表性页：首页、含公式页、含图页
JOBS = [
    ("Heat notes.pdf", [1, 2, 3, 9, 13, 20, 29, 38], "heat"),
    ("Gases note.pdf", [1, 2, 5, 12, 20, 28], "gas"),
    ("Book 1 Heat Notes solution.pdf", [1, 2, 6, 12], "sol"),
]

made = []
for name, pages, tag in JOBS:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失 %s" % p)
        continue
    doc = pymupdf.open(p)
    for pno in pages:
        if pno < 1 or pno > doc.page_count:
            continue
        page = doc[pno - 1]
        # 2 倍分辨率，足够看清公式下标
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        op = os.path.join(OUT, "%s_p%02d.png" % (tag, pno))
        pix.save(op)
        made.append((op, pix.width, pix.height, os.path.getsize(op)))
    doc.close()

print("已渲染 %d 张预览图到 %s\n" % (len(made), OUT))
for op, w, h, sz in made:
    print("  %-26s %4dx%-5d %7.1f KB" % (os.path.basename(op), w, h, sz / 1024.0))

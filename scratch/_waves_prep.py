# -*- coding: utf-8 -*-
"""波動學頁面分析與頁圖渲染（與熱學/力學管線同參數）。

輸出：
  scratch/waves_pagemap.txt
  site/img/phys_wav_pNN.webp（工作紙 85 頁；答案本不渲染）
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf
from PIL import Image

SRC = r"D:\物理相关\波动学"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")
os.makedirs(IMGDIR, exist_ok=True)

SCALE = 1.6
QUALITY = 80
FILES = [("ws_3A3B notes.pdf", "wav")]   # 僅工作紙；答案只提供文字

HEAD_LESSON = re.compile(r"^第\s*\d+\s*課")
HEAD_SEC = re.compile(r"^\d+\.\d+\s+\S")
HEAD_SUB = re.compile(r"^[A-D]\s+\S")
CJK = re.compile(r"[\u4e00-\u9fff]")


def headings(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or len(s) > 46:
            continue
        if (HEAD_LESSON.match(s) or HEAD_SEC.match(s) or HEAD_SUB.match(s)) and CJK.search(s):
            out.append(s)
    return out


lines = []
n_webp = 0
total = 0

for name, tag in FILES:
    p = os.path.join(SRC, name)
    doc = pymupdf.open(p)
    lines.append("=" * 78)
    lines.append("%s   (%d 頁, tag=%s)" % (name, doc.page_count, tag))
    lines.append("=" * 78)
    for i, page in enumerate(doc):
        t = page.get_text("text")
        hs = headings(t)
        nimg = len(page.get_images(full=True))
        ndraw = len(page.get_drawings())

        pix = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        op = os.path.join(IMGDIR, "phys_%s_p%02d.webp" % (tag, i + 1))
        im.save(op, "WEBP", quality=QUALITY, method=6)
        sz = os.path.getsize(op)
        total += sz
        n_webp += 1

        flags = []
        if nimg:
            flags.append("圖%d" % nimg)
        if ndraw > 12:
            flags.append("矢量%d" % ndraw)
        lines.append("p%02d | 字%4d %-16s | %s"
                     % (i + 1, len(t), " ".join(flags), " / ".join(hs[:4])))
    doc.close()

out = os.path.join(SCRATCH, "waves_pagemap.txt")
with io.open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("頁面分析: %s" % out)
print("渲染頁圖 %d 張，合計 %.2f MB" % (n_webp, total / 1024.0 / 1024.0))

# -*- coding: utf-8 -*-
"""力學內容生產：頁面分析與頁圖渲染（套用熱學管線）。

輸出：
  scratch/mech_pagemap.txt       每頁結構（章節標題/字數/圖數）
  site/img/phys_mecha_pNN.webp   第 1–7 課工作紙頁圖
  site/img/phys_mechb_pNN.webp   第 8–10 課工作紙頁圖

渲染參數與熱學一致：scale 1.6（A4→953×1348）、WebP quality 80。
答案本不渲染頁圖（轉錄時直接讀提取文字）。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf
from PIL import Image

SRC = r"D:\物理相关\力学"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")
os.makedirs(IMGDIR, exist_ok=True)

SCALE = 1.6
QUALITY = 80

FILES = [
    ("ws_book 2 mechanic notes version 2.pdf", "mecha"),   # 第 1–7 課
    ("ws_book 2 mechanic notes 2.pdf", "mechb"),           # 第 8–10 課
]

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
total_webp = 0

for name, tag in FILES:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失 %s" % p)
        continue
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
        total_webp += sz
        n_webp += 1

        flags = []
        if nimg:
            flags.append("圖%d" % nimg)
        if ndraw > 12:
            flags.append("矢量%d" % ndraw)
        lines.append("p%02d | 字%4d %-16s | %s"
                     % (i + 1, len(t), " ".join(flags), " / ".join(hs[:4])))
    doc.close()
    lines.append("")

out = os.path.join(SCRATCH, "mech_pagemap.txt")
with io.open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("頁面分析已寫出: %s" % out)
print("渲染頁圖 %d 張，合計 %.2f MB" % (n_webp, total_webp / 1024.0 / 1024.0))

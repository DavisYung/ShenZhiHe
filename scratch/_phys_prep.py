# -*- coding: utf-8 -*-
"""物理内容生产：第 1 步「页面分析与页图渲染」。

产出：
  1. f6chem/scratch/phys_pagemap.txt  —— 每页的结构信息（标题/字数/图数/矢量图数/DSE标记）
  2. f6chem/site/img/phys_*.webp      —— 渲染好的页图，供知识点内嵌

同时打印化学既有图片的规格，作为物理渲染质量的对照基准。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf
from PIL import Image

SRC = r"D:\物理相关"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")
os.makedirs(IMGDIR, exist_ok=True)

SCALE = 1.6          # 渲染倍率：A4 → 约 952x1346，公式下标可辨且体积可控
QUALITY = 80

FILES = [
    ("Heat notes.pdf", "heat"),
    ("Gases note.pdf", "gas"),
    ("Book 1 Heat Notes solution.pdf", "sol"),
]

HEAD_LESSON = re.compile(r"^第\s*\d+\s*課")
HEAD_SEC = re.compile(r"^\d+\.\d+\s+\S")
HEAD_SUB = re.compile(r"^[A-D]\s+\S")
HEAD_EVAL = re.compile(r"^進度評估\s*\d+")
DSE = re.compile(r"(20\d\d)\s*(?:L\.Q\.|P\.\d|Paper|卷一|卷二|Q\d)")
CJK = re.compile(r"[\u4e00-\u9fff]")


def headings(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or len(s) > 46:
            continue
        if HEAD_LESSON.match(s) or HEAD_SEC.match(s) or HEAD_SUB.match(s) or HEAD_EVAL.match(s):
            # 必須含中文，且不是算式（算式沒有中文）
            if CJK.search(s):
                out.append(s)
    return out


lines = []
total_webp = 0
n_webp = 0

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
        dse = sorted(set(DSE.findall(t)))

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
        if dse:
            flags.append("DSE:" + ",".join(dse))
        lines.append("p%02d | 字%4d %-16s | %s"
                     % (i + 1, len(t), " ".join(flags), " / ".join(hs[:4])))
    doc.close()
    lines.append("")

out = os.path.join(SCRATCH, "phys_pagemap.txt")
with io.open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("頁面分析已寫出: %s" % out)
print("渲染頁圖 %d 張，合計 %.2f MB" % (n_webp, total_webp / 1024.0 / 1024.0))

# 化學圖片規格對照
chem = [f for f in os.listdir(IMGDIR) if f.endswith(".webp") and not f.startswith("phys_")]
if chem:
    sizes = [(os.path.getsize(os.path.join(IMGDIR, f)), f) for f in chem]
    sizes.sort()
    print("\n=== 化學既有圖片規格（對照基準）===")
    print("  數量: %d  合計 %.2f MB  平均 %.1f KB"
          % (len(chem), sum(s for s, _ in sizes) / 1024.0 / 1024.0,
             sum(s for s, _ in sizes) / len(chem) / 1024.0))
    for s, f in (sizes[0], sizes[len(sizes) // 2], sizes[-1]):
        im = Image.open(os.path.join(IMGDIR, f))
        print("  %-30s %sx%s  %6.1f KB" % (f, im.size[0], im.size[1], s / 1024.0))

# 物理圖片規格
phys = [(os.path.getsize(os.path.join(IMGDIR, f)), f)
        for f in os.listdir(IMGDIR) if f.startswith("phys_")]
phys.sort()
print("\n=== 物理新渲染圖片 ===")
print("  數量: %d  合計 %.2f MB  平均 %.1f KB"
      % (len(phys), sum(s for s, _ in phys) / 1024.0 / 1024.0,
         sum(s for s, _ in phys) / len(phys) / 1024.0))
for s, f in (phys[0], phys[len(phys) // 2], phys[-1]):
    im = Image.open(os.path.join(IMGDIR, f))
    print("  %-30s %sx%s  %6.1f KB" % (f, im.size[0], im.size[1], s / 1024.0))

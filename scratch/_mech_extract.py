# -*- coding: utf-8 -*-
"""力学 PDF 第一步：提取文字，判断材料性质与结构。

输出到 scratch/mech_extract/，为后续课题划分做依据。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\力学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mech_extract")
os.makedirs(OUT, exist_ok=True)

FILES = [
    "ws_book 2 mechanic notes version 2.pdf",
    "ws_book 2 mechanic notes 2.pdf",
    "ws_2_ans_ce.pdf",
]

HEAD_LESSON = re.compile(r"^\d+\.\d+\s+[^\d\s]")
HEAD_CH = re.compile(r"^(第\s*\d+\s*課|[Cc]hapter\s*\d+)", re.I)
HEAD_SUB = re.compile(r"^[A-D]\s+\S")
CJK = re.compile(r"[\u4e00-\u9fff]")

for name in FILES:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失: %s" % p)
        continue
    doc = pymupdf.open(p)
    n = doc.page_count
    print("=" * 74)
    print("%s   %d 頁" % (name, n))
    print("=" * 74)

    all_text = []
    info = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        all_text.append("\n<<<PAGE %d>>>\n" % (i + 1) + t)
        # 页级信息
        hs = [ln.strip() for ln in t.split("\n")
              if ln.strip() and len(ln.strip()) < 46
              and (HEAD_LESSON.match(ln.strip()) or HEAD_CH.match(ln.strip())
                   or HEAD_SUB.match(ln.strip())) and CJK.search(ln.strip())]
        nimg = len(page.get_images(full=True))
        flags = []
        if nimg:
            flags.append("圖%d" % nimg)
        info.append("  p%02d | 字%4d %-12s | %s"
                    % (i + 1, len(t), " ".join(flags), " / ".join(hs[:4])))
    doc.close()

    # 打印页级信息（紧凑）
    for line in info[:60]:
        print(line)
    if len(info) > 60:
        print("  ... (共 %d 頁)" % len(info))

    txt = "".join(all_text)
    stem = os.path.splitext(name)[0].replace(" ", "_")
    op = os.path.join(OUT, stem + ".txt")
    with io.open(op, "w", encoding="utf-8") as f:
        f.write(txt)
    # 粗统计
    n_cjk = len(CJK.findall(txt))
    n_blank = txt.count("____")
    print("  → 已写出 %s  |  中文 %d 字  |  填空 %d 处  |  乱码 %d"
          % (op, n_cjk, n_blank, txt.count("\ufffd")))
    print()

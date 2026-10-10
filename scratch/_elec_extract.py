# -*- coding: utf-8 -*-
"""提取电学 PDF 的文字与结构信息，输出到 scratch/elec_extract/ 供分析。

注意：中文内容一律走文件读写，不经管道，避免 U+FFFD 乱码。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\电学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elec_extract")
os.makedirs(OUT, exist_ok=True)

FILES = [
    "Book 4 Electric notes.pdf",
    "ws_4_ans_ce.pdf",
]

for name in FILES:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失: %s" % p)
        continue
    doc = pymupdf.open(p)
    n_pages = doc.page_count
    print("=" * 70)
    print("%s   共 %d 页" % (name, n_pages))
    print("=" * 70)

    all_text = []
    img_pages = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        all_text.append("\n<<<PAGE %d>>>\n" % (i + 1) + t)
        imgs = page.get_images(full=True)
        if imgs:
            img_pages.append((i + 1, len(imgs)))
        if i < 3:
            print("--- p%d 文字预览 ---" % (i + 1))
            print(t[:600])
    doc.close()

    txt = "".join(all_text)
    stem = os.path.splitext(name)[0].replace(" ", "_")
    op = os.path.join(OUT, stem + ".txt")
    with io.open(op, "w", encoding="utf-8") as f:
        f.write(txt)

    n_chars = len(txt)
    n_cjk = len([c for c in txt if '\u4e00' <= c <= '\u9fff'])
    n_fffd = txt.count("\ufffd")
    print()
    print("  文字 %d 字符（中文约 %d 字）" % (n_chars, n_cjk))
    print("  乱码 U+FFFD: %d" % n_fffd)
    print("  含图页数: %d / %d" % (len(img_pages), n_pages))
    print("  已写出: %s" % op)
    print()
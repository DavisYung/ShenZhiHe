# -*- coding: utf-8 -*-
"""波動學三份 PDF 提取：工作紙 + 两份答案本，输出到 scratch/waves_extract/。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\波动学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waves_extract")
os.makedirs(OUT, exist_ok=True)

FILES = ["ws_3A3B notes.pdf", "ws_3A_ans_ce.pdf", "ws_3B_ans_ce.pdf"]
CJK = re.compile(r"[\u4e00-\u9fff]")

for name in FILES:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("缺失: %s" % p)
        continue
    doc = pymupdf.open(p)
    n = doc.page_count
    all_text = []
    heads_by_page = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        all_text.append("\n<<<PAGE %d>>>\n" % (i + 1) + t)
        hs = [ln.strip() for ln in t.split("\n") if ln.strip() and len(ln.strip()) < 50
              and (re.match(r"^\d+\.\d+\s*\S", ln.strip()) or re.match(r"^第\s*\d+\s*課", ln.strip())
                   or re.match(r"^[A-D]\s+\S", ln.strip())) and CJK.search(ln.strip())]
        heads_by_page.append((i + 1, len(t), len(page.get_images(full=True)), hs[:3]))
    doc.close()

    txt = "".join(all_text)
    stem = os.path.splitext(name)[0].replace(" ", "_")
    op = os.path.join(OUT, stem + ".txt")
    with io.open(op, "w", encoding="utf-8") as f:
        f.write(txt)

    print("=" * 74)
    print("%s   %d 頁  → %s" % (name, n, op))
    print("=" * 74)
    # 答案本：打印每页的課題标题（验证覆盖范围）
    if "ans" in name:
        for pg, ln, ni, hs in heads_by_page:
            if hs:
                print("  p%02d | 字%4d | %s" % (pg, ln, " / ".join(hs)))
    else:
        # 工作纸：紧凑打印全部页
        for pg, ln, ni, hs in heads_by_page:
            print("  p%02d | 字%4d %-6s | %s" % (pg, ln, ("圖%d" % ni) if ni else "", " / ".join(hs)))
    print("  中文 %d 字 | 填空 %d | 乱码 %d\n" % (len(CJK.findall(txt)), txt.count("____"), txt.count("\ufffd")))

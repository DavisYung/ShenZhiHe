# -*- coding: utf-8 -*-
import io, os, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\核物理学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuclear_content")
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
    all_text = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        all_text.append("\n<<<PAGE %d>>>\n" % (i + 1) + t)
    doc.close()
    txt = "".join(all_text)
    stem = os.path.splitext(name)[0].replace(" ", "_")
    op = os.path.join(OUT, stem + ".txt")
    with io.open(op, "w", encoding="utf-8") as f:
        f.write(txt)
    n_cjk = len([c for c in txt if '\u4e00' <= c <= '\u9fff'])
    n_fffd = txt.count("\ufffd")
    print("  文字 %d 字符（中文约 %d 字）" % (len(txt), n_cjk))
    print("  乱码 U+FFFD: %d" % n_fffd)
    print("  已写出:", op)
    print()
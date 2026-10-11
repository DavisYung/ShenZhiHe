# -*- coding: utf-8 -*-
"""抽取 E2 两份 PDF 的文字层，按工作纸页码切分成每课一份材料。

产出（f6chem/atomic_src/）：
  notes_p01.txt ... notes_p39.txt   工作纸逐页文字
  ans_p01.txt   ... ans_p07.txt     答案本逐页文字
  course1.txt / course2.txt / course3.txt   按课合并（含逐页标记）
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

import pymupdf

SRC = r"C:\dsh_pdfrender"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "atomic_src")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)


def extract(pdf_path, prefix):
    doc = pymupdf.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, 1):
        # "text" 保留阅读顺序；用 sort=True 按位置重排
        t = page.get_text("text", sort=True)
        pages.append(t)
        with io.open(os.path.join(OUT, f"{prefix}_p{i:02d}.txt"), "w", encoding="utf-8") as f:
            f.write(t)
    doc.close()
    return pages


print("抽取工作纸 notes ...")
notes = extract(os.path.join(SRC, "e2_notes.pdf"), "notes")
print(f"  {len(notes)} 页")

print("抽取答案本 ans ...")
ans = extract(os.path.join(SRC, "e2_ans.pdf"), "ans")
print(f"  {len(ans)} 页")

# 按课合并：notes 页序 = 工作纸页码 1..39
# 第1课 p.1-14；第2课 p.15-26；第3课 p.27-39（由答案本标注推得）
COURSES = [
    ("course1", "第1課 邁向現代原子模型 I", 1, 14),
    ("course2", "第2課 邁向現代原子模型 II", 15, 26),
    ("course3", "第3課 納米材料", 27, 39),
]

for name, title, lo, hi in COURSES:
    buf = [f"# {title}\n", f"（工作紙第 {lo}–{hi} 頁）\n"]
    for p in range(lo, hi + 1):
        if p <= len(notes):
            buf.append(f"\n===== 工作紙 p{p} =====\n")
            buf.append(notes[p - 1])
    txt = "".join(buf)
    with io.open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"  {name}.txt  {len(txt)} 字元  含 p{lo}-p{hi}")

# 答案本全文（答案按小节标了工作纸页码，不分课切）
full = []
for i, t in enumerate(ans, 1):
    full.append(f"\n===== 答案本 p{i} =====\n")
    full.append(t)
with io.open(os.path.join(OUT, "ans_all.txt"), "w", encoding="utf-8") as f:
    f.write("".join(full))
print(f"  ans_all.txt  {len(''.join(full))} 字元")

# 检查是否有缺字/乱码
bad = 0
for root, _d, files in os.walk(OUT):
    for n in files:
        with io.open(os.path.join(root, n), encoding="utf-8") as f:
            c = f.read()
        if "\ufffd" in c:
            print(f"  [WARN] {n} 含 U+FFFD 乱码")
            bad += 1
print(f"乱码检查: {bad} 个文件有问题" if bad else "乱码检查: 全部干净")
print(f"\n输出目录: {OUT}")

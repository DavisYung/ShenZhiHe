# -*- coding: utf-8 -*-
import io, os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\核物理学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuclear")
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
os.makedirs(os.path.join(OUT, "quiz"), exist_ok=True)

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


def dump(path, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("寫出", path)


# ============================ nuclear1 辐射与物质 ============================
notes = pymupdf.open(os.path.join(SRC, r"Book 5 notes.pdf"))
anns = pymupdf.open(os.path.join(SRC, r"Atomic note's solution.pdf"))

topic = {
    "id": "nuclear1",
    "title": "輻射與物質",
    "pdf": "Book 5 notes.pdf",
    "sections": [
        {
            "id": "nuclear1-s1",
            "title": "輻射與電離",
            "points": [
                {
                    "id": "nuclear1-s1-p1",
                    "title": "輻射與電離",
                    "page": 1,
                    "tags": ["輻射", "電離"],
                    "body": "**輻射**是某放射源以**粒子**或**______________**的形式放射的______________，並且可以經介質或**______________**傳播開去。**電子**在**高電壓**下**移動**，金屬絲與**正極**連接，加熱後便放射出**X 射線**。X 射線管 重金屬(+) 電子 金屬絲(-) X 射線",
                }
            ]
        }
    ]
}
quiz = {"topic": "nuclear1", "questions": []}

dump(os.path.join(OUT, "data", "nuclear1.json"), topic)
dump(os.path.join(OUT, "quiz", "nuclear1.json"), quiz)

n_pages = sum(pymupdf.open(os.path.join(SRC, f[0])).page_count for f in FILES)
print("nuclear1：1章、%d點" % (1,))
print("完成")
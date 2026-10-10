# -*- coding: utf-8 -*-
import io, os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

SRC = r"D:\物理相关\核物理学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuclear")
dump = lambda path, obj: io.open(path, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")

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

notes = pymupdf.open(os.path.join(SRC, r"Book 5 notes.pdf"))
anns = pymupdf.open(os.path.join(SRC, r"Atomic note's solution.pdf"))

# nuclear3: 核反應與應用
topic = {
 "id": "nuclear3",
 "title": "核反應與應用",
 "pdf": "Book 5 notes.pdf",
 "sections": [
  {
   "id": "nuclear3-s1",
   "title": "核分裂",
   "points": [
    {
     "id": "nuclear3-s1-p1",
     "title": "核分裂概念",
     "page": 6,
     "tags": ["核分裂", "中子", "分裂產物"],
     "body": "當一個重核在吸收**中子**後變得不穩定，分裂成兩個較輕的核子，釋放出額外的**中子**和大量能量。此過程稱為**核分裂**。\n\n核分裂的關鍵特徵：\n- 釋放2-3個額外中子\n- 產生大量熱能\n- 生成的產物是中等質量的核素"
    }
   ]
  },
  {
   "id": "nuclear3-s2",
   "title": "核聚變",
   "points": [
    {
     "id": "nuclear3-s2-p1",
     "title": "核聚變概念",
     "page": 7,
     "tags": ["核聚變", "氫", "質子", "能量"],
     "body": "兩個輕核在極高溫度和高壓下結合成一個較重的核子，釋放能量。此過程稱為**核聚變**。\n\n核聚變的關鍵條件：\n- 極高溫（數千萬度）使粒子有足夠動能\n- 高壓 confining 粒子\n- 適當的**同位素**（如氫的氘、氚）\n\n能量來源：太陽和星體能量來源"
    }
   ]
  }
 ]
}

quiz = {"topic": "nuclear3", "questions": []}

OUT_DATA = os.path.join(OUT, "data")
OUT_QUIZ = os.path.join(OUT, "quiz")
os.makedirs(OUT_DATA, exist_ok=True)
os.makedirs(OUT_QUIZ, exist_ok=True)

dump(os.path.join(OUT_DATA, "nuclear3.json"), topic)
dump(os.path.join(OUT_QUIZ, "nuclear3.json"), quiz)
print("nuclear3完成：2章")
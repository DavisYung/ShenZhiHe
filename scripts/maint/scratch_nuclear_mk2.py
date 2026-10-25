# -*- coding: utf-8 -*-
import io, os, re, sys, json

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

def dump(path, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

SRC = r"D:\物理相关\核物理学"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuclear")
anns_sol = pymupdf.open(os.path.join(SRC, r"Atomic note's solution.pdf"))

topic = {
 "id": "nuclear2",
 "title": "核素與放射衰變",
 "pdf": "Book 5 notes.pdf",
 "sections": [
  {
   "id": "nuclear2-s1",
   "title": "核素",
   "points": [
    {
     "id": "nuclear2-s1-p1",
     "title": "核素的組成",
     "page": 3,
     "tags": ["核素", "質子", "中子"],
     "body": "核素是由**質子**和**中子**組成的。質子帶正電，中子帶**無電** charge。原子序數 Z 等於質子數，質量數 A 等於質子數加中子數。同位素是指**同樣**的原子序數卻有不同質量數的核素。"
    },
    {
     "id": "nuclear2-s1-p2",
     "title": "放射衰變",
     "page": 3,
     "tags": ["放射衰變", "α", "β", "γ"],
     "body": "原子核不穩定時，會經過**放射衰變**釋放能量。三種常見的衰變方式：\n- **α輻射**：失去2個質子和2個中子，質量數減4，原子序數減2\n- **β輻射**：中子轉變為質子，發出β粒子（高速電子），原子序數增加1\n- **γ輻射**：發出高能量γ射線，質量數和原子序數不變"
    }
   ]
  }
 ]
}

quiz = {"topic": "nuclear2", "questions": []}

OUT_DATA = os.path.join(OUT, "data")
OUT_QUIZ = os.path.join(OUT, "quiz")
dump(os.path.join(OUT_DATA, "nuclear2.json"), topic)
dump(os.path.join(OUT_QUIZ, "nuclear2.json"), quiz)
print("nuclear2完成：1章")
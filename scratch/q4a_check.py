# -*- coding: utf-8 -*-
"""檢查 f6chem/quiz/4a.json 與 f6chem/data/4a.json 現況。"""
import json, os, sys, io, re

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(ROOT, "data", "4a.json")
QUIZ = os.path.join(ROOT, "quiz", "4a.json")

# ---- 1. data ----
with io.open(DATA, encoding="utf-8") as f:
    data = json.load(f)
points = []
print("sections:", len(data["sections"]))
for s in data["sections"]:
    print("  %s %s -> %d points" % (s["id"], s["title"], len(s["points"])))
    for p in s["points"]:
        points.append(p["id"])
print("total points:", len(points))

# ---- 2. quiz ----
raw = open(QUIZ, "rb").read()
print("quiz bytes:", len(raw))
try:
    txt = raw.decode("utf-8")
    print("utf-8 decode: OK")
except Exception as e:
    print("utf-8 decode FAIL:", e)
    txt = raw.decode("utf-8", errors="replace")

bad = [(i + 1, l) for i, l in enumerate(txt.splitlines()) if "\ufffd" in l]
print("lines with U+FFFD:", len(bad))
for n, l in bad:
    print("   L%d: %s" % (n, l.strip()))

try:
    quiz = json.loads(txt)
    print("json.load: OK")
except Exception as e:
    print("json.load FAIL:", e)
    sys.exit(0)

qs = quiz.get("questions", [])
print("top-level keys:", list(quiz.keys()))
print("question count:", len(qs))
ids = [q.get("id") for q in qs]
print("ids:", ids)
exp = ["4a-q%d" % i for i in range(1, len(ids) + 1)]
print("ids continuous:", ids == exp)
print("dup ids:", len(ids) != len(set(ids)))
from collections import Counter
print("type counts:", Counter(q.get("type") for q in qs))
print("types:", [q.get("type") for q in qs])
bad_pt = [(q.get("id"), q.get("point")) for q in qs if q.get("point") not in points]
print("unknown points:", bad_pt)
for q in qs:
    for ch in q.get("q", "") + str(q.get("options", "")) + str(q.get("explanation", "")):
        if ch == "\ufffd":
            print("FFFD in", q["id"])

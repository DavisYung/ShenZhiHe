# -*- coding: utf-8 -*-
"""驗證填充題轉選擇題後的資料品質。

檢查項：
  1. 所有題目只剩 mc / tf，沒有 fill 殘留
  2. 每道 mc 恰好 4 個選項、answer 是 0-3 的整數、選項互不重複
  3. 題幹裡不該再有連續兩個空（多空題會造成歧義）
  4. explanation 非空
  5. point 欄位指向存在的知識點（若提供 data 則交叉檢查）
  6. 掃描 U+FFFD 亂碼
"""
import glob
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
CHEM = os.path.join(BASE, "chem")
ROOT = os.path.dirname(BASE)
DATA = os.path.join(ROOT, "data", "chem")

# 收集所有知識點 id
points = set()
for p in glob.glob(os.path.join(DATA, "*.json")):
    if os.path.basename(p) in ("links.json",):
        continue
    try:
        t = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        continue
    for s in t.get("sections", []) or []:
        for pt in s.get("points", []) or []:
            points.add(pt.get("id"))

types = Counter()
problems = []
blank_multi = []
n_q = 0

for path in sorted(glob.glob(os.path.join(CHEM, "*.json"))):
    tid = os.path.basename(path)[:-5]
    data = json.load(io.open(path, encoding="utf-8"))
    for q in data.get("questions", []):
        n_q += 1
        qid = q.get("id")
        t = q.get("type")
        types[t] += 1

        if t == "fill":
            problems.append((qid, "仍是 fill 類型"))
            continue
        if t == "tf":
            if not isinstance(q.get("answer"), bool):
                problems.append((qid, "tf 的 answer 不是布林值"))
            continue
        if t != "mc":
            problems.append((qid, "未知題型 %r" % t))
            continue

        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4:
            problems.append((qid, "選項數不是 4（%s）" % (len(opts) if isinstance(opts, list) else "非陣列")))
            continue
        if any(not str(o).strip() for o in opts):
            problems.append((qid, "有空選項"))
        if len(set(opts)) != 4:
            problems.append((qid, "選項重複：%s" % opts))
        ans = q.get("answer")
        if not isinstance(ans, int) or not (0 <= ans <= 3):
            problems.append((qid, "answer 不是 0-3 的整數：%r" % ans))
        if not str(q.get("explanation") or "").strip():
            problems.append((qid, "沒有解析"))
        if q.get("point") and points and q["point"] not in points:
            problems.append((qid, "point %s 不存在" % q["point"]))

        # 題幹連續空
        text = str(q.get("q") or "")
        if len(re.findall(r"_{2,}", text)) >= 2:
            blank_multi.append(qid)
        if "\ufffd" in text or "\ufffd" in str(q.get("explanation") or ""):
            problems.append((qid, "含 U+FFFD 亂碼"))

print("總題數：%d" % n_q)
print("題型分布：%s" % dict(types))
print()
if blank_multi:
    print("題幹仍有 2 個以上空格的題目（%d）：" % len(blank_multi))
    for qid in blank_multi:
        print("  " + qid)
    print()
if problems:
    print("!! 發現 %d 個問題：" % len(problems))
    for qid, msg in problems[:60]:
        print("  %-10s %s" % (qid, msg))
else:
    print("資料檢查全部通過 ✅")
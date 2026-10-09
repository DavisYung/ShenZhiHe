# -*- coding: utf-8 -*-
"""統計與覆蓋檢查（含最終驗證）"""
import json, os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
base = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
out = os.path.join(base, "quiz", "3a.json")
data = json.load(open(out, encoding="utf-8"))
src = json.load(open(os.path.join(base, "data", "3a.json"), encoding="utf-8"))

real_points = {p["id"]: p["title"] for s in src["sections"] for p in s["points"]}
real_secs = {s["id"]: s["title"] for s in src["sections"]}
Q = data["questions"]

print("topic:", data.get("topic"), "| total:", len(Q))
types = collections.Counter(q["type"] for q in Q)
print("types:", dict(types), {k: f"{v/len(Q)*100:.0f}%" for k, v in types.items()})

errs = []
if data.get("topic") != "3a": errs.append("topic 錯")

# id 連續
for i, q in enumerate(Q, 1):
    if q["id"] != f"3a-q{i}": errs.append(f"id 不連續: {q['id']} (應為 3a-q{i})")

for q in Q:
    t = q["type"]
    if q.get("point") not in real_points:
        errs.append(f"{q['id']} point 不存在: {q.get('point')}")
    if t == "mc":
        o = q.get("options")
        if not (isinstance(o, list) and len(o) == 4): errs.append(f"{q['id']} 選項數≠4")
        if not isinstance(q.get("answer"), int) or not (0 <= q["answer"] <= 3):
            errs.append(f"{q['id']} answer 索引錯: {q.get('answer')}")
    elif t == "tf":
        if not isinstance(q.get("answer"), bool): errs.append(f"{q['id']} answer 非布林")
    elif t == "fill":
        a = q.get("answer")
        if not (isinstance(a, str) or (isinstance(a, list) and a and all(isinstance(x, str) for x in a))):
            errs.append(f"{q['id']} fill answer 型別錯")
        if "____" not in q.get("q", ""): errs.append(f"{q['id']} fill 題幹缺 ____")
    else:
        errs.append(f"{q['id']} 未知 type: {t}")
    if not q.get("explanation") or len(q["explanation"]) < 10:
        errs.append(f"{q['id']} explanation 過短/缺")

# mc 答案分佈（避免全同一位置）
mc = [q["answer"] for q in Q if q["type"] == "mc"]
print("mc answer 分佈:", dict(collections.Counter(mc)))

# tf 約一半 false
tf = [q["answer"] for q in Q if q["type"] == "tf"]
print("tf false 比例:", f"{sum(1 for x in tf if x is False)}/{len(tf)}")

# section 覆蓋
sec_count = collections.Counter(q["point"].rsplit("-p", 1)[0] for q in Q)
miss = [s for s in real_secs if sec_count.get(s, 0) < 2]
print("每 section 題數:")
for s in real_secs:
    print(f"  {s} {real_secs[s]}: {sec_count.get(s,0)}")
if miss: errs.append(f"section 少於 2 題: {miss}")

print("\nERRORS:", len(errs))
for e in errs: print("  !", e)
print("RESULT:", "PASS" if not errs else "FAIL")
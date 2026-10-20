# -*- coding: utf-8 -*-
"""檢查數學分區知識點是否符合 mdLite 語法與資料規範。"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALC = os.path.join(BASE, "data", "math", "calc.json")
SUBJ = os.path.join(BASE, "data", "math", "subject.json")

IMG_RE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)\s]+)\)\s*$")

with io.open(CALC, encoding="utf-8") as f:
    d = json.load(f)
with io.open(SUBJ, encoding="utf-8") as f:
    subj = json.load(f)

problems = []
warns = []

# ---- subject ↔ topic 一致性 ----
if d["id"] not in subj.get("topics", []):
    problems.append("subject.json 的 topics 沒有列出 %s" % d["id"])

pid_set = set()
n_pts = 0
for sec in d["sections"]:
    if not re.match(r"^[a-z0-9]+-s\d+$", sec["id"]):
        problems.append("章節 id 格式不對：%s" % sec["id"])
    for p in sec["points"]:
        n_pts += 1
        pid = p["id"]
        if pid in pid_set:
            problems.append("知識點 id 重複：%s" % pid)
        pid_set.add(pid)
        if not re.match(r"^calc-s\d+-p\d+$", pid):
            problems.append("知識點 id 格式不對：%s" % pid)
        if not pid.startswith(sec["id"] + "-"):
            problems.append("%s 不屬於章節 %s" % (pid, sec["id"]))
        body = p.get("body", "")
        if not body.strip():
            problems.append("%s 正文為空" % pid)
        if "\ufffd" in body:
            problems.append("%s 正文有亂碼 U+FFFD" % pid)
        if "![自製圖解]" in body and not re.search(r"!\[自製圖解[^\]]*\]\(", body):
            problems.append("%s 有孤立的自製圖解標記" % pid)
        # 围栏配对
        if body.count("```") % 2 != 0:
            problems.append("%s 代碼圍欄 ``` 不配對（%d 個）" % (pid, body.count("```")))
        # 图片行必须整行合法
        for ln in body.split("\n"):
            s = ln.strip()
            if s.startswith("![") and not IMG_RE.match(ln):
                problems.append("%s 圖片行語法不合法：%s" % (pid, s[:50]))
        # 表格行首尾管線
        in_code = False
        for ln in body.split("\n"):
            if ln.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if "|" in ln and ln.strip().startswith("|") and not ln.strip().endswith("|"):
                warns.append("%s 表格行未以 | 結尾：%s" % (pid, ln[:40]))
        # 標題層級
        if re.search(r"^#{1,2}\s", body, re.M):
            warns.append("%s 使用了 # 或 ## 標題（mdLite 會轉粗體）" % pid)

# ---- 練習章節完整性（每個練習 section 內：第 1 點＝題目、第 2 點＝答案） ----
practice = [s for s in d["sections"] if "練習" in s["title"]]
for sec in practice:
    pts = sec["points"]
    if len(pts) != 2:
        problems.append("%s 應該有「題目＋答案」兩個知識點，實際 %d 個"
                        % (sec["id"], len(pts)))
        continue
    q, a = pts
    if "答案" not in a["title"]:
        problems.append("%s 的第 2 個知識點標題應含「答案」，實際是「%s」"
                        % (sec["id"], a["title"]))
    if "答案" in q["title"]:
        problems.append("%s 的第 1 個知識點標題不應含「答案」" % sec["id"])
    qnums = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", q["body"], re.M)]
    anums = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", a["body"], re.M)]
    if qnums != anums:
        problems.append("%s 題號 %s 與答案題號 %s 不一致"
                        % (sec["id"], qnums, anums))

print("章節 %d　知識點 %d　練習章節 %d" % (len(d["sections"]), n_pts, len(practice)))
if problems:
    print("\n問題 %d 項：" % len(problems))
    for p in problems:
        print("  FAIL", p)
if warns:
    print("\n提示 %d 項：" % len(warns))
    for w in warns[:15]:
        print("  WARN", w)

ok = not problems
print("\n結果：%s" % ("全部通過" if ok else "有 %d 項問題" % len(problems)))
sys.exit(0 if ok else 1)

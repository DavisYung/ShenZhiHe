# -*- coding: utf-8 -*-
"""4a 測驗題庫完整驗證：json.load、無 \\ufffd、id 連續、point 真實存在、
每 section ≥2 題、選項/答案格式、mc60/tf20/fill20 比例、tf 約半 false。"""
import io, json, os, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(ROOT, "data", "4a.json")
QUIZ = os.path.join(ROOT, "quiz", "4a.json")

fails = []

# ---------- 1. data ----------
with io.open(DATA, encoding="utf-8") as f:
    data = json.load(f)
points, sec_of_point, sec_title = [], {}, {}
for s in data["sections"]:
    sec_of_point[s["id"]] = s["title"]
    for p in s["points"]:
        points.append(p["id"])
        sec_of_point[p["id"]] = s["id"]
print("data: sections=%d points=%d" % (len(data["sections"]), len(points)))

# ---------- 2. quiz raw 掃描 ----------
raw = open(QUIZ, "rb").read()
try:
    txt = raw.decode("utf-8")
    print("utf-8 decode: OK")
except Exception as e:
    fails.append("utf-8 decode FAIL: %s" % e)
    txt = raw.decode("utf-8", errors="replace")
n_fffd = txt.count("\ufffd")
print("U+FFFD count: %d" % n_fffd)
if n_fffd:
    fails.append("發現 %d 個 U+FFFD 替換字元" % n_fffd)
    for i, l in enumerate(txt.splitlines(), 1):
        if "\ufffd" in l:
            print("   L%d: %s" % (i, l.strip()))

# ---------- 3. json.load ----------
try:
    quiz = json.loads(txt)
    print("json.load: OK")
except Exception as e:
    fails.append("json.load FAIL: %s" % e)
    sys.exit(1)

if quiz.get("topic") != "4a":
    fails.append("topic 欄位應為 '4a'，實為 %r" % quiz.get("topic"))
qs = quiz.get("questions")
if not isinstance(qs, list):
    fails.append("questions 不是陣列")
    sys.exit(1)

# ---------- 4. 題數 / id 連續 ----------
n = len(qs)
print("question count: %d" % n)
if not (25 <= n <= 30):
    fails.append("題數 %d 超出 25-30 範圍" % n)
ids = [q.get("id") for q in qs]
exp = ["4a-q%d" % i for i in range(1, n + 1)]
if ids != exp:
    fails.append("id 不連續或次序錯：%s" % ids)
if len(ids) != len(set(ids)):
    fails.append("id 有重複")
print("id 連續且無重複: %s" % (ids == exp))

# ---------- 5. 每題欄位與格式 ----------
REQ = {"id", "type", "point", "q", "answer", "explanation"}
per_sec = defaultdict(int)
per_sec_type = defaultdict(Counter)
for q in qs:
    qid = q.get("id", "?")
    missing = REQ - set(q)
    if missing:
        fails.append("%s 缺欄位 %s" % (qid, sorted(missing)))
    t = q.get("type")
    if t not in ("mc", "tf", "fill"):
        fails.append("%s type 非法: %r" % (qid, t))
    if not q.get("explanation", "").strip():
        fails.append("%s explanation 為空" % qid)
    # point 必須真實存在
    pt = q.get("point")
    if pt not in points:
        fails.append("%s point 不存在於 data: %r" % (qid, pt))
        continue
    per_sec[sec_of_point[pt]] += 1
    per_sec_type[sec_of_point[pt]][t] += 1

    ans = q.get("answer")
    if t == "mc":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4:
            fails.append("%s 必須有 4 個選項，實為 %s" % (qid, len(opts) if isinstance(opts, list) else opts))
        elif len(set(opts)) != 4:
            fails.append("%s 選項有重複" % qid)
        if not isinstance(ans, int) or isinstance(ans, bool):
            fails.append("%s answer 非整數索引: %r" % (qid, ans))
        elif isinstance(opts, list) and not (0 <= ans < len(opts)):
            fails.append("%s answer 越界: %r" % (qid, ans))
    elif t == "tf":
        if not isinstance(ans, bool):
            fails.append("%s answer 非布林: %r" % (qid, ans))
    elif t == "fill":
        if "____" not in q.get("q", ""):
            fails.append("%s 題幹缺少 ____" % qid)
        if isinstance(ans, str):
            ans_list = [ans]
        elif isinstance(ans, list) and ans and all(isinstance(a, str) and a.strip() for a in ans):
            ans_list = ans
        else:
            fails.append("%s fill answer 應為非空字串或字串陣列: %r" % (qid, ans))
            ans_list = []

# ---------- 6. 每 section ≥2 ----------
print("\n每 section 題數：")
for s in data["sections"]:
    c = per_sec.get(s["id"], 0)
    ct = dict(per_sec_type.get(s["id"], {}))
    mark = "OK " if c >= 2 else "不足"
    print("  %s %-4s %-22s %d 題 %s  %s" % (mark, s["id"], s["title"][:20], c, ct, "" if c >= 2 else "<<<"))
    if c < 2:
        fails.append("%s (%s) 只有 %d 題，少於 2" % (s["id"], s["title"], c))

# ---------- 7. 比例 mc60/tf20/fill20 ----------
tc = Counter(q.get("type") for q in qs)
tot = n
print("\n題型比例：")
for k in ("mc", "tf", "fill"):
    c = tc.get(k, 0)
    print("  %-4s %2d 題  %.0f%% (目標 60/20/20)" % (k, c, 100.0 * c / tot))
target = {"mc": 0.60, "tf": 0.20, "fill": 0.20}
for k, want in target.items():
    got = tc.get(k, 0) / tot
    if abs(got - want) > 0.02:
        fails.append("%s 比例 %.0f%% 偏離目標 %.0f%%" % (k, 100 * got, 100 * want))

# ---------- 8. tf 約一半 false ----------
tfq = [q for q in qs if q.get("type") == "tf"]
nf = sum(1 for q in tfq if q.get("answer") is False)
nt = sum(1 for q in tfq if q.get("answer") is True)
print("\ntf 題 %d：True %d / False %d" % (len(tfq), nt, nf))
if len(tfq) and not (0.3 <= nf / len(tfq) <= 0.7):
    fails.append("tf 的 false 比例 %d/%d 未接近一半" % (nf, len(tfq)))

# ---------- 9. 題幹/選項不得引用「（原頁不清）」 ----------
for q in qs:
    blob = q.get("q", "") + " " + " ".join(q.get("options", []) or [])
    if "不清" in blob:
        fails.append("%s 引用了『（原頁不清）』內容" % q["id"])

# ---------- 10. 化學式完整性抽查 ----------
import re
suspects = []
for q in qs:
    blob = " ".join([q.get("q", ""), " ".join(q.get("options", []) or []), q.get("explanation", "")])
    # 常見損壞式：元素符號後接異常數字/雜訊，例如 NaCO3(少數字)、CaCO33
    for m in re.finditer(r"\b([A-Z][a-z]?)(\d{0,4})", blob):
        sym, num = m.group(1), m.group(2)
        if sym in ("Ca", "Na", "Mn", "Zn", "H", "C", "O", "N", "S", "Cl") and num and len(num) > 2:
            suspects.append((q["id"], m.group(0)))
if suspects:
    for s in suspects:
        print("  可疑化學式 %s: %s" % s)
    fails.append("發現可疑化學式 %d 處" % len(suspects))

# ---------- 11. 重複題目 ----------
seen = {}
for q in qs:
    k = q.get("q", "").strip()
    if k in seen:
        fails.append("題目重複：%s 與 %s" % (seen[k], q["id"]))
    seen[k] = q["id"]

# ---------- 結果 ----------
print("\n" + "=" * 60)
if fails:
    print("驗證未通過，共 %d 項：" % len(fails))
    for f in fails:
        print("  [FAIL]", f)
    sys.exit(1)
print("驗證全部通過 ✅")
print("總題數 %d（mc %d / tf %d / fill %d），section %d 個各 ≥2 題，無亂碼。"
      % (n, tc.get("mc", 0), tc.get("tf", 0), tc.get("fill", 0), len(per_sec)))

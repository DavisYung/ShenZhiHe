# -*- coding: utf-8 -*-
"""把化學區所有填充題（fill）轉成選擇題（mc）。

作法：
  1. 從 _fill_mc_*.py 讀入四個課題群組的改寫資料（id -> 題幹/正解/誘答/解析）
  2. 對每個 quiz/chem/*.json 裡的 fill 題，改寫成 mc：
     - type: fill -> mc
     - options: 正解 + 三個誘答，依題號決定性打亂（不固定放 A，避免答案規律）
     - answer: 正解的索引（數字）
     - 移除 fill 專用的 answer 陣列（改由 answer 索引取代）
  3. 有缺漏或對不上的題目一律報錯，不靜默跳過

可重複執行：已經轉成 mc 的題目會直接跳過。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
CHEM = os.path.join(BASE, "chem")
sys.path.insert(0, BASE)

from _fill_mc_1a_1b import MAP as M1  # noqa: E402
from _fill_mc_1c_2a import MAP as M2  # noqa: E402
from _fill_mc_2b_3a import MAP as M3  # noqa: E402
from _fill_mc_3b_to_8 import MAP as M4  # noqa: E402

MAP = {}
for m in (M1, M2, M3, M4):
    dup = set(MAP) & set(m)
    if dup:
        sys.exit("改寫資料有重複 id：%s" % sorted(dup))
    MAP.update(m)

print("改寫資料共 %d 道" % len(MAP))


# 每筆資料的欄位數可能是 4（無指定位置）或 5（指定位置），統一成 4 欄
NORM = {}
for k, v in MAP.items():
    if len(v) == 5:
        NORM[k] = (v[0], v[1], v[2], v[4])
    elif len(v) == 4:
        NORM[k] = v
    else:
        sys.exit("資料格式錯誤：%s 有 %d 欄" % (k, len(v)))
MAP = NORM


def pick_pos(qid):
    """依題號決定正解位置（0-3），確保四個位置都會出現。"""
    return sum(ord(c) for c in qid) % 4


def to_mc(qid, q):
    title, correct, wrongs, expl = MAP[qid]
    if len(wrongs) != 3:
        sys.exit("%s 的誘答不是 3 個" % qid)
    if correct in wrongs:
        sys.exit("%s 的正解與誘答重複" % qid)
    pos = pick_pos(qid)
    opts = list(wrongs)
    opts.insert(pos, correct)
    return {
        "id": q["id"],
        "type": "mc",
        "point": q.get("point"),
        "q": title,
        "options": opts,
        "answer": pos,
        "explanation": expl,
    }


total = 0
converted = 0
missing = []
pos_count = {0: 0, 1: 0, 2: 0, 3: 0}

for path in sorted(glob.glob(os.path.join(CHEM, "*.json"))):
    tid = os.path.basename(path)[:-5]
    data = json.load(io.open(path, encoding="utf-8"))
    qs = data.get("questions", [])
    out = []
    changed = 0
    for q in qs:
        total += 1
        if q.get("type") != "fill":
            out.append(q)
            continue
        qid = q.get("id")
        if qid not in MAP:
            missing.append(qid)
            out.append(q)
            continue
        mq = to_mc(qid, q)
        pos_count[mq["answer"]] += 1
        out.append(mq)
        changed += 1
        converted += 1
    if changed:
        data["questions"] = out
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("  %-4s 轉換 %d 道" % (tid, changed))

print()
print("總題數 %d，轉換 %d 道填充題 -> 選擇題" % (total, converted))
print("正解位置分布：A=%d B=%d C=%d D=%d" % (
    pos_count[0], pos_count[1], pos_count[2], pos_count[3]))
if missing:
    print("!! 缺漏 %d 道：%s" % (len(missing), missing))
else:
    print("沒有缺漏")

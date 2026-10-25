# -*- coding: utf-8 -*-
"""收尾 v2：刪減至 35 題、tf 加入 false 敘述、mc 答案均勻分佈
嚴格保護：只旋轉「explanation 內每一個 A-D 字母都是選項引用」的題目；
只要存在任何化學符號中的字母（C=C、CO、黑煙(C) 等），一律不旋轉。"""
import json, os, re
base = r"D:\deepseek-harness\default-workspace\f6chem"
out = os.path.join(base, "quiz", "3a.json")
data = json.load(open(out, encoding="utf-8"))
Q = data["questions"]
assert len(Q) == 40, len(Q)
by_id = {q["id"]: q for q in Q}
LETTERS = "ABCD"

# ---------- 1) 三題 tf 改為 false 敘述 ----------
by_id["3a-q2"].update({
 "q": "石油中的烴只分為烷和環烷兩類，並不包括芳香族烴。",
 "answer": False,
 "explanation": "錯誤。石油中的烴分為脂肪族烴（烷與環烷）及芳香族烴三類。芳香族烴的特徵是含有苯環，例如苯（C₆H₆，交替單雙鍵的六元環）和甲基苯（苯環接 CH₃）；烷是開鏈飽和烴（直鏈如丁烷、支鏈如 2-甲基丁烷）；環烷是碳環飽和烴（如環戊烷，五元環）。"})

by_id["3a-q16"].update({
 "q": "聚合作用只是把單體分子原封不動地拼在一起，聚合物與單體的原子成分完全相同，且沒有小分子產生。",
 "answer": False,
 "explanation": "錯誤。這只適用於加成聚合：單體必定含 C=C，聚合物與單體的原子成分相同，且沒有細小分子產生（原子經濟率 100%）。縮合聚合則要求單體具兩個或以上官能基，過程中有小分子（如 H₂O、HCl、NH₃）產生，故聚合物的原子組成與單體不同。此外，由於重複次數 n 無法控制，聚合物是不同長度聚合物分子的混合物，並無單一固定的相對分子質量。"})

by_id["3a-q32"].update({
 "q": "實驗室製備乙酸乙酯時，乙酸乙酯形成的油層在下層，因為其密度大於水。",
 "answer": False,
 "explanation": "錯誤。乙酸乙酯的密度小於水，故形成的油層在上層，並散發芳香氣味；下層是乙酸、乙醇、水及稀硫酸的混合液，可用分液漏斗分開兩層。實驗用暖水浴加熱，是因乙酸乙酯與乙醇均易燃且沸點低。"})

# ---------- 2) q30 fill 答案收斂 ----------
by_id["3a-q30"]["answer"] = ["CH₃CH₂OH"]
by_id["3a-q30"]["explanation"] = ("烷醇可視為烷烴的一個 H 被羥基（-OH）取代，通式 CₙH₂ₙ₊₁OH。n = 2 時為 C₂H₅OH，"
 "以簡明結構式寫作 CH₃CH₂OH（C₂H₅OH 是同一物質的另一種簡寫）。寫結構式時不可把 -OH 拆成 O 和 H 分開畫，"
 "氧原子須同時連接碳和氫。注意：工業酒精含雜質有毒，不可飲用；消毒藥水則是 75% 乙醇。")

# ---------- 3) 刪減 5 題 → 35 ----------
DROP = {"3a-q11", "3a-q13", "3a-q19", "3a-q29", "3a-q24"}
Q = [q for q in Q if q["id"] not in DROP]
assert len(Q) == 35, len(Q)

# ---------- 4) 嚴格保護下的 mc 答案均勻化 ----------
# RUN：形如 "B 錯" / "A、C 錯" / "A、D 錯" / "C、D 錯"
RUN = re.compile(r'[ABCD](?:[、，,]\s*[ABCD])*\s*錯')
# BARE：任何獨立的 A-D 字母（可能出現在化學式內）
NEIGH = r"A-Za-z0-9\u2080-\u2089\u4e00-\u9fff"
BARE = re.compile(r'(?<![%s])[ABCD](?![%s])' % (NEIGH, NEIGH))

targets = [1, 0, 2, 1, 3, 0, 2, 1, 0, 3, 2, 1, 0, 3, 1, 2, 0, 1, 3, 2, 0]
mcs = [q for q in Q if q["type"] == "mc"]
assert len(mcs) == len(targets), (len(mcs), len(targets))

rotated, skipped = [], []
for q, tgt in zip(mcs, targets):
    old = q["answer"]
    if old == tgt:
        continue
    exp = q["explanation"]
    # 移除所有「選項引用 run」後，若仍殘留任何 A-D 字母 → 該題不安全
    leftover = BARE.sub("", RUN.sub(" ", exp))
    if BARE.search(leftover):
        skipped.append((q["id"], old, tgt, BARE.findall(leftover)))
        continue
    shift = (tgt - old) % 4
    q["options"] = q["options"][-shift:] + q["options"][:-shift]
    def rot(m):
        run = m.group(0)
        letters = re.findall(r'[ABCD]', run)
        out = []
        for ch in run:
            out.append(LETTERS[(LETTERS.index(ch) + shift) % 4] if ch in LETTERS else ch)
        return "".join(out)
    q["explanation"] = RUN.sub(rot, exp)
    q["answer"] = tgt
    rotated.append((q["id"], old, tgt, shift))

# ---------- 5) 重編 id ----------
for i, q in enumerate(Q, 1):
    q["id"] = "3a-q%d" % i

with open(out, "w", encoding="utf-8") as f:
    json.dump({"topic": "3a", "questions": Q}, f, ensure_ascii=False, indent=1)

print("total:", len(Q), "| rotated:", len(rotated))
print("skipped:", skipped)
# 驗證：不得改動化學式字母
bad = [q["id"] for q in Q if "B=B" in json.dumps(q, ensure_ascii=False)]
print("B=B 殘留:", bad)
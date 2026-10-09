# -*- coding: utf-8 -*-
"""Fix 2b-s13 to satisfy the 3-6 points-per-section rule.

The section was written by this same run (batch B), so correcting it does
not touch any pre-existing content. Content is split, never dropped:
p1 構造 / p2 兩極半反應 / p3 整體反應與電子流向 (was p2).
"""
import json, os, sys

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)

SID = "2b-s13"
SPLIT = {
    "id": "2b-s13-p3",
    "title": "整體反應與電子流向",
    "body": "**整體反應：Mg(s) + Cu²⁺(aq) → Mg²⁺(aq) + Cu(s)**。\n電子由**負電極（Mg，陽極）經外電路流向正電極（Cu，陰極）**；鹽橋中的 K⁺ 與 NO₃⁻ 分別移向陰極室與陽極室，維持兩邊電中性，令電流可持續流通。",
    "page": 26,
    "tags": ["化學電池", "整體反應", "電子流向"],
}

with open(DATA, "r", encoding="utf-8") as f:
    doc = json.load(f)

sec = next(s for s in doc["sections"] if s["id"] == SID)
before = len(sec["points"])
if any(p["id"] == "2b-s13-p3" for p in sec["points"]):
    print("[fix] already applied")
    raise SystemExit(0)

# rewrite p1 to cover construction only; p2 becomes the two half-reactions
sec["points"][0]["title"] = "簡單化學電池的構造"
sec["points"][0]["body"] = (
    "最基本的化學電池，由**兩片不同金屬**浸在各自的金屬離子溶液中，以**鹽橋"
    "（內含 KNO₃ 凝膠）**連接：\n"
    "- **負電極（陽極）**：Mg 片浸於 MgSO₄(aq)\n"
    "- **正電極（陰極）**：Cu 片浸於 CuSO₄(aq)\n"
    "鹽橋令兩半電池的溶液保持電中性，是 Type 1 電池的關鍵部件。"
)

sec["points"][1] = {
    "id": "2b-s13-p2",
    "title": "兩極的半反應：氧化與還原",
    "body": "- **負電極／陽極（氧化作用）**：Mg(s) → Mg²⁺(aq) + 2e⁻（Mg 失電子，被氧化）\n"
    "- **正電極／陰極（還原作用）**：Cu²⁺(aq) + 2e⁻ → Cu(s)（Cu²⁺ 得電子，被還原，銅片表面析出紅色銅）\n"
    "⚠️ 對照本課題 s2：Mg 與 Cu 的半反應、整體反應與電池符號在此以化學電池形式呈現。",
    "page": 26,
    "tags": ["化學電池", "半反應", "氧化", "還原"],
}

# insert the split-off point after p2
sec["points"].insert(2, SPLIT)
assert len(sec["points"]) == before + 1 == 3, len(sec["points"])

tmp = DATA + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
os.replace(tmp, DATA)

with open(DATA, "r", encoding="utf-8") as f:
    json.load(f)
print("[fix] %s points %d->%d | json ok" % (SID, before, len(sec["points"])))
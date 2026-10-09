# -*- coding: utf-8 -*-
"""Top up 2b-s20 and 2b-s21 to the 3-6 point rule (final two violations).

Content is taken from the source pages already transcribed in this run
(p038: 離子分析與包裹電線的作用; p039: 溶液最終變成稀硫酸), not invented.
"""
import json, os

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)

TOPUPS = [
    (
        "2b-s20",
        {
            "id": "2b-s20-p3",
            "title": "先分析溶液中的離子",
            "body": "與其他電解例題相同，**第一步先列出濃 NaCl(aq) 中的離子：Na⁺、Cl⁻、H⁺、OH⁻**。\n"
            "- **陽極**候選：Cl⁻ 與 OH⁻（陰離子，被氧化）\n"
            "- **陰極**候選：Na⁺ 與 H⁺（陽離子，被還原）\n"
            "⚠️ 由於兩極都用**特製電極**（碳陽極、汞陰極），電極物料本身成為決定產物的關鍵因素——"
            "這正是「三大因素」的**③ 電極物料**。",
            "page": 38,
            "tags": ["電解NaCl", "離子分析", "電極物料"],
        },
        1,
    ),
    (
        "2b-s21",
        {
            "id": "2b-s21-p3",
            "title": "溶液變化的判讀",
            "body": "⚠️ 教師指出：電解過程中**Cu²⁺ 與 OH⁻ 在兩極同時被消耗**（Cu²⁺ 於陰極析出、"
            "OH⁻ 於陽極放電），淨效果是水被分解。\n"
            "因此溶液的**藍色（Cu²⁺）逐漸變淡直至褪去**，而 SO₄²⁻ 無被消耗、H⁺ 在陰極優先於 Na⁺（此處無 Na⁺）留下，"
            "最終溶液**變成稀硫酸 H₂SO₄**。",
            "page": 39,
            "tags": ["電解CuSO₄", "溶液變化", "H₂SO₄"],
        },
        2,
    ),
]


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        doc = json.load(f)
    changed = 0
    for sid, point, idx in TOPUPS:
        sec = next(s for s in doc["sections"] if s["id"] == sid)
        if any(p["id"] == point["id"] for p in sec["points"]):
            print("[fix] %s %s already present, skip" % (sid, point["id"]))
            continue
        sec["points"].insert(idx, point)
        assert 3 <= len(sec["points"]) <= 6, (sid, len(sec["points"]))
        changed += 1
        print("[fix] %s: %s inserted -> %d points"
              % (sid, point["id"], len(sec["points"])))
    if not changed:
        print("[fix] nothing to do")
        return
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, DATA)
    with open(DATA, "r", encoding="utf-8") as f:
        json.load(f)
    print("[fix] %d section(s) updated | json ok" % changed)


main()
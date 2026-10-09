# -*- coding: utf-8 -*-
"""Top up 2b-s19 (and any other new section) to the 3-6 point rule.

Content is drawn from the source pages already transcribed into this run
(the 離子分析 step and the 兩個情況的對比), never invented.
"""
import json, os, sys

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)

# (section_id, new_point) — inserted at index 1 unless specified
TOPUPS = [
    (
        "2b-s19",
        {
            "id": "2b-s19-p3",
            "title": "兩個情況的對比：濃度決定陽極產物",
            "body": "同樣是碳電極電解 NaCl(aq)，**陽極產物完全由 Cl⁻ 與 OH⁻ 的濃度差決定**：\n"
            "- **極稀 NaCl(aq)**：OH⁻ 濃度相對較高 → **OH⁻ 放電 → O₂(g)**（等同電解水）\n"
            "- **濃 NaCl(aq)**：Cl⁻ 濃度高很多 → **Cl⁻ 放電 → Cl₂(g)**\n"
            "**陰極不變**：兩者都是 H⁺ 優先放電生成 H₂(g)（H⁺ 位置較 Na⁺ 低）。\n"
            "⚠️ 這正是「三大因素」中**濃度凌駕電化序位置**的典型例子。",
            "page": 37,
            "tags": ["電解NaCl", "濃度", "對比", "Cl₂"],
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
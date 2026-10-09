# -*- coding: utf-8 -*-
"""Batch D: pages 36-39 (electrolysis case studies: NaCl dilute/conc, Hg cathode, CuSO4)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import append_helper as H

BATCH = [
    {
        "id": "2b-s19",
        "title": "電解氯化鈉溶液的兩個情況",
        "points": [
            {
                "id": "2b-s19-p1",
                "title": "電解極稀 NaCl(aq)：只產生 H₂ 與 O₂",
                "body": "用**碳電極**電解**極稀** NaCl(aq)，溶液中離子為 **Na⁺、Cl⁻、H⁺、OH⁻**。經過一段時間後：\n- **陽極：OH⁻ 優先放電，生成 O₂** —— **4OH⁻(aq) → O₂(g) + 2H₂O(l) + 4e⁻**。⚠️ 因 OH⁻ 在電化序的位置較 Cl⁻ 高，所以 OH⁻ 優先放電。\n- **陰極：H⁺ 優先放電，生成 H₂** —— **2H⁺(aq) + 2e⁻ → H₂(g)**。因 H⁺ 在電化序的位置較 Na⁺ 低，所以 H⁺ 優先放電。\n- **整體反應：2H₂O(l) → 2H₂(g) + O₂(g)**（等同電解水）",
                "page": 36,
                "tags": ["電解NaCl", "極稀", "OH⁻", "H⁺"],
            },
            {
                "id": "2b-s19-p2",
                "title": "電解濃 NaCl(aq)：Cl⁻ 濃度高而優先放電",
                "body": "用**碳電極**電解**稀／濃** NaCl(aq)，經過一段時間後：\n- **陽極：2Cl⁻(aq) → Cl₂(g) + 2e⁻**。⚠️ 雖然 OH⁻ 在電化序的位置較 Cl⁻ 高，但**濃 NaCl 中 Cl⁻ 濃度比 OH⁻ 高很多，所以 Cl⁻ 優先放電，生成 Cl₂**（濃度因素凌駕電化序）。\n- **陰極：2H⁺(aq) + 2e⁻ → H₂(g)**。H⁺ 位置較 Na⁺ 低，故 H⁺ 優先放電。\n- **整體反應：2Cl⁻(aq) + 2H⁺(aq) → Cl₂(g) + H₂(g)**",
                "page": 37,
                "tags": ["電解NaCl", "濃", "Cl₂", "濃度"],
            },
        ],
    },
    {
        "id": "2b-s20",
        "title": "電解濃 NaCl(aq)：碳陽極 + 汞陰極（製鈉）",
        "points": [
            {
                "id": "2b-s20-p1",
                "title": "特製電極的構造",
                "body": "電解**濃 NaCl(aq)** 時使用**碳陽極**與**汞（Hg）陰極**，陰極以**塑膠包裹的電線**並覆上 **H₂O 以防止 Hg 揮發**。溶液中離子為 **Na⁺、Cl⁻、H⁺、OH⁻**。",
                "page": 38,
                "tags": ["電解NaCl", "汞陰極", "塑膠包裹"],
            },
            {
                "id": "2b-s20-p2",
                "title": "兩極半反應：生成鈉汞齊",
                "body": "- **陽極：2Cl⁻(aq) → Cl₂(g) + 2e⁻**\n- **陰極：Na⁺ 與 H⁺ 競爭放電，Na⁺ 得電子生成鈉汞齊（Na/Hg）**：**Na⁺(aq) + e⁻ → Na/Hg**。⚠️ 由於 Na⁺ 在電化序的位置較 H⁺ 低，本應放出 H₂，但汞陰極（高氫過電位）令 H⁺ 難以還原，改由 **Na⁺ 還原溶入汞中形成鈉汞齊**。\n- **汞陰極副反應：2Na/Hg(aq) + 2H₂O(l) → 2NaOH(aq) + H₂(g) + 2Hg(l)**\n- **整體反應：2Na⁺(aq) + 2Cl⁻(aq) + Hg(l) → 2Na/Hg(aq) + Cl₂(g)**",
                "page": 38,
                "tags": ["鈉汞齊", "Na⁺", "汞陰極", "整體反應"],
            },
        ],
    },
    {
        "id": "2b-s21",
        "title": "電解 CuSO₄(aq)：用碳電極",
        "points": [
            {
                "id": "2b-s21-p1",
                "title": "電解 CuSO₄(aq)（碳電極）的兩極反應",
                "body": "溶液中離子為 **Cu²⁺、SO₄²⁻、H⁺、OH⁻**，兩極皆用碳電極：\n- **陽極：4OH⁻(aq) → O₂(g) + 2H₂O(l) + 4e⁻**（OH⁻ 位置較 SO₄²⁻ 高，優先放電生成 O₂）\n- **陰極：Cu²⁺(aq) + 2e⁻ → Cu(s)**。⚠️ Cu²⁺ 在電化序的位置較 H⁺ **低**，所以 Cu²⁺ 優先放電，於陰極**析出銅**。",
                "page": 39,
                "tags": ["電解CuSO₄", "Cu²⁺", "OH⁻"],
            },
            {
                "id": "2b-s21-p2",
                "title": "整體反應與溶液的變化",
                "body": "**整體反應：2Cu²⁺(aq) + 4OH⁻(aq) → 2Cu(s) + O₂(g) + 2H₂O(l)**。\n⚠️ 教師指出：過程中**不消耗 Cu²⁺ 及 OH⁻**（兩者同時在兩極被消耗並再生），溶液的**藍色逐漸變淺／褪去**，最終變成**稀硫酸 H₂SO₄**（SO₄²⁻ 與 H⁺ 殘留）。",
                "page": 39,
                "tags": ["電解CuSO₄", "整體反應", "溶液變化", "H₂SO₄"],
            },
        ],
    },
]

H.append(H.load(), BATCH)
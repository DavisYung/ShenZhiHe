# -*- coding: utf-8 -*-
"""最終掃描：化學式完整性 + 抽印 tf/fill 題"""
import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
base = r"D:\deepseek-harness\default-workspace\f6chem"
Q = json.load(open(os.path.join(base, "quiz", "3a.json"), encoding="utf-8"))["questions"]
blob = json.dumps(Q, ensure_ascii=False)

# 常見化學式必須存在且未被字母誤替
MUST = ["C=C", "CO₂", "CO", "CH₄", "C₄H₈", "CH₃CH₂OH", "C₂H₅OH", "Br₂", "KMnO₄",
        "H₂SO₄", "C₆H₁₂O₆", "C₂H₅OH", "CH₂Br-CH₂Br", "C₅H₁₀", "C₁₆H₃₄", "CH₃COOCH₂CH₃",
        "H₂N(CH₂)₆NH₂", "CH₂=C(CH₃)COOCH₃", "Al₂O₃"]
miss = [m for m in MUST if m not in blob]
print("缺失的化學式:", miss if miss else "無")

# 不應出現的畸形
BADPAT = r"B=B|A=B|D=C|CO₃\?|H₂SO_?C|CH₃COOC_?H₅"
print("畸形化學式:", re.findall(BADPAT, blob) or "無")

# 亂碼檢查
print("含替換字元:", "�" in blob)

for q in Q:
    if q["type"] == "tf":
        print(f"[{q['id']}] {q['point']} answer={q['answer']}  {q['q'][:70]}")
print()
for q in Q:
    if q["type"] == "fill":
        print(f"[{q['id']}] {q['point']} answer={q['answer']}  {q['q'][:60]}")
print("\nALL GOOD" if not miss and "\ufffd" not in blob else "\nCHECK NEEDED")
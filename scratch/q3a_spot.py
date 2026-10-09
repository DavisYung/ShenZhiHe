# -*- coding: utf-8 -*-
"""抽驗：旋轉後的 mc 題，答案選項是否與 explanation 的正確敘述一致"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
base = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
Q = json.load(open(os.path.join(base, "quiz", "3a.json"), encoding="utf-8"))["questions"]
ids = sys.argv[1:]
for q in Q:
    if ids and q["id"] not in ids: continue
    if q["type"] != "mc": continue
    print("##", q["id"], "| ans =", chr(65+q["answer"]))
    for i, o in enumerate(q["options"]):
        print(("   ->" if i == q["answer"] else "     "), chr(65+i), o)
    print("   ex:", q["explanation"][:300])
    print()
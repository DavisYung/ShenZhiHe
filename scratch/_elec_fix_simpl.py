# -*- coding: utf-8 -*-
"""修正电学数据中误入的简体字（香港繁体用字统一）。

用法: python _elec_fix_simpl.py

只做「简繁不同形」的安全替换，且只处理明确的通用词，不动专名
（「范德格拉夫」是标准译名，必须保留「范」）。
同时同步修正生成脚本，避免日后重跑又把简体写回。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 顺序很重要：先长词，后短词
REPL = [
    ("为什么", "為什麼"),
    ("什么", "什麼"),
    ("关系", "關係"),
    ("范德格拉夫", "范德格拉夫"),   # 占位：确认不动
]

TARGETS = []
for sub in ("data/phys", "quiz/phys"):
    d = os.path.join(BASE, sub)
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if n.startswith("elec") and n.endswith(".json"):
                TARGETS.append(os.path.join(d, n))
for n in ("_mk_elec1.py", "_mk_elec2.py"):
    p = os.path.join(BASE, "scratch", n)
    if os.path.isfile(p):
        TARGETS.append(p)

changed = 0
for p in TARGETS:
    txt = io.open(p, encoding="utf-8").read()
    orig = txt
    for a, b in REPL:
        if a != b:
            txt = txt.replace(a, b)
    if txt != orig:
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        changed += 1
        print("修正 %s" % os.path.basename(p))
    else:
        print("無需修改 %s" % os.path.basename(p))

print("\n共修改 %d 個檔" % changed)

# 复查
print("\n=== 复查 ===")
for p in TARGETS:
    txt = io.open(p, encoding="utf-8").read()
    left = [c for c in ("什", "么", "关", "为") if txt.count(c)]
    if left:
        print("%-20s 仍有 %s" % (os.path.basename(p), " ".join(left)))
    else:
        print("%-20s 乾淨" % os.path.basename(p))
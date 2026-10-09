# -*- coding: utf-8 -*-
"""點算 template.html 裡所有與站名／版本有關的字串，取得可信事實。

工具回顯的行號有時會錯亂，改檔前先用這支腳本確認每個錨點的真實出現次數。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "template.html")

with io.open(TPL, encoding="utf-8") as f:
    lines = f.readlines()
text = "".join(lines)

PATTERNS = [
    "<title>F6 化學筆記整合網</title>",
    "F6 筆記整合網",
    "F6 化學筆記整合網",
    "F6筆記整合網",
    "F6化學筆記整合網",
    "sitever",
    "DATA.site",
    "const SITE",
    "<footer>",
    "brandname",
    "__DATA__",
    "F6 化學",
]

print("template.html 共 %d 行，%d 字元\n" % (len(lines), len(text)))
for p in PATTERNS:
    cnt = text.count(p)
    locs = [str(i + 1) for i, ln in enumerate(lines) if p in ln]
    print("%-28s 出現 %2d 次  %s" % (p, cnt, ",".join(locs[:12])))

print("\n--- 首 8 行 ---")
for i, ln in enumerate(lines[:8]):
    print("%3d| %s" % (i + 1, ln.rstrip()))

print("\n--- footer 附近 ---")
for i, ln in enumerate(lines):
    if "<footer>" in ln or "sitever" in ln:
        print("%3d| %s" % (i + 1, ln.rstrip()))

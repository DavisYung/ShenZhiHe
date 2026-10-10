# -*- coding: utf-8 -*-
"""把 version.json 的 subtitle/tagline 也修回与 V0.3.0 一致：核物理尚未上线，先不宣称四科。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

p = r"f6chem\site\version.json"
t = json.load(io.open(p, encoding="utf-8"))

t["subtitle"] = "三科筆記整合網"
t["tagline"] = "化學、物理、生物三科離線筆記 · 知識圖譜 · 測驗與複習排程 · 歷屆試卷考點標記"
t["note"] = ("版號規則：V0.0.x = Demo／開發中，每次結構性改動加 x；V0.1.0 = 內容大致定型、"
             "可正式分享；V0.2.0 = 新增物理電學分區（六課，靜電學至輸電）。只改這個檔，"
             "build.py 會自動套用到檔名、頁面標題與頁尾。")

with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("version =", t["version"])
print("tagline =", t["tagline"])
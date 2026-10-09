# -*- coding: utf-8 -*-
"""抽查：打印指定 map 档里若干条映射的完整内容 + 对应 OCR 原题片段，供人工比对。"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")
MAPD = os.path.join(BASE, "scratch", "map")

which = sys.argv[1]            # e.g. 2012_p1a
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
d = json.load(io.open(os.path.join(MAPD, which + ".json"), encoding="utf-8"))
year = d["year"]
# 按 ref 的节选对应 OCR 文件（避免跨文件搜题号错位）
PART_FILE = {"P1A": "_p1_mc.txt", "P1B": "_p1_b.txt"}
cat = {}
for line in io.open(os.path.join(PP, "catalog.tsv"), encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    cat[parts[0]] = parts[3] if len(parts) > 3 else ""

maps = d["mappings"]
step = max(1, len(maps) // n)
picks = maps[::step][:n]
for m in picks:
    ref = m["ref"]
    print("=== %s  points=%s" % (ref, m.get("points")))
    print("    focus: %s" % m.get("focus"))
    for pid in m.get("points") or []:
        print("    %s → %s" % (pid, cat.get(pid, "?")))
    # 定位对应 OCR 文件与题目片段
    sec = "P2" if "-P2" in ref else ("P1B" if "-P1B" in ref else "P1A")
    suffix = "_p2.txt" if sec == "P2" else PART_FILE[sec]
    p = os.path.join(PP, "%d%s" % (year, suffix))
    ocr = io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    qn = re.search(r"Q(\d+)", ref)
    if qn and ocr:
        pat = r"\n\s*%s[\.\．]\s" % re.escape(qn.group(1))
        mm = re.search(pat, ocr)
        if mm:
            seg = ocr[mm.start():mm.start() + 400].replace("\n", " ⏎ ")
            print("    OCR(%s): %s..." % (suffix.strip("_"), seg[:360]))
    print()

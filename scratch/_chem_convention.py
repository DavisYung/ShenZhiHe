# -*- coding: utf-8 -*-
"""核查化学区的既有惯例：一个知识点的 page 字段与内嵌图片页码是什么关系。

用来判断物理区的「多页知识点」写法是否符合项目既定惯例。
"""
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEM = os.path.join(BASE, "data", "chem")

same = multi_img = mismatch = total = 0
examples = []
multi_examples = []

for n in sorted(os.listdir(CHEM)):
    if not n.endswith(".json") or n in ("subject.json", "links.json"):
        continue
    with io.open(os.path.join(CHEM, n), encoding="utf-8") as f:
        t = json.load(f)
    for s in t.get("sections", []):
        for pt in s.get("points", []):
            body = pt.get("body") or ""
            page = pt.get("page")
            imgs = re.findall(r"!\[[^\]]*\]\(img/([^)\s]+)\)", body)
            # 从檔名抽页码，如 1a_p2_b466.webp → 2
            pages = []
            for im in imgs:
                m = re.search(r"_p(\d+)_", im)
                if m:
                    pages.append(int(m.group(1)))
            if not pages:
                continue
            total += 1
            if len(pages) > 1:
                multi_img += 1
                if len(multi_examples) < 6:
                    multi_examples.append((pt.get("id"), page, sorted(set(pages))))
            if all(p == page for p in pages):
                same += 1
            else:
                mismatch += 1
                if len(examples) < 8:
                    examples.append((pt.get("id"), page, sorted(set(pages))))

print("=== 化学区：有内嵌图片的知识点 %d 个 ===" % total)
print("  图片页码与 page 字段完全一致: %d" % same)
print("  含不一致（多页/跨页）      : %d" % mismatch)
print("  其中内嵌多张图的知识点      : %d" % multi_img)

if examples:
    print("\n不一致的例子（id, page字段, 图片页码）:")
    for e in examples:
        print("   %-18s page=%-4s imgs=%s" % e)

if multi_examples:
    print("\n内嵌多张图的例子:")
    for e in multi_examples:
        print("   %-18s page=%-4s imgs=%s" % e)

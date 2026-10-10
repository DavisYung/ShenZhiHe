# -*- coding: utf-8 -*-
"""查看 wave5 / wave7 已落盘 data 的点结构与页图引用（写 quiz 前必须先看）。"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

for tid in ("wave5", "wave7"):
    p = "f6chem/data/phys/%s.json" % tid
    d = json.load(io.open(p, encoding="utf-8"))
    print("=" * 72)
    print("%s  (%s)  pdf=%s" % (d["id"], d["title"], d.get("pdf")))
    print("=" * 72)
    for s in d["sections"]:
        print("  %s  %s" % (s["id"], s["title"]))
        for pt in s["points"]:
            imgs = re.findall(r"img/(phys_\w+_\d+\.webp)", pt["body"] or "")
            print("    %-16s p%-3s %-40s 图=%d" % (pt["id"], pt.get("page"), (pt["title"] or "")[:44], len(imgs)))
    # quiz 现状
    qp = "f6chem/quiz/phys/%s.json" % tid
    if os.path.exists(qp):
        q = json.load(io.open(qp, encoding="utf-8"))
        from collections import Counter
        print("  quiz: %d 题 %s\n" % (len(q["questions"]), dict(Counter(x["type"] for x in q["questions"]))))
    else:
        print("  quiz: 未落盘\n")

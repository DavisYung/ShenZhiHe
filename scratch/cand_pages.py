# -*- coding: utf-8 -*-
"""挑出每个课题「疑似含关键图」的候选页，供找图子代理按页取证。

信号：
1. point 标题含图类关键词（圖/裝置/結構/流程/週期表/階/循環/儀器/譜/示意...）
2. 该页正文文字量很低（页面大部分留给图）
每页附上该页的 point 线索（id+title），代理据此选挂载点。
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "chem")

FIG_KW = ["圖", "裝置", "結構", "流程", "週期表", "焓階", "能階", "循環", "儀器",
          "譜", "示意", "分餾", "滴定", "曲線", "坐標", "圖解", "方格", "塔", "爐",
          "電解池", "原電池", "電子式", "點‑叉", "排佈圖", "分布"]

meta = json.load(io.open(os.path.join(BASE, "pages", "meta.json"), encoding="utf-8"))
sub = json.load(io.open(os.path.join(DATA, "subject.json"), encoding="utf-8"))

out = {}
for tid in sub["topics"]:
    t = json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8"))
    by_page = {}
    kw_pages = {}
    for s in t["sections"]:
        for p in s["points"]:
            pg = p["page"]
            by_page.setdefault(pg, []).append((p["id"], p["title"]))
            body_len = len(p.get("body") or "")
            hit = [k for k in FIG_KW if k in p["title"]]
            if hit:
                kw_pages.setdefault(pg, set()).add(p["id"] + "|" + p["title"])
    # 低文字页：该页所有 point 正文总长 < 阈值 → 疑似大半是图
    low = set()
    for pg, lst in by_page.items():
        # 重新从 data 拿 body 长度
        total = 0
        for s in t["sections"]:
            for p in s["points"]:
                if p["page"] == pg:
                    total += len(p.get("body") or "")
        if total < 420:
            low.add(pg)
    cand = sorted(set(kw_pages) | low)
    lines = []
    for pg in cand:
        pts = "; ".join("%s %s" % (i, ti) for i, ti in by_page.get(pg, []))
        lines.append("p%02d: %s" % (pg, pts))
    out[tid] = {
        "pages": meta.get(tid, {}).get("pages"),
        "candidates": lines,
        "kw_hits": len(kw_pages),
        "low_text": len(low),
    }

for tid, v in out.items():
    print("=== %s (%s pages) candidates=%d (kw=%d low=%d) ==="
          % (tid, v["pages"], len(v["candidates"]), v["kw_hits"], v["low_text"]))
    for ln in v["candidates"]:
        print("  ", ln[:150])

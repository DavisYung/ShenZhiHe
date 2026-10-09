# -*- coding: utf-8 -*-
"""从 data/chem/*.json 的 exam 标注重生 extras/chem/hot.json（高频考点报告）。

口径（与站点 viewHot 一致）：
  point.hits  = len(years)；level：>=5 年=3 必考 / 2-4 年=2 常考 / 1 年=1 考过
  summary.hits = Σ len(years)（点-年对）
  topics[].hits = 该课题所有点的 Σ len(years)
  years[].hits = 该年 sample 条数（一道题命中一个知识点算一条）
  keywords     = 所有带标注知识点的得分字眼词频（全站）

用法：python f6chem/_mk_hot.py
"""
import glob
import io
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "chem")
DST = os.path.join(BASE, "extras", "chem", "hot.json")


def level_of(nyears):
    if nyears >= 5:
        return 3
    if nyears >= 2:
        return 2
    return 1


def load_points():
    pts = []  # (point, topic_id, topic_title, sec_title)
    topic_titles = {}
    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        stem = os.path.basename(f)[:-5]
        if stem in ("subject", "links", "index"):
            continue
        t = json.load(io.open(f, encoding="utf-8"))
        if not isinstance(t, dict):
            continue
        topic_titles[stem] = t.get("title") or stem
        for s in t.get("sections") or []:
            for p in s.get("points") or []:
                if p.get("exam"):
                    pts.append((p, stem, topic_titles[stem], s.get("title", "")))
    return pts, topic_titles


def main():
    pts, topic_titles = load_points()
    years_all = sorted({y for p, _, _, _ in pts for y in (p["exam"].get("years") or [])})
    lv = Counter(level_of(len(p["exam"].get("years") or [])) for p, _, _, _ in pts)
    n_hits = sum(len(p["exam"].get("years") or []) for p, _, _, _ in pts)

    # --- groups: lv3 / lv2 条目 ---
    groups = [
        {"id": "lv3", "name": "🔥 必考熱點（5 年以上）", "color": "#dc2626", "items": []},
        {"id": "lv2", "name": "⭐ 常考（2-4 年）", "color": "#ea580c", "items": []},
    ]
    for p, tid, tname, sec in pts:
        e = p["exam"]
        n = len(e.get("years") or [])
        lvn = level_of(n)
        if lvn == 3:
            gi = 0
        elif lvn == 2:
            gi = 1
        else:
            continue
        groups[gi]["items"].append({
            "id": p["id"], "topic": tid, "tname": tname, "sec": sec,
            "title": p.get("title", ""), "page": p.get("page"),
            "years": sorted(e.get("years") or []),
            "hits": n, "level": lvn,
            "kw": e.get("keywords") or [],
            "samples": e.get("samples") or [],
        })
    for g in groups:
        g["items"].sort(key=lambda i: (-i["hits"], i["id"]))

    # --- topics（命中降序）---
    thit = Counter()
    tseen = set()
    for p, tid, _, _ in pts:
        thit[tid] += len(p["exam"].get("years") or [])
        tseen.add(tid)
    topics = [{"id": tid, "name": topic_titles.get(tid, tid), "hits": thit[tid]}
              for tid in sorted(tseen, key=lambda k: (-thit[k], k))]

    # --- years（该年题-点映射条数）---
    y_samp = Counter()
    y_topics = {}
    for p, tid, _, _ in pts:
        for sm in p["exam"].get("samples") or []:
            y = sm.get("y")
            if y is None:
                continue
            y_samp[y] += 1
            y_topics.setdefault(y, set()).add(tid)
    years = [{"year": y, "topics": sorted(y_topics.get(y, set())),
              "hits": y_samp.get(y, 0)} for y in years_all]

    # --- 得分字眼词频 ---
    kw_c = Counter()
    for p, _, _, _ in pts:
        for k in (p["exam"].get("keywords") or []):
            kw_c[k] += 1
    keywords = [{"text": k, "count": c} for k, c in
                sorted(kw_c.items(), key=lambda kv: (-kv[1], kv[0]))]

    npts = len(pts)
    span = ("%d–%d" % (years_all[0], years_all[-1])) if years_all else "?"
    hot = {
        "id": "hot", "type": "hot", "order": 2, "emoji": "🔥",
        "title": "高頻考點報告",
        "subtitle": "%d 年歷屆試卷（卷一＋卷二）逐題比對 · %d 個知識點標注 · 附得分字眼"
                    % (len(years_all), npts),
        "source": "香港考評局 HKEAA 化學科課程及評估指引（中四至中六）· "
                  "DSE %s 年中文試卷（卷一甲部／乙部、卷二）" % span,
        "intro": "每個知識點卡片上的「考過年份」徽章就是依這份對照表標的。"
                 "這裡把最常考的集中在前面：🔥 是 5 年以上都考過，⭐ 是 2-4 年。",
        "note": "本報告由本機 OCR 逐頁識別試卷後自動比對生成，僅供複習參考；"
                "過往試卷版權屬香港考試及評核局所有。OCR 對小數點、化學式下標偶有誤讀，"
                "個別題目的標注請以原卷為準。",
        "summary": {"years": years_all, "points": npts, "hits": n_hits,
                    "lv3": lv[3], "lv2": lv[2], "lv1": lv[1],
                    "topics": len(tseen)},
        "groups": groups,
        "topics": topics,
        "years": years,
        "keywords": keywords,
    }
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with io.open(DST, "w", encoding="utf-8") as f:
        json.dump(hot, f, ensure_ascii=False, separators=(",", ":"))
    print("hot.json: points=%d hits=%d lv3=%d lv2=%d lv1=%d years=%s"
          % (npts, n_hits, lv[3], lv[2], lv[1], years_all))
    print("groups: lv3=%d lv2=%d  keywords=%d  written: %s"
          % (len(groups[0]["items"]), len(groups[1]["items"]), len(keywords), DST))


if __name__ == "__main__":
    main()

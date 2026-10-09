# -*- coding: utf-8 -*-
"""挑关键图：对候选页打分选块 → 裁剪 → 生成送审清单。

- 候选页：标题含图类关键词（优先）或该页正文很短（次优）
- 每页选 1 个最像图的块（块坐标来自 pages/blocks.json，程序计算可靠）
- 裁剪（左右留 4% 边距、上下 6px padding）→ f6chem/scratch/figcrops/*.jpg
- 输出 f6chem/scratch/figcrops/manifest.json 供视觉子代理逐张送审
"""
import io, json, os, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # f6chem
DATA = os.path.join(BASE, "data", "chem")
PAGES = os.path.join(BASE, "pages")
OUT = os.path.join(BASE, "scratch", "figcrops")

FIG_KW = ["圖", "裝置", "結構", "流程", "週期表", "焓階", "能階", "循環", "儀器",
          "譜", "示意", "分餾", "滴定", "曲線", "坐標", "電子式", "排佈", "塔",
          "爐", "電解池", "原電池", "點‑叉", "分布", "框"]

PER_TOPIC = 10          # 每课题最多送审页数

blocks_all = json.load(io.open(os.path.join(PAGES, "blocks.json"), encoding="utf-8"))
os.makedirs(OUT, exist_ok=True)
manifest = []

for tid, pages in sorted(blocks_all.items()):
    # 页 → point 线索 / 关键词分 / 文字量
    page_pts, page_kw, page_len = {}, {}, {}
    t = json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8"))
    for s in t["sections"]:
        for p in s["points"]:
            pg = str(p["page"])
            page_pts.setdefault(pg, []).append({"id": p["id"], "title": p["title"]})
            page_len[pg] = page_len.get(pg, 0) + len(p.get("body") or "")
            if any(k in p["title"] for k in FIG_KW):
                page_kw[pg] = page_kw.get(pg, 0) + 1

    ranked = []
    for pg, pts in page_pts.items():
        if pg not in pages:
            continue
        if pg in page_kw:
            ranked.append((0, -page_kw[pg], pg))
        elif page_len.get(pg, 9999) < 420:
            ranked.append((1, page_len.get(pg, 9999), pg))
    ranked.sort()
    chosen = ranked[:PER_TOPIC]

    for _, _, pg in chosen:
        blocks = pages[pg]["blocks"]
        pool = [b for b in blocks if b["h"] >= 110 and b["ink"] >= 0.008]
        if not pool:
            pool = [b for b in blocks if b["h"] >= 80]
        if not pool:
            continue
        def score(b):
            return b.get("lines", 0) * 8 + (0 if b.get("kind") == "text" else 25) + min(b["h"], 700) / 10.0
        best = max(pool, key=score)

        src = os.path.join(PAGES, tid, "p%03d.jpg" % int(pg))
        if not os.path.exists(src):
            continue
        im = Image.open(src)
        w, h = im.size
        x1, x2 = int(w * 0.04), int(w * 0.96)
        y1 = max(0, best["y1"] - 6)
        y2 = min(h, best["y2"] + 6)
        if y2 - y1 < 80:
            continue
        item_id = "%s_p%s_b%d" % (tid, pg, best["y1"])
        crop = im.crop((x1, y1, x2, y2))
        crop.save(os.path.join(OUT, item_id + ".jpg"), quality=90)
        manifest.append({
            "id": item_id, "tid": tid, "page": int(pg),
            "box": [x1, y1, x2, y2],
            "kind_guess": best.get("kind"),
            "points": page_pts[pg],
        })

with io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
from collections import Counter
c = Counter(m["tid"] for m in manifest)
print("crops:", len(manifest), dict(c))

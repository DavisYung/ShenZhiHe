# -*- coding: utf-8 -*-
"""把 attached.json 里的图挂到对应知识点 body 顶部（幂等）。

body 顶部插入一行：  ![說明](img/<file>.webp)
build.py 会把 img/<file> 转成 data URI 注入 payload。
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROPS = os.path.join(BASE, "scratch", "figcrops")
DATA = os.path.join(BASE, "data", "chem")
IMG_DIR = os.path.join(BASE, "site", "img")

attached = json.load(io.open(os.path.join(CROPS, "attached.json"), encoding="utf-8"))

# 按课题分组加载
tids = sorted({a["tid"] for a in attached})
docs = {tid: json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8"))
        for tid in tids}

# 页 → 该页所有 point（挂载时如果指定点不在，退回该页第一个）
stats = {"ok": 0, "skip_exists": 0, "no_point": 0, "missing_file": 0}
for a in attached:
    fn = a["file"]
    if not os.path.exists(os.path.join(IMG_DIR, fn)):
        stats["missing_file"] += 1
        continue
    t = docs[a["tid"]]
    target = None
    page_pts = []
    for s in t["sections"]:
        for p in s["points"]:
            if p["page"] == a["page"]:
                page_pts.append(p)
            if p["id"] == a["point"]:
                target = p
    if target is None and page_pts:
        target = page_pts[0]
    if target is None:
        stats["no_point"] += 1
        continue
    ref = "![筆記原圖 p%d](img/%s)" % (a["page"], fn)
    body = target.get("body") or ""
    if "](img/" in body:
        stats["skip_exists"] += 1
        continue
    target["body"] = ref + "\n\n" + body
    stats["ok"] += 1

for tid, t in docs.items():
    with io.open(os.path.join(DATA, tid + ".json"), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("written", tid)

print(stats)

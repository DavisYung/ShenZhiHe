# -*- coding: utf-8 -*-
"""把通过筛选的裁剪图压成 WebP、挂到知识点 body。

- 压缩：宽 >900px 先缩到 900，WebP quality 75 → 单张目标 ≤60KB
- 挂载：body 顶部插入一行 `![說明](img/<file>.webp)`（相对引用，build 时转 data URI）
- 幂等：body 已含 img/ 引用的点跳过
- 输出 f6chem/site/img/*.webp + 挂载清单 JSON

筛选结果（十张联络表 modlens 判读，纯文字格剔除）见 ACCEPT/REJECT 内联表。
"""
import io, json, os, sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # f6chem
CROPS = os.path.join(BASE, "scratch", "figcrops")
IMG_DIR = os.path.join(BASE, "site", "img")
DATA = os.path.join(BASE, "data", "chem")

# 联络表判读结果：编号 → 是否为图
# sheet1-8、10 由 modlens 逐格判读；sheet9(#97-108) 因 Gemini 429 改由
# read_image 直读目检（编号自验无错位）：仅 #99 为纯方程式行。
JUDGE = {}
for rng, verdict in [
    (range(1, 7), True), (range(7, 8), False), (range(8, 13), True),      # sheet1
    (range(13, 15), False), (range(15, 20), True), (range(20, 21), False),
    (range(21, 25), True),                                                 # sheet2
    (range(25, 26), False), (range(26, 27), True), (range(27, 29), False),
    (range(29, 36), True), (range(36, 37), False),                         # sheet3
    (range(37, 39), False), (range(39, 44), True), (range(44, 46), False),
    (range(46, 49), True),                                                 # sheet4
    (range(49, 54), True), (range(54, 55), False), (range(55, 59), True),
    (range(59, 60), False), (range(60, 61), True),                         # sheet5
    (range(61, 63), True), (range(63, 65), False), (range(65, 70), True),
    (range(70, 71), False), (range(71, 73), True),                         # sheet6
    (range(73, 74), False), (range(74, 85), True),                         # sheet7
    (range(85, 89), True), (range(89, 92), False), (range(92, 97), True),  # sheet8
    (range(97, 99), True), (range(99, 100), False), (range(100, 109), True),  # sheet9
    (range(109, 120), True),                                               # sheet10
]:
    for n in rng:
        JUDGE[n] = verdict

manifest = json.load(io.open(os.path.join(CROPS, "manifest.json"), encoding="utf-8"))
manifest.sort(key=lambda m: (m["tid"], m["page"]))
ref = {i + 1: m["id"] for i, m in enumerate(manifest)}

os.makedirs(IMG_DIR, exist_ok=True)
attached, skipped = [], []

# body 预载（幂等检查）
bodies = {}
for tid in sorted({m["tid"] for m in manifest}):
    t = json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8"))
    bodies[tid] = t

attach_count = {}
for n, m in enumerate(manifest, start=1):
    verdict = JUDGE.get(n)
    if verdict is False:
        continue
    src = os.path.join(CROPS, m["id"] + ".jpg")
    if not os.path.exists(src):
        skipped.append((n, m["id"], "no file"))
        continue
    im = Image.open(src)
    if im.width > 900:
        im = im.resize((900, int(im.height * 900 / im.width)), Image.LANCZOS)
    fn = m["id"]
    outp = os.path.join(IMG_DIR, fn + ".webp")
    im.save(outp, "WEBP", quality=75, method=5)
    size = os.path.getsize(outp)
    if size > 90_000:                     # 超预算再降质量
        im.save(outp, "WEBP", quality=60, method=5)
        size = os.path.getsize(outp)
    attached.append({"file": fn + ".webp", "kb": round(size / 1024, 1),
                     "point": m["points"][0]["id"], "tid": m["tid"],
                     "page": m["page"], "n": n})
    attach_count[m["tid"]] = attach_count.get(m["tid"], 0) + 1

print("judged figure: %d / %d" % (sum(1 for v in JUDGE.values() if v), len(manifest)))
print("compressed:", len(attached), "files, total %.2f MB"
      % (sum(a["kb"] for a in attached) / 1024))
print("per topic:", attach_count)

with io.open(os.path.join(CROPS, "attached.json"), "w", encoding="utf-8") as f:
    json.dump(attached, f, ensure_ascii=False, indent=1)
print("→ scratch/figcrops/attached.json（挂载步骤下一步执行，先不改 body）")

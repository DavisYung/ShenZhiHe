# -*- coding: utf-8 -*-
"""把裁剪图拼成带编号的联络表（每张 12 图一页），供目检筛选。"""
import io, json, os, sys

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "scratch", "figcrops")
OUT = os.path.join(BASE, "scratch", "sheets")
os.makedirs(OUT, exist_ok=True)

manifest = json.load(io.open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))
manifest.sort(key=lambda m: (m["tid"], m["page"]))

COLS, ROWS = 4, 3
CELL_W, CELL_H = 460, 340
PER = COLS * ROWS

sheets = []
for si in range(0, len(manifest), PER):
    chunk = manifest[si:si + PER]
    sheet = Image.new("RGB", (COLS * CELL_W, ROWS * (CELL_H + 26)), "white")
    d = ImageDraw.Draw(sheet)
    for i, m in enumerate(chunk):
        p = os.path.join(SRC, m["id"] + ".jpg")
        if not os.path.exists(p):
            continue
        im = Image.open(p)
        im.thumbnail((CELL_W - 12, CELL_H - 12))
        cx = (i % COLS) * CELL_W
        cy = (i // COLS) * (CELL_H + 26)
        sheet.paste(im, (cx + 6, cy + 26))
        label = "#%d %s p%02d" % (si + i + 1, m["tid"], m["page"])
        d.rectangle([cx, cy, cx + CELL_W, cy + 24], fill="black")
        d.text((cx + 8, cy + 6), label, fill="white")
    out = os.path.join(OUT, "sheet_%d.jpg" % (si // PER + 1))
    sheet.save(out, quality=88)
    sheets.append((out, [m["id"] for m in chunk]))

# 输出编号→id 对照表
ref = {si + i + 1: m["id"] for si in range(0, len(manifest), PER)
       for i, m in enumerate(manifest[si:si + PER])}
with io.open(os.path.join(OUT, "ref.json"), "w", encoding="utf-8") as f:
    json.dump(ref, f, ensure_ascii=False, indent=0)
for s, _ in sheets:
    print(s, os.path.getsize(s) // 1024, "KB")

# -*- coding: utf-8 -*-
"""生成交付包里各图标的预览图，方便一眼确认外观。"""
import os, sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("TEMP", ".")

items = [
    ("apple-touch-icon.png", "180 iOS"),
    ("apple-touch-icon-167.png", "167 iPad Pro"),
    ("apple-touch-icon-152.png", "152 iPad"),
    ("icon-192.png", "192 Android"),
    ("icon-512.png", "512 PWA"),
    ("icon-maskable-512.png", "512 maskable"),
    ("favicon-32.png", "32 favicon"),
]

# 统一缩放到 128 展示
CELL = 128
GAP = 18
LABEL_H = 26
W = GAP + len(items) * (CELL + GAP)
H = LABEL_H + CELL + GAP * 2
canvas = Image.new("RGB", (W, H), (245, 245, 245))
d = ImageDraw.Draw(canvas)
font = None
try:
    from PIL import ImageFont
    font = ImageFont.load_default()
except Exception:
    pass

for i, (fn, label) in enumerate(items):
    p = os.path.join(BASE, fn)
    im = Image.open(p).convert("RGB").resize((CELL, CELL), Image.LANCZOS)
    x = GAP + i * (CELL + GAP)
    y = LABEL_H + GAP
    canvas.paste(im, (x, y))
    d.text((x, 8), label, fill=(40, 40, 40), font=font)

out = os.path.join(OUT, "icon_preview.png")
canvas.save(out)
print("预览图：%s" % out)

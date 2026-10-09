# -*- coding: utf-8 -*-
"""定位透明像素到底在哪：四角？边缘？还是整块区域？"""
import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SITE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.join(SITE, "icons")

for n in ("apple-touch-icon.png", "icon-192.png"):
    p = os.path.join(IDIR, n)
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    print("=== %s (%dx%d) ===" % (n, w, h))
    pts = {
        "左上角(0,0)": (0, 0),
        "右上角": (w - 1, 0),
        "左下角": (0, h - 1),
        "右下角": (w - 1, h - 1),
        "中心": (w // 2, h // 2),
        "上边中点": (w // 2, 0),
        "左边中点": (0, h // 2),
        "内部(10,10)": (10, 10),
    }
    for label, xy in pts.items():
        print("  %-14s RGBA=%s" % (label, im.getpixel(xy)))

    # 统计 alpha 分布
    a = im.getchannel("A")
    hist = a.histogram()
    print("  alpha=0 的像素: %d" % hist[0])
    print("  alpha=255 的像素: %d" % hist[255])
    print("  0<alpha<255 的像素: %d" % sum(hist[1:255]))
    print("  总计: %d (%.1f%% 完全透明)" % (w * h, hist[0] / (w * h) * 100))
    print()

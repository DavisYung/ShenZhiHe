# -*- coding: utf-8 -*-
"""诊断 PWA 图标：iOS 对 apple-touch-icon 有硬性要求，逐项检查。"""
import io, os, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SITE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.join(SITE, "icons")

print("=== 图标文件体检 ===\n")
for n in sorted(os.listdir(IDIR)):
    p = os.path.join(IDIR, n)
    if not n.lower().endswith(".png"):
        continue
    im = Image.open(p)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    # 统计真正透明的像素
    n_trans = 0
    if has_alpha:
        a = im.convert("RGBA").getchannel("A")
        hist = a.histogram()
        n_trans = sum(hist[:255])   # 非 255 的都算半透明/透明
    print("%-26s mode=%-5s size=%-9s alpha=%-5s 非不透明像素=%d"
          % (n, im.mode, "%dx%d" % im.size, "是" if has_alpha else "否", n_trans))
    if has_alpha and n_trans:
        print("      ⚠️ 有透明/半透明像素 —— iOS 会把透明处渲染成黑色")

print("\n=== 根目录是否有 apple-touch-icon（iOS 的兜底查找位置）===")
for cand in ("apple-touch-icon.png", "apple-touch-icon-precomposed.png"):
    p = os.path.join(SITE, cand)
    print("  %-34s %s" % (cand, "存在" if os.path.exists(p) else "❌ 不存在"))

print("\n=== 站点 HTML 里的图标声明 ===")
html = os.path.join(SITE, "神智核.html")
with io.open(html, encoding="utf-8") as f:
    t = f.read()
import re
for m in re.finditer(r'<link[^>]*(?:icon|manifest)[^>]*>', t):
    print("  " + m.group(0))

print("\n=== manifest 里的图标 ===")
import json
with io.open(os.path.join(SITE, "manifest.json"), encoding="utf-8") as f:
    mf = json.load(f)
for i in mf.get("icons", []):
    p = os.path.join(SITE, i["src"].lstrip("./").replace("/", os.sep))
    print("  %-34s sizes=%-9s purpose=%-9s 檔案%s"
          % (i["src"], i.get("sizes"), i.get("purpose"),
             "存在" if os.path.exists(p) else "❌ 缺失"))

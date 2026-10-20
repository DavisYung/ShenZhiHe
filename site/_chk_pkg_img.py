# -*- coding: utf-8 -*-
"""校驗交付包：index.html 引用的所有 img/ 圖片是否都存在。

用法：python _chk_pkg_img.py <交付包目錄>
"""
import io
import os
import re
import sys
from collections import Counter

pkg = sys.argv[1] if len(sys.argv) > 1 else "."
html_path = os.path.join(pkg, "index.html")
if not os.path.exists(html_path):
    sys.exit("找不到 %s" % html_path)

with io.open(html_path, encoding="utf-8") as f:
    html = f.read()

refs = set(re.findall(r"img/[A-Za-z0-9_\-/]+\.[a-zA-Z0-9]+", html))
missing = [r for r in sorted(refs) if not os.path.exists(os.path.join(pkg, r.replace("/", os.sep)))]
ext = Counter(os.path.splitext(r)[1] for r in refs)

print("index.html 引用圖片：%d 張  %s" % (len(refs), dict(ext)))
print("缺失：%d" % len(missing))
for m in missing[:20]:
    print("  MISS", m)

# 其他必要檔案
need = ["404.html", ".nojekyll", "manifest.json", "service-worker.js",
        "apple-touch-icon.png", "apple-touch-icon-167.png", "apple-touch-icon-152.png",
        "favicon.ico", "favicon-32.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]
gone = [n for n in need if not os.path.exists(os.path.join(pkg, n))]
print("缺少必要檔案：%d %s" % (len(gone), gone))

sys.exit(1 if (missing or gone) else 0)

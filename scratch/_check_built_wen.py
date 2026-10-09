# -*- coding: utf-8 -*-
"""检查构建产物里是否残留「温度」这种异体字写法。

注意：「温和提示」的「温」是正确用字（温和），不是错字。
所以只检查「温」紧接「度」的情况——那才是应该写成「溫度」的地方。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, "site")

# 「温度」= 异体字（错）；「温和」= 正确用字（对）
BAD = re.compile("\u6e29\u5ea6")      # 温度
ALL = re.compile("\u6e29")            # 所有「温」

for name in ("神智核.html", "神智核-V0.0.16.html"):
    p = os.path.join(SITE, name)
    if not os.path.exists(p):
        print("  缺少 %s" % name)
        continue
    t = io.open(p, encoding="utf-8").read()
    n_bad = len(BAD.findall(t))
    n_all = len(ALL.findall(t))
    print("  %-24s %6.2f MB   「温度」錯字 %d   「温」總數 %d  %s"
          % (name, os.path.getsize(p) / 1024.0 / 1024.0, n_bad, n_all,
             "✓" if n_bad == 0 else "✗"))
    if n_bad:
        for m in list(BAD.finditer(t))[:3]:
            print("     例: ...%s..." % t[max(0, m.start() - 45):m.start() + 45].replace("\n", " "))
    # 剩下的「温」都應該是「温和」之類
    for m in ALL.finditer(t):
        after = t[m.start() + 1:m.start() + 2]
        if after != "\u548c":   # 和
            print("     ℹ 「温」後接「%s」: ...%s..." % (after, t[max(0, m.start() - 30):m.start() + 30].replace("\n", " ")))

# -*- coding: utf-8 -*-
"""列出物理数据中每个疑似简体字的上下文，供人工确认是误报还是真的要改。

用法: python _elec_simpl_ctx.py [档名片段]
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 待确认字（简繁不同形，但部分可能是专名正确用字）
CHARS = "什么点绝内对热变匀画于据数动侧范关为"

TARGETS = []
for sub in ("data/phys", "quiz/phys"):
    d = os.path.join(BASE, sub)
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if n.endswith(".json"):
                TARGETS.append(os.path.join(d, n))

filt = sys.argv[1] if len(sys.argv) > 1 else None

for p in TARGETS:
    name = os.path.basename(p)
    if filt and filt not in name:
        continue
    txt = io.open(p, encoding="utf-8").read()
    hits = []
    for ch in CHARS:
        for m in re.finditer(re.escape(ch), txt):
            a = max(0, m.start() - 14)
            b = min(len(txt), m.end() + 14)
            ctx = txt[a:b].replace("\\n", " ")
            hits.append("    %s | …%s…" % (ch, ctx))
    if hits:
        print("=== %s (%d 处) ===" % (name, len(hits)))
        for h in hits[:40]:
            print(h)
        if len(hits) > 40:
            print("    …还有 %d 处" % (len(hits) - 40))
        print()
# -*- coding: utf-8 -*-
"""列出 elec*.json 中疑似简体字的上下文，供人工确认。

用法: python _elec_ctx.py [档名片段]
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARS = "什么范关为点绝内对热变匀画于据数动侧"

TARGETS = []
for sub in ("data/phys", "quiz/phys"):
    d = os.path.join(BASE, sub)
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if n.startswith("elec") and n.endswith(".json"):
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
            a = max(0, m.start() - 16)
            b = min(len(txt), m.end() + 16)
            hits.append("    %s | ...%s..." % (ch, txt[a:b]))
    if hits:
        print("=== %s (%d 处) ===" % (name, len(hits)))
        for h in hits:
            print(h)
        print()

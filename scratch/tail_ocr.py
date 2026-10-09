# -*- coding: utf-8 -*-
"""Dump OCR text for the pages this task must cover."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOBS = [
    ("2b", [40, 41, 42, 43, 44]),
    ("4b", [11, 12, 22]),
    ("8",  [27]),
]

for tid, pages in JOBS:
    for n in pages:
        p = os.path.join(ROOT, "ocr", tid, "p%03d.txt" % n)
        print("\n===== %s p%03d =====" % (tid, n))
        if not os.path.exists(p):
            print("!! missing:", p)
            continue
        txt = open(p, encoding="utf-8").read()
        print("[chars=%d]" % len(txt.strip()))
        print(txt.strip())
# -*- coding: utf-8 -*-
"""探测 data json 的落盘格式（缩进/换行/分隔符），确保 merge 后格式不漂移。"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"f6chem\data\chem\4a.json"
orig = io.open(p, encoding="utf-8").read()
d = json.loads(orig)
matched = False
for ind in (1, 2, 3, 4):
    out = json.dumps(d, ensure_ascii=False, indent=ind)
    for nl in ("", "\n"):
        if out + nl == orig:
            print("MATCH indent=%d trailing_nl=%r" % (ind, nl))
            matched = True
if not matched:
    print("NO MATCH; orig tail:", repr(orig[-80:]))
    print("indent1 tail:", repr(json.dumps(d, ensure_ascii=False, indent=1)[-80:]))
print("endswith newline:", orig.endswith("\n"), "len:", len(orig))

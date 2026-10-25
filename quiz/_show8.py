# -*- coding: utf-8 -*-
import json, io, sys
p = r"D:\deepseek-harness\default-workspace\f6chem\data\8.json"
d = json.loads(io.open(p, encoding="utf-8").read(), strict=False)
sys.stdout.reconfigure(encoding="utf-8")
want = sys.argv[1:]
for s in d["sections"]:
    for pt in s.get("points", []):
        if pt["id"] in want:
            print("=" * 8, pt["id"], pt.get("title", ""))
            print(pt.get("body", ""))

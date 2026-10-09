# -*- coding: utf-8 -*-
import json, io, sys
p = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\8.json"
raw = io.open(p, encoding="utf-8").read()
d = json.loads(raw, strict=False)
sys.stdout.reconfigure(encoding="utf-8")
for s in d["sections"]:
    print(s["id"], s.get("title", ""))
    for pt in s.get("points", []):
        print("   ", pt["id"], "|", pt.get("title", ""))

import json, glob, os

base = "C:/Users/guomi/OneDrive/文件/deepseek-harness/default-workspace/f6chem/nuclear/data"
for f in sorted(glob.glob(base + "/*.json")):
    with open(f, encoding="utf-8") as fh:
        d = json.load(fh)
    n = sum(len(s["points"]) for s in d["sections"])
    print(f"{d['id']:12s} title={d['title']:24s} sections={len(d['sections'])} points={n}")
    for s in d["sections"]:
        print(f"    - {s['id']}: {s['title']}")

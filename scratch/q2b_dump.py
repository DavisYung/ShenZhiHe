import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
d = json.load(open(os.path.join(BASE, "data", "2b.json"), encoding="utf-8"))
secs = d["sections"]
a = int(sys.argv[1]); b = int(sys.argv[2])
for s in secs:
    n = int(s["id"].split("-s")[1])
    if not (a <= n <= b):
        continue
    print("=== %s | %s" % (s["id"], s["title"]))
    for p in s["points"]:
        print("--- %s | %s" % (p["id"], p["title"]))
        print(p.get("body", ""))
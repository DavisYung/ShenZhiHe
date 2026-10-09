import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")

P = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\1b.json"
d = json.load(open(P, encoding="utf-8"))
secs = d["sections"]

sarg = sys.argv[1] if len(sys.argv) > 1 else "1"
earg = sys.argv[2] if len(sys.argv) > 2 else "18"
lo, hi = int(sarg), int(earg)

total = 0
for s in secs:
    n = int(s["id"].split("-")[1][1:])
    for p in s["points"]:
        b = p.get("body", "")
        if b:
            total += len(b)
print("[total body chars]", total, "file ok", file=sys.stderr)

for s in secs:
    n = int(s["id"].split("-")[1][1:])
    if not (lo <= n <= hi):
        continue
    print(f'===== {s["id"]} {s["title"]} =====')
    for p in s["points"]:
        b = re.sub(r"\n{2,}", "\n", p.get("body", "")).strip()
        print(f'--- {p["id"]} {p.get("title","")} [len={len(b)}]')
        print(b)
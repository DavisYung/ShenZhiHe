import json, sys
sys.stdout.reconfigure(encoding="utf-8")

P = r"D:\deepseek-harness\default-workspace\f6chem\data\1b.json"
d = json.load(open(P, encoding="utf-8"))
print("top keys:", list(d.keys()) if isinstance(d, dict) else type(d))
secs = d["sections"]
print("sections:", len(secs))
print("section keys:", list(secs[0].keys()))
for s in secs:
    pts = s.get("points", [])
    print(f'{s["id"]}  {s.get("title","")}   ({len(pts)} pts)')
    for p in pts:
        print(f'    {p["id"]}  {p.get("title","")}')

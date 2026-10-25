import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")

p = r"D:\deepseek-harness\default-workspace\f6chem\data\1b.json"
with io.open(p, encoding="utf-8") as f:
    raw = f.read()

d = json.loads(raw)
print("TOP TYPE:", type(d).__name__)
if isinstance(d, dict):
    print("TOP KEYS:", list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print("  list len", k, len(v))
secs = d["sections"] if isinstance(d, dict) and "sections" in d else d
print("num sections:", len(secs))
print("num points:", sum(len(s.get("points", [])) for s in secs))
print("last section ids:", [s["id"] for s in secs][-3:])
print("sample section:", json.dumps(secs[-1], ensure_ascii=False, indent=2)[:900])

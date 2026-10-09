import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
d = json.load(open(os.path.join(BASE, "data", "2b.json"), encoding="utf-8"))
print("top keys:", list(d.keys()) if isinstance(d, dict) else type(d))
secs = d["sections"] if isinstance(d, dict) else d
print("n_sections:", len(secs))
s0 = secs[0]
print("sec keys:", list(s0.keys()))
p0 = s0["points"][0]
print("point keys:", list(p0.keys()))
print("total points:", sum(len(s.get("points", [])) for s in secs))
for s in secs:
    print("==", s.get("id"), "|", s.get("title"))
    for p in s.get("points", []):
        body = p.get("body", "") or ""
        mark = " [OCR?]" if "OCR" in body else ""
        print("   ", p.get("id"), "|", p.get("title"), "| len=%d%s" % (len(body), mark))

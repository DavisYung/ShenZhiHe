import sys, json, os, re
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"D:\deepseek-harness\default-workspace\f6chem"
qs = json.load(open(os.path.join(BASE,"quiz","2b.json"), encoding="utf-8"))["questions"]
print("=== TF ===")
for q in qs:
    if q["type"]=="tf":
        print(q["id"], q["point"], "|", q["answer"], "|", q["q"])
print("=== MC answers ===")
for q in qs:
    if q["type"]=="mc":
        print(q["id"], q["point"], "ans=", q["answer"], "|", q["q"][:38])
print("=== option-letter refs in explanations (rotation hazard) ===")
hits=0
for q in qs:
    blob = q.get("explanation","") + " " + q.get("q","") + " " + " ".join(q.get("options",[]))
    for m in re.finditer(r"[（(]?\s*選項\s*([ABCD])|答案\s*([ABCD])\b|([ABCD])\s*項", blob):
        hits+=1; print("  ", q["id"], blob[max(0,m.start()-20):m.end()+20])
print("hits:", hits)
print("=== explanation mentions of 錯項字母/順序 ===")
for q in qs:
    if q["type"]=="mc" and re.search(r"[ABCD]\s*[項、，,。]|答案[為是]\s*[ABCD]", q.get("explanation","")):
        print("  CHECK", q["id"], q["explanation"][:120])
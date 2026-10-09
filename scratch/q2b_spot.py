import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
qs = json.load(open(os.path.join(BASE,"quiz","2b.json"), encoding="utf-8"))["questions"]
SHOW = {"2b-s8-p1","2b-s10-p1","2b-s14-p2","2b-s17-p2","2b-s21-p2","2b-s18-p2"}
for q in qs:
    if q["point"] in SHOW:
        print(q["id"], q["point"], q["type"], "ans=", q["answer"])
        print("  Q:", q["q"])
        if q["type"] == "mc":
            for i,o in enumerate(q["options"]):
                print("   ", "ABCD"[i], ("*" if i==q["answer"] else " "), o)
        print("  E:", q["explanation"][:230])
        print()
print("---- tf (all) ----")
for q in qs:
    if q["type"]=="tf":
        print(q["id"], q["point"], "|", "T" if q["answer"] else "F", "|", q["q"][:70])
print("---- fill (all) ----")
for q in qs:
    if q["type"]=="fill":
        print(q["id"], q["point"], "|", q["q"][:66], "| ans=", json.dumps(q["answer"], ensure_ascii=False))
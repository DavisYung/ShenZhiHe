import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
q = json.load(open(os.path.join(BASE,"quiz","2a.json"), encoding="utf-8"))
qs = q["questions"]
print("keys:", list(q.keys()))
for x in qs:
    if x["type"]=="fill":
        print("FILL", x["id"], x["point"], "|", x["q"], "| ans=", json.dumps(x["answer"], ensure_ascii=False))
        print("   expl:", x["explanation"][:110])
print("---- mc sample ----")
c=0
for x in qs:
    if x["type"]=="mc" and c<3:
        print(x["id"], x["point"], "|", x["q"])
        for i,o in enumerate(x["options"]): print("   ", "ABCD"[i], o)
        print("   ans:", x["answer"], "|", x["explanation"][:120])
        c+=1
print("---- tf sample ----")
c=0
for x in qs:
    if x["type"]=="tf" and c<3:
        print(x["id"], x["point"], "|", x["q"], "| ans=", x["answer"])
        print("   expl:", x["explanation"][:120]); c+=1
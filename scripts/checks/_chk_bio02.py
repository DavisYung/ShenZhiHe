import json,sys,re
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/bio/bio02.json",encoding="utf-8"))
print("topic:",d.get("title"),"sections:",len(d.get("sections",[])))
n=0
for s in d.get("sections",[]):
    for p in s.get("points",[]):
        b=p.get("body","")
        if re.search(r"[A-Za-z]_[A-Za-z0-9]", b):
            n+=1
            if n<=3:
                print("---",p["id"],"---")
                print(b[:300].replace("\n"," | "))
print("含下划线的知识点:",n)

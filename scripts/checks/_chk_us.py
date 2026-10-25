import json,re,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
pat=re.compile(r"[A-Za-z]\w*_\w+")
hits=[]
for sec in ("toback","given"):
    for g in d.get(sec,[]):
        for it in g.get("items",[]):
            for k in ("f","n"):
                v=it.get(k,"")
                if "_" in v: hits.append((sec,k,v))
            for s in it.get("sym",[]):
                if "_" in s: hits.append((sec,"sym",s))
print("含下划线的条目:",len(hits))
for h in hits[:15]: print(" ",h[0],h[1],"->",h[2][:90])

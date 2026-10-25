import json,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
c=collections.Counter()
for g in d["given"]:
    for k in g: c["G."+k]+=1
    for it in g.get("items",[]):
        for k in it: c["I."+k]+=1
print(dict(c))
print("given groups:",[ (g["group"], len(g.get("items",[])), g.get("note","")) for g in d["given"]])

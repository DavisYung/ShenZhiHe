import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="extras/phys/formulas.json"
d=json.load(open(p,encoding="utf-8"))
print("keys:",list(d.keys()))
print("id/type:",d.get("id"),d.get("type"))
print("title:",d.get("title"))
print("subtitle:",d.get("subtitle"))
print("source:",d.get("source"))
print("groups:",len(d.get("toback",[])))
tot=0
for g in d["toback"]:
    print("  -",g.get("group"),"items=",len(g.get("items",[])))
    tot+=len(g.get("items",[]))
print("total items:",tot)
it=d["toback"][0]["items"][0]
print("item keys:",list(it.keys()))
print(json.dumps(it,ensure_ascii=False,indent=1))

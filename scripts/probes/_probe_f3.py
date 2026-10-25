import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
print("=== given ===")
print(json.dumps(d["given"],ensure_ascii=False,indent=1)[:3000])
print("=== items with from ===")
for g in d["toback"]:
    for it in g["items"]:
        if "from" in it:
            print(g["group"],"|",it["f"],"| from=",it["from"],"| n=",it["n"][:40])

import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
for g in d["toback"]:
    print("###",g["group"],"| note:",g.get("note",""))
    for it in g["items"]:
        print("  f:",it["f"])
        print("    n:",it["n"])
        print("    pt:",it["pt"],"tp:",it["tp"],"from:",it.get("from"))
        print("    sym:",it["sym"])

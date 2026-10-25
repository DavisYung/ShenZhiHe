import json,sys
sys.stdout.reconfigure(encoding="utf-8")
for p in ["extras/chem/orgnaming.json","extras/chem/ptable.json","extras/chem/hot.json","extras/math/programs.json","extras/phys/formulas.json"]:
    d=json.load(open(p,encoding="utf-8"))
    print(p,"-> type =",d.get("type"))

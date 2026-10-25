import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/chem/orgnaming.json",encoding="utf-8"))
print("keys:",list(d.keys()))
for k,v in d.items():
    if isinstance(v,list):
        print(f"{k}: list[{len(v)}]")
        if v and isinstance(v[0],dict): print("   item0 keys:",list(v[0].keys()))
    elif isinstance(v,str):
        print(f"{k}: {v[:120]}")
    else:
        print(f"{k}: {v}")
print()
print(json.dumps(d,ensure_ascii=False,indent=1)[:4000])

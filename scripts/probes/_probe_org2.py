import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/chem/orgnaming.json",encoding="utf-8"))
print("=== chain ==="); print(json.dumps(d["chain"],ensure_ascii=False,indent=1))
print("=== examples ==="); print(json.dumps(d["examples"],ensure_ascii=False,indent=1))
print("=== rules 剩余 ==="); print(json.dumps(d["rules"][5:],ensure_ascii=False,indent=1))

import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
print("emoji 字段:",repr(d.get("emoji")))
print("id:",d.get("id"),"type:",d.get("type"))

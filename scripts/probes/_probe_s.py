import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/phys/subject.json",encoding="utf-8"))
print("subject keys:",list(d.keys()))
print(json.dumps(d.get("extras"),ensure_ascii=False,indent=1))

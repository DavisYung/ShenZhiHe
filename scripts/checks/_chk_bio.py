import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/bio/subject.json",encoding="utf-8"))
print("=== units ===")
for u in d.get("units",[]):
    print(" ",u.get("id"),"|",u.get("title"),"| topics:",u.get("topics"))
print("\n=== topics 数量:",len(d.get("topics",[])))

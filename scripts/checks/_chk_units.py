import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/phys/subject.json",encoding="utf-8"))
print("units:")
for u in d.get("units",[]):
    print(" ",u.get("id"),u.get("title"),"->",u.get("topics"))
print("\nTOPICS 是字符串还是对象:",type(d.get("topics",[])[0]).__name__ if d.get("topics") else "empty")
print("colors 字段:",d.get("colors"))

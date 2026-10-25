import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/phys/subject.json",encoding="utf-8"))
print("subject.color:",d.get("color"))
# 看 topics 是否带 color
for t in d.get("topics",[])[:6]:
    print(" ",t.get("id"),t.get("title"),"color=",t.get("color"))
print("units:")
for u in d.get("units",[]):
    print("  ",u.get("id"),u.get("title"),"color=",u.get("color"),"topics=",u.get("topics"))

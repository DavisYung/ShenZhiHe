import json,sys,glob,os
sys.stdout.reconfigure(encoding="utf-8")
# 检查 bio32-35 是否存在及其 tags
for n in ["bio32","bio33","bio34","bio35"]:
    p=f"data/bio/{n}.json"
    if not os.path.exists(p):
        print(n,"**文件不存在**")
        continue
    d=json.load(open(p,encoding="utf-8"))
    print(n,"|",d.get("title"),"| tags:",d.get("tags"))

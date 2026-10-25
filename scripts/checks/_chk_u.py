import json,glob,sys
sys.stdout.reconfigure(encoding="utf-8")
u_cnt=0; under_cnt=0; samples=[]
for f in glob.glob("data/*/*.json"):
    if "links" in f or "subject" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except: continue
    for s in d.get("sections",[]):
        for p in s.get("points",[]):
            b=p.get("body","")
            if "<u>" in b: u_cnt+=1
            # 找 markdown 下划线强调 __xxx__ 或 _xxx_
            import re
            if re.search(r"(?<![A-Za-z0-9])_[^_\n]{1,30}_(?![A-Za-z0-9])", b):
                under_cnt+=1
                if len(samples)<3: samples.append((p["id"], re.findall(r"(?<![A-Za-z0-9])_[^_\n]{1,30}_(?![A-Za-z0-9])", b)[:3]))
print("<u> 标签:",u_cnt)
print("疑似 _强调_ 写法:",under_cnt)
for s in samples: print("  ",s)

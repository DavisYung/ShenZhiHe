import json,glob,re,sys
sys.stdout.reconfigure(encoding="utf-8")
cnt=0
samples=[]
for f in glob.glob("data/*/*.json"):
    if "links" in f or "subject" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except: continue
    for s in d.get("sections",[]):
        for p in s.get("points",[]):
            b=p.get("body","")
            if "<sub>" in b or "<sup>" in b:
                cnt+=1
                if len(samples)<3: samples.append((f,p["id"],b[:200]))
print("含 sub/sup 标签的知识点:",cnt)
for s in samples: print(s[0],s[1],"->",s[2].replace("\n"," | ")[:180])

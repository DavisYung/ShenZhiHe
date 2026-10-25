import json,glob,re,sys
sys.stdout.reconfigure(encoding="utf-8")
best=[]
for f in glob.glob("data/*/*.json"):
    if "links" in f or "subject" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except: continue
    npts=sum(len(s.get("points",[])) for s in d.get("sections",[]))
    nsub=0
    for s in d.get("sections",[]):
        for p in s.get("points",[]):
            if re.search(r"[A-Za-z]_[A-Za-z0-9]", p.get("body","")): nsub+=1
    if nsub>0: best.append((f.split("\\")[-1],d.get("title"),npts,nsub))
best.sort(key=lambda x:x[2])
for b in best[:8]: print(b)

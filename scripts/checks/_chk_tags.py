import json,glob,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
c=collections.Counter()
for p in glob.glob("data/*/*.json"):
    if "links" in p or "subject" in p or ".bak" in p: continue
    try: d=json.load(open(p,encoding="utf-8"))
    except: continue
    for t in (d.get("tags") or []):
        c[t]+=1
print("全站 topic tags 取值:",dict(c))

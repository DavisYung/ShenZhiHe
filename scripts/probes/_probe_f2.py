import json,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
allitems=[it for g in d["toback"] for it in g["items"]]
# 所有字段出现情况
c=collections.Counter()
for it in allitems:
    for k in it: c[k]+=1
print("field freq:",dict(c))
# tp 分布
print("tp dist:",dict(collections.Counter(it.get("tp") for it in allitems)))
# 是否有 pt 指向的知识点存在
import os,glob
pts=set()
for f in glob.glob("data/phys/*.json"):
    if f.endswith("links.json") or "subject" in f: continue
    try: dd=json.load(open(f,encoding="utf-8"))
    except: continue
    for s in dd.get("sections",[]):
        for p in s.get("points",[]): pts.add(p["id"])
miss=[(it.get("tp"),it.get("pt")) for it in allitems if it.get("pt") and it["pt"] not in pts]
print("missing pt refs:",len(miss),miss[:10])
print("no pt:",sum(1 for it in allitems if not it.get("pt")))
